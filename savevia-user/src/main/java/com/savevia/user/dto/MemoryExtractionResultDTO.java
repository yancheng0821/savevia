package com.savevia.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * DTO representing the result of LLM memory extraction from a conversation.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemoryExtractionResultDTO {

    /**
     * Identity information extracted
     */
    private IdentityInfo identity;

    /**
     * Spending patterns extracted
     */
    private SpendingInfo spending;

    /**
     * User preferences extracted
     */
    private PreferenceInfo preference;

    /**
     * Items user explicitly excluded
     */
    private ExclusionInfo exclusion;

    /**
     * Lifestyle context extracted
     */
    private LifestyleInfo lifestyle;

    /**
     * Card recommendations made and user responses
     */
    private List<RecommendationInfo> recommendations;

    /**
     * Brief summary of the conversation
     */
    private String summary;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IdentityInfo {
        private String userType;
        private Integer residencyYears;
        private String occupation;
        private String incomeRange;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SpendingInfo {
        private Integer monthlyGrocery;
        private Integer monthlyGas;
        private Integer monthlyDining;
        private Integer monthlyOnline;
        private Integer monthlyTravel;
        private Integer monthlyTotal;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PreferenceInfo {
        private String annualFeeTolerance;
        private String rewardType;
        private List<String> preferredBanks;
        private List<String> preferredNetworks;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExclusionInfo {
        private List<String> excludedBanks;
        private List<String> excludedNetworks;
        private List<String> excludedCards;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LifestyleInfo {
        private String travelFrequency;
        private Boolean hasChildren;
        private Boolean hasPets;
        private String commuteMethod;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RecommendationInfo {
        private String cardName;
        private Long cardId;
        private String userResponse; // accepted, rejected, considering
    }
}
