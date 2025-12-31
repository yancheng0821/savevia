package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.AdminLoginRequest;
import com.savevia.user.dto.AdminLoginResponse;
import com.savevia.user.dto.AdminStatsDTO;
import com.savevia.user.dto.AdminUserDTO;
import com.savevia.user.dto.TrackEventRequest;
import com.savevia.user.service.AdminStatsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/admin")
@RequiredArgsConstructor
@Slf4j
public class AdminController {

    private final AdminStatsService adminStatsService;

    /**
     * Admin login - returns token
     */
    @PostMapping("/login")
    public Result<AdminLoginResponse> login(@RequestBody AdminLoginRequest request) {
        try {
            AdminLoginResponse response = adminStatsService.login(request);
            return Result.success(response);
        } catch (RuntimeException e) {
            log.error("Admin login failed: {}", e.getMessage());
            return Result.error(401, e.getMessage());
        }
    }

    /**
     * Get admin statistics - requires valid admin token
     */
    @GetMapping("/stats")
    public Result<AdminStatsDTO> getStats(@RequestHeader("X-Admin-Token") String token) {
        if (!adminStatsService.validateToken(token)) {
            return Result.error(401, "Invalid or expired token");
        }

        try {
            AdminStatsDTO stats = adminStatsService.getStats();
            return Result.success(stats);
        } catch (Exception e) {
            log.error("Failed to get stats", e);
            return Result.error(500, "Failed to get statistics");
        }
    }

    /**
     * Get all users - requires valid admin token
     */
    @GetMapping("/users")
    public Result<List<AdminUserDTO>> getUsers(@RequestHeader("X-Admin-Token") String token) {
        if (!adminStatsService.validateToken(token)) {
            return Result.error(401, "Invalid or expired token");
        }

        try {
            List<AdminUserDTO> users = adminStatsService.getAllUsers();
            return Result.success(users);
        } catch (Exception e) {
            log.error("Failed to get users", e);
            return Result.error(500, "Failed to get users");
        }
    }

    /**
     * Track user event - public endpoint (no auth required)
     */
    @PostMapping("/track")
    public Result<Void> trackEvent(
            @RequestBody TrackEventRequest request,
            @RequestHeader(value = "X-User-Id", required = false) Long userId
    ) {
        try {
            adminStatsService.trackEvent(request, userId);
            return Result.success(null);
        } catch (Exception e) {
            log.error("Failed to track event", e);
            // Don't return error to client for tracking - just log it
            return Result.success(null);
        }
    }

    /**
     * Get user events - requires valid admin token
     */
    @GetMapping("/users/{userId}/events")
    public Result<AdminStatsDTO> getUserEvents(
            @RequestHeader("X-Admin-Token") String token,
            @PathVariable Long userId
    ) {
        if (!adminStatsService.validateToken(token)) {
            return Result.error(401, "Invalid or expired token");
        }

        try {
            AdminStatsDTO stats = adminStatsService.getUserEvents(userId);
            return Result.success(stats);
        } catch (Exception e) {
            log.error("Failed to get user events for userId: {}", userId, e);
            return Result.error(500, "Failed to get user events");
        }
    }
}
