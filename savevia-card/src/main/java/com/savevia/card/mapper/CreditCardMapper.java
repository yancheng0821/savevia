package com.savevia.card.mapper;

import com.savevia.card.entity.CreditCard;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CreditCardMapper {

    /**
     * 根据ID查询信用卡
     */
    CreditCard selectById(@Param("id") Long id);

    /**
     * 查询所有有效的信用卡
     */
    List<CreditCard> selectAllActive();

    /**
     * 根据银行查询信用卡
     */
    List<CreditCard> selectByBank(@Param("bank") String bank);

    /**
     * 根据ID列表批量查询
     */
    List<CreditCard> selectByIds(@Param("ids") List<Long> ids);

    /**
     * 插入信用卡
     */
    int insert(CreditCard card);

    /**
     * 更新信用卡
     */
    int update(CreditCard card);

    /**
     * 删除信用卡（软删除）
     */
    int deleteById(@Param("id") Long id);
}
