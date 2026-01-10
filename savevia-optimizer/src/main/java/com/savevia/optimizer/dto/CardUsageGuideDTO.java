package com.savevia.optimizer.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
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
@JsonIgnoreProperties(ignoreUnknown = true)
public class CardUsageGuideDTO {
    private Long cardId;
    private String rewardType;
    private BigDecimal pointValue;
    private String pointProgram;
    private List<TransferPartnerDTO> transferPartners;
    private List<CardUsageTipDTO> tips;
}
