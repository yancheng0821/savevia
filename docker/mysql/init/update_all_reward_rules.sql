-- ============================================
-- SaveVia Credit Cards Reward Rules Update Script
-- ============================================
-- Description: Update reward rules (base rate, category rates) for all cards
-- Usage: Run this file to update reward rules in production
-- Last Updated: 2025-12-26
-- ============================================

START TRANSACTION;


-- ============================================
-- SECTION 2: AMEX AEROPLAN RESERVE CARD (id=7)
-- ============================================
-- Base: 1.25x Aeroplan points on everything else
-- TRAVEL: 3x on Air Canada & travel
-- DINING: 2x on dining
-- NO GROCERY category

UPDATE credit_cards
SET base_reward_rate = 0.0125
WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card';

-- Delete incorrect GROCERY rule
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card')
AND category = 'GROCERY';

-- Update TRAVEL rule
UPDATE reward_rules
SET reward_rate = 0.0300, description = '3x points on Air Canada & travel'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card')
AND category = 'TRAVEL';

-- Update DINING rule
UPDATE reward_rules
SET reward_rate = 0.0200, description = '2x points on dining'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card')
AND category = 'DINING';


-- ============================================
-- SECTION 3: AMEX COBALT CARD (id=1)
-- ============================================
-- Official rates:
-- DINING: 5x (up to $2,500/month)
-- GROCERY: 5x (up to $2,500/month)
-- STREAMING: 3x
-- GAS: 2x
-- TRANSIT: 2x
-- Base: 1x on everything else

-- Ensure base rate is correct
UPDATE credit_cards
SET base_reward_rate = 0.0100
WHERE bank = 'AMEX' AND name = 'Cobalt Card';

-- Delete incorrect rules (not in official card benefits)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Cobalt Card')
AND category IN ('PERSONAL_SERVICES', 'TRAVEL', 'ENTERTAINMENT', 'RETAIL', 'HOME_IMPROVEMENT');


-- ============================================
-- SECTION 4: AMEX GOLD REWARDS CARD (id=2)
-- ============================================
-- Official rates:
-- TRAVEL: 2x
-- GAS: 2x
-- GROCERY: 2x
-- PHARMACY: 2x (drugstores)
-- Base: 1x on everything else

-- Ensure base rate is correct
UPDATE credit_cards
SET base_reward_rate = 0.0100
WHERE bank = 'AMEX' AND name = 'Gold Rewards Card';

-- Add GROCERY rule (missing)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.02, NULL, '2x points on groceries'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2x points on groceries';

-- Add PHARMACY rule (missing)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'PHARMACY', 0.02, NULL, '2x points on drugstores'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'Gold Rewards Card'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2x points on drugstores';


-- ============================================
-- SECTION 5: AMEX PLATINUM CARD (id=3)
-- ============================================
-- Official rates:
-- TRAVEL: 2x
-- DINING: 2x
-- Base: 1x on everything else
-- +1x additional on Amex Travel Online (stored in amex_travel_bonus_rate)

-- Ensure base rate is correct
UPDATE credit_cards
SET base_reward_rate = 0.0100
WHERE bank = 'AMEX' AND name = 'Platinum Card';

-- Delete incorrect rules (ONLINE_SHOPPING and OTHER should not be separate rules)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Platinum Card')
AND category IN ('ONLINE_SHOPPING', 'OTHER');


-- ============================================
-- SECTION 6: AMEX SIMPLYCASH CARD (id=5)
-- ============================================
-- Official rates:
-- GAS: 2% (up to $15,000/year combined with grocery)
-- GROCERY: 2% (up to $15,000/year combined with gas)
-- Base: 1.25% on everything else

-- Ensure base rate is correct
UPDATE credit_cards
SET base_reward_rate = 0.0125
WHERE bank = 'AMEX' AND name = 'SimplyCash';

-- Add GAS rule
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.02, NULL, '2% on gas (up to $15,000/year combined)'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'SimplyCash'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% on gas (up to $15,000/year combined)';

-- Add GROCERY rule
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.02, NULL, '2% on groceries (up to $15,000/year combined)'
FROM credit_cards WHERE bank = 'AMEX' AND name = 'SimplyCash'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% on groceries (up to $15,000/year combined)';


-- ============================================
-- SECTION 7: AMEX SIMPLYCASH PREFERRED CARD (id=4)
-- ============================================
-- Official rates:
-- GAS: 4% (up to $30,000/year combined with grocery)
-- GROCERY: 4% (up to $30,000/year combined with gas)
-- Base: 2% on everything else
-- NOTE: EV charging does NOT qualify for 4% - only stand-alone gas stations

-- Ensure base rate is correct
UPDATE credit_cards
SET base_reward_rate = 0.0200
WHERE bank = 'AMEX' AND name = 'SimplyCash Preferred';

-- Delete incorrect rules (RETAIL, HOME_IMPROVEMENT, EV_CHARGING are not bonus categories)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'SimplyCash Preferred')
AND category IN ('RETAIL', 'HOME_IMPROVEMENT', 'EV_CHARGING');


-- ============================================
-- SECTION 8: BMO AIR MILES WORLD ELITE MASTERCARD (id=29)
-- ============================================
-- Official rates:
-- AIR MILES Partners (Shell, etc.): 3 miles per $12 (0.25 miles/$)
-- Grocery/Wholesale/Liquor: 2 miles per $12 (0.167 miles/$)
-- Everything else: 1 mile per $12 (0.083 miles/$)
-- Using multiplier representation: base=0.01, 2x=0.02, 3x=0.03

-- Ensure base rate is correct (1x = 1 mile per $12)
UPDATE credit_cards
SET base_reward_rate = 0.0100
WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard';

-- Delete incorrect TRANSIT rule (no transit bonus for this card)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard')
AND category = 'TRANSIT';

-- Fix GROCERY rule: should be 2x (not 3x)
UPDATE reward_rules
SET reward_rate = 0.0200, description = '2 miles per $12 at grocery stores & wholesale clubs'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard')
AND category = 'GROCERY';

-- Fix GAS rule: should be 3x at AIR MILES partners (Shell)
UPDATE reward_rules
SET reward_rate = 0.0300, description = '3 miles per $12 at AIR MILES partners (Shell, etc.)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard')
AND category = 'GAS';

-- Add LIQUOR category (same as grocery, 2x)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'LIQUOR', 0.02, NULL, '2 miles per $12 at liquor retailers'
FROM credit_cards WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2 miles per $12 at liquor retailers';


-- ============================================
-- SECTION 9: BMO CASHBACK WORLD ELITE MASTERCARD (id=28)
-- ============================================
-- Official rates:
-- GROCERY: 5% (up to $500/month)
-- TRANSIT: 4% (up to $300/month)
-- GAS: 3% (up to $300/month)
-- EV_CHARGING: 3% (up to $300/month)
-- RECURRING: 2% (up to $500/month)
-- Base: 1.5% on everything else

-- Delete incorrect/redundant rules (TELECOM, STREAMING are part of RECURRING; RETAIL, HOME_IMPROVEMENT are base rate)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'CashBack World Elite Mastercard')
AND category IN ('TELECOM', 'STREAMING', 'RETAIL', 'HOME_IMPROVEMENT');

-- Keep RENT as it's a useful subcategory of RECURRING for user reference


-- ============================================
-- SECTION 10: BMO ECLIPSE VISA INFINITE (id=27)
-- ============================================
-- Official rates:
-- DINING: 5x (up to 30,000 pts/year)
-- GROCERY: 5x (up to 30,000 pts/year)
-- GAS: 5x (up to 100,000 pts/year)
-- TRANSIT: 5x (up to 100,000 pts/year)
-- Base: 1x on everything else

-- Delete incorrect rules (TRAVEL and STREAMING are not bonus categories)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite')
AND category IN ('TRAVEL', 'STREAMING');

-- Add GAS 5x rule (missing)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.05, NULL, '5x points on gas (up to 100,000 pts/year)'
FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite'
ON DUPLICATE KEY UPDATE reward_rate = 0.05, description = '5x points on gas (up to 100,000 pts/year)';

-- Fix TRANSIT from 2x to 5x
UPDATE reward_rules
SET reward_rate = 0.05, description = '5x points on transit (up to 100,000 pts/year)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite')
AND category = 'TRANSIT';

-- Update DINING and GROCERY descriptions with annual caps
UPDATE reward_rules
SET description = '5x points on dining (up to 30,000 pts/year)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite')
AND category = 'DINING';

UPDATE reward_rules
SET description = '5x points on groceries (up to 30,000 pts/year)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite')
AND category = 'GROCERY';


-- ============================================
-- SECTION 11: TRIANGLE WORLD ELITE MASTERCARD (id=49)
-- ============================================
-- Official rates:
-- RETAIL: 4% at Canadian Tire, Sport Chek, Mark's, etc.
-- GROCERY: 3% (up to $12,000/year, excludes Costco/Walmart)
-- GAS: 5¢/L regular, 7¢/L premium at Gas+ (~2% equivalent)
-- Base: 1% on everything else
-- Perks: Free Roadside Assistance, pay bills with card

-- Fix GAS description (remove garbled characters)
UPDATE reward_rules
SET description = '5-7 cents/L at Gas+ stations (~2% equivalent)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle World Elite Mastercard')
AND category = 'GAS';

-- Update GROCERY description
UPDATE reward_rules
SET description = '3% CT Money on groceries (up to $12,000/year, excludes Costco/Walmart)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle World Elite Mastercard')
AND category = 'GROCERY';

-- Update RETAIL description
UPDATE reward_rules
SET description = '4% CT Money at Canadian Tire, Sport Chek, Mark''s, Atmosphere, Party City'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle World Elite Mastercard')
AND category = 'RETAIL';


-- ============================================
-- SECTION 12: TRIANGLE MASTERCARD (id=50)
-- ============================================
-- Official rates:
-- RETAIL: 4% at Canadian Tire, Sport Chek, Mark's, etc.
-- GROCERY: 1.5% (up to $12,000/year, excludes Costco/Walmart)
-- GAS: 5¢/L at Gas+ (~1.5% equivalent)
-- Base: 0.5% on everything else

-- Fix GAS description (remove garbled characters)
UPDATE reward_rules
SET description = '5 cents/L at Gas+ stations (~1.5% equivalent)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle Mastercard')
AND category = 'GAS';

-- Update RETAIL description
UPDATE reward_rules
SET description = '4% CT Money at Canadian Tire, Sport Chek, Mark''s'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle Mastercard')
AND category = 'RETAIL';

-- Add missing GROCERY rule (1.5%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.015, 1000, '1.5% CT Money on groceries (up to $12,000/year, excludes Costco/Walmart)'
FROM credit_cards WHERE bank = 'Canadian Tire' AND name = 'Triangle Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.015, description = '1.5% CT Money on groceries (up to $12,000/year, excludes Costco/Walmart)';


-- ============================================
-- SECTION 13: CIBC ADAPTA MASTERCARD (id=53)
-- ============================================
-- Official rates:
-- Top 3 categories: 1.5 pts/$1 (auto-detected monthly, $40K/yr cap)
-- Travel via CIBCbyExpedia: 2 pts/$1
-- Base: 1 pt/$1 on everything else
-- Point value: 1,500 pts = $10 cashback (0.667¢/pt)

-- Update OTHER rule description (top 3 categories)
UPDATE reward_rules
SET description = '1.5 pts/$1 on your top 3 spending categories (auto-detected each month, $40K/yr cap)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Adapta Mastercard')
AND category = 'OTHER';

-- Update TRAVEL rule description
UPDATE reward_rules
SET description = '2 pts/$1 on travel booked via CIBCbyExpedia.com'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Adapta Mastercard')
AND category = 'TRAVEL';


-- ============================================
-- SECTION 14: CIBC AEROPLAN VISA CARD (id=62)
-- ============================================
-- Official rates:
-- GAS, EV_CHARGING, GROCERY, TRAVEL (Air Canada): 1 pt/$1
-- Everything else: 1 pt/$1.50 (0.67 pt/$1) - handled by base_reward_rate
-- No annual fee entry-level Aeroplan card

-- Delete duplicate OTHER rule (base_reward_rate already handles this)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card')
AND category = 'OTHER';

-- Update GAS rule description
UPDATE reward_rules
SET description = '1 Aeroplan point per $1 on gas'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card')
AND category = 'GAS';

-- Update EV_CHARGING rule description
UPDATE reward_rules
SET description = '1 Aeroplan point per $1 on EV charging'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card')
AND category = 'EV_CHARGING';

-- Update GROCERY rule description
UPDATE reward_rules
SET description = '1 Aeroplan point per $1 on groceries'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card')
AND category = 'GROCERY';

-- Update TRAVEL rule description (Air Canada)
UPDATE reward_rules
SET description = '1 Aeroplan point per $1 on Air Canada purchases'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card')
AND category = 'TRAVEL';


-- ============================================
-- SECTION 15: CIBC AEROPLAN VISA INFINITE (id=24)
-- ============================================
-- Official rates:
-- TRAVEL (Air Canada), GROCERY, GAS: 1.5 pts/$1
-- Everything else: 1 pt/$1 (base_reward_rate)
-- Perks: Free checked bag, first year free, travel insurance

-- Update TRAVEL rule description
UPDATE reward_rules
SET description = '1.5 Aeroplan points per $1 on Air Canada purchases'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite')
AND category = 'TRAVEL';

-- Update GROCERY rule description
UPDATE reward_rules
SET description = '1.5 Aeroplan points per $1 on groceries'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite')
AND category = 'GROCERY';

-- Update GAS rule description
UPDATE reward_rules
SET description = '1.5 Aeroplan points per $1 on gas'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite')
AND category = 'GAS';


-- ============================================
-- SECTION 16: CIBC AVENTURA VISA INFINITE (id=22)
-- ============================================
-- Official rates:
-- TRAVEL (via CIBC Rewards Centre): 2x
-- GAS, EV_CHARGING, GROCERY, PHARMACY: 1.5x
-- Everything else: 1x (base_reward_rate)
-- Perks: 4 lounge visits/year, $160 NEXUS discount

-- Update TRAVEL rule description
UPDATE reward_rules
SET description = '2 Aventura points per $1 on travel via CIBC Rewards Centre'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite')
AND category = 'TRAVEL';

-- Update GROCERY rule description
UPDATE reward_rules
SET description = '1.5 Aventura points per $1 on groceries'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite')
AND category = 'GROCERY';

-- Update GAS rule description
UPDATE reward_rules
SET description = '1.5 Aventura points per $1 on gas'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite')
AND category = 'GAS';

-- Update PHARMACY rule description
UPDATE reward_rules
SET description = '1.5 Aventura points per $1 on drugstores'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite')
AND category = 'PHARMACY';

-- Add missing EV_CHARGING rule (1.5x)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'EV_CHARGING', 0.015, NULL, '1.5 Aventura points per $1 on EV charging'
FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite'
ON DUPLICATE KEY UPDATE reward_rate = 0.015, description = '1.5 Aventura points per $1 on EV charging';


-- ============================================
-- SECTION 17: CIBC AVENTURA VISA INFINITE PRIVILEGE (id=23)
-- ============================================
-- Official rates:
-- TRAVEL (via CIBC Rewards Centre): 3x
-- GROCERY, GAS, EV_CHARGING, DINING: 2x
-- Everything else: 1.25x (base_reward_rate)
-- Perks: 6 lounge visits/year, $200 NEXUS discount, $200 travel credit

-- Update TRAVEL rule (2.5x → 3x)
UPDATE reward_rules
SET reward_rate = 0.03, description = '3 Aventura points per $1 on travel via CIBC Rewards Centre'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege')
AND category = 'TRAVEL';

-- Update GROCERY rule (1.75x → 2x)
UPDATE reward_rules
SET reward_rate = 0.02, description = '2 Aventura points per $1 on groceries'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege')
AND category = 'GROCERY';

-- Update GAS rule (1.75x → 2x)
UPDATE reward_rules
SET reward_rate = 0.02, description = '2 Aventura points per $1 on gas'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege')
AND category = 'GAS';

-- Update PHARMACY rule (1.75x → 2x)
UPDATE reward_rules
SET reward_rate = 0.02, description = '2 Aventura points per $1 on drugstores'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege')
AND category = 'PHARMACY';


-- ============================================
-- SECTION 18: CIBC COSTCO MASTERCARD (id=26)
-- ============================================
-- Official rates (no limits):
-- DINING: 3% on restaurants
-- GAS: 3% at Costco gas, 2% at other gas stations
-- EV_CHARGING: 2%
-- ONLINE_SHOPPING (Costco.ca): 2%
-- Everything else (including in-warehouse Costco): 1% (base_reward_rate)
-- Note: WHOLESALE rule should be removed - Costco in-store is 1%, not 2%

-- Delete incorrect WHOLESALE rule (Costco in-store is 1%, covered by base rate)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Costco Mastercard')
AND category = 'WHOLESALE';

-- Update GAS rule description to clarify Costco gas vs other gas
UPDATE reward_rules
SET description = '3% at Costco Gas Bars (2% at other gas stations)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Costco Mastercard')
AND category = 'GAS';

-- Update ONLINE_SHOPPING rule description
UPDATE reward_rules
SET description = '2% on Costco.ca purchases'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Costco Mastercard')
AND category = 'ONLINE_SHOPPING';

-- Add EV_CHARGING rule (2%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'EV_CHARGING', 0.02, NULL, '2% cash back on EV charging'
FROM credit_cards WHERE bank = 'CIBC' AND name = 'Costco Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on EV charging';


-- ============================================
-- SECTION 19: CIBC DIVIDEND VISA CARD (id=61)
-- ============================================
-- Official rates (no limits):
-- GROCERY: 2%
-- GAS, EV_CHARGING, TRANSIT, DINING, RECURRING, TRAVEL: 1%
-- Everything else: 0.5% (base_reward_rate)
-- Note: Delete OTHER rule to avoid duplicate display with base_reward_rate

-- Delete OTHER rule (duplicates base_reward_rate of 0.5%)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Dividend Visa Card')
AND category = 'OTHER';


-- ============================================
-- SECTION 20: CIBC DIVIDEND VISA INFINITE (id=25)
-- ============================================
-- Official rates (no limits):
-- GAS, EV_CHARGING, GROCERY: 4%
-- TRANSIT, DINING, RECURRING, TRAVEL (via CIBC by Expedia): 2%
-- Everything else: 1% (base_reward_rate)
-- Note: RETAIL and HOME_IMPROVEMENT rules are redundant (same as base rate)

-- Delete redundant RETAIL rule (1% = base rate)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite')
AND category = 'RETAIL';

-- Delete redundant HOME_IMPROVEMENT rule (1% = base rate)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite')
AND category = 'HOME_IMPROVEMENT';

-- Add TRAVEL rule (2% via CIBC by Expedia)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.02, NULL, '2% cash back on travel via CIBC by Expedia'
FROM credit_cards WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on travel via CIBC by Expedia';


-- ============================================
-- SECTION 21: DESJARDINS CASH BACK MASTERCARD (id=48)
-- ============================================
-- Official rates:
-- DINING: 2% (up to $3,600/year combined with RECURRING, then 0.5%)
-- ENTERTAINMENT: 2%
-- TRANSIT: 2%
-- RECURRING: 2% (up to $3,600/year combined with DINING, then 0.5%)
-- Everything else: 0.5% (base_reward_rate)
-- Note: GROCERY rule is incorrect and should be deleted

-- Delete incorrect GROCERY rule (not offered by this card)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard')
AND category = 'GROCERY';

-- Add DINING rule (2%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.02, NULL, '2% cash back on restaurants (up to $3,600/year with recurring, then 0.5%)'
FROM credit_cards WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on restaurants (up to $3,600/year with recurring, then 0.5%)';

-- Add ENTERTAINMENT rule (2%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'ENTERTAINMENT', 0.02, NULL, '2% cash back on entertainment'
FROM credit_cards WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on entertainment';

-- Add TRANSIT rule (2%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRANSIT', 0.02, NULL, '2% cash back on public transit & alternative transportation'
FROM credit_cards WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on public transit & alternative transportation';

-- Add RECURRING rule (2%)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RECURRING', 0.02, NULL, '2% cash back on pre-authorized payments (up to $3,600/year with dining, then 0.5%)'
FROM credit_cards WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard'
ON DUPLICATE KEY UPDATE reward_rate = 0.02, description = '2% cash back on pre-authorized payments (up to $3,600/year with dining, then 0.5%)';


-- ============================================
-- SECTION 22: HOME TRUST PREFERRED VISA (id=43)
-- ============================================
-- Official rates:
-- All CAD purchases: 1% (base_reward_rate)
-- Foreign purchases: NO CASHBACK (but no FX fee)
-- Note: FOREIGN and TRAVEL rules are incorrect - should be deleted

-- Delete incorrect FOREIGN rule (no cashback on foreign purchases!)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Home Trust' AND name = 'Preferred Visa')
AND category = 'FOREIGN';

-- Delete redundant TRAVEL rule (same as base rate)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Home Trust' AND name = 'Preferred Visa')
AND category = 'TRAVEL';


-- ============================================
-- SECTION 23: MBNA REWARDS WORLD ELITE MASTERCARD (id=40)
-- ============================================
-- Fix: RENT is not a household utility, remove it
-- Official 5x categories: restaurants, grocery, digital media, membership, household utilities

-- Delete incorrect RENT rule (household utilities ≠ rent)
DELETE FROM reward_rules
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard')
AND category = 'RENT';


-- ============================================
-- SECTION 24: MERIDIAN VISA CASH BACK (id=59)
-- ============================================
-- Add missing reward rules: 1% on gas, grocery, pharmacy, recurring
-- Base rate is 0.5% on other purchases

-- Insert GAS 1%
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back'), 'GAS', 0.0100, '1% on gas'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'GAS');

-- Insert GROCERY 1%
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back'), 'GROCERY', 0.0100, '1% on groceries'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'GROCERY');

-- Insert PHARMACY 1%
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back'), 'PHARMACY', 0.0100, '1% on pharmacy'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'PHARMACY');

-- Insert RECURRING 1%
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back'), 'RECURRING', 0.0100, '1% on utility bills'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Meridian' AND name = 'Visa Cash Back') AND category = 'RECURRING');


-- ============================================
-- SECTION 25: NATIONAL BANK WORLD ELITE MASTERCARD (id=42)
-- ============================================
-- Fix: Delete RENT (not a valid category), keep RECURRING for bills
-- Also remove redundant TELECOM, INSURANCE, STREAMING (covered by RECURRING or base rate)

-- Delete RENT (not a valid 2x category)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'RENT';

-- Delete TELECOM (should use RECURRING for bills)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'TELECOM';

-- Delete INSURANCE (not a specific 2x category)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'INSURANCE';

-- Delete STREAMING (not a specific 2x category)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard') AND category = 'STREAMING';


-- ============================================
-- SECTION 26: NEO WORLD ELITE MASTERCARD (id=35)
-- ============================================
-- Fix: Remove redundant categories that are same as base rate or covered by other categories

-- Delete RENT (should use RECURRING)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Neo' AND name = 'World Elite Mastercard') AND category = 'RENT';

-- Delete RETAIL (same as base rate 1%)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Neo' AND name = 'World Elite Mastercard') AND category = 'RETAIL';

-- Delete HOME_IMPROVEMENT (same as base rate 1%)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Neo' AND name = 'World Elite Mastercard') AND category = 'HOME_IMPROVEMENT';

-- Update RECURRING cap to $500/month (not $1,000)
UPDATE reward_rules
SET monthly_cap_amount = 500.00
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Neo' AND name = 'World Elite Mastercard') AND category = 'RECURRING';


-- ============================================
-- SECTION 27: PC FINANCIAL WORLD ELITE MASTERCARD (id=37)
-- ============================================
-- Fix: Delete RETAIL rule (same as base rate 1%)

DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard') AND category = 'RETAIL';


-- ============================================
-- SECTION 28: RBC WESTJET WORLD ELITE MASTERCARD (id=15)
-- ============================================

-- Add missing GROCERY rule (2x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard'), 'GROCERY', 0.0200, '2x WestJet points on groceries'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'GROCERY');

-- Add missing GAS rule (2x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard'), 'GAS', 0.0200, '2x WestJet points on gas'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'GAS');

-- Add missing EV_CHARGING rule (2x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard'), 'EV_CHARGING', 0.0200, '2x WestJet points on EV charging'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'EV_CHARGING');

-- Add missing TRANSIT rule (2x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard'), 'TRANSIT', 0.0200, '2x WestJet points on transit & rideshare'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard') AND category = 'TRANSIT');


-- ============================================
-- SECTION 29: ROGERS RED MASTERCARD (id=32)
-- ============================================
UPDATE credit_cards
SET name = 'Red Mastercard'
WHERE bank = 'Rogers' AND name = 'Platinum Mastercard';

-- 39.2 Rename Rogers World Elite Mastercard to Rogers Red World Elite Mastercard
UPDATE credit_cards
SET name = 'Red World Elite Mastercard'
WHERE bank = 'Rogers' AND name = 'World Elite Mastercard';

-- Delete incorrect FOREIGN rule (there IS a 2.5% FX fee on this card)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red Mastercard') AND category = 'FOREIGN';

-- Delete incorrect TELECOM rule (1.5x is redemption bonus, not earning rate)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red Mastercard') AND category = 'TELECOM';

-- Add USD rule (2% on USD purchases)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red Mastercard'), 'USD', 0.0200, '2% cashback on USD purchases'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red Mastercard') AND category = 'USD');

-- Note: For Rogers/Fido/Shaw customers, they get 2% on all CAD purchases (handled by base_reward_rate)
-- For non-customers, base rate is 1% CAD
-- The 1.5x Rogers redemption bonus is a redemption feature, not an earning rate


-- ============================================
-- SECTION 30: ROGERS RED WORLD ELITE MASTERCARD (id=31)
-- ============================================

-- Delete incorrect TRAVEL rule (no special travel bonus)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard') AND category = 'TRAVEL';

-- Delete incorrect FOREIGN rule (there IS a 2.5% FX fee on non-CAD/non-USD)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard') AND category = 'FOREIGN';

-- Delete incorrect TELECOM rule (Rogers customers get 2% on ALL purchases, not just telecom)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard') AND category = 'TELECOM';

-- Delete incorrect RETAIL rule (use base_reward_rate instead)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard') AND category = 'RETAIL';

-- Add USD rule (3% on USD purchases)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard'), 'USD', 0.0300, '3% cashback on USD purchases'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard') AND category = 'USD');

-- Note: base_reward_rate = 1.5% for non-Rogers customers
-- Rogers/Fido/Shaw customers get 2% on all non-USD purchases (condition-based, not a separate rule)
-- The 1.5x Rogers redemption bonus is a redemption feature, not an earning rate
-- 2.5% FX fee applies to non-CAD/non-USD currencies


-- ============================================
-- SECTION 31: SCOTIABANK GOLD AMERICAN EXPRESS (id=18)
-- ============================================

-- Update GROCERY from 3x to 5x (6x at Sobeys/Safeway, but we use general grocer rate)
UPDATE reward_rules SET reward_rate = 0.0500, description = '5x Scene+ points at grocery stores (6x at Sobeys/Safeway/FreshCo)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'GROCERY';

-- Update ENTERTAINMENT from 3x to 5x
UPDATE reward_rules SET reward_rate = 0.0500, description = '5x Scene+ points on entertainment (movies, theatre)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'ENTERTAINMENT';

-- Add GAS rule (3x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express'), 'GAS', 0.0300, '3x Scene+ points on gas'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'GAS');

-- Add TRANSIT rule (3x)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express'), 'TRANSIT', 0.0300, '3x Scene+ points on transit and rideshare'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'TRANSIT');

-- Add FOREIGN rule (no FX fee)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express'), 'FOREIGN', 0.0100, '1x Scene+ points on foreign purchases - NO FX fee'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Gold American Express') AND category = 'FOREIGN');

-- Note: Accelerated rates apply to first $50,000/year, then 1x
-- Note: Travel via Scene+ Travel portal gets 4x (3x bonus + 1x base)


-- ============================================
-- SECTION 32: SCOTIABANK PASSPORT VISA INFINITE (id=19)
-- ============================================

-- Update GROCERY to 3x for Sobeys family stores (primary grocery partner)
UPDATE reward_rules SET reward_rate = 0.0300, description = '3x Scene+ points at Sobeys/Safeway/IGA/Foodland (2x at other grocers)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite') AND category = 'GROCERY';

-- Note: 2x categories (DINING, TRANSIT, ENTERTAINMENT) are correct
-- Note: FOREIGN 1x with no FX fee is correct
-- Note: $50,000 annual cap on accelerated (2x-3x) categories


-- ============================================
-- SECTION 33: SCOTIABANK SCENE+ VISA (id=21)
-- ============================================

-- Update ENTERTAINMENT description to mention Cineplex
UPDATE reward_rules SET description = '2x Scene+ points at Cineplex theatres'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'ENTERTAINMENT';

-- Add GROCERY rule (2x at Sobeys family stores)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa'), 'GROCERY', 0.0200, '2x Scene+ points at Sobeys/Safeway/IGA/Foodland'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'GROCERY');

-- Add HOME_IMPROVEMENT rule (2x at Home Hardware)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa'), 'HOME_IMPROVEMENT', 0.0200, '2x Scene+ points at Home Hardware'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa') AND category = 'HOME_IMPROVEMENT');

-- Note: base_reward_rate = 1x on all other purchases
-- Note: 4x on hotels/car rentals via Scene+ Travel portal (1x base + 3x bonus)


-- ============================================
-- SECTION 34: TANGERINE MONEY-BACK CREDIT CARD (id=33)
-- ============================================

-- Add missing categories (Tangerine added 3 new categories in Oct 2025, total now 13)
-- Note: User chooses 2 categories (3 if rewards go to Savings Account), each gets 2%

-- Add HOTEL category (Hotel-Motel)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card'), 'HOTEL', 0.0200, '2% on hotels/motels (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card') AND category = 'HOTEL');

-- Add FURNITURE category
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card'), 'FURNITURE', 0.0200, '2% on furniture (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card') AND category = 'FURNITURE');

-- Add FOREIGN category (Foreign Currency Spend - new in Oct 2025)
-- Note: Still has 2.5% FX fee, so net is -0.5% on foreign purchases
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card'), 'FOREIGN', 0.0200, '2% on foreign currency spend (if selected) - still has 2.5% FX fee'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card') AND category = 'FOREIGN');

-- Add FITNESS category (new in Oct 2025)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card'), 'FITNESS', 0.0200, '2% on fitness/sports clubs (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card') AND category = 'FITNESS');

-- Note: E-Games category not added as we don't have this category type in our system


-- ============================================
-- SECTION 35: TANGERINE WORLD MASTERCARD (id=34)
-- ============================================

-- Add missing categories (same as Money-Back, Tangerine added 3 new categories in Oct 2025)
-- Note: User chooses 2 categories (3 if rewards go to Savings Account), each gets 2%

-- Add HOTEL category (Hotel-Motel)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard'), 'HOTEL', 0.0200, '2% on hotels/motels (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard') AND category = 'HOTEL');

-- Add FURNITURE category
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard'), 'FURNITURE', 0.0200, '2% on furniture (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard') AND category = 'FURNITURE');

-- Add FOREIGN category (Foreign Currency Spend - new in Oct 2025)
-- Note: Still has 2.5% FX fee, so net is -0.5% on foreign purchases
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard'), 'FOREIGN', 0.0200, '2% on foreign currency spend (if selected) - still has 2.5% FX fee'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard') AND category = 'FOREIGN');

-- Add FITNESS category (new in Oct 2025)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard'), 'FITNESS', 0.0200, '2% on fitness/sports clubs (if selected as category)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Tangerine' AND name = 'World Mastercard') AND category = 'FITNESS');

-- Note: E-Games category not added as we don't have this category type in our system


-- ============================================
-- SECTION 36: TD AEROPLAN VISA INFINITE (id=10)
-- ============================================

-- Add EV_CHARGING category (1.5 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite'), 'EV_CHARGING', 0.0150, '1.5x Aeroplan points on EV charging'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite') AND category = 'EV_CHARGING');


-- ============================================
-- SECTION 37: TD AEROPLAN VISA INFINITE PRIVILEGE (id=11)
-- ============================================

-- Fix TRAVEL rate from 2.5x to 2x (Air Canada purchases)
UPDATE reward_rules
SET reward_rate = 0.0200, description = '2x Aeroplan points on Air Canada purchases'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'TRAVEL';

-- Add GAS category (1.5 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege'), 'GAS', 0.0150, '1.5x Aeroplan points on gas'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'GAS');

-- Add TRANSIT category (1.5 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege'), 'TRANSIT', 0.0150, '1.5x Aeroplan points on transit'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'TRANSIT');

-- Add EV_CHARGING category (1.5 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege'), 'EV_CHARGING', 0.0150, '1.5x Aeroplan points on EV charging'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege') AND category = 'EV_CHARGING');


-- ============================================
-- SECTION 38: TD CASH BACK VISA (id=12)
-- ============================================

-- Add EV_CHARGING category (1% cash back)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa'), 'EV_CHARGING', 0.0100, '1% cash back on EV charging'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa') AND category = 'EV_CHARGING');

-- Add TRANSIT category (1% cash back)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa'), 'TRANSIT', 0.0100, '1% cash back on public transit'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa') AND category = 'TRANSIT');

-- Add STREAMING category (1% cash back)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa'), 'STREAMING', 0.0100, '1% cash back on streaming services'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa') AND category = 'STREAMING');

-- Add ENTERTAINMENT category (1% cash back on digital gaming/media)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa'), 'ENTERTAINMENT', 0.0100, '1% cash back on digital gaming and media'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa') AND category = 'ENTERTAINMENT');


-- ============================================
-- SECTION 39: TD CASH BACK VISA INFINITE (id=8)
-- ============================================

-- Remove redundant RETAIL rule (base_reward_rate already handles 1% on all other purchases)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa Infinite') AND category = 'RETAIL';


-- ============================================
-- SECTION 40: TD FIRST CLASS VISA INFINITE (id=9)
-- ============================================

-- Fix TRAVEL rate from 3% to 8% (8 points per $1 on Expedia for TD)
UPDATE reward_rules
SET reward_rate = 0.0800, description = '8x TD Rewards points on travel via Expedia for TD'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'TRAVEL';

-- Fix DINING rate from 2% to 6% (6 points per $1)
UPDATE reward_rules
SET reward_rate = 0.0600, description = '6x TD Rewards points on dining'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'DINING';

-- Fix ENTERTAINMENT rate from 2% to 4% (4 points per $1 on streaming/gaming)
UPDATE reward_rules
SET reward_rate = 0.0400, description = '4x TD Rewards points on streaming and gaming'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'ENTERTAINMENT';

-- Add GROCERY category (6 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite'), 'GROCERY', 0.0600, '6x TD Rewards points on groceries'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'GROCERY');

-- Add TRANSIT category (6 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite'), 'TRANSIT', 0.0600, '6x TD Rewards points on public transit'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'TRANSIT');

-- Add RECURRING category (4 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite'), 'RECURRING', 0.0400, '4x TD Rewards points on recurring bills'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'RECURRING');

-- Add STREAMING category (4 points per $1)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite'), 'STREAMING', 0.0400, '4x TD Rewards points on streaming services'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'TD' AND name = 'First Class Visa Infinite') AND category = 'STREAMING');


-- ============================================
-- SECTION 41: VANCITY ENVIRO VISA CLASSIC (id=52)
-- ============================================

-- Delete redundant OTHER rule (base_reward_rate handles 0.5% on all purchases)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Classic') AND category = 'OTHER';

-- Add TRAVEL category (2x points when booking through Vancity Rewards)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Classic'), 'TRAVEL', 0.0200, '2x Vancity points on travel via Vancity Rewards portal'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Classic') AND category = 'TRAVEL');


-- ============================================
-- SECTION 42: VANCITY ENVIRO VISA INFINITE (id=51)
-- ============================================

-- Delete redundant OTHER rule (base_reward_rate handles 1.25x on all purchases)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'OTHER';

-- Add TRAVEL category (2x base = 2.5x when booking through Vancity Rewards)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite'), 'TRAVEL', 0.0250, '2x points (2.5% value) on travel via Vancity Rewards portal'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'TRAVEL');

-- Add LOCAL_BUSINESS category (10 points per $1 at select BC partners)
INSERT INTO reward_rules (card_id, category, reward_rate, description)
SELECT (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite'), 'LOCAL_BUSINESS', 0.1000, '10x points at select BC partners (Modo, JJ Bean, Fresh Prep, etc.)'
WHERE NOT EXISTS (SELECT 1 FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite') AND category = 'LOCAL_BUSINESS');


-- ============================================
-- SECTION 43: WEALTHSIMPLE VISA INFINITE (id=46)
-- ============================================
-- Official rates:
-- 2% unlimited on all purchases (base_reward_rate)
-- No foreign transaction fees
-- Note: OTHER rule is redundant (same as base rate)

-- Delete redundant OTHER rule (base_reward_rate already handles 2%)
DELETE FROM reward_rules WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Wealthsimple' AND name = 'Visa Infinite') AND category = 'OTHER';

-- Update FOREIGN rule description
UPDATE reward_rules
SET reward_rate = 0.0200, description = '2% cashback + no foreign transaction fees'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Wealthsimple' AND name = 'Visa Infinite') AND category = 'FOREIGN';


-- ============================================
-- SECTION 44: [ADD MORE CARDS BELOW]
-- ============================================
-- Template:
--
-- -- Update [Card Name] base rate
-- UPDATE credit_cards
-- SET base_reward_rate = 0.0100  -- 1% or 1x
-- WHERE bank = 'BANK' AND name = 'Card Name';
--
-- -- Delete incorrect rules
-- DELETE FROM reward_rules
-- WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'BANK' AND name = 'Card Name')
-- AND category = 'CATEGORY_TO_DELETE';
--
-- -- Update/Insert rules
-- INSERT INTO reward_rules (card_id, category, reward_rate, description)
-- SELECT (SELECT id FROM credit_cards WHERE bank = 'BANK' AND name = 'Card Name'),
--        'CATEGORY', 0.0200, '2x points on category'
-- WHERE NOT EXISTS (...);


COMMIT;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================
