package com.savevia.user.mapper;

import com.savevia.user.entity.UserConversationSummary;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserConversationSummaryMapper {

    /**
     * Insert a new summary
     */
    int insert(UserConversationSummary summary);

    /**
     * Get recent summaries for a user
     */
    List<UserConversationSummary> selectRecentByUserId(
            @Param("userId") Long userId,
            @Param("limit") int limit);

    /**
     * Get all summaries for a user
     */
    List<UserConversationSummary> selectByUserId(@Param("userId") Long userId);

    /**
     * Delete summaries older than N days
     */
    int deleteOlderThan(@Param("days") int days);

    /**
     * Delete all summaries for a user
     */
    int deleteByUserId(@Param("userId") Long userId);
}
