package com.savevia.user.mapper;

import com.savevia.user.entity.UserCard;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserCardMapper {

    /**
     * Get all cards for a user
     */
    List<Long> selectCardIdsByUserId(@Param("userId") Long userId);

    /**
     * Check if user has a specific card
     */
    int countByUserIdAndCardId(@Param("userId") Long userId, @Param("cardId") Long cardId);

    /**
     * Insert a user card
     */
    int insert(UserCard userCard);

    /**
     * Delete a specific card from user
     */
    int deleteByUserIdAndCardId(@Param("userId") Long userId, @Param("cardId") Long cardId);

    /**
     * Delete all cards for a user
     */
    int deleteAllByUserId(@Param("userId") Long userId);

    /**
     * Batch insert cards for a user
     */
    int batchInsert(@Param("userId") Long userId, @Param("cardIds") List<Long> cardIds);
}
