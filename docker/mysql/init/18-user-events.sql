-- User events tracking table for admin statistics
CREATE TABLE IF NOT EXISTS user_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL COMMENT 'Event type: quick_card_finder, card_detail_view, result_view',
    user_id BIGINT COMMENT 'User ID (null for anonymous)',
    session_id VARCHAR(100) COMMENT 'Session identifier for anonymous tracking',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_event_type (event_type),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_event_created (event_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User behavior events for analytics';
