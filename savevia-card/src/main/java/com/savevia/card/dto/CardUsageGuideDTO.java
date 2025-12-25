package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CardUsageGuideDTO {

    private Long cardId;

    private RewardType rewardType;

    private BigDecimal pointValue;

    private String pointProgram;

    private List<TransferPartnerDTO> transferPartners;

    private List<CardUsageTipDTO> tips;
}
