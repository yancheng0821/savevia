package com.savevia.gateway.util;

import org.springframework.http.server.reactive.ServerHttpRequest;

import java.util.Objects;

public class IpUtils {

    private IpUtils() {}

    /**
     * Extract real client IP, handling proxies and load balancers
     */
    public static String getClientIp(ServerHttpRequest request) {
        // Check X-Forwarded-For header (set by reverse proxies)
        String xForwardedFor = request.getHeaders().getFirst("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            // Take the first IP (original client)
            String ip = xForwardedFor.split(",")[0].trim();
            if (isValidIp(ip)) {
                return ip;
            }
        }

        // Check X-Real-IP header (set by Nginx)
        String xRealIp = request.getHeaders().getFirst("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty() && isValidIp(xRealIp)) {
            return xRealIp;
        }

        // Check CF-Connecting-IP header (Cloudflare)
        String cfConnectingIp = request.getHeaders().getFirst("CF-Connecting-IP");
        if (cfConnectingIp != null && !cfConnectingIp.isEmpty() && isValidIp(cfConnectingIp)) {
            return cfConnectingIp;
        }

        // Fall back to remote address
        if (request.getRemoteAddress() != null) {
            return Objects.requireNonNull(request.getRemoteAddress()).getAddress().getHostAddress();
        }

        return "unknown";
    }

    private static boolean isValidIp(String ip) {
        if (ip == null || ip.isEmpty()) {
            return false;
        }
        // Basic validation - not localhost or internal proxy
        return !ip.equals("127.0.0.1") && !ip.equals("0:0:0:0:0:0:0:1");
    }
}
