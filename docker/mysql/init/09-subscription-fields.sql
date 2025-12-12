-- Add subscription fields to users table

-- subscription_type: FREE (default), PRO
-- subscription_expires_at: when the subscription expires (NULL for free users)
-- subscription_platform: ios, android, web (where the subscription was purchased)
-- subscription_product_id: the product ID from App Store / Google Play

ALTER TABLE users
ADD COLUMN subscription_type VARCHAR(20) DEFAULT 'FREE' COMMENT 'FREE or PRO',
ADD COLUMN subscription_expires_at DATETIME DEFAULT NULL COMMENT 'When subscription expires',
ADD COLUMN subscription_platform VARCHAR(20) DEFAULT NULL COMMENT 'ios, android, web',
ADD COLUMN subscription_product_id VARCHAR(100) DEFAULT NULL COMMENT 'Product ID from store';

-- Update ai_usage monthly_limit based on subscription
-- FREE users: 3 per month
-- PRO users: unlimited (we'll check subscription_type instead of monthly_limit)

-- Set default monthly_limit to 3 for free users
UPDATE ai_usage SET monthly_limit = 3 WHERE monthly_limit = 100;

-- Add index for subscription queries
ALTER TABLE users ADD INDEX idx_subscription_type (subscription_type);
