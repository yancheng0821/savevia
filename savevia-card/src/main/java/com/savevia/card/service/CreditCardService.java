package com.savevia.card.service;

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
        SignupBonusDTO signupBonus = null;
        if (card.getSignupBonusJson() != null) {
            try {
                signupBonus = JSONUtil.toBean(card.getSignupBonusJson(), SignupBonusDTO.class);
            } catch (Exception e) {
                log.warn("Failed to parse signup bonus for card {}: {}", card.getId(), e.getMessage());
            }
        }

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
                .imageUrl(card.getImageUrl())
                .applyUrl(card.getApplyUrl())
                .noFxFee(card.getNoFxFee() != null && card.getNoFxFee())
                .signupBonus(signupBonus)
                .rewardRules(ruleDTOs)
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
}
