package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 联盟申卡链接数据传输对象
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AffiliateLinkDTO {

    /**
     * 联盟链接ID
     */
    private Long id;

    /**
     * 卡片ID
     */
    private Long cardId;

    /**
     * 银行名称 (e.g., "American Express", "RBC", "TD")
     */
    private String bankName;

    /**
     * 联盟类型 (e.g., "AMEX_AFFILIATE", "RBC_AFFILIATE")
     */
    private String affiliateType;

    /**
     * 联盟申卡链接
     */
    private String affiliateUrl;

    /**
     * 预估佣金金额 (CAD)
     */
    private Double commissionAmount;

    /**
     * 是否激活
     */
    private Boolean isActive;
}
