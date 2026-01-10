package com.savevia.optimizer.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

/**
 * OpenAI Streaming Service for Chat
 * Uses OkHttp for SSE (Server-Sent Events) streaming
 */
@Slf4j
@Service
public class OpenAiStreamService {

    @Value("${openai.api.key:}")
    private String apiKey;

    @Value("${openai.api.model:gpt-4o-mini}")
    private String model;

    @Value("${openai.api.base-url:https://api.openai.com}")
    private String baseUrl;

    @Value("${openai.enabled:true}")
    private boolean enabled;

    private OkHttpClient httpClient;
    private final ObjectMapper objectMapper;

    public OpenAiStreamService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    public void init() {
        httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(120, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        log.info("OpenAI Stream Service initialized");
    }

    @PreDestroy
    public void shutdown() {
        if (httpClient != null) {
            httpClient.dispatcher().executorService().shutdown();
            httpClient.connectionPool().evictAll();
        }
    }

    /**
     * Check if the service is available
     */
    public boolean isAvailable() {
        return enabled && apiKey != null && !apiKey.isEmpty();
    }

    /**
     * Stream chat completion from OpenAI
     *
     * @param messages List of message maps with "role" and "content"
     * @param onChunk  Consumer called for each text chunk received
     * @param onComplete Runnable called when streaming is complete
     * @param onError Consumer called if an error occurs
     */
    public void streamChat(
            List<Map<String, String>> messages,
            Consumer<String> onChunk,
            Runnable onComplete,
            Consumer<String> onError) {

        if (!isAvailable()) {
            onError.accept("OpenAI service is not available");
            return;
        }

        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", model);
            requestBody.put("messages", messages);
            requestBody.put("stream", true);
            requestBody.put("max_tokens", 500);
            requestBody.put("temperature", 0.7);

            String jsonBody = objectMapper.writeValueAsString(requestBody);

            Request request = new Request.Builder()
                    .url(baseUrl + "/v1/chat/completions")
                    .addHeader("Authorization", "Bearer " + apiKey)
                    .addHeader("Content-Type", "application/json")
                    .addHeader("Accept", "text/event-stream")
                    .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                    .build();

            httpClient.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    log.error("OpenAI stream request failed: {}", e.getMessage());
                    onError.accept("Failed to connect to AI service: " + e.getMessage());
                }

                @Override
                public void onResponse(Call call, Response response) {
                    if (!response.isSuccessful()) {
                        String errorMsg = "OpenAI API error: " + response.code();
                        try {
                            if (response.body() != null) {
                                errorMsg += " - " + response.body().string();
                            }
                        } catch (IOException ignored) {}
                        log.error(errorMsg);
                        onError.accept(errorMsg);
                        return;
                    }

                    try (ResponseBody body = response.body()) {
                        if (body == null) {
                            onError.accept("Empty response from AI service");
                            return;
                        }

                        BufferedReader reader = new BufferedReader(
                                new InputStreamReader(body.byteStream()));
                        String line;

                        while ((line = reader.readLine()) != null) {
                            if (line.isEmpty()) continue;
                            if (line.equals("data: [DONE]")) {
                                onComplete.run();
                                return;
                            }
                            if (!line.startsWith("data: ")) continue;

                            String jsonData = line.substring(6);
                            try {
                                JsonNode node = objectMapper.readTree(jsonData);
                                JsonNode choices = node.path("choices");
                                if (choices.isArray() && !choices.isEmpty()) {
                                    JsonNode delta = choices.get(0).path("delta");
                                    if (delta.has("content")) {
                                        String content = delta.get("content").asText();
                                        // Don't filter - pass all content including spaces
                                        if (content != null) {
                                            onChunk.accept(content);
                                        }
                                    }
                                }
                            } catch (Exception e) {
                                log.debug("Failed to parse chunk: {}", e.getMessage());
                            }
                        }

                        onComplete.run();

                    } catch (IOException e) {
                        log.error("Error reading stream: {}", e.getMessage());
                        onError.accept("Error reading AI response: " + e.getMessage());
                    }
                }
            });

        } catch (Exception e) {
            log.error("Failed to start stream: {}", e.getMessage());
            onError.accept("Failed to start AI stream: " + e.getMessage());
        }
    }

    /**
     * Synchronous streaming - blocks until complete
     * Returns the full response text
     */
    public String streamChatSync(List<Map<String, String>> messages) throws Exception {
        if (!isAvailable()) {
            throw new RuntimeException("OpenAI service is not available");
        }

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", model);
        requestBody.put("messages", messages);
        requestBody.put("stream", true);
        requestBody.put("max_tokens", 500);
        requestBody.put("temperature", 0.7);

        String jsonBody = objectMapper.writeValueAsString(requestBody);

        Request request = new Request.Builder()
                .url(baseUrl + "/v1/chat/completions")
                .addHeader("Authorization", "Bearer " + apiKey)
                .addHeader("Content-Type", "application/json")
                .addHeader("Accept", "text/event-stream")
                .post(RequestBody.create(jsonBody, MediaType.parse("application/json")))
                .build();

        StringBuilder fullResponse = new StringBuilder();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new RuntimeException("OpenAI API error: " + response.code());
            }

            ResponseBody body = response.body();
            if (body == null) {
                throw new RuntimeException("Empty response from AI service");
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(body.byteStream()));
            String line;

            while ((line = reader.readLine()) != null) {
                if (line.isEmpty()) continue;
                if (line.equals("data: [DONE]")) break;
                if (!line.startsWith("data: ")) continue;

                String jsonData = line.substring(6);
                try {
                    JsonNode node = objectMapper.readTree(jsonData);
                    JsonNode choices = node.path("choices");
                    if (choices.isArray() && !choices.isEmpty()) {
                        JsonNode delta = choices.get(0).path("delta");
                        if (delta.has("content")) {
                            String content = delta.get("content").asText();
                            if (content != null && !content.isEmpty()) {
                                fullResponse.append(content);
                            }
                        }
                    }
                } catch (Exception ignored) {}
            }
        }

        return fullResponse.toString();
    }
}
