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
public class CreditCardDTO {

    private Long id;
    private String bank;
    private String name;
    private String cardType;
    private BigDecimal annualFee;
    private BigDecimal baseRewardRate;
    private String imageUrl;
    private String applyUrl;
    private Boolean noFxFee;
    private List<RewardRuleDTO> rewardRules;
    private Object signupBonus; // Allow any structure from card service
}
