package com.savevia.gateway.config;

import org.springframework.cloud.gateway.filter.ratelimit.RedisRateLimiter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class RateLimitConfig {

    /**
     * Default rate limiter: 30 requests per second, burst capacity 60
     */
    @Bean
    @Primary
    public RedisRateLimiter defaultRateLimiter() {
        return new RedisRateLimiter(30, 60, 1);
    }

    /**
     * Strict rate limiter for sensitive endpoints: 5 requests per second, burst 10
     */
    @Bean
    public RedisRateLimiter strictRateLimiter() {
        return new RedisRateLimiter(5, 10, 1);
    }

    /**
     * Auth rate limiter: 3 requests per second, burst 5
     */
    @Bean
    public RedisRateLimiter authRateLimiter() {
        return new RedisRateLimiter(3, 5, 1);
    }
}
