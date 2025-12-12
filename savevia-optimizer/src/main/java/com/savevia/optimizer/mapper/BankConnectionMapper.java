package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.BankConnection;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface BankConnectionMapper {

    @Insert("INSERT INTO bank_connections (user_id, flinks_login_id, institution_name, status) " +
            "VALUES (#{userId}, #{flinksLoginId}, #{institutionName}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(BankConnection connection);

    @Update("UPDATE bank_connections SET status = #{status}, last_sync_at = #{lastSyncAt}, " +
            "error_message = #{errorMessage}, flinks_login_id = #{flinksLoginId} WHERE id = #{id}")
    int updateStatus(BankConnection connection);

    @Select("SELECT * FROM bank_connections WHERE user_id = #{userId}")
    List<BankConnection> findByUserId(@Param("userId") Long userId);

    @Select("SELECT * FROM bank_connections WHERE id = #{id}")
    BankConnection findById(@Param("id") Long id);

    @Select("SELECT * FROM bank_connections WHERE user_id = #{userId} AND flinks_login_id = #{loginId}")
    BankConnection findByUserAndLoginId(@Param("userId") Long userId, @Param("loginId") String loginId);

    @Select("SELECT * FROM bank_connections WHERE user_id = #{userId} AND institution_name = #{institutionName} LIMIT 1")
    BankConnection findByUserAndInstitution(@Param("userId") Long userId, @Param("institutionName") String institutionName);

    @Delete("DELETE FROM bank_connections WHERE id = #{id}")
    int deleteById(@Param("id") Long id);
}
