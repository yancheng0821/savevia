package com.savevia.optimizer.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.common.dto.SpendingCategory;
import com.savevia.optimizer.dto.CategoryRecommendation;
import com.savevia.optimizer.dto.CreditCardDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.concurrent.*;

@Slf4j
@Service
public class OpenAiService {

    @Value("${openai.api.key:}")
    private String apiKey;

    @Value("${openai.api.model:gpt-4o-mini}")
    private String model;

    @Value("${openai.api.base-url:https://api.openai.com}")
    private String baseUrl;

    @Value("${openai.enabled:true}")
    private boolean enabled;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    // Bounded thread pool for OpenAI calls - limits concurrent API requests
    private ExecutorService aiExecutor;

    public OpenAiService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void init() {
        // Max 10 concurrent OpenAI calls, queue up to 50 waiting tasks
        // Prevents CPU overload and API rate limiting
        aiExecutor = new ThreadPoolExecutor(
            4,                          // core threads
            10,                         // max threads
            60L, TimeUnit.SECONDS,      // idle thread timeout
            new LinkedBlockingQueue<>(50),  // bounded queue
            new ThreadPoolExecutor.CallerRunsPolicy()  // if queue full, run in caller thread
        );
        log.info("OpenAI executor initialized: core=4, max=10, queue=50");
    }

    @PreDestroy
    public void shutdown() {
        if (aiExecutor != null) {
            aiExecutor.shutdown();
            try {
                if (!aiExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    aiExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                aiExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * Generate AI explanations for all recommendations using parallel API calls
     */
    public void generateExplanations(List<CategoryRecommendation> recommendations,
                                     List<CreditCardDTO> userCards,
                                     String locale) {
        if (!enabled || apiKey == null || apiKey.isEmpty()) {
            log.info("OpenAI is disabled or API key not configured");
            return;
        }

        if (recommendations == null || recommendations.isEmpty()) {
            return;
        }

        String systemMessage = buildSystemMessage(locale);

        // Parallel API calls for each category using bounded thread pool
        List<CompletableFuture<Void>> futures = recommendations.stream()
            .map(rec -> CompletableFuture.runAsync(() -> {
                try {
                    String userMessage = buildSinglePrompt(rec, userCards);
                    String explanation = callOpenAiApi(systemMessage, userMessage);
                    if (explanation != null && !explanation.isEmpty()) {
                        rec.setAiExplanation(explanation.trim());
                    }
                } catch (Exception e) {
                    log.warn("Failed to generate AI explanation for {}: {}",
                        rec.getCategory().name(), e.getMessage());
                }
            }, aiExecutor))
            .toList();

        // Wait for all to complete (with timeout)
        try {
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .get(30, TimeUnit.SECONDS);
            long successCount = recommendations.stream()
                .filter(r -> r.getAiExplanation() != null)
                .count();
            log.info("Generated {} AI explanations in parallel", successCount);
        } catch (Exception e) {
            log.warn("Some AI explanations timed out: {}", e.getMessage());
        }
    }

    /**
     * Build system message with language and role instructions
     */
    private String buildSystemMessage(String locale) {
        String langInstruction = getLanguageInstruction(locale);

        return String.format("""
            You are a professional Canadian financial advisor providing credit card optimization insights.

            Rephrase the pre-calculated data below into a clear, professional summary. Vary sentence structure naturally.

            TONE: Professional financial advisor - confident, informative, trustworthy. Not casual, not robotic.

            DO:
            - Use the exact numbers provided
            - Vary how you present the information
            - Sound like a professional giving advice

            DON'T:
            - Start with greetings ("Hey!", "Hi there!")
            - Use casual slang
            - Do any calculations yourself
            - Use the same sentence pattern repeatedly

            Keep to 2-3 sentences. Plain text only.

            %s
            """, langInstruction);
    }

    /**
     * Get card reward rate for a specific category
     */
    private BigDecimal getCardRateForCategory(CreditCardDTO card, SpendingCategory category) {
        if (card.getRewardRules() != null) {
            for (var rule : card.getRewardRules()) {
                if (rule.getCategory() == category) {
                    return rule.getRewardRate();
                }
            }
        }
        return card.getBaseRewardRate() != null ? card.getBaseRewardRate() : BigDecimal.ZERO;
    }

    /**
     * Get language instruction based on locale
     */
    private String getLanguageInstruction(String locale) {
        if (locale == null) locale = "en";

        return switch (locale.toLowerCase()) {
            case "zh", "zh-cn", "zh-tw" -> "LANGUAGE: Respond in Simplified Chinese. 用简洁专业的语气。";
            case "ja" -> "LANGUAGE: Respond in Japanese. 簡潔でプロフェッショナルな表現で。";
            case "ko" -> "LANGUAGE: Respond in Korean. 간결하고 전문적인 어조로.";
            case "fr" -> "LANGUAGE: Respond in French. Style concis et professionnel.";
            case "es" -> "LANGUAGE: Respond in Spanish. Estilo conciso y profesional.";
            default -> "LANGUAGE: Respond in English.";
        };
    }

    /**
     * Build prompt for a single category - provides pre-calculated conclusions
     */
    private String buildSinglePrompt(CategoryRecommendation rec, List<CreditCardDTO> userCards) {
        CreditCardDTO bestCard = rec.getRecommendedCard();
        List<String> insights = new ArrayList<>();

        BigDecimal monthlyReward = rec.getMonthlyReward();
        BigDecimal annualReward = monthlyReward.multiply(BigDecimal.valueOf(12)).setScale(2, RoundingMode.HALF_UP);
        BigDecimal annualFee = bestCard.getAnnualFee() != null ? bestCard.getAnnualFee() : BigDecimal.ZERO;

        // Insight 1: Earnings
        insights.add(String.format("Category: %s. Card: %s %s. You earn $%.2f/month, $%.2f/year at %.1f%% rate.",
            rec.getCategory().getDisplayName(),
            bestCard.getBank(),
            bestCard.getName(),
            monthlyReward.doubleValue(),
            annualReward.doubleValue(),
            rec.getRewardRate().doubleValue() * 100));

        // Insight 2: Fee coverage (if applicable)
        if (annualFee.compareTo(BigDecimal.ZERO) > 0) {
            int coveragePercent = annualReward.multiply(BigDecimal.valueOf(100))
                .divide(annualFee, 0, RoundingMode.HALF_UP).intValue();
            if (coveragePercent >= 100) {
                insights.add(String.format("This category ALONE covers the $%.0f annual fee (and then some).",
                    annualFee.doubleValue()));
            } else {
                insights.add(String.format("This category covers %d%% of the $%.0f annual fee.",
                    coveragePercent, annualFee.doubleValue()));
            }
        }

        // Insight 3: Comparison with alternative
        if (userCards.size() > 1) {
            for (CreditCardDTO card : userCards) {
                if (!card.getId().equals(bestCard.getId())) {
                    BigDecimal cardRate = getCardRateForCategory(card, rec.getCategory());
                    BigDecimal altAnnual = rec.getMonthlySpend().multiply(cardRate)
                        .multiply(BigDecimal.valueOf(12)).setScale(2, RoundingMode.HALF_UP);
                    BigDecimal diffAnnual = annualReward.subtract(altAnnual).setScale(2, RoundingMode.HALF_UP);
                    if (diffAnnual.compareTo(BigDecimal.ZERO) > 0) {
                        insights.add(String.format("You earn $%.2f/year MORE than using %s %s.",
                            diffAnnual.doubleValue(), card.getBank(), card.getName()));
                    }
                    break;
                }
            }
        }

        // Insight 4: Points cards travel redemption
        String cardName = bestCard.getName().toLowerCase();
        if (cardName.contains("cobalt") || cardName.contains("gold") || cardName.contains("platinum") ||
            cardName.contains("aeroplan") || cardName.contains("avion")) {
            insights.add("Bonus: These are travel points - redeemable for flights and hotels.");
        }

        return String.join("\n", insights);
    }

    /**
     * Call OpenAI API for single category, return plain text
     */
    private String callOpenAiApi(String systemMessage, String userMessage) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(apiKey);

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", model);
            requestBody.put("max_tokens", 250);
            requestBody.put("temperature", 0.8);
            requestBody.put("messages", List.of(
                Map.of("role", "system", "content", systemMessage),
                Map.of("role", "user", "content", userMessage)
            ));

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                baseUrl + "/v1/chat/completions",
                HttpMethod.POST,
                entity,
                String.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                JsonNode root = objectMapper.readTree(response.getBody());
                JsonNode choices = root.path("choices");
                if (choices.isArray() && !choices.isEmpty()) {
                    return choices.get(0).path("message").path("content").asText();
                }
            }
            return null;

        } catch (Exception e) {
            log.warn("OpenAI API call failed: {}", e.getMessage());
            return null;
        }
    }
}
