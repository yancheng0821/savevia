package com.savevia.card.mapper;

import com.savevia.card.entity.AffiliateClickTracking;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface AffiliateClickTrackingMapper {

    int insert(AffiliateClickTracking tracking);

    int getClickCountToday(Long cardId);

    int getClickCountTodayByBank(Long cardId, String bankName);

    int getClickCountTodayByAffiliate(Long affiliateLinkId);
}
