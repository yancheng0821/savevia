package com.savevia.user.mapper;

import com.savevia.user.entity.UserDevice;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface UserDeviceMapper {

    int insert(UserDevice device);

    int update(UserDevice device);

    UserDevice findByToken(@Param("deviceToken") String deviceToken);

    List<UserDevice> findByUserId(@Param("userId") Long userId);

    List<UserDevice> findActiveByUserId(@Param("userId") Long userId);

    int deactivateByToken(@Param("deviceToken") String deviceToken);

    int deactivateAllByUserId(@Param("userId") Long userId);

    int updateLastUsed(@Param("deviceToken") String deviceToken);

    List<Long> findAllActiveUserIds();

    List<Long> findInactiveUserIds(@Param("lastActiveTime") LocalDateTime lastActiveTime);
}
