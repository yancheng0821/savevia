package com.savevia.user.mapper;

import com.savevia.user.entity.UserEvent;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Mapper
public interface UserEventMapper {

    /**
     * Insert a new event
     */
    int insert(UserEvent event);

    /**
     * Count events by type
     */
    List<Map<String, Object>> countByEventType(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count distinct active users (users with events in date range)
     */
    long countActiveUsers(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count total events
     */
    long countTotal(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count events by type and date (for trend charts)
     */
    List<Map<String, Object>> countByEventTypeAndDate(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Get distinct active user IDs (users with events in date range)
     */
    List<Long> getActiveUserIds(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count events by type for a specific user
     */
    List<Map<String, Object>> countByEventTypeForUser(
            @Param("userId") Long userId,
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count events by type and date for a specific user (for trend charts)
     */
    List<Map<String, Object>> countByEventTypeAndDateForUser(
            @Param("userId") Long userId,
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );

    /**
     * Count daily active users (distinct users per day)
     */
    List<Map<String, Object>> countDailyActiveUsers(
            @Param("from") LocalDateTime from,
            @Param("to") LocalDateTime to
    );
}
