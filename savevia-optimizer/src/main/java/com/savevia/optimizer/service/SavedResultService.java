package com.savevia.optimizer.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.optimizer.dto.OptimizationResult;
import com.savevia.optimizer.dto.SaveResultResponse;
import com.savevia.optimizer.entity.SavedResult;
import com.savevia.optimizer.mapper.SavedResultMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.security.SecureRandom;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class SavedResultService {

    private final SavedResultMapper savedResultMapper;
    private final ObjectMapper objectMapper;

    @Value("${app.base-url:http://localhost:5173}")
    private String baseUrl;

    private static final String CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789";
    private static final SecureRandom RANDOM = new SecureRandom();

    public SaveResultResponse saveResult(OptimizationResult result, Long userId) {
        String shareId = generateShareId();

        // For logged-in users, update existing record instead of creating new one
        if (userId != null) {
            SavedResult existing = savedResultMapper.selectByUserIdLatest(userId);
            if (existing != null) {
                savedResultMapper.updateShareId(existing.getId(), shareId);
                String shareUrl = baseUrl + "/share/" + shareId;
                return new SaveResultResponse(shareId, shareUrl);
            }
        }

        // For anonymous users or if no existing record, create new one
        try {
            String resultJson = objectMapper.writeValueAsString(result);

            SavedResult savedResult = new SavedResult();
            savedResult.setShareId(shareId);
            savedResult.setUserId(userId);
            savedResult.setResultJson(resultJson);
            savedResult.setNetAnnualSavings(result.getNetAnnualSavings());
            savedResult.setAnnualReward(result.getAnnualReward());
            savedResult.setTotalAnnualFees(result.getTotalAnnualFees());
            savedResult.setExpiresAt(LocalDateTime.now().plusDays(30));

            savedResultMapper.insert(savedResult);

            String shareUrl = baseUrl + "/share/" + shareId;
            return new SaveResultResponse(shareId, shareUrl);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize result", e);
        }
    }

    public OptimizationResult getByShareId(String shareId) {
        SavedResult saved = savedResultMapper.selectByShareId(shareId);
        if (saved == null) {
            return null;
        }

        try {
            return objectMapper.readValue(saved.getResultJson(), OptimizationResult.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to deserialize result", e);
        }
    }

    private String generateShareId() {
        StringBuilder sb = new StringBuilder(8);
        for (int i = 0; i < 8; i++) {
            sb.append(CHARS.charAt(RANDOM.nextInt(CHARS.length())));
        }
        return sb.toString();
    }

    /**
     * Save user's current optimization result (for logged-in users)
     * Updates existing record if exists, otherwise creates new one
     */
    public void saveUserResult(OptimizationResult result, Long userId) {
        if (userId == null) {
            return;
        }

        try {
            String resultJson = objectMapper.writeValueAsString(result);

            SavedResult savedResult = new SavedResult();
            savedResult.setShareId(null);
            savedResult.setUserId(userId);
            savedResult.setResultJson(resultJson);
            savedResult.setNetAnnualSavings(result.getNetAnnualSavings());
            savedResult.setAnnualReward(result.getAnnualReward());
            savedResult.setTotalAnnualFees(result.getTotalAnnualFees());

            // Check if user already has a saved result
            SavedResult existing = savedResultMapper.selectByUserIdLatest(userId);
            if (existing != null) {
                // Update existing record
                savedResultMapper.updateUserResult(savedResult);
            } else {
                // Insert new record
                savedResultMapper.insertUserResult(savedResult);
            }
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize result", e);
        }
    }

    /**
     * Get user's latest optimization result
     */
    public OptimizationResult getUserResult(Long userId) {
        if (userId == null) {
            return null;
        }

        SavedResult saved = savedResultMapper.selectByUserIdLatest(userId);
        if (saved == null) {
            return null;
        }

        try {
            return objectMapper.readValue(saved.getResultJson(), OptimizationResult.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to deserialize result", e);
        }
    }
}
