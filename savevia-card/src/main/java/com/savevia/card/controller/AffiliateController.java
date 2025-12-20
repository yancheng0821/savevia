package com.savevia.card.controller;

import com.savevia.card.dto.AffiliateLinkDTO;
import com.savevia.card.entity.AffiliateLink;
import com.savevia.card.service.AffiliateService;
import com.savevia.common.response.Result;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

/**
 * 联盟链接管理API
 *
 * 功能：
 * 1. 获取卡片的联盟申卡链接
 * 2. 追踪用户点击申卡链接
 * 3. 获取点击统计
 * 4. 管理联盟链接配置（添加、修改、删除）
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/affiliate")
@RequiredArgsConstructor
public class AffiliateController {

    private final AffiliateService affiliateService;

    // ==================== 公共接口 ====================

    /**
     * 获取卡片的联盟申卡链接
     * GET /api/v1/affiliate/links/{cardId}
     *
     * @param cardId 卡片ID
     * @return 联盟链接信息（如果存在）
     */
    @GetMapping("/links/{cardId}")
    public Result<AffiliateLinkDTO> getAffiliateLink(@PathVariable Long cardId) {
        Optional<AffiliateLinkDTO> affiliateLink = affiliateService.getAffiliateLink(cardId);
        return Result.success(affiliateLink.orElse(null));
    }

    /**
     * 获取卡片的所有联盟申卡链接
     * GET /api/v1/affiliate/links-all/{cardId}
     *
     * @param cardId 卡片ID
     * @return 联盟链接列表
     */
    @GetMapping("/links-all/{cardId}")
    public Result<List<AffiliateLinkDTO>> getAllAffiliateLinks(@PathVariable Long cardId) {
        List<AffiliateLinkDTO> links = affiliateService.getAllAffiliateLinks(cardId);
        return Result.success(links);
    }

    /**
     * 追踪用户点击申卡链接
     * POST /api/v1/affiliate/track-click
     *
     * 请求体：
     * {
     *   "cardId": 1,
     *   "affiliateLinkId": 123,
     *   "bankName": "American Express",
     *   "userId": 456  // 可选，未登录时为null
     * }
     *
     * @param request 追踪请求
     * @return 追踪结果
     */
    @PostMapping("/track-click")
    public Result<Void> trackAffiliateClick(@RequestBody TrackClickRequest request) {
        affiliateService.trackAffiliateClick(
            request.getUserId(),
            request.getCardId(),
            request.getAffiliateLinkId(),
            request.getBankName()
        );
        return Result.success(null);
    }

    /**
     * 获取卡片的今日点击统计
     * GET /api/v1/affiliate/stats/{cardId}/today
     *
     * @param cardId 卡片ID
     * @return 今日点击数
     */
    @GetMapping("/stats/{cardId}/today")
    public Result<Integer> getClickCountToday(@PathVariable Long cardId) {
        int count = affiliateService.getClickCountToday(cardId);
        return Result.success(count);
    }

    /**
     * 获取银行的今日点击统计
     * GET /api/v1/affiliate/stats/{cardId}/bank/{bankName}/today
     *
     * @param cardId 卡片ID
     * @param bankName 银行名称
     * @return 今日点击数
     */
    @GetMapping("/stats/{cardId}/bank/{bankName}/today")
    public Result<Integer> getClickCountTodayByBank(
        @PathVariable Long cardId,
        @PathVariable String bankName) {
        int count = affiliateService.getClickCountTodayByBank(cardId, bankName);
        return Result.success(count);
    }

    // ==================== 管理接口 ====================

    /**
     * 添加新的联盟链接
     * POST /api/v1/affiliate/admin/links
     *
     * @param affiliateLink 联盟链接信息
     * @return 新建的链接ID
     */
    @PostMapping("/admin/links")
    public Result<Long> addAffiliateLink(@RequestBody AffiliateLink affiliateLink) {
        Long id = affiliateService.addAffiliateLink(affiliateLink);
        return Result.success(id);
    }

    /**
     * 更新联盟链接
     * PUT /api/v1/affiliate/admin/links/{id}
     *
     * @param id 联盟链接ID
     * @param affiliateLink 更新的信息
     * @return 更新结果
     */
    @PutMapping("/admin/links/{id}")
    public Result<Void> updateAffiliateLink(
        @PathVariable Long id,
        @RequestBody AffiliateLink affiliateLink) {
        affiliateLink.setId(id);
        affiliateService.updateAffiliateLink(affiliateLink);
        return Result.success(null);
    }

    /**
     * 删除联盟链接
     * DELETE /api/v1/affiliate/admin/links/{id}
     *
     * @param id 联盟链接ID
     * @return 删除结果
     */
    @DeleteMapping("/admin/links/{id}")
    public Result<Void> deleteAffiliateLink(@PathVariable Long id) {
        affiliateService.deleteAffiliateLink(id);
        return Result.success(null);
    }

    /**
     * 获取所有活跃的联盟链接
     * GET /api/v1/affiliate/admin/links-all
     *
     * @return 联盟链接列表
     */
    @GetMapping("/admin/links-all")
    public Result<List<AffiliateLinkDTO>> getAllActiveLinks() {
        List<AffiliateLinkDTO> links = affiliateService.getAllActiveLinks();
        return Result.success(links);
    }

    /**
     * 获取特定银行的所有活跃链接
     * GET /api/v1/affiliate/admin/bank/{bankName}
     *
     * @param bankName 银行名称
     * @return 联盟链接列表
     */
    @GetMapping("/admin/bank/{bankName}")
    public Result<List<AffiliateLinkDTO>> getLinksByBank(@PathVariable String bankName) {
        List<AffiliateLinkDTO> links = affiliateService.getLinksByBank(bankName);
        return Result.success(links);
    }

    // ==================== 请求/响应类 ====================

    /**
     * 追踪请求体
     */
    @lombok.Data
    public static class TrackClickRequest {
        private Long cardId;
        private Long affiliateLinkId;
        private String bankName;
        private Long userId;
    }
}
