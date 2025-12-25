-- Add CIBC Dividend Visa Card (no annual fee version)
-- Generated: 2025-12-25

-- ============================================
-- CIBC Dividend Visa Card
-- ============================================
-- The no-fee version of CIBC Dividend card
-- Different from CIBC Dividend Visa Infinite ($120/yr)

INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, is_active) VALUES
('CIBC', 'Dividend Visa Card', 'VISA', 0, 0.005, NULL,
'{"gradient": "linear-gradient(135deg, #8b1538 0%, #5c0f26 100%)", "textColor": "white"}',
'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/dividend-visa-card.html',
true);

-- Get the card ID for reward rules
SET @card_id = LAST_INSERT_ID();

-- Reward Rules for CIBC Dividend Visa Card
-- 2% on groceries, 1% on gas/EV/transit/dining/recurring/travel, 0.5% base
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@card_id, 'GROCERY', 0.02, NULL, '2% cash back on groceries'),
(@card_id, 'GAS', 0.01, NULL, '1% cash back on gas'),
(@card_id, 'EV_CHARGING', 0.01, NULL, '1% cash back on EV charging'),
(@card_id, 'TRANSIT', 0.01, NULL, '1% cash back on transportation'),
(@card_id, 'DINING', 0.01, NULL, '1% cash back on dining'),
(@card_id, 'RECURRING', 0.01, NULL, '1% cash back on recurring payments'),
(@card_id, 'TRAVEL', 0.01, NULL, '1% cash back on CIBC by Expedia travel'),
(@card_id, 'OTHER', 0.005, NULL, '0.5% cash back on everything else');

-- ============================================
-- Fix existing cards
-- ============================================

-- AMEX Cobalt Card: Update color to dark gray/black
UPDATE credit_cards SET image_url = '{"gradient": "linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)", "textColor": "white"}'
WHERE bank = 'AMEX' AND name = 'Cobalt Card';

-- AMEX Platinum Card: Fix apply URL and signup bonus
UPDATE credit_cards SET
    apply_url = 'https://www.americanexpress.com/en-ca/charge-cards/the-platinum-card/',
    signup_bonus_json = '{"bonusAmount": 100000, "minSpend": 10000, "daysToComplete": 90, "description": "70K points on $10K spend in 3 months + 30K points on purchase in months 15-17"}'
WHERE bank = 'AMEX' AND name = 'Platinum Card';

-- AMEX Platinum Card: Add missing OTHER reward rule (1x on everything else)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'OTHER', 0.01, NULL, '1x points on everything else'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card';

-- AMEX Platinum Card: Update TRAVEL description
UPDATE reward_rules SET description = '2x points on travel (flights, hotels, tours, etc.)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card') AND category = 'TRAVEL';

-- AMEX Platinum Card: Add Amex Travel Online bonus (3x total = 2x travel + 1x additional)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'ONLINE_SHOPPING', 0.03, NULL, '3x points on Amex Travel Online hotel/car rental (2x travel + 1x additional)'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card';

-- ============================================
-- CIBC Aeroplan Visa Card (no annual fee version)
-- ============================================
-- Different from CIBC Aeroplan Visa Infinite ($139/yr)

INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, is_active) VALUES
('CIBC', 'Aeroplan Visa Card', 'VISA', 0, 0.0067,
'{"bonusAmount": 10000, "minSpend": 0, "daysToComplete": 365, "description": "2.5K pts on first purchase + 2.5K pts on $1.5K spend in 4 months + 5K pts anniversary bonus on $10K spend in 12 months"}',
'{"gradient": "linear-gradient(135deg, #d4d4d4 0%, #9ca3af 100%)", "textColor": "#1a1a1a"}',
'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-card.html',
true);

SET @aeroplan_visa_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@aeroplan_visa_id, 'GAS', 0.01, NULL, '1 Aeroplan point per $1 on gas'),
(@aeroplan_visa_id, 'EV_CHARGING', 0.01, NULL, '1 Aeroplan point per $1 on EV charging'),
(@aeroplan_visa_id, 'GROCERY', 0.01, NULL, '1 Aeroplan point per $1 on groceries'),
(@aeroplan_visa_id, 'TRAVEL', 0.01, NULL, '1 Aeroplan point per $1 on Air Canada'),
(@aeroplan_visa_id, 'OTHER', 0.0067, NULL, '1 Aeroplan point per $1.50 on everything else');
