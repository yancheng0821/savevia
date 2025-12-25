package com.savevia.card.service;

import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.savevia.card.dto.*;
import com.savevia.card.entity.CardUsageTip;
import com.savevia.card.entity.CreditCard;
import com.savevia.card.mapper.CardUsageTipMapper;
import com.savevia.card.mapper.CreditCardMapper;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class CardUsageTipService {

    private final CardUsageTipMapper cardUsageTipMapper;
    private final CreditCardMapper creditCardMapper;

    private static final String DEFAULT_LANG = "en";
    private static final List<String> SUPPORTED_LANGS = List.of("en", "zh", "fr", "es", "ja", "ko");

    /**
     * 获取卡片的使用指南
     */
    @Cacheable(value = "cardUsageGuide", key = "#cardId + ':' + #lang")
    public CardUsageGuideDTO getUsageGuide(Long cardId, String lang) {
        // 验证语言参数
        String language = SUPPORTED_LANGS.contains(lang) ? lang : DEFAULT_LANG;

        // 获取卡片信息
        CreditCard card = creditCardMapper.selectById(cardId);
        if (card == null || !card.getIsActive()) {
            throw new BusinessException(ErrorCode.CARD_NOT_FOUND);
        }

        // 获取使用指南
        List<CardUsageTip> tips = cardUsageTipMapper.selectByCardId(cardId);
        List<CardUsageTipDTO> tipDTOs = tips.stream()
                .map(tip -> toTipDTO(tip, language))
                .toList();

        // 解析转换伙伴
        List<TransferPartnerDTO> transferPartners = parseTransferPartners(card.getTransferPartnersJson(), language);

        // 解析奖励类型
        RewardType rewardType = parseRewardType(card.getRewardType());

        return CardUsageGuideDTO.builder()
                .cardId(cardId)
                .rewardType(rewardType)
                .pointValue(card.getPointValue())
                .pointProgram(card.getPointProgram())
                .transferPartners(transferPartners)
                .tips(tipDTOs)
                .build();
    }

    /**
     * 将实体转换为DTO，提取指定语言的内容
     */
    private CardUsageTipDTO toTipDTO(CardUsageTip tip, String lang) {
        String title = extractLocalizedText(tip.getTitleJson(), lang);
        String content = extractLocalizedText(tip.getContentJson(), lang);
        TipType tipType = parseTipType(tip.getTipType());

        return CardUsageTipDTO.builder()
                .id(tip.getId())
                .tipType(tipType)
                .title(title)
                .content(content)
                .icon(tip.getIcon())
                .build();
    }

    /**
     * 从JSON中提取指定语言的文本
     */
    private String extractLocalizedText(String json, String lang) {
        if (json == null || json.isBlank()) {
            return "";
        }

        try {
            JSONObject jsonObj = JSONUtil.parseObj(json);
            // 尝试获取指定语言，如果不存在则回退到英文
            String text = jsonObj.getStr(lang);
            if (text == null || text.isBlank()) {
                text = jsonObj.getStr(DEFAULT_LANG);
            }
            return text != null ? text : "";
        } catch (Exception e) {
            log.warn("Failed to parse localized text: {}", e.getMessage());
            return "";
        }
    }

    /**
     * 解析转换伙伴JSON
     */
    private List<TransferPartnerDTO> parseTransferPartners(String json, String lang) {
        if (json == null || json.isBlank()) {
            return List.of();
        }

        try {
            JSONArray jsonArray = JSONUtil.parseArray(json);
            List<TransferPartnerDTO> partners = new ArrayList<>();

            for (int i = 0; i < jsonArray.size(); i++) {
                JSONObject obj = jsonArray.getJSONObject(i);
                String name = obj.getStr("name");
                String ratio = obj.getStr("ratio");

                // value可能是字符串或多语言对象
                String value;
                Object valueObj = obj.get("value");
                if (valueObj instanceof JSONObject) {
                    JSONObject valueJson = (JSONObject) valueObj;
                    value = valueJson.getStr(lang);
                    if (value == null || value.isBlank()) {
                        value = valueJson.getStr(DEFAULT_LANG);
                    }
                } else {
                    value = String.valueOf(valueObj);
                }

                partners.add(TransferPartnerDTO.builder()
                        .name(name)
                        .ratio(ratio)
                        .value(value != null ? value : "")
                        .build());
            }

            return partners;
        } catch (Exception e) {
            log.warn("Failed to parse transfer partners: {}", e.getMessage());
            return List.of();
        }
    }

    /**
     * 解析奖励类型
     */
    private RewardType parseRewardType(String rewardType) {
        if (rewardType == null || rewardType.isBlank()) {
            return RewardType.CASHBACK;
        }

        try {
            return RewardType.valueOf(rewardType.toUpperCase());
        } catch (Exception e) {
            return RewardType.CASHBACK;
        }
    }

    /**
     * 解析提示类型
     */
    private TipType parseTipType(String tipType) {
        if (tipType == null || tipType.isBlank()) {
            return TipType.BEST_USE;
        }

        try {
            return TipType.valueOf(tipType.toUpperCase());
        } catch (Exception e) {
            return TipType.BEST_USE;
        }
    }
}
