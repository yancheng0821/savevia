-- ============================================
-- 修正积分卡 point_value 和 reward_rate (幂等版本)
-- 数据来源:
--   - Prince of Travel (2025年7月2日)
--   - Milesopedia (2025年1月1日)
--   - Ratehub.ca (2025年)
--
-- 注意：此脚本可以安全地重复执行
-- ============================================

-- ============================================
-- 1. 更新所有积分项目的 point_value
-- ============================================

-- Aeroplan: 1.8¢/点
UPDATE credit_cards SET point_value = 0.0180 WHERE point_program = 'Aeroplan';

-- Membership Rewards: 1.8¢/点
UPDATE credit_cards SET point_value = 0.0180 WHERE point_program = 'Membership Rewards';

-- RBC Avion: 1.6¢/点
UPDATE credit_cards SET point_value = 0.0160 WHERE point_program IN ('RBC Rewards', 'RBC Avion', 'Avion', 'RBC Avion Rewards');

-- TD Rewards: 0.5¢/点
UPDATE credit_cards SET point_value = 0.0050 WHERE point_program = 'TD Rewards';

-- PC Optimum: 0.1¢/点
UPDATE credit_cards SET point_value = 0.0010 WHERE point_program = 'PC Optimum';

-- AIR MILES: 10.5¢/mile
UPDATE credit_cards SET point_value = 0.1050 WHERE point_program = 'AIR MILES';

-- BMO Rewards: 0.67¢/点 (已正确，确认一下)
UPDATE credit_cards SET point_value = 0.0067 WHERE point_program = 'BMO Rewards';

-- Scene+: 1.0¢/点 (已正确，确认一下)
UPDATE credit_cards SET point_value = 0.0100 WHERE point_program = 'Scene+';

-- Aventura: 1.0¢/点 (已正确，确认一下)
UPDATE credit_cards SET point_value = 0.0100 WHERE point_program = 'Aventura';

-- Marriott Bonvoy: 0.8¢/点 (已正确，确认一下)
UPDATE credit_cards SET point_value = 0.0080 WHERE point_program = 'Marriott Bonvoy';


-- ============================================
-- 2. 使用绝对值更新 credit_cards.base_reward_rate
-- 公式: base_reward_rate = base_multiplier × point_value
-- ============================================

-- Aeroplan 卡片
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Aeroplan Card';                        -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0225 WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card';               -- 1.25x × 1.8¢ = 2.25%
UPDATE credit_cards SET base_reward_rate = 0.0225 WHERE bank = 'AMEX' AND name = 'Aeroplan Business Reserve Card';      -- 1.25x × 1.8¢ = 2.25%
UPDATE credit_cards SET base_reward_rate = 0.0121 WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card';                  -- 0.67x × 1.8¢ = 1.21% (1pt/$1.50)
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite';              -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite';                -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0225 WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege';      -- 1.25x × 1.8¢ = 2.25%

-- Membership Rewards 卡片
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Cobalt Card';                         -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Gold Rewards Card';                   -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Platinum Card';                       -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Green Card';                          -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0180 WHERE bank = 'AMEX' AND name = 'Business Gold Rewards Card';          -- 1x × 1.8¢ = 1.80%
UPDATE credit_cards SET base_reward_rate = 0.0225 WHERE bank = 'AMEX' AND name = 'Business Platinum Card';              -- 1.25x × 1.8¢ = 2.25%

-- Marriott Bonvoy 卡片
UPDATE credit_cards SET base_reward_rate = 0.0160 WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Card';                -- 2x × 0.8¢ = 1.60%
UPDATE credit_cards SET base_reward_rate = 0.0160 WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Business Card';       -- 2x × 0.8¢ = 1.60%

-- RBC Avion 卡片
UPDATE credit_cards SET base_reward_rate = 0.0160 WHERE bank = 'RBC' AND name = 'Avion Visa Infinite';                  -- 1x × 1.6¢ = 1.60%
UPDATE credit_cards SET base_reward_rate = 0.0200 WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege';        -- 1.25x × 1.6¢ = 2.00%
UPDATE credit_cards SET base_reward_rate = 0.0160 WHERE bank = 'RBC' AND name = 'ION Visa';                             -- 1x × 1.6¢ = 1.60%
UPDATE credit_cards SET base_reward_rate = 0.0160 WHERE bank = 'RBC' AND name = 'ION+ Visa';                            -- 1x × 1.6¢ = 1.60%

-- TD Rewards 卡片
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'TD' AND name = 'First Class Visa Infinite';             -- 2x × 0.5¢ = 1.00%

-- PC Optimum 卡片
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard';     -- 10pts × 0.1¢ = 1.00%
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'PC Financial' AND name = 'World Mastercard';           -- 10pts × 0.1¢ = 1.00%

-- AIR MILES 卡片 (特殊: 1 mile/$12 × 10.5¢ = 0.875%)
UPDATE credit_cards SET base_reward_rate = 0.00875 WHERE point_program = 'AIR MILES';

-- BMO Rewards 卡片
UPDATE credit_cards SET base_reward_rate = 0.0067 WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard';       -- 1x × 0.67¢ = 0.67%
UPDATE credit_cards SET base_reward_rate = 0.0067 WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite';               -- 1x × 0.67¢ = 0.67%

-- Scene+ 卡片
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'Scotiabank' AND name = 'Gold American Express';        -- 1x × 1.0¢ = 1.00%
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';       -- 1x × 1.0¢ = 1.00%
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa';                  -- 1x × 1.0¢ = 1.00%

-- Aventura 卡片
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite';             -- 1x × 1.0¢ = 1.00%
UPDATE credit_cards SET base_reward_rate = 0.0125 WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege';   -- 1.25x × 1.0¢ = 1.25%

-- MBNA Rewards 卡片
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard';     -- 1x × 1.0¢ = 1.00%

-- National Bank à la carte
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'National Bank' AND name = 'World Elite Mastercard';   -- 1x × 1.0¢ = 1.00%

-- CIBC Adapta
UPDATE credit_cards SET base_reward_rate = 0.0067 WHERE bank = 'CIBC' AND name = 'Adapta Mastercard';                  -- 1x × 0.67¢ = 0.67%

-- Meridian Rewards
UPDATE credit_cards SET base_reward_rate = 0.0050 WHERE bank = 'Meridian' AND name = 'Visa Cash Back';                 -- 0.5x × 1.0¢ = 0.50%
UPDATE credit_cards SET base_reward_rate = 0.0100 WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back';        -- 1x × 1.0¢ = 1.00%

-- Vancity Rewards
UPDATE credit_cards SET base_reward_rate = 0.0050 WHERE bank = 'Vancity' AND name = 'enviro Visa Classic';             -- 1x × 0.5¢ = 0.50%
UPDATE credit_cards SET base_reward_rate = 0.0125 WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite';            -- 1.25x × 1.0¢ = 1.25%

-- WestJet Rewards
UPDATE credit_cards SET base_reward_rate = 0.0150 WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard';      -- 1.5x × 1.0¢ = 1.50%


-- ============================================
-- 3. 使用绝对值更新 reward_rules.reward_rate
-- 公式: reward_rate = category_multiplier × point_value
-- ============================================

-- ----- Aeroplan 规则 -----

-- AMEX Aeroplan Card
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Card') AND category = 'DINING';       -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Card') AND category = 'TRAVEL';       -- 2x × 1.8¢

-- AMEX Aeroplan Reserve Card
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card') AND category = 'DINING';   -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0540 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card') AND category = 'TRAVEL';   -- 3x × 1.8¢

-- AMEX Aeroplan Business Reserve Card
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Business Reserve Card') AND category = 'TRAVEL'; -- 2x avg

-- CIBC Aeroplan Visa Card
UPDATE reward_rules SET reward_rate = 0.0180 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card') AND category = 'EV_CHARGING';  -- 1x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0180 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card') AND category = 'GAS';          -- 1x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0180 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card') AND category = 'GROCERY';      -- 1x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0180 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card') AND category = 'TRAVEL';       -- 1x × 1.8¢

-- CIBC Aeroplan Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite') AND category = 'GAS';      -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite') AND category = 'GROCERY';  -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite') AND category = 'TRAVEL';   -- 1.5x × 1.8¢

-- TD Aeroplan Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite') AND category = 'EV_CHARGING';  -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite') AND category = 'GAS';          -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite') AND category = 'GROCERY';      -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite') AND category = 'TRAVEL';       -- 1.5x × 1.8¢

-- TD Aeroplan Visa Infinite Privilege
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'DINING';       -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'EV_CHARGING';  -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'GAS';          -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'GROCERY';      -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0270 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'TRANSIT';      -- 1.5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'TRAVEL';       -- 2x × 1.8¢


-- ----- Membership Rewards 规则 -----

-- AMEX Cobalt Card
UPDATE reward_rules SET reward_rate = 0.0900 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card') AND category = 'DINING';       -- 5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card') AND category = 'GAS';          -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0900 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card') AND category = 'GROCERY';      -- 5x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0540 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card') AND category = 'STREAMING';    -- 3x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card') AND category = 'TRANSIT';      -- 2x × 1.8¢

-- AMEX Gold Rewards Card
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card') AND category = 'GAS';        -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card') AND category = 'GROCERY';    -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card') AND category = 'PHARMACY';   -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card') AND category = 'TRAVEL';     -- 2x × 1.8¢

-- AMEX Platinum Card
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card') AND category = 'DINING';     -- 2x × 1.8¢
UPDATE reward_rules SET reward_rate = 0.0360 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card') AND category = 'TRAVEL';     -- 2x × 1.8¢


-- ----- RBC Avion 规则 -----

-- RBC Avion Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Infinite') AND category = 'TRAVEL';   -- 1.25x × 1.6¢

-- RBC Avion Visa Infinite Privilege
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege') AND category = 'DINING';  -- 1.5x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0320 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege') AND category = 'TRAVEL';  -- 2x × 1.6¢

-- RBC ION Visa
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION Visa') AND category = 'DINING';       -- 1.5x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION Visa') AND category = 'GROCERY';      -- 1.5x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION Visa') AND category = 'RECURRING';    -- 1.5x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION Visa') AND category = 'TRANSIT';      -- 1.5x × 1.6¢

-- RBC ION+ Visa
UPDATE reward_rules SET reward_rate = 0.0480 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION+ Visa') AND category = 'DINING';      -- 3x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0480 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION+ Visa') AND category = 'GAS';         -- 3x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0480 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION+ Visa') AND category = 'GROCERY';     -- 3x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0480 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION+ Visa') AND category = 'STREAMING';   -- 3x × 1.6¢
UPDATE reward_rules SET reward_rate = 0.0480 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'ION+ Visa') AND category = 'TRANSIT';     -- 3x × 1.6¢


-- ----- TD Rewards 规则 -----

-- TD First Class Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'DINING';        -- 6x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'ENTERTAINMENT'; -- 4x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'GROCERY';       -- 6x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'RECURRING';     -- 4x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'STREAMING';     -- 4x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'TRANSIT';       -- 6x × 0.5¢
UPDATE reward_rules SET reward_rate = 0.0400 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'TRAVEL';        -- 8x × 0.5¢


-- ----- PC Optimum 规则 -----

-- PC Financial World Elite Mastercard
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard') AND category = 'GAS';       -- 30pts × 0.1¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard') AND category = 'GROCERY';   -- 30pts × 0.1¢
UPDATE reward_rules SET reward_rate = 0.0450 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard') AND category = 'PHARMACY';  -- 45pts × 0.1¢

-- PC Financial World Mastercard
UPDATE reward_rules SET reward_rate = 0.0250 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Mastercard') AND category = 'GAS';       -- 25pts × 0.1¢
UPDATE reward_rules SET reward_rate = 0.0250 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Mastercard') AND category = 'GROCERY';   -- 25pts × 0.1¢
UPDATE reward_rules SET reward_rate = 0.0350 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Mastercard') AND category = 'PHARMACY';  -- 35pts × 0.1¢


-- ----- AIR MILES 规则 (特殊: per $12) -----

-- BMO Air Miles World Elite Mastercard
UPDATE reward_rules rr
JOIN credit_cards cc ON rr.card_id = cc.id
SET rr.reward_rate = 0.0175     -- 2mi/$12 × 10.5¢ = 1.75%
WHERE cc.point_program = 'AIR MILES' AND rr.category = 'GROCERY';

UPDATE reward_rules rr
JOIN credit_cards cc ON rr.card_id = cc.id
SET rr.reward_rate = 0.02625    -- 3mi/$12 × 10.5¢ = 2.625%
WHERE cc.point_program = 'AIR MILES' AND rr.category = 'GAS';

UPDATE reward_rules rr
JOIN credit_cards cc ON rr.card_id = cc.id
SET rr.reward_rate = 0.0175     -- 2mi/$12 × 10.5¢ = 1.75%
WHERE cc.point_program = 'AIR MILES' AND rr.category = 'LIQUOR';


-- ----- BMO Rewards 规则 -----

-- BMO Ascend World Elite Mastercard
UPDATE reward_rules SET reward_rate = 0.0201 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard') AND category = 'DINING';        -- 3x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0201 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard') AND category = 'ENTERTAINMENT'; -- 3x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0201 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard') AND category = 'RECURRING';     -- 3x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0335 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard') AND category = 'TRAVEL';        -- 5x × 0.67¢

-- BMO Eclipse Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0335 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite') AND category = 'DINING';   -- 5x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0335 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite') AND category = 'GAS';      -- 5x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0335 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite') AND category = 'GROCERY';  -- 5x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0335 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite') AND category = 'TRANSIT';  -- 5x × 0.67¢


-- ----- Marriott Bonvoy 规则 -----

-- AMEX Marriott Bonvoy Card
UPDATE reward_rules SET reward_rate = 0.0400 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Card') AND category = 'TRAVEL';   -- 5x × 0.8¢

-- AMEX Marriott Bonvoy Business Card
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Business Card') AND category = 'DINING';  -- 3x × 0.8¢
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Business Card') AND category = 'GAS';     -- 3x × 0.8¢
UPDATE reward_rules SET reward_rate = 0.0240 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Marriott Bonvoy Business Card') AND category = 'TRAVEL';  -- 3x × 0.8¢


-- ----- Scene+ 规则 -----

-- Scotiabank Gold American Express
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'DINING';        -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'ENTERTAINMENT'; -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'FOREIGN';       -- 1x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'GAS';           -- 3x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'GROCERY';       -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'STREAMING';     -- 3x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'TRANSIT';       -- 3x × 1.0¢

-- Scotiabank Passport Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'DINING';        -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'ENTERTAINMENT'; -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'FOREIGN';       -- 1x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'GROCERY';       -- 3x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'TRANSIT';       -- 2x × 1.0¢

-- Scotiabank Scene+ Visa
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'ENTERTAINMENT';     -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'GROCERY';           -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'HOME_IMPROVEMENT';  -- 2x × 1.0¢


-- ----- Aventura 规则 -----

-- CIBC Aventura Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0150 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite') AND category = 'EV_CHARGING';  -- 1.5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0150 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite') AND category = 'GAS';          -- 1.5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0150 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite') AND category = 'GROCERY';      -- 1.5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0150 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite') AND category = 'PHARMACY';     -- 1.5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite') AND category = 'TRAVEL';       -- 2x × 1.0¢

-- CIBC Aventura Visa Infinite Privilege
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'DINING';        -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'ENTERTAINMENT'; -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'EV_CHARGING';   -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'GAS';           -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'GROCERY';       -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'PHARMACY';      -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0300 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege') AND category = 'TRAVEL';        -- 3x × 1.0¢


-- ----- MBNA Rewards 规则 -----

-- MBNA Rewards World Elite Mastercard
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard') AND category = 'DINING';     -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard') AND category = 'GROCERY';    -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard') AND category = 'RECURRING';  -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard') AND category = 'STREAMING';  -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard') AND category = 'TELECOM';    -- 5x × 1.0¢


-- ----- National Bank à la carte 规则 -----

-- National Bank World Elite Mastercard
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'DINING';     -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'GAS';        -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'GROCERY';    -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'RECURRING';  -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'TRAVEL';     -- 2x × 1.0¢


-- ----- CIBC Adapta 规则 -----

-- CIBC Adapta Mastercard
UPDATE reward_rules SET reward_rate = 0.0101 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Adapta Mastercard') AND category = 'OTHER';    -- 1.5x × 0.67¢
UPDATE reward_rules SET reward_rate = 0.0134 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Adapta Mastercard') AND category = 'TRAVEL';   -- 2x × 0.67¢


-- ----- Meridian Rewards 规则 -----

-- Meridian Visa Cash Back
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'GAS';        -- 1x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'GROCERY';    -- 1x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'PHARMACY';   -- 1x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'RECURRING';  -- 1x × 1.0¢

-- Meridian Visa Infinite Cash Back
UPDATE reward_rules SET reward_rate = 0.0400 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back') AND category = 'GAS';        -- 4x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0400 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back') AND category = 'GROCERY';    -- 4x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back') AND category = 'PHARMACY';   -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back') AND category = 'RECURRING';  -- 2x × 1.0¢


-- ----- Vancity Rewards 规则 -----

-- Vancity enviro Visa Classic
UPDATE reward_rules SET reward_rate = 0.0100 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Classic') AND category = 'TRAVEL';   -- 2x × 0.5¢

-- Vancity enviro Visa Infinite
UPDATE reward_rules SET reward_rate = 0.0250 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'GROCERY';         -- 2.5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.1000 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'LOCAL_BUSINESS';  -- 10x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0500 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'TRANSIT';         -- 5x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0250 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'TRAVEL';          -- 2.5x × 1.0¢


-- ----- WestJet Rewards 规则 -----

-- RBC WestJet World Elite Mastercard
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'DINING';        -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'ENTERTAINMENT'; -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'EV_CHARGING';   -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'GAS';           -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'GROCERY';       -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'STREAMING';     -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'TRANSIT';       -- 2x × 1.0¢
UPDATE reward_rules SET reward_rate = 0.0200 WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'TRAVEL';        -- 2x × 1.0¢


-- ============================================
-- 4. 验证查询
-- ============================================

-- 验证 point_value 按项目分组
SELECT
    point_program,
    point_value,
    COUNT(*) as card_count,
    CONCAT(ROUND(point_value * 100, 2), '¢/点') AS value_display
FROM credit_cards
WHERE reward_type = 'POINTS'
GROUP BY point_program, point_value
ORDER BY point_program;

-- 验证 credit_cards base_reward_rate
SELECT
    bank,
    name,
    point_program,
    point_value,
    base_reward_rate,
    CONCAT(ROUND(base_reward_rate * 100, 2), '%') AS equivalent_cashback,
    ROUND(base_reward_rate / point_value, 2) AS implied_multiplier
FROM credit_cards
WHERE reward_type = 'POINTS'
ORDER BY point_program, bank, name;
