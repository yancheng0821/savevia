-- SaveVia Credit Card Data Update
-- Generated: 2025-12-15
-- New cards not in current database

-- ============================================
-- NEW CARDS
-- ============================================

-- Wealthsimple Cards
-- ============================================

-- Wealthsimple Visa Infinite
-- $240/year ($20/month), 2% unlimited cashback, no FX fee
-- Fee waived with $100K assets or $4K monthly direct deposit
-- Card color: black-gray
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Wealthsimple', 'Visa Infinite', 'VISA', 240.00, 0.02, '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": "Fee waived with $100K assets or $4K/month direct deposit"}', '{"gradient": "linear-gradient(135deg, #374151 0%, #111827 100%)", "textColor": "white"}', 'https://www.wealthsimple.com/en-ca/credit-card', true, true);

SET @ws_vi_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@ws_vi_id, 'OTHER', 0.02, NULL, '2% unlimited cashback on all purchases'),
(@ws_vi_id, 'FOREIGN', 0.02, NULL, '2% cashback + no foreign transaction fees');


-- Desjardins Cards
-- ============================================

-- Desjardins Cash Back World Elite Mastercard
-- $100/year, 4% grocery (up to $10K/yr), 3% restaurant/entertainment/transit (up to $6K/yr), 1% other
-- Card color: gray-black
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Desjardins', 'Cash Back World Elite Mastercard', 'MASTERCARD', 100.00, 0.01, '{"bonusAmount": 100, "minSpend": 0, "daysToComplete": 0, "description": "$100 cash back welcome bonus"}', '{"gradient": "linear-gradient(135deg, #4b5563 0%, #1f2937 100%)", "textColor": "white"}', 'https://www.desjardins.com/en/credit-cards/cash-back-world-elite-mastercard.html', false, true);

SET @desj_we_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@desj_we_id, 'GROCERY', 0.04, 833, '4% on groceries (up to $10,000/year)'),
(@desj_we_id, 'DINING', 0.03, 500, '3% on restaurants (up to $6,000/year)'),
(@desj_we_id, 'ENTERTAINMENT', 0.03, 500, '3% on entertainment (up to $6,000/year)'),
(@desj_we_id, 'TRANSIT', 0.03, 500, '3% on public transit (up to $6,000/year)');

-- Desjardins Cash Back Mastercard (No Fee)
-- No annual fee, 1.5% grocery, 1% everything else
-- Card color: left white, right gray
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Desjardins', 'Cash Back Mastercard', 'MASTERCARD', 0, 0.01, NULL, '{"gradient": "linear-gradient(90deg, #ffffff 0%, #9ca3af 100%)", "textColor": "#1f2937"}', 'https://www.desjardins.com/en/credit-cards/cash-back-mastercard.html', false, true);

SET @desj_cb_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@desj_cb_id, 'GROCERY', 0.015, NULL, '1.5% on groceries');


-- Canadian Tire / Triangle Cards
-- ============================================

-- Triangle World Elite Mastercard
-- No annual fee, 4% at CT stores, 3% groceries (up to $12K/yr), 5-7¢/L gas
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Canadian Tire', 'Triangle World Elite Mastercard', 'MASTERCARD', 0, 0.01, '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": "4% CT Money at Canadian Tire stores"}', NULL, 'https://triangle.canadiantire.ca/en/credit-cards/triangle-world-elite-mastercard.html', false, true);

SET @ct_we_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@ct_we_id, 'RETAIL', 0.04, NULL, '4% CT Money at Canadian Tire, Sport Chek, Mark''s, Atmosphere'),
(@ct_we_id, 'GROCERY', 0.03, 1000, '3% CT Money on groceries (up to $12,000/year, excludes Costco/Walmart)'),
(@ct_we_id, 'GAS', 0.02, NULL, '5-7¢/L at Gas+ stations (~2% equivalent)');

-- Triangle Mastercard (No Fee, lower tier)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Canadian Tire', 'Triangle Mastercard', 'MASTERCARD', 0, 0.005, NULL, NULL, 'https://triangle.canadiantire.ca/en/credit-cards.html', false, true);

SET @ct_mc_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@ct_mc_id, 'RETAIL', 0.04, NULL, '4% CT Money at Canadian Tire, Sport Chek, Mark''s'),
(@ct_mc_id, 'GAS', 0.015, NULL, '3-5¢/L at Gas+ stations');


-- Vancity Cards (BC Only)
-- ============================================

-- Vancity enviro Visa Infinite
-- $120/year (waived for Total Chequing members), 2.5% grocery, 5% transit, 1.25% other
-- BC residents only, up to $540 in rewards value first year
-- Card color: dark green
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Vancity', 'enviro Visa Infinite', 'VISA', 120.00, 0.0125, '{"bonusAmount": 54000, "minSpend": 0, "daysToComplete": 365, "description": "Up to $540 in rewards value first year + first year fee waived + airport lounge access"}', '{"gradient": "linear-gradient(135deg, #22c55e 0%, #166534 100%)", "textColor": "white"}', 'https://www.vancity.com/bank/credit-cards/enviro-infinite/', false, true);

SET @vancity_vi_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@vancity_vi_id, 'GROCERY', 0.025, NULL, '2.5 points/$1 on groceries (2.5% value)'),
(@vancity_vi_id, 'TRANSIT', 0.05, NULL, '5 points/$1 on public transit and ferries (5% value)'),
(@vancity_vi_id, 'OTHER', 0.0125, NULL, '1.25 points/$1 on all other purchases');

-- Vancity enviro Visa Classic (No Fee)
-- No annual fee, 1% on everything
-- Card color: light green (muted)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Vancity', 'enviro Visa Classic', 'VISA', 0, 0.01, '{"bonusAmount": 5000, "minSpend": 1500, "daysToComplete": 90, "description": "5,000 points ($50 value)"}', '{"gradient": "linear-gradient(135deg, #6ee7b7 0%, #34d399 100%)", "textColor": "#065f46"}', 'https://www.vancity.com/bank/credit-cards/enviro-classic/', false, true);

SET @vancity_classic_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@vancity_classic_id, 'OTHER', 0.01, NULL, '1 point/$1 on all purchases (1% value)');


-- CIBC Adapta Mastercard (New 2025)
-- ============================================

-- CIBC Adapta Mastercard
-- No annual fee, 1.5 pts/$1 on top 3 categories (auto-detected), 1 pt/$1 other
-- $40,000 annual cap on bonus categories
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('CIBC', 'Adapta Mastercard', 'MASTERCARD', 0, 0.01, '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": "Auto-adapts to your spending - 1.5x on top 3 categories each month"}', NULL, 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/adapta-mastercard.html', false, true);

SET @cibc_adapta_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@cibc_adapta_id, 'OTHER', 0.015, 3333, '1.5 Adapta pts/$1 on top 3 spending categories (auto-detected monthly, $40K/yr cap)'),
(@cibc_adapta_id, 'TRAVEL', 0.02, NULL, '2 Adapta pts/$1 on travel booked via CIBCbyExpedia.com');


-- RBC Cards (Additional)
-- ============================================

-- RBC ION+ Visa
-- $48/year (waived for students/under 24), 3x grocery/dining/gas/streaming/transit, 1x other
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('RBC', 'ION+ Visa', 'VISA', 48.00, 0.01, '{"bonusAmount": 14000, "minSpend": 0, "daysToComplete": 0, "description": "14,000 Avion points (~$100 value)"}', NULL, 'https://www.rbcroyalbank.com/credit-cards/rewards/rbc-ion-plus-visa.html', false, true);

SET @rbc_ion_plus_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@rbc_ion_plus_id, 'GROCERY', 0.03, NULL, '3x Avion points on groceries'),
(@rbc_ion_plus_id, 'DINING', 0.03, NULL, '3x Avion points on dining & food delivery'),
(@rbc_ion_plus_id, 'GAS', 0.03, NULL, '3x Avion points on gas & EV charging'),
(@rbc_ion_plus_id, 'TRANSIT', 0.03, NULL, '3x Avion points on rideshare & transit'),
(@rbc_ion_plus_id, 'STREAMING', 0.03, NULL, '3x Avion points on streaming & subscriptions');


-- BMO Cards (Additional)
-- ============================================

-- BMO Ascend World Elite Mastercard
-- $150/year, 5x travel, 3x dining/entertainment/recurring, 1x other
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('BMO', 'Ascend World Elite Mastercard', 'MASTERCARD', 150.00, 0.01, '{"bonusAmount": 90000, "minSpend": 4500, "daysToComplete": 90, "description": "Up to 90,000 BMO points"}', NULL, 'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-ascend-world-elite-mastercard/', false, true);

SET @bmo_ascend_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@bmo_ascend_id, 'TRAVEL', 0.05, 1250, '5x BMO points on travel (up to $15,000/year)'),
(@bmo_ascend_id, 'DINING', 0.03, 833, '3x BMO points on dining (up to $10,000/year)'),
(@bmo_ascend_id, 'ENTERTAINMENT', 0.03, 833, '3x BMO points on entertainment (up to $10,000/year)'),
(@bmo_ascend_id, 'RECURRING', 0.03, 833, '3x BMO points on recurring bills (up to $10,000/year)');


-- Retail Store Cards
-- ============================================

-- Walmart Rewards Mastercard
-- No annual fee, 3% Walmart, 1% everywhere else (Updated Sept 2025)
-- Card color: silver
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Walmart', 'Rewards Mastercard', 'MASTERCARD', 0, 0.01, '{"bonusAmount": 25, "minSpend": 75, "daysToComplete": 30, "description": "$25 Welcome Bonus"}', '{"gradient": "linear-gradient(135deg, #d1d5db 0%, #6b7280 100%)", "textColor": "#1f2937"}', 'https://www.walmartrewards.ca/en', false, true);

SET @walmart_mc_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@walmart_mc_id, 'RETAIL', 0.03, NULL, '3% Walmart Reward Dollars at Walmart stores & walmart.ca');

-- MBNA Amazon.ca Rewards Mastercard
-- No annual fee, 2.5% Amazon/Whole Foods (Prime), 1.5% non-Prime, 1% other
-- 2.5% FX fee but 2.5% rewards on foreign purchases (effectively offsets FX fee for Prime)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('MBNA', 'Amazon.ca Rewards Mastercard', 'MASTERCARD', 0, 0.01, '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": "5% back first 6 months on $3000 at Amazon/grocery/dining"}', NULL, 'https://www.mbna.ca/en/credit-cards/retail-store/amazon-rewards-mastercard', false, true);

SET @amazon_mc_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@amazon_mc_id, 'ONLINE_SHOPPING', 0.025, NULL, '2.5% at Amazon.ca & Whole Foods (Prime members)'),
(@amazon_mc_id, 'FOREIGN', 0.025, NULL, '2.5% on foreign purchases (offsets 2.5% FX fee)');


-- Credit Union Cards
-- ============================================

-- Meridian Visa Infinite Cash Back (Ontario)
-- $99/year (first year waived), 4% gas/grocery, 2% pharmacy/utility, 1% other
-- Card color: blue to black gradient
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Meridian', 'Visa Infinite Cash Back', 'VISA', 99.00, 0.01, '{"bonusAmount": 7000, "minSpend": 0, "daysToComplete": 0, "description": "7,000 bonus points + first year fee waived"}', '{"gradient": "linear-gradient(135deg, #3b82f6 0%, #1e3a8a 50%, #0f172a 100%)", "textColor": "white"}', 'https://www.meridiancu.ca/personal/credit-cards/meridian-visa-infinite-cash-back-card', false, true);

SET @meridian_vi_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@meridian_vi_id, 'GAS', 0.04, 2083, '4% on gas (up to $25,000/year combined)'),
(@meridian_vi_id, 'GROCERY', 0.04, 2083, '4% on groceries (up to $25,000/year combined)'),
(@meridian_vi_id, 'PHARMACY', 0.02, 2083, '2% on pharmacy (up to $25,000/year combined)'),
(@meridian_vi_id, 'RECURRING', 0.02, 2083, '2% on utility bills (up to $25,000/year combined)');

-- Meridian Visa Cash Back (No Fee)
-- No annual fee, 1% on everything
-- Card color: white to blue gradient
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Meridian', 'Visa Cash Back', 'VISA', 0, 0.01, NULL, '{"gradient": "linear-gradient(135deg, #ffffff 0%, #3b82f6 100%)", "textColor": "#1e40af"}', 'https://www.meridiancu.ca/personal/credit-cards/meridian-visa-cash-back-card', false, true);

-- Coast Capital Cash Back Mastercard (BC)
-- No annual fee, 1% on bonus categories, 0.5% other
-- Card color: left gray-white, top-right blue, bottom-right green
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('Coast Capital', 'Cash Back Mastercard', 'MASTERCARD', 0, 0.005, NULL, '{"gradient": "linear-gradient(135deg, #e5e7eb 0%, #e5e7eb 40%, #0066cc 70%, #22c55e 100%)", "textColor": "#1f2937"}', 'https://www.coastcapitalsavings.com/everyday-banking/credit-cards', false, true);

SET @coast_mc_id = LAST_INSERT_ID();

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@coast_mc_id, 'GROCERY', 0.01, 417, '1% on groceries (up to $5,000/year)'),
(@coast_mc_id, 'GAS', 0.01, 417, '1% on gas (up to $5,000/year)'),
(@coast_mc_id, 'TRANSIT', 0.01, 417, '1% on transit (up to $5,000/year)'),
(@coast_mc_id, 'STREAMING', 0.01, 417, '1% on streaming (up to $5,000/year)'),
(@coast_mc_id, 'RECURRING', 0.01, 417, '1% on recurring bills (up to $5,000/year)');


-- ============================================
-- Summary of new cards added (Verified & Updated 2025-12-15):
-- ============================================
-- 1. Wealthsimple Visa Infinite - $240/yr ($20/mo), 2% unlimited, no FX fee
-- 2. Desjardins Cash Back World Elite - $100/yr, 4% grocery, $100 bonus
-- 3. Desjardins Cash Back Mastercard - No fee, 1.5% grocery
-- 4. Triangle World Elite Mastercard - No fee, 4% CT, 3% grocery
-- 5. Triangle Mastercard - No fee, 4% CT stores
-- 6. Vancity enviro Visa Infinite - $120/yr, 5% transit, 2.5% grocery (BC), up to $540 bonus
-- 7. Vancity enviro Visa Classic - No fee, 1% back (BC)
-- 8. CIBC Adapta Mastercard - No fee, 1.5x on top 3 categories (auto), $40K cap
-- 9. RBC ION+ Visa - $48/yr, 3x grocery/dining/gas/streaming
-- 10. BMO Ascend World Elite - $150/yr, 5x travel, 3x dining
-- 11. Walmart Rewards Mastercard - No fee, 3% Walmart
-- 12. MBNA Amazon.ca Rewards - No fee, 2.5% Amazon (Prime)
-- 13. Meridian Visa Infinite Cash Back - $99/yr (1st yr waived), 4% gas/grocery, 7K bonus (Ontario)
-- 14. Meridian Visa Cash Back - No fee, 1% (Ontario)
-- 15. Coast Capital Cash Back Mastercard - No fee, 1% categories (BC)
-- ============================================
