package com.savevia.user.mapper;

import com.savevia.user.entity.UserProfileFact;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserProfileFactMapper {

    /**
     * Insert a new fact
     */
    int insert(UserProfileFact fact);

    /**
     * Insert or update fact (upsert)
     */
    int upsert(UserProfileFact fact);

    /**
     * Get all facts for a user
     */
    List<UserProfileFact> selectByUserId(@Param("userId") Long userId);

    /**
     * Get facts by user and categories
     */
    List<UserProfileFact> selectByUserIdAndCategories(
            @Param("userId") Long userId,
            @Param("categories") List<String> categories);

    /**
     * Get a specific fact
     */
    UserProfileFact selectByUserIdAndCategoryAndKey(
            @Param("userId") Long userId,
            @Param("factCategory") String factCategory,
            @Param("factKey") String factKey);

    /**
     * Delete a specific fact
     */
    int deleteByUserIdAndCategoryAndKey(
            @Param("userId") Long userId,
            @Param("factCategory") String factCategory,
            @Param("factKey") String factKey);

    /**
     * Delete all facts for a user
     */
    int deleteByUserId(@Param("userId") Long userId);
}
