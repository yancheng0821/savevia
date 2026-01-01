package com.savevia.user.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
@Builder
public class AdminStatsDTO {
    // User statistics
    private long totalUsers;
    private long activeUsers; // Users with events in last 30 days

    // Event statistics
    private Map<String, Long> eventCounts; // event_type -> count

    // Daily event trends (last 30 days)
    private List<DailyEventCount> dailyEvents;

    // Daily active users trend (last 30 days)
    private List<DailyActiveCount> dailyActiveUsers;

    // Time range
    private String statsFrom; // ISO date
    private String statsTo;   // ISO date

    @Data
    @Builder
    public static class DailyEventCount {
        private String date;      // YYYY-MM-DD
        private String eventType;
        private long count;
    }

    @Data
    @Builder
    public static class DailyActiveCount {
        private String date;      // YYYY-MM-DD
        private long count;
    }
}
