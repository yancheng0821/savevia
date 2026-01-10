package com.savevia.user.service;

import com.eatthepath.pushy.apns.ApnsClient;
import com.eatthepath.pushy.apns.ApnsClientBuilder;
import com.eatthepath.pushy.apns.PushNotificationResponse;
import com.eatthepath.pushy.apns.util.ApnsPayloadBuilder;
import com.eatthepath.pushy.apns.util.SimpleApnsPayloadBuilder;
import com.eatthepath.pushy.apns.util.SimpleApnsPushNotification;
import com.eatthepath.pushy.apns.util.TokenUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.File;
import java.io.InputStream;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Slf4j
@Service
public class ApnsPushService {

    @Value("${apns.enabled:false}")
    private boolean enabled;

    @Value("${apns.production:false}")
    private boolean production;

    @Value("${apns.key-id:}")
    private String keyId;

    @Value("${apns.team-id:}")
    private String teamId;

    @Value("${apns.key-path:}")
    private String keyPath;

    @Value("${apns.bundle-id:}")
    private String bundleId;

    private ApnsClient apnsClient;

    @PostConstruct
    public void init() {
        if (!enabled) {
            log.info("APNs push service is disabled");
            return;
        }

        try {
            // Load the .p8 key file
            File keyFile = new File(keyPath);
            if (!keyFile.exists()) {
                log.warn("APNs key file not found: {}. Push notifications will be disabled.", keyPath);
                enabled = false;
                return;
            }

            apnsClient = new ApnsClientBuilder()
                    .setApnsServer(production ? ApnsClientBuilder.PRODUCTION_APNS_HOST : ApnsClientBuilder.DEVELOPMENT_APNS_HOST)
                    .setSigningKey(ApnsSigningKey.loadFromPkcs8File(keyFile, teamId, keyId))
                    .build();

            log.info("APNs push service initialized successfully (production: {})", production);
        } catch (Exception e) {
            log.error("Failed to initialize APNs push service: {}", e.getMessage());
            enabled = false;
        }
    }

    @PreDestroy
    public void shutdown() {
        if (apnsClient != null) {
            try {
                apnsClient.close().get();
            } catch (Exception e) {
                log.warn("Error closing APNs client: {}", e.getMessage());
            }
        }
    }

    /**
     * Check if APNs service is available
     */
    public boolean isAvailable() {
        return enabled && apnsClient != null;
    }

    /**
     * Send a push notification to an iOS device
     *
     * @param deviceToken The device token
     * @param title       Notification title
     * @param body        Notification body
     * @param data        Additional data payload
     * @return CompletableFuture with the result
     */
    public CompletableFuture<PushResult> sendPush(String deviceToken, String title, String body, Map<String, Object> data) {
        if (!isAvailable()) {
            return CompletableFuture.completedFuture(
                    PushResult.failure("APNs service not available")
            );
        }

        try {
            // Build the payload
            ApnsPayloadBuilder payloadBuilder = new SimpleApnsPayloadBuilder()
                    .setAlertTitle(title)
                    .setAlertBody(body)
                    .setSound("default")
                    .setBadgeNumber(1);

            // Add custom data
            if (data != null) {
                for (Map.Entry<String, Object> entry : data.entrySet()) {
                    payloadBuilder.addCustomProperty(entry.getKey(), entry.getValue());
                }
            }

            String payload = payloadBuilder.build();
            String token = TokenUtil.sanitizeTokenString(deviceToken);

            SimpleApnsPushNotification pushNotification = new SimpleApnsPushNotification(
                    token,
                    bundleId,
                    payload,
                    Instant.now().plusSeconds(86400), // Expire in 24 hours
                    com.eatthepath.pushy.apns.DeliveryPriority.IMMEDIATE,
                    com.eatthepath.pushy.apns.PushType.ALERT
            );

            return apnsClient.sendNotification(pushNotification)
                    .thenApply(response -> {
                        if (response.isAccepted()) {
                            log.debug("Push notification accepted by APNs: {}", token);
                            return PushResult.success();
                        } else {
                            String reason = response.getRejectionReason().orElse("Unknown");
                            log.warn("Push notification rejected by APNs: {} - {}", token, reason);

                            // Check if token is invalid
                            if ("BadDeviceToken".equals(reason) || "Unregistered".equals(reason)) {
                                return PushResult.invalidToken(reason);
                            }
                            return PushResult.failure(reason);
                        }
                    })
                    .exceptionally(e -> {
                        log.error("Failed to send push notification: {}", e.getMessage());
                        return PushResult.failure(e.getMessage());
                    });

        } catch (Exception e) {
            log.error("Error preparing push notification: {}", e.getMessage());
            return CompletableFuture.completedFuture(PushResult.failure(e.getMessage()));
        }
    }

    /**
     * Send a silent push notification (for background updates)
     */
    public CompletableFuture<PushResult> sendSilentPush(String deviceToken, Map<String, Object> data) {
        if (!isAvailable()) {
            return CompletableFuture.completedFuture(
                    PushResult.failure("APNs service not available")
            );
        }

        try {
            ApnsPayloadBuilder payloadBuilder = new SimpleApnsPayloadBuilder()
                    .setContentAvailable(true);

            if (data != null) {
                for (Map.Entry<String, Object> entry : data.entrySet()) {
                    payloadBuilder.addCustomProperty(entry.getKey(), entry.getValue());
                }
            }

            String payload = payloadBuilder.build();
            String token = TokenUtil.sanitizeTokenString(deviceToken);

            SimpleApnsPushNotification pushNotification = new SimpleApnsPushNotification(
                    token,
                    bundleId,
                    payload,
                    Instant.now().plusSeconds(86400),
                    com.eatthepath.pushy.apns.DeliveryPriority.CONSERVE_POWER,
                    com.eatthepath.pushy.apns.PushType.BACKGROUND
            );

            return apnsClient.sendNotification(pushNotification)
                    .thenApply(response -> {
                        if (response.isAccepted()) {
                            return PushResult.success();
                        } else {
                            return PushResult.failure(response.getRejectionReason().orElse("Unknown"));
                        }
                    })
                    .exceptionally(e -> PushResult.failure(e.getMessage()));

        } catch (Exception e) {
            return CompletableFuture.completedFuture(PushResult.failure(e.getMessage()));
        }
    }

    /**
     * Result of a push notification attempt
     */
    public static class PushResult {
        private final boolean success;
        private final boolean invalidToken;
        private final String errorMessage;

        private PushResult(boolean success, boolean invalidToken, String errorMessage) {
            this.success = success;
            this.invalidToken = invalidToken;
            this.errorMessage = errorMessage;
        }

        public static PushResult success() {
            return new PushResult(true, false, null);
        }

        public static PushResult failure(String message) {
            return new PushResult(false, false, message);
        }

        public static PushResult invalidToken(String message) {
            return new PushResult(false, true, message);
        }

        public boolean isSuccess() {
            return success;
        }

        public boolean isInvalidToken() {
            return invalidToken;
        }

        public String getErrorMessage() {
            return errorMessage;
        }
    }
}

/**
 * Helper class to load APNs signing key
 */
class ApnsSigningKey {
    public static com.eatthepath.pushy.apns.auth.ApnsSigningKey loadFromPkcs8File(File file, String teamId, String keyId) throws Exception {
        return com.eatthepath.pushy.apns.auth.ApnsSigningKey.loadFromPkcs8File(file, teamId, keyId);
    }
}
