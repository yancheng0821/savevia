-- Card Usage Tips - 卡片使用指南
-- 用于存储如何最大化使用信用卡的建议，支持多语言

-- 扩展 credit_cards 表，添加积分相关字段
ALTER TABLE credit_cards
    ADD COLUMN reward_type VARCHAR(20) DEFAULT 'CASHBACK' COMMENT 'CASHBACK, POINTS, MILES',
    ADD COLUMN point_value DECIMAL(5,4) COMMENT '每分价值，如 0.015 = 1.5 cents',
    ADD COLUMN point_program VARCHAR(100) COMMENT '积分项目名称，如 Aeroplan, Scene+',
    ADD COLUMN transfer_partners_json JSON COMMENT '转换伙伴列表';

-- 创建 card_usage_tips 表
CREATE TABLE IF NOT EXISTS card_usage_tips (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    card_id BIGINT NOT NULL,
    tip_type VARCHAR(50) NOT NULL COMMENT 'BEST_USE, REDEMPTION, TRANSFER_PARTNER, STACKING, AVOID',

    -- 多语言标题 (JSON)
    title_json JSON NOT NULL COMMENT '{"en": "...", "zh": "...", "fr": "...", "es": "...", "ja": "...", "ko": "..."}',

    -- 多语言内容 (JSON)
    content_json JSON NOT NULL COMMENT '{"en": "...", "zh": "...", ...}',

    -- 元数据
    icon VARCHAR(50) COMMENT '图标标识',
    priority INT DEFAULT 0 COMMENT '排序优先级，数字越小越靠前',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (card_id) REFERENCES credit_cards(id) ON DELETE CASCADE,
    INDEX idx_card_id (card_id),
    INDEX idx_tip_type (tip_type),
    INDEX idx_priority (priority),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
