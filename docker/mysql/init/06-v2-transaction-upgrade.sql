-- SaveVia V2: Transaction Analysis Upgrade
-- Extends existing tables for Flinks integration and cashback analysis

-- ============================================
-- 1. Bank Connections (Flinks Integration)
-- ============================================
CREATE TABLE IF NOT EXISTS bank_connections (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    flinks_login_id VARCHAR(255) NOT NULL COMMENT 'Flinks LoginId from Connect',
    institution_name VARCHAR(100) COMMENT 'Bank name (e.g., TD, RBC)',
    status ENUM('PENDING', 'CONNECTED', 'REFRESHING', 'ERROR', 'DISCONNECTED') DEFAULT 'PENDING',
    last_sync_at DATETIME NULL COMMENT 'Last successful data sync',
    error_message VARCHAR(500) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_user_login (user_id, flinks_login_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. Bank Accounts (linked via Flinks)
-- ============================================
CREATE TABLE IF NOT EXISTS bank_accounts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    connection_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    flinks_account_id VARCHAR(255) NOT NULL COMMENT 'Flinks Account ID',
    account_type VARCHAR(50) DEFAULT 'OTHER',
    account_name VARCHAR(100),
    account_number_masked VARCHAR(20) COMMENT 'Last 4 digits',
    institution_name VARCHAR(100),
    balance DECIMAL(15, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    linked_card_id BIGINT NULL COMMENT 'Linked credit card ID from cards table',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_connection_id (connection_id),
    INDEX idx_linked_card (linked_card_id),
    FOREIGN KEY (connection_id) REFERENCES bank_connections(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. Upgrade existing transactions table
-- ============================================
-- Add new columns for V2 (use stored procedure to handle if exists)
DROP PROCEDURE IF EXISTS add_transaction_columns;
DELIMITER //
CREATE PROCEDURE add_transaction_columns()
BEGIN
    -- account_id
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='account_id') THEN
        ALTER TABLE transactions ADD COLUMN account_id BIGINT NULL AFTER user_id;
    END IF;
    -- flinks_transaction_id
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='flinks_transaction_id') THEN
        ALTER TABLE transactions ADD COLUMN flinks_transaction_id VARCHAR(255) NULL AFTER account_id;
    END IF;
    -- description
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='description') THEN
        ALTER TABLE transactions ADD COLUMN description VARCHAR(500) NULL AFTER merchant;
    END IF;
    -- best_card_id
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='best_card_id') THEN
        ALTER TABLE transactions ADD COLUMN best_card_id BIGINT NULL AFTER card_used_id;
    END IF;
    -- actual_cashback
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='actual_cashback') THEN
        ALTER TABLE transactions ADD COLUMN actual_cashback DECIMAL(10, 4) DEFAULT 0;
    END IF;
    -- optimal_cashback
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='optimal_cashback') THEN
        ALTER TABLE transactions ADD COLUMN optimal_cashback DECIMAL(10, 4) DEFAULT 0;
    END IF;
    -- missed_cashback
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='missed_cashback') THEN
        ALTER TABLE transactions ADD COLUMN missed_cashback DECIMAL(10, 4) DEFAULT 0;
    END IF;
    -- is_analyzed
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='savevia' AND TABLE_NAME='transactions' AND COLUMN_NAME='is_analyzed') THEN
        ALTER TABLE transactions ADD COLUMN is_analyzed BOOLEAN DEFAULT FALSE;
    END IF;
END //
DELIMITER ;

CALL add_transaction_columns();
DROP PROCEDURE IF EXISTS add_transaction_columns;

-- Add indexes if not exist
CREATE INDEX idx_txn_account_id ON transactions(account_id);
CREATE INDEX idx_txn_category ON transactions(category);
CREATE INDEX idx_txn_analyzed ON transactions(is_analyzed);

-- ============================================
-- 4. Merchant Category Mapping
-- ============================================
CREATE TABLE IF NOT EXISTS merchant_categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    merchant_pattern VARCHAR(200) NOT NULL COMMENT 'Keyword pattern to match',
    category VARCHAR(50) NOT NULL,
    priority INT DEFAULT 0 COMMENT 'Higher = checked first',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_priority (priority DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. Missed Cashback Reports (cached)
-- ============================================
CREATE TABLE IF NOT EXISTS missed_cashback_reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    report_type VARCHAR(20) NOT NULL COMMENT '90days, monthly, yearly',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_transactions INT DEFAULT 0,
    total_spending DECIMAL(15, 2) DEFAULT 0,
    total_actual_cashback DECIMAL(10, 2) DEFAULT 0,
    total_optimal_cashback DECIMAL(10, 2) DEFAULT 0,
    total_missed_cashback DECIMAL(10, 2) DEFAULT 0,
    category_breakdown JSON,
    top_recommendations JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    UNIQUE KEY uk_user_report (user_id, report_type, start_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 6. Seed Merchant Category Mappings
-- ============================================
INSERT IGNORE INTO merchant_categories (merchant_pattern, category, priority) VALUES
-- Dining (highest priority)
('UBER EATS', 'DINING', 100),
('DOORDASH', 'DINING', 100),
('SKIP THE DISHES', 'DINING', 100),
('SKIPTHEDISHES', 'DINING', 100),
('MCDONALD', 'DINING', 95),
('TIM HORTONS', 'DINING', 95),
('TIMS', 'DINING', 95),
('STARBUCKS', 'DINING', 95),
('SUBWAY', 'DINING', 90),
('BOSTON PIZZA', 'DINING', 90),
('EARLS', 'DINING', 90),
('CACTUS CLUB', 'DINING', 90),
('JOEYS', 'DINING', 90),
('A&W', 'DINING', 90),
('WENDYS', 'DINING', 90),
('BURGER KING', 'DINING', 90),
('POPEYES', 'DINING', 90),
('KFC', 'DINING', 90),
('PIZZA HUT', 'DINING', 90),
('DOMINOS', 'DINING', 90),
('RESTAURANT', 'DINING', 50),
('CAFE', 'DINING', 50),
('PIZZA', 'DINING', 40),
('SUSHI', 'DINING', 40),
('GRILL', 'DINING', 40),

-- Grocery
('LOBLAWS', 'GROCERY', 100),
('SOBEYS', 'GROCERY', 100),
('METRO', 'GROCERY', 100),
('NO FRILLS', 'GROCERY', 100),
('NOFRILLS', 'GROCERY', 100),
('FOOD BASICS', 'GROCERY', 100),
('FRESHCO', 'GROCERY', 100),
('SAFEWAY', 'GROCERY', 100),
('SUPERSTORE', 'GROCERY', 100),
('REAL CANADIAN', 'GROCERY', 100),
('WALMART', 'GROCERY', 90),
('COSTCO WHOLESALE', 'GROCERY', 100),
('T&T', 'GROCERY', 100),
('WHOLE FOODS', 'GROCERY', 100),
('FARM BOY', 'GROCERY', 100),
('IGA', 'GROCERY', 100),
('SAVE-ON-FOODS', 'GROCERY', 100),
('LONGOS', 'GROCERY', 100),
('FORTINOS', 'GROCERY', 100),
('ZEHRS', 'GROCERY', 100),
('VALU-MART', 'GROCERY', 100),
('YOUR INDEPENDENT', 'GROCERY', 100),

-- Gas
('PETRO-CANADA', 'GAS', 100),
('PETRO CANADA', 'GAS', 100),
('SHELL', 'GAS', 100),
('ESSO', 'GAS', 100),
('MOBIL', 'GAS', 100),
('HUSKY', 'GAS', 100),
('PIONEER', 'GAS', 100),
('ULTRAMAR', 'GAS', 100),
('CANADIAN TIRE GAS', 'GAS', 100),
('COSTCO GAS', 'GAS', 100),
('CO-OP GAS', 'GAS', 100),
('CHEVRON', 'GAS', 100),
('7-ELEVEN GAS', 'GAS', 100),
('CIRCLE K', 'GAS', 90),
('ON THE RUN', 'GAS', 90),

-- Transit
('TTC', 'TRANSIT', 100),
('PRESTO', 'TRANSIT', 100),
('TRANSLINK', 'TRANSIT', 100),
('OC TRANSPO', 'TRANSIT', 100),
('STM', 'TRANSIT', 100),
('GO TRANSIT', 'TRANSIT', 100),
('UP EXPRESS', 'TRANSIT', 100),
('UBER TRIP', 'TRANSIT', 95),
('LYFT', 'TRANSIT', 95),
('TAXI', 'TRANSIT', 80),
('CAB', 'TRANSIT', 70),

-- Travel
('AIR CANADA', 'TRAVEL', 100),
('WESTJET', 'TRAVEL', 100),
('PORTER', 'TRAVEL', 100),
('FLAIR', 'TRAVEL', 100),
('EXPEDIA', 'TRAVEL', 100),
('BOOKING.COM', 'TRAVEL', 100),
('HOTELS.COM', 'TRAVEL', 100),
('AIRBNB', 'TRAVEL', 100),
('VRBO', 'TRAVEL', 100),
('MARRIOTT', 'TRAVEL', 100),
('HILTON', 'TRAVEL', 100),
('HYATT', 'TRAVEL', 100),
('BEST WESTERN', 'TRAVEL', 100),
('HOLIDAY INN', 'TRAVEL', 100),
('HOTEL', 'TRAVEL', 70),
('AIRLINE', 'TRAVEL', 70),
('RESORT', 'TRAVEL', 70),

-- Streaming
('NETFLIX', 'STREAMING', 100),
('SPOTIFY', 'STREAMING', 100),
('DISNEY+', 'STREAMING', 100),
('DISNEY PLUS', 'STREAMING', 100),
('APPLE MUSIC', 'STREAMING', 100),
('APPLE TV', 'STREAMING', 100),
('AMAZON PRIME', 'STREAMING', 100),
('PRIME VIDEO', 'STREAMING', 100),
('CRAVE', 'STREAMING', 100),
('YOUTUBE PREMIUM', 'STREAMING', 100),
('HBO MAX', 'STREAMING', 100),
('PARAMOUNT+', 'STREAMING', 100),
('AUDIBLE', 'STREAMING', 90),

-- Pharmacy
('SHOPPERS DRUG', 'PHARMACY', 100),
('SHOPPERS', 'PHARMACY', 90),
('REXALL', 'PHARMACY', 100),
('LONDON DRUGS', 'PHARMACY', 100),
('PHARMASAVE', 'PHARMACY', 100),
('JEAN COUTU', 'PHARMACY', 100),
('GUARDIAN', 'PHARMACY', 90),
('IDA', 'PHARMACY', 90),

-- Online Shopping
('AMAZON.CA', 'ONLINE_SHOPPING', 100),
('AMAZON', 'ONLINE_SHOPPING', 95),
('EBAY', 'ONLINE_SHOPPING', 100),
('BEST BUY', 'ONLINE_SHOPPING', 90),
('APPLE.COM', 'ONLINE_SHOPPING', 100),
('ALIEXPRESS', 'ONLINE_SHOPPING', 100),
('SHEIN', 'ONLINE_SHOPPING', 100),
('WAYFAIR', 'ONLINE_SHOPPING', 100),
('INDIGO', 'ONLINE_SHOPPING', 90),
('ETSY', 'ONLINE_SHOPPING', 100),

-- Recurring Bills
('ROGERS WIRELESS', 'RECURRING', 100),
('ROGERS CABLE', 'RECURRING', 100),
('BELL CANADA', 'RECURRING', 100),
('BELL MOBILITY', 'RECURRING', 100),
('TELUS', 'RECURRING', 100),
('SHAW', 'RECURRING', 100),
('FIDO', 'RECURRING', 100),
('KOODO', 'RECURRING', 100),
('FREEDOM MOBILE', 'RECURRING', 100),
('VIRGIN MOBILE', 'RECURRING', 100),
('CHATR', 'RECURRING', 100),
('HYDRO', 'RECURRING', 90),
('ENBRIDGE', 'RECURRING', 90),
('FORTIS', 'RECURRING', 90),
('TORONTO HYDRO', 'RECURRING', 100),
('BC HYDRO', 'RECURRING', 100),
('INSURANCE', 'RECURRING', 70),
('GYM', 'RECURRING', 70),
('FITNESS', 'RECURRING', 70),
('GOODLIFE', 'RECURRING', 90),
('PLANET FITNESS', 'RECURRING', 90);
