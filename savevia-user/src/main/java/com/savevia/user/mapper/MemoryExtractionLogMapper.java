package com.savevia.user.mapper;

import com.savevia.user.entity.MemoryExtractionLog;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface MemoryExtractionLogMapper {

    /**
     * Insert a new log entry
     */
    int insert(MemoryExtractionLog log);

    /**
     * Update status to processed
     */
    int updateStatusProcessed(@Param("conversationId") Long conversationId);

    /**
     * Update status to failed with error message
     */
    int updateStatusFailed(
            @Param("conversationId") Long conversationId,
            @Param("errorMessage") String errorMessage);

    /**
     * Check if conversation has been processed
     */
    MemoryExtractionLog selectByConversationId(@Param("conversationId") Long conversationId);

    /**
     * Get pending extractions
     */
    List<MemoryExtractionLog> selectPending(@Param("limit") int limit);

    /**
     * Get failed extractions for retry
     */
    List<MemoryExtractionLog> selectFailed(@Param("limit") int limit);
}
