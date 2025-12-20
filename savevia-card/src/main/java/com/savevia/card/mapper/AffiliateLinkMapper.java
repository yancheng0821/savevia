package com.savevia.card.mapper;

import com.savevia.card.entity.AffiliateLink;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface AffiliateLinkMapper {

    // 根据卡片ID获取所有活跃的联盟链接
    List<AffiliateLink> selectByCardIdActive(Long cardId);

    // 根据ID获取联盟链接
    AffiliateLink selectById(Long id);

    // 根据卡片ID和联盟类型获取
    AffiliateLink selectByCardIdAndType(Long cardId, String affiliateType);

    // 获取所有活跃的联盟链接
    List<AffiliateLink> selectAllActive();

    // 获取特定银行的所有活跃链接
    List<AffiliateLink> selectByBankNameActive(String bankName);

    // 插入联盟链接
    int insert(AffiliateLink affiliateLink);

    // 更新联盟链接
    int update(AffiliateLink affiliateLink);

    // 根据ID删除（逻辑删除或物理删除）
    int deleteById(Long id);

    // 批量获取
    List<AffiliateLink> selectByCardIds(List<Long> cardIds);

    // 获取卡片的第一个活跃联盟链接
    AffiliateLink selectFirstActiveByCardId(Long cardId);
}
