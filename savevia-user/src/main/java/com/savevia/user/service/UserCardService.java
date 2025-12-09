package com.savevia.user.service;

import com.savevia.user.mapper.UserCardMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserCardService {

    private final UserCardMapper userCardMapper;

    /**
     * Get all card IDs for a user
     */
    public List<Long> getUserCardIds(Long userId) {
        return userCardMapper.selectCardIdsByUserId(userId);
    }

    /**
     * Save user's card selection (replace existing)
     */
    @Transactional
    public List<Long> saveUserCards(Long userId, List<Long> cardIds) {
        // Delete all existing cards
        userCardMapper.deleteAllByUserId(userId);

        // Insert new cards if any
        if (cardIds != null && !cardIds.isEmpty()) {
            userCardMapper.batchInsert(userId, cardIds);
            log.info("Saved {} cards for user {}", cardIds.size(), userId);
        }

        return cardIds;
    }

    /**
     * Add a single card to user's collection
     */
    @Transactional
    public boolean addCard(Long userId, Long cardId) {
        int exists = userCardMapper.countByUserIdAndCardId(userId, cardId);
        if (exists > 0) {
            return false; // Already has this card
        }

        userCardMapper.batchInsert(userId, List.of(cardId));
        log.info("Added card {} for user {}", cardId, userId);
        return true;
    }

    /**
     * Remove a single card from user's collection
     */
    @Transactional
    public boolean removeCard(Long userId, Long cardId) {
        int deleted = userCardMapper.deleteByUserIdAndCardId(userId, cardId);
        if (deleted > 0) {
            log.info("Removed card {} from user {}", cardId, userId);
            return true;
        }
        return false;
    }
}
