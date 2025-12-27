package com.savevia.gateway.filter;

import com.savevia.gateway.util.IpUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.regex.Pattern;

@Slf4j
@Component
public class BotDetectionFilter implements GlobalFilter, Ordered {

    @Value("${savevia.security.bot-detection.enabled:true}")
    private boolean enabled;

    @Value("${savevia.security.bot-detection.block-empty-ua:true}")
    private boolean blockEmptyUa;

    // Known bot/crawler User-Agent patterns
    private static final List<Pattern> BOT_PATTERNS = List.of(
        Pattern.compile(".*bot.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*spider.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*crawler.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*scraper.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("python-requests.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("python-urllib.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("java/.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("Apache-HttpClient.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^curl.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^wget.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^Go-http-client.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^okhttp.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^axios.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^node-fetch.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^PostmanRuntime.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^insomnia.*", Pattern.CASE_INSENSITIVE)
    );

    // Allowed bots (search engines, etc.)
    private static final List<Pattern> ALLOWED_BOT_PATTERNS = List.of(
        Pattern.compile(".*Googlebot.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*Bingbot.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*Applebot.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*facebookexternalhit.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*Twitterbot.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*LinkedInBot.*", Pattern.CASE_INSENSITIVE)
    );

    // Paths that don't need bot detection (health checks, etc.)
    private static final List<String> EXCLUDED_PATHS = List.of(
        "/actuator",
        "/health"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        if (!enabled) {
            return chain.filter(exchange);
        }

        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().value();

        // Skip excluded paths
        if (isExcludedPath(path)) {
            return chain.filter(exchange);
        }

        String userAgent = request.getHeaders().getFirst("User-Agent");
        String clientIp = IpUtils.getClientIp(request);

        // Check empty User-Agent
        if (blockEmptyUa && (userAgent == null || userAgent.trim().isEmpty())) {
            log.warn("Blocked request with empty User-Agent from IP: {}", clientIp);
            return rejectRequest(exchange, "Empty User-Agent not allowed");
        }

        if (userAgent != null) {
            // Check if it's an allowed bot first
            if (isAllowedBot(userAgent)) {
                return chain.filter(exchange);
            }

            // Check if it matches blocked bot patterns
            if (isBlockedBot(userAgent)) {
                log.warn("Blocked bot request from IP: {}, User-Agent: {}", clientIp, userAgent);
                return rejectRequest(exchange, "Automated requests not allowed");
            }
        }

        return chain.filter(exchange);
    }

    private boolean isExcludedPath(String path) {
        return EXCLUDED_PATHS.stream().anyMatch(path::startsWith);
    }

    private boolean isAllowedBot(String userAgent) {
        return ALLOWED_BOT_PATTERNS.stream()
            .anyMatch(pattern -> pattern.matcher(userAgent).matches());
    }

    private boolean isBlockedBot(String userAgent) {
        return BOT_PATTERNS.stream()
            .anyMatch(pattern -> pattern.matcher(userAgent).matches());
    }

    private Mono<Void> rejectRequest(ServerWebExchange exchange, String reason) {
        exchange.getResponse().setStatusCode(HttpStatus.FORBIDDEN);
        exchange.getResponse().getHeaders().add("X-Block-Reason", reason);
        return exchange.getResponse().setComplete();
    }

    @Override
    public int getOrder() {
        // Run before JWT auth filter (-100) but after IP block filter
        return -150;
    }
}
