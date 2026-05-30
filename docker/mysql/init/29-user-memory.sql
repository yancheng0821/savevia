-- User Long-term Memory Tables
-- Migration: 29-user-memory.sql

-- 1. User profile facts (structured memory)
CREATE TABLE IF NOT EXISTS user_profile_facts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    fact_category VARCHAR(50) NOT NULL COMMENT 'identity|spending|preference|exclusion|lifestyle',
    fact_key VARCHAR(100) NOT NULL,
    fact_value TEXT NOT NULL,
    source VARCHAR(20) DEFAULT 'inferred' COMMENT 'explicit|inferred',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_fact (user_id, fact_category, fact_key),
    INDEX idx_user_id (user_id),
    INDEX idx_category (fact_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Conversation summaries (unstructured memory)
CREATE TABLE IF NOT EXISTS user_conversation_summaries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    summary TEXT NOT NULL,
    key_topics JSON COMMENT '["grocery", "travel"]',
    recommendations JSON COMMENT '[{"cardId":1,"accepted":true}]',
    source_conversation_ids JSON NOT NULL COMMENT '[101, 102]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Memory extraction tracking
CREATE TABLE IF NOT EXISTS memory_extraction_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    conversation_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending|processed|failed',
    processed_at TIMESTAMP NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_conversation (conversation_id),
    INDEX idx_status (status),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
