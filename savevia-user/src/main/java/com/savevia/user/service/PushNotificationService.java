package com.savevia.user.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.user.entity.PushNotification;
import com.savevia.user.entity.UserDevice;
import com.savevia.user.mapper.PushNotificationMapper;
import com.savevia.user.mapper.UserDeviceMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class PushNotificationService {

    private final ApnsPushService apnsPushService;
    private final UserDeviceMapper userDeviceMapper;
    private final PushNotificationMapper pushNotificationMapper;
    private final ObjectMapper objectMapper;

    /**
     * Register a device for push notifications
     */
    public void registerDevice(Long userId, String deviceToken, String platform, String deviceName, String appVersion, String osVersion, String locale) {
        UserDevice device = UserDevice.builder()
                .userId(userId)
                .deviceToken(deviceToken)
                .platform(platform)
                .deviceName(deviceName)
                .appVersion(appVersion)
                .osVersion(osVersion)
                .locale(locale != null ? locale : "en")
                .isActive(true)
                .lastUsedAt(LocalDateTime.now())
                .build();

        userDeviceMapper.insert(device);
        log.info("Registered device for user {}: {} ({}) locale={}", userId, platform, deviceName, locale);
    }

    /**
     * Unregister a device
     */
    public void unregisterDevice(String deviceToken) {
        userDeviceMapper.deactivateByToken(deviceToken);
        log.info("Unregistered device: {}", deviceToken);
    }

    /**
     * Schedule a push notification
     */
    public Long schedulePush(Long userId, String notificationType, String title, String body, Map<String, Object> data, LocalDateTime scheduledAt) {
        String dataJson = null;
        if (data != null) {
            try {
                dataJson = objectMapper.writeValueAsString(data);
            } catch (JsonProcessingException e) {
                log.warn("Failed to serialize push data: {}", e.getMessage());
            }
        }

        PushNotification notification = PushNotification.builder()
                .userId(userId)
                .notificationType(notificationType)
                .title(title)
                .body(body)
                .data(dataJson)
                .scheduledAt(scheduledAt)
                .status("pending")
                .build();

        pushNotificationMapper.insert(notification);
        log.info("Scheduled push notification for user {}: {} at {}", userId, notificationType, scheduledAt);
        return notification.getId();
    }

    /**
     * Send an immediate push notification to a user
     */
    public void sendPushToUser(Long userId, String notificationType, String title, String body, Map<String, Object> data) {
        // Save notification record
        String dataJson = null;
        if (data != null) {
            try {
                dataJson = objectMapper.writeValueAsString(data);
            } catch (JsonProcessingException e) {
                log.warn("Failed to serialize push data: {}", e.getMessage());
            }
        }

        PushNotification notification = PushNotification.builder()
                .userId(userId)
                .notificationType(notificationType)
                .title(title)
                .body(body)
                .data(dataJson)
                .status("pending")
                .build();
        pushNotificationMapper.insert(notification);

        // Get active devices
        List<UserDevice> devices = userDeviceMapper.findActiveByUserId(userId);
        if (devices.isEmpty()) {
            log.debug("No active devices for user {}", userId);
            pushNotificationMapper.updateStatus(notification.getId(), "failed", "No active devices");
            return;
        }

        // Send to all active devices
        for (UserDevice device : devices) {
            sendToDevice(notification, device, data);
        }
    }

    /**
     * Send push to a specific device
     */
    private void sendToDevice(PushNotification notification, UserDevice device, Map<String, Object> data) {
        if ("ios".equalsIgnoreCase(device.getPlatform())) {
            apnsPushService.sendPush(device.getDeviceToken(), notification.getTitle(), notification.getBody(), data)
                    .thenAccept(result -> {
                        if (result.isSuccess()) {
                            pushNotificationMapper.markAsSent(notification.getId(), LocalDateTime.now());
                            userDeviceMapper.updateLastUsed(device.getDeviceToken());
                        } else if (result.isInvalidToken()) {
                            // Deactivate invalid token
                            userDeviceMapper.deactivateByToken(device.getDeviceToken());
                            log.info("Deactivated invalid device token: {}", device.getDeviceToken());
                        } else {
                            pushNotificationMapper.updateStatus(notification.getId(), "failed", result.getErrorMessage());
                        }
                    });
        } else if ("android".equalsIgnoreCase(device.getPlatform())) {
            // TODO: Implement FCM for Android
            log.warn("Android push not yet implemented");
        }
    }

    /**
     * Scheduled task: send pending notifications
     */
    @Scheduled(fixedRate = 60000) // Every minute
    public void processPendingNotifications() {
        List<PushNotification> pending = pushNotificationMapper.findPendingToSend(LocalDateTime.now());
        if (pending.isEmpty()) {
            return;
        }

        log.info("Processing {} pending notifications", pending.size());
        for (PushNotification notification : pending) {
            try {
                Map<String, Object> data = null;
                if (notification.getData() != null) {
                    data = objectMapper.readValue(notification.getData(), Map.class);
                }
                sendPushDirect(notification, data);
            } catch (Exception e) {
                log.error("Failed to process notification {}: {}", notification.getId(), e.getMessage());
                pushNotificationMapper.updateStatus(notification.getId(), "failed", e.getMessage());
            }
        }
    }

    /**
     * Send push directly (for scheduled notifications)
     */
    private void sendPushDirect(PushNotification notification, Map<String, Object> data) {
        List<UserDevice> devices = userDeviceMapper.findActiveByUserId(notification.getUserId());
        if (devices.isEmpty()) {
            pushNotificationMapper.updateStatus(notification.getId(), "failed", "No active devices");
            return;
        }

        for (UserDevice device : devices) {
            sendToDevice(notification, device, data);
        }
    }

    /**
     * Get user's notification history
     */
    public List<PushNotification> getUserNotifications(Long userId, int limit) {
        return pushNotificationMapper.findByUserId(userId, limit);
    }

    /**
     * Mark notification as read
     */
    public void markAsRead(Long notificationId) {
        pushNotificationMapper.markAsRead(notificationId, LocalDateTime.now());
    }
}
