-- Card Usage Tips Update
-- Generated: 2025-12-23 11:03:18
-- Total tips: 5

START TRANSACTION;

-- ============================================
-- USAGE TIPS
-- ============================================

-- BEST_USE tip for card 1
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    1,
    'BEST_USE',
    '{"en": "Dining and Food Delivery", "zh": "[ZH] Dining and Food Delivery", "fr": "[FR] Dining and Food Delivery", "es": "[ES] Dining and Food Delivery", "ja": "[JA] Dining and Food Delivery", "ko": "[KO] Dining and Food Delivery"}',
    '{"en": "Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.", "zh": "[ZH] Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.", "fr": "[FR] Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.", "es": "[ES] Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.", "ja": "[JA] Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.", "ko": "[KO] Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada."}',
    'dining',
    1,
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();

-- BEST_USE tip for card 1
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    1,
    'BEST_USE',
    '{"en": "Grocery Shopping", "zh": "[ZH] Grocery Shopping", "fr": "[FR] Grocery Shopping", "es": "[ES] Grocery Shopping", "ja": "[JA] Grocery Shopping", "ko": "[KO] Grocery Shopping"}',
    '{"en": "Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.", "zh": "[ZH] Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.", "fr": "[FR] Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.", "es": "[ES] Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.", "ja": "[JA] Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.", "ko": "[KO] Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro."}',
    'grocery',
    2,
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();

-- REDEMPTION tip for card 1
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    1,
    'REDEMPTION',
    '{"en": "Transfer to Aeroplan for Best Value", "zh": "[ZH] Transfer to Aeroplan for Best Value", "fr": "[FR] Transfer to Aeroplan for Best Value", "es": "[ES] Transfer to Aeroplan for Best Value", "ja": "[JA] Transfer to Aeroplan for Best Value", "ko": "[KO] Transfer to Aeroplan for Best Value"}',
    '{"en": "Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.", "zh": "[ZH] Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.", "fr": "[FR] Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.", "es": "[ES] Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.", "ja": "[JA] Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.", "ko": "[KO] Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners."}',
    'transfer',
    1,
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();

-- STACKING tip for card 1
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    1,
    'STACKING',
    '{"en": "Combine with Amex Offers", "zh": "[ZH] Combine with Amex Offers", "fr": "[FR] Combine with Amex Offers", "es": "[ES] Combine with Amex Offers", "ja": "[JA] Combine with Amex Offers", "ko": "[KO] Combine with Amex Offers"}',
    '{"en": "Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.", "zh": "[ZH] Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.", "fr": "[FR] Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.", "es": "[ES] Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.", "ja": "[JA] Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.", "ko": "[KO] Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants."}',
    'stack',
    1,
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();

-- AVOID tip for card 1
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    1,
    'AVOID',
    '{"en": "Foreign Transactions", "zh": "[ZH] Foreign Transactions", "fr": "[FR] Foreign Transactions", "es": "[ES] Foreign Transactions", "ja": "[JA] Foreign Transactions", "ko": "[KO] Foreign Transactions"}',
    '{"en": "Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.", "zh": "[ZH] Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.", "fr": "[FR] Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.", "es": "[ES] Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.", "ja": "[JA] Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.", "ko": "[KO] Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead."}',
    'warning',
    1,
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();

-- ============================================
-- CARD REWARD INFO UPDATES
-- ============================================

-- Update reward info for card 1
UPDATE credit_cards SET
    reward_type = 'POINTS',
    point_value = 0.0200,
    point_program = 'Membership Rewards',
    transfer_partners_json = '[{"partner": "Aeroplan", "ratio": "1:1", "type": "AIRLINE"}, {"partner": "Hilton Honors", "ratio": "1:2", "type": "HOTEL"}, {"partner": "Marriott Bonvoy", "ratio": "1:1.2", "type": "HOTEL"}]',
    updated_at = NOW()
WHERE id = 1;

COMMIT;

-- End of update