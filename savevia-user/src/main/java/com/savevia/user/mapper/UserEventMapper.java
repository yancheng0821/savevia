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

    /**
     * Get last active time for each user in the given list
     */
    List<Map<String, Object>> getLastActiveTimeByUserIds(
            @Param("userIds") List<Long> userIds
    );

    /**
     * Get inactive user IDs (users who haven't had any events since the given time)
     */
    List<Long> getInactiveUserIds(@Param("since") LocalDateTime since);

    /**
     * Get all user IDs who have ever had events
     */
    List<Long> getAllUserIdsWithEvents();
}
