package com.savevia.optimizer.dto.chat;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {

    /**
     * User's message
     */
    private String message;

    /**
     * Conversation ID (null for new conversation)
     */
    private Long conversationId;

    /**
     * User's locale for AI response language
     */
    private String locale;
}
