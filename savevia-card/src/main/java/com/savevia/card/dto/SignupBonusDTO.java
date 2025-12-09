package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SignupBonusDTO {

    private BigDecimal bonusAmount;
    private BigDecimal minSpend;
    private Integer daysToComplete;
    private String description;
}
