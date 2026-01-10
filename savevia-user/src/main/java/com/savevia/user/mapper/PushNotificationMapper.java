package com.savevia.user.mapper;

import com.savevia.user.entity.PushNotification;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface PushNotificationMapper {

    int insert(PushNotification notification);

    int update(PushNotification notification);

    PushNotification findById(@Param("id") Long id);

    List<PushNotification> findByUserId(@Param("userId") Long userId, @Param("limit") Integer limit);

    List<PushNotification> findPendingToSend(@Param("now") LocalDateTime now);

    int updateStatus(@Param("id") Long id, @Param("status") String status, @Param("errorMessage") String errorMessage);

    int markAsSent(@Param("id") Long id, @Param("sentAt") LocalDateTime sentAt);

    int markAsRead(@Param("id") Long id, @Param("readAt") LocalDateTime readAt);

    int countTodayByUserId(@Param("userId") Long userId, @Param("startOfDay") LocalDateTime startOfDay);

    int cancelPending(@Param("userId") Long userId, @Param("notificationType") String notificationType);

    /**
     * Count recent notifications sent to user within a time window
     */
    int countRecentByUserId(@Param("userId") Long userId, @Param("since") LocalDateTime since);

    /**
     * Get recent message types sent to user (for diversity tracking)
     */
    List<String> findRecentMessageTypes(@Param("userId") Long userId, @Param("since") LocalDateTime since, @Param("limit") int limit);
}
