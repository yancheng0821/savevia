package com.savevia.gateway.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Slf4j
@Service
@RequiredArgsConstructor
public class IpBlockService {

    private final ReactiveRedisTemplate<String, String> redisTemplate;

    private static final String BLOCKED_IP_PREFIX = "blocked:ip:";
    private static final String VIOLATION_COUNT_PREFIX = "violation:count:";

    @Value("${savevia.security.ip-block.first-block-minutes:5}")
    private int firstBlockMinutes;

    @Value("${savevia.security.ip-block.second-block-minutes:60}")
    private int secondBlockMinutes;

    @Value("${savevia.security.ip-block.third-block-minutes:1440}")
    private int thirdBlockMinutes;

    /**
     * Check if an IP is blocked
     */
    public Mono<Boolean> isBlocked(String ip) {
        return redisTemplate.hasKey(BLOCKED_IP_PREFIX + ip);
    }

    /**
     * Get the reason why an IP is blocked
     */
    public Mono<String> getBlockReason(String ip) {
        return redisTemplate.opsForValue().get(BLOCKED_IP_PREFIX + ip);
    }

    /**
     * Block an IP with escalating duration based on violation count
     */
    public Mono<Void> blockIp(String ip, String reason) {
        String violationKey = VIOLATION_COUNT_PREFIX + ip;

        return redisTemplate.opsForValue().increment(violationKey)
            .flatMap(count -> {
                // Set expiry for violation count (24 hours)
                redisTemplate.expire(violationKey, Duration.ofHours(24)).subscribe();

                Duration blockDuration = calculateBlockDuration(count.intValue());
                log.warn("Blocking IP {} for {} minutes, reason: {}, violation count: {}",
                    ip, blockDuration.toMinutes(), reason, count);

                return redisTemplate.opsForValue()
                    .set(BLOCKED_IP_PREFIX + ip, reason, blockDuration)
                    .then();
            });
    }

    /**
     * Manually unblock an IP
     */
    public Mono<Boolean> unblockIp(String ip) {
        return redisTemplate.delete(BLOCKED_IP_PREFIX + ip)
            .map(count -> count > 0);
    }

    /**
     * Reset violation count for an IP
     */
    public Mono<Boolean> resetViolationCount(String ip) {
        return redisTemplate.delete(VIOLATION_COUNT_PREFIX + ip)
            .map(count -> count > 0);
    }

    /**
     * Get remaining block time in seconds
     */
    public Mono<Long> getRemainingBlockTime(String ip) {
        return redisTemplate.getExpire(BLOCKED_IP_PREFIX + ip)
            .map(Duration::getSeconds)
            .defaultIfEmpty(0L);
    }

    private Duration calculateBlockDuration(int violationCount) {
        return switch (violationCount) {
            case 1 -> Duration.ofMinutes(firstBlockMinutes);
            case 2 -> Duration.ofMinutes(secondBlockMinutes);
            default -> Duration.ofMinutes(thirdBlockMinutes);
        };
    }
}
