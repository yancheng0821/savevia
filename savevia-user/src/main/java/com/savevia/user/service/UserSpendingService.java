package com.savevia.user.service;

import com.savevia.user.entity.UserSpending;
import com.savevia.user.mapper.UserSpendingMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class UserSpendingService {

    private final UserSpendingMapper userSpendingMapper;

    public Map<String, BigDecimal> getUserSpending(Long userId) {
        List<UserSpending> spendings = userSpendingMapper.selectByUserId(userId);
        Map<String, BigDecimal> result = new HashMap<>();
        for (UserSpending spending : spendings) {
            result.put(spending.getCategory(), spending.getAmount());
        }
        return result;
    }

    @Transactional
    public Map<String, BigDecimal> saveUserSpending(Long userId, Map<String, BigDecimal> spending) {
        // Delete existing spending data
        userSpendingMapper.deleteByUserId(userId);

        // Insert new spending data (only non-zero values)
        if (spending != null && !spending.isEmpty()) {
            List<UserSpending> list = new ArrayList<>();
            for (Map.Entry<String, BigDecimal> entry : spending.entrySet()) {
                if (entry.getValue() != null && entry.getValue().compareTo(BigDecimal.ZERO) > 0) {
                    UserSpending us = new UserSpending();
                    us.setUserId(userId);
                    us.setCategory(entry.getKey());
                    us.setAmount(entry.getValue());
                    list.add(us);
                }
            }
            if (!list.isEmpty()) {
                userSpendingMapper.batchInsert(list);
            }
        }

        return spending;
    }
}
