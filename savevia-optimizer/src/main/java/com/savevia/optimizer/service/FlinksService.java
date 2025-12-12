package com.savevia.optimizer.service;

import com.savevia.optimizer.dto.CreditCardDTO;
import com.savevia.optimizer.dto.FlinksConnectRequest;
import com.savevia.optimizer.entity.BankAccount;
import com.savevia.optimizer.entity.BankConnection;
import com.savevia.optimizer.entity.Transaction;
import com.savevia.optimizer.mapper.BankAccountMapper;
import com.savevia.optimizer.mapper.BankConnectionMapper;
import com.savevia.optimizer.mapper.TransactionMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class FlinksService {

    private final BankConnectionMapper bankConnectionMapper;
    private final BankAccountMapper bankAccountMapper;
    private final TransactionMapper transactionMapper;
    private final TransactionCategorizationService categorizationService;
    private final CardServiceClient cardServiceClient;
    private final ConnectionLimitService connectionLimitService;
    private final RestTemplate restTemplate;

    @Value("${flinks.api.base-url:https://toolbox-api.private.fin.ag/v3}")
    private String flinksBaseUrl;

    @Value("${flinks.api.customer-id:43387ca6-0391-4c82-857d-70d95f087ecb}")
    private String flinksCustomerId;

    @Value("${flinks.sandbox.enabled:true}")
    private boolean sandboxEnabled;

    /**
     * Connect bank account via Flinks
     */
    @Transactional
    public BankConnection connectBank(Long userId, FlinksConnectRequest request) {
        log.info("Connecting bank for user {}, loginId: {}", userId, request.getLoginId());

        // Check if connection already exists by loginId (refresh doesn't count as new connection)
        BankConnection existing = bankConnectionMapper.findByUserAndLoginId(userId, request.getLoginId());
        if (existing != null) {
            existing.setStatus("REFRESHING");
            bankConnectionMapper.updateStatus(existing);
            // Trigger refresh (doesn't use monthly quota)
            refreshBankData(existing);
            connectionLimitService.recordRefresh(userId, existing.getInstitutionName(), existing.getFlinksLoginId());
            return existing;
        }

        // Also check by institution name (for demo mode where loginId changes)
        BankConnection existingByInstitution = bankConnectionMapper.findByUserAndInstitution(userId, request.getInstitutionName());
        if (existingByInstitution != null) {
            existingByInstitution.setStatus("REFRESHING");
            existingByInstitution.setFlinksLoginId(request.getLoginId()); // Update loginId
            bankConnectionMapper.updateStatus(existingByInstitution);
            refreshBankData(existingByInstitution);
            connectionLimitService.recordRefresh(userId, existingByInstitution.getInstitutionName(), existingByInstitution.getFlinksLoginId());
            return existingByInstitution;
        }

        // Check monthly connection limit before creating NEW connection
        if (!connectionLimitService.canConnect(userId)) {
            int remaining = connectionLimitService.getRemainingConnections(userId);
            log.warn("User {} has reached monthly connection limit. Remaining: {}", userId, remaining);
            throw new RuntimeException("LIMIT_EXCEEDED:You have reached your monthly bank connection limit (5 per month). Please try again next month.");
        }

        // Create new connection
        BankConnection connection = new BankConnection();
        connection.setUserId(userId);
        connection.setFlinksLoginId(request.getLoginId());
        connection.setInstitutionName(request.getInstitutionName());
        connection.setStatus("PENDING");
        bankConnectionMapper.insert(connection);

        // Fetch data from Flinks (pass user card IDs for demo mode)
        try {
            fetchFlinksData(connection, request.getUserCardIds());
            connection.setStatus("CONNECTED");
            connection.setLastSyncAt(LocalDateTime.now(ZoneOffset.UTC));

            // Record successful connection (counts against monthly limit)
            connectionLimitService.recordConnection(userId, request.getInstitutionName(), request.getLoginId());
        } catch (Exception e) {
            log.error("Failed to fetch Flinks data", e);
            connection.setStatus("ERROR");
            connection.setErrorMessage(e.getMessage());
            // Note: Failed connections don't count against the monthly limit
        }
        bankConnectionMapper.updateStatus(connection);

        return connection;
    }

    /**
     * Refresh bank data - local status check only
     * Note: Does NOT call Flinks API to avoid additional charges
     * Note: Does NOT update lastSyncAt since no actual sync occurs
     * The actual data refresh happens when user uses "Resync" feature
     */
    public void refreshBankData(BankConnection connection) {
        // Only update status locally without calling Flinks API
        // Flinks charges per API call, so we avoid unnecessary refreshes
        // Do NOT update lastSyncAt - that should only change when actual Flinks sync happens
        connection.setStatus("CONNECTED");
        connection.setErrorMessage(null);
        bankConnectionMapper.updateStatus(connection);
        log.info("Checked connection status for {} (no Flinks API call, no timestamp update)", connection.getId());
    }

    /**
     * Force refresh bank data from Flinks API (use sparingly - costs money!)
     */
    public void forceRefreshBankData(BankConnection connection, List<Long> userCardIds) {
        try {
            fetchFlinksData(connection, userCardIds);
            connection.setStatus("CONNECTED");
            connection.setLastSyncAt(LocalDateTime.now(ZoneOffset.UTC));
            connection.setErrorMessage(null);
        } catch (Exception e) {
            log.error("Failed to refresh Flinks data", e);
            connection.setStatus("ERROR");
            connection.setErrorMessage(e.getMessage());
        }
        bankConnectionMapper.updateStatus(connection);
    }

    /**
     * Fetch data from Flinks API
     */
    private void fetchFlinksData(BankConnection connection) {
        fetchFlinksData(connection, null);
    }

    /**
     * Fetch data from Flinks API with user card IDs
     */
    private void fetchFlinksData(BankConnection connection, List<Long> userCardIds) {
        // Step 1: Get user's credit cards for matching
        List<CreditCardDTO> userCards = new ArrayList<>();
        if (userCardIds != null && !userCardIds.isEmpty()) {
            try {
                var result = cardServiceClient.getCardsByIds(userCardIds);
                if (result.getData() != null) {
                    userCards = result.getData();
                }
            } catch (Exception e) {
                log.warn("Failed to fetch user cards for matching: {}", e.getMessage());
            }
        }

        // Step 2: Authorize with Flinks
        String requestId = authorizeWithFlinks(connection.getFlinksLoginId());

        // Step 3: Get accounts detail (with polling for async)
        Map<String, Object> accountsData = getAccountsDetail(requestId);

        // Step 4: Parse and save all accounts (credit cards will have transactions analyzed)
        List<Map<String, Object>> accounts = (List<Map<String, Object>>) accountsData.get("Accounts");
        if (accounts != null) {
            int creditCardCount = 0;
            for (Map<String, Object> accountData : accounts) {
                String accountType = mapAccountType((String) accountData.get("Type"));
                saveOrUpdateAccount(connection, accountData, userCards);
                if ("CREDIT_CARD".equals(accountType)) {
                    creditCardCount++;
                }
            }
            log.info("Saved {} accounts for connection {}, including {} credit cards",
                    accounts.size(), connection.getId(), creditCardCount);
        }
    }

    private String authorizeWithFlinks(String loginId) {
        log.info("Authorizing with Flinks loginId: {}, sandbox: {}", loginId, sandboxEnabled);

        // If sandbox mode is enabled OR loginId starts with 'demo-', use demo mode
        // We don't have Flinks API access without a contract, so always use demo in sandbox
        if (sandboxEnabled || loginId.startsWith("demo-")) {
            log.info("Using demo mode for authorization (sandbox={}, loginId={})", sandboxEnabled, loginId);
            return "demo-request-" + UUID.randomUUID().toString();
        }

        // Real Flinks API call (requires production contract with Flinks)
        // Flinks Toolbox API: POST /{customerId}/BankingServices/Authorize
        String url = String.format("%s/%s/BankingServices/Authorize", flinksBaseUrl, flinksCustomerId);
        log.info("Calling Flinks Authorize API: {}", url);

        Map<String, Object> body = new HashMap<>();
        body.put("LoginId", loginId);
        body.put("MostRecentCached", true);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, request, Map.class);

            if (response.getBody() != null) {
                log.info("Flinks Authorize response: {}", response.getBody());
                String requestId = (String) response.getBody().get("RequestId");
                if (requestId != null) {
                    return requestId;
                }
            }
            throw new RuntimeException("Failed to get RequestId from Flinks authorization");
        } catch (Exception e) {
            log.error("Flinks Authorize API error: {}", e.getMessage());
            throw new RuntimeException("Bank connection failed: " + e.getMessage());
        }
    }

    private Map<String, Object> getAccountsDetail(String requestId) {
        log.info("Getting accounts detail for requestId: {}", requestId);

        // If demo requestId, use demo data
        if (requestId.startsWith("demo-")) {
            log.info("Using demo mode for accounts detail");
            return generateMockAccountsData();
        }

        // Real Flinks API call
        // Flinks Toolbox API: POST /{customerId}/BankingServices/GetAccountsDetail
        String url = String.format("%s/%s/BankingServices/GetAccountsDetail", flinksBaseUrl, flinksCustomerId);
        log.info("Calling Flinks GetAccountsDetail API: {}", url);

        Map<String, Object> body = new HashMap<>();
        body.put("RequestId", requestId);
        body.put("WithTransactions", true);
        body.put("DaysOfTransactions", "Days90");

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

        // Poll for async response (Flinks may return 202 while processing)
        int maxRetries = 10;
        Exception lastError = null;

        for (int i = 0; i < maxRetries; i++) {
            try {
                ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, request, Map.class);
                log.info("Flinks GetAccountsDetail response status: {}", response.getStatusCode());

                if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                    Map<String, Object> responseBody = response.getBody();
                    // Check if response contains accounts
                    if (responseBody.containsKey("Accounts")) {
                        log.info("Successfully got accounts from Flinks");
                        return responseBody;
                    }
                    // Check for HttpStatusCode in response (async processing)
                    Object statusCode = responseBody.get("HttpStatusCode");
                    if (statusCode != null && (statusCode.equals(202) || statusCode.equals("202"))) {
                        log.info("Flinks still processing, waiting... (attempt {}/{})", i + 1, maxRetries);
                    }
                }
            } catch (Exception e) {
                log.warn("Flinks API call attempt {} failed: {}", i + 1, e.getMessage());
                lastError = e;
            }

            // Wait before retry
            try {
                Thread.sleep(3000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("Bank data retrieval interrupted");
            }
        }

        log.error("Timeout waiting for Flinks data after {} retries", maxRetries);
        String errorMsg = lastError != null ? lastError.getMessage() : "Timeout waiting for bank data";
        throw new RuntimeException("Failed to retrieve bank data: " + errorMsg);
    }

    private void saveOrUpdateAccount(BankConnection connection, Map<String, Object> accountData, List<CreditCardDTO> userCards) {
        String flinksAccountId = (String) accountData.get("Id");
        String accountType = mapAccountType((String) accountData.get("Type"));
        String accountName = (String) accountData.get("Title");

        // Check if account exists
        List<BankAccount> existing = bankAccountMapper.findByConnectionId(connection.getId());
        BankAccount account = existing.stream()
                .filter(a -> a.getFlinksAccountId().equals(flinksAccountId))
                .findFirst()
                .orElse(null);

        // Try to match credit card account to user's cards
        Long linkedCardId = null;
        if ("CREDIT_CARD".equals(accountType) && userCards != null && !userCards.isEmpty()) {
            linkedCardId = matchCreditCardToUserCard(accountName, connection.getInstitutionName(), userCards);
            if (linkedCardId != null) {
                log.info("Matched credit card account '{}' to card ID {}", accountName, linkedCardId);
            }
        }

        if (account == null) {
            account = new BankAccount();
            account.setConnectionId(connection.getId());
            account.setUserId(connection.getUserId());
            account.setFlinksAccountId(flinksAccountId);
            account.setAccountType(accountType);
            account.setAccountName(accountName);
            account.setAccountNumberMasked(maskAccountNumber((String) accountData.get("AccountNumber")));
            account.setInstitutionName(connection.getInstitutionName());
            account.setIsActive(true);
            account.setLinkedCardId(linkedCardId);
            bankAccountMapper.insert(account);
        } else if (linkedCardId != null && account.getLinkedCardId() == null) {
            // Update linked card if newly matched
            account.setLinkedCardId(linkedCardId);
        }

        // Update balance
        Object balanceObj = accountData.get("Balance");
        if (balanceObj != null) {
            account.setBalance(new BigDecimal(balanceObj.toString()));
            bankAccountMapper.update(account);
        }

        // Save transactions (use linkedCardId as card_used_id for credit card accounts)
        List<Map<String, Object>> transactions = (List<Map<String, Object>>) accountData.get("Transactions");
        if (transactions != null) {
            saveTransactions(account, transactions);
        }
    }

    /**
     * Match a credit card account name to user's cards
     * Uses bank name and fuzzy matching on card name
     */
    private Long matchCreditCardToUserCard(String accountName, String institutionName, List<CreditCardDTO> userCards) {
        if (accountName == null || institutionName == null) return null;

        String normalizedAccountName = accountName.toUpperCase();
        String normalizedInstitution = institutionName.toUpperCase();

        // Extract bank short name (e.g., "TD Canada Trust" -> "TD")
        String bankShortName = normalizedInstitution.split(" ")[0];

        CreditCardDTO bestMatch = null;
        int bestScore = 0;

        for (CreditCardDTO card : userCards) {
            // Check if bank matches
            if (!card.getBank().toUpperCase().contains(bankShortName) &&
                !bankShortName.contains(card.getBank().toUpperCase())) {
                continue;
            }

            // Calculate match score based on card name keywords
            int score = 0;
            String cardNameUpper = card.getName().toUpperCase();
            String[] keywords = cardNameUpper.split(" ");

            for (String keyword : keywords) {
                if (keyword.length() >= 3 && normalizedAccountName.contains(keyword)) {
                    score += keyword.length();
                }
            }

            // Also check if account name contains card type hints
            if (normalizedAccountName.contains("VISA") && cardNameUpper.contains("VISA")) score += 5;
            if (normalizedAccountName.contains("MASTERCARD") && cardNameUpper.contains("MASTERCARD")) score += 5;
            if (normalizedAccountName.contains("AMEX") && cardNameUpper.contains("AMEX")) score += 5;
            if (normalizedAccountName.contains("CASHBACK") && cardNameUpper.contains("CASH")) score += 5;
            if (normalizedAccountName.contains("INFINITE") && cardNameUpper.contains("INFINITE")) score += 5;

            if (score > bestScore) {
                bestScore = score;
                bestMatch = card;
            }
        }

        // Require minimum score for a match
        return bestScore >= 3 && bestMatch != null ? bestMatch.getId() : null;
    }

    /**
     * Save transactions for an account
     * For credit card accounts, card_used_id is set from account.linkedCardId
     */
    private void saveTransactions(BankAccount account, List<Map<String, Object>> transactionsData) {
        for (Map<String, Object> txnData : transactionsData) {
            String flinksId = (String) txnData.get("Id");

            // Check if already exists
            Transaction existing = transactionMapper.findByAccountAndFlinksId(account.getId(), flinksId);
            if (existing != null) {
                continue;
            }

            Transaction txn = new Transaction();
            txn.setUserId(account.getUserId());
            txn.setAccountId(account.getId());
            txn.setFlinksTransactionId(flinksId);
            txn.setAmount(new BigDecimal(txnData.get("Debit") != null ?
                    txnData.get("Debit").toString() : "-" + txnData.get("Credit").toString()));
            txn.setMerchant((String) txnData.get("Description"));
            txn.setDescription((String) txnData.get("Description"));

            String dateStr = (String) txnData.get("Date");
            if (dateStr != null) {
                txn.setTransactionDate(LocalDateTime.parse(dateStr.substring(0, 19)));
            }

            // Auto-categorize
            String category = categorizationService.categorize(txn.getMerchant());
            txn.setCategory(category);
            txn.setIsAnalyzed(false);

            // For credit card accounts, use the linked card ID
            // For debit/checking/savings accounts, cardUsedId stays null (indicates debit payment)
            if ("CREDIT_CARD".equals(account.getAccountType()) && account.getLinkedCardId() != null) {
                txn.setCardUsedId(account.getLinkedCardId());
            }
            // Note: cardUsedId = null means debit card/bank transfer was used (no cashback earned)

            transactionMapper.insert(txn);
        }
    }

    private String mapAccountType(String flinksType) {
        if (flinksType == null) return "OTHER";
        switch (flinksType.toUpperCase()) {
            case "CHEQUING":
            case "CHECKING":
                return "CHECKING";
            case "SAVINGS":
                return "SAVINGS";
            case "CREDIT":
            case "CREDITCARD":
                return "CREDIT_CARD";
            case "LOC":
            case "LINEOFCREDIT":
                return "LINE_OF_CREDIT";
            default:
                return "OTHER";
        }
    }

    private String maskAccountNumber(String accountNumber) {
        if (accountNumber == null || accountNumber.length() < 4) return "****";
        return "****" + accountNumber.substring(accountNumber.length() - 4);
    }

    /**
     * Generate mock data for demo mode
     * Creates both checking accounts (debit transactions) and credit card accounts
     */
    private Map<String, Object> generateMockAccountsData() {
        Map<String, Object> result = new HashMap<>();
        List<Map<String, Object>> accounts = new ArrayList<>();
        Random rand = new Random();

        // Always add a checking account (debit card transactions - no cashback)
        Map<String, Object> checkingAccount = new HashMap<>();
        checkingAccount.put("Id", "demo-chk-" + UUID.randomUUID().toString().substring(0, 8));
        checkingAccount.put("Type", "Chequing");
        checkingAccount.put("Title", "Chequing Account");
        checkingAccount.put("AccountNumber", "****" + (1000 + rand.nextInt(9000)));
        checkingAccount.put("Balance", String.valueOf(2000 + rand.nextInt(8000)));
        checkingAccount.put("Transactions", generateMockDebitTransactions());
        accounts.add(checkingAccount);

        // Mock credit card accounts (these will be matched to user's selected cards)
        String[][] creditCardMocks = {
                {"demo-cc-001", "TD Cash Back Visa Infinite", "****1234"},
                {"demo-cc-002", "TD Aeroplan Visa Infinite", "****5678"},
                {"demo-cc-003", "RBC Avion Visa Infinite", "****9012"},
                {"demo-cc-004", "Scotiabank Scene+ Visa", "****3456"},
                {"demo-cc-005", "CIBC Dividend Visa Infinite", "****7890"},
        };

        // Pick 1-2 random credit cards for this demo connection
        int numCards = 1 + rand.nextInt(2);
        List<Integer> selectedIndices = new ArrayList<>();
        while (selectedIndices.size() < numCards && selectedIndices.size() < creditCardMocks.length) {
            int idx = rand.nextInt(creditCardMocks.length);
            if (!selectedIndices.contains(idx)) {
                selectedIndices.add(idx);
            }
        }

        for (int idx : selectedIndices) {
            Map<String, Object> ccAccount = new HashMap<>();
            ccAccount.put("Id", creditCardMocks[idx][0] + "-" + UUID.randomUUID().toString().substring(0, 8));
            ccAccount.put("Type", "Credit");
            ccAccount.put("Title", creditCardMocks[idx][1]);
            ccAccount.put("AccountNumber", creditCardMocks[idx][2]);
            ccAccount.put("Balance", String.valueOf(500 + rand.nextInt(3000)));
            ccAccount.put("Transactions", generateMockCreditTransactions());
            accounts.add(ccAccount);
        }

        result.put("Accounts", accounts);
        return result;
    }

    /**
     * Generate mock debit card transactions (from checking account)
     * These will have cardUsedId = null, representing missed cashback opportunities
     */
    private List<Map<String, Object>> generateMockDebitTransactions() {
        List<Map<String, Object>> transactions = new ArrayList<>();
        Random rand = new Random();
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);

        // Common debit card purchases that could have earned cashback
        String[][] mockData = {
                {"INTERAC PURCHASE - LOBLAWS #1234", "178.45", "GROCERY"},
                {"INTERAC PURCHASE - PETRO-CANADA", "72.50", "GAS"},
                {"INTERAC PURCHASE - SHOPPERS DRUG MART", "38.99", "PHARMACY"},
                {"INTERAC PURCHASE - COSTCO WHOLESALE", "285.67", "GROCERY"},
                {"INTERAC PURCHASE - SHELL", "58.00", "GAS"},
                {"INTERAC PURCHASE - SOBEYS", "112.30", "GROCERY"},
                {"INTERAC PURCHASE - REXALL PHARMA", "25.50", "PHARMACY"},
                {"INTERAC PURCHASE - ESSO", "45.00", "GAS"},
        };

        // Generate 5-8 debit transactions
        int numTxns = 5 + rand.nextInt(4);
        for (int i = 0; i < numTxns && i < mockData.length; i++) {
            Map<String, Object> txn = new HashMap<>();
            txn.put("Id", "demo-debit-" + UUID.randomUUID().toString());
            txn.put("Description", mockData[i][0]);
            txn.put("Debit", mockData[i][1]);
            txn.put("Date", now.minusDays(rand.nextInt(90)).toString());
            transactions.add(txn);
        }

        return transactions;
    }

    /**
     * Generate mock credit card transactions
     */
    private List<Map<String, Object>> generateMockCreditTransactions() {
        List<Map<String, Object>> transactions = new ArrayList<>();
        Random rand = new Random();
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);

        String[][] mockData = {
                {"UBER EATS", "25.99", "DINING"},
                {"NETFLIX.COM", "16.99", "STREAMING"},
                {"TIM HORTONS", "8.45", "DINING"},
                {"AMAZON.CA", "89.99", "ONLINE_SHOPPING"},
                {"ROGERS WIRELESS", "85.00", "RECURRING"},
                {"STARBUCKS", "6.75", "DINING"},
                {"PRESTO", "20.00", "TRANSIT"},
                {"UBER", "18.50", "TRANSIT"},
                {"BOSTON PIZZA", "52.30", "DINING"},
                {"SPOTIFY", "9.99", "STREAMING"},
        };

        // Generate 6-10 credit transactions
        int numTxns = 6 + rand.nextInt(5);
        for (int i = 0; i < numTxns && i < mockData.length; i++) {
            Map<String, Object> txn = new HashMap<>();
            txn.put("Id", "demo-credit-" + UUID.randomUUID().toString());
            txn.put("Description", mockData[i][0]);
            txn.put("Debit", mockData[i][1]);
            txn.put("Date", now.minusDays(rand.nextInt(90)).toString());
            transactions.add(txn);
        }

        return transactions;
    }
}
