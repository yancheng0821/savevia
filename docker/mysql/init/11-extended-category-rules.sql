-- SaveVia Extended Categories Update
-- Adds reward rules for new categories: RETAIL, ENTERTAINMENT, PERSONAL_SERVICES,
-- HOME_IMPROVEMENT, WHOLESALE, INSURANCE, TELECOM, EV_CHARGING
-- Generated: 2025-12-11

-- ============================================
-- Update existing cards with new category rules
-- ============================================

-- AMEX Cobalt (ID 1) - Add ENTERTAINMENT and PERSONAL_SERVICES
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'ENTERTAINMENT', 0.02, NULL, '2x points on entertainment');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'PERSONAL_SERVICES', 0.05, 2500, '5x points on personal services (beauty, spa)');

-- TD Cash Back Visa Infinite (ID 8) - Add EV_CHARGING and TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'EV_CHARGING', 0.03, 1250, '3% on EV charging (up to $15,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'TELECOM', 0.03, 1250, '3% on telecom (up to $15,000/year)');

-- Scotiabank Passport (ID 19) - Add ENTERTAINMENT
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(19, 'ENTERTAINMENT', 0.02, NULL, '2x Scene+ points on entertainment');

-- Scotiabank Momentum (ID 20) - Add EV_CHARGING, TELECOM, INSURANCE, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'EV_CHARGING', 0.02, 2083, '2% on EV charging (up to $25,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'TELECOM', 0.04, 2083, '4% on telecom (up to $25,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'INSURANCE', 0.04, 2083, '4% on insurance (up to $25,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'STREAMING', 0.04, 2083, '4% on streaming (up to $25,000/year)');

-- CIBC Dividend Visa Infinite (ID 25) - Add EV_CHARGING, TELECOM, STREAMING, INSURANCE
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'EV_CHARGING', 0.04, 1667, '4% on EV charging (up to $20,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'TELECOM', 0.02, 1667, '2% on telecom (up to $20,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'STREAMING', 0.02, 1667, '2% on streaming (up to $20,000/year)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'INSURANCE', 0.02, 1667, '2% on insurance (up to $20,000/year)');

-- BMO CashBack World Elite (ID 28) - Add EV_CHARGING, TELECOM, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'EV_CHARGING', 0.03, 300, '3% on EV charging (up to $300/month)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'TELECOM', 0.02, 500, '2% on telecom (up to $500/month)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'STREAMING', 0.02, 500, '2% on streaming (up to $500/month)');

-- Rogers World Elite (ID 31) - Add TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(31, 'TELECOM', 0.03, NULL, '3% on Rogers/Fido/Shaw services');

-- Neo World Elite (ID 35) - Add EV_CHARGING, TELECOM, INSURANCE, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'EV_CHARGING', 0.03, NULL, '3% on EV charging');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'TELECOM', 0.04, NULL, '4% on telecom/internet');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'INSURANCE', 0.04, NULL, '4% on insurance');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'STREAMING', 0.04, NULL, '4% on streaming');

-- Neo World Mastercard (ID 36) - Add EV_CHARGING, TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(36, 'EV_CHARGING', 0.02, NULL, '2% on EV charging');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(36, 'TELECOM', 0.02, NULL, '2% on telecom/internet');

-- PC Financial World Elite (ID 37) - Add RETAIL
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(37, 'RETAIL', 0.01, NULL, '10 PC Optimum points per $1 at other retail');

-- Simplii Cash Back (ID 39) - Add RECURRING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(39, 'RECURRING', 0.015, NULL, '1.5% on pre-authorized payments');

-- MBNA Rewards World Elite (ID 40) - Add TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(40, 'TELECOM', 0.05, NULL, '5x points on telecom');

-- National Bank World Elite (ID 42) - Add TELECOM, INSURANCE, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'TELECOM', 0.02, NULL, '2x points on telecom');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'INSURANCE', 0.02, NULL, '2x points on insurance');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'STREAMING', 0.02, NULL, '2x points on streaming');

-- Tangerine Money-Back (ID 33) - Add more selectable categories
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'RECURRING', 0.02, NULL, '2% on recurring bills (if selected)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'PHARMACY', 0.02, NULL, '2% on pharmacy (if selected)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'ENTERTAINMENT', 0.02, NULL, '2% on entertainment (if selected)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'HOME_IMPROVEMENT', 0.02, NULL, '2% on home improvement (if selected)');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'TRANSIT', 0.02, NULL, '2% on public transit (if selected)');

-- AMEX SimplyCash Preferred (ID 4) - Add EV_CHARGING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(4, 'EV_CHARGING', 0.04, 2500, '4% on EV charging (up to $30,000/year combined with gas)');

-- RBC WestJet World Elite (ID 15) - Add ENTERTAINMENT
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(15, 'ENTERTAINMENT', 0.02, NULL, '2x WestJet points on entertainment');

-- CIBC Costco Mastercard (ID 26) - Add WHOLESALE
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(26, 'WHOLESALE', 0.02, 667, '2% at Costco (up to $8,000/year)');

-- ============================================
-- Update no_fx_fee for cards that have it
-- ============================================
UPDATE credit_cards SET no_fx_fee = true WHERE id = 19; -- Scotiabank Passport
UPDATE credit_cards SET no_fx_fee = true WHERE id = 43; -- Home Trust Preferred

-- ============================================
-- Add RETAIL as catch-all for general shopping cards
-- ============================================

-- Cards with good general rewards that apply to retail
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'RETAIL', 0.01, NULL, '1x points on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(4, 'RETAIL', 0.02, NULL, '2% on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'RETAIL', 0.01, NULL, '1% on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'RETAIL', 0.01, NULL, '1% on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'RETAIL', 0.015, NULL, '1.5% on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(31, 'RETAIL', 0.015, NULL, '1.5% on retail shopping');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'RETAIL', 0.01, NULL, '1% on retail shopping');

-- ============================================
-- Add HOME_IMPROVEMENT for relevant cards
-- ============================================

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'HOME_IMPROVEMENT', 0.01, NULL, '1x points on home improvement');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(4, 'HOME_IMPROVEMENT', 0.02, NULL, '2% on home improvement');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'HOME_IMPROVEMENT', 0.01, NULL, '1% on home improvement');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'HOME_IMPROVEMENT', 0.015, NULL, '1.5% on home improvement');

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'HOME_IMPROVEMENT', 0.01, NULL, '1% on home improvement');
