package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CardUsageTipDTO {

    private Long id;

    private TipType tipType;

    private String title;

    private String content;

    private String icon;
}
