package com.savevia.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * DTO containing user's long-term memory context for chat injection.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemoryContextDTO {

    /**
     * Core memory text (identity + preference + exclusion)
     * Always injected into system prompt
     */
    private String coreMemory;

    /**
     * Extended memory text (spending + lifestyle)
     * Injected based on user message keywords
     */
    private String extendedMemory;

    /**
     * Recent conversation summaries
     */
    private List<String> recentSummaries;

    /**
     * Structured facts grouped by category
     * Map<category, Map<key, value>>
     */
    private Map<String, Map<String, String>> structuredFacts;

    /**
     * Whether the user has any memory data
     */
    private boolean hasMemory;
}
