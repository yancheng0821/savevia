package com.savevia.card.mapper;

import com.savevia.card.entity.RewardRule;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RewardRuleMapper {

    /**
     * 根据卡片ID查询规则
     */
    List<RewardRule> selectByCardId(@Param("cardId") Long cardId);

    /**
     * 根据卡片ID列表批量查询规则
     */
    List<RewardRule> selectByCardIds(@Param("cardIds") List<Long> cardIds);

    /**
     * 插入规则
     */
    int insert(RewardRule rule);

    /**
     * 批量插入规则
     */
    int batchInsert(@Param("rules") List<RewardRule> rules);

    /**
     * 删除卡片的所有规则
     */
    int deleteByCardId(@Param("cardId") Long cardId);
}
