-- ============================================
-- RBC 新增信用卡 SQL
-- 11张新卡
-- 创建时间: 2026-01-06
-- ============================================

-- ============================================
-- 1. RBC Cash Back Preferred World Elite Mastercard
-- $99 年费，1.5% unlimited cashback
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'Cash Back Preferred World Elite Mastercard', 'MASTERCARD', 99.00, 0.0150,
     '{"bonusAmount": 240, "minSpend": 2000, "daysToComplete": 90, "description": {"en": "Get 12% cash back for first 3 months on up to $2,000 purchases (max $240). Apply by March 25, 2026.", "zh": "前3个月消费最高$2,000享12%返现（最高$240）。申请截止2026年3月25日。", "fr": "12% de remise les 3 premiers mois sur achats jusqu''à 2 000$ (max 240$). Postulez avant le 25 mars 2026.", "es": "12% de reembolso los primeros 3 meses en compras hasta $2,000 (máx $240). Solicita antes del 25 marzo 2026.", "ko": "첫 3개월 최대 $2,000 구매 시 12% 캐시백 (최대 $240). 2026년 3월 25일까지 신청.", "ja": "最初の3ヶ月、最大$2,000購入で12%キャッシュバック（最大$240）。2026年3月25日まで申請可能。"}}',
     '{"gradient": "linear-gradient(135deg, #4a5654 0%, #2d3533 50%, #1f2726 100%)", "textColor": "white"}',
     'https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-preferred-world-elite-mastercard.html', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 2. RBC British Airways Visa Infinite
-- $165 年费，Avios积分
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'British Airways Visa Infinite', 'VISA', 165.00, 0.0150,
     '{"bonusAmount": 60000, "minSpend": 10000, "daysToComplete": 180, "description": {"en": "Up to 60,000 Avios: 30,000 after $5,000 in 3 months + 30,000 after $5,000 in months 4-6. Enough for a return Reward Flight to London!", "zh": "最高60,000 Avios: 3个月消费$5,000获30,000 + 4-6个月再消费$5,000获30,000. 足够往返伦敦!", "fr": "Jusqu a 60,000 Avios: 30,000 apres 5,000$ en 3 mois + 30,000 apres 5,000$ mois 4-6. Assez pour un vol aller-retour a Londres!", "es": "Hasta 60,000 Avios: 30,000 tras $5,000 en 3 meses + 30,000 tras $5,000 en meses 4-6. Suficiente para vuelo ida y vuelta a Londres!", "ko": "최대 60,000 Avios: 3개월 $5,000 후 30,000 + 4-6개월 $5,000 후 30,000. 런던 왕복 항공권 충분!", "ja": "最大60,000 Avios：3ヶ月で$5,000利用後30,000 + 4-6ヶ月で$5,000利用後30,000。ロンドン往復航空券に十分！"}}',
     '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)", "textColor": "white"}',
     'https://www.rbcroyalbank.com/credit-cards/travel/rbc-british-airways-visa-infinite.html', 0, 1, 'POINTS', 0.0150, 'British Airways Avios');

-- ============================================
-- 3. RBC U.S. Dollar Visa Gold
-- US$65 年费 (US$3,000消费返还)，无美元外汇费
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'U.S. Dollar Visa Gold', 'VISA', 65.00, 0.0100,
     '{"bonusAmount": 0, "minSpend": 3000, "daysToComplete": 365, "description": {"en": "US$65 annual fee rebated when you spend US$3,000+ annually. No FX fees on USD purchases. 1 Avion point per US$1.", "zh": "年消费满US$3,000可获US$65年费返还。美元消费无外汇费。每消费US$1获1 Avion积分。", "fr": "Frais annuels de 65$ US remboursés avec 3 000$ US+ de dépenses. Sans frais de change USD. 1 point Avion par 1$ US.", "es": "Cuota anual de US$65 reembolsada al gastar US$3,000+ al año. Sin cargo FX en USD. 1 punto Avion por US$1.", "ko": "연간 US$3,000 이상 사용 시 US$65 연회비 환급. USD 구매 시 외환 수수료 없음. US$1당 1 Avion 포인트.", "ja": "年間US$3,000以上利用でUS$65年会費キャッシュバック。USD購入時FX手数料なし。US$1で1 Avionポイント。"}}',
     '{"gradient": "linear-gradient(135deg, #d4af37 0%, #c9a227 50%, #9a7b1c 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/travel/rbc-us-dollar-visa-gold.html', 1, 1, 'POINTS', 0.0100, 'RBC Avion Rewards');

-- ============================================
-- 4. RBC Visa Platinum
-- $0 年费，基础信用卡，无奖励
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'Visa Platinum', 'VISA', 0.00, 0.0000,
     '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": {"en": "No annual fee credit card with basic benefits. Free additional cards. Purchase protection and extended warranty included.", "zh": "无年费信用卡，基础福利。附属卡免费。含购物保护和延长保修。", "fr": "Carte sans frais annuels avec avantages de base. Cartes supplémentaires gratuites. Protection achats et garantie incluses.", "es": "Tarjeta sin cuota anual con beneficios básicos. Tarjetas adicionales gratis. Protección y garantía incluidas.", "ko": "기본 혜택이 있는 무연회비 신용카드. 추가 카드 무료. 구매 보호 및 연장 보증 포함.", "ja": "基本特典付き年会費無料クレジットカード。追加カード無料。購入保護と延長保証付き。"}}',
     '{"gradient": "linear-gradient(135deg, #e5e4e2 0%, #c0c0c0 50%, #a8a8a8 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/no-fee/rbc-visa-platinum.html', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 5. RBC Visa Classic Low Rate Option
-- $20 年费，12.99% 低息
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'Visa Classic Low Rate Option', 'VISA', 20.00, 0.0000,
     '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": {"en": "Low 12.99% interest rate on purchases, cash advances and balance transfers. Current promo: 0.99% for 10 months on balance transfers + first year free.", "zh": "购物、取现、余额转账均享12.99%低利率。当前优惠：余额转账10个月0.99% + 首年免年费。", "fr": "Taux bas de 12,99% sur achats, avances et transferts. Promo: 0,99% 10 mois sur transferts + 1ère année gratuite.", "es": "Tasa baja de 12.99% en compras, adelantos y transferencias. Promo: 0.99% 10 meses + primer año gratis.", "ko": "구매, 현금서비스, 잔액이체 12.99% 저금리. 현재 프로모: 잔액이체 10개월 0.99% + 첫해 무료.", "ja": "購入・キャッシング・残高移行12.99%低金利。現在のプロモ：残高移行10ヶ月0.99% + 初年度無料。"}}',
     '{"gradient": "linear-gradient(135deg, #003168 0%, #005bbb 50%, #0073cf 100%)", "textColor": "white"}',
     'https://www.rbcroyalbank.com/credit-cards/low-interest/rbc-visa-classic-low-rate.html', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 6. RBC Avion Visa Platinum
-- $120 年费，1 Avion point per $1，无收入要求
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'Avion Visa Platinum', 'VISA', 120.00, 0.0100,
     '{"bonusAmount": 35000, "minSpend": 0, "daysToComplete": 0, "description": {"en": "Earn 35,000 Avion points upon approval - travel value up to $750. No minimum income requirement.", "zh": "开卡即获35,000 Avion积分，旅行价值最高$750。无最低收入要求。", "fr": "Gagnez 35 000 pts Avion a l''approbation - valeur voyage jusqu''a 750$. Sans exigence de revenu.", "es": "Gana 35,000 puntos Avion al aprobar - valor de viaje hasta $750. Sin requisito de ingresos.", "ko": "승인 시 35,000 Avion 포인트 - 여행 가치 최대 $750. 최소 소득 요건 없음.", "ja": "承認時35,000 Avionポイント - 旅行価値最大$750。最低収入要件なし。"}}',
     '{"gradient": "linear-gradient(135deg, #6b7280 0%, #9ca3af 50%, #6b7280 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/travel/rbc-visa-platinum-avion.html', 0, 1, 'POINTS', 0.0100, 'RBC Avion Rewards');

-- ============================================
-- 7. RBC WestJet Mastercard
-- $39 年费，WestJet积分
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'WestJet Mastercard', 'MASTERCARD', 39.00, 0.0100,
     '{"bonusAmount": 15000, "minSpend": 0, "daysToComplete": 0, "description": {"en": "Up to 15,000 WestJet points (value up to $150) upon first purchase. Plus round-trip companion voucher from $199.", "zh": "首次消费最高获15,000 WestJet积分（价值最高$150）。另加$199起同伴往返机票券。", "fr": "Jusqu a 15 000 points WestJet (valeur jusqu a 150 $) au premier achat. Plus bon accompagnateur aller-retour des 199 $.", "es": "Hasta 15,000 puntos WestJet (valor hasta $150) en primera compra. Mas voucher acompanante ida/vuelta desde $199.", "ko": "첫 구매 시 최대 15,000 WestJet 포인트 (가치 $150 까지). $199부터 동반자 왕복 바우처 포함.", "ja": "初回購入で最大15,000 WestJetポイント（価値最大$150）。$199からのコンパニオン往復バウチャー付き。"}}',
     '{"gradient": "linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/travel/westjet-rbc-mastercard.html', 0, 1, 'POINTS', 0.0100, 'WestJet Rewards');

-- ============================================
-- 8. RBC More Rewards Visa
-- $0 年费，More Rewards积分 (不适用魁北克)
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'More Rewards Visa', 'VISA', 0.00, 0.0045,
     '{"bonusAmount": 20000, "minSpend": 0, "daysToComplete": 90, "description": {"en": "20,000 welcome More Rewards points upon first purchase. 5x at Save-On-Foods partners, 5x on dining/gas, 3x other. Not available in Quebec.", "zh": "首次消费即获20,000 More Rewards积分。Save-On-Foods等合作商家5倍，餐饮/加油5倍，其他3倍。魁北克不适用。", "fr": "20 000 pts More Rewards au premier achat. 5x chez partenaires Save-On-Foods, 5x resto/essence, 3x autre. Non disponible au Québec.", "es": "20,000 puntos More Rewards en primera compra. 5x en socios Save-On-Foods, 5x comida/gas, 3x otro. No disponible en Quebec.", "ko": "첫 구매 시 20,000 More Rewards 포인트. Save-On-Foods 파트너 5배, 식당/주유 5배, 기타 3배. 퀘벡 불가.", "ja": "初回購入で20,000 More Rewardsポイント。Save-On-Foodsパートナー5倍、飲食/ガス5倍、他3倍。ケベック不可。"}}',
     '{"gradient": "linear-gradient(135deg, #c0c0c0 0%, #4a90c0 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/rewards/more-rewards-rbc-visa.html', 0, 1, 'POINTS', 0.0015, 'More Rewards');

-- ============================================
-- 9. RBC More Rewards Visa Infinite
-- $0 年费，More Rewards积分升级版 (不适用魁北克)
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'More Rewards Visa Infinite', 'VISA', 0.00, 0.0060,
     '{"bonusAmount": 20000, "minSpend": 0, "daysToComplete": 90, "description": {"en": "20,000 welcome More Rewards points. 8x at Save-On-Foods partners, 8x on dining/gas/EV, 4x other. No annual fee! Not available in Quebec.", "zh": "开卡获20,000 More Rewards积分。Save-On-Foods等合作商家8倍，餐饮/加油/充电8倍，其他4倍。免年费！魁北克不适用。", "fr": "20 000 pts More Rewards. 8x chez Save-On-Foods, 8x resto/essence/VE, 4x autre. Sans frais annuels! Non disponible au Québec.", "es": "20,000 puntos More Rewards. 8x en Save-On-Foods, 8x comida/gas/EV, 4x otro. Sin cuota anual! No disponible en Quebec.", "ko": "20,000 More Rewards 포인트. Save-On-Foods 파트너 8배, 식당/주유/EV 8배, 기타 4배. 무연회비! 퀘벡 불가.", "ja": "20,000 More Rewardsポイント。Save-On-Foodsパートナー8倍、飲食/ガス/EV8倍、他4倍。年会費無料！ケベック不可。"}}',
     '{"gradient": "linear-gradient(135deg, #1a1a2e 0%, #0d1421 100%)", "textColor": "white"}',
     'https://www.rbcroyalbank.com/credit-cards/rewards/more-rewards-rbc-visa-infinite.html', 0, 1, 'POINTS', 0.0015, 'More Rewards');

-- ============================================
-- 10. RBC RateAdvantage Visa
-- $0 年费，可变低息 (Prime + 4.99% to 8.99%)
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'RateAdvantage Visa', 'VISA', 0.00, 0.0000,
     '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": {"en": "No annual fee with variable low interest rate (Prime + 4.99% to 8.99% based on credit). The better your credit, the lower your rate.", "zh": "无年费，可变低利率（Prime + 4.99%至8.99%，根据信用评分）。信用越好，利率越低。", "fr": "Sans frais annuels avec taux variable bas (Taux préférentiel + 4,99% à 8,99% selon crédit). Meilleur crédit = taux plus bas.", "es": "Sin cuota anual con tasa variable baja (Prime + 4.99% a 8.99% según crédito). Mejor crédito = menor tasa.", "ko": "무연회비, 변동 저금리 (Prime + 4.99%~8.99%, 신용 기반). 신용이 좋을수록 금리가 낮아집니다.", "ja": "年会費無料、変動低金利（Prime + 4.99%〜8.99%、信用に基づく）。信用が良いほど金利が低くなります。"}}',
     '{"gradient": "linear-gradient(135deg, #c0c0c0 0%, #4a90c0 100%)", "textColor": "#1a1a1a"}',
     'https://www.rbcroyalbank.com/credit-cards/low-interest/rbc-rateadvantage-visa.html', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 11. moi RBC Visa
-- $0 年费，Moi积分 (魁北克/安省/新不伦瑞克)
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('RBC', 'moi RBC Visa', 'VISA', 0.00, 0.0080,
     '{"bonusAmount": 5000, "minSpend": 500, "daysToComplete": 90, "description": {"en": "3,000 welcome Moi points on first purchase + 2,000 bonus with $500 spend in 3 months. Save 3¢/L at Petro-Canada + 20% more Petro-Points.", "zh": "首次消费获3,000 Moi积分 + 3个月内消费$500获2,000奖励积分。Petro-Canada每升省3分钱 + 多赚20% Petro-Points。", "fr": "3 000 pts Moi au 1er achat + 2 000 bonus avec 500$ en 3 mois. Économisez 3¢/L chez Petro-Canada + 20% plus de Petro-Points.", "es": "3,000 puntos Moi en primera compra + 2,000 bonus con $500 en 3 meses. Ahorra 3¢/L en Petro-Canada + 20% más Petro-Points.", "ko": "첫 구매 시 3,000 Moi 포인트 + 3개월 $500 지출 시 2,000 보너스. Petro-Canada에서 리터당 3¢ 절약 + 20% 추가 Petro-Points.", "ja": "初回購入で3,000 Moiポイント + 3ヶ月で$500利用で2,000ボーナス。Petro-Canadaでリットル3¢節約 + 20%追加Petro-Points。"}}',
     '{"gradient": "linear-gradient(135deg, #9370db 0%, #7b68ee 100%)", "textColor": "white"}',
     'https://www.rbcroyalbank.com/credit-cards/rewards/moi-rbc-visa.html', 0, 1, 'POINTS', 0.0080, 'Moi');


-- ============================================
-- REWARD RULES (使用子查询获取card_id)
-- ============================================

-- Cash Back Preferred World Elite Mastercard (1.5% unlimited cashback on all purchases)
-- 因为我们用base_reward_rate表示，这里不需要额外规则

-- British Airways Visa Infinite (3x BA, 2x dining, 1x other)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.045, NULL, '3 Avios per $1 on British Airways purchases' FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.03, NULL, '2 Avios per $1 on dining and food delivery' FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

-- WestJet Mastercard (1.5x on WestJet/dining/streaming, 1x other)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.015, NULL, '1.5x points on WestJet flights, WestJet Vacations, Sunwing Vacations' FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.015, NULL, '1.5x points on restaurants and food delivery' FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'STREAMING', 0.015, NULL, '1.5x points on digital subscriptions, streaming services, digital games' FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

-- More Rewards Visa (5x grocery/pharmacy/dining/gas, 3x other)
-- point_value = 0.0015, so 5x = 0.0075, 3x base = 0.0045
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.0075, NULL, '5x points at Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare and partner locations' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'PHARMACY', 0.0075, NULL, '5x points at pharmacy and partner locations' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.0075, NULL, '5x points on dining' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.0075, NULL, '5x points on gas and EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'EV_CHARGING', 0.0075, NULL, '5x points on EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

-- More Rewards Visa Infinite (8x grocery/pharmacy/dining/gas, 4x other)
-- point_value = 0.0015, so 8x = 0.012, 4x base = 0.006
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.012, NULL, '8x points at Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare and 700+ partner locations' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'PHARMACY', 0.012, NULL, '8x points at pharmacy and partner locations' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.012, NULL, '8x points on dining' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.012, NULL, '8x points on gas and EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'EV_CHARGING', 0.012, NULL, '8x points on EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

-- moi RBC Visa (2x at Metro/partners, 2x dining/gas, 1x other)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.016, NULL, '2x Moi points at Metro, Brunet, Première Moisson, Jean Coutu with Moi card' FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.016, NULL, '2x Moi points on dining' FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.016, NULL, '2x Moi points on gas and EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'EV_CHARGING', 0.016, NULL, '2x Moi points on EV charging' FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';


-- ============================================
-- CARD USAGE TIPS (使用子查询获取card_id)
-- ============================================

-- 1. RBC Cash Back Preferred World Elite Mastercard (6条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Unlimited Cash Back", "zh": "无限返现", "fr": "Remise illimitée", "es": "Reembolso ilimitado", "ko": "무제한 캐시백", "ja": "無制限キャッシュバック"}',
    '{"en": "Earn 1.5% unlimited cash back on ALL purchases with no cap. Simple flat-rate without tracking spending categories.", "zh": "所有消费享1.5%返现，无上限。简单统一费率，无需追踪消费类别。", "fr": "Gagnez 1,5% de remise illimitée sur TOUS les achats sans plafond. Taux simple sans suivi de catégories.", "es": "Gana 1.5% de reembolso ilimitado en TODAS las compras sin tope. Tasa simple sin rastrear categorías.", "ko": "모든 구매에서 상한 없이 1.5% 무제한 캐시백. 카테고리 추적 없는 단순 정액 리워드.", "ja": "すべての購入で上限なし1.5%無制限キャッシュバック。カテゴリ追跡なしのシンプルな定額リワード。"}',
    'dollar', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Airport Lounges", "zh": "机场贵宾室", "fr": "Salons d''aéroport", "es": "Salas VIP", "ko": "공항 라운지", "ja": "空港ラウンジ"}',
    '{"en": "Free access to 1,300+ airport lounges worldwide via DragonPass. Complimentary food, drinks and WiFi while traveling.", "zh": "通过DragonPass免费使用全球1,300+机场贵宾室。旅途中享免费餐饮和WiFi。", "fr": "Accès gratuit à 1 300+ salons via DragonPass. Repas, boissons et WiFi gratuits en voyage.", "es": "Acceso gratis a 1,300+ salas vía DragonPass. Comida, bebidas y WiFi gratis al viajar.", "ko": "DragonPass로 전 세계 1,300+ 라운지 무료 이용. 여행 중 무료 음식, 음료, WiFi.", "ja": "DragonPassで世界1,300+ラウンジ無料利用。旅行中は無料の食事、ドリンク、WiFi。"}',
    'plane', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Partner Savings", "zh": "合作商家优惠", "fr": "Économies partenaires", "es": "Ahorros socios", "ko": "파트너 할인", "ja": "パートナー特典"}',
    '{"en": "Save 3¢/L at Petro-Canada + 20% bonus Petro-Points. Exclusive offers from 2,000+ brands including Rexall and DoorDash.", "zh": "Petro-Canada每升省3分+20%额外积分。Rexall、DoorDash等2,000+品牌专属优惠。", "fr": "Économisez 3¢/L chez Petro-Canada + 20% bonus Petro-Points. Offres exclusives de 2 000+ marques.", "es": "Ahorra 3¢/L en Petro-Canada + 20% bonus Petro-Points. Ofertas exclusivas de 2,000+ marcas.", "ko": "Petro-Canada에서 리터당 3¢ 절약 + 20% 보너스. 2,000+ 브랜드 특별 혜택.", "ja": "Petro-Canadaでリットル3¢節約 + 20%ボーナス。2,000+ブランドの特別オファー。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase & Rental Protection", "zh": "购物和租车保护", "fr": "Protection achats et location", "es": "Protección compras y alquiler", "ko": "구매 및 렌터카 보호", "ja": "購入＆レンタカー保護"}',
    '{"en": "90-day purchase security + extended warranty doubles manufacturer coverage. Rental car collision/loss damage insurance included.", "zh": "90天购物保护 + 延长保修将原厂保修延长一倍。含租车碰撞/损失保险。", "fr": "Protection achats 90 jours + garantie prolongée double la couverture. Assurance collision voiture de location incluse.", "es": "Protección 90 días + garantía extendida duplica cobertura. Seguro colisión/pérdida auto rentado incluido.", "ko": "90일 구매 보호 + 연장 보증으로 제조사 보증 2배. 렌터카 충돌/손실 보험 포함.", "ja": "90日購入保護 + 延長保証でメーカー保証2倍。レンタカー衝突/損害保険付き。"}',
    'shield', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "World Elite Perks", "zh": "World Elite特权", "fr": "Avantages World Elite", "es": "Beneficios World Elite", "ko": "World Elite 혜택", "ja": "World Elite特典"}',
    '{"en": "Access on-demand apps and subscription offers from Mastercard. Travel rewards cashback when shopping abroad.", "zh": "享受万事达卡的应用和订阅优惠。境外消费可获旅行返现奖励。", "fr": "Accédez aux applis et abonnements Mastercard. Récompenses voyage lors d''achats à l''étranger.", "es": "Acceso a apps y suscripciones de Mastercard. Recompensas de viaje al comprar en el extranjero.", "ko": "마스터카드 앱 및 구독 혜택 이용. 해외 쇼핑 시 여행 리워드 캐시백.", "ja": "マスターカードのアプリ・サブスク特典。海外ショッピングで旅行リワードキャッシュバック。"}',
    'star', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transactions", "zh": "外币交易", "fr": "Transactions étrangères", "es": "Transacciones extranjeras", "ko": "해외 거래", "ja": "海外取引"}',
    '{"en": "2.5% foreign transaction fee applies. Use a no-FX-fee card for international purchases.", "zh": "外币交易收取2.5%手续费。国际消费建议使用无外汇费卡。", "fr": "Frais de 2,5% sur transactions étrangères. Utilisez une carte sans frais FX pour achats internationaux.", "es": "Se aplica 2.5% en transacciones extranjeras. Usa tarjeta sin cargo FX para compras internacionales.", "ko": "해외 거래 수수료 2.5%. 해외 구매에는 FX 무료 카드 사용 권장.", "ja": "海外取引手数料2.5%。海外購入にはFX手数料なしカードを使用推奨。"}',
    'alert', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Cash Back Preferred World Elite Mastercard';

-- 2. RBC British Airways Visa Infinite (8条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "British Airways Bookings", "zh": "英航预订", "fr": "Reservations British Airways", "es": "Reservas British Airways", "ko": "British Airways 예약", "ja": "British Airways予約"}',
    '{"en": "Earn 3 Avios per $1 on BA flights, hotels and vacation packages. Plus get 10% off every BA flight when you pay with this card.", "zh": "英航机票、酒店和度假套餐每消费$1赚3 Avios。用此卡支付还可享受所有英航机票9折。", "fr": "Gagnez 3 Avios par dollar sur vols, hotels et forfaits BA. Plus 10% de rabais sur chaque vol BA paye avec cette carte.", "es": "Gana 3 Avios por $1 en vuelos, hoteles y paquetes BA. Ademas 10% descuento en cada vuelo BA pagado con esta tarjeta.", "ko": "BA 항공편, 호텔, 패키지에서 $1당 3 Avios. 이 카드로 결제 시 모든 BA 항공편 10% 할인.", "ja": "BA航空券、ホテル、パッケージで$1あたり3 Avios。このカードでBA航空券10%オフ。"}',
    'plane', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Dining & Food Delivery", "zh": "餐饮和外卖", "fr": "Restaurants et livraison", "es": "Restaurantes y delivery", "ko": "식당 및 배달", "ja": "飲食とデリバリー"}',
    '{"en": "Earn 2 Avios per $1 at restaurants and on food delivery orders. Great for everyday spending to accumulate Avios faster.", "zh": "餐厅和外卖订单每消费$1赚2 Avios。日常消费快速累积Avios的好方法。", "fr": "Gagnez 2 Avios par dollar aux restaurants et livraisons. Ideal pour accumuler des Avios au quotidien.", "es": "Gana 2 Avios por $1 en restaurantes y delivery. Excelente para acumular Avios con gastos diarios.", "ko": "식당과 배달 주문에서 $1당 2 Avios. 일상 소비로 Avios 빠르게 적립.", "ja": "レストランとデリバリーで$1あたり2 Avios。日常の支出でAviosを早く貯める。"}',
    'utensils', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "10% Flight Discount", "zh": "机票9折", "fr": "10% rabais vols", "es": "10% descuento vuelos", "ko": "항공권 10% 할인", "ja": "航空券10%オフ"}',
    '{"en": "Get 10% off every British Airways flight when you book and pay with your card. Discount applies to the base fare.", "zh": "用此卡预订并支付英航机票可享9折优惠。折扣适用于基础票价。", "fr": "10% de rabais sur chaque vol BA reserve et paye avec cette carte. Rabais sur le tarif de base.", "es": "10% descuento en cada vuelo BA al reservar y pagar con tu tarjeta. Aplica al precio base.", "ko": "이 카드로 예약 및 결제 시 모든 BA 항공편 10% 할인. 기본 운임에 적용.", "ja": "このカードで予約・支払いすればBA航空券10%オフ。基本運賃に適用。"}',
    'percent', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Companion Voucher", "zh": "同伴券", "fr": "Bon accompagnateur", "es": "Voucher acompanante", "ko": "동반자 바우처", "ja": "コンパニオンバウチャー"}',
    '{"en": "Spend $30,000 CAD annually to earn a Companion Voucher. Bring a companion OR fly solo for 50% off the Avios fare on reward seats.", "zh": "年消费$30,000 CAD即可获得同伴券。携同伴同行或单独乘机享奖励座位Avios票价5折。", "fr": "Depensez 30,000$ CAD par an pour obtenir un bon accompagnateur. Amenez un compagnon OU voyagez seul a 50% de rabais sur les sieges recompenses.", "es": "Gasta $30,000 CAD al ano para obtener un Voucher. Lleva acompanante O vuela solo con 50% descuento en asientos premio.", "ko": "연간 $30,000 CAD 사용 시 동반자 바우처 획득. 동반자 동행 또는 단독 비행 시 보상 좌석 Avios 요금 50% 할인.", "ja": "年間$30,000 CADでコンパニオンバウチャー獲得。同伴またはソロでリワード座席Avios50%オフ。"}',
    'ticket', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Flexible Avios Use", "zh": "灵活使用Avios", "fr": "Utilisation flexible Avios", "es": "Uso flexible de Avios", "ko": "유연한 Avios 사용", "ja": "Aviosを自由に使用"}',
    '{"en": "Use Avios for BA and oneworld partner flights to 1,000+ destinations, cabin upgrades, partial payment on cash tickets, hotels. Book at ba.com or call 1-800-452-1201.", "zh": "Avios可用于英航和寰宇一家伙伴航班（1,000+目的地）、舱位升级、现金票部分支付、酒店。在ba.com预订或致电1-800-452-1201。", "fr": "Utilisez Avios pour vols BA et oneworld vers 1,000+ destinations, surclassements, paiement partiel, hotels. Reservez sur ba.com ou appelez 1-800-452-1201.", "es": "Usa Avios para vuelos BA y oneworld a 1,000+ destinos, upgrades, pago parcial, hoteles. Reserva en ba.com o llama 1-800-452-1201.", "ko": "Avios로 BA 및 oneworld 파트너 항공편(1,000+ 목적지), 좌석 업그레이드, 부분 결제, 호텔 이용. ba.com 또는 1-800-452-1201.", "ja": "AviosでBAとoneworld航空便(1,000+目的地)、アップグレード、部分支払い、ホテル。ba.comか1-800-452-1201。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Comprehensive Travel Insurance", "zh": "全面旅行保险", "fr": "Assurance voyage complete", "es": "Seguro de viaje completo", "ko": "종합 여행 보험", "ja": "総合旅行保険"}',
    '{"en": "Includes emergency medical ($5M), flight delay, delayed baggage, trip cancellation, auto rental collision/loss, purchase protection and extended warranty.", "zh": "包含紧急医疗（$500万）、航班延误、行李延误、旅行取消、租车碰撞/损失、购物保护和延长保修。", "fr": "Comprend medical urgence (5M$), retard de vol, bagages retardes, annulation voyage, collision auto location, protection achats et garantie prolongee.", "es": "Incluye medico emergencia ($5M), retraso vuelo, equipaje retrasado, cancelacion viaje, colision auto alquilado, proteccion compras y garantia extendida.", "ko": "응급 의료($5M), 항공편 지연, 수하물 지연, 여행 취소, 렌터카 충돌/손실, 구매 보호, 연장 보증 포함.", "ja": "緊急医療($5M)、フライト遅延、手荷物遅延、旅行キャンセル、レンタカー保険、購入保護、延長保証。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Executive Club Benefits", "zh": "行政俱乐部会员", "fr": "Avantages Executive Club", "es": "Beneficios Executive Club", "ko": "Executive Club 혜택", "ja": "エグゼクティブクラブ特典"}',
    '{"en": "Free BA Executive Club membership with saved preferences, exclusive offers, online Avios tracking via ba.com or BA app.", "zh": "免费英航行政俱乐部会员资格，保存偏好设置，专属优惠，通过ba.com或BA应用追踪Avios。", "fr": "Adhesion gratuite au Executive Club BA avec preferences sauvegardees, offres exclusives, suivi Avios sur ba.com ou appli BA.", "es": "Membresia gratuita Executive Club BA con preferencias guardadas, ofertas exclusivas, seguimiento Avios en ba.com o app BA.", "ko": "무료 BA Executive Club 회원, 저장된 선호 설정, 독점 혜택, ba.com 또는 BA 앱에서 Avios 추적.", "ja": "無料BAエグゼクティブクラブ会員、設定保存、限定オファー、ba.comかBAアプリでAvios追跡。"}',
    'star', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transaction Fee", "zh": "外币交易手续费", "fr": "Frais de change", "es": "Cargo por transaccion extranjera", "ko": "해외 거래 수수료", "ja": "外貨取引手数料"}',
    '{"en": "2.5% foreign transaction fee applies. For non-BA international purchases, consider a no-FX-fee card instead.", "zh": "收取2.5%外币交易手续费。非英航国际消费建议使用无外汇费卡。", "fr": "Frais de change de 2,5%. Pour achats internationaux non-BA, considerez une carte sans frais de change.", "es": "Se aplica 2.5% en transacciones extranjeras. Para compras internacionales no-BA, considera una tarjeta sin cargo FX.", "ko": "해외 거래 수수료 2.5%. BA 외 해외 구매 시 FX 무료 카드 권장.", "ja": "外貨取引手数料2.5%。BA以外の海外購入にはFX無料カードを。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'British Airways Visa Infinite';

-- 3. RBC U.S. Dollar Visa Gold (8条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "U.S. Purchases", "zh": "美国消费", "fr": "Achats aux É.-U.", "es": "Compras en EE.UU.", "ko": "미국 구매", "ja": "アメリカ購入"}',
    '{"en": "No foreign exchange fees on U.S. dollar purchases. Pay in USD and avoid the typical 2.5% FX markup.", "zh": "美元消费无外汇费。以美元支付，避免通常2.5%的外汇加价。", "fr": "Aucuns frais de change sur les achats en dollars US. Payez en USD et évitez les 2,5% de majoration.", "es": "Sin cargos de cambio en compras en dólares US. Paga en USD y evita el 2.5% de cargo FX.", "ko": "미국 달러 구매 시 외환 수수료 없음. USD로 결제하여 일반적인 2.5% FX 마크업 회피.", "ja": "米ドル購入で外国為替手数料なし。USDで支払い、通常の2.5%FXマークアップを回避。"}',
    'dollar', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Cross-Border Shopping", "zh": "跨境购物", "fr": "Achats transfrontaliers", "es": "Compras transfronterizas", "ko": "국경 쇼핑", "ja": "国境越えショッピング"}',
    '{"en": "Perfect for frequent cross-border shoppers, U.S. online purchases, and U.S. subscriptions paid in USD.", "zh": "非常适合经常跨境购物者、美国在线购物和以美元支付的美国订阅服务。", "fr": "Parfait pour les acheteurs transfrontaliers, achats en ligne américains et abonnements payés en USD.", "es": "Perfecto para compradores transfronterizos, compras en línea de EE.UU. y suscripciones pagadas en USD.", "ko": "잦은 국경 쇼핑, 미국 온라인 구매, USD로 결제하는 미국 구독에 완벽.", "ja": "頻繁な国境越えショッピング、米国オンライン購入、USDで支払う米国サブスクに最適。"}',
    'cart', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Annual Fee Rebate", "zh": "年费返还", "fr": "Remise frais annuels", "es": "Reembolso de cuota", "ko": "연회비 환급", "ja": "年会費キャッシュバック"}',
    '{"en": "US$65 annual fee is rebated when you spend US$3,000 or more annually on the card.", "zh": "年消费满US$3,000即可获得US$65年费返还。", "fr": "Les frais annuels de 65$ US sont remboursés avec 3 000$ US de dépenses annuelles.", "es": "La cuota anual de US$65 se reembolsa al gastar US$3,000 o más al año.", "ko": "연간 US$3,000 이상 사용 시 US$65 연회비 환급.", "ja": "年間US$3,000以上利用でUS$65年会費キャッシュバック。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Non-USD Currencies", "zh": "非美元货币", "fr": "Devises non-USD", "es": "Monedas no-USD", "ko": "비-USD 통화", "ja": "非USD通貨"}',
    '{"en": "2.5% FX fee applies to non-USD transactions. Use a different card for purchases in other currencies.", "zh": "非美元交易收取2.5%外汇费。其他货币消费请使用其他卡。", "fr": "Frais de 2,5% sur transactions non-USD. Utilisez une autre carte pour les achats en autres devises.", "es": "Se aplica 2.5% en transacciones no-USD. Usa otra tarjeta para compras en otras monedas.", "ko": "비-USD 거래에 2.5% FX 수수료 부과. 다른 통화 구매에는 다른 카드 사용.", "ja": "非USD取引に2.5%FX手数料。他の通貨での購入には別のカードを使用。"}',
    'alert', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Partner Savings", "zh": "合作商家优惠", "fr": "Économies partenaires", "es": "Ahorros socios", "ko": "파트너 할인", "ja": "パートナー特典"}',
    '{"en": "Exclusive offers from 2,000+ brands including Petro-Canada, Rexall and DoorDash. Save 3¢/L at Petro-Canada + 20% bonus Petro-Points.", "zh": "Petro-Canada、Rexall、DoorDash等2,000+品牌专属优惠。Petro-Canada每升省3分+20%额外积分。", "fr": "Offres exclusives de 2 000+ marques dont Petro-Canada, Rexall et DoorDash. Économisez 3¢/L chez Petro-Canada + 20% bonus.", "es": "Ofertas exclusivas de 2,000+ marcas incluyendo Petro-Canada, Rexall y DoorDash. Ahorra 3¢/L en Petro-Canada + 20% bonus.", "ko": "Petro-Canada, Rexall, DoorDash 포함 2,000+ 브랜드 특별 혜택. Petro-Canada에서 리터당 3¢ 절약 + 20% 보너스.", "ja": "Petro-Canada、Rexall、DoorDash含む2,000+ブランドの特別オファー。Petro-Canadaでリットル3¢節約 + 20%ボーナス。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Flexible Avion Redemption", "zh": "灵活积分兑换", "fr": "Échange Avion flexible", "es": "Canje Avion flexible", "ko": "유연한 Avion 교환", "ja": "柔軟なAvion交換"}',
    '{"en": "Redeem for gift cards, merchandise, travel (100 pts = $1 CAD), pay your balance, investments, or convert to WestJet points. Start at 2,500 points!", "zh": "可兑换礼品卡、商品、旅行（100积分=$1 CAD）、抵扣账单、投资，或转换为WestJet积分。2,500积分起兑！", "fr": "Échangez contre cartes-cadeaux, marchandises, voyages (100 pts = 1$ CAD), payez votre solde, investissements, ou convertissez en points WestJet. Dès 2 500 pts!", "es": "Canjea por gift cards, mercancía, viajes (100 pts = $1 CAD), paga tu saldo, inversiones, o convierte a puntos WestJet. Desde 2,500 puntos!", "ko": "기프트 카드, 상품, 여행(100포인트=$1 CAD), 잔액 결제, 투자, WestJet 포인트 전환 가능. 2,500포인트부터!", "ja": "ギフトカード、商品、旅行（100pts=$1 CAD）、残高支払い、投資、WestJetポイント変換に交換可能。2,500ポイントから！"}',
    'star', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Travel Insurance", "zh": "旅行保险", "fr": "Assurance voyage", "es": "Seguro de viaje", "ko": "여행 보험", "ja": "旅行保険"}',
    '{"en": "Includes travel accident insurance, trip cancellation & interruption, flight delay, and delayed baggage coverage for peace of mind.", "zh": "包含旅行意外险、行程取消/中断险、航班延误险和行李延误险，让您出行无忧。", "fr": "Comprend assurance accident de voyage, annulation/interruption de voyage, retard de vol et bagages retardés pour votre tranquillité.", "es": "Incluye seguro de accidente de viaje, cancelación/interrupción, retraso de vuelo y equipaje retrasado para tu tranquilidad.", "ko": "여행 사고 보험, 여행 취소/중단, 항공편 지연, 수하물 지연 보장 포함으로 안심 여행.", "ja": "旅行傷害保険、旅行キャンセル/中断、フライト遅延、手荷物遅延保険で安心。"}',
    'plane', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Auto & Purchase Protection", "zh": "租车和购物保护", "fr": "Protection auto et achats", "es": "Protección auto y compras", "ko": "렌터카 및 구매 보호", "ja": "レンタカー＆購入保護"}',
    '{"en": "Auto rental collision/loss damage waiver plus purchase security and extended warranty protection on eligible purchases.", "zh": "租车碰撞/损失豁免，以及符合条件购物的购物保护和延长保修。", "fr": "Assurance collision/perte location auto plus protection achats et garantie prolongée sur achats admissibles.", "es": "Exención de colisión/pérdida de auto rentado más protección de compras y garantía extendida en compras elegibles.", "ko": "렌터카 충돌/손실 면제, 적격 구매에 대한 구매 보호 및 연장 보증.", "ja": "レンタカー衝突/損害免除、対象購入の購入保護と延長保証。"}',
    'shield', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'U.S. Dollar Visa Gold';

-- 4. RBC Visa Platinum (7条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Building Credit", "zh": "建立信用", "fr": "Bâtir son crédit", "es": "Construir crédito", "ko": "신용 구축", "ja": "信用構築"}',
    '{"en": "A solid no-fee starter card to build credit history. No rewards, but no annual fee either.", "zh": "可靠的无年费入门卡，用于建立信用记录。无奖励，但也无年费。", "fr": "Excellente carte de départ sans frais pour bâtir votre crédit. Pas de récompenses, mais pas de frais annuels.", "es": "Tarjeta inicial sin cuota para construir crédito. Sin recompensas, pero sin cuota anual.", "ko": "신용 기록을 쌓기 위한 무연회비 기본 카드. 리워드는 없지만 연회비도 없음.", "ja": "信用履歴を構築するための堅実な年会費無料スターターカード。リワードなしだが年会費もなし。"}',
    'trending-up', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Additional Cards", "zh": "免费附属卡", "fr": "Cartes supplémentaires gratuites", "es": "Tarjetas adicionales gratis", "ko": "무료 추가 카드", "ja": "追加カード無料"}',
    '{"en": "Add authorized users to your account at no extra cost. Share the card benefits with family members.", "zh": "免费为账户添加授权用户。与家人共享卡片福利。", "fr": "Ajoutez des utilisateurs autorisés sans frais supplémentaires. Partagez les avantages avec votre famille.", "es": "Agrega usuarios autorizados sin costo extra. Comparte los beneficios con tu familia.", "ko": "추가 비용 없이 승인된 사용자 추가. 가족과 카드 혜택 공유.", "ja": "追加費用なしで承認済みユーザーを追加。家族とカード特典を共有。"}',
    'users', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Avion Rewards Deals", "zh": "Avion合作优惠", "fr": "Offres Avion Rewards", "es": "Ofertas Avion Rewards", "ko": "Avion Rewards 혜택", "ja": "Avion Rewards特典"}',
    '{"en": "Access offers from 2,000+ brands including Petro-Canada, Rexall and DoorDash. Earn extra points and savings from partners.", "zh": "可使用2,000+品牌优惠，包括Petro-Canada、Rexall和DoorDash。从合作伙伴获得额外积分和折扣。", "fr": "Accédez aux offres de 2 000+ marques dont Petro-Canada, Rexall et DoorDash. Gagnez des points et économies bonus.", "es": "Accede a ofertas de 2,000+ marcas incluyendo Petro-Canada, Rexall y DoorDash. Gana puntos y ahorros extra.", "ko": "Petro-Canada, Rexall, DoorDash 포함 2,000+ 브랜드 혜택 이용. 파트너에서 추가 포인트 및 할인.", "ja": "Petro-Canada、Rexall、DoorDash含む2,000+ブランドのオファー利用可能。パートナーから追加ポイントと割引。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Travel & Auto Insurance", "zh": "旅行和租车保险", "fr": "Assurance voyage et auto", "es": "Seguro viaje y auto", "ko": "여행 및 렌터카 보험", "ja": "旅行・レンタカー保険"}',
    '{"en": "Includes travel accident insurance and auto rental collision/loss damage waiver for peace of mind when traveling.", "zh": "包含旅行意外险和租车碰撞/损失豁免，让您出行无忧。", "fr": "Comprend assurance accident de voyage et exonération collision/perte location auto pour voyager tranquille.", "es": "Incluye seguro de accidente de viaje y exención de colisión/pérdida de auto rentado para viajar tranquilo.", "ko": "여행 사고 보험과 렌터카 충돌/손실 면제 포함으로 안심 여행.", "ja": "旅行傷害保険とレンタカー衝突/損害免除で安心の旅。"}',
    'plane', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection des achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "Purchase security and extended warranty protection included even on this no-fee card.", "zh": "即使是这张无年费卡也包含购物保护和延长保修。", "fr": "Protection des achats et garantie prolongée incluses même sur cette carte sans frais.", "es": "Protección de compras y garantía extendida incluidas incluso en esta tarjeta sin cuota.", "ko": "이 무연회비 카드에도 구매 보호 및 연장 보증 포함.", "ja": "この年会費無料カードでも購入保護と延長保証が含まれます。"}',
    'shield', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Rewards Earning", "zh": "赚取奖励", "fr": "Gagner des récompenses", "es": "Ganar recompensas", "ko": "리워드 적립", "ja": "リワード獲得"}',
    '{"en": "This card offers no rewards. Consider upgrading to a rewards card if you want to earn points or cash back.", "zh": "此卡无奖励。如想赚取积分或返现，请考虑升级到奖励卡。", "fr": "Cette carte n''offre pas de récompenses. Considérez une carte récompenses pour gagner des points.", "es": "Esta tarjeta no ofrece recompensas. Considera una tarjeta con recompensas para ganar puntos.", "ko": "이 카드는 리워드가 없습니다. 포인트나 캐시백을 원하면 리워드 카드로 업그레이드 고려.", "ja": "このカードにはリワードがありません。ポイントやキャッシュバックを獲得したい場合はリワードカードへのアップグレードを検討。"}',
    'alert', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transactions", "zh": "外币交易", "fr": "Transactions étrangères", "es": "Transacciones extranjeras", "ko": "해외 거래", "ja": "海外取引"}',
    '{"en": "2.5% foreign transaction fee applies. Use a no-FX-fee card for international purchases.", "zh": "外币交易收取2.5%手续费。国际消费建议使用无外汇费卡。", "fr": "Frais de 2,5% sur transactions étrangères. Utilisez une carte sans frais FX pour achats internationaux.", "es": "Se aplica 2.5% en transacciones extranjeras. Usa tarjeta sin cargo FX para compras internacionales.", "ko": "해외 거래 수수료 2.5%. 해외 구매에는 FX 무료 카드 사용 권장.", "ja": "海外取引手数料2.5%。海外購入にはFX手数料なしカードを使用推奨。"}',
    'alert', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Platinum';

-- 5. RBC Visa Classic Low Rate Option (8条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Carrying a Balance", "zh": "分期还款", "fr": "Reporter un solde", "es": "Mantener saldo", "ko": "잔액 유지", "ja": "残高を持つ場合"}',
    '{"en": "12.99% fixed interest rate on purchases, cash advances and balance transfers - one of the lowest in Canada. No surprises.", "zh": "购物、取现、余额转账均享12.99%固定利率——加拿大最低之一。无意外费用。", "fr": "Taux fixe de 12,99% sur achats, avances et transferts - l''un des plus bas au Canada. Pas de surprises.", "es": "Tasa fija de 12.99% en compras, adelantos y transferencias - una de las más bajas en Canadá. Sin sorpresas.", "ko": "구매, 현금서비스, 잔액이체 12.99% 고정 금리 - 캐나다 최저 수준. 예상치 못한 비용 없음.", "ja": "購入、キャッシング、残高移行12.99%固定金利 - カナダ最低水準。予想外の費用なし。"}',
    'percent', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Balance Transfers", "zh": "余额转账", "fr": "Transferts de solde", "es": "Transferencias de saldo", "ko": "잔액 이체", "ja": "残高移行"}',
    '{"en": "Transfer high-interest debt from other cards. Consolidate debt and pay down balances faster with the low 12.99% rate.", "zh": "转移其他卡的高息债务。以12.99%低利率整合债务，更快还清余额。", "fr": "Transférez vos dettes à intérêt élevé. Consolidez vos dettes et remboursez plus vite au taux de 12,99%.", "es": "Transfiere deuda de alto interés. Consolida deudas y paga más rápido con el 12.99%.", "ko": "다른 카드의 고금리 부채 이체. 12.99% 저금리로 부채 통합 및 빠른 상환.", "ja": "他カードの高金利債務を移行。12.99%で債務統合し早く返済。"}',
    'credit-card', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Welcome Promo", "zh": "开卡优惠", "fr": "Promo bienvenue", "es": "Promo bienvenida", "ko": "웰컴 프로모", "ja": "ウェルカムプロモ"}',
    '{"en": "0.99% intro rate for 10 months on balance transfers + first year annual fee waived. Apply by March 25, 2026.", "zh": "余额转账享10个月0.99%优惠利率 + 首年免年费。申请截止2026年3月25日。", "fr": "Taux intro de 0,99% pendant 10 mois sur transferts + 1ère année gratuite. Postulez avant le 25 mars 2026.", "es": "Tasa intro 0.99% por 10 meses en transferencias + primer año gratis. Aplica antes del 25 marzo 2026.", "ko": "잔액이체 10개월 0.99% 특별금리 + 첫해 연회비 면제. 2026년 3월 25일까지 신청.", "ja": "残高移行10ヶ月0.99%プロモ + 初年度年会費無料。2026年3月25日まで申請可能。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Partner Savings", "zh": "合作商家优惠", "fr": "Économies partenaires", "es": "Ahorros socios", "ko": "파트너 할인", "ja": "パートナー特典"}',
    '{"en": "Save 3¢/L + 20% bonus Petro-Points at Petro-Canada. Earn 50 Be Well pts/$1 at Rexall. Get 6-month free DashPass ($60 value) from DoorDash.", "zh": "Petro-Canada每升省3分+20%额外Petro-Points。Rexall每消费$1获50 Be Well积分。DoorDash免费6个月DashPass（价值$60）。", "fr": "Économisez 3¢/L + 20% bonus Petro-Points chez Petro-Canada. Gagnez 50 pts Be Well/$1 chez Rexall. 6 mois DashPass gratuit ($60) de DoorDash.", "es": "Ahorra 3¢/L + 20% bonus Petro-Points en Petro-Canada. Gana 50 pts Be Well/$1 en Rexall. 6 meses DashPass gratis ($60) de DoorDash.", "ko": "Petro-Canada 리터당 3¢ 절약 + 20% 보너스. Rexall $1당 50 Be Well 포인트. DoorDash 6개월 무료 DashPass ($60 가치).", "ja": "Petro-Canadaでリットル3¢節約 + 20%ボーナス。Rexallで$1につき50 Be Wellポイント。DoorDash 6ヶ月無料DashPass（$60相当）。"}',
    'percent', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection achats", "es": "Protección compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "Purchase security protects eligible purchases against loss, theft or damage within 90 days of purchase.", "zh": "购物保护在购买后90天内为符合条件的购物提供丢失、被盗或损坏保障。", "fr": "La protection achats couvre les achats admissibles contre perte, vol ou dommage dans les 90 jours.", "es": "Protección de compras cubre pérdida, robo o daño dentro de 90 días de la compra.", "ko": "구매 보호는 구매 후 90일 이내 분실, 도난, 손상에 대해 보장.", "ja": "購入保護は購入後90日以内の紛失、盗難、破損を保障。"}',
    'shield', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty", "zh": "延长保修", "fr": "Garantie prolongée", "es": "Garantía extendida", "ko": "연장 보증", "ja": "延長保証"}',
    '{"en": "Doubles the manufacturer''s original Canadian warranty by up to one additional year, to a maximum of five years total.", "zh": "将制造商原保修延长最多一年，总保修期最长五年。", "fr": "Double la garantie originale du fabricant jusqu''à un an de plus, maximum cinq ans au total.", "es": "Duplica la garantía original del fabricante hasta un año adicional, máximo cinco años en total.", "ko": "제조사 보증을 최대 1년 연장, 총 최대 5년까지.", "ja": "メーカー保証を最大1年延長、合計最大5年まで。"}',
    'clock', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Rewards Earning", "zh": "赚取奖励", "fr": "Gagner des récompenses", "es": "Ganar recompensas", "ko": "리워드 적립", "ja": "リワード獲得"}',
    '{"en": "This is a low-interest card with no rewards. If you pay your balance in full monthly, a rewards card is better.", "zh": "这是无奖励的低息卡。如果每月全额还款，奖励卡更好。", "fr": "C''est une carte à faible intérêt sans récompenses. Si vous payez le solde complet, une carte récompenses est mieux.", "es": "Esta es una tarjeta de bajo interés sin recompensas. Si pagas el saldo completo mensualmente, una tarjeta con recompensas es mejor.", "ko": "이것은 리워드가 없는 저금리 카드입니다. 매월 잔액을 전액 결제한다면 리워드 카드가 더 좋습니다.", "ja": "これはリワードなしの低金利カードです。毎月残高を全額支払うなら、リワードカードの方が良いです。"}',
    'alert', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transactions", "zh": "外币交易", "fr": "Transactions étrangères", "es": "Transacciones extranjeras", "ko": "해외 거래", "ja": "海外取引"}',
    '{"en": "2.5% foreign transaction fee applies. Use a no-FX-fee card for international purchases.", "zh": "外币交易收取2.5%手续费。国际消费建议使用无外汇费卡。", "fr": "Frais de 2,5% sur transactions étrangères. Utilisez une carte sans frais FX pour achats internationaux.", "es": "Se aplica 2.5% en transacciones extranjeras. Usa tarjeta sin cargo FX para compras internacionales.", "ko": "해외 거래 수수료 2.5%. 해외 구매에는 FX 무료 카드 사용 권장.", "ja": "海外取引手数料2.5%。海外購入にはFX手数料なしカードを使用推奨。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Visa Classic Low Rate Option';

-- 6. RBC Avion Visa Platinum (9条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Welcome Bonus", "zh": "开户奖励", "fr": "Bonus bienvenue", "es": "Bono bienvenida", "ko": "웰컴 보너스", "ja": "ウェルカムボーナス"}',
    '{"en": "Earn 35,000 Avion points upon approval - travel value up to $750. Plus 20,000 more when you spend $5,000 in first 6 months.", "zh": "开户即获35,000 Avion积分（旅行价值最高$750），首6个月消费$5,000再获20,000积分。", "fr": "Gagnez 35 000 pts Avion a l''approbation - valeur voyage jusqu''a 750$. Plus 20 000 avec 5 000$ en 6 mois.", "es": "Gana 35,000 puntos Avion al aprobar - valor de viaje hasta $750. Mas 20,000 con $5,000 en 6 meses.", "ko": "승인 시 35,000 Avion 포인트 - 여행 가치 최대 $750. 6개월 내 $5,000 사용 시 20,000 추가.", "ja": "承認時35,000 Avionポイント - 旅行価値最大$750。6ヶ月で$5,000利用で20,000追加。"}',
    'gift', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "All Purchases", "zh": "所有消费", "fr": "Tous les achats", "es": "Todas las compras", "ko": "모든 구매", "ja": "全ての購入"}',
    '{"en": "Earn 1 Avion point per $1 spent on all purchases including travel. Simple earning with no category restrictions.", "zh": "所有消费（包括旅行）每消费$1赚1 Avion积分。简单积分，无分类限制。", "fr": "Gagnez 1 pt Avion par dollar sur tous les achats incluant les voyages. Pas de restrictions de categorie.", "es": "Gana 1 punto Avion por $1 en todas las compras incluyendo viajes. Sin restricciones de categoria.", "ko": "여행 포함 모든 구매에서 $1당 1 Avion 포인트. 카테고리 제한 없음.", "ja": "旅行含む全購入で$1につき1 Avionポイント。カテゴリ制限なし。"}',
    'credit-card', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Flexible Redemption", "zh": "灵活兑换", "fr": "Echange flexible", "es": "Canje flexible", "ko": "유연한 교환", "ja": "柔軟な交換"}',
    '{"en": "Redeem for flights on 500+ airlines, hotels worldwide, car rentals, gift cards, merchandise, or pay down your balance. 100 pts = $1 travel.", "zh": "可兑换500+航空公司机票、全球酒店、租车、礼品卡、商品，或抵扣账单。100积分=$1旅行。", "fr": "Echangez pour vols sur 500+ compagnies, hotels, locations auto, cartes-cadeaux, ou payez votre solde. 100 pts = 1$ voyage.", "es": "Canjea por vuelos en 500+ aerolineas, hoteles, autos, gift cards, o paga tu saldo. 100 pts = $1 viaje.", "ko": "500+ 항공사 항공편, 호텔, 렌터카, 기프트카드, 상품 또는 잔액 결제. 100포인트 = $1 여행.", "ja": "500+航空会社のフライト、ホテル、レンタカー、ギフトカード、商品、残高支払いに交換。100pts=$1旅行。"}',
    'plane', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Transfer Partners", "zh": "转点伙伴", "fr": "Partenaires transfert", "es": "Socios transferencia", "ko": "전환 파트너", "ja": "トランスファーパートナー"}',
    '{"en": "Transfer Avion points to WestJet Dollars, American Airlines, British Airways Avios, or Cathay Pacific Asia Miles for maximum value.", "zh": "可将Avion积分转换至WestJet Dollars、美国航空、英航Avios或国泰亚洲万里通，获得最大价值。", "fr": "Transferez vos points Avion vers WestJet Dollars, American Airlines, British Airways Avios ou Cathay Pacific Asia Miles.", "es": "Transfiere puntos Avion a WestJet Dollars, American Airlines, British Airways Avios o Cathay Pacific Asia Miles.", "ko": "Avion 포인트를 WestJet Dollars, American Airlines, British Airways Avios, Cathay Pacific Asia Miles로 전환.", "ja": "AvionポイントをWestJet Dollars、American Airlines、British Airways Avios、Cathay Pacific Asia Milesに移行。"}',
    'star', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Partner Savings", "zh": "合作商家优惠", "fr": "Economies partenaires", "es": "Ahorros socios", "ko": "파트너 할인", "ja": "パートナー特典"}',
    '{"en": "Save 3c/L + 20% more Petro-Points at Petro-Canada. Earn 50 Be Well pts/$1 at Rexall. Get 20% off + 3x pts at Hertz. 6-12 month free DashPass from DoorDash.", "zh": "Petro-Canada每升省3分+20%额外积分。Rexall每$1获50 Be Well积分。Hertz享8折+3倍积分。DoorDash免费6-12个月DashPass。", "fr": "Economisez 3c/L + 20% Petro-Points chez Petro-Canada. 50 pts Be Well/$1 chez Rexall. 20% + 3x pts chez Hertz. 6-12 mois DashPass gratuit.", "es": "Ahorra 3c/L + 20% Petro-Points en Petro-Canada. 50 pts Be Well/$1 en Rexall. 20% + 3x pts en Hertz. 6-12 meses DashPass gratis.", "ko": "Petro-Canada 리터당 3센트 + 20% 추가. Rexall $1당 50 Be Well. Hertz 20% 할인 + 3배. DoorDash 6-12개월 무료 DashPass.", "ja": "Petro-Canadaでリットル3セント + 20%追加。Rexallで$1につき50 Be Well。Hertz 20%オフ + 3倍。DoorDash 6-12ヶ月無料DashPass。"}',
    'percent', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Travel Insurance Package", "zh": "旅行保险套餐", "fr": "Forfait assurance voyage", "es": "Paquete seguro viaje", "ko": "여행 보험 패키지", "ja": "旅行保険パッケージ"}',
    '{"en": "Includes travel accident insurance, trip cancellation & interruption, flight delay, delayed baggage, and hotel burglary coverage.", "zh": "包含旅行意外险、行程取消/中断险、航班延误险、行李延误险和酒店失窃险。", "fr": "Comprend assurance accident voyage, annulation/interruption, retard de vol, bagages retardes et cambriolage hotel.", "es": "Incluye seguro accidente viaje, cancelacion/interrupcion, retraso vuelo, equipaje retrasado y robo hotel.", "ko": "여행 사고, 취소/중단, 항공편 지연, 수하물 지연, 호텔 도난 보험 포함.", "ja": "旅行傷害、キャンセル/中断、フライト遅延、手荷物遅延、ホテル盗難保険含む。"}',
    'plane', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Auto & Purchase Protection", "zh": "租车和购物保护", "fr": "Protection auto et achats", "es": "Proteccion auto y compras", "ko": "렌터카 및 구매 보호", "ja": "レンタカー＆購入保護"}',
    '{"en": "Auto rental collision/loss damage waiver plus purchase security and extended warranty protection on eligible purchases.", "zh": "租车碰撞/损失豁免，以及符合条件购物的购物保护和延长保修。", "fr": "Assurance collision/perte location auto plus protection achats et garantie prolongee sur achats admissibles.", "es": "Exencion colision/perdida auto rentado mas proteccion compras y garantia extendida en compras elegibles.", "ko": "렌터카 충돌/손실 면제, 적격 구매에 대한 구매 보호 및 연장 보증.", "ja": "レンタカー衝突/損害免除、対象購入の購入保護と延長保証。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Income Requirement", "zh": "无收入要求", "fr": "Sans exigence de revenu", "es": "Sin requisito de ingresos", "ko": "소득 요건 없음", "ja": "収入要件なし"}',
    '{"en": "No minimum income requirement to apply. Great entry point into the Avion rewards program with full travel benefits.", "zh": "申请无最低收入要求。进入Avion奖励计划的理想入门卡，享受完整旅行福利。", "fr": "Aucune exigence de revenu minimum. Excellente entree dans le programme Avion avec tous les avantages voyage.", "es": "Sin requisito de ingresos minimos. Gran entrada al programa Avion con beneficios de viaje completos.", "ko": "최소 소득 요건 없음. 전체 여행 혜택과 함께 Avion 프로그램 시작에 이상적.", "ja": "最低収入要件なし。完全な旅行特典付きAvionプログラムへの最適な入口。"}',
    'user', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transactions", "zh": "外币交易", "fr": "Transactions etrangeres", "es": "Transacciones extranjeras", "ko": "해외 거래", "ja": "海外取引"}',
    '{"en": "2.5% foreign transaction fee applies. Use a no-FX-fee card like RBC Avion Visa Infinite for international purchases.", "zh": "外币交易收取2.5%手续费。国际消费建议使用无外汇费卡如RBC Avion Visa Infinite。", "fr": "Frais de 2,5% sur transactions etrangeres. Utilisez une carte sans frais FX comme RBC Avion Visa Infinite.", "es": "Se aplica 2.5% en transacciones extranjeras. Usa tarjeta sin cargo FX como RBC Avion Visa Infinite.", "ko": "해외 거래 수수료 2.5%. RBC Avion Visa Infinite 같은 FX 무료 카드 사용 권장.", "ja": "海外取引手数料2.5%。RBC Avion Visa InfiniteなどFX手数料なしカードを使用推奨。"}',
    'alert', 9, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'Avion Visa Platinum';

-- 7. RBC WestJet Mastercard (13条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "2x on WestJet Flights", "zh": "WestJet航班2倍", "fr": "2x sur vols WestJet", "es": "2x en vuelos WestJet", "ko": "WestJet 항공 2배", "ja": "WestJet航空2倍"}',
    '{"en": "Earn 2 WestJet dollars per $1 on WestJet flights and WestJet Vacations. Points worth 1 cent each toward WestJet flights.", "zh": "在WestJet航班和WestJet假期上每$1赚2 WestJet积分。积分每1分钱可用于WestJet航班。", "fr": "Gagnez 2 dollars WestJet par dollar sur vols WestJet et Vacations. Points valent 1 cent vers vols WestJet.", "es": "Gana 2 dolares WestJet por $1 en vuelos WestJet y Vacations. Puntos valen 1 centavo hacia vuelos WestJet.", "ko": "WestJet 항공 및 Vacations에서 $1당 2 WestJet 달러. 포인트는 WestJet 항공에 1센트씩 가치.", "ja": "WestJet航空とバケーションで$1あたり2 WestJetドル。ポイントは1セントでWestJet航空に使用。"}',
    'plane', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "1.5x Everywhere Else", "zh": "其他消费1.5倍", "fr": "1,5x partout ailleurs", "es": "1.5x en todo lo demas", "ko": "그 외 모든 곳 1.5배", "ja": "その他1.5倍"}',
    '{"en": "Earn 1.5 WestJet dollars per $1 on all other purchases. Great base earn rate for a travel card.", "zh": "在其他所有消费上每$1赚1.5 WestJet积分。旅行卡的优秀基础积分率。", "fr": "Gagnez 1,5 dollars WestJet par dollar sur tous les autres achats. Excellent taux de base pour une carte voyage.", "es": "Gana 1.5 dolares WestJet por $1 en todas las demas compras. Excelente tasa base para tarjeta de viaje.", "ko": "기타 모든 구매에서 $1당 1.5 WestJet 달러. 여행 카드로서 훌륭한 기본 적립률.", "ja": "その他の購入で$1あたり1.5 WestJetドル。旅行カードとして優れた基本獲得率。"}',
    'credit-card', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Companion Voucher from $199", "zh": "同伴券$199起", "fr": "Billet accompagnateur 199 $", "es": "Voucher acompanante $199", "ko": "동반자 바우처 $199부터", "ja": "コンパニオンバウチャー$199から"}',
    '{"en": "Welcome companion voucher for round-trip from $199. Annual voucher after $5,000 spend, or exchange for 30% off flights, $200 vacation credit, or 2 lounge passes.", "zh": "欢迎同伴券往返$199起。年消费$5,000后获年度券，或兑换30%机票折扣、$200假期积分、2张贵宾室通行证。", "fr": "Billet accompagnateur aller-retour des 199 $. Annuel apres 5 000 $, ou echangez pour 30 % rabais, 200 $ vacances ou 2 passes salon.", "es": "Voucher acompanante ida/vuelta desde $199. Anual tras $5,000, o cambia por 30% descuento, $200 vacaciones o 2 pases de sala.", "ko": "왕복 $199부터 웰컴 동반자 바우처. $5,000 지출 후 연간 바우처, 또는 30% 할인, $200 휴가 크레딧, 라운지 패스 2장으로 교환.", "ja": "往復$199からのウェルカムコンパニオンバウチャー。$5,000利用後に年間バウチャー、または30%割引、$200バケーションクレジット、ラウンジパス2枚に交換。"}',
    'ticket', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free First Checked Bag", "zh": "首件托运行李免费", "fr": "Premier bagage gratuit", "es": "Primera maleta gratis", "ko": "첫 번째 위탁 수하물 무료", "ja": "最初の預け荷物無料"}',
    '{"en": "Primary cardholder and up to 8 companions get free first checked bag on WestJet flights when booked with the card.", "zh": "主卡持有人和最多8名同伴在用此卡预订WestJet航班时可享首件托运行李免费。", "fr": "Le titulaire principal et jusqu a 8 accompagnateurs ont le premier bagage gratuit sur vols WestJet.", "es": "Titular principal y hasta 8 acompanantes obtienen primera maleta gratis en vuelos WestJet.", "ko": "주 카드 소유자와 최대 8명의 동반자가 WestJet 항공에서 첫 번째 위탁 수하물 무료.", "ja": "主カード保有者と最大8人の同伴者がWestJet航空で最初の預け荷物無料。"}',
    'briefcase', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Comprehensive Travel Insurance", "zh": "全面旅行保险", "fr": "Assurance voyage complete", "es": "Seguro de viaje completo", "ko": "종합 여행 보험", "ja": "総合旅行保険"}',
    '{"en": "Includes Travel Accident, Auto Rental Collision/Loss Damage, Purchase Security, Extended Warranty, Delayed Baggage, and Hotel/Motel Burglary insurance.", "zh": "包含旅行意外险、租车碰撞/损失险、购物保护、延长保修、行李延误和酒店/汽车旅馆盗窃保险。", "fr": "Inclut accident de voyage, collision/perte location auto, protection achats, garantie prolongee, bagages retardes et cambriolage hotel/motel.", "es": "Incluye accidente de viaje, colision/perdida de alquiler de auto, proteccion de compras, garantia extendida, equipaje retrasado y robo de hotel/motel.", "ko": "여행 사고, 렌터카 충돌/손실, 구매 보호, 연장 보증, 수하물 지연, 호텔/모텔 도난 보험 포함.", "ja": "旅行傷害、レンタカー衝突/損害、購入保護、延長保証、手荷物遅延、ホテル/モーテル盗難保険含む。"}',
    'smartphone', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "手机保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo movil", "ko": "모바일 기기 보험", "ja": "モバイル保険"}',
    '{"en": "Protect your smartphone or tablet against damage, loss, or theft worldwide when you pay your monthly wireless bill with your card.", "zh": "用此卡支付每月无线账单时，您的智能手机或平板电脑在全球范围内享受损坏、丢失或被盗保护。", "fr": "Protegez votre smartphone ou tablette contre les dommages, pertes ou vols dans le monde entier en payant votre facture sans fil avec votre carte.", "es": "Protege tu smartphone o tablet contra danos, perdida o robo en todo el mundo al pagar tu factura de celular con tu tarjeta.", "ko": "카드로 월간 무선 요금을 결제하면 전 세계에서 스마트폰 또는 태블릿의 손상, 분실, 도난으로부터 보호.", "ja": "カードで毎月のワイヤレス料金を支払うと、スマホやタブレットが世界中で損傷・紛失・盗難から保護。"}',
    'smartphone', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Petro-Canada Savings", "zh": "Petro-Canada优惠", "fr": "Economies Petro-Canada", "es": "Ahorros Petro-Canada", "ko": "Petro-Canada 할인", "ja": "Petro-Canada特典"}',
    '{"en": "Save 3 cents/L on gas at Petro-Canada with every fill-up, plus earn 20% more Petro-Points when you link your RBC card.", "zh": "在Petro-Canada每次加油每升省3分钱，关联RBC卡还可多赚20%Petro-Points。", "fr": "Economisez 3 cents/L sur l essence chez Petro-Canada, plus 20 % de Petro-Points en plus en liant votre carte RBC.", "es": "Ahorra 3 centavos/L en gasolina en Petro-Canada, mas 20% extra de Petro-Points al vincular tu tarjeta RBC.", "ko": "Petro-Canada에서 매번 주유 시 리터당 3센트 절약, RBC 카드 연결 시 Petro-Points 20% 추가 적립.", "ja": "Petro-Canadaで給油ごとに1L3セント節約、RBCカード連携でPetro-Points20%追加。"}',
    'fuel', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Rexall Be Well Points", "zh": "Rexall Be Well积分", "fr": "Points Be Well Rexall", "es": "Puntos Be Well Rexall", "ko": "Rexall Be Well 포인트", "ja": "Rexall Be Wellポイント"}',
    '{"en": "Get 50 Be Well points for every $1 spent on eligible purchases when you shop at Rexall with your linked RBC card.", "zh": "关联RBC卡在Rexall购物时，每消费$1可获50 Be Well积分。", "fr": "Obtenez 50 points Be Well pour chaque 1 $ depense sur les achats admissibles chez Rexall avec votre carte RBC liee.", "es": "Obten 50 puntos Be Well por cada $1 gastado en compras elegibles en Rexall con tu tarjeta RBC vinculada.", "ko": "연결된 RBC 카드로 Rexall에서 적격 구매 시 $1당 50 Be Well 포인트 획득.", "ja": "連携RBCカードでRexallで買い物すると$1につき50 Be Wellポイント獲得。"}',
    'heart', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free DashPass", "zh": "免费DashPass会员", "fr": "DashPass gratuit", "es": "DashPass gratis", "ko": "무료 DashPass", "ja": "無料DashPass"}',
    '{"en": "Get complimentary DashPass subscription for up to 6 months with $0 delivery fees on orders $15+ from qualifying restaurants.", "zh": "免费获得最长6个月DashPass订阅，在符合条件的餐厅$15以上订单享$0配送费。", "fr": "Obtenez un abonnement DashPass gratuit jusqu a 6 mois avec 0 $ de frais de livraison sur commandes de 15 $ +.", "es": "Obten suscripcion DashPass gratis hasta 6 meses con $0 de entrega en pedidos de $15+.", "ko": "최대 6개월 무료 DashPass 구독, $15 이상 주문 시 배달비 없음.", "ja": "最大6ヶ月無料DashPass、$15以上の注文で配送料$0。"}',
    'food', 9, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Member Exclusive Fares", "zh": "会员专属票价", "fr": "Tarifs exclusifs membres", "es": "Tarifas exclusivas", "ko": "회원 전용 요금", "ja": "会員限定運賃"}',
    '{"en": "Access Member Exclusive Fares available only to WestJet Rewards members and stretch your points further.", "zh": "享受仅限WestJet Rewards会员的专属票价，让积分更有价值。", "fr": "Accedez aux tarifs exclusifs reserves aux membres WestJet Rewards et maximisez vos points.", "es": "Accede a tarifas exclusivas solo para miembros WestJet Rewards y estira tus puntos.", "ko": "WestJet Rewards 회원만을 위한 전용 요금에 접근하여 포인트를 더 활용하세요.", "ja": "WestJet Rewards会員限定の特別運賃でポイントをさらに活用。"}',
    'tag', 10, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Fly for Less", "zh": "低价飞行", "fr": "Volez pour moins", "es": "Vuela por menos", "ko": "저렴하게 비행", "ja": "お得に飛ぶ"}',
    '{"en": "Use WestJet points to pay for flights including taxes, fees, and surcharges. Start redeeming with as few as 2,500 points and even cover the full cost.", "zh": "使用WestJet积分支付机票，包括税费和附加费。最低2,500积分即可开始兑换，甚至可支付全部费用。", "fr": "Utilisez vos points WestJet pour payer les vols incluant taxes et frais. Commencez a echanger avec seulement 2 500 points.", "es": "Usa puntos WestJet para pagar vuelos incluyendo impuestos y cargos. Empieza a canjear desde solo 2,500 puntos.", "ko": "WestJet 포인트로 세금, 수수료 포함 항공권 결제. 최소 2,500 포인트부터 교환 시작.", "ja": "WestJetポイントで税金・手数料込みの航空券支払い。最低2,500ポイントから交換開始。"}',
    'plane', 11, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Enhance Every Journey", "zh": "升级每次旅程", "fr": "Ameliorez chaque voyage", "es": "Mejora cada viaje", "ko": "모든 여행 업그레이드", "ja": "毎回の旅をアップグレード"}',
    '{"en": "Redeem points for seat selection, checked bags, or cabin upgrades. Enjoy added comfort and convenience every time you fly.", "zh": "用积分兑换座位选择、托运行李或舱位升级。每次飞行都享受更多舒适和便利。", "fr": "Echangez des points pour la selection de siege, les bagages ou les surclassements de cabine. Plus de confort a chaque vol.", "es": "Canjea puntos por seleccion de asiento, equipaje facturado o mejoras de cabina. Mas comodidad en cada vuelo.", "ko": "포인트로 좌석 선택, 위탁 수하물, 캐빈 업그레이드 교환. 매번 비행할 때마다 편안함과 편리함.", "ja": "ポイントで座席選択、預け荷物、キャビンアップグレードに交換。毎回のフライトで快適さを。"}',
    'upgrade', 12, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Points Beyond Travel", "zh": "积分不止旅行", "fr": "Points au-dela du voyage", "es": "Puntos mas alla del viaje", "ko": "여행 외 포인트 사용", "ja": "旅行以外にもポイント活用"}',
    '{"en": "Redeem WestJet points at the WestJet Rewards eStore for gift cards, tech, home essentials, and more from your favourite brands.", "zh": "在WestJet Rewards电子商店用积分兑换礼品卡、科技产品、家居必需品等您喜爱的品牌商品。", "fr": "Echangez vos points WestJet au eStore pour des cartes-cadeaux, de la tech, des articles menagers et plus.", "es": "Canjea puntos WestJet en la eStore por tarjetas de regalo, tecnologia, articulos para el hogar y mas.", "ko": "WestJet Rewards eStore에서 기프트 카드, 기술제품, 가정용품 등을 좋아하는 브랜드로 교환.", "ja": "WestJet Rewards eStoreでギフトカード、テック製品、生活必需品などに交換。"}',
    'gift', 13, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'WestJet Mastercard';

-- 8. RBC More Rewards Visa (8条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Partner Grocery Stores", "zh": "合作超市", "fr": "Épiceries partenaires", "es": "Supermercados asociados", "ko": "파트너 식료품점", "ja": "提携スーパー"}',
    '{"en": "Earn 5x points at Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare, Pure Integrative Pharmacy and 700+ partner locations.", "zh": "在Save-On-Foods、Quality Foods、Buy-Low Foods、PriceSmart Foods、Urban Fare、Pure Integrative Pharmacy等700+合作商家可获5倍积分。", "fr": "5x points chez Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare et 700+ partenaires.", "es": "5x puntos en Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare y 700+ socios.", "ko": "Save-On-Foods, Quality Foods 등 700+ 파트너에서 5배 포인트.", "ja": "Save-On-Foods等700+提携店で5倍ポイント。"}',
    'cart', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Gas & Dining", "zh": "加油和餐饮", "fr": "Essence et restaurants", "es": "Gasolina y restaurantes", "ko": "주유 및 식사", "ja": "ガソリン・外食"}',
    '{"en": "Earn 5x points on gas, EV charging, and dining purchases.", "zh": "加油、电动车充电和餐饮消费可获5倍积分。", "fr": "5x points sur essence, recharge VE et restaurants.", "es": "5x puntos en gasolina, carga EV y restaurantes.", "ko": "주유, EV 충전, 식사에서 5배 포인트.", "ja": "ガソリン、EV充電、外食で5倍ポイント。"}',
    'gas', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "免年费", "fr": "Sans frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "No annual fee makes this a great everyday card with strong rewards.", "zh": "无年费，是一张奖励丰厚的日常用卡。", "fr": "Sans frais annuels, excellente carte quotidienne avec de bonnes récompenses.", "es": "Sin cuota anual, excelente tarjeta diaria con buenas recompensas.", "ko": "연회비 없음, 좋은 보상의 일상 카드.", "ja": "年会費無料、優れた特典の日常カード。"}',
    'dollar', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Petro-Canada Savings", "zh": "Petro-Canada优惠", "fr": "Économies Petro-Canada", "es": "Ahorros Petro-Canada", "ko": "Petro-Canada 할인", "ja": "Petro-Canada特典"}',
    '{"en": "Save 3¢/L on fuel and earn 20% more Petro-Points when you pay with linked RBC card.", "zh": "使用关联RBC卡支付可省3¢/升油费，并多赚20% Petro-Points。", "fr": "Économisez 3¢/L et gagnez 20% plus de Petro-Points avec carte RBC liée.", "es": "Ahorre 3¢/L y gane 20% más Petro-Points con tarjeta RBC vinculada.", "ko": "연결된 RBC 카드로 리터당 3¢ 절약, Petro-Points 20% 추가.", "ja": "連携RBCカードで3¢/L節約、Petro-Points 20%増。"}',
    'percent', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Flexible Redemption", "zh": "灵活兑换", "fr": "Échange flexible", "es": "Canje flexible", "ko": "유연한 리워드", "ja": "柔軟な交換"}',
    '{"en": "Redeem points for groceries, gift cards, experiences, or travel rewards.", "zh": "积分可兑换杂货、礼品卡、体验或旅行奖励。", "fr": "Échangez vos points contre épicerie, cartes-cadeaux, expériences ou voyages.", "es": "Canjee puntos por comestibles, tarjetas de regalo, experiencias o viajes.", "ko": "식료품, 기프트카드, 체험, 여행으로 포인트 교환.", "ja": "食料品、ギフトカード、体験、旅行に交換可能。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "手机保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo móvil", "ko": "모바일 기기 보험", "ja": "モバイル保険"}',
    '{"en": "2 years coverage up to $1,000 for loss, theft, damage or mechanical failure when you purchase your mobile device with this card.", "zh": "用此卡购买手机可获2年最高$1,000保障，涵盖丢失、被盗、损坏或机械故障。", "fr": "2 ans de couverture jusqu''à 1 000$ pour perte, vol, dommage ou panne en achetant avec cette carte.", "es": "2 años de cobertura hasta $1,000 por pérdida, robo, daño o falla mecánica al comprar con esta tarjeta.", "ko": "이 카드로 구매 시 분실, 도난, 손상, 기계 고장에 대해 2년간 최대 $1,000 보장.", "ja": "このカードで購入すると紛失・盗難・破損・故障に2年間最大$1,000補償。"}',
    'smartphone', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "90-day protection against loss, theft or damage on eligible purchases, plus extended warranty up to 1 additional year (max 5 years).", "zh": "符合条件的购物享90天丢失、被盗或损坏保护，并延长保修最多1年（最长5年）。", "fr": "90 jours de protection contre perte, vol ou dommage, plus garantie prolongée jusqu''à 1 an supplémentaire (max 5 ans).", "es": "90 días de protección contra pérdida, robo o daño, más garantía extendida hasta 1 año adicional (máx 5 años).", "ko": "적격 구매에 대해 90일 분실/도난/손상 보호, 최대 1년 연장 보증(최대 5년).", "ja": "対象購入品に90日間の紛失・盗難・破損保護、最大1年の延長保証（最長5年）。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Quebec Residents", "zh": "魁北克居民", "fr": "Résidents du Québec", "es": "Residentes de Quebec", "ko": "퀘벡 거주자", "ja": "ケベック州居住者"}',
    '{"en": "This card is not available to Quebec residents.", "zh": "此卡不适用于魁北克省居民。", "fr": "Cette carte n''est pas disponible pour les résidents du Québec.", "es": "Esta tarjeta no está disponible para residentes de Quebec.", "ko": "이 카드는 퀘벡 거주자에게 제공되지 않습니다.", "ja": "このカードはケベック州居住者には利用できません。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa';

-- 9. RBC More Rewards Visa Infinite (8条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Partner Grocery Stores", "zh": "合作超市", "fr": "Épiceries partenaires", "es": "Supermercados asociados", "ko": "파트너 식료품점", "ja": "提携スーパー"}',
    '{"en": "Earn 8x points at Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare, Pure Integrative Pharmacy and 700+ partner locations.", "zh": "在Save-On-Foods、Quality Foods、Buy-Low Foods、PriceSmart Foods、Urban Fare、Pure Integrative Pharmacy等700+合作商家可获8倍积分。", "fr": "8x points chez Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare et 700+ partenaires.", "es": "8x puntos en Save-On-Foods, Quality Foods, Buy-Low Foods, PriceSmart Foods, Urban Fare y 700+ socios.", "ko": "Save-On-Foods, Quality Foods 등 700+ 파트너에서 8배 포인트.", "ja": "Save-On-Foods等700+提携店で8倍ポイント。"}',
    'cart', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Gas & Dining", "zh": "加油和餐饮", "fr": "Essence et restaurants", "es": "Gasolina y restaurantes", "ko": "주유 및 식사", "ja": "ガソリン・外食"}',
    '{"en": "Earn 8x points on gas, EV charging, and dining purchases.", "zh": "加油、电动车充电和餐饮消费可获8倍积分。", "fr": "8x points sur essence, recharge VE et restaurants.", "es": "8x puntos en gasolina, carga EV y restaurantes.", "ko": "주유, EV 충전, 식사에서 8배 포인트.", "ja": "ガソリン、EV充電、外食で8倍ポイント。"}',
    'gas', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee Infinite", "zh": "免年费Infinite卡", "fr": "Infinite sans frais", "es": "Infinite sin cuota", "ko": "연회비 없음 Infinite", "ja": "年会費無料Infinite"}',
    '{"en": "Rare no annual fee Visa Infinite card with premium rewards and insurance benefits.", "zh": "罕见的免年费Visa Infinite卡，享有高端奖励和保险福利。", "fr": "Rare carte Visa Infinite sans frais avec récompenses premium et assurances.", "es": "Rara tarjeta Visa Infinite sin cuota con recompensas premium y seguros.", "ko": "프리미엄 보상과 보험 혜택이 있는 희귀한 연회비 없는 Visa Infinite 카드.", "ja": "プレミアム特典と保険付きの珍しい年会費無料Visa Infiniteカード。"}',
    'star', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Petro-Canada Savings", "zh": "Petro-Canada优惠", "fr": "Économies Petro-Canada", "es": "Ahorros Petro-Canada", "ko": "Petro-Canada 할인", "ja": "Petro-Canada特典"}',
    '{"en": "Save 3¢/L on fuel and earn 20% more Petro-Points when you pay with linked RBC card.", "zh": "使用关联RBC卡支付可省3¢/升油费，并多赚20% Petro-Points。", "fr": "Économisez 3¢/L et gagnez 20% plus de Petro-Points avec carte RBC liée.", "es": "Ahorre 3¢/L y gane 20% más Petro-Points con tarjeta RBC vinculada.", "ko": "연결된 RBC 카드로 리터당 3¢ 절약, Petro-Points 20% 추가.", "ja": "連携RBCカードで3¢/L節約、Petro-Points 20%増。"}',
    'percent', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Flexible Redemption", "zh": "灵活兑换", "fr": "Échange flexible", "es": "Canje flexible", "ko": "유연한 리워드", "ja": "柔軟な交換"}',
    '{"en": "Redeem points for groceries, gift cards, experiences, or travel rewards.", "zh": "积分可兑换杂货、礼品卡、体验或旅行奖励。", "fr": "Échangez vos points contre épicerie, cartes-cadeaux, expériences ou voyages.", "es": "Canjee puntos por comestibles, tarjetas de regalo, experiencias o viajes.", "ko": "식료품, 기프트카드, 체험, 여행으로 포인트 교환.", "ja": "食料品、ギフトカード、体験、旅行に交換可能。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "手机保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo móvil", "ko": "모바일 기기 보험", "ja": "モバイル保険"}',
    '{"en": "2 years coverage up to $1,000 for loss, theft, damage or mechanical failure when you purchase your mobile device with this card.", "zh": "用此卡购买手机可获2年最高$1,000保障，涵盖丢失、被盗、损坏或机械故障。", "fr": "2 ans de couverture jusqu''a 1 000$ pour perte, vol, dommage ou panne en achetant avec cette carte.", "es": "2 años de cobertura hasta $1,000 por pérdida, robo, daño o falla mecánica al comprar con esta tarjeta.", "ko": "이 카드로 구매 시 분실, 도난, 손상, 기계 고장에 대해 2년간 최대 $1,000 보장.", "ja": "このカードで購入すると紛失・盗難・破損・故障に2年間最大$1,000補償。"}',
    'smartphone', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "90-day protection against loss, theft or damage on eligible purchases, plus extended warranty up to 1 additional year (max 5 years).", "zh": "符合条件的购物享90天丢失、被盗或损坏保护，并延长保修最多1年（最长5年）。", "fr": "90 jours de protection contre perte, vol ou dommage, plus garantie prolongee jusqu''a 1 an supplementaire (max 5 ans).", "es": "90 días de protección contra pérdida, robo o daño, más garantía extendida hasta 1 año adicional (máx 5 años).", "ko": "적격 구매에 대해 90일 분실/도난/손상 보호, 최대 1년 연장 보증(최대 5년).", "ja": "対象購入品に90日間の紛失・盗難・破損保護、最大1年の延長保証（最長5年）。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Quebec Residents", "zh": "魁北克居民", "fr": "Résidents du Québec", "es": "Residentes de Quebec", "ko": "퀘벡 거주자", "ja": "ケベック州居住者"}',
    '{"en": "This card is not available to Quebec residents.", "zh": "此卡不适用于魁北克省居民。", "fr": "Cette carte n''est pas disponible pour les résidents du Québec.", "es": "Esta tarjeta no está disponible para residentes de Quebec.", "ko": "이 카드는 퀘벡 거주자에게 제공되지 않습니다.", "ja": "このカードはケベック州居住者には利用できません。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'More Rewards Visa Infinite';

-- 10. RBC RateAdvantage Visa (7条用卡攻略)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Carrying a Balance", "zh": "需要分期还款", "fr": "Porter un solde", "es": "Mantener saldo", "ko": "잔액 유지", "ja": "残高を持ち越す場合"}',
    '{"en": "Best for those who carry a balance - low variable interest rate based on your credit rating. Better credit = lower rate!", "zh": "适合需要分期还款的人——基于信用评分的低可变利率。信用越好，利率越低！", "fr": "Idéal pour ceux qui portent un solde - taux variable bas selon votre cote de crédit. Meilleur crédit = taux plus bas!", "es": "Ideal para quienes mantienen saldo - tasa variable baja según tu calificación crediticia. Mejor crédito = menor tasa!", "ko": "잔액을 유지하는 분에게 최적 - 신용 등급에 따른 낮은 변동 금리. 좋은 신용 = 낮은 금리!", "ja": "残高を持ち越す方に最適 - 信用評価に基づく低変動金利。信用が良いほど金利が低い！"}',
    'percent', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "免年费", "fr": "Sans frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "No annual fee combined with low interest rate makes this ideal for balance carriers.", "zh": "免年费加低利率，非常适合需要分期还款的用户。", "fr": "Sans frais annuels avec taux bas, idéal pour ceux qui portent un solde.", "es": "Sin cuota anual con tasa baja, ideal para quienes mantienen saldo.", "ko": "연회비 없음과 낮은 금리로 잔액 유지자에게 이상적.", "ja": "年会費無料と低金利で残高持ち越しに最適。"}',
    'dollar', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Petro-Canada Savings", "zh": "Petro-Canada优惠", "fr": "Économies Petro-Canada", "es": "Ahorros Petro-Canada", "ko": "Petro-Canada 할인", "ja": "Petro-Canada特典"}',
    '{"en": "Save 3¢/L on fuel and earn 20% more Petro-Points when you pay with linked RBC card.", "zh": "使用关联RBC卡支付可省3¢/升油费，并多赚20% Petro-Points。", "fr": "Économisez 3¢/L et gagnez 20% plus de Petro-Points avec carte RBC liée.", "es": "Ahorre 3¢/L y gane 20% más Petro-Points con tarjeta RBC vinculada.", "ko": "연결된 RBC 카드로 리터당 3¢ 절약, Petro-Points 20% 추가.", "ja": "連携RBCカードで3¢/L節約、Petro-Points 20%増。"}',
    'gas', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Rexall Be Well Points", "zh": "Rexall Be Well积分", "fr": "Points Be Well Rexall", "es": "Puntos Be Well Rexall", "ko": "Rexall Be Well 포인트", "ja": "Rexall Be Wellポイント"}',
    '{"en": "Earn 50 Be Well points per $1 at Rexall. Redeem 25,000 points = $10 savings.", "zh": "在Rexall每消费$1可获50 Be Well积分。25,000积分可兑换$10。", "fr": "Gagnez 50 points Be Well par 1$ chez Rexall. 25 000 points = 10$ économies.", "es": "Gana 50 puntos Be Well por $1 en Rexall. 25,000 puntos = $10 de ahorro.", "ko": "Rexall에서 $1당 50 Be Well 포인트. 25,000 포인트 = $10 할인.", "ja": "Rexallで$1あたり50 Be Wellポイント。25,000ポイント=$10節約。"}',
    'star', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "DoorDash Free Delivery", "zh": "DoorDash免配送费", "fr": "Livraison DoorDash gratuite", "es": "Entrega gratis DoorDash", "ko": "DoorDash 무료 배달", "ja": "DoorDash配送無料"}',
    '{"en": "6-month complimentary DashPass with $0 delivery fees on orders $15+ (value ~$60).", "zh": "6个月免费DashPass会员，$15以上订单免配送费（价值约$60）。", "fr": "DashPass gratuit 6 mois, livraison gratuite sur commandes 15$+ (valeur ~60$).", "es": "DashPass gratis 6 meses, entrega gratis en pedidos de $15+ (valor ~$60).", "ko": "6개월 무료 DashPass, $15 이상 주문 시 무료 배달 (가치 ~$60).", "ja": "6ヶ月無料DashPass、$15以上で配送無料（価値約$60）。"}',
    'cart', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "90-day protection against loss, theft or damage, plus extended warranty doubling manufacturer warranty up to 1 year.", "zh": "90天丢失、被盗或损坏保护，并延长保修（原厂保修延长一倍，最多1年）。", "fr": "90 jours de protection contre perte, vol ou dommage, plus garantie prolongee doublant la garantie fabricant jusqu a 1 an.", "es": "90 dias de proteccion contra perdida, robo o dano, mas garantia extendida duplicando garantia del fabricante hasta 1 ano.", "ko": "90일 분실/도난/손상 보호, 제조사 보증 최대 1년 연장.", "ja": "90日間の紛失・盗難・破損保護、メーカー保証最大1年延長。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Rewards", "zh": "无奖励", "fr": "Pas de recompenses", "es": "Sin recompensas", "ko": "리워드 없음", "ja": "リワードなし"}',
    '{"en": "This card offers no points or cashback rewards. Only use if you need low interest rate for carrying a balance.", "zh": "此卡不提供积分或返现奖励。只适合需要低利率分期还款的用户。", "fr": "Cette carte n offre pas de points ou remises. Utilisez uniquement si vous avez besoin d un taux bas.", "es": "Esta tarjeta no ofrece puntos ni reembolsos. Solo use si necesita tasa baja para mantener saldo.", "ko": "이 카드는 포인트나 캐시백이 없습니다. 낮은 금리가 필요한 경우에만 사용.", "ja": "このカードにはポイントやキャッシュバックがありません。低金利が必要な場合のみ使用。"}',
    'alert', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'RateAdvantage Visa';

-- 11. moi RBC Visa (8条用卡攻略，魁北克/安省/新不伦瑞克)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Metro & Partner Stores", "zh": "Metro及合作商家", "fr": "Metro et partenaires", "es": "Metro y socios", "ko": "Metro 및 파트너", "ja": "Metro＆パートナー"}',
    '{"en": "Earn 2x Moi points at Metro, Brunet, Première Moisson (Quebec) and Jean Coutu when using both Moi card and this credit card.", "zh": "同时使用Moi卡和此信用卡在Metro、Brunet、Première Moisson（魁北克）和Jean Coutu消费可获2倍Moi积分。", "fr": "Gagnez 2x pts Moi chez Metro, Brunet, Première Moisson (Québec) et Jean Coutu avec votre carte Moi et cette carte.", "es": "Gana 2x puntos Moi en Metro, Brunet, Première Moisson (Quebec) y Jean Coutu al usar ambas tarjetas.", "ko": "Moi 카드와 이 신용카드로 Metro, Brunet, Première Moisson, Jean Coutu에서 2배 Moi 포인트.", "ja": "MoiカードとこのカードでMetro、Brunet、Première Moisson、Jean Coutuで2倍Moiポイント。"}',
    'cart', 1, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Dining & Gas", "zh": "餐饮和加油", "fr": "Restaurants et essence", "es": "Restaurantes y gasolina", "ko": "식사 및 주유", "ja": "飲食・ガソリン"}',
    '{"en": "Earn 2x Moi points on dining, gas and EV charging purchases.", "zh": "餐饮、加油和电动车充电消费可获2倍Moi积分。", "fr": "Gagnez 2x pts Moi sur restaurants, essence et recharge VE.", "es": "Gana 2x puntos Moi en restaurantes, gasolina y carga EV.", "ko": "식사, 주유, EV 충전에서 2배 Moi 포인트.", "ja": "飲食、ガソリン、EV充電で2倍Moiポイント。"}',
    'gas', 2, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "免年费", "fr": "Sans frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "No annual fee. Perfect for Quebec/Ontario/New Brunswick residents who shop at Metro stores.", "zh": "无年费。适合在Metro购物的魁北克/安省/新不伦瑞克居民。", "fr": "Sans frais annuels. Parfait pour les résidents du Québec/Ontario/Nouveau-Brunswick qui magasinent chez Metro.", "es": "Sin cuota anual. Perfecto para residentes de Quebec/Ontario/New Brunswick que compran en Metro.", "ko": "연회비 없음. Metro에서 쇼핑하는 퀘벡/온타리오/뉴브런즈윅 거주자에게 적합.", "ja": "年会費無料。Metroで買い物するケベック/オンタリオ/ニューブランズウィック居住者に最適。"}',
    'dollar', 3, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Easy Redemption", "zh": "轻松兑换", "fr": "Échange facile", "es": "Canje fácil", "ko": "쉬운 리워드", "ja": "簡単交換"}',
    '{"en": "Only 500 Moi points gets you $4 off at nearly 900 participating stores.", "zh": "只需500 Moi积分即可在近900家合作商店获得$4折扣。", "fr": "Seulement 500 pts Moi = 4$ de rabais dans près de 900 magasins participants.", "es": "Solo 500 puntos Moi = $4 de descuento en casi 900 tiendas participantes.", "ko": "500 Moi 포인트로 900개 참여 매장에서 $4 할인.", "ja": "500 Moiポイントで約900店舗で$4割引。"}',
    'gift', 4, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Petro-Canada Savings", "zh": "Petro-Canada优惠", "fr": "Économies Petro-Canada", "es": "Ahorros Petro-Canada", "ko": "Petro-Canada 할인", "ja": "Petro-Canada特典"}',
    '{"en": "Save 3¢/L on fuel and earn 20% more points when you pay with linked RBC card.", "zh": "使用关联RBC卡支付可省3¢/升油费，并多赚20%积分。", "fr": "Économisez 3¢/L et gagnez 20% plus de points avec carte RBC liée.", "es": "Ahorre 3¢/L y gane 20% más puntos con tarjeta RBC vinculada.", "ko": "연결된 RBC 카드로 리터당 3¢ 절약, 20% 추가 포인트.", "ja": "連携RBCカードで3¢/L節約、20%追加ポイント。"}',
    'percent', 5, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "手机保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo móvil", "ko": "모바일 기기 보험", "ja": "モバイル保険"}',
    '{"en": "2 years coverage up to $1,000 for loss, theft, damage or mechanical failure when you purchase your mobile device with this card.", "zh": "用此卡购买手机可获2年最高$1,000保障，涵盖丢失、被盗、损坏或机械故障。", "fr": "2 ans de couverture jusqu a 1 000$ pour perte, vol, dommage ou panne en achetant avec cette carte.", "es": "2 años de cobertura hasta $1,000 por pérdida, robo, daño o falla mecánica al comprar con esta tarjeta.", "ko": "이 카드로 구매 시 분실, 도난, 손상, 기계 고장에 대해 2년간 최대 $1,000 보장.", "ja": "このカードで購入すると紛失・盗難・破損・故障に2年間最大$1,000補償。"}',
    'smartphone', 6, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "90-day protection against loss, theft or damage, plus extended warranty up to 1 additional year (max 5 years).", "zh": "90天丢失、被盗或损坏保护，并延长保修最多1年（最长5年）。", "fr": "90 jours de protection contre perte, vol ou dommage, plus garantie prolongee jusqu a 1 an supplementaire (max 5 ans).", "es": "90 dias de proteccion contra perdida, robo o dano, mas garantia extendida hasta 1 ano adicional (max 5 anos).", "ko": "90일 분실/도난/손상 보호, 최대 1년 연장 보증(최대 5년).", "ja": "90日間の紛失・盗難・破損保護、最大1年の延長保証（最長5年）。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Limited Regions", "zh": "地区限制", "fr": "Régions limitées", "es": "Regiones limitadas", "ko": "지역 제한", "ja": "地域限定"}',
    '{"en": "Metro stores are only in Quebec, Ontario and New Brunswick. Best value if you shop at these stores regularly.", "zh": "Metro门店仅在魁北克、安省和新不伦瑞克。如果经常在这些商店购物才最划算。", "fr": "Les magasins Metro sont seulement au Québec, Ontario et Nouveau-Brunswick. Meilleure valeur si vous y magasinez souvent.", "es": "Las tiendas Metro solo estan en Quebec, Ontario y New Brunswick. Mejor valor si compras ahi regularmente.", "ko": "Metro 매장은 퀘벡, 온타리오, 뉴브런즈윅에만 있습니다. 정기적으로 방문하면 최고의 가치.", "ja": "Metro店舗はケベック、オンタリオ、ニューブランズウィックのみ。定期的に買い物するなら最高の価値。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'RBC' AND name = 'moi RBC Visa';
