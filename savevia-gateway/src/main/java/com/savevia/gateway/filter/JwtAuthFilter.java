package com.savevia.gateway.filter;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Slf4j
@Component
public class JwtAuthFilter implements GlobalFilter, Ordered {

    @Value("${jwt.secret}")
    private String jwtSecret;

    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    // Paths that don't require authentication
    private final List<String> publicPaths = List.of(
        "/api/v1/auth/**",
        "/api/v1/app/**",
        "/api/v1/cards",
        "/api/v1/cards/**",
        "/api/v1/optimize/calculate",
        "/api/v1/optimize/share/**",
        "/uploads/**",
        "/actuator/**"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().value();
        String authHeader = request.getHeaders().getFirst("Authorization");

        // Check if path is public
        if (isPublicPath(path)) {
            // For public paths, still try to extract user info if token is present (optional auth)
            if (authHeader != null && authHeader.startsWith("Bearer ")) {
                try {
                    String token = authHeader.substring(7);
                    Claims claims = validateToken(token);
                    ServerHttpRequest modifiedRequest = request.mutate()
                        .header("X-User-Id", claims.getSubject())
                        .header("X-User-Email", claims.get("email", String.class))
                        .build();
                    return chain.filter(exchange.mutate().request(modifiedRequest).build());
                } catch (Exception e) {
                    // Token invalid, but path is public so continue without user info
                    log.debug("Optional auth failed for public path: {}", e.getMessage());
                }
            }
            return chain.filter(exchange);
        }

        // Protected paths require valid token
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        String token = authHeader.substring(7);
        try {
            Claims claims = validateToken(token);

            // Add user info to headers for downstream services
            ServerHttpRequest modifiedRequest = request.mutate()
                .header("X-User-Id", claims.getSubject())
                .header("X-User-Email", claims.get("email", String.class))
                .build();

            return chain.filter(exchange.mutate().request(modifiedRequest).build());
        } catch (Exception e) {
            log.warn("JWT validation failed: {}", e.getMessage());
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }

    private boolean isPublicPath(String path) {
        return publicPaths.stream()
            .anyMatch(pattern -> pathMatcher.match(pattern, path));
    }

    private Claims validateToken(String token) {
        SecretKey key = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        return Jwts.parser()
            .verifyWith(key)
            .build()
            .parseSignedClaims(token)
            .getPayload();
    }

    @Override
    public int getOrder() {
        return -100;
    }
}
