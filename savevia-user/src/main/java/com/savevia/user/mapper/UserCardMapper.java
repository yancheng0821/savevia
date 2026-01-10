package com.savevia.user.mapper;

import com.savevia.user.dto.UserCardRewardInfo;
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

    /**
     * Get card names for a user
     */
    List<String> selectCardNamesByUserId(@Param("userId") Long userId);

    /**
     * Get user's top reward categories
     */
    List<String> selectTopCategoriesByUserId(@Param("userId") Long userId);

    /**
     * Get user's card reward info for smart notifications
     */
    List<UserCardRewardInfo> selectUserCardRewardInfo(@Param("userId") Long userId);

    /**
     * Get user's best card for a specific category
     */
    UserCardRewardInfo selectBestCardForCategory(@Param("userId") Long userId, @Param("category") String category);
}
