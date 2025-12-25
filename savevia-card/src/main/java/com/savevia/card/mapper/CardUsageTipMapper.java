package com.savevia.card.mapper;

import com.savevia.card.entity.CardUsageTip;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CardUsageTipMapper {

    /**
     * 根据卡片ID查询所有使用指南
     */
    List<CardUsageTip> selectByCardId(@Param("cardId") Long cardId);

    /**
     * 根据卡片ID和类型查询使用指南
     */
    List<CardUsageTip> selectByCardIdAndType(@Param("cardId") Long cardId, @Param("tipType") String tipType);

    /**
     * 插入使用指南
     */
    int insert(CardUsageTip tip);

    /**
     * 批量插入使用指南
     */
    int batchInsert(@Param("tips") List<CardUsageTip> tips);

    /**
     * 更新使用指南
     */
    int update(CardUsageTip tip);

    /**
     * 删除使用指南
     */
    int deleteById(@Param("id") Long id);

    /**
     * 删除卡片的所有使用指南
     */
    int deleteByCardId(@Param("cardId") Long cardId);
}
