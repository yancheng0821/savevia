package com.savevia.card.service;

import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.savevia.card.dto.CreditCardDTO;
import com.savevia.card.dto.RewardRuleDTO;
import com.savevia.card.dto.SignupBonusDTO;
import com.savevia.card.entity.CreditCard;
import com.savevia.card.entity.RewardRule;
import com.savevia.card.mapper.CreditCardMapper;
import com.savevia.card.mapper.RewardRuleMapper;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class CreditCardService {

    private final CreditCardMapper creditCardMapper;
    private final RewardRuleMapper rewardRuleMapper;
    private final AffiliateService affiliateService;

    @Cacheable(value = "cards", key = "'all'")
    public List<CreditCardDTO> getAllCards() {
        List<CreditCard> cards = creditCardMapper.selectAllActive();

        List<Long> cardIds = cards.stream().map(CreditCard::getId).toList();
        Map<Long, List<RewardRule>> rulesMap = getRulesMap(cardIds);

        return cards.stream()
                .map(card -> toDTO(card, rulesMap.get(card.getId())))
                .toList();
    }

    @Cacheable(value = "cards", key = "#id")
    public CreditCardDTO getCardById(Long id) {
        CreditCard card = creditCardMapper.selectById(id);
        if (card == null || !card.getIsActive()) {
            throw new BusinessException(ErrorCode.CARD_NOT_FOUND);
        }

        List<RewardRule> rules = rewardRuleMapper.selectByCardId(id);
        return toDTO(card, rules);
    }

    @Cacheable(value = "cards", key = "'bank:' + #bank")
    public List<CreditCardDTO> getCardsByBank(String bank) {
        List<CreditCard> cards = creditCardMapper.selectByBank(bank.toUpperCase());

        List<Long> cardIds = cards.stream().map(CreditCard::getId).toList();
        Map<Long, List<RewardRule>> rulesMap = getRulesMap(cardIds);

        return cards.stream()
                .map(card -> toDTO(card, rulesMap.get(card.getId())))
                .toList();
    }

    public List<CreditCardDTO> getCardsByIds(List<Long> ids) {
        if (ids == null || ids.isEmpty()) {
            return List.of();
        }

        List<CreditCard> cards = creditCardMapper.selectByIds(ids);
        Map<Long, List<RewardRule>> rulesMap = getRulesMap(ids);

        return cards.stream()
                .map(card -> toDTO(card, rulesMap.get(card.getId())))
                .toList();
    }

    private Map<Long, List<RewardRule>> getRulesMap(List<Long> cardIds) {
        if (cardIds == null || cardIds.isEmpty()) {
            return Map.of();
        }

        List<RewardRule> allRules = rewardRuleMapper.selectByCardIds(cardIds);

        return allRules.stream()
                .collect(Collectors.groupingBy(RewardRule::getCardId));
    }

    private CreditCardDTO toDTO(CreditCard card, List<RewardRule> rules) {
        SignupBonusDTO signupBonus = parseSignupBonus(card.getSignupBonusJson(), card.getId());

        List<RewardRuleDTO> ruleDTOs = rules != null
                ? rules.stream().map(this::toRuleDTO).toList()
                : List.of();

        // 获取联盟链接（如果存在）
        var affiliateLink = affiliateService.getAffiliateLink(card.getId()).orElse(null);

        return CreditCardDTO.builder()
                .id(card.getId())
                .bank(card.getBank())
                .name(card.getName())
                .cardType(card.getCardType())
                .annualFee(card.getAnnualFee())
                .baseRewardRate(card.getBaseRewardRate())
                .rewardType(card.getRewardType())
                .pointProgram(card.getPointProgram())
                .pointValue(card.getPointValue())
                .imageUrl(card.getImageUrl())
                .applyUrl(card.getApplyUrl())
                .noFxFee(card.getNoFxFee() != null && card.getNoFxFee())
                .signupBonus(signupBonus)
                .rewardRules(ruleDTOs)
                .amexTravelBonusRate(card.getAmexTravelBonusRate())
                .affiliateLink(affiliateLink)
                .build();
    }

    private RewardRuleDTO toRuleDTO(RewardRule rule) {
        return RewardRuleDTO.builder()
                .id(rule.getId())
                .category(rule.getCategoryEnum())
                .rewardRate(rule.getRewardRate())
                .monthlyCapAmount(rule.getMonthlyCapAmount())
                .description(rule.getDescription())
                .build();
    }

    /**
     * 解析 signup bonus JSON，兼容新旧格式
     * - description: 返回英文描述（旧前端兼容）
     * - descriptionI18n: 返回完整多语言对象（新前端用）
     */
    private SignupBonusDTO parseSignupBonus(String json, Long cardId) {
        if (json == null || json.isBlank()) {
            return null;
        }

        try {
            JSONObject obj = JSONUtil.parseObj(json);

            SignupBonusDTO.SignupBonusDTOBuilder builder = SignupBonusDTO.builder()
                    .bonusAmount(obj.getBigDecimal("bonusAmount"))
                    .minSpend(obj.getBigDecimal("minSpend"))
                    .daysToComplete(obj.getInt("daysToComplete"));

            // 处理 description - 可能是字符串或 i18n 对象
            Object desc = obj.get("description");
            if (desc instanceof String) {
                // 旧格式：直接是字符串
                builder.description((String) desc);
            } else if (desc instanceof JSONObject) {
                // 新格式：i18n 对象
                JSONObject i18n = (JSONObject) desc;
                // description 返回英文（旧前端兼容）
                builder.description(i18n.getStr("en"));
                // descriptionI18n 返回完整对象（新前端用）
                builder.descriptionI18n(i18n.toBean(new cn.hutool.core.lang.TypeReference<java.util.Map<String, String>>() {}));
            }

            return builder.build();
        } catch (Exception e) {
            log.warn("Failed to parse signup bonus for card {}: {}", cardId, e.getMessage());
            return null;
        }
    }
}
