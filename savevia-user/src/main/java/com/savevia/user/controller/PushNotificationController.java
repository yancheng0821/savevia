package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.entity.PushNotification;
import com.savevia.user.service.PushNotificationService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/v1/users/push")
@RequiredArgsConstructor
public class PushNotificationController {

    private final PushNotificationService pushNotificationService;

    /**
     * Register device for push notifications
     */
    @PostMapping("/device/register")
    public Result<Void> registerDevice(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @RequestBody DeviceRegistrationRequest request) {

        if (userId == null) {
            return Result.error(401, "Unauthorized");
        }

        pushNotificationService.registerDevice(
                userId,
                request.getDeviceToken(),
                request.getPlatform(),
                request.getDeviceName(),
                request.getAppVersion(),
                request.getOsVersion(),
                request.getLocale()
        );

        return Result.success();
    }

    /**
     * Unregister device
     */
    @PostMapping("/device/unregister")
    public Result<Void> unregisterDevice(@RequestBody DeviceUnregisterRequest request) {
        pushNotificationService.unregisterDevice(request.getDeviceToken());
        return Result.success();
    }

    /**
     * Get user's notification history
     */
    @GetMapping("/history")
    public Result<List<PushNotification>> getHistory(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @RequestParam(defaultValue = "20") int limit) {

        if (userId == null) {
            return Result.error(401, "Unauthorized");
        }

        List<PushNotification> notifications = pushNotificationService.getUserNotifications(userId, limit);
        return Result.success(notifications);
    }

    /**
     * Mark notification as read
     */
    @PostMapping("/{id}/read")
    public Result<Void> markAsRead(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @PathVariable Long id) {

        if (userId == null) {
            return Result.error(401, "Unauthorized");
        }

        pushNotificationService.markAsRead(id);
        return Result.success();
    }

    /**
     * Test push notification (for development only)
     */
    @PostMapping("/test")
    public Result<Void> testPush(
            @RequestHeader(value = "X-User-Id", required = false) Long userId,
            @RequestBody TestPushRequest request) {

        if (userId == null) {
            return Result.error(401, "Unauthorized");
        }

        pushNotificationService.sendPushToUser(
                userId,
                "test",
                request.getTitle() != null ? request.getTitle() : "Test Notification",
                request.getBody() != null ? request.getBody() : "This is a test push notification",
                null
        );

        return Result.success();
    }

    // Request DTOs

    @Data
    public static class DeviceRegistrationRequest {
        private String deviceToken;
        private String platform;        // 'ios', 'android', 'web'
        private String deviceName;
        private String appVersion;
        private String osVersion;
        private String locale;          // 'en', 'zh', 'fr', 'ja', 'ko', 'es'
    }

    @Data
    public static class DeviceUnregisterRequest {
        private String deviceToken;
    }

    @Data
    public static class TestPushRequest {
        private String title;
        private String body;
    }
}
