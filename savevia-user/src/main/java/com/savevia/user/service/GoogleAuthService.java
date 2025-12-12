package com.savevia.user.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

@Slf4j
@Service
public class GoogleAuthService {

    private final GoogleIdTokenVerifier verifier;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final String clientId;
    private final String clientSecret;

    public GoogleAuthService(
            @Value("${google.client-id}") String clientId,
            @Value("${google.client-secret:}") String clientSecret,
            @Value("${google.ios-client-id:}") String iosClientId) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;

        // Support multiple client IDs (web + iOS)
        List<String> audiences = Arrays.asList(clientId, iosClientId).stream()
                .filter(id -> id != null && !id.isEmpty())
                .toList();

        this.verifier = new GoogleIdTokenVerifier.Builder(
                new NetHttpTransport(),
                GsonFactory.getDefaultInstance())
                .setAudience(audiences)
                .build();
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();

        log.info("GoogleAuthService initialized with audiences: {}", audiences);
    }

    public GoogleUserInfo verifyToken(String credential) {
        log.debug("Verifying credential, length: {}, starts with: {}",
                credential.length(), credential.substring(0, Math.min(20, credential.length())));

        // First, try to verify as ID Token (JWT format)
        try {
            GoogleIdToken idToken = verifier.verify(credential);
            if (idToken != null) {
                GoogleIdToken.Payload payload = idToken.getPayload();
                String googleId = payload.getSubject();
                String email = payload.getEmail();
                String name = (String) payload.get("name");
                String pictureUrl = (String) payload.get("picture");

                log.info("Google user verified via ID Token: {} ({})", email, googleId);
                return new GoogleUserInfo(googleId, email, name, pictureUrl);
            } else {
                log.warn("ID Token verification returned null - audience mismatch or invalid token");
            }
        } catch (Exception e) {
            log.warn("ID Token verification failed: {}", e.getMessage());
        }

        // Check if it's an authorization code (starts with "4/" typically)
        if (credential.startsWith("4/")) {
            log.debug("Credential is an auth code, exchanging for tokens");
            return exchangeAuthCodeForUserInfo(credential);
        }

        // If not an ID Token or auth code, try as access token
        return verifyAccessToken(credential);
    }

    private GoogleUserInfo exchangeAuthCodeForUserInfo(String authCode) {
        try {
            String tokenEndpoint = "https://oauth2.googleapis.com/token";
            String requestBody = "code=" + URLEncoder.encode(authCode, StandardCharsets.UTF_8)
                    + "&client_id=" + URLEncoder.encode(clientId, StandardCharsets.UTF_8)
                    + "&client_secret=" + URLEncoder.encode(clientSecret, StandardCharsets.UTF_8)
                    + "&grant_type=authorization_code"
                    + "&redirect_uri=";

            HttpRequest tokenRequest = HttpRequest.newBuilder()
                    .uri(URI.create(tokenEndpoint))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                    .build();

            HttpResponse<String> tokenResponse = httpClient.send(tokenRequest, HttpResponse.BodyHandlers.ofString());

            if (tokenResponse.statusCode() != 200) {
                log.error("Token exchange failed: {} - {}", tokenResponse.statusCode(), tokenResponse.body());
                throw new BusinessException(ErrorCode.GOOGLE_AUTH_FAILED, "Failed to exchange authorization code");
            }

            JsonNode tokenJson = objectMapper.readTree(tokenResponse.body());
            log.debug("Token exchange response keys: {}", tokenJson.fieldNames());

            // Try to use id_token if available
            if (tokenJson.has("id_token")) {
                String idTokenStr = tokenJson.get("id_token").asText();
                try {
                    GoogleIdToken idToken = verifier.verify(idTokenStr);
                    if (idToken != null) {
                        GoogleIdToken.Payload payload = idToken.getPayload();
                        log.info("Google user verified via exchanged ID Token: {}", payload.getEmail());
                        return new GoogleUserInfo(
                                payload.getSubject(),
                                payload.getEmail(),
                                (String) payload.get("name"),
                                (String) payload.get("picture")
                        );
                    }
                } catch (Exception e) {
                    log.debug("Could not verify exchanged id_token, using access_token: {}", e.getMessage());
                }
            }

            // Fall back to using access token
            if (tokenJson.has("access_token")) {
                String accessToken = tokenJson.get("access_token").asText();
                return verifyAccessToken(accessToken);
            }

            throw new BusinessException(ErrorCode.GOOGLE_AUTH_FAILED, "No valid token in response");

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to exchange auth code: {}", e.getMessage(), e);
            throw new BusinessException(ErrorCode.GOOGLE_AUTH_FAILED, "Failed to verify Google credential");
        }
    }

    private GoogleUserInfo verifyAccessToken(String accessToken) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("https://www.googleapis.com/oauth2/v3/userinfo"))
                    .header("Authorization", "Bearer " + accessToken)
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() != 200) {
                log.error("Google userinfo API returned status: {}", response.statusCode());
                throw new BusinessException(ErrorCode.GOOGLE_AUTH_FAILED, "Invalid Google access token");
            }

            JsonNode userInfo = objectMapper.readTree(response.body());
            String googleId = userInfo.get("sub").asText();
            String email = userInfo.get("email").asText();
            String name = userInfo.has("name") ? userInfo.get("name").asText() : email.split("@")[0];
            String pictureUrl = userInfo.has("picture") ? userInfo.get("picture").asText() : null;

            log.info("Google user verified via access token: {} ({})", email, googleId);
            return new GoogleUserInfo(googleId, email, name, pictureUrl);
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to verify Google access token", e);
            throw new BusinessException(ErrorCode.GOOGLE_AUTH_FAILED, "Failed to verify Google credential");
        }
    }

    public record GoogleUserInfo(String googleId, String email, String name, String pictureUrl) {}
}
