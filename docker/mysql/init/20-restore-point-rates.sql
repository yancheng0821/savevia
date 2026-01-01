-- ============================================
-- 前端上线后执行：将 POINTS 卡的 reward_rate 改为等效返现格式
-- ============================================
--
-- 背景说明：
-- - 旧格式: reward_rate = multiplier / 100 (例如 5x -> 0.05)
-- - 新格式: reward_rate = multiplier * point_value (例如 5x * 0.018 = 0.09，即 9% 等效返现)
--
-- 前端更新内容：
-- - CardDetailPage.tsx: formatRewardRate 函数已更新，会用 rate / pointValue 计算显示倍数
-- - ResultPage.tsx: 同上
-- - SharedResultPage.tsx: 同上
--
-- 执行时机：前端部署后立即执行
-- ============================================

-- 0. 修正积分价值 (必须在转换之前执行)

-- CIBC Adapta Mastercard: 12,000 积分 = $100 → 0.83¢
UPDATE credit_cards SET point_value = 0.0083
WHERE bank = 'CIBC' AND name = 'Adapta Mastercard';

-- RBC Avion Visa Infinite: 100 积分 = $1 → 1.0¢
UPDATE credit_cards SET point_value = 0.010
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite';

-- RBC Avion Visa Infinite Privilege: 100 积分 = $1.50 → 1.5¢
UPDATE credit_cards SET point_value = 0.015
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege';

-- RBC ION Visa: 172 积分 = $1 → 0.7¢ (受限兑换选项)
UPDATE credit_cards SET point_value = 0.007
WHERE bank = 'RBC' AND name = 'ION Visa';

-- RBC ION+ Visa: 172 积分 = $1 → 0.7¢ (受限兑换选项)
UPDATE credit_cards SET point_value = 0.007
WHERE bank = 'RBC' AND name = 'ION+ Visa';

-- Vancity enviro Visa Classic: 100 积分 = $1 → 1.0¢
UPDATE credit_cards SET point_value = 0.010
WHERE bank = 'Vancity' AND name = 'enviro Visa Classic';

-- 1. 更新 reward_rules 表
UPDATE reward_rules r
JOIN credit_cards c ON r.card_id = c.id
SET r.reward_rate = r.reward_rate * 100 * c.point_value
WHERE c.reward_type = 'POINTS' AND c.point_value > 0;

-- 2. 更新 credit_cards 的 base_reward_rate
UPDATE credit_cards
SET base_reward_rate = base_reward_rate * 100 * point_value
WHERE reward_type = 'POINTS' AND point_value > 0;

-- 3. 更新 amex_travel_bonus_rate (Amex Travel Online 额外积分)
UPDATE credit_cards
SET amex_travel_bonus_rate = amex_travel_bonus_rate * 100 * point_value
WHERE amex_travel_bonus_rate IS NOT NULL
  AND amex_travel_bonus_rate > 0
  AND point_value > 0;

-- 验证结果
SELECT c.name, c.point_value, c.base_reward_rate,
       r.category, r.reward_rate,
       r.reward_rate / c.point_value AS 'displays_as_multiplier'
FROM credit_cards c
JOIN reward_rules r ON c.id = r.card_id
WHERE c.name LIKE '%Cobalt%'
LIMIT 5;

-- 验证 Amex Travel 额外积分
SELECT name, point_value, amex_travel_bonus_rate,
       amex_travel_bonus_rate / point_value AS 'displays_as'
FROM credit_cards
WHERE amex_travel_bonus_rate IS NOT NULL AND amex_travel_bonus_rate > 0;

