package com.savevia.user.controller;

import com.savevia.common.response.Result;
import com.savevia.user.dto.MemoryContextDTO;
import com.savevia.user.dto.MemoryExtractionResultDTO;
import com.savevia.user.entity.UserProfileFact;
import com.savevia.user.job.MemoryExtractionJob;
import com.savevia.user.service.MemoryExtractionService;
import com.savevia.user.service.MemoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Internal API for user memory management.
 * Used by optimizer service to retrieve memory context.
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/internal/memory")
@RequiredArgsConstructor
public class MemoryController {

    private final MemoryService memoryService;
    private final MemoryExtractionService extractionService;
    private final MemoryExtractionJob extractionJob;

    /**
     * Get user's memory context for prompt injection.
     *
     * @param userId     User ID
     * @param categories Optional comma-separated categories to include
     * @return Memory context DTO
     */
    @GetMapping("/{userId}/context")
    public Result<MemoryContextDTO> getUserMemoryContext(
            @PathVariable Long userId,
            @RequestParam(required = false) String categories) {

        Set<String> categorySet = null;
        if (categories != null && !categories.isEmpty()) {
            categorySet = Set.of(categories.split(","));
        }

        MemoryContextDTO context = memoryService.getUserMemoryContext(userId, categorySet);
        return Result.success(context);
    }

    /**
     * Get all profile facts for a user.
     *
     * @param userId User ID
     * @return List of profile facts
     */
    @GetMapping("/{userId}/facts")
    public Result<List<UserProfileFact>> getUserFacts(@PathVariable Long userId) {
        List<UserProfileFact> facts = memoryService.getProfileFacts(userId);
        return Result.success(facts);
    }

    /**
     * Update or create a profile fact.
     *
     * @param userId User ID
     * @param body   Request body with category, key, value
     * @return Success result
     */
    @PutMapping("/{userId}/facts")
    public Result<Void> updateFact(
            @PathVariable Long userId,
            @RequestBody Map<String, String> body) {

        String category = body.get("category");
        String key = body.get("key");
        String value = body.get("value");
        String source = body.getOrDefault("source", "explicit");

        if (category == null || key == null || value == null) {
            return Result.error("Missing required fields: category, key, value");
        }

        memoryService.saveProfileFact(userId, category, key, value, source);
        return Result.success(null);
    }

    /**
     * Delete a profile fact.
     *
     * @param userId   User ID
     * @param category Fact category
     * @param key      Fact key
     * @return Success result
     */
    @DeleteMapping("/{userId}/facts/{category}/{key}")
    public Result<Void> deleteFact(
            @PathVariable Long userId,
            @PathVariable String category,
            @PathVariable String key) {

        memoryService.deleteProfileFact(userId, category, key);
        return Result.success(null);
    }

    /**
     * Save the result of an LLM-extracted memory. Called by savevia-ai (Python)
     * after it runs its extraction chain.
     *
     * Reuses the same persistence logic the in-process Java extraction uses:
     * upsert per fact, append a summary row.
     */
    @PostMapping("/{userId}/extracted")
    public Result<Void> saveExtractedMemory(
            @PathVariable Long userId,
            @RequestParam(value = "conversationId", required = false) Long conversationId,
            @RequestBody MemoryExtractionResultDTO body) {

        if (body == null) {
            return Result.error("Request body is required");
        }
        extractionService.saveExtractedMemory(userId, body, conversationId);
        return Result.success(null);
    }

    /**
     * Manually trigger memory extraction for a conversation (debug endpoint).
     *
     * @param conversationId Conversation ID
     * @return Extraction result
     */
    @PostMapping("/extract/{conversationId}")
    public Result<MemoryExtractionResultDTO> extractMemory(@PathVariable Long conversationId) {
        MemoryExtractionResultDTO result = extractionService.extractMemoryFromConversation(conversationId);
        if (result == null) {
            return Result.error("Extraction failed or conversation not found");
        }
        return Result.success(result);
    }

    /**
     * Trigger memory extraction for all unprocessed conversations of a user.
     *
     * @param userId User ID
     * @return Number of conversations processed
     */
    @PostMapping("/extract/user/{userId}")
    public Result<Integer> extractUserMemories(@PathVariable Long userId) {
        int processed = extractionJob.processUserConversations(userId);
        return Result.success(processed);
    }

    /**
     * Clear all memory data for a user.
     *
     * @param userId User ID
     * @return Success result
     */
    @DeleteMapping("/{userId}")
    public Result<Void> clearUserMemory(@PathVariable Long userId) {
        memoryService.clearUserMemory(userId);
        return Result.success(null);
    }
}
