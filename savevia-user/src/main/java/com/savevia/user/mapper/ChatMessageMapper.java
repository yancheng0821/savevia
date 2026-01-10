package com.savevia.user.mapper;

import com.savevia.user.entity.ChatMessage;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ChatMessageMapper {

    /**
     * Insert a new message
     */
    int insert(ChatMessage message);

    /**
     * Get messages for a conversation, ordered by created_at asc
     */
    List<ChatMessage> selectByConversationId(@Param("conversationId") Long conversationId);

    /**
     * Get recent messages for a conversation (for context)
     */
    List<ChatMessage> selectRecentByConversationId(
            @Param("conversationId") Long conversationId,
            @Param("limit") int limit);

    /**
     * Get first message of a conversation (for title)
     */
    ChatMessage selectFirstByConversationId(@Param("conversationId") Long conversationId);

    /**
     * Delete messages by conversation id
     */
    int deleteByConversationId(@Param("conversationId") Long conversationId);
}
