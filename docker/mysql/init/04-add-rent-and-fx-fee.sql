-- Add no_fx_fee column to credit_cards table
ALTER TABLE credit_cards ADD COLUMN no_fx_fee BOOLEAN DEFAULT FALSE AFTER apply_url;

-- Update no FX fee cards
UPDATE credit_cards SET no_fx_fee = TRUE WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';
UPDATE credit_cards SET no_fx_fee = TRUE WHERE bank = 'Home Trust' AND name = 'Preferred Visa';
UPDATE credit_cards SET no_fx_fee = TRUE WHERE bank = 'Rogers' AND name = 'World Elite Mastercard';
UPDATE credit_cards SET no_fx_fee = TRUE WHERE bank = 'Rogers' AND name = 'Platinum Mastercard';
UPDATE credit_cards SET no_fx_fee = TRUE WHERE bank = 'HSBC' AND name LIKE '%World Elite%';

-- Add RENT category rules
-- For cards with good RECURRING rates, RENT can often be paid via services like Plastiq
-- These cards will earn their RECURRING rate on rent payments

-- TD Cash Back Visa Infinite - 3% recurring applies to rent via Plastiq
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.03, 1250, '3% via recurring bill payment services'
FROM credit_cards WHERE bank = 'TD' AND name = 'Cash Back Visa Infinite';

-- Scotiabank Momentum Visa Infinite - 4% recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.04, 2083, '4% via recurring bill payment (up to $25,000/year)'
FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Momentum Visa Infinite';

-- BMO CashBack World Elite - 2% recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.02, 500, '2% via recurring bills (up to $500/month)'
FROM credit_cards WHERE bank = 'BMO' AND name = 'CashBack World Elite Mastercard';

-- Neo World Elite Mastercard - 4% recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.04, NULL, '4% via recurring bill payments'
FROM credit_cards WHERE bank = 'Neo' AND name = 'World Elite Mastercard';

-- CIBC Dividend Visa Infinite - 2% recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.02, 1667, '2% via recurring bills (up to $20,000/year)'
FROM credit_cards WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite';

-- MBNA Rewards World Elite - 5% recurring/utilities
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.05, NULL, '5x points on household utilities'
FROM credit_cards WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard';

-- National Bank World Elite - 2% recurring
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RENT', 0.02, NULL, '2x points on recurring bills'
FROM credit_cards WHERE bank = 'National Bank' AND name = 'World Elite Mastercard';

-- Add FOREIGN category rules for no FX fee cards
-- Scotiabank Passport - 2% on everything + no FX fee
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'FOREIGN', 0.02, NULL, '2x Scene+ points + No FX fee (save 2.5%)'
FROM credit_cards WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';

-- Home Trust Preferred - 1% + no FX fee
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'FOREIGN', 0.01, NULL, '1% cashback + No foreign transaction fees'
FROM credit_cards WHERE bank = 'Home Trust' AND name = 'Preferred Visa';

-- Rogers World Elite - 3% on foreign + no FX fee
-- Already exists, update description
UPDATE reward_rules SET description = '3% on foreign currency purchases (No FX fee - effective 5.5% savings!)'
WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'Rogers' AND name = 'World Elite Mastercard')
AND category = 'TRAVEL';

-- Add FOREIGN rule for Rogers
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'FOREIGN', 0.03, NULL, '3% cashback + No FX fee (effective 5.5% savings vs cards with FX fees)'
FROM credit_cards WHERE bank = 'Rogers' AND name = 'World Elite Mastercard';

-- Rogers Platinum - 1.75% on foreign
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'FOREIGN', 0.0175, NULL, '1.75% cashback on foreign transactions (No FX fee)'
FROM credit_cards WHERE bank = 'Rogers' AND name = 'Platinum Mastercard';
