package com.savevia.card.service;

import com.savevia.card.dto.AffiliateLinkDTO;
import com.savevia.card.entity.AffiliateClickTracking;
import com.savevia.card.entity.AffiliateLink;
import com.savevia.card.mapper.AffiliateClickTrackingMapper;
import com.savevia.card.mapper.AffiliateLinkMapper;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Affiliate Service - 管理银行申卡联盟链接和点击追踪
 *
 * 特点：
 * 1. 联盟链接完全由数据库配置，无需修改代码
 * 2. 支持灵活的添加、修改、删除操作
 * 3. 缓存优化性能
 * 4. 完整的点击追踪
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AffiliateService {

    private final AffiliateLinkMapper affiliateLinkMapper;
    private final AffiliateClickTrackingMapper affiliateClickTrackingMapper;

    /**
     * 获取卡片的联盟链接（从数据库）
     * 返回第一个活跃的链接，优先使用已配置的链接
     * @param cardId 卡片ID
     * @return 联盟链接信息
     */
    @Cacheable(value = "affiliateLinks", key = "#cardId")
    public Optional<AffiliateLinkDTO> getAffiliateLink(Long cardId) {
        AffiliateLink link = affiliateLinkMapper.selectFirstActiveByCardId(cardId);
        if (link == null) {
            return Optional.empty();
        }
        return Optional.of(toDTO(link));
    }

    /**
     * 获取卡片的所有活跃联盟链接
     * @param cardId 卡片ID
     * @return 联盟链接列表
     */
    @Cacheable(value = "affiliateLinksAll", key = "#cardId")
    public List<AffiliateLinkDTO> getAllAffiliateLinks(Long cardId) {
        List<AffiliateLink> links = affiliateLinkMapper.selectByCardIdActive(cardId);
        return links.stream().map(this::toDTO).toList();
    }

    /**
     * 检查是否有联盟链接
     * @param cardId 卡片ID
     * @return true 如果有至少一个活跃的联盟链接
     */
    public boolean hasAffiliateLink(Long cardId) {
        return getAffiliateLink(cardId).isPresent();
    }

    /**
     * 追踪用户点击申卡链接
     * @param userId 用户ID (可能为null，如未登录)
     * @param cardId 卡片ID
     * @param affiliateLinkId 联盟链接ID
     * @param bankName 银行名称
     */
    public void trackAffiliateClick(Long userId, Long cardId, Long affiliateLinkId, String bankName) {
        try {
            AffiliateClickTracking tracking = AffiliateClickTracking.builder()
                .userId(userId)
                .cardId(cardId)
                .affiliateLinkId(affiliateLinkId)
                .bankName(bankName)
                .build();

            affiliateClickTrackingMapper.insert(tracking);
            log.info("Tracked affiliate click - userId: {}, cardId: {}, affiliateLinkId: {}, bank: {}",
                    userId, cardId, affiliateLinkId, bankName);
        } catch (Exception e) {
            log.error("Failed to track affiliate click", e);
            // 不要让追踪失败影响用户体验
        }
    }

    /**
     * 获取卡片的今日点击统计
     * @param cardId 卡片ID
     * @return 今日点击数
     */
    public int getClickCountToday(Long cardId) {
        return affiliateClickTrackingMapper.getClickCountToday(cardId);
    }

    /**
     * 获取特定银行的今日点击统计
     * @param cardId 卡片ID
     * @param bankName 银行名称
     * @return 今日点击数
     */
    public int getClickCountTodayByBank(Long cardId, String bankName) {
        return affiliateClickTrackingMapper.getClickCountTodayByBank(cardId, bankName);
    }

    /**
     * 获取特定联盟链接的今日点击统计
     * @param affiliateLinkId 联盟链接ID
     * @return 今日点击数
     */
    public int getClickCountTodayByAffiliate(Long affiliateLinkId) {
        return affiliateClickTrackingMapper.getClickCountTodayByAffiliate(affiliateLinkId);
    }

    // ==================== 管理接口 ====================

    /**
     * 添加新的联盟链接
     * @param affiliateLink 联盟链接信息
     * @return 新建的链接ID
     */
    @CacheEvict(value = {"affiliateLinks", "affiliateLinksAll"}, allEntries = true)
    public Long addAffiliateLink(AffiliateLink affiliateLink) {
        // 验证卡片是否存在
        if (affiliateLink.getCardId() == null || affiliateLink.getCardId() <= 0) {
            throw new BusinessException("卡片ID不能为空");
        }

        affiliateLink.setIsActive(true);
        int result = affiliateLinkMapper.insert(affiliateLink);

        if (result > 0) {
            log.info("Added affiliate link - cardId: {}, bank: {}, type: {}",
                    affiliateLink.getCardId(), affiliateLink.getBankName(), affiliateLink.getAffiliateType());
            return affiliateLink.getId();
        }

        throw new BusinessException("添加联盟链接失败");
    }

    /**
     * 更新联盟链接
     * @param affiliateLink 联盟链接信息（需要包含ID）
     */
    @CacheEvict(value = {"affiliateLinks", "affiliateLinksAll"}, allEntries = true)
    public void updateAffiliateLink(AffiliateLink affiliateLink) {
        if (affiliateLink.getId() == null || affiliateLink.getId() <= 0) {
            throw new BusinessException("链接ID不能为空");
        }

        AffiliateLink existing = affiliateLinkMapper.selectById(affiliateLink.getId());
        if (existing == null) {
            throw new BusinessException("联盟链接不存在");
        }

        int result = affiliateLinkMapper.update(affiliateLink);

        if (result > 0) {
            log.info("Updated affiliate link - id: {}", affiliateLink.getId());
        } else {
            throw new BusinessException("更新联盟链接失败");
        }
    }

    /**
     * 删除联盟链接
     * @param affiliateLinkId 联盟链接ID
     */
    @CacheEvict(value = {"affiliateLinks", "affiliateLinksAll"}, allEntries = true)
    public void deleteAffiliateLink(Long affiliateLinkId) {
        if (affiliateLinkId == null || affiliateLinkId <= 0) {
            throw new BusinessException("链接ID不能为空");
        }

        int result = affiliateLinkMapper.deleteById(affiliateLinkId);

        if (result > 0) {
            log.info("Deleted affiliate link - id: {}", affiliateLinkId);
        } else {
            throw new BusinessException("删除联盟链接失败");
        }
    }

    /**
     * 获取所有活跃的联盟链接
     * @return 联盟链接列表
     */
    @Cacheable(value = "allActiveAffiliateLinks", key = "'all'")
    public List<AffiliateLinkDTO> getAllActiveLinks() {
        List<AffiliateLink> links = affiliateLinkMapper.selectAllActive();
        return links.stream().map(this::toDTO).toList();
    }

    /**
     * 根据银行名称获取所有活跃链接
     * @param bankName 银行名称
     * @return 联盟链接列表
     */
    @Cacheable(value = "affiliateLinksByBank", key = "#bankName")
    public List<AffiliateLinkDTO> getLinksByBank(String bankName) {
        List<AffiliateLink> links = affiliateLinkMapper.selectByBankNameActive(bankName);
        return links.stream().map(this::toDTO).toList();
    }

    // ==================== 工具方法 ====================

    /**
     * 实体转DTO
     */
    private AffiliateLinkDTO toDTO(AffiliateLink link) {
        return AffiliateLinkDTO.builder()
            .id(link.getId())
            .cardId(link.getCardId())
            .bankName(link.getBankName())
            .affiliateType(link.getAffiliateType())
            .affiliateUrl(link.getAffiliateUrl())
            .commissionAmount(link.getCommissionAmount() != null ? link.getCommissionAmount().doubleValue() : null)
            .isActive(link.getIsActive())
            .build();
    }
}
