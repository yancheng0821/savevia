package com.savevia.user.dto;

import lombok.Data;

@Data
public class TrackEventRequest {
    private String eventType;
    private String sessionId; // Optional, for anonymous tracking
}
