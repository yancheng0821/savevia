package com.savevia.optimizer.mapper;

import com.savevia.optimizer.entity.BankAccount;
import org.apache.ibatis.annotations.*;
import java.util.List;

@Mapper
public interface BankAccountMapper {

    @Insert("INSERT INTO bank_accounts (connection_id, user_id, flinks_account_id, account_type, " +
            "account_name, account_number_masked, institution_name, balance, linked_card_id) " +
            "VALUES (#{connectionId}, #{userId}, #{flinksAccountId}, #{accountType}, " +
            "#{accountName}, #{accountNumberMasked}, #{institutionName}, #{balance}, #{linkedCardId})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(BankAccount account);

    @Update("UPDATE bank_accounts SET balance = #{balance}, is_active = #{isActive}, linked_card_id = #{linkedCardId} WHERE id = #{id}")
    int update(BankAccount account);

    @Select("SELECT * FROM bank_accounts WHERE user_id = #{userId} AND is_active = true")
    List<BankAccount> findActiveByUserId(@Param("userId") Long userId);

    @Select("SELECT * FROM bank_accounts WHERE connection_id = #{connectionId}")
    List<BankAccount> findByConnectionId(@Param("connectionId") Long connectionId);

    @Select("SELECT * FROM bank_accounts WHERE id = #{id}")
    BankAccount findById(@Param("id") Long id);
}
