-- Saved Results Table
-- Stores optimization results for sharing and user persistence

CREATE TABLE IF NOT EXISTS saved_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    share_id VARCHAR(32) NULL UNIQUE,
    user_id BIGINT NULL,
    result_json TEXT NOT NULL,
    net_annual_savings DECIMAL(10, 2) DEFAULT 0,
    annual_reward DECIMAL(10, 2) DEFAULT 0,
    total_annual_fees DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    INDEX idx_share_id (share_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
