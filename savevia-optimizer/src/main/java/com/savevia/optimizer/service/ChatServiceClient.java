package com.savevia.optimizer.service;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.chat.ChatMessageDTO;
import com.savevia.optimizer.dto.chat.ConversationDTO;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@FeignClient(name = "savevia-user", path = "/api/v1/chat", contextId = "chatServiceClient")
public interface ChatServiceClient {

    /**
     * Create a new conversation
     */
    @PostMapping("/conversations")
    Result<ConversationDTO> createConversation(
            @RequestHeader("X-User-Id") Long userId,
            @RequestBody Map<String, String> body);

    /**
     * Get user's conversations
     */
    @GetMapping("/conversations")
    Result<List<ConversationDTO>> getConversations(
            @RequestHeader("X-User-Id") Long userId,
            @RequestParam(defaultValue = "20") int limit);

    /**
     * Get a specific conversation
     */
    @GetMapping("/conversations/{id}")
    Result<ConversationDTO> getConversation(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable("id") Long id);

    /**
     * Delete a conversation
     */
    @DeleteMapping("/conversations/{id}")
    Result<String> deleteConversation(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable("id") Long id);

    /**
     * Get messages for a conversation
     */
    @GetMapping("/conversations/{id}/messages")
    Result<List<ChatMessageDTO>> getMessages(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable("id") Long id);

    /**
     * Add a message to a conversation
     */
    @PostMapping("/conversations/{id}/messages")
    Result<ChatMessageDTO> addMessage(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable("id") Long id,
            @RequestBody Map<String, String> body);

    /**
     * Get recent messages for AI context
     */
    @GetMapping("/conversations/{id}/messages/recent")
    Result<List<ChatMessageDTO>> getRecentMessages(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable("id") Long id,
            @RequestParam(defaultValue = "10") int limit);
}
