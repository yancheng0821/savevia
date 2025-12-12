-- SaveVia: Bank Connection Limits
-- Track monthly bank connection usage to prevent API cost abuse

-- ============================================
-- 1. User Connection Limits Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_connection_limits (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    `year_month` VARCHAR(7) NOT NULL COMMENT 'Format: YYYY-MM',
    connection_count INT DEFAULT 0 COMMENT 'Number of connections this month',
    max_connections INT DEFAULT 5 COMMENT 'Max allowed connections per month',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_month (user_id, `year_month`),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. Connection History Log (for audit)
-- ============================================
CREATE TABLE IF NOT EXISTS connection_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    institution_name VARCHAR(100) NOT NULL,
    action ENUM('CONNECT', 'DISCONNECT', 'REFRESH') NOT NULL,
    flinks_login_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
