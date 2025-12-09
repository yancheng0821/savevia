package com.savevia.user.mapper;

import com.savevia.user.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.Optional;

@Mapper
public interface UserMapper {

    /**
     * 根据ID查询用户
     */
    User selectById(@Param("id") Long id);

    /**
     * 根据邮箱查询用户
     */
    Optional<User> selectByEmail(@Param("email") String email);

    /**
     * 根据Google ID查询用户
     */
    Optional<User> selectByGoogleId(@Param("googleId") String googleId);

    /**
     * 根据Apple ID查询用户
     */
    Optional<User> selectByAppleId(@Param("appleId") String appleId);

    /**
     * 根据邮箱验证Token查询用户
     */
    Optional<User> selectByEmailVerificationToken(@Param("token") String token);

    /**
     * 根据密码重置Token查询用户
     */
    Optional<User> selectByPasswordResetToken(@Param("token") String token);

    /**
     * 检查邮箱是否存在
     */
    int countByEmail(@Param("email") String email);

    /**
     * 插入用户
     */
    int insert(User user);

    /**
     * 更新用户
     */
    int update(User user);

    /**
     * 删除用户（软删除）
     */
    int deleteById(@Param("id") Long id);

    /**
     * 清除密码重置Token
     */
    int clearPasswordResetToken(@Param("id") Long id);

    /**
     * 清除邮箱验证Token
     */
    int clearEmailVerificationToken(@Param("id") Long id);
}
