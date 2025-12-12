package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.BankConnectionDTO;
import com.savevia.optimizer.dto.FlinksConnectRequest;
import com.savevia.optimizer.entity.BankAccount;
import com.savevia.optimizer.entity.BankConnection;
import com.savevia.optimizer.entity.UserConnectionLimit;
import com.savevia.optimizer.mapper.BankAccountMapper;
import com.savevia.optimizer.mapper.BankConnectionMapper;
import com.savevia.optimizer.service.ConnectionLimitService;
import com.savevia.optimizer.service.FlinksService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequestMapping("/api/v1/optimize/bank")
@RequiredArgsConstructor
public class BankConnectionController {

    private final FlinksService flinksService;
    private final BankConnectionMapper bankConnectionMapper;
    private final BankAccountMapper bankAccountMapper;
    private final ConnectionLimitService connectionLimitService;

    @Value("${flinks.api.customer-id:}")
    private String flinksCustomerId;

    @Value("${flinks.api.iframe-url:https://toolbox.private.fin.ag/v2/}")
    private String flinksIframeUrl;

    @Value("${flinks.sandbox.enabled:true}")
    private boolean sandboxEnabled;

    /**
     * Get Flinks Connect configuration for frontend
     */
    @GetMapping("/flinks-config")
    public Result<Map<String, Object>> getFlinksConfig(@RequestHeader("X-User-Id") Long userId) {
        Map<String, Object> config = new HashMap<>();
        config.put("customerId", flinksCustomerId);
        config.put("iframeUrl", flinksIframeUrl);
        config.put("sandbox", sandboxEnabled);

        // Build the full iframe URL with customer ID
        String fullIframeUrl = flinksIframeUrl;
        if (!flinksCustomerId.isEmpty()) {
            fullIframeUrl = flinksIframeUrl + "?customerId=" + flinksCustomerId;
        }
        config.put("connectUrl", fullIframeUrl);

        // Add connection limit info
        UserConnectionLimit limit = connectionLimitService.getConnectionLimit(userId);
        config.put("connectionLimit", Map.of(
            "used", limit.getConnectionCount(),
            "max", limit.getMaxConnections(),
            "remaining", limit.getRemainingConnections(),
            "canConnect", limit.canConnect()
        ));

        return Result.success(config);
    }

    /**
     * Get current month's connection limit status
     */
    @GetMapping("/connection-limit")
    public Result<Map<String, Object>> getConnectionLimit(@RequestHeader("X-User-Id") Long userId) {
        UserConnectionLimit limit = connectionLimitService.getConnectionLimit(userId);
        return Result.success(Map.of(
            "used", limit.getConnectionCount(),
            "max", limit.getMaxConnections(),
            "remaining", limit.getRemainingConnections(),
            "canConnect", limit.canConnect(),
            "yearMonth", limit.getYearMonth()
        ));
    }

    /**
     * Connect a bank account via Flinks
     */
    @PostMapping("/connect")
    public Result<BankConnectionDTO> connectBank(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody FlinksConnectRequest request) {
        log.info("User {} connecting bank: {}", userId, request.getInstitutionName());

        BankConnection connection = flinksService.connectBank(userId, request);
        return Result.success(toDTO(connection));
    }

    /**
     * Get all bank connections for a user
     */
    @GetMapping("/connections")
    public Result<List<BankConnectionDTO>> getConnections(@RequestHeader("X-User-Id") Long userId) {
        List<BankConnection> connections = bankConnectionMapper.findByUserId(userId);
        List<BankConnectionDTO> dtos = connections.stream()
                .map(this::toDTO)
                .collect(Collectors.toList());
        return Result.success(dtos);
    }

    /**
     * Get a specific bank connection with accounts
     */
    @GetMapping("/connections/{connectionId}")
    public Result<BankConnectionDTO> getConnection(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long connectionId) {
        BankConnection connection = bankConnectionMapper.findById(connectionId);
        if (connection == null || !connection.getUserId().equals(userId)) {
            return Result.error("Connection not found");
        }
        return Result.success(toDTO(connection));
    }

    /**
     * Refresh bank data (local only, no Flinks API call)
     */
    @PostMapping("/connections/{connectionId}/refresh")
    public Result<BankConnectionDTO> refreshConnection(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long connectionId) {
        BankConnection connection = bankConnectionMapper.findById(connectionId);
        if (connection == null || !connection.getUserId().equals(userId)) {
            return Result.error("Connection not found");
        }

        flinksService.refreshBankData(connection);
        return Result.success(toDTO(connection));
    }

    /**
     * Resync bank data from Flinks API (costs connection quota!)
     */
    @PostMapping("/connections/{connectionId}/resync")
    public Result<BankConnectionDTO> resyncConnection(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long connectionId,
            @RequestBody(required = false) Map<String, Object> body) {
        BankConnection connection = bankConnectionMapper.findById(connectionId);
        if (connection == null || !connection.getUserId().equals(userId)) {
            return Result.error("Connection not found");
        }

        // Check monthly connection limit
        if (!connectionLimitService.canConnect(userId)) {
            return Result.error("LIMIT_EXCEEDED:Monthly connection limit reached (5/month). Please try again next month.");
        }

        // Get user card IDs if provided
        List<Long> userCardIds = null;
        if (body != null && body.get("userCardIds") != null) {
            userCardIds = ((List<?>) body.get("userCardIds")).stream()
                    .map(id -> ((Number) id).longValue())
                    .collect(java.util.stream.Collectors.toList());
        }

        // Force refresh from Flinks API
        flinksService.forceRefreshBankData(connection, userCardIds);

        // Record this as a connection usage
        connectionLimitService.recordConnection(userId, connection.getInstitutionName(), connection.getFlinksLoginId());

        return Result.success(toDTO(connection));
    }

    /**
     * Disconnect a bank
     */
    @DeleteMapping("/connections/{connectionId}")
    public Result<Void> disconnectBank(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long connectionId) {
        BankConnection connection = bankConnectionMapper.findById(connectionId);
        if (connection == null || !connection.getUserId().equals(userId)) {
            return Result.error("Connection not found");
        }

        connection.setStatus("DISCONNECTED");
        bankConnectionMapper.updateStatus(connection);

        // Record disconnect in history (doesn't restore monthly quota)
        connectionLimitService.recordDisconnect(userId, connection.getInstitutionName(), connection.getFlinksLoginId());

        return Result.success(null);
    }

    private BankConnectionDTO toDTO(BankConnection connection) {
        BankConnectionDTO dto = new BankConnectionDTO();
        dto.setId(connection.getId());
        dto.setInstitutionName(connection.getInstitutionName());
        dto.setStatus(connection.getStatus());
        dto.setLastSyncAt(connection.getLastSyncAt());
        dto.setErrorMessage(connection.getErrorMessage());
        dto.setCreatedAt(connection.getCreatedAt());

        // Load accounts
        List<BankAccount> accounts = bankAccountMapper.findByConnectionId(connection.getId());
        dto.setAccounts(accounts.stream().map(acc -> {
            BankConnectionDTO.BankAccountDTO accDto = new BankConnectionDTO.BankAccountDTO();
            accDto.setId(acc.getId());
            accDto.setAccountType(acc.getAccountType());
            accDto.setAccountName(acc.getAccountName());
            accDto.setAccountNumberMasked(acc.getAccountNumberMasked());
            accDto.setBalance(acc.getBalance());
            accDto.setIsActive(acc.getIsActive());
            return accDto;
        }).collect(Collectors.toList()));

        return dto;
    }
}
