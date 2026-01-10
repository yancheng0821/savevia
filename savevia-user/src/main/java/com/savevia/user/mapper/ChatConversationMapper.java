package com.savevia.user.mapper;

import com.savevia.user.entity.ChatConversation;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ChatConversationMapper {

    /**
     * Insert a new conversation
     */
    int insert(ChatConversation conversation);

    /**
     * Get conversation by id
     */
    ChatConversation selectById(@Param("id") Long id);

    /**
     * Get conversations for a user, ordered by updated_at desc
     */
    List<ChatConversation> selectByUserId(@Param("userId") Long userId, @Param("limit") int limit);

    /**
     * Update conversation title
     */
    int updateTitle(@Param("id") Long id, @Param("title") String title);

    /**
     * Update updated_at timestamp
     */
    int updateTimestamp(@Param("id") Long id);

    /**
     * Delete a conversation
     */
    int deleteById(@Param("id") Long id);

    /**
     * Delete all conversations for a user
     */
    int deleteByUserId(@Param("userId") Long userId);

    /**
     * Check if conversation belongs to user
     */
    int countByIdAndUserId(@Param("id") Long id, @Param("userId") Long userId);
}
