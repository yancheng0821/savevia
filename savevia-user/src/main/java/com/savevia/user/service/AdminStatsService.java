package com.savevia.user.service;

import com.savevia.user.dto.AdminLoginRequest;
import com.savevia.user.dto.AdminLoginResponse;
import com.savevia.user.dto.AdminStatsDTO;
import com.savevia.user.dto.AdminUserDTO;
import com.savevia.user.dto.TrackEventRequest;
import com.savevia.user.entity.UserEvent;
import com.savevia.user.mapper.UserEventMapper;
import com.savevia.user.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class AdminStatsService {

    private final UserMapper userMapper;
    private final UserEventMapper userEventMapper;

    @Value("${admin.username:admin}")
    private String adminUsername;

    @Value("${admin.password:}")
    private String adminPassword;

    @Value("${admin.token-secret:default-secret-key-change-in-production}")
    private String tokenSecret;

    private static final long TOKEN_EXPIRY_HOURS = 2;

    /**
     * Validate admin credentials and generate token
     */
    public AdminLoginResponse login(AdminLoginRequest request) {
        if (adminPassword == null || adminPassword.isEmpty()) {
            log.error("Admin password not configured");
            throw new RuntimeException("Admin not configured");
        }

        if (!adminUsername.equals(request.getUsername()) || !adminPassword.equals(request.getPassword())) {
            log.warn("Failed admin login attempt for username: {}", request.getUsername());
            throw new RuntimeException("Invalid credentials");
        }

        // Generate simple token: base64(timestamp:hmac)
        long expiryTime = System.currentTimeMillis() + (TOKEN_EXPIRY_HOURS * 60 * 60 * 1000);
        String token = generateToken(expiryTime);

        log.info("Admin login successful");
        return AdminLoginResponse.builder()
                .token(token)
                .expiresIn(TOKEN_EXPIRY_HOURS * 60 * 60)
                .build();
    }

    /**
     * Validate admin token
     */
    public boolean validateToken(String token) {
        try {
            String decoded = new String(Base64.getDecoder().decode(token), StandardCharsets.UTF_8);
            String[] parts = decoded.split(":");
            if (parts.length != 2) return false;

            long expiryTime = Long.parseLong(parts[0]);
            String signature = parts[1];

            // Check expiry
            if (System.currentTimeMillis() > expiryTime) {
                log.warn("Admin token expired");
                return false;
            }

            // Verify signature
            String expectedSignature = hmacSha256(String.valueOf(expiryTime));
            return signature.equals(expectedSignature);
        } catch (Exception e) {
            log.error("Token validation failed", e);
            return false;
        }
    }

    /**
     * Get admin statistics
     */
    public AdminStatsDTO getStats() {
        // Use UTC to match database timezone
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        LocalDateTime thirtyDaysAgo = now.minusDays(30);

        // Get total users
        long totalUsers = userMapper.countTotalActiveUsers();

        // Get active users (last 30 days)
        long activeUsers = userEventMapper.countActiveUsers(thirtyDaysAgo, now);

        // Get event counts by type (last 30 days)
        List<Map<String, Object>> eventCounts = userEventMapper.countByEventType(thirtyDaysAgo, now);
        Map<String, Long> eventCountMap = new HashMap<>();
        for (Map<String, Object> row : eventCounts) {
            String eventType = (String) row.get("eventType");
            Long count = ((Number) row.get("count")).longValue();
            eventCountMap.put(eventType, count);
        }

        // Get daily event counts (last 30 days) for trend charts
        List<Map<String, Object>> dailyEventCounts = userEventMapper.countByEventTypeAndDate(thirtyDaysAgo, now);
        List<AdminStatsDTO.DailyEventCount> dailyEvents = new java.util.ArrayList<>();
        for (Map<String, Object> row : dailyEventCounts) {
            Object dateObj = row.get("eventDate");
            String dateStr = dateObj != null ? dateObj.toString() : null;
            String eventType = (String) row.get("eventType");
            Long count = ((Number) row.get("count")).longValue();

            dailyEvents.add(AdminStatsDTO.DailyEventCount.builder()
                    .date(dateStr)
                    .eventType(eventType)
                    .count(count)
                    .build());
        }

        // Get daily active users (last 30 days) for DAU trend chart
        List<Map<String, Object>> dailyActiveUserCounts = userEventMapper.countDailyActiveUsers(thirtyDaysAgo, now);
        List<AdminStatsDTO.DailyActiveCount> dailyActiveUsers = new java.util.ArrayList<>();
        for (Map<String, Object> row : dailyActiveUserCounts) {
            Object dateObj = row.get("eventDate");
            String dateStr = dateObj != null ? dateObj.toString() : null;
            Long count = ((Number) row.get("count")).longValue();

            dailyActiveUsers.add(AdminStatsDTO.DailyActiveCount.builder()
                    .date(dateStr)
                    .count(count)
                    .build());
        }

        DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        return AdminStatsDTO.builder()
                .totalUsers(totalUsers)
                .activeUsers(activeUsers)
                .eventCounts(eventCountMap)
                .dailyEvents(dailyEvents)
                .dailyActiveUsers(dailyActiveUsers)
                .statsFrom(thirtyDaysAgo.format(formatter))
                .statsTo(now.format(formatter))
                .build();
    }

    /**
     * Track an event
     */
    public void trackEvent(TrackEventRequest request, Long userId) {
        UserEvent event = UserEvent.builder()
                .eventType(request.getEventType())
                .userId(userId)
                .sessionId(request.getSessionId())
                .createdAt(LocalDateTime.now(ZoneOffset.UTC))
                .build();

        userEventMapper.insert(event);
        log.debug("Tracked event: {} for user: {}", request.getEventType(), userId);
    }

    /**
     * Get all active users
     */
    public List<AdminUserDTO> getAllUsers() {
        DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

        // Get active user IDs (last 30 days)
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        LocalDateTime thirtyDaysAgo = now.minusDays(30);
        List<Long> activeUserIdList = userEventMapper.getActiveUserIds(thirtyDaysAgo, now);
        java.util.Set<Long> activeUserIds = new java.util.HashSet<>(activeUserIdList);

        // Get last active time for active users
        Map<Long, String> lastActiveTimeMap = new HashMap<>();
        if (!activeUserIdList.isEmpty()) {
            List<Map<String, Object>> lastActiveTimes = userEventMapper.getLastActiveTimeByUserIds(activeUserIdList);
            for (Map<String, Object> row : lastActiveTimes) {
                Long userId = ((Number) row.get("userId")).longValue();
                Object lastActiveAt = row.get("lastActiveAt");
                if (lastActiveAt != null) {
                    if (lastActiveAt instanceof java.time.LocalDateTime) {
                        lastActiveTimeMap.put(userId, ((java.time.LocalDateTime) lastActiveAt).format(formatter));
                    } else {
                        lastActiveTimeMap.put(userId, lastActiveAt.toString());
                    }
                }
            }
        }

        return userMapper.selectAllActiveUsers().stream()
                .map(user -> AdminUserDTO.builder()
                        .id(user.getId())
                        .name(user.getName())
                        .email(user.getEmail())
                        .createdAt(user.getCreatedAt() != null ? user.getCreatedAt().format(formatter) : null)
                        .subscriptionType(user.getSubscriptionType())
                        .subscriptionPlatform(user.getSubscriptionPlatform())
                        .subscriptionProductId(user.getSubscriptionProductId())
                        .subscriptionExpiresAt(user.getSubscriptionExpiresAt() != null ? user.getSubscriptionExpiresAt().format(formatter) : null)
                        .active(activeUserIds.contains(user.getId()))
                        .lastActiveAt(lastActiveTimeMap.get(user.getId()))
                        .build())
                .toList();
    }

    /**
     * Get events for a specific user
     */
    public AdminStatsDTO getUserEvents(Long userId) {
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        LocalDateTime thirtyDaysAgo = now.minusDays(30);

        // Get event counts by type for this user
        List<Map<String, Object>> eventCounts = userEventMapper.countByEventTypeForUser(userId, thirtyDaysAgo, now);
        Map<String, Long> eventCountMap = new HashMap<>();
        for (Map<String, Object> row : eventCounts) {
            String eventType = (String) row.get("eventType");
            Long count = ((Number) row.get("count")).longValue();
            eventCountMap.put(eventType, count);
        }

        // Get daily event counts for this user
        List<Map<String, Object>> dailyEventCounts = userEventMapper.countByEventTypeAndDateForUser(userId, thirtyDaysAgo, now);
        List<AdminStatsDTO.DailyEventCount> dailyEvents = new java.util.ArrayList<>();
        for (Map<String, Object> row : dailyEventCounts) {
            Object dateObj = row.get("eventDate");
            String dateStr = dateObj != null ? dateObj.toString() : null;
            String eventType = (String) row.get("eventType");
            Long count = ((Number) row.get("count")).longValue();

            dailyEvents.add(AdminStatsDTO.DailyEventCount.builder()
                    .date(dateStr)
                    .eventType(eventType)
                    .count(count)
                    .build());
        }

        DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
        return AdminStatsDTO.builder()
                .totalUsers(0) // Not relevant for single user
                .activeUsers(0) // Not relevant for single user
                .eventCounts(eventCountMap)
                .dailyEvents(dailyEvents)
                .statsFrom(thirtyDaysAgo.format(formatter))
                .statsTo(now.format(formatter))
                .build();
    }

    private String generateToken(long expiryTime) {
        String signature = hmacSha256(String.valueOf(expiryTime));
        String tokenData = expiryTime + ":" + signature;
        return Base64.getEncoder().encodeToString(tokenData.getBytes(StandardCharsets.UTF_8));
    }

    private String hmacSha256(String data) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(tokenSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            byte[] hash = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash);
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate HMAC", e);
        }
    }
}
