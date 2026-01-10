package com.savevia.user.service;

import com.savevia.user.entity.ChatConversation;
import com.savevia.user.entity.ChatMessage;
import com.savevia.user.mapper.ChatConversationMapper;
import com.savevia.user.mapper.ChatMessageMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatConversationService {

    private final ChatConversationMapper conversationMapper;
    private final ChatMessageMapper messageMapper;

    /**
     * Create a new conversation
     */
    @Transactional
    public ChatConversation createConversation(Long userId, String title) {
        ChatConversation conversation = ChatConversation.builder()
                .userId(userId)
                .title(title != null ? title : "New Conversation")
                .build();
        conversationMapper.insert(conversation);
        log.info("Created conversation {} for user {}", conversation.getId(), userId);
        return conversation;
    }

    /**
     * Get conversation by ID (with ownership check)
     */
    public ChatConversation getConversation(Long conversationId, Long userId) {
        int count = conversationMapper.countByIdAndUserId(conversationId, userId);
        if (count == 0) {
            return null;
        }
        return conversationMapper.selectById(conversationId);
    }

    /**
     * Get user's conversations (most recent first)
     */
    public List<ChatConversation> getUserConversations(Long userId, int limit) {
        return conversationMapper.selectByUserId(userId, limit);
    }

    /**
     * Update conversation title
     */
    @Transactional
    public boolean updateTitle(Long conversationId, Long userId, String title) {
        int count = conversationMapper.countByIdAndUserId(conversationId, userId);
        if (count == 0) {
            return false;
        }
        conversationMapper.updateTitle(conversationId, title);
        return true;
    }

    /**
     * Delete a conversation (and all its messages via cascade)
     */
    @Transactional
    public boolean deleteConversation(Long conversationId, Long userId) {
        int count = conversationMapper.countByIdAndUserId(conversationId, userId);
        if (count == 0) {
            return false;
        }
        // Delete messages first (even though cascade should handle it)
        messageMapper.deleteByConversationId(conversationId);
        conversationMapper.deleteById(conversationId);
        log.info("Deleted conversation {} for user {}", conversationId, userId);
        return true;
    }

    /**
     * Add a message to a conversation
     */
    @Transactional
    public ChatMessage addMessage(Long conversationId, String role, String content) {
        ChatMessage message = ChatMessage.builder()
                .conversationId(conversationId)
                .role(role)
                .content(content)
                .build();
        messageMapper.insert(message);
        // Update conversation timestamp
        conversationMapper.updateTimestamp(conversationId);
        return message;
    }

    /**
     * Get messages for a conversation
     */
    public List<ChatMessage> getMessages(Long conversationId) {
        return messageMapper.selectByConversationId(conversationId);
    }

    /**
     * Get recent messages for context (for AI prompts)
     */
    public List<ChatMessage> getRecentMessages(Long conversationId, int limit) {
        return messageMapper.selectRecentByConversationId(conversationId, limit);
    }

    /**
     * Auto-generate title from first message
     */
    @Transactional
    public void autoUpdateTitle(Long conversationId) {
        ChatMessage firstMessage = messageMapper.selectFirstByConversationId(conversationId);
        if (firstMessage != null && firstMessage.getContent() != null) {
            String content = firstMessage.getContent();
            // Take first 50 chars as title
            String title = content.length() > 50 ? content.substring(0, 47) + "..." : content;
            conversationMapper.updateTitle(conversationId, title);
        }
    }
}
