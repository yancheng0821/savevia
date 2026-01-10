package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.entity.ChatConversation;
import com.savevia.user.entity.ChatMessage;
import com.savevia.user.service.ChatConversationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST endpoints for chat conversation and message persistence
 * Called internally by savevia-optimizer via Feign
 */
@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatConversationService chatService;

    /**
     * Create a new conversation
     */
    @PostMapping("/conversations")
    public Result<ChatConversation> createConversation(
            @RequestHeader("X-User-Id") Long userId,
            @RequestBody(required = false) Map<String, String> body) {
        String title = body != null ? body.get("title") : null;
        ChatConversation conversation = chatService.createConversation(userId, title);
        return Result.success(conversation);
    }

    /**
     * Get user's conversations
     */
    @GetMapping("/conversations")
    public Result<List<ChatConversation>> getConversations(
            @RequestHeader("X-User-Id") Long userId,
            @RequestParam(defaultValue = "20") int limit) {
        List<ChatConversation> conversations = chatService.getUserConversations(userId, limit);
        return Result.success(conversations);
    }

    /**
     * Get a specific conversation
     */
    @GetMapping("/conversations/{id}")
    public Result<ChatConversation> getConversation(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id) {
        ChatConversation conversation = chatService.getConversation(id, userId);
        if (conversation == null) {
            return Result.error("Conversation not found");
        }
        return Result.success(conversation);
    }

    /**
     * Delete a conversation
     */
    @DeleteMapping("/conversations/{id}")
    public Result<String> deleteConversation(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id) {
        boolean deleted = chatService.deleteConversation(id, userId);
        if (!deleted) {
            return Result.error("Conversation not found or access denied");
        }
        return Result.success("Conversation deleted");
    }

    /**
     * Get messages for a conversation
     */
    @GetMapping("/conversations/{id}/messages")
    public Result<List<ChatMessage>> getMessages(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id) {
        // Verify ownership
        ChatConversation conversation = chatService.getConversation(id, userId);
        if (conversation == null) {
            return Result.error("Conversation not found or access denied");
        }
        List<ChatMessage> messages = chatService.getMessages(id);
        return Result.success(messages);
    }

    /**
     * Add a message to a conversation (internal use by optimizer service)
     */
    @PostMapping("/conversations/{id}/messages")
    public Result<ChatMessage> addMessage(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        // Verify ownership
        ChatConversation conversation = chatService.getConversation(id, userId);
        if (conversation == null) {
            return Result.error("Conversation not found or access denied");
        }

        String role = body.get("role");
        String content = body.get("content");

        if (role == null || content == null) {
            return Result.error("Role and content are required");
        }

        ChatMessage message = chatService.addMessage(id, role, content);
        return Result.success(message);
    }

    /**
     * Get recent messages for AI context (internal use)
     */
    @GetMapping("/conversations/{id}/messages/recent")
    public Result<List<ChatMessage>> getRecentMessages(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id,
            @RequestParam(defaultValue = "10") int limit) {
        // Verify ownership
        ChatConversation conversation = chatService.getConversation(id, userId);
        if (conversation == null) {
            return Result.error("Conversation not found or access denied");
        }
        List<ChatMessage> messages = chatService.getRecentMessages(id, limit);
        return Result.success(messages);
    }

    /**
     * Update conversation title
     */
    @PatchMapping("/conversations/{id}/title")
    public Result<String> updateTitle(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        String title = body.get("title");
        if (title == null || title.isEmpty()) {
            return Result.error("Title is required");
        }
        boolean updated = chatService.updateTitle(id, userId, title);
        if (!updated) {
            return Result.error("Conversation not found or access denied");
        }
        return Result.success("Title updated");
    }
}
