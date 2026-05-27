package com.savevia.user.service;

import com.savevia.user.dto.MemoryContextDTO;
import com.savevia.user.entity.UserConversationSummary;
import com.savevia.user.entity.UserProfileFact;

import java.util.List;
import java.util.Set;

/**
 * Service interface for user long-term memory management.
 * This interface allows for future implementation swapping (e.g., Redis cache layer).
 */
public interface MemoryService {

    /**
     * Save or update a user profile fact.
     * If the fact already exists (same userId + category + key), it will be updated.
     *
     * @param userId       User ID
     * @param category     Fact category (identity, spending, preference, exclusion, lifestyle)
     * @param key          Fact key within the category
     * @param value        Fact value
     * @param source       Source type (explicit, inferred)
     */
    void saveProfileFact(Long userId, String category, String key, String value, String source);

    /**
     * Get all profile facts for a user.
     *
     * @param userId User ID
     * @return List of all facts
     */
    List<UserProfileFact> getProfileFacts(Long userId);

    /**
     * Get profile facts for specific categories.
     *
     * @param userId     User ID
     * @param categories Set of categories to retrieve
     * @return List of facts in the specified categories
     */
    List<UserProfileFact> getProfileFactsByCategories(Long userId, Set<String> categories);

    /**
     * Delete a specific profile fact.
     *
     * @param userId   User ID
     * @param category Fact category
     * @param key      Fact key
     */
    void deleteProfileFact(Long userId, String category, String key);

    /**
     * Save a conversation summary.
     *
     * @param userId                User ID
     * @param summary               Summary text
     * @param keyTopics             JSON array of key topics
     * @param recommendations       JSON array of recommendations
     * @param sourceConversationIds JSON array of source conversation IDs
     */
    void saveSummary(Long userId, String summary, String keyTopics,
                     String recommendations, String sourceConversationIds);

    /**
     * Get recent conversation summaries for a user.
     *
     * @param userId User ID
     * @param limit  Maximum number of summaries to return
     * @return List of recent summaries
     */
    List<UserConversationSummary> getRecentSummaries(Long userId, int limit);

    /**
     * Get the complete memory context for a user, ready for prompt injection.
     *
     * @param userId     User ID
     * @param categories Categories to include (null for all)
     * @return Memory context DTO with formatted text
     */
    MemoryContextDTO getUserMemoryContext(Long userId, Set<String> categories);

    /**
     * Clear all memory data for a user.
     *
     * @param userId User ID
     */
    void clearUserMemory(Long userId);
}
