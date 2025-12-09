package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.SavedResult;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SavedResultMapper {
    int insert(SavedResult result);
    SavedResult selectByShareId(@Param("shareId") String shareId);
    SavedResult selectByUserIdLatest(@Param("userId") Long userId);
    int insertUserResult(SavedResult result);
    int updateUserResult(SavedResult result);
    int updateShareId(@Param("id") Long id, @Param("shareId") String shareId);
}
