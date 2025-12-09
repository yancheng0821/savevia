package com.savevia.user.mapper;

import com.savevia.user.entity.UserSpending;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface UserSpendingMapper {
    List<UserSpending> selectByUserId(@Param("userId") Long userId);
    int deleteByUserId(@Param("userId") Long userId);
    int batchInsert(@Param("list") List<UserSpending> list);
}
