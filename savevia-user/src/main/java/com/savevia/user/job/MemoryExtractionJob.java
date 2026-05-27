package com.savevia.user.job;

import com.savevia.user.entity.ChatConversation;
import com.savevia.user.mapper.ChatConversationMapper;
import com.savevia.user.mapper.ChatMessageMapper;
import com.savevia.user.mapper.MemoryExtractionLogMapper;
import com.savevia.user.service.MemoryExtractionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Scheduled job for batch memory extraction from conversations.
 * Runs periodically to process conversations that haven't been analyzed yet.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class MemoryExtractionJob {

    private final MemoryExtractionService extractionService;
    private final ChatConversationMapper conversationMapper;
    private final ChatMessageMapper messageMapper;
    private final MemoryExtractionLogMapper extractionLogMapper;

    @Value("${memory.extraction.enabled:true}")
    private boolean enabled;

    @Value("${memory.extraction.batch-size:50}")
    private int batchSize;

    @Value("${memory.extraction.min-messages:4}")
    private int minMessages;

    @Value("${memory.extraction.idle-minutes:30}")
    private int idleMinutes;

    /**
     * Main extraction job - runs every hour.
     * Finds conversations that:
     * 1. Have not been processed yet
     * 2. Have been idle for at least 30 minutes
     * 3. Have at least 4 messages
     */
    @Scheduled(cron = "${memory.extraction.cron:0 0 * * * *}")
    public void processUnextractedConversations() {
        if (!enabled) {
            log.debug("Memory extraction is disabled");
            return;
        }

        log.info("Starting memory extraction job...");

        try {
            // Calculate cutoff time (conversations idle for at least N minutes)
            LocalDateTime cutoffTime = LocalDateTime.now().minusMinutes(idleMinutes);

            // Find unprocessed conversations
            List<ChatConversation> conversations = findUnprocessedConversations(cutoffTime);

            log.info("Found {} conversations to process", conversations.size());

            int processed = 0;
            int failed = 0;

            for (ChatConversation conversation : conversations) {
                try {
                    var result = extractionService.extractMemoryFromConversation(conversation.getId());
                    if (result != null) {
                        processed++;
                    } else {
                        failed++;
                    }
                } catch (Exception e) {
                    log.error("Error processing conversation {}: {}", conversation.getId(), e.getMessage());
                    failed++;
                }

                // Small delay between API calls to avoid rate limiting
                Thread.sleep(500);
            }

            log.info("Memory extraction job completed. Processed: {}, Failed: {}", processed, failed);

        } catch (Exception e) {
            log.error("Memory extraction job failed: {}", e.getMessage(), e);
        }
    }

    /**
     * Find conversations that need processing.
     * A conversation needs processing if:
     * - It's not in the extraction log (never processed)
     * - It was last updated before the cutoff time (idle)
     * - It has at least minMessages messages
     */
    private List<ChatConversation> findUnprocessedConversations(LocalDateTime cutoffTime) {
        // Get all conversations that are idle and have enough messages
        List<ChatConversation> candidates = conversationMapper.selectIdleConversations(cutoffTime, batchSize * 2);

        // Filter out already processed ones and those with too few messages
        return candidates.stream()
                .filter(conv -> {
                    // Check if already processed
                    if (extractionLogMapper.selectByConversationId(conv.getId()) != null) {
                        return false;
                    }
                    // Check message count
                    int messageCount = messageMapper.selectByConversationId(conv.getId()).size();
                    return messageCount >= minMessages;
                })
                .limit(batchSize)
                .toList();
    }

    /**
     * Manual trigger for processing a specific user's conversations.
     * Can be called from admin controller.
     */
    public int processUserConversations(Long userId) {
        if (!enabled) {
            log.warn("Memory extraction is disabled");
            return 0;
        }

        log.info("Processing conversations for user {}", userId);

        List<ChatConversation> conversations = conversationMapper.selectByUserId(userId, 100);
        int processed = 0;

        for (ChatConversation conversation : conversations) {
            // Skip if already processed
            if (extractionLogMapper.selectByConversationId(conversation.getId()) != null) {
                continue;
            }

            // Check message count
            int messageCount = messageMapper.selectByConversationId(conversation.getId()).size();
            if (messageCount < minMessages) {
                continue;
            }

            try {
                var result = extractionService.extractMemoryFromConversation(conversation.getId());
                if (result != null) {
                    processed++;
                }
            } catch (Exception e) {
                log.error("Error processing conversation {} for user {}: {}",
                        conversation.getId(), userId, e.getMessage());
            }
        }

        log.info("Processed {} conversations for user {}", processed, userId);
        return processed;
    }
}
