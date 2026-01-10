package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.chat.ChatRequest;
import com.savevia.optimizer.service.ChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;

/**
 * SSE streaming endpoint for AI chat
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
public class ChatStreamController {

    private final ChatService chatService;

    private static final long SSE_TIMEOUT = 120_000L; // 2 minutes

    /**
     * Stream AI chat response via SSE
     */
    @PostMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamChat(
            @RequestHeader("X-User-Id") Long userId,
            @RequestBody ChatRequest request) {

        log.info("Chat stream request from user {}, conversationId: {}",
                userId, request.getConversationId());

        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT);

        // Handle client disconnect
        emitter.onCompletion(() -> log.debug("SSE completed for user {}", userId));
        emitter.onTimeout(() -> {
            log.warn("SSE timeout for user {}", userId);
            emitter.complete();
        });
        emitter.onError(e -> log.error("SSE error for user {}: {}", userId, e.getMessage()));

        // Start async streaming
        chatService.streamResponse(userId, request, emitter);

        return emitter;
    }

    /**
     * Get suggested questions
     */
    @GetMapping("/suggestions")
    public Result<List<String>> getSuggestions(
            @RequestParam(defaultValue = "en") String locale) {
        return Result.success(chatService.getSuggestions(locale));
    }
}
