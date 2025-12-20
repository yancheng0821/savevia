-- Affiliate Links Configuration
-- 存储所有银行申卡联盟链接的配置（灵活可配）

CREATE TABLE IF NOT EXISTS affiliate_links (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    card_id BIGINT NOT NULL,
    bank_name VARCHAR(100) NOT NULL COMMENT '银行名称 (e.g., American Express, RBC, TD)',
    affiliate_type VARCHAR(50) NOT NULL COMMENT '联盟类型 (e.g., AMEX_AFFILIATE, RBC_AFFILIATE)',
    affiliate_url VARCHAR(500) NOT NULL COMMENT '申卡联盟链接',
    commission_amount DECIMAL(10,2) COMMENT '预估佣金金额(CAD)',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES credit_cards(id) ON DELETE CASCADE,
    UNIQUE KEY uk_card_affiliate_type (card_id, affiliate_type),
    INDEX idx_card_id (card_id),
    INDEX idx_bank_name (bank_name),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Affiliate Click Tracking
-- 仅用于追踪用户点击申卡链接的行为统计

CREATE TABLE IF NOT EXISTS affiliate_click_tracking (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    card_id BIGINT NOT NULL,
    affiliate_link_id BIGINT COMMENT '联盟链接ID，用于追踪哪个链接被点击',
    bank_name VARCHAR(50) NOT NULL COMMENT '银行名称',
    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (card_id) REFERENCES credit_cards(id) ON DELETE CASCADE,
    FOREIGN KEY (affiliate_link_id) REFERENCES affiliate_links(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_card_id (card_id),
    INDEX idx_affiliate_link_id (affiliate_link_id),
    INDEX idx_bank_name (bank_name),
    INDEX idx_clicked_at (clicked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
