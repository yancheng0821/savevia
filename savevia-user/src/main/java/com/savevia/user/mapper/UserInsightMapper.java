package com.savevia.user.mapper;

import com.savevia.user.entity.UserInsight;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface UserInsightMapper {

    int insert(UserInsight insight);

    int update(UserInsight insight);

    UserInsight findById(@Param("id") Long id);

    List<UserInsight> findByUserId(@Param("userId") Long userId);

    List<UserInsight> findActiveByUserId(@Param("userId") Long userId, @Param("now") LocalDateTime now);

    List<UserInsight> findByUserIdAndType(@Param("userId") Long userId, @Param("insightType") String insightType);

    int upsertByKey(@Param("userId") Long userId, @Param("insightKey") String insightKey, @Param("insight") UserInsight insight);

    int deleteExpired(@Param("now") LocalDateTime now);
}
