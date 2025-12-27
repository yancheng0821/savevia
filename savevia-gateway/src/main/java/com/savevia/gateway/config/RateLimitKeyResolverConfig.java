package com.savevia.gateway.config;

import com.savevia.gateway.util.IpUtils;
import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Mono;

@Configuration
public class RateLimitKeyResolverConfig {

    @Bean
    public KeyResolver ipKeyResolver() {
        return exchange -> {
            String ip = IpUtils.getClientIp(exchange.getRequest());
            return Mono.just(ip);
        };
    }
}
