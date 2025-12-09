package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.SaveUserCardsRequest;
import com.savevia.user.service.UserCardService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/users/me/cards")
@RequiredArgsConstructor
public class UserCardController {

    private final UserCardService userCardService;

    /**
     * Get current user's saved cards
     */
    @GetMapping
    public Result<List<Long>> getUserCards(@RequestHeader("X-User-Id") Long userId) {
        List<Long> cardIds = userCardService.getUserCardIds(userId);
        return Result.success(cardIds);
    }

    /**
     * Save/replace user's card selection
     */
    @PostMapping
    public Result<List<Long>> saveUserCards(
            @RequestHeader("X-User-Id") Long userId,
            @Valid @RequestBody SaveUserCardsRequest request) {
        List<Long> savedCards = userCardService.saveUserCards(userId, request.getCardIds());
        return Result.success("Cards saved successfully", savedCards);
    }

    /**
     * Add a single card
     */
    @PostMapping("/{cardId}")
    public Result<String> addCard(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long cardId) {
        boolean added = userCardService.addCard(userId, cardId);
        if (added) {
            return Result.success("Card added", "added");
        }
        return Result.success("Card already exists", "exists");
    }

    /**
     * Remove a single card
     */
    @DeleteMapping("/{cardId}")
    public Result<String> removeCard(
            @RequestHeader("X-User-Id") Long userId,
            @PathVariable Long cardId) {
        userCardService.removeCard(userId, cardId);
        return Result.success("Card removed", "removed");
    }
}
