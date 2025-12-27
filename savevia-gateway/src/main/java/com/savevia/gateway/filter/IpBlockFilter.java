package com.savevia.gateway.filter;

import com.savevia.gateway.util.IpUtils;
import com.savevia.gateway.service.IpBlockService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.core.io.buffer.DataBuffer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;

@Slf4j
@Component
@RequiredArgsConstructor
public class IpBlockFilter implements GlobalFilter, Ordered {

    private final IpBlockService ipBlockService;

    @Value("${savevia.security.ip-block.enabled:true}")
    private boolean enabled;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        if (!enabled) {
            return chain.filter(exchange);
        }

        ServerHttpRequest request = exchange.getRequest();
        String clientIp = IpUtils.getClientIp(request);

        return ipBlockService.isBlocked(clientIp)
            .flatMap(isBlocked -> {
                if (isBlocked) {
                    return ipBlockService.getRemainingBlockTime(clientIp)
                        .flatMap(remainingSeconds -> {
                            log.debug("Blocked request from IP: {}, remaining time: {}s", clientIp, remainingSeconds);
                            return rejectBlockedRequest(exchange, remainingSeconds);
                        });
                }
                return chain.filter(exchange);
            });
    }

    private Mono<Void> rejectBlockedRequest(ServerWebExchange exchange, Long retryAfterSeconds) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.TOO_MANY_REQUESTS);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
        response.getHeaders().add("Retry-After", String.valueOf(retryAfterSeconds));

        String body = String.format(
            "{\"code\":429,\"message\":\"Your IP has been temporarily blocked due to suspicious activity. Please try again later.\",\"retryAfter\":%d}",
            retryAfterSeconds
        );

        DataBuffer buffer = response.bufferFactory().wrap(body.getBytes(StandardCharsets.UTF_8));
        return response.writeWith(Mono.just(buffer));
    }

    @Override
    public int getOrder() {
        // Run first, before all other filters
        return -200;
    }
}
