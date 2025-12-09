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
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Collections;

@Slf4j
@Service
public class GoogleAuthService {

    private final GoogleIdTokenVerifier verifier;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public GoogleAuthService(@Value("${google.client-id}") String clientId) {
        this.verifier = new GoogleIdTokenVerifier.Builder(
                new NetHttpTransport(),
                GsonFactory.getDefaultInstance())
                .setAudience(Collections.singletonList(clientId))
                .build();
        this.httpClient = HttpClient.newHttpClient();
        this.objectMapper = new ObjectMapper();
    }

    public GoogleUserInfo verifyToken(String credential) {
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
            }
        } catch (Exception e) {
            log.debug("Not a valid ID Token, trying as access token: {}", e.getMessage());
        }

        // If not an ID Token, try as access token by calling Google's userinfo API
        return verifyAccessToken(credential);
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
