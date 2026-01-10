-- Push Notification System Tables
-- Created: 2026-01-08

-- User device tokens for push notifications
CREATE TABLE IF NOT EXISTS user_devices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    device_token VARCHAR(500) NOT NULL,
    platform VARCHAR(20) NOT NULL,          -- 'ios', 'android', 'web'
    device_name VARCHAR(100),               -- e.g., 'iPhone 15 Pro'
    app_version VARCHAR(20),
    os_version VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_device_token (device_token),
    INDEX idx_user_active (user_id, is_active),
    INDEX idx_platform (platform)
);

-- User insights extracted from chat/behavior/transactions
CREATE TABLE IF NOT EXISTS user_insights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    insight_type VARCHAR(50) NOT NULL,      -- 'spending_pattern', 'upcoming_event', 'preference'
    insight_key VARCHAR(100),               -- 'grocery_day', 'travel_plan', 'favorite_category'
    insight_value JSON,                     -- {"day": "saturday", "time": "10:00-12:00"}
    confidence DECIMAL(3,2),                -- 0.00-1.00
    source VARCHAR(50),                     -- 'chat', 'transaction', 'behavior'
    expires_at DATETIME,                    -- For temporary events
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_type (user_id, insight_type),
    INDEX idx_expires (expires_at)
);

-- Push notification records
CREATE TABLE IF NOT EXISTS push_notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- 'spending_reminder', 'travel_alert', 'promo_expiry', 'missed_reward'
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    data JSON,                              -- Additional payload data
    locale VARCHAR(10) DEFAULT 'en',        -- Message language
    scheduled_at DATETIME,
    sent_at DATETIME,
    read_at DATETIME,                       -- When user opened the notification
    status VARCHAR(20) DEFAULT 'pending',   -- 'pending', 'sent', 'failed', 'cancelled', 'read'
    error_message VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_status (user_id, status),
    INDEX idx_scheduled (scheduled_at, status),
    INDEX idx_type (notification_type)
);

-- Push notification templates (for different languages)
CREATE TABLE IF NOT EXISTS push_templates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    template_key VARCHAR(50) NOT NULL,      -- 'grocery_reminder', 'travel_reminder', etc.
    locale VARCHAR(10) NOT NULL DEFAULT 'en',
    title_template VARCHAR(200) NOT NULL,   -- "Time for {{category}} shopping!"
    body_template TEXT NOT NULL,            -- "Use {{card_name}} for {{reward_rate}}% back"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_template_locale (template_key, locale)
);

-- Insert default templates
INSERT INTO push_templates (template_key, locale, title_template, body_template) VALUES
-- English templates
('grocery_reminder', 'en', 'Grocery shopping today?', 'Use {{card_name}} for {{reward_rate}}% cashback at supermarkets!'),
('travel_reminder', 'en', 'Travel coming up!', 'Remember to bring {{card_name}} - no foreign transaction fees!'),
('dining_reminder', 'en', 'Dining out tonight?', 'Use {{card_name}} for {{reward_rate}}x points on restaurants!'),
('gas_reminder', 'en', 'Time to fill up?', 'Get {{reward_rate}}% back on gas with {{card_name}}!'),
('missed_reward', 'en', 'You could have saved more!', 'Last week you missed ${{amount}} in rewards. Here are some tips...'),
('weekly_summary', 'en', 'Your Weekly Savings', 'You saved ${{amount}} this week! Keep it up!'),

-- Chinese templates
('grocery_reminder', 'zh', '今天买菜吗？', '使用 {{card_name}} 超市返现 {{reward_rate}}%！'),
('travel_reminder', 'zh', '旅行即将开始！', '记得带上 {{card_name}} - 无外汇手续费！'),
('dining_reminder', 'zh', '今晚外出就餐？', '使用 {{card_name}} 餐饮消费获得 {{reward_rate}}x 积分！'),
('gas_reminder', 'zh', '该加油了？', '使用 {{card_name}} 加油返现 {{reward_rate}}%！'),
('missed_reward', 'zh', '你本可以省更多！', '上周你错过了 ${{amount}} 的返现。来看看这些建议...'),
('weekly_summary', 'zh', '本周省钱报告', '本周你省了 ${{amount}}！继续保持！'),

-- French templates
('grocery_reminder', 'fr', 'Courses aujourd''hui?', 'Utilisez {{card_name}} pour {{reward_rate}}% de remise!'),
('travel_reminder', 'fr', 'Voyage bientôt!', 'N''oubliez pas {{card_name}} - sans frais de change!'),

-- Japanese templates
('grocery_reminder', 'ja', '今日は買い物？', '{{card_name}}でスーパーで{{reward_rate}}%還元！'),
('travel_reminder', 'ja', '旅行が近づいています！', '{{card_name}}を忘れずに - 海外手数料無料！'),

-- Korean templates
('grocery_reminder', 'ko', '오늘 장보기?', '{{card_name}}으로 마트에서 {{reward_rate}}% 캐시백!'),
('travel_reminder', 'ko', '여행이 다가옵니다!', '{{card_name}}을 챙기세요 - 해외 수수료 무료!');
