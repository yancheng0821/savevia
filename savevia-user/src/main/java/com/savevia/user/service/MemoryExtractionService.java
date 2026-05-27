package com.savevia.user.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.common.constants.MemoryConstants;
import com.savevia.user.dto.MemoryExtractionResultDTO;
import com.savevia.user.entity.ChatConversation;
import com.savevia.user.entity.ChatMessage;
import com.savevia.user.entity.MemoryExtractionLog;
import com.savevia.user.mapper.ChatConversationMapper;
import com.savevia.user.mapper.ChatMessageMapper;
import com.savevia.user.mapper.MemoryExtractionLogMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Service for extracting long-term memory from conversations using LLM.
 * This service is designed for async/batch processing.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class MemoryExtractionService {

    private final ChatConversationMapper conversationMapper;
    private final ChatMessageMapper messageMapper;
    private final MemoryExtractionLogMapper extractionLogMapper;
    private final MemoryService memoryService;
    private final ObjectMapper objectMapper;

    @Value("${openai.api.key:}")
    private String apiKey;

    @Value("${openai.api.model:gpt-4o-mini}")
    private String model;

    @Value("${openai.api.base-url:https://api.openai.com}")
    private String baseUrl;

    @Value("${memory.extraction.enabled:true}")
    private boolean extractionEnabled;

    private OkHttpClient httpClient;

    @PostConstruct
    public void init() {
        httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        log.info("MemoryExtractionService initialized, enabled: {}", extractionEnabled);
    }

    @PreDestroy
    public void shutdown() {
        if (httpClient != null) {
            httpClient.dispatcher().executorService().shutdown();
            httpClient.connectionPool().evictAll();
        }
    }

    /**
     * Extract memory from a single conversation.
     *
     * @param conversationId Conversation ID to process
     * @return Extraction result or null if failed
     */
    @Transactional
    public MemoryExtractionResultDTO extractMemoryFromConversation(Long conversationId) {
        if (!extractionEnabled || apiKey == null || apiKey.isEmpty()) {
            log.warn("Memory extraction is disabled or API key not configured");
            return null;
        }

        try {
            // Get conversation
            ChatConversation conversation = conversationMapper.selectById(conversationId);
            if (conversation == null) {
                log.warn("Conversation {} not found", conversationId);
                return null;
            }

            // Get messages
            List<ChatMessage> messages = messageMapper.selectByConversationId(conversationId);
            if (messages.size() < 4) {
                log.debug("Conversation {} has only {} messages, skipping", conversationId, messages.size());
                return null;
            }

            // Build conversation content
            String conversationContent = buildConversationContent(messages);

            // Call LLM for extraction
            String extractionResult = callLlmForExtraction(conversationContent);
            if (extractionResult == null) {
                markExtractionFailed(conversationId, conversation.getUserId(), "LLM call failed");
                return null;
            }

            // Parse result
            MemoryExtractionResultDTO result = parseExtractionResult(extractionResult);
            if (result == null) {
                markExtractionFailed(conversationId, conversation.getUserId(), "Failed to parse LLM response");
                return null;
            }

            // Save extracted memory
            saveExtractedMemory(conversation.getUserId(), result, conversationId);

            // Mark as processed
            markExtractionProcessed(conversationId, conversation.getUserId());

            log.info("Successfully extracted memory from conversation {} for user {}",
                    conversationId, conversation.getUserId());
            return result;

        } catch (Exception e) {
            log.error("Error extracting memory from conversation {}: {}", conversationId, e.getMessage(), e);
            return null;
        }
    }

    /**
     * Build conversation content string from messages.
     */
    private String buildConversationContent(List<ChatMessage> messages) {
        StringBuilder sb = new StringBuilder();
        for (ChatMessage msg : messages) {
            String role = "user".equals(msg.getRole()) ? "User" : "Assistant";
            sb.append(role).append(": ").append(msg.getContent()).append("\n\n");
        }
        return sb.toString();
    }

    /**
     * Call LLM API to extract memory from conversation.
     */
    private String callLlmForExtraction(String conversationContent) {
        log.info("Starting LLM extraction, model: {}, baseUrl: {}, apiKey configured: {}",
                model, baseUrl, apiKey != null && !apiKey.isEmpty());

        try {
            String systemPrompt = buildExtractionPrompt();

            List<Map<String, String>> messages = new ArrayList<>();
            messages.add(Map.of("role", "system", "content", systemPrompt));
            messages.add(Map.of("role", "user", "content", "CONVERSATION:\n" + conversationContent));

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", model);
            requestBody.put("messages", messages);
            requestBody.put("max_tokens", 1500);
            requestBody.put("temperature", 0.3);
            requestBody.put("response_format", Map.of("type", "json_object"));

            String jsonBody = objectMapper.writeValueAsString(requestBody);
            log.debug("LLM request body length: {} chars", jsonBody.length());

            Request request = new Request.Builder()
                    .url(baseUrl + "/v1/chat/completions")
                    .addHeader("Authorization", "Bearer " + apiKey)
                    .addHeader("Content-Type", "application/json")
                    .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                    .build();

            log.info("Calling LLM API at {}", baseUrl + "/v1/chat/completions");

            try (Response response = httpClient.newCall(request).execute()) {
                log.info("LLM API response code: {}", response.code());

                if (!response.isSuccessful()) {
                    String errorBody = response.body() != null ? response.body().string() : "no body";
                    log.error("LLM API error: {} - {}", response.code(), errorBody);
                    return null;
                }

                ResponseBody body = response.body();
                if (body == null) {
                    log.error("LLM API returned null body");
                    return null;
                }

                String responseStr = body.string();
                log.debug("LLM response length: {} chars", responseStr.length());

                JsonNode root = objectMapper.readTree(responseStr);
                JsonNode choices = root.path("choices");
                if (choices.isArray() && !choices.isEmpty()) {
                    String content = choices.get(0).path("message").path("content").asText();
                    log.info("LLM extraction successful, response length: {} chars", content.length());
                    return content;
                } else {
                    log.error("LLM response has no choices: {}", responseStr);
                }
            }
        } catch (Exception e) {
            log.error("LLM API call failed with exception: {}", e.getMessage(), e);
        }
        return null;
    }

    /**
     * Build the extraction prompt.
     */
    private String buildExtractionPrompt() {
        return """
            You are a memory extraction assistant for SaveVia, a Canadian credit card advisor app.

            Analyze the conversation and extract user information as JSON. Only include facts explicitly stated or strongly implied. Use null for unknown values.

            Output ONLY valid JSON in this exact format:
            {
              "identity": {
                "user_type": "student|new_immigrant|pr_holder|citizen|work_permit|visitor|null",
                "residency_years": number or null,
                "occupation": "string or null",
                "income_range": "under_30k|30k_60k|60k_100k|100k_plus|null"
              },
              "spending": {
                "monthly_grocery": number or null,
                "monthly_gas": number or null,
                "monthly_dining": number or null,
                "monthly_online": number or null,
                "monthly_travel": number or null,
                "monthly_total": number or null
              },
              "preference": {
                "annual_fee_tolerance": "0|50|100|200|500|unlimited|null",
                "reward_type": "cashback|points|travel_miles|null",
                "preferred_banks": ["array"] or null,
                "preferred_networks": ["VISA","Mastercard","AMEX"] or null
              },
              "exclusion": {
                "excluded_banks": ["array"] or null,
                "excluded_networks": ["array"] or null,
                "excluded_cards": ["array"] or null
              },
              "lifestyle": {
                "travel_frequency": "never|yearly|quarterly|monthly|weekly|null",
                "has_children": true|false|null,
                "has_pets": true|false|null,
                "commute_method": "car|transit|bike|remote|null"
              },
              "recommendations": [
                {
                  "card_name": "string",
                  "card_id": number or null,
                  "user_response": "accepted|rejected|considering|null"
                }
              ],
              "summary": "One paragraph summary of key insights (max 200 chars)"
            }

            Rules:
            - Only extract information explicitly mentioned or strongly implied
            - For spending amounts, convert to monthly CAD estimates
            - summary should focus on actionable insights for future recommendations
            - If nothing is mentioned for a category, use null values
            """;
    }

    /**
     * Parse LLM response into DTO.
     */
    private MemoryExtractionResultDTO parseExtractionResult(String jsonResponse) {
        try {
            JsonNode root = objectMapper.readTree(jsonResponse);

            MemoryExtractionResultDTO result = new MemoryExtractionResultDTO();

            // Parse identity
            JsonNode identity = root.path("identity");
            if (!identity.isMissingNode()) {
                result.setIdentity(MemoryExtractionResultDTO.IdentityInfo.builder()
                        .userType(getTextOrNull(identity, "user_type"))
                        .residencyYears(getIntOrNull(identity, "residency_years"))
                        .occupation(getTextOrNull(identity, "occupation"))
                        .incomeRange(getTextOrNull(identity, "income_range"))
                        .build());
            }

            // Parse spending
            JsonNode spending = root.path("spending");
            if (!spending.isMissingNode()) {
                result.setSpending(MemoryExtractionResultDTO.SpendingInfo.builder()
                        .monthlyGrocery(getIntOrNull(spending, "monthly_grocery"))
                        .monthlyGas(getIntOrNull(spending, "monthly_gas"))
                        .monthlyDining(getIntOrNull(spending, "monthly_dining"))
                        .monthlyOnline(getIntOrNull(spending, "monthly_online"))
                        .monthlyTravel(getIntOrNull(spending, "monthly_travel"))
                        .monthlyTotal(getIntOrNull(spending, "monthly_total"))
                        .build());
            }

            // Parse preference
            JsonNode preference = root.path("preference");
            if (!preference.isMissingNode()) {
                result.setPreference(MemoryExtractionResultDTO.PreferenceInfo.builder()
                        .annualFeeTolerance(getTextOrNull(preference, "annual_fee_tolerance"))
                        .rewardType(getTextOrNull(preference, "reward_type"))
                        .preferredBanks(getStringListOrNull(preference, "preferred_banks"))
                        .preferredNetworks(getStringListOrNull(preference, "preferred_networks"))
                        .build());
            }

            // Parse exclusion
            JsonNode exclusion = root.path("exclusion");
            if (!exclusion.isMissingNode()) {
                result.setExclusion(MemoryExtractionResultDTO.ExclusionInfo.builder()
                        .excludedBanks(getStringListOrNull(exclusion, "excluded_banks"))
                        .excludedNetworks(getStringListOrNull(exclusion, "excluded_networks"))
                        .excludedCards(getStringListOrNull(exclusion, "excluded_cards"))
                        .build());
            }

            // Parse lifestyle
            JsonNode lifestyle = root.path("lifestyle");
            if (!lifestyle.isMissingNode()) {
                result.setLifestyle(MemoryExtractionResultDTO.LifestyleInfo.builder()
                        .travelFrequency(getTextOrNull(lifestyle, "travel_frequency"))
                        .hasChildren(getBooleanOrNull(lifestyle, "has_children"))
                        .hasPets(getBooleanOrNull(lifestyle, "has_pets"))
                        .commuteMethod(getTextOrNull(lifestyle, "commute_method"))
                        .build());
            }

            // Parse recommendations
            JsonNode recommendations = root.path("recommendations");
            if (recommendations.isArray()) {
                List<MemoryExtractionResultDTO.RecommendationInfo> recList = new ArrayList<>();
                for (JsonNode rec : recommendations) {
                    recList.add(MemoryExtractionResultDTO.RecommendationInfo.builder()
                            .cardName(getTextOrNull(rec, "card_name"))
                            .cardId(getLongOrNull(rec, "card_id"))
                            .userResponse(getTextOrNull(rec, "user_response"))
                            .build());
                }
                result.setRecommendations(recList);
            }

            // Parse summary
            result.setSummary(getTextOrNull(root, "summary"));

            return result;

        } catch (Exception e) {
            log.error("Failed to parse extraction result: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Save extracted memory to database.
     */
    public void saveExtractedMemory(Long userId, MemoryExtractionResultDTO result, Long conversationId) {
        String source = MemoryConstants.Source.INFERRED;

        // Save identity facts
        if (result.getIdentity() != null) {
            var id = result.getIdentity();
            if (id.getUserType() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.IDENTITY,
                        MemoryConstants.IdentityKey.USER_TYPE, id.getUserType(), source);
            }
            if (id.getResidencyYears() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.IDENTITY,
                        MemoryConstants.IdentityKey.RESIDENCY_YEARS, String.valueOf(id.getResidencyYears()), source);
            }
            if (id.getOccupation() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.IDENTITY,
                        MemoryConstants.IdentityKey.OCCUPATION, id.getOccupation(), source);
            }
            if (id.getIncomeRange() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.IDENTITY,
                        MemoryConstants.IdentityKey.INCOME_RANGE, id.getIncomeRange(), source);
            }
        }

        // Save spending facts
        if (result.getSpending() != null) {
            var sp = result.getSpending();
            if (sp.getMonthlyGrocery() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_GROCERY, String.valueOf(sp.getMonthlyGrocery()), source);
            }
            if (sp.getMonthlyGas() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_GAS, String.valueOf(sp.getMonthlyGas()), source);
            }
            if (sp.getMonthlyDining() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_DINING, String.valueOf(sp.getMonthlyDining()), source);
            }
            if (sp.getMonthlyOnline() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_ONLINE, String.valueOf(sp.getMonthlyOnline()), source);
            }
            if (sp.getMonthlyTravel() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_TRAVEL, String.valueOf(sp.getMonthlyTravel()), source);
            }
            if (sp.getMonthlyTotal() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.SPENDING,
                        MemoryConstants.SpendingKey.MONTHLY_TOTAL, String.valueOf(sp.getMonthlyTotal()), source);
            }
        }

        // Save preference facts
        if (result.getPreference() != null) {
            var pref = result.getPreference();
            if (pref.getAnnualFeeTolerance() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.PREFERENCE,
                        MemoryConstants.PreferenceKey.ANNUAL_FEE_TOLERANCE, pref.getAnnualFeeTolerance(), source);
            }
            if (pref.getRewardType() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.PREFERENCE,
                        MemoryConstants.PreferenceKey.REWARD_TYPE, pref.getRewardType(), source);
            }
            if (pref.getPreferredBanks() != null && !pref.getPreferredBanks().isEmpty()) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.PREFERENCE,
                        MemoryConstants.PreferenceKey.PREFERRED_BANKS, toJsonArray(pref.getPreferredBanks()), source);
            }
            if (pref.getPreferredNetworks() != null && !pref.getPreferredNetworks().isEmpty()) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.PREFERENCE,
                        MemoryConstants.PreferenceKey.PREFERRED_NETWORKS, toJsonArray(pref.getPreferredNetworks()), source);
            }
        }

        // Save exclusion facts
        if (result.getExclusion() != null) {
            var excl = result.getExclusion();
            if (excl.getExcludedBanks() != null && !excl.getExcludedBanks().isEmpty()) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.EXCLUSION,
                        MemoryConstants.ExclusionKey.EXCLUDED_BANKS, toJsonArray(excl.getExcludedBanks()), source);
            }
            if (excl.getExcludedNetworks() != null && !excl.getExcludedNetworks().isEmpty()) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.EXCLUSION,
                        MemoryConstants.ExclusionKey.EXCLUDED_NETWORKS, toJsonArray(excl.getExcludedNetworks()), source);
            }
            if (excl.getExcludedCards() != null && !excl.getExcludedCards().isEmpty()) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.EXCLUSION,
                        MemoryConstants.ExclusionKey.EXCLUDED_CARDS, toJsonArray(excl.getExcludedCards()), source);
            }
        }

        // Save lifestyle facts
        if (result.getLifestyle() != null) {
            var life = result.getLifestyle();
            if (life.getTravelFrequency() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.LIFESTYLE,
                        MemoryConstants.LifestyleKey.TRAVEL_FREQUENCY, life.getTravelFrequency(), source);
            }
            if (life.getHasChildren() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.LIFESTYLE,
                        MemoryConstants.LifestyleKey.HAS_CHILDREN, String.valueOf(life.getHasChildren()), source);
            }
            if (life.getHasPets() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.LIFESTYLE,
                        MemoryConstants.LifestyleKey.HAS_PETS, String.valueOf(life.getHasPets()), source);
            }
            if (life.getCommuteMethod() != null) {
                memoryService.saveProfileFact(userId, MemoryConstants.Category.LIFESTYLE,
                        MemoryConstants.LifestyleKey.COMMUTE_METHOD, life.getCommuteMethod(), source);
            }
        }

        // Save summary
        if (result.getSummary() != null && !result.getSummary().isEmpty()) {
            String keyTopics = extractKeyTopics(result);
            String recommendations = extractRecommendations(result);
            String conversationIds = "[" + conversationId + "]";

            memoryService.saveSummary(userId, result.getSummary(), keyTopics, recommendations, conversationIds);
        }
    }

    private String extractKeyTopics(MemoryExtractionResultDTO result) {
        List<String> topics = new ArrayList<>();
        if (result.getSpending() != null) {
            if (result.getSpending().getMonthlyGrocery() != null) topics.add("grocery");
            if (result.getSpending().getMonthlyDining() != null) topics.add("dining");
            if (result.getSpending().getMonthlyGas() != null) topics.add("gas");
            if (result.getSpending().getMonthlyTravel() != null) topics.add("travel");
        }
        if (result.getPreference() != null && result.getPreference().getRewardType() != null) {
            topics.add(result.getPreference().getRewardType());
        }
        return toJsonArray(topics);
    }

    private String extractRecommendations(MemoryExtractionResultDTO result) {
        if (result.getRecommendations() == null || result.getRecommendations().isEmpty()) {
            return "[]";
        }
        try {
            return objectMapper.writeValueAsString(result.getRecommendations());
        } catch (Exception e) {
            return "[]";
        }
    }

    private void markExtractionProcessed(Long conversationId, Long userId) {
        MemoryExtractionLog log = extractionLogMapper.selectByConversationId(conversationId);
        if (log == null) {
            log = MemoryExtractionLog.builder()
                    .conversationId(conversationId)
                    .userId(userId)
                    .status(MemoryConstants.ExtractionStatus.SUCCESS)
                    .build();
            extractionLogMapper.insert(log);
        } else {
            extractionLogMapper.updateStatusProcessed(conversationId);
        }
    }

    private void markExtractionFailed(Long conversationId, Long userId, String errorMessage) {
        MemoryExtractionLog log = extractionLogMapper.selectByConversationId(conversationId);
        if (log == null) {
            log = MemoryExtractionLog.builder()
                    .conversationId(conversationId)
                    .userId(userId)
                    .status(MemoryConstants.ExtractionStatus.FAILED)
                    .errorMessage(errorMessage)
                    .build();
            extractionLogMapper.insert(log);
        } else {
            extractionLogMapper.updateStatusFailed(conversationId, errorMessage);
        }
    }

    // JSON helper methods
    private String getTextOrNull(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNull() || value.isMissingNode() || "null".equals(value.asText())) {
            return null;
        }
        return value.asText();
    }

    private Integer getIntOrNull(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNull() || value.isMissingNode() || !value.isNumber()) {
            return null;
        }
        return value.asInt();
    }

    private Long getLongOrNull(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNull() || value.isMissingNode() || !value.isNumber()) {
            return null;
        }
        return value.asLong();
    }

    private Boolean getBooleanOrNull(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNull() || value.isMissingNode()) {
            return null;
        }
        if (value.isBoolean()) {
            return value.asBoolean();
        }
        return null;
    }

    private List<String> getStringListOrNull(JsonNode node, String field) {
        JsonNode value = node.path(field);
        if (value.isNull() || value.isMissingNode() || !value.isArray()) {
            return null;
        }
        List<String> list = new ArrayList<>();
        for (JsonNode item : value) {
            if (!item.isNull()) {
                list.add(item.asText());
            }
        }
        return list.isEmpty() ? null : list;
    }

    private String toJsonArray(List<String> list) {
        if (list == null || list.isEmpty()) {
            return "[]";
        }
        try {
            return objectMapper.writeValueAsString(list);
        } catch (Exception e) {
            return "[]";
        }
    }
}
