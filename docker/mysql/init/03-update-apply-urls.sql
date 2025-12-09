-- Update apply URLs for credit cards
-- Note: These are official bank product pages

-- AMEX Cards
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/' WHERE bank = 'AMEX' AND name = 'Cobalt Card';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/gold-rewards-card/' WHERE bank = 'AMEX' AND name = 'Gold Rewards Card';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/platinum-card/' WHERE bank = 'AMEX' AND name = 'Platinum Card';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/simply-cash-preferred/' WHERE bank = 'AMEX' AND name = 'SimplyCash Preferred';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/simply-cash/' WHERE bank = 'AMEX' AND name = 'SimplyCash';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/aeroplan-card/' WHERE bank = 'AMEX' AND name = 'Aeroplan Card';
UPDATE credit_cards SET apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/aeroplan-reserve/' WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card';

-- TD Cards
UPDATE credit_cards SET apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card' WHERE bank = 'TD' AND name = 'Cash Back Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/travel-rewards/first-class-travel-visa-infinite-card' WHERE bank = 'TD' AND name = 'First Class Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-card' WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-privilege-card' WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege';
UPDATE credit_cards SET apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-card' WHERE bank = 'TD' AND name = 'Cash Back Visa';

-- RBC Cards
UPDATE credit_cards SET apply_url = 'https://www.rbcroyalbank.com/credit-cards/travel/rbc-avion-visa-infinite.html' WHERE bank = 'RBC' AND name = 'Avion Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.rbcroyalbank.com/credit-cards/travel/rbc-avion-visa-infinite-privilege.html' WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege';
UPDATE credit_cards SET apply_url = 'https://www.rbcroyalbank.com/credit-cards/travel/rbc-westjet-world-elite-mastercard.html' WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-cash-back-mastercard.html' WHERE bank = 'RBC' AND name = 'Cash Back Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-ion-visa.html' WHERE bank = 'RBC' AND name = 'ION Visa';

-- Scotiabank Cards
UPDATE credit_cards SET apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/gold-american-express-card.html' WHERE bank = 'Scotiabank' AND name = 'Gold American Express';
UPDATE credit_cards SET apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/passport-visa-infinite-card.html' WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-visa-infinite-card.html' WHERE bank = 'Scotiabank' AND name = 'Momentum Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scene-visa-card.html' WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa';

-- CIBC Cards
UPDATE credit_cards SET apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-card.html' WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-privilege-card.html' WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege';
UPDATE credit_cards SET apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-infinite-card.html' WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/dividend-visa-infinite-card.html' WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/costco-mastercard.html' WHERE bank = 'CIBC' AND name = 'Costco Mastercard';

-- BMO Cards
UPDATE credit_cards SET apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-eclipse-visa-infinite/' WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite';
UPDATE credit_cards SET apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-cashback-world-elite-mastercard/' WHERE bank = 'BMO' AND name = 'CashBack World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-air-miles-world-elite-mastercard/' WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/' WHERE bank = 'BMO' AND name = 'CashBack Mastercard';

-- Rogers Bank
UPDATE credit_cards SET apply_url = 'https://rogersbank.com/en/rogers_world_elite_mastercard' WHERE bank = 'Rogers' AND name = 'World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://rogersbank.com/en/rogers_platinum_mastercard' WHERE bank = 'Rogers' AND name = 'Platinum Mastercard';

-- Tangerine
UPDATE credit_cards SET apply_url = 'https://www.tangerine.ca/en/products/spending/creditcard/money-back' WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card';
UPDATE credit_cards SET apply_url = 'https://www.tangerine.ca/en/products/spending/creditcard/world' WHERE bank = 'Tangerine' AND name = 'World Mastercard';

-- Neo Financial
UPDATE credit_cards SET apply_url = 'https://www.neofinancial.com/credit' WHERE bank = 'Neo' AND name = 'World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.neofinancial.com/credit' WHERE bank = 'Neo' AND name = 'World Mastercard';

-- PC Financial
UPDATE credit_cards SET apply_url = 'https://www.pcfinancial.ca/en/credit-cards/pc-money-account' WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.pcfinancial.ca/en/credit-cards/pc-money-account' WHERE bank = 'PC Financial' AND name = 'World Mastercard';

-- Simplii Financial
UPDATE credit_cards SET apply_url = 'https://www.simplii.com/en/credit-cards/cash-back-visa.html' WHERE bank = 'Simplii' AND name = 'Cash Back Visa Card';

-- MBNA
UPDATE credit_cards SET apply_url = 'https://www.mbna.ca/en/credit-cards/rewards/rewards-world-elite-mastercard/' WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard';
UPDATE credit_cards SET apply_url = 'https://www.mbna.ca/en/credit-cards/low-rate/true-line-gold-mastercard/' WHERE bank = 'MBNA' AND name = 'True Line Gold Mastercard';

-- National Bank
UPDATE credit_cards SET apply_url = 'https://www.nbc.ca/personal/credit-cards/mastercard-world-elite.html' WHERE bank = 'National Bank' AND name = 'World Elite Mastercard';

-- Home Trust
UPDATE credit_cards SET apply_url = 'https://www.hometrust.ca/credit-cards/preferred-visa-card/' WHERE bank = 'Home Trust' AND name = 'Preferred Visa';
