package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.OptimizationResult;
import com.savevia.optimizer.dto.SaveResultRequest;
import com.savevia.optimizer.dto.SaveResultResponse;
import com.savevia.optimizer.service.SavedResultService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/optimize")
@RequiredArgsConstructor
public class SavedResultController {

    private final SavedResultService savedResultService;

    /**
     * Save/share optimization result
     */
    @PostMapping("/share")
    public Result<SaveResultResponse> shareResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @Valid @RequestBody SaveResultRequest request) {
        SaveResultResponse response = savedResultService.saveResult(request.getResult(), userId);
        return Result.success(response);
    }

    /**
     * Get shared result by shareId
     */
    @GetMapping("/share/{shareId}")
    public Result<OptimizationResult> getSharedResult(@PathVariable String shareId) {
        OptimizationResult result = savedResultService.getByShareId(shareId);
        if (result == null) {
            return Result.error(404, "Shared result not found or expired");
        }
        return Result.success(result);
    }

    /**
     * Save user's current optimization result
     */
    @PostMapping("/user-result")
    public Result<Void> saveUserResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @Valid @RequestBody SaveResultRequest request) {
        if (userId == null) {
            return Result.error(401, "User not authenticated");
        }
        savedResultService.saveUserResult(request.getResult(), userId);
        return Result.success(null);
    }

    /**
     * Get user's latest optimization result
     */
    @GetMapping("/user-result")
    public Result<OptimizationResult> getUserResult(
            @RequestHeader(value = "X-User-Id", required = false) Long userId) {
        if (userId == null) {
            return Result.error(401, "User not authenticated");
        }
        OptimizationResult result = savedResultService.getUserResult(userId);
        return Result.success(result);
    }
}
