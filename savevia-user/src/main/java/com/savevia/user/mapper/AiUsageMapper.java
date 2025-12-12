package com.savevia.user.mapper;

import com.savevia.user.entity.AiUsage;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AiUsageMapper {

    AiUsage findByUserIdAndYearMonth(@Param("userId") Long userId, @Param("yearMonth") String yearMonth);

    int incrementUsage(@Param("userId") Long userId, @Param("yearMonth") String yearMonth);

    int updateMonthlyLimit(@Param("userId") Long userId, @Param("yearMonth") String yearMonth, @Param("limit") int limit);

    int insert(AiUsage aiUsage);
}
