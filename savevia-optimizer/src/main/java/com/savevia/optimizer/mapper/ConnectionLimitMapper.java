package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.ConnectionHistory;
import com.savevia.optimizer.entity.UserConnectionLimit;
import org.apache.ibatis.annotations.*;

@Mapper
public interface ConnectionLimitMapper {

    @Select("SELECT * FROM user_connection_limits WHERE user_id = #{userId} AND `year_month` = #{yearMonth}")
    @Results({
        @Result(property = "id", column = "id"),
        @Result(property = "userId", column = "user_id"),
        @Result(property = "yearMonth", column = "year_month"),
        @Result(property = "connectionCount", column = "connection_count"),
        @Result(property = "maxConnections", column = "max_connections"),
        @Result(property = "createdAt", column = "created_at"),
        @Result(property = "updatedAt", column = "updated_at")
    })
    UserConnectionLimit findByUserAndMonth(@Param("userId") Long userId, @Param("yearMonth") String yearMonth);

    @Insert("INSERT INTO user_connection_limits (user_id, `year_month`, connection_count, max_connections) " +
            "VALUES (#{userId}, #{yearMonth}, #{connectionCount}, #{maxConnections})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insert(UserConnectionLimit limit);

    @Update("UPDATE user_connection_limits SET connection_count = #{connectionCount}, " +
            "updated_at = CURRENT_TIMESTAMP WHERE id = #{id}")
    void updateConnectionCount(UserConnectionLimit limit);

    @Insert("INSERT INTO connection_history (user_id, institution_name, action, flinks_login_id) " +
            "VALUES (#{userId}, #{institutionName}, #{action}, #{flinksLoginId})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insertHistory(ConnectionHistory history);

    @Select("SELECT COUNT(*) FROM connection_history WHERE user_id = #{userId} " +
            "AND action = 'CONNECT' AND YEAR(created_at) = YEAR(#{yearMonth}) " +
            "AND MONTH(created_at) = MONTH(#{yearMonth})")
    int countMonthlyConnections(@Param("userId") Long userId, @Param("yearMonth") String yearMonth);
}
