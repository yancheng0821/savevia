package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.SaveUserSpendingRequest;
import com.savevia.user.service.UserSpendingService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/users/me/spending")
@RequiredArgsConstructor
public class UserSpendingController {

    private final UserSpendingService userSpendingService;

    /**
     * Get current user's saved spending data
     */
    @GetMapping
    public Result<Map<String, BigDecimal>> getUserSpending(@RequestHeader("X-User-Id") Long userId) {
        Map<String, BigDecimal> spending = userSpendingService.getUserSpending(userId);
        return Result.success(spending);
    }

    /**
     * Save user's spending data
     */
    @PostMapping
    public Result<Map<String, BigDecimal>> saveUserSpending(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody SaveUserSpendingRequest request) {
        Map<String, BigDecimal> saved = userSpendingService.saveUserSpending(userId, request.getSpending());
        return Result.success("Spending saved successfully", saved);
    }
}
