package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.service.AiUsageService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/users/ai-usage")
@RequiredArgsConstructor
public class AiUsageController {

    private final AiUsageService aiUsageService;

    /**
     * Get AI usage info for current user
     * Logged-in users get 100 calls per month
     */
    @GetMapping
    public Result<AiUsageService.AiUsageInfo> getUsageInfo(
            @RequestHeader("X-User-Id") Long userId) {
        return Result.success(aiUsageService.getUsageInfo(userId));
    }

    /**
     * Check if user can use AI (called by optimizer service via Feign)
     */
    @GetMapping("/check/{userId}")
    public Result<Boolean> checkCanUseAi(@PathVariable("userId") Long userId) {
        return Result.success(aiUsageService.canUseAi(userId));
    }

    /**
     * Record AI usage (called by optimizer service via Feign after successful AI generation)
     */
    @PostMapping("/record/{userId}")
    public Result<Boolean> recordAiUsage(@PathVariable("userId") Long userId) {
        boolean success = aiUsageService.incrementUsage(userId);
        if (success) {
            return Result.success(true);
        } else {
            return Result.error(429, "AI usage limit exceeded");
        }
    }

    /**
     * Check if user can use AI chat (called by optimizer service via Feign)
     */
    @GetMapping("/chat/check/{userId}")
    public Result<Boolean> checkCanUseChat(@PathVariable("userId") Long userId) {
        return Result.success(aiUsageService.canUseChat(userId));
    }

    /**
     * Record chat usage (called by optimizer service via Feign after successful chat)
     */
    @PostMapping("/chat/record/{userId}")
    public Result<Boolean> recordChatUsage(@PathVariable("userId") Long userId) {
        boolean success = aiUsageService.incrementChatUsage(userId);
        if (success) {
            return Result.success(true);
        } else {
            return Result.error(429, "Chat usage limit exceeded");
        }
    }
}
