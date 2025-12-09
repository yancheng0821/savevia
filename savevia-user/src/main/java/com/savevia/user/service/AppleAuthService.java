package com.savevia.user.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigInteger;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.RSAPublicKeySpec;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
public class AppleAuthService {

    private static final String APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys";
    private static final String APPLE_ISSUER = "https://appleid.apple.com";

    private final String clientId;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final Map<String, PublicKey> publicKeyCache = new ConcurrentHashMap<>();

    public AppleAuthService(
            @Value("${apple.client-id:}") String clientId) {
        this.clientId = clientId;
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    public AppleUserInfo verifyToken(String identityToken) {
        try {
            // Decode JWT header to get the key ID (kid)
            String[] parts = identityToken.split("\\.");
            if (parts.length != 3) {
                throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Invalid token format");
            }

            String headerJson = new String(Base64.getUrlDecoder().decode(parts[0]));
            JsonNode header = objectMapper.readTree(headerJson);
            String kid = header.get("kid").asText();

            // Get Apple's public key
            PublicKey publicKey = getApplePublicKey(kid);

            // Verify and parse the token (JJWT 0.12+ API)
            Claims claims = Jwts.parser()
                    .verifyWith((RSAPublicKey) publicKey)
                    .build()
                    .parseSignedClaims(identityToken)
                    .getPayload();

            // Validate issuer and audience
            if (!APPLE_ISSUER.equals(claims.getIssuer())) {
                throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Invalid token issuer");
            }

            // Apple can send aud as String, List, or Set - check all
            Object audObj = claims.get("aud");
            log.info("Apple token audience check - clientId: '{}', tokenAud: '{}', audType: {}",
                     clientId, audObj, audObj != null ? audObj.getClass().getName() : "null");

            boolean validAudience = false;
            if (audObj instanceof String) {
                validAudience = clientId.equals(audObj);
            } else if (audObj instanceof java.util.Collection) {
                // Handles both List and Set types
                validAudience = ((java.util.Collection<?>) audObj).contains(clientId);
            }

            // Skip audience check if clientId is not configured
            if (!validAudience && clientId != null && !clientId.isEmpty()) {
                log.warn("Invalid audience: expected '{}', got '{}'", clientId, audObj);
                throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Invalid token audience");
            }

            // Extract user info
            String appleId = claims.getSubject();
            String email = claims.get("email", String.class);
            Boolean emailVerified = claims.get("email_verified", Boolean.class);

            // Apple doesn't provide name in the token, it's only sent on first auth
            // Name will be passed separately from the frontend
            log.info("Apple user verified: {} ({})", email, appleId);
            return new AppleUserInfo(appleId, email, emailVerified != null && emailVerified);

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to verify Apple token", e);
            throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Failed to verify Apple credential: " + e.getMessage());
        }
    }

    private PublicKey getApplePublicKey(String kid) {
        // Check cache first
        PublicKey cachedKey = publicKeyCache.get(kid);
        if (cachedKey != null) {
            return cachedKey;
        }

        try {
            // Fetch Apple's public keys
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(APPLE_KEYS_URL))
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Failed to fetch Apple public keys");
            }

            JsonNode keysResponse = objectMapper.readTree(response.body());
            JsonNode keys = keysResponse.get("keys");

            for (JsonNode key : keys) {
                if (kid.equals(key.get("kid").asText())) {
                    String n = key.get("n").asText();
                    String e = key.get("e").asText();

                    // Convert to RSA public key
                    BigInteger modulus = new BigInteger(1, Base64.getUrlDecoder().decode(n));
                    BigInteger exponent = new BigInteger(1, Base64.getUrlDecoder().decode(e));

                    RSAPublicKeySpec spec = new RSAPublicKeySpec(modulus, exponent);
                    KeyFactory factory = KeyFactory.getInstance("RSA");
                    PublicKey publicKey = factory.generatePublic(spec);

                    // Cache the key
                    publicKeyCache.put(kid, publicKey);
                    return publicKey;
                }
            }

            throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Public key not found for kid: " + kid);

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to get Apple public key", e);
            throw new BusinessException(ErrorCode.APPLE_AUTH_FAILED, "Failed to get Apple public key");
        }
    }

    public record AppleUserInfo(String appleId, String email, boolean emailVerified) {}
}
