package com.savevia.gateway.filter;

import com.savevia.gateway.service.IpBlockService;
import com.savevia.gateway.util.IpUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.time.Duration;

@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimitMonitorFilter implements WebFilter, Ordered {

    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final IpBlockService ipBlockService;

    private static final String RATE_EXCEEDED_PREFIX = "rate:exceeded:";

    @Value("${savevia.security.rate-limit.block-threshold:10}")
    private int blockThreshold;

    @Value("${savevia.security.rate-limit.enabled:true}")
    private boolean enabled;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        if (!enabled) {
            return chain.filter(exchange);
        }

        ServerHttpRequest request = exchange.getRequest();
        String clientIp = IpUtils.getClientIp(request);

        return chain.filter(exchange)
            .doOnSuccess(v -> checkRateLimitStatus(exchange, clientIp))
            .doOnError(e -> checkRateLimitStatus(exchange, clientIp));
    }

    private void checkRateLimitStatus(ServerWebExchange exchange, String clientIp) {
        int statusCode = exchange.getResponse().getStatusCode() != null
            ? exchange.getResponse().getStatusCode().value() : 0;

        if (statusCode == 429) {
            log.warn("Rate limit 429 detected for IP: {}", clientIp);
            handleRateLimitExceeded(clientIp).subscribe();
        }
    }

    private Mono<Void> handleRateLimitExceeded(String clientIp) {
        String key = RATE_EXCEEDED_PREFIX + clientIp;

        return redisTemplate.opsForValue().increment(key)
            .flatMap(count -> {
                redisTemplate.expire(key, Duration.ofMinutes(1)).subscribe();

                log.info("IP {} rate limit exceeded count: {}/{}", clientIp, count, blockThreshold);

                if (count >= blockThreshold) {
                    log.warn("IP {} exceeded rate limit {} times, blocking!", clientIp, count);
                    return ipBlockService.blockIp(clientIp, "Rate limit exceeded repeatedly")
                        .then(redisTemplate.delete(key).then());
                }
                return Mono.empty();
            });
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
