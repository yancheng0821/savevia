package com.savevia.user.service;

import com.savevia.user.entity.AiUsage;
import com.savevia.user.entity.User;
import com.savevia.user.mapper.AiUsageMapper;
import com.savevia.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

@Slf4j
@Service
@RequiredArgsConstructor
public class AiUsageService {

    private final AiUsageMapper aiUsageMapper;
    private final UserMapper userMapper;

    // PRO users: 100 per month, FREE users: 3 per month
    private static final int FREE_USER_MONTHLY_LIMIT = 3;
    private static final int PRO_USER_MONTHLY_LIMIT = 100;

    private String getCurrentYearMonth() {
        return LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM"));
    }

    /**
     * Check if user is a PRO subscriber with active subscription
     */
    private boolean isProUser(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            return false;
        }

        String subscriptionType = user.getSubscriptionType();
        if (!"PRO".equals(subscriptionType)) {
            return false;
        }

        // Check if subscription has expired
        LocalDateTime expiresAt = user.getSubscriptionExpiresAt();
        if (expiresAt != null && expiresAt.isBefore(LocalDateTime.now(ZoneOffset.UTC))) {
            return false;  // Subscription expired
        }

        return true;
    }

    /**
     * Get monthly limit based on subscription type
     */
    private int getMonthlyLimit(Long userId) {
        return isProUser(userId) ? PRO_USER_MONTHLY_LIMIT : FREE_USER_MONTHLY_LIMIT;
    }

    /**
     * Get or create usage record for user in current month
     */
    public AiUsage getOrCreateUsage(Long userId) {
        String yearMonth = getCurrentYearMonth();
        AiUsage usage = aiUsageMapper.findByUserIdAndYearMonth(userId, yearMonth);
        int limit = getMonthlyLimit(userId);

        if (usage == null) {
            usage = new AiUsage();
            usage.setUserId(userId);
            usage.setYearMonth(yearMonth);
            usage.setUsageCount(0);
            usage.setMonthlyLimit(limit);
            aiUsageMapper.insert(usage);
        } else if (usage.getMonthlyLimit() != limit) {
            // Update limit if subscription status changed
            usage.setMonthlyLimit(limit);
            aiUsageMapper.updateMonthlyLimit(userId, yearMonth, limit);
        }

        return usage;
    }

    /**
     * Check if user can use AI optimization
     */
    public boolean canUseAi(Long userId) {
        AiUsage usage = getOrCreateUsage(userId);
        return usage.getUsageCount() < usage.getMonthlyLimit();
    }

    /**
     * Get remaining AI usage count
     */
    public int getRemainingUsage(Long userId) {
        AiUsage usage = getOrCreateUsage(userId);
        return Math.max(0, usage.getMonthlyLimit() - usage.getUsageCount());
    }

    /**
     * Increment AI usage count
     */
    @Transactional
    public boolean incrementUsage(Long userId) {
        if (!canUseAi(userId)) {
            return false;
        }

        String yearMonth = getCurrentYearMonth();
        AiUsage usage = aiUsageMapper.findByUserIdAndYearMonth(userId, yearMonth);

        if (usage == null) {
            getOrCreateUsage(userId);
        }

        aiUsageMapper.incrementUsage(userId, yearMonth);
        return true;
    }

    /**
     * Get current usage info
     */
    public AiUsageInfo getUsageInfo(Long userId) {
        AiUsage usage = getOrCreateUsage(userId);
        boolean isPro = isProUser(userId);

        return new AiUsageInfo(
            usage.getUsageCount(),
            usage.getMonthlyLimit(),
            Math.max(0, usage.getMonthlyLimit() - usage.getUsageCount()),
            isPro
        );
    }

    public record AiUsageInfo(int used, int limit, int remaining, boolean isProUser) {}
}
