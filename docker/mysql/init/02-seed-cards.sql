-- SaveVia Seed Data - Canadian Credit Cards
-- Updated December 2025 with verified rates

-- ============================================
-- AMEX Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('AMEX', 'Cobalt Card', 'AMEX', 191.88, 0.01, '{"bonusAmount": 15000, "minSpend": 750, "daysToComplete": 30, "description": "1,250 MR points/month when spending $750+, for 12 months"}', true),
('AMEX', 'Gold Rewards Card', 'AMEX', 150.00, 0.01, '{"bonusAmount": 40000, "minSpend": 3000, "daysToComplete": 90}', true),
('AMEX', 'Platinum Card', 'AMEX', 799.00, 0.01, '{"bonusAmount": 80000, "minSpend": 6000, "daysToComplete": 90, "description": "80,000 MR points + $200 travel credit"}', true),
('AMEX', 'SimplyCash Preferred', 'AMEX', 119.88, 0.02, '{"bonusAmount": 250, "minSpend": 2000, "daysToComplete": 90, "description": "10% cashback first 3 months up to $2000 + $50 credit in month 13"}', true),
('AMEX', 'SimplyCash', 'AMEX', 0, 0.0125, NULL, true),
('AMEX', 'Aeroplan Card', 'AMEX', 120.00, 0.01, '{"bonusAmount": 30000, "minSpend": 1500, "daysToComplete": 90}', true),
('AMEX', 'Aeroplan Reserve Card', 'AMEX', 599.00, 0.015, '{"bonusAmount": 90000, "minSpend": 6000, "daysToComplete": 90}', true);

-- ============================================
-- TD Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('TD', 'Cash Back Visa Infinite', 'VISA', 139.00, 0.01, '{"bonusAmount": 350, "minSpend": 3500, "daysToComplete": 90, "description": "10% cashback first 3 months on bonus categories"}', true),
('TD', 'First Class Visa Infinite', 'VISA', 139.00, 0.015, '{"bonusAmount": 40000, "minSpend": 1000, "daysToComplete": 90}', true),
('TD', 'Aeroplan Visa Infinite', 'VISA', 139.00, 0.01, '{"bonusAmount": 30000, "minSpend": 1500, "daysToComplete": 90}', true),
('TD', 'Aeroplan Visa Infinite Privilege', 'VISA', 599.00, 0.015, '{"bonusAmount": 80000, "minSpend": 6000, "daysToComplete": 90}', true),
('TD', 'Cash Back Visa', 'VISA', 0, 0.0075, NULL, true);

-- ============================================
-- RBC Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('RBC', 'Avion Visa Infinite', 'VISA', 120.00, 0.01, '{"bonusAmount": 35000, "minSpend": 5000, "daysToComplete": 90}', true),
('RBC', 'Avion Visa Infinite Privilege', 'VISA', 175.00, 0.0125, '{"bonusAmount": 55000, "minSpend": 5000, "daysToComplete": 90}', true),
('RBC', 'WestJet World Elite Mastercard', 'MASTERCARD', 139.00, 0.015, '{"bonusAmount": 30000, "minSpend": 5000, "daysToComplete": 90, "description": "30,000 WestJet points + companion voucher"}', true),
('RBC', 'Cash Back Mastercard', 'MASTERCARD', 0, 0.01, NULL, true),
('RBC', 'ION Visa', 'VISA', 0, 0.01, NULL, true);

-- ============================================
-- Scotiabank Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Scotiabank', 'Gold American Express', 'AMEX', 120.00, 0.01, '{"bonusAmount": 40000, "minSpend": 1000, "daysToComplete": 90}', true),
('Scotiabank', 'Passport Visa Infinite', 'VISA', 150.00, 0.01, '{"bonusAmount": 35000, "minSpend": 2000, "daysToComplete": 90, "description": "No FX fee + 35,000 Scene+ points"}', true),
('Scotiabank', 'Momentum Visa Infinite', 'VISA', 120.00, 0.01, '{"bonusAmount": 200, "minSpend": 2000, "daysToComplete": 90, "description": "10% cashback first 3 months up to $2000"}', true),
('Scotiabank', 'Scene+ Visa', 'VISA', 0, 0.01, NULL, true);

-- ============================================
-- CIBC Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('CIBC', 'Aventura Visa Infinite', 'VISA', 139.00, 0.015, '{"bonusAmount": 20000, "minSpend": 3000, "daysToComplete": 120}', true),
('CIBC', 'Aventura Visa Infinite Privilege', 'VISA', 499.00, 0.02, '{"bonusAmount": 50000, "minSpend": 7500, "daysToComplete": 120}', true),
('CIBC', 'Aeroplan Visa Infinite', 'VISA', 139.00, 0.01, '{"bonusAmount": 30000, "minSpend": 3000, "daysToComplete": 120}', true),
('CIBC', 'Dividend Visa Infinite', 'VISA', 120.00, 0.01, '{"bonusAmount": 10, "minSpend": 2500, "daysToComplete": 120}', true),
('CIBC', 'Costco Mastercard', 'MASTERCARD', 0, 0.01, NULL, true);

-- ============================================
-- BMO Cards
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('BMO', 'Eclipse Visa Infinite', 'VISA', 120.00, 0.01, '{"bonusAmount": 50000, "minSpend": 3000, "daysToComplete": 90}', true),
('BMO', 'CashBack World Elite Mastercard', 'MASTERCARD', 120.00, 0.015, '{"bonusAmount": 335, "minSpend": 3000, "daysToComplete": 90, "description": "10% cashback first 3 months + $120 fee waived year 1"}', true),
('BMO', 'Air Miles World Elite Mastercard', 'MASTERCARD', 120.00, 0.01, '{"bonusAmount": 3000, "minSpend": 3000, "daysToComplete": 90, "description": "3,000 AIR MILES Bonus Miles"}', true),
('BMO', 'CashBack Mastercard', 'MASTERCARD', 0, 0.005, NULL, true);

-- ============================================
-- Rogers Bank
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Rogers', 'World Elite Mastercard', 'MASTERCARD', 0, 0.015, '{"bonusAmount": 25, "minSpend": 500, "daysToComplete": 90, "description": "$25 bonus on first $500 spent"}', true),
('Rogers', 'Platinum Mastercard', 'MASTERCARD', 0, 0.01, NULL, true);

-- ============================================
-- Tangerine
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Tangerine', 'Money-Back Credit Card', 'MASTERCARD', 0, 0.005, '{"bonusAmount": 50, "minSpend": 1000, "daysToComplete": 60, "description": "$50 bonus + 15% cashback on first $1000"}', true),
('Tangerine', 'World Mastercard', 'MASTERCARD', 0, 0.005, '{"bonusAmount": 50, "minSpend": 1000, "daysToComplete": 60}', true);

-- ============================================
-- Neo Financial
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Neo', 'World Elite Mastercard', 'MASTERCARD', 125.00, 0.01, '{"bonusAmount": 50, "minSpend": 500, "daysToComplete": 90, "description": "$50 welcome bonus"}', true),
('Neo', 'World Mastercard', 'MASTERCARD', 0, 0.005, '{"bonusAmount": 25, "minSpend": 500, "daysToComplete": 90}', true);

-- ============================================
-- PC Financial
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('PC Financial', 'World Elite Mastercard', 'MASTERCARD', 0, 0.01, '{"bonusAmount": 20000, "minSpend": 1000, "daysToComplete": 30, "description": "20,000 PC Optimum points"}', true),
('PC Financial', 'World Mastercard', 'MASTERCARD', 0, 0.01, NULL, true);

-- ============================================
-- Simplii Financial
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Simplii', 'Cash Back Visa Card', 'VISA', 0, 0.005, '{"bonusAmount": 200, "minSpend": 5000, "daysToComplete": 120, "description": "$200 + 10% cashback on first $5000"}', true);

-- ============================================
-- MBNA
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('MBNA', 'Rewards World Elite Mastercard', 'MASTERCARD', 120.00, 0.01, '{"bonusAmount": 20000, "minSpend": 2000, "daysToComplete": 90, "description": "20,000 MBNA Rewards Points"}', true),
('MBNA', 'True Line Gold Mastercard', 'MASTERCARD', 39.00, 0.0, NULL, true);

-- ============================================
-- National Bank
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('National Bank', 'World Elite Mastercard', 'MASTERCARD', 150.00, 0.02, '{"bonusAmount": 30000, "minSpend": 1500, "daysToComplete": 90}', true);

-- ============================================
-- Home Trust
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, is_active) VALUES
('Home Trust', 'Preferred Visa', 'VISA', 0, 0.01, NULL, true);

-- ============================================
-- REWARD RULES
-- ============================================

-- AMEX Cobalt Card (ID 1)
-- 5x on dining/grocery (up to $2500/month), 3x streaming, 2x gas/transit
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'DINING', 0.05, 2500, '5x points on dining (up to $2,500/month)'),
(1, 'GROCERY', 0.05, 2500, '5x points on groceries (up to $2,500/month)'),
(1, 'STREAMING', 0.03, NULL, '3x points on streaming'),
(1, 'TRAVEL', 0.02, NULL, '2x points on travel booked via Amex Travel'),
(1, 'TRANSIT', 0.02, NULL, '2x points on transit & rideshare'),
(1, 'GAS', 0.02, NULL, '2x points on gas');

-- AMEX Gold Rewards (ID 2)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(2, 'TRAVEL', 0.02, NULL, '2x points on travel'),
(2, 'GAS', 0.02, NULL, '2x points on gas');

-- AMEX Platinum Card (ID 3)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(3, 'TRAVEL', 0.02, NULL, '2x points on travel'),
(3, 'DINING', 0.02, NULL, '2x points on dining');

-- AMEX SimplyCash Preferred (ID 4)
-- 4% on gas/grocery (up to $30,000 combined), 2% on everything else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(4, 'GROCERY', 0.04, 2500, '4% on groceries (up to $30,000/year combined with gas)'),
(4, 'GAS', 0.04, 2500, '4% on gas (up to $30,000/year combined with grocery)');

-- AMEX Aeroplan Card (ID 6)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(6, 'TRAVEL', 0.02, NULL, '2x points on Air Canada & travel'),
(6, 'DINING', 0.015, NULL, '1.5x points on dining'),
(6, 'GROCERY', 0.015, NULL, '1.5x points on groceries');

-- AMEX Aeroplan Reserve Card (ID 7)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(7, 'TRAVEL', 0.03, NULL, '3x points on Air Canada & travel'),
(7, 'DINING', 0.02, NULL, '2x points on dining'),
(7, 'GROCERY', 0.02, NULL, '2x points on groceries');

-- TD Cash Back Visa Infinite (ID 8)
-- 3% on grocery, gas, transit, recurring, streaming
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'GROCERY', 0.03, 1250, '3% on groceries (up to $15,000/year)'),
(8, 'GAS', 0.03, 1250, '3% on gas & EV charging (up to $15,000/year)'),
(8, 'TRANSIT', 0.03, 1250, '3% on public transit (up to $15,000/year)'),
(8, 'RECURRING', 0.03, 1250, '3% on recurring bills (up to $15,000/year)'),
(8, 'STREAMING', 0.03, 1250, '3% on streaming & digital media (up to $15,000/year)');

-- TD Aeroplan Visa Infinite (ID 10)
-- 1.5x on gas/grocery/Air Canada, 1x else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(10, 'TRAVEL', 0.015, NULL, '1.5x Aeroplan points on Air Canada'),
(10, 'GROCERY', 0.015, NULL, '1.5x Aeroplan points on groceries'),
(10, 'GAS', 0.015, NULL, '1.5x Aeroplan points on gas');

-- TD Aeroplan Visa Infinite Privilege (ID 11)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(11, 'TRAVEL', 0.025, NULL, '2.5x points on Air Canada'),
(11, 'GROCERY', 0.015, NULL, '1.5x points on groceries'),
(11, 'DINING', 0.015, NULL, '1.5x points on dining');

-- RBC Avion Visa Infinite (ID 13)
-- 1.25x on travel, 1x else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(13, 'TRAVEL', 0.0125, NULL, '1.25x Avion points on travel');

-- RBC Avion Visa Infinite Privilege (ID 14)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(14, 'TRAVEL', 0.02, NULL, '2x Avion points on travel'),
(14, 'DINING', 0.015, NULL, '1.5x Avion points on dining');

-- RBC WestJet World Elite (ID 15)
-- 2x on WestJet/restaurants/streaming, 1.5x on everything else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(15, 'TRAVEL', 0.02, NULL, '2x WestJet points on WestJet flights'),
(15, 'DINING', 0.02, NULL, '2x WestJet points on restaurants'),
(15, 'STREAMING', 0.02, NULL, '2x WestJet points on streaming/subscriptions');

-- Scotiabank Passport Visa Infinite (ID 19)
-- 3x at Sobeys/Safeway/IGA, 2x grocery/dining/entertainment/transit, 1x else, NO FX fee
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(19, 'GROCERY', 0.02, NULL, '2x Scene+ points on groceries (3x at Sobeys/Safeway/IGA)'),
(19, 'DINING', 0.02, NULL, '2x Scene+ points on dining'),
(19, 'TRANSIT', 0.02, NULL, '2x Scene+ points on transit');

-- Scotiabank Momentum Visa Infinite (ID 20)
-- 4% on grocery & recurring (up to $25,000/year), 2% on gas & transit
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'GROCERY', 0.04, 2083, '4% on groceries (up to $25,000/year)'),
(20, 'RECURRING', 0.04, 2083, '4% on recurring bills (up to $25,000/year)'),
(20, 'GAS', 0.02, 2083, '2% on gas (up to $25,000/year)'),
(20, 'TRANSIT', 0.02, 2083, '2% on transit & rideshare (up to $25,000/year)');

-- CIBC Aventura Visa Infinite (ID 22)
-- 2x CIBC travel, 1.5x gas/grocery/pharmacy, 1x else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(22, 'TRAVEL', 0.02, NULL, '2x Aventura points via CIBC Rewards Centre'),
(22, 'GROCERY', 0.015, NULL, '1.5x Aventura points on groceries'),
(22, 'GAS', 0.015, NULL, '1.5x Aventura points on gas'),
(22, 'PHARMACY', 0.015, NULL, '1.5x Aventura points on drugstores');

-- CIBC Aventura Visa Infinite Privilege (ID 23)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(23, 'TRAVEL', 0.025, NULL, '2.5x Aventura points via CIBC Rewards Centre'),
(23, 'GROCERY', 0.0175, NULL, '1.75x Aventura points on groceries'),
(23, 'GAS', 0.0175, NULL, '1.75x Aventura points on gas'),
(23, 'PHARMACY', 0.0175, NULL, '1.75x Aventura points on drugstores');

-- CIBC Aeroplan Visa Infinite (ID 24)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(24, 'TRAVEL', 0.015, NULL, '1.5x points on Air Canada'),
(24, 'GROCERY', 0.015, NULL, '1.5x points on groceries'),
(24, 'GAS', 0.015, NULL, '1.5x points on gas');

-- CIBC Dividend Visa Infinite (ID 25)
-- 4% on grocery & gas, 2% on transit, dining, recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'GROCERY', 0.04, 1667, '4% on groceries (up to $20,000/year)'),
(25, 'GAS', 0.04, 1667, '4% on gas & EV charging (up to $20,000/year)'),
(25, 'TRANSIT', 0.02, 1667, '2% on transit (up to $20,000/year)'),
(25, 'DINING', 0.02, 1667, '2% on dining (up to $20,000/year)'),
(25, 'RECURRING', 0.02, 1667, '2% on recurring bills (up to $20,000/year)');

-- CIBC Costco Mastercard (ID 26)
-- 3% on restaurants (unlimited), 3% Costco gas / 2% other gas
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(26, 'DINING', 0.03, NULL, '3% on restaurants (unlimited)'),
(26, 'GAS', 0.03, 417, '3% at Costco gas, 2% other gas (up to $5,000/year)'),
(26, 'ONLINE_SHOPPING', 0.02, 667, '2% on Costco.ca (up to $8,000/year)');

-- BMO CashBack World Elite Mastercard (ID 28)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'GROCERY', 0.05, 500, '5% on groceries (up to $500/month)'),
(28, 'TRANSIT', 0.04, 300, '4% on transit (up to $300/month)'),
(28, 'GAS', 0.03, 300, '3% on gas (up to $300/month)'),
(28, 'RECURRING', 0.02, 500, '2% on recurring bills (up to $500/month)');

-- BMO Air Miles World Elite (ID 29)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(29, 'GROCERY', 0.03, NULL, '3x Air Miles on groceries'),
(29, 'TRANSIT', 0.03, NULL, '3x Air Miles on transit'),
(29, 'GAS', 0.02, NULL, '2x Air Miles on gas');

-- Rogers World Elite Mastercard (ID 31)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(31, 'TRAVEL', 0.03, NULL, '3% on foreign currency purchases');

-- Tangerine Money-Back Credit Card (ID 33)
-- 2% on up to 3 categories
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'GROCERY', 0.02, NULL, '2% on groceries (if selected)'),
(33, 'GAS', 0.02, NULL, '2% on gas (if selected)'),
(33, 'DINING', 0.02, NULL, '2% on restaurants (if selected)');

-- Neo World Elite Mastercard (ID 35)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'GROCERY', 0.05, NULL, '5% on groceries'),
(35, 'RECURRING', 0.04, NULL, '4% on recurring bills'),
(35, 'GAS', 0.03, NULL, '3% on gas');

-- Neo World Mastercard (ID 36)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(36, 'GROCERY', 0.02, NULL, '2% on groceries'),
(36, 'GAS', 0.02, NULL, '2% on gas'),
(36, 'RECURRING', 0.02, NULL, '2% on recurring payments');

-- PC Financial World Elite Mastercard (ID 37)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(37, 'GROCERY', 0.03, NULL, '30 PC Optimum points per $1 at Loblaw stores (~3%)'),
(37, 'PHARMACY', 0.045, NULL, '45 PC Optimum points per $1 at Shoppers (~4.5%)');

-- Simplii Cash Back Visa (ID 39)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(39, 'DINING', 0.04, NULL, '4% on restaurants'),
(39, 'GROCERY', 0.015, NULL, '1.5% on groceries'),
(39, 'GAS', 0.015, NULL, '1.5% on gas'),
(39, 'PHARMACY', 0.015, NULL, '1.5% on pharmacies');

-- MBNA Rewards World Elite (ID 40)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(40, 'DINING', 0.05, NULL, '5x points on restaurants'),
(40, 'GROCERY', 0.05, NULL, '5x points on groceries'),
(40, 'STREAMING', 0.05, NULL, '5x points on digital media'),
(40, 'RECURRING', 0.05, NULL, '5x points on household utilities');

-- National Bank World Elite (ID 42)
-- 5x grocery/restaurant (up to $2500/month), 2x gas/recurring/travel, 1x else
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'GROCERY', 0.05, 2500, '5x points on groceries (up to $2,500/month)'),
(42, 'DINING', 0.05, 2500, '5x points on restaurants (up to $2,500/month)'),
(42, 'GAS', 0.02, NULL, '2x points on gas'),
(42, 'RECURRING', 0.02, NULL, '2x points on recurring bills'),
(42, 'TRAVEL', 0.02, NULL, '2x points on travel');

-- Home Trust Preferred Visa (ID 43)
-- No FX fee, 1% on everything
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(43, 'TRAVEL', 0.01, NULL, '1% on all purchases + no foreign transaction fees');
