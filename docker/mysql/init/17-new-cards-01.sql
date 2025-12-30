-- ============================================
-- 7张新AMEX卡片 SQL
-- 新卡ID从63开始
-- ============================================

-- 1. AMEX Essential Credit Card (ID: 63)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('AMEX', 'Essential Credit Card', 'AMEX', 25.00, 0.0000, NULL,
     '{"gradient": "linear-gradient(135deg, #c0c0c0 0%, #a0a0a0 100%)", "textColor": "#1a1a1a"}',
     'https://www.americanexpress.com/en-ca/credit-cards/essential-credit-card/', 0, 1, 'CASHBACK', NULL, NULL);

-- 2. Business Gold Rewards Card (ID: 64)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program, amex_travel_bonus_rate) VALUES
    ('AMEX', 'Business Gold Rewards Card', 'AMEX', 199.00, 0.0100,
     '{"bonusAmount": 40000, "minSpend": 7500, "daysToComplete": 90, "description": {"en": "40,000 MR points after $7,500 spend in first 3 months", "zh": "3个月内消费$7,500获40,000 MR积分", "fr": "40 000 pts MR après 7 500 $ en 3 mois", "es": "40,000 pts MR después de $7,500 en 3 meses", "ja": "3ヶ月で$7,500消費後40,000 MRポイント", "ko": "3개월 내 $7,500 사용 시 40,000 MR 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #c9a227 0%, #9a7b1c 100%)", "textColor": "#1a1a1a"}',
     'https://www.americanexpress.com/en-ca/business/credit-cards/business-gold-rewards-card/', 0, 1, 'POINTS', 0.0100, 'Membership Rewards',null);

-- 3. Business Platinum Card (ID: 65)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program, amex_travel_bonus_rate) VALUES
    ('AMEX', 'Business Platinum Card', 'AMEX', 799.00, 0.0125,
     '{"bonusAmount": 120000, "minSpend": 15000, "daysToComplete": 90, "description": {"en": "80,000 pts after $15,000 in 3 months + 40,000 pts in months 15-17", "zh": "3个月消费$15,000获80,000积分 + 第15-17月获40,000积分", "fr": "80 000 pts après 15 000 $ en 3 mois + 40 000 pts aux mois 15-17", "es": "80,000 pts después de $15,000 en 3 meses + 40,000 pts en meses 15-17", "ja": "3ヶ月で$15,000消費後80,000ポイント + 15-17ヶ月目に40,000ポイント", "ko": "3개월 내 $15,000 사용 시 80,000 포인트 + 15-17개월차 40,000 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #e5e4e2 0%, #c0c0c0 100%)", "textColor": "#1a1a1a"}',
     'https://www.americanexpress.com/en-ca/business/credit-cards/business-platinum-card/', 0, 1, 'POINTS', 0.0200, 'Membership Rewards',null);

-- 4. Green Card (ID: 66)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program, amex_travel_bonus_rate) VALUES
    ('AMEX', 'Green Card', 'AMEX', 0.00, 0.0100,
     '{"bonusAmount": 10000, "minSpend": 1000, "daysToComplete": 90, "description": {"en": "10,000 MR points after $1,000 spend in first 3 months", "zh": "3个月内消费$1,000获10,000 MR积分", "fr": "10 000 pts MR après 1 000 $ en 3 mois", "es": "10,000 pts MR después de $1,000 en 3 meses", "ja": "3ヶ月で$1,000消費後10,000 MRポイント", "ko": "3개월 내 $1,000 사용 시 10,000 MR 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #90c9a7 0%, #6ba583 100%)", "textColor": "#1a1a1a"}',
     'https://www.americanexpress.com/en-ca/credit-cards/green-card/', 0, 1, 'POINTS', 0.0100, 'Membership Rewards', 0.0100);

-- 5. Marriott Bonvoy Card (ID: 65)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('AMEX', 'Marriott Bonvoy Card', 'AMEX', 120.00, 0.0200,
     '{"bonusAmount": 60000, "minSpend": 1500, "daysToComplete": 90, "description": {"en": "60,000 Marriott Bonvoy points after $1,500 spend in first 3 months", "zh": "3个月内消费$1,500获60,000万豪积分", "fr": "60 000 pts Marriott Bonvoy après 1 500 $ en 3 mois", "es": "60,000 pts Marriott Bonvoy después de $1,500 en 3 meses", "ja": "3ヶ月で$1,500消費後60,000マリオットポイント", "ko": "3개월 내 $1,500 사용 시 60,000 메리어트 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #3d4f5f 0%, #2a3640 100%)", "textColor": "white"}',
     'https://www.americanexpress.com/en-ca/credit-cards/marriott-bonvoy-card/', 0, 1, 'POINTS', 0.0080, 'Marriott Bonvoy');

-- 6. Marriott Bonvoy Business Card (ID: 66)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('AMEX', 'Marriott Bonvoy Business Card', 'AMEX', 150.00, 0.0200,
     '{"bonusAmount": 60000, "minSpend": 5000, "daysToComplete": 90, "description": {"en": "60,000 Marriott Bonvoy points after $5,000 spend in first 3 months", "zh": "3个月内消费$5,000获60,000万豪积分", "fr": "60 000 pts Marriott Bonvoy après 5 000 $ en 3 mois", "es": "60,000 pts Marriott Bonvoy después de $5,000 en 3 meses", "ja": "3ヶ月で$5,000消費後60,000マリオットポイント", "ko": "3개월 내 $5,000 사용 시 60,000 메리어트 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #3d4f5f 0%, #2a3640 100%)", "textColor": "white"}',
     'https://www.americanexpress.com/en-ca/credit-cards/marriott-bonvoy-business-card/', 0, 1, 'POINTS', 0.0080, 'Marriott Bonvoy');

-- 7. Aeroplan Business Reserve Card (ID: 69)
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('AMEX', 'Aeroplan Business Reserve Card', 'AMEX', 599.00, 0.0125,
     '{"bonusAmount": 90000, "minSpend": 10500, "daysToComplete": 90, "description": {"en": "65,000 pts after $10,500 in 3 months + 25,000 pts after $3,500 in month 13", "zh": "3个月消费$10,500获65,000积分 + 第13月消费$3,500获25,000积分", "fr": "65 000 pts après 10 500 $ en 3 mois + 25 000 pts après 3 500 $ au mois 13", "es": "65,000 pts después de $10,500 en 3 meses + 25,000 pts después de $3,500 en mes 13", "ja": "3ヶ月で$10,500消費後65,000ポイント + 13ヶ月目に$3,500消費で25,000ポイント", "ko": "3개월 내 $10,500 사용 시 65,000 포인트 + 13개월차 $3,500 사용 시 25,000 포인트"}}',
     '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%)", "textColor": "white"}',
     'https://www.americanexpress.com/en-ca/business/credit-cards/aeroplan-business-reserve-card/', 0, 1, 'POINTS', 0.0200, 'Aeroplan');

-- ============================================
-- REWARD RULES (假设卡ID从63开始)
-- ============================================

-- Essential Credit Card (ID: 63) - 无返现规则

-- Business Gold Rewards Card (ID: 64) - 1x all, 10k quarterly bonus
-- 无特定分类bonus，base rate已经是1x

-- Business Platinum Card (ID: 65) - 1.25x all
-- 无特定分类bonus，base rate已经是1.25x

-- Green Card (ID: 66) - 1x all, 2x via Amex Travel (handled by amex_travel_bonus_rate field)
-- No category-specific reward_rules needed

-- Marriott Bonvoy Card (ID: 65)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
    (65, 'TRAVEL', 0.0500, NULL, '5x points at Marriott Bonvoy hotels');

-- Marriott Bonvoy Business Card (ID: 66)
-- Note: 5x on Marriott hotels is merchant-specific, handled in tips
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
                                                                                               (66, 'TRAVEL', 0.0300, NULL, '3x points on travel'),
                                                                                               (66, 'DINING', 0.0300, NULL, '3x points on dining'),
                                                                                               (66, 'GAS', 0.0300, NULL, '3x points on gas');

-- Aeroplan Business Reserve Card (ID: 67)
-- 3X on Air Canada direct purchases (specific merchant, not category-based)
-- 2X on eligible hotel and car rentals
-- 1.25X on everything else (base rate)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
    (67, 'TRAVEL', 0.0200, NULL, '3x on Air Canada, 2x on eligible hotel and car rentals');

-- ============================================
-- UPDATE SQL (如果数据库中已有数据，运行以下语句更新)
-- ============================================
-- UPDATE reward_rules SET reward_rate = 0.0200, description = '2x points on eligible hotel and car rentals'
--   WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Business Reserve Card') AND category = 'TRAVEL';
-- DELETE FROM reward_rules
--   WHERE card_id = (SELECT id FROM credit_cards WHERE bank = 'AMEX' AND name = 'Aeroplan Business Reserve Card') AND category = 'DINING';

-- ============================================
-- CARD USAGE TIPS
-- ============================================

-- Essential Credit Card (ID: 61)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
                                                                                                   (61, 'BEST_USE',
                                                                                                    '{"en": "Low Interest Balance Transfer", "zh": "低利率余额转移", "fr": "Transfert de solde à faible taux", "es": "Transferencia de saldo con bajo interés", "ja": "低金利残高移行", "ko": "저금리 잔액 이체"}',
                                                                                                    '{"en": "Use this card primarily for balance transfers with 12.99% APR. Not recommended for earning rewards.", "zh": "主要用于余额转移，年利率12.99%。不建议用于赚取返现。", "fr": "Utilisez principalement pour les transferts de solde à 12,99%. Non recommandé pour les récompenses.", "es": "Use principalmente para transferencias de saldo al 12.99%. No recomendado para recompensas.", "ja": "主に12.99%APRの残高移行に使用。リワード獲得には不向き。", "ko": "주로 12.99% APR 잔액 이체에 사용. 리워드 적립에는 비추천."}',
                                                                                                    10, 1),
                                                                                                   (61, 'AVOID',
                                                                                                    '{"en": "Not for Rewards", "zh": "不适合赚取奖励", "fr": "Pas pour les récompenses", "es": "No para recompensas", "ja": "リワード向けではない", "ko": "리워드용이 아님"}',
                                                                                                    '{"en": "This card has no rewards program. Use other AMEX cards for earning points or cashback.", "zh": "此卡没有奖励计划。使用其他AMEX卡赚取积分或返现。", "fr": "Cette carte n''a pas de programme de récompenses. Utilisez d''autres cartes AMEX.", "es": "Esta tarjeta no tiene programa de recompensas. Use otras tarjetas AMEX.", "ja": "このカードにはリワードプログラムがありません。", "ko": "이 카드에는 리워드 프로그램이 없습니다."}',
                                                                                                    9, 1),
                                                                                                   -- INSURANCE: Travel Accident
                                                                                                   (61, 'INSURANCE',
                                                                                                    '{"en": "$100K Travel Accident Insurance", "zh": "$10万旅行意外保险", "fr": "Assurance accident voyage 100 000 $", "es": "Seguro accidente viaje $100K", "ja": "$10万旅行傷害保険", "ko": "$10만 여행 상해 보험"}',
                                                                                                    '{"en": "Up to $100,000 Accidental Death & Dismemberment coverage when charging travel tickets to your Card.", "zh": "使用此卡购买机票可获最高$10万意外身故及伤残保险。", "fr": "Jusqu''à 100 000 $ décès et mutilation accidentels pour billets achetés avec la Carte.", "es": "Hasta $100,000 muerte accidental y desmembramiento al cargar boletos a su Tarjeta.", "ja": "カードで旅行チケット購入時、最大$10万の傷害死亡・後遺障害補償。", "ko": "카드로 여행 티켓 구매 시 최대 $10만 상해사망 및 후유장해 보장."}',
                                                                                                    8, 1),
                                                                                                   -- INSURANCE: Purchase Protection
                                                                                                   (61, 'INSURANCE',
                                                                                                    '{"en": "Purchase Protection 90 Days", "zh": "90天购物保护", "fr": "Protection achats 90 jours", "es": "Protección compras 90 días", "ja": "90日間購入保護", "ko": "90일 구매 보호"}',
                                                                                                    '{"en": "Purchase Protection for 90 days up to $1,000 per occurrence for accidental damage or theft.", "zh": "购物后90天内意外损坏或盗窃，每次最高$1,000保障。", "fr": "Protection achats 90 jours jusqu''à 1 000 $ par événement pour dommage accidentel ou vol.", "es": "Protección de compras 90 días hasta $1,000 por evento por daño accidental o robo.", "ja": "購入から90日間、事故破損・盗難に対し1回最大$1,000補償。", "ko": "구매 후 90일간 사고 파손 또는 도난에 대해 건당 최대 $1,000 보장."}',
                                                                                                    7, 1);

-- Business Gold Rewards Card (ID: 62)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
                                                                                                   (62, 'BEST_USE',
                                                                                                    '{"en": "Quarterly Spending Bonus", "zh": "季度消费奖励", "fr": "Bonus de dépenses trimestrielles", "es": "Bono de gastos trimestrales", "ja": "四半期消費ボーナス", "ko": "분기별 지출 보너스"}',
                                                                                                    '{"en": "Earn 10,000 bonus MR points for each quarter you spend $20,000+. Up to 40,000 extra points annually.", "zh": "每季度消费$20,000+可获10,000额外MR积分。每年最多可获40,000额外积分。", "fr": "Gagnez 10 000 pts MR bonus par trimestre si vous dépensez 20 000 $+. Jusqu''à 40 000 pts supplémentaires par an.", "es": "Gane 10,000 pts MR extra por trimestre gastando $20,000+. Hasta 40,000 pts extra anuales.", "ja": "四半期$20,000+消費で10,000ボーナスMRポイント。年間最大40,000追加ポイント。", "ko": "분기당 $20,000+ 지출 시 10,000 보너스 MR 포인트. 연간 최대 40,000 추가 포인트."}',
                                                                                                    10, 1),
                                                                                                   (62, 'REDEMPTION',
                                                                                                    '{"en": "Transfer to Aeroplan 1:1", "zh": "1:1转至Aeroplan", "fr": "Transférer vers Aeroplan 1:1", "es": "Transferir a Aeroplan 1:1", "ja": "Aeroplanへ1:1転送", "ko": "Aeroplan으로 1:1 전환"}',
                                                                                                    '{"en": "Transfer MR points 1:1 to Aeroplan, British Airways Avios, or 1:1.2 to Marriott Bonvoy for best value.", "zh": "将MR积分1:1转至Aeroplan、英航Avios，或1:1.2转至万豪以获最佳价值。", "fr": "Transférez les pts MR 1:1 vers Aeroplan, BA Avios, ou 1:1.2 vers Marriott Bonvoy.", "es": "Transfiera pts MR 1:1 a Aeroplan, BA Avios, o 1:1.2 a Marriott Bonvoy.", "ja": "MRポイントを1:1でAeroplan、BA Avios、または1:1.2でMarriott Bonvoyへ。", "ko": "MR 포인트를 1:1로 Aeroplan, BA Avios, 또는 1:1.2로 Marriott Bonvoy로 전환."}',
                                                                                                    9, 1),
                                                                                                   -- PERK: Referral Bonus
                                                                                                   (62, 'PERK',
                                                                                                    '{"en": "75,000 Points Referral Bonus", "zh": "推荐奖励75,000积分", "fr": "Bonus parrainage 75 000 pts", "es": "Bono referido 75,000 pts", "ja": "紹介ボーナス75,000ポイント", "ko": "추천 보너스 75,000 포인트"}',
                                                                                                    '{"en": "Refer business owner friends/family and earn up to 75,000 MR points annually.", "zh": "推荐商务朋友/家人，每年最高可获75,000 MR积分。", "fr": "Parrainez des amis/famille propriétaires d''entreprise, jusqu''à 75 000 pts MR/an.", "es": "Refiera amigos/familia dueños de negocio, hasta 75,000 pts MR anuales.", "ja": "ビジネスオーナーの友人/家族を紹介し、年間最大75,000 MRポイント獲得。", "ko": "사업주 친구/가족 추천 시 연간 최대 75,000 MR 포인트."}',
                                                                                                    8, 1),
                                                                                                   -- PERK: No Pre-Set Spending Limit
                                                                                                   (62, 'PERK',
                                                                                                    '{"en": "No Pre-Set Spending Limit", "zh": "无预设消费限额", "fr": "Pas de limite prédéfinie", "es": "Sin límite preestablecido", "ja": "利用限度額なし", "ko": "사전 설정 한도 없음"}',
                                                                                                    '{"en": "Dynamic Purchasing Power adapts to your business needs. No fixed credit limit.", "zh": "动态购买力根据您的业务需求调整，无固定信用额度。", "fr": "Pouvoir d''achat dynamique qui s''adapte à vos besoins commerciaux.", "es": "Poder de compra dinámico que se adapta a sus necesidades comerciales.", "ja": "ビジネスニーズに適応するダイナミックな購買力。固定限度額なし。", "ko": "비즈니스 필요에 맞게 조정되는 동적 구매력. 고정 한도 없음."}',
                                                                                                    7, 1),
                                                                                                   -- PERK: Employee Misuse Protection
                                                                                                   (62, 'PERK',
                                                                                                    '{"en": "$100K Employee Misuse Protection", "zh": "$10万员工滥用保护", "fr": "Protection abus employé 100 000 $", "es": "Protección mal uso empleado $100K", "ja": "$10万従業員不正使用保護", "ko": "$10만 직원 오용 보호"}',
                                                                                                    '{"en": "Up to $100,000 coverage for unauthorized charges by terminated employees on supplementary cards.", "zh": "附属卡被解雇员工未授权消费最高$10万保障。", "fr": "Jusqu''à 100 000 $ pour frais non autorisés par employés licenciés sur cartes supplémentaires.", "es": "Hasta $100,000 por cargos no autorizados de empleados despedidos en tarjetas suplementarias.", "ja": "解雇された従業員の追加カード不正利用に対し最大$10万補償。", "ko": "해고 직원의 추가 카드 무단 사용에 대해 최대 $10만 보장."}',
                                                                                                    6, 1),
                                                                                                   -- INSURANCE: Mobile Device Insurance
                                                                                                   (62, 'INSURANCE',
                                                                                                    '{"en": "$1,000 Mobile Device Insurance", "zh": "$1,000手机保险", "fr": "Assurance appareil mobile 1 000 $", "es": "Seguro dispositivo móvil $1,000", "ja": "$1,000モバイル保険", "ko": "$1,000 모바일 기기 보험"}',
                                                                                                    '{"en": "Up to $1,000 coverage for theft, loss, or accidental damage of mobile devices for 2 years from purchase.", "zh": "手机设备盗窃、丢失或意外损坏，自购买起2年内最高$1,000保障。", "fr": "Jusqu''à 1 000 $ pour vol, perte ou dommage accidentel d''appareils mobiles pendant 2 ans.", "es": "Hasta $1,000 por robo, pérdida o daño accidental de dispositivos móviles por 2 años.", "ja": "モバイル機器の盗難・紛失・事故破損に対し購入から2年間最大$1,000補償。", "ko": "모바일 기기 도난/분실/사고 파손에 대해 구매 후 2년간 최대 $1,000 보장."}',
                                                                                                    5, 1),
                                                                                                   -- INSURANCE: Travel Accident
                                                                                                   (62, 'INSURANCE',
                                                                                                    '{"en": "$100K Travel Accident Insurance", "zh": "$10万旅行意外保险", "fr": "Assurance accident voyage 100 000 $", "es": "Seguro accidente viaje $100K", "ja": "$10万旅行傷害保険", "ko": "$10만 여행 상해 보험"}',
                                                                                                    '{"en": "Up to $100,000 Accidental Death & Dismemberment coverage when charging travel tickets to your Card.", "zh": "使用此卡购买机票可获最高$10万意外身故及伤残保险。", "fr": "Jusqu''à 100 000 $ décès et mutilation accidentels pour billets achetés avec la Carte.", "es": "Hasta $100,000 muerte accidental y desmembramiento al cargar boletos a su Tarjeta.", "ja": "カードで旅行チケット購入時、最大$10万の傷害死亡・後遺障害補償。", "ko": "카드로 여행 티켓 구매 시 최대 $10만 상해사망 및 후유장해 보장."}',
                                                                                                    4, 1),
                                                                                                   -- INSURANCE: Car Rental & Purchase Protection
                                                                                                   (62, 'INSURANCE',
                                                                                                    '{"en": "Car Rental & Purchase Protection", "zh": "租车和购物保护", "fr": "Protection location auto et achats", "es": "Protección alquiler auto y compras", "ja": "レンタカー・購入保護", "ko": "렌터카 및 구매 보호"}',
                                                                                                    '{"en": "Car rental coverage up to 48 days ($85K MSRP), plus Purchase Protection for 90 days up to $1,000.", "zh": "租车保险最长48天（车价$8.5万内），购物保护90天内最高$1,000。", "fr": "Location auto jusqu''à 48 jours (85 000 $ PDSF), Protection achats 90 jours jusqu''à 1 000 $.", "es": "Alquiler auto hasta 48 días ($85K MSRP), Protección compras 90 días hasta $1,000.", "ja": "レンタカー最大48日（$8.5万MSRP）、購入保護90日間最大$1,000。", "ko": "렌터카 최대 48일 ($8.5만 MSRP), 구매 보호 90일간 최대 $1,000."}',
                                                                                                    3, 1),
                                                                                                   -- TRAVEL_BENEFIT: The Hotel Collection
                                                                                                   (62, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "The Hotel Collection Benefits", "zh": "精选酒店福利", "fr": "Avantages Hotel Collection", "es": "Beneficios Hotel Collection", "ja": "ホテルコレクション特典", "ko": "호텔 컬렉션 혜택"}',
                                                                                                    '{"en": "Stay 2+ nights at participating hotels: $100 USD credit, room upgrade, early check-in, late check-out.", "zh": "精选酒店连住2晚+：$100美元抵扣、房间升级、提前入住、延迟退房。", "fr": "Séjour 2+ nuits : crédit 100 $ USD, surclassement, check-in tôt, check-out tardif.", "es": "Estadía 2+ noches: crédito $100 USD, upgrade, check-in temprano, check-out tardío.", "ja": "2泊以上で$100 USDクレジット、部屋アップグレード、アーリーチェックイン、レイトチェックアウト。", "ko": "2박 이상 시 $100 USD 크레딧, 객실 업그레이드, 얼리 체크인, 레이트 체크아웃."}',
                                                                                                    2, 1),
                                                                                                   -- TRAVEL_BENEFIT: Hertz Benefits
                                                                                                   (62, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Hertz Gold Plus Rewards", "zh": "Hertz金卡会员福利", "fr": "Avantages Hertz Gold Plus", "es": "Beneficios Hertz Gold Plus", "ja": "Hertz Gold Plus特典", "ko": "Hertz Gold Plus 혜택"}',
                                                                                                    '{"en": "Hertz discount rates, free car class upgrade on 5+ day rentals, and fee-waived additional driver.", "zh": "Hertz折扣价、5天以上租车免费升级车型、免费附加驾驶员。", "fr": "Tarifs Hertz réduits, surclassement gratuit pour 5+ jours, conducteur additionnel gratuit.", "es": "Tarifas Hertz con descuento, upgrade gratis en 5+ días, conductor adicional sin cargo.", "ja": "Hertz割引、5日以上レンタルで無料アップグレード、追加ドライバー無料。", "ko": "Hertz 할인 요금, 5일 이상 렌트 시 무료 업그레이드, 추가 운전자 무료."}',
                                                                                                    1, 1);

-- Business Platinum Card (ID: 63)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
                                                                                                   (63, 'BEST_USE',
                                                                                                    '{"en": "1.25x on Everything", "zh": "所有消费1.25倍积分", "fr": "1,25x sur tout", "es": "1.25x en todo", "ja": "すべての購入で1.25倍", "ko": "모든 구매 1.25배"}',
                                                                                                    '{"en": "Earn 1.25 MR points per $1 on all purchases. Best for high-volume business spending.", "zh": "所有消费每$1赚1.25个MR积分。适合高消费量的商务支出。", "fr": "Gagnez 1,25 pt MR par dollar sur tous les achats. Idéal pour les dépenses commerciales élevées.", "es": "Gane 1.25 pts MR por $1 en todas las compras. Ideal para gastos comerciales altos.", "ja": "すべての購入で$1あたり1.25 MRポイント。高額ビジネス支出に最適。", "ko": "모든 구매에서 $1당 1.25 MR 포인트. 대량 비즈니스 지출에 최적."}',
                                                                                                    10, 1),
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Unlimited Lounge Access", "zh": "无限贵宾室使用", "fr": "Accès illimité aux salons", "es": "Acceso ilimitado a salas", "ja": "無制限ラウンジアクセス", "ko": "무제한 라운지 이용"}',
                                                                                                    '{"en": "Access 1,400+ airport lounges including Centurion, Priority Pass, and Plaza Premium. Note: From 2027, requires $20,000 annual spend.", "zh": "可使用1,400多个机场贵宾室，包括Centurion、Priority Pass和Plaza Premium。注意：2027年起需年消费$20,000。", "fr": "Accès à 1 400+ salons dont Centurion, Priority Pass et Plaza Premium. Note : À partir de 2027, 20 000 $ de dépenses annuelles requis.", "es": "Acceso a 1,400+ salas incluyendo Centurion, Priority Pass y Plaza Premium. Nota: Desde 2027, requiere $20,000 de gasto anual.", "ja": "Centurion、Priority Pass、Plaza Premium含む1,400+空港ラウンジ利用可。注意：2027年から年間$20,000消費が必要。", "ko": "Centurion, Priority Pass, Plaza Premium 포함 1,400+ 공항 라운지 이용. 참고: 2027년부터 연간 $20,000 지출 필요."}',
                                                                                                    9, 1),
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "Hotel Elite Status", "zh": "酒店精英会员", "fr": "Statut élite hôtelier", "es": "Estatus élite de hotel", "ja": "ホテルエリートステータス", "ko": "호텔 엘리트 자격"}',
                                                                                                    '{"en": "Complimentary Marriott Bonvoy Gold and Hilton Honors Gold status included.", "zh": "包含免费万豪金卡和希尔顿金卡会员资格。", "fr": "Statut Marriott Bonvoy Gold et Hilton Honors Gold inclus.", "es": "Estatus Marriott Bonvoy Gold y Hilton Honors Gold incluidos.", "ja": "Marriott Bonvoy GoldとHilton Honors Goldステータスが含まれます。", "ko": "Marriott Bonvoy Gold 및 Hilton Honors Gold 자격 포함."}',
                                                                                                    8, 1),
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "$200 Travel Credit", "zh": "$200旅行抵扣", "fr": "Crédit voyage de 200 $", "es": "Crédito de viaje de $200", "ja": "$200旅行クレジット", "ko": "$200 여행 크레딧"}',
                                                                                                    '{"en": "Annual $200 travel credit for bookings of $200+ through American Express Travel Online.", "zh": "每年通过AMEX旅行网站预订$200+可获$200抵扣。", "fr": "Crédit voyage annuel de 200 $ pour réservations de 200 $+ via Amex Travel.", "es": "Crédito de viaje anual de $200 para reservas de $200+ a través de Amex Travel.", "ja": "Amex Travel Onlineで$200+予約時に年間$200旅行クレジット。", "ko": "Amex Travel Online에서 $200+ 예약 시 연간 $200 여행 크레딧."}',
                                                                                                    14, 1),
                                                                                                   -- PERK: Referral Bonus
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "225,000 Points Referral Bonus", "zh": "推荐奖励225,000积分", "fr": "Bonus parrainage 225 000 pts", "es": "Bono referido 225,000 pts", "ja": "紹介ボーナス225,000ポイント", "ko": "추천 보너스 225,000 포인트"}',
                                                                                                    '{"en": "Refer business owner friends/family and earn up to 225,000 MR points annually - the highest referral bonus.", "zh": "推荐商务朋友/家人，每年最高可获225,000 MR积分，最高推荐奖励。", "fr": "Parrainez des propriétaires d''entreprise, jusqu''à 225 000 pts MR/an - le bonus le plus élevé.", "es": "Refiera dueños de negocio, hasta 225,000 pts MR anuales - el bono más alto.", "ja": "ビジネスオーナーを紹介し、年間最大225,000 MRポイント - 最高の紹介ボーナス。", "ko": "사업주 추천 시 연간 최대 225,000 MR 포인트 - 최고 추천 보너스."}',
                                                                                                    13, 1),
                                                                                                   -- PERK: Business Credits
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "$620 Annual Business Credits", "zh": "$620年度商务抵扣", "fr": "Crédits commerciaux 620 $/an", "es": "Créditos comerciales $620/año", "ja": "$620年間ビジネスクレジット", "ko": "$620 연간 비즈니스 크레딧"}',
                                                                                                    '{"en": "Up to $200 Dell credits + $300 Indeed credits annually for business purchases.", "zh": "每年最高$200 Dell抵扣 + $300 Indeed抵扣，用于商务采购。", "fr": "Jusqu''à 200 $ Dell + 300 $ Indeed par an pour achats commerciaux.", "es": "Hasta $200 Dell + $300 Indeed anuales para compras comerciales.", "ja": "年間最大$200 Dell + $300 Indeedクレジット、ビジネス購入用。", "ko": "비즈니스 구매용 연간 최대 $200 Dell + $300 Indeed 크레딧."}',
                                                                                                    12, 1),
                                                                                                   -- PERK: Wireless Credits
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "$120 Annual Wireless Credits", "zh": "$120年度无线抵扣", "fr": "Crédits sans fil 120 $/an", "es": "Créditos inalámbricos $120/año", "ja": "$120年間ワイヤレスクレジット", "ko": "$120 연간 무선 크레딧"}',
                                                                                                    '{"en": "Earn $10 monthly statement credit when spending $10+ with eligible wireless providers.", "zh": "每月在符合条件的无线运营商消费$10+可获$10账单抵扣。", "fr": "Gagnez 10 $ de crédit mensuel en dépensant 10 $+ chez les fournisseurs sans fil éligibles.", "es": "Gane $10 de crédito mensual gastando $10+ con proveedores inalámbricos elegibles.", "ja": "対象ワイヤレスプロバイダーで月$10+消費で$10クレジット。", "ko": "적격 무선 통신사에서 월 $10+ 사용 시 $10 크레딧."}',
                                                                                                    11, 1),
                                                                                                   -- PERK: Employee Misuse Protection
                                                                                                   (63, 'PERK',
                                                                                                    '{"en": "$100K Employee Misuse Protection", "zh": "$10万员工滥用保护", "fr": "Protection abus employé 100 000 $", "es": "Protección mal uso empleado $100K", "ja": "$10万従業員不正使用保護", "ko": "$10만 직원 오용 보호"}',
                                                                                                    '{"en": "Up to $100,000 coverage for unauthorized charges by terminated employees on supplementary cards.", "zh": "附属卡被解雇员工未授权消费最高$10万保障。", "fr": "Jusqu''à 100 000 $ pour frais non autorisés par employés licenciés.", "es": "Hasta $100,000 por cargos no autorizados de empleados despedidos.", "ja": "解雇された従業員の追加カード不正利用に対し最大$10万補償。", "ko": "해고 직원의 추가 카드 무단 사용에 대해 최대 $10만 보장."}',
                                                                                                    10, 1),
                                                                                                   -- TRAVEL_BENEFIT: Fine Hotels + Resorts
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Fine Hotels + Resorts", "zh": "精品酒店及度假村", "fr": "Fine Hotels + Resorts", "es": "Fine Hotels + Resorts", "ja": "ファインホテル+リゾート", "ko": "파인 호텔 + 리조트"}',
                                                                                                    '{"en": "Book 1,600+ luxury properties via Amex Travel: ~$550 USD value including breakfast, room upgrade, 4pm late checkout.", "zh": "通过Amex Travel预订1,600+豪华酒店：约$550美元价值，含早餐、房间升级、下午4点延迟退房。", "fr": "Réservez 1 600+ propriétés de luxe : ~550 $ USD incluant petit-déjeuner, surclassement, départ tardif 16h.", "es": "Reserve 1,600+ propiedades de lujo: ~$550 USD incluyendo desayuno, upgrade, checkout tardío 4pm.", "ja": "1,600+高級物件予約：朝食、部屋アップグレード、16時レイトチェックアウト含む約$550 USD相当。", "ko": "1,600+ 럭셔리 호텔 예약: 조식, 객실 업그레이드, 오후 4시 레이트 체크아웃 포함 약 $550 USD 가치."}',
                                                                                                    9, 1),
                                                                                                   -- TRAVEL_BENEFIT: The Hotel Collection
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "The Hotel Collection Benefits", "zh": "精选酒店福利", "fr": "Avantages Hotel Collection", "es": "Beneficios Hotel Collection", "ja": "ホテルコレクション特典", "ko": "호텔 컬렉션 혜택"}',
                                                                                                    '{"en": "Stay 2+ nights at participating hotels: $100 USD credit, room upgrade, early check-in, late check-out.", "zh": "精选酒店连住2晚+：$100美元抵扣、房间升级、提前入住、延迟退房。", "fr": "Séjour 2+ nuits : crédit 100 $ USD, surclassement, check-in tôt, check-out tardif.", "es": "Estadía 2+ noches: crédito $100 USD, upgrade, check-in temprano, check-out tardío.", "ja": "2泊以上で$100 USDクレジット、部屋アップグレード、アーリーチェックイン、レイトチェックアウト。", "ko": "2박 이상 시 $100 USD 크레딧, 객실 업그레이드, 얼리 체크인, 레이트 체크아웃."}',
                                                                                                    8, 1),
                                                                                                   -- TRAVEL_BENEFIT: Toronto Pearson VIP
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Toronto Pearson VIP Benefits", "zh": "多伦多皮尔逊VIP福利", "fr": "Avantages VIP Toronto Pearson", "es": "Beneficios VIP Toronto Pearson", "ja": "トロント・ピアソンVIP特典", "ko": "토론토 피어슨 VIP 혜택"}',
                                                                                                    '{"en": "Complimentary valet service at T1, 15% parking discount, Priority Security Lane access at Pearson.", "zh": "T1航站楼免费代客泊车、15%停车折扣、皮尔逊机场优先安检通道。", "fr": "Service voiturier gratuit T1, 15% réduction stationnement, accès prioritaire sécurité à Pearson.", "es": "Valet gratis T1, 15% descuento estacionamiento, acceso prioritario seguridad en Pearson.", "ja": "T1無料バレー、駐車15%オフ、ピアソン優先セキュリティレーン。", "ko": "T1 무료 발렛, 15% 주차 할인, 피어슨 우선 보안 레인."}',
                                                                                                    7, 1),
                                                                                                   -- TRAVEL_BENEFIT: $100 NEXUS Credit
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "$100 NEXUS Credit", "zh": "$100 NEXUS抵扣", "fr": "Crédit NEXUS 100 $", "es": "Crédito NEXUS $100", "ja": "$100 NEXUSクレジット", "ko": "$100 NEXUS 크레딧"}',
                                                                                                    '{"en": "Up to $100 statement credit for NEXUS application or renewal fees every 4 years.", "zh": "每4年NEXUS申请或续期费用最高$100账单抵扣。", "fr": "Jusqu''à 100 $ de crédit pour demande ou renouvellement NEXUS tous les 4 ans.", "es": "Hasta $100 de crédito para solicitud o renovación NEXUS cada 4 años.", "ja": "4年ごとにNEXUS申請・更新費用に最大$100クレジット。", "ko": "4년마다 NEXUS 신청/갱신 비용에 최대 $100 크레딧."}',
                                                                                                    6, 1),
                                                                                                   -- TRAVEL_BENEFIT: Premium Airport Transfer
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Premium Airport Transfer", "zh": "高端机场接送", "fr": "Transfert aéroport premium", "es": "Traslado aeropuerto premium", "ja": "プレミアム空港送迎", "ko": "프리미엄 공항 이동"}',
                                                                                                    '{"en": "Up to 6 complimentary airport transfers per year when booking eligible first/business class + hotel.", "zh": "预订符合条件的头等舱/商务舱+酒店时，每年最多6次免费机场接送。", "fr": "Jusqu''à 6 transferts aéroport gratuits/an pour réservations première/affaires + hôtel.", "es": "Hasta 6 traslados aeropuerto gratis/año al reservar primera/business + hotel.", "ja": "対象ファースト/ビジネスクラス+ホテル予約で年間最大6回無料空港送迎。", "ko": "적격 일등석/비즈니스석 + 호텔 예약 시 연간 최대 6회 무료 공항 이동."}',
                                                                                                    5, 1),
                                                                                                   -- TRAVEL_BENEFIT: International Airline Program
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "International Airline Program", "zh": "国际航空计划", "fr": "Programme aérien international", "es": "Programa aéreo internacional", "ja": "国際航空プログラム", "ko": "국제 항공 프로그램"}',
                                                                                                    '{"en": "Discounted base fares on First, Business, and Premium Economy class for you + up to 7 companions.", "zh": "头等舱、商务舱、超级经济舱基础票价折扣，本人+最多7位同行人。", "fr": "Tarifs réduits Première, Affaires, Économie Premium pour vous + 7 accompagnateurs.", "es": "Tarifas con descuento Primera, Business, Premium Economy para usted + 7 acompañantes.", "ja": "ファースト、ビジネス、プレミアムエコノミーの割引運賃、本人+最大7名。", "ko": "일등석, 비즈니스, 프리미엄 이코노미 할인 요금, 본인 + 최대 7명."}',
                                                                                                    4, 1),
                                                                                                   -- TRAVEL_BENEFIT: Hertz & Avis
                                                                                                   (63, 'TRAVEL_BENEFIT',
                                                                                                    '{"en": "Hertz Five Star & Avis Status", "zh": "Hertz五星及Avis会员", "fr": "Hertz Five Star et Avis", "es": "Hertz Five Star y Avis", "ja": "Hertz Five Star & Avisステータス", "ko": "Hertz Five Star 및 Avis 자격"}',
                                                                                                    '{"en": "Hertz Gold Plus Five Star: upgrades, discounts, 4hr grace. Plus complimentary Avis status.", "zh": "Hertz Gold Plus五星：升级、折扣、4小时宽限。另享Avis免费会员。", "fr": "Hertz Gold Plus Five Star : surclassements, réductions, délai 4h. Statut Avis gratuit.", "es": "Hertz Gold Plus Five Star: upgrades, descuentos, 4h gracia. Estatus Avis gratis.", "ja": "Hertz Gold Plus Five Star：アップグレード、割引、4時間猶予。Avisステータス無料。", "ko": "Hertz Gold Plus Five Star: 업그레이드, 할인, 4시간 유예. Avis 자격 무료."}',
                                                                                                    3, 1),
                                                                                                   -- INSURANCE: Emergency Medical
                                                                                                   (63, 'INSURANCE',
                                                                                                    '{"en": "$5M Emergency Medical", "zh": "$500万紧急医疗", "fr": "5 M$ urgences médicales", "es": "$5M emergencias médicas", "ja": "$500万緊急医療", "ko": "$500만 응급 의료"}',
                                                                                                    '{"en": "Up to $5 million emergency medical coverage for the first 15 days of your trip (under age 65).", "zh": "旅行前15天最高$500万紧急医疗保险（65岁以下）。", "fr": "Jusqu''à 5 M$ de couverture médicale d''urgence pour les 15 premiers jours (moins de 65 ans).", "es": "Hasta $5M de cobertura médica de emergencia para los primeros 15 días (menores de 65).", "ja": "旅行最初の15日間、最大$500万緊急医療補償（65歳未満）。", "ko": "여행 첫 15일간 최대 $500만 응급 의료 보장 (65세 미만)."}',
                                                                                                    2, 1),
                                                                                                   -- INSURANCE: Travel Accident & Mobile
                                                                                                   (63, 'INSURANCE',
                                                                                                    '{"en": "$500K Accident + $1.5K Mobile", "zh": "$50万意外+$1,500手机", "fr": "500 000 $ accident + 1 500 $ mobile", "es": "$500K accidente + $1,500 móvil", "ja": "$50万傷害+$1,500モバイル", "ko": "$50만 상해 + $1,500 모바일"}',
                                                                                                    '{"en": "$500,000 Travel Accident insurance plus $1,500 Mobile Device coverage for 2 years from purchase.", "zh": "$50万旅行意外保险，加$1,500手机保险（购买起2年）。", "fr": "500 000 $ assurance accident voyage + 1 500 $ couverture mobile pendant 2 ans.", "es": "$500,000 seguro accidente viaje + $1,500 cobertura móvil por 2 años.", "ja": "$50万旅行傷害保険 + $1,500モバイル保険（購入から2年）。", "ko": "$50만 여행 상해 보험 + $1,500 모바일 보장 (구매 후 2년)."}',
                                                                                                    1, 1);

-- Green Card (ID: 64)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
                                                                                                   (64, 'BEST_USE',
                                                                                                    '{"en": "No Annual Fee Entry Card", "zh": "无年费入门卡", "fr": "Carte d''entrée sans frais", "es": "Tarjeta de entrada sin cuota", "ja": "年会費無料エントリーカード", "ko": "연회비 없는 입문 카드"}',
                                                                                                    '{"en": "Good entry-level MR earning card with no annual fee. Earn 2x on hotel and car rental via Amex Travel.", "zh": "无年费的MR入门卡。通过AMEX旅行预订酒店和租车可获2倍积分。", "fr": "Bonne carte MR d''entrée sans frais annuels. Gagnez 2x sur hôtel et location via Amex Travel.", "es": "Buena tarjeta MR de entrada sin cuota anual. Gane 2x en hotel y auto via Amex Travel.", "ja": "年会費無料のMRエントリーカード。Amex Travelでホテル・レンタカー2倍。", "ko": "연회비 없는 MR 입문 카드. Amex Travel에서 호텔/렌터카 2배."}',
                                                                                                    10, 1),
                                                                                                   (64, 'REDEMPTION',
                                                                                                    '{"en": "Transfer to Partners", "zh": "转至合作伙伴", "fr": "Transférer aux partenaires", "es": "Transferir a socios", "ja": "パートナーへ転送", "ko": "파트너로 전환"}',
                                                                                                    '{"en": "Transfer MR points 1:1 to Aeroplan, British Airways Avios, Asia Miles, or Marriott Bonvoy.", "zh": "将MR积分1:1转至Aeroplan、英航Avios、亚洲万里通或万豪。", "fr": "Transférez les pts MR 1:1 vers Aeroplan, BA Avios, Asia Miles ou Marriott Bonvoy.", "es": "Transfiera pts MR 1:1 a Aeroplan, BA Avios, Asia Miles o Marriott Bonvoy.", "ja": "MRポイントを1:1でAeroplan、BA Avios、Asia Miles、Marriott Bonvoyへ。", "ko": "MR 포인트를 1:1로 Aeroplan, BA Avios, Asia Miles, Marriott Bonvoy로 전환."}',
                                                                                                    9, 1);

-- Marriott Bonvoy Card (ID: 65)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
    -- BEST_USE: Earning Points
    (65, 'BEST_USE',
     '{"en": "5x Marriott + 2x Everything Else", "zh": "万豪5倍+其他2倍", "fr": "5x Marriott + 2x tout le reste", "es": "5x Marriott + 2x todo lo demás", "ja": "マリオット5倍+その他2倍", "ko": "메리어트 5배 + 기타 2배"}',
     '{"en": "Earn 5x points at participating Marriott Bonvoy hotels (plus member points), 2x on all other purchases including dining, groceries and online shopping.", "zh": "万豪酒店消费5倍积分（加会员积分），其他所有消费（餐饮、杂货、网购等）2倍积分。", "fr": "Gagnez 5x aux hôtels Marriott (plus pts membre), 2x sur tous les autres achats dont restos, épicerie et achats en ligne.", "es": "Gane 5x en hoteles Marriott (más pts miembro), 2x en todas las demás compras incluyendo comida, supermercado y compras en línea.", "ja": "Marriottホテルで5倍（会員ポイント加算）、飲食・食料品・オンラインショッピング等その他すべて2倍。", "ko": "메리어트 호텔 5배 (회원 포인트 추가), 식당/식료품/온라인 쇼핑 등 기타 모두 2배."}',
     14, 1),
    -- PERK: Elite Status
    (65, 'PERK',
     '{"en": "Silver Elite → Gold Elite Status", "zh": "银卡→金卡会员升级", "fr": "Statut Silver Elite → Gold Elite", "es": "Estatus Silver Elite → Gold Elite", "ja": "シルバーエリート→ゴールドエリート", "ko": "실버 엘리트 → 골드 엘리트"}',
     '{"en": "Automatic Silver Elite status. Upgrade to Gold Elite after $30,000/year spend or 10 qualifying nights + 15 Elite Night Credits from card.", "zh": "自动获得银卡会员。年消费$30,000或10个符合条件的入住夜+卡片15晚房晚后升级为金卡。", "fr": "Statut Silver Elite automatique. Passez à Gold Elite après 30 000 $/an ou 10 nuits qualifiantes + 15 crédits de la carte.", "es": "Estatus Silver Elite automático. Upgrade a Gold Elite después de $30,000/año o 10 noches calificantes + 15 créditos de la tarjeta.", "ja": "自動シルバーエリート。年間$30,000消費または対象10泊+カードの15ナイトクレジットでゴールドエリートへ。", "ko": "자동 실버 엘리트. 연간 $30,000 지출 또는 적격 10박 + 카드 15나이트 크레딧으로 골드 엘리트 승급."}',
     13, 1),
    -- PERK: 15 Elite Night Credits
    (65, 'PERK',
     '{"en": "15 Elite Night Credits", "zh": "15晚精英房晚", "fr": "15 nuits élite", "es": "15 noches élite", "ja": "15エリートナイトクレジット", "ko": "15 엘리트 나이트 크레딧"}',
     '{"en": "Receive 15 Elite Night Credits annually toward Marriott Bonvoy elite status qualification.", "zh": "每年获得15个精英房晚，助力升级万豪会员等级。", "fr": "Recevez 15 crédits de nuits élite par an pour la qualification au statut Marriott Bonvoy.", "es": "Reciba 15 créditos de noches élite anuales para la calificación de estatus Marriott Bonvoy.", "ja": "年間15エリートナイトクレジットでMarriott Bonvoyステータス資格取得に貢献。", "ko": "연간 15 엘리트 나이트 크레딧으로 메리어트 본보이 자격 취득에 기여."}',
     12, 1),
    -- REDEMPTION: Free Nights
    (65, 'REDEMPTION',
     '{"en": "Free Nights at 7,000+ Hotels", "zh": "7,000+酒店免费住宿", "fr": "Nuits gratuites dans 7 000+ hôtels", "es": "Noches gratis en 7,000+ hoteles", "ja": "7,000+ホテルで無料宿泊", "ko": "7,000+ 호텔 무료 숙박"}',
     '{"en": "Redeem points for free nights with no blackout dates at 30+ hotel brands and 7,000+ hotels including Ritz-Carlton, St. Regis, W Hotels, JW Marriott, Westin, Sheraton.", "zh": "在30+酒店品牌、7,000+酒店兑换免费住宿，无黑日期，包括丽思卡尔顿、瑞吉、W酒店、JW万豪、威斯汀、喜来登。", "fr": "Échangez vos points contre des nuits gratuites sans dates bloquées dans 30+ marques et 7 000+ hôtels dont Ritz-Carlton, St. Regis, W Hotels.", "es": "Canjee puntos por noches gratis sin fechas restringidas en 30+ marcas y 7,000+ hoteles incluyendo Ritz-Carlton, St. Regis, W Hotels.", "ja": "30+ブランド、7,000+ホテルでポイントを無料宿泊に交換。ブラックアウト日なし。Ritz-Carlton、St. Regis、W Hotels等。", "ko": "30+ 브랜드, 7,000+ 호텔에서 블랙아웃 없이 무료 숙박 교환. Ritz-Carlton, St. Regis, W Hotels 등."}',
     11, 1),
    -- REDEMPTION: Airline Transfer
    (65, 'REDEMPTION',
     '{"en": "5,000 Bonus Miles on Transfer", "zh": "转点5,000里程奖励", "fr": "5 000 miles bonus au transfert", "es": "5,000 millas bonus al transferir", "ja": "転送で5,000ボーナスマイル", "ko": "전환 시 5,000 보너스 마일"}',
     '{"en": "Transfer points to frequent flyer miles with a wide selection of airlines. Receive 5,000 bonus miles when you transfer 60,000 points.", "zh": "可将积分转至多家航司里程计划。转60,000积分可额外获得5,000里程奖励。", "fr": "Transférez vos points vers les miles de nombreuses compagnies aériennes. Recevez 5 000 miles bonus en transférant 60 000 pts.", "es": "Transfiera puntos a millas de aerolíneas con amplia selección. Reciba 5,000 millas bonus al transferir 60,000 puntos.", "ja": "多数の航空会社マイルに転送可能。60,000ポイント転送で5,000ボーナスマイル獲得。", "ko": "다양한 항공사 마일로 전환 가능. 60,000 포인트 전환 시 5,000 보너스 마일."}',
     10, 1),
    -- INSURANCE: Travel Emergency Assistance
    (65, 'INSURANCE',
     '{"en": "24/7 Travel Emergency Assistance", "zh": "24/7旅行紧急援助", "fr": "Assistance voyage urgence 24/7", "es": "Asistencia emergencia viaje 24/7", "ja": "24/7旅行緊急アシスタンス", "ko": "24/7 여행 응급 지원"}',
     '{"en": "Access out-of-town worldwide emergency medical assistance services and legal referrals by phone, 24/7/365.", "zh": "全年无休24/7电话获取全球异地紧急医疗援助服务和法律咨询。", "fr": "Accédez aux services d''assistance médicale d''urgence et références juridiques par téléphone 24/7/365.", "es": "Acceda a servicios de asistencia médica de emergencia y referencias legales por teléfono 24/7/365.", "ja": "24時間365日、海外での緊急医療支援サービスと法的紹介を電話で利用可能。", "ko": "24/7/365 전화로 해외 응급 의료 지원 서비스 및 법적 상담 이용 가능."}',
     9, 1),
    -- INSURANCE: Travel Accident
    (65, 'INSURANCE',
     '{"en": "$500K Travel Accident Insurance", "zh": "$50万旅行意外保险", "fr": "Assurance accident voyage 500 000 $", "es": "Seguro accidente viaje $500K", "ja": "$50万旅行傷害保険", "ko": "$50만 여행 상해 보험"}',
     '{"en": "Up to $500,000 Accidental Death & Dismemberment coverage when you fully charge plane, train, ship, or bus tickets to your Card.", "zh": "使用此卡全额支付飞机、火车、轮船或巴士票可获最高$50万意外身故及伤残保险。", "fr": "Jusqu''à 500 000 $ décès et mutilation accidentels pour billets avion, train, bateau ou bus payés avec la Carte.", "es": "Hasta $500,000 muerte accidental y desmembramiento al cargar boletos de avión, tren, barco o bus a su Tarjeta.", "ja": "カードで飛行機、電車、船、バスのチケットを全額支払った場合、最大$50万の傷害死亡・後遺障害補償。", "ko": "카드로 비행기, 기차, 선박, 버스 티켓 전액 결제 시 최대 $50만 상해사망 및 후유장해 보장."}',
     8, 1),
    -- INSURANCE: Car Rental
    (65, 'INSURANCE',
     '{"en": "Car Rental Theft & Damage Insurance", "zh": "租车盗窃损坏保险", "fr": "Assurance vol/dommages location auto", "es": "Seguro robo/daños alquiler auto", "ja": "レンタカー盗難・損害保険", "ko": "렌터카 도난/손상 보험"}',
     '{"en": "Coverage for theft, loss and damage of rental cars with MSRP up to $85,000 for rentals of 48 days or less. Decline the rental agency CDW/LDW.", "zh": "租车48天以内、车价$8.5万以内的租车盗窃、丢失和损坏保险。需拒绝租车公司的CDW/LDW。", "fr": "Couverture vol, perte et dommages pour locations jusqu''à 48 jours, PDSF jusqu''à 85 000 $. Refusez le CDW/LDW.", "es": "Cobertura por robo, pérdida y daños para alquileres de hasta 48 días, MSRP hasta $85,000. Rechace el CDW/LDW.", "ja": "48日以内のレンタル、MSRP $8.5万以下の車両の盗難・紛失・損害補償。CDW/LDWは辞退必要。", "ko": "48일 이하 렌트, MSRP $8.5만 이하 차량 도난/분실/손상 보장. 렌터카 CDW/LDW 거절 필요."}',
     7, 1),
    -- INSURANCE: Flight & Baggage Delay
    (65, 'INSURANCE',
     '{"en": "Flight & Baggage Delay Insurance", "zh": "航班和行李延误保险", "fr": "Assurance retard vol/bagages", "es": "Seguro retraso vuelo/equipaje", "ja": "フライト・手荷物遅延保険", "ko": "항공편/수하물 지연 보험"}',
     '{"en": "Flight delay 4+ hours: up to $500 for accommodations and meals. Baggage delay 6+ hours: up to $500 for essential items within 4 days. Combined max $500.", "zh": "航班延误4小时+：住宿和餐饮最高$500。行李延误6小时+：4天内必需品最高$500。合计最高$500。", "fr": "Retard vol 4h+ : jusqu''à 500 $ hébergement/repas. Retard bagages 6h+ : jusqu''à 500 $ articles essentiels sous 4 jours. Max combiné 500 $.", "es": "Retraso vuelo 4h+: hasta $500 alojamiento/comidas. Retraso equipaje 6h+: hasta $500 artículos esenciales en 4 días. Máx combinado $500.", "ja": "フライト4時間以上遅延：宿泊・食事最大$500。手荷物6時間以上遅延：4日以内の必需品最大$500。合計最大$500。", "ko": "항공편 4시간+ 지연: 숙박/식사 최대 $500. 수하물 6시간+ 지연: 4일 내 필수품 최대 $500. 합산 최대 $500."}',
     6, 1),
    -- INSURANCE: Lost/Stolen Baggage & Hotel Burglary
    (65, 'INSURANCE',
     '{"en": "Baggage & Hotel Burglary Insurance", "zh": "行李丢失和酒店盗窃保险", "fr": "Assurance bagages perdus/vol hôtel", "es": "Seguro equipaje perdido/robo hotel", "ja": "手荷物紛失・ホテル盗難保険", "ko": "수하물 분실/호텔 도난 보험"}',
     '{"en": "Lost or stolen baggage: up to $500 per trip for checked and carry-on bags. Hotel burglary: up to $500 for personal items if your room is broken into.", "zh": "行李丢失或被盗：托运和手提行李每次旅行最高$500。酒店盗窃：房间被闯入时个人物品最高$500。", "fr": "Bagages perdus/volés : jusqu''à 500 $/voyage. Vol à l''hôtel : jusqu''à 500 $ pour effets personnels si effraction.", "es": "Equipaje perdido/robado: hasta $500/viaje. Robo hotel: hasta $500 por artículos personales si hay robo.", "ja": "手荷物紛失・盗難：預け・機内持込み荷物、1旅行最大$500。ホテル侵入盗：個人物品最大$500。", "ko": "수하물 분실/도난: 위탁/기내 수하물 여행당 최대 $500. 호텔 침입 도난: 개인 물품 최대 $500."}',
     5, 1),
    -- INSURANCE: Purchase & Warranty Protection
    (65, 'INSURANCE',
     '{"en": "Purchase & Warranty Protection", "zh": "购物和保修保护", "fr": "Protection achats et garantie", "es": "Protección compras y garantía", "ja": "購入・保証保護", "ko": "구매 및 보증 보호"}',
     '{"en": "Purchase Protection: 90 days coverage up to $1,000 per occurrence for accidental damage or theft. Buyer''s Assurance: extends manufacturer warranty by 1 year.", "zh": "购物保护：90天内意外损坏或盗窃每次最高$1,000。延保保障：制造商保修延长1年。", "fr": "Protection achats : 90 jours jusqu''à 1 000 $/événement. Assurance acheteur : prolonge la garantie fabricant d''1 an.", "es": "Protección compras: 90 días hasta $1,000/evento. Garantía comprador: extiende garantía fabricante 1 año.", "ja": "購入保護：90日間、事故破損・盗難1回最大$1,000。保証延長：メーカー保証を1年延長。", "ko": "구매 보호: 90일간 사고 파손/도난 건당 최대 $1,000. 보증 연장: 제조사 보증 1년 연장."}',
     4, 1);

-- Marriott Bonvoy Business Card (ID: 66)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
    -- BEST_USE: Earning Points
    (66, 'BEST_USE',
     '{"en": "5x Marriott + 3x Dining/Gas/Travel", "zh": "万豪5倍+餐饮/加油/旅行3倍", "fr": "5x Marriott + 3x resto/essence/voyage", "es": "5x Marriott + 3x comida/gas/viaje", "ja": "マリオット5倍+飲食/ガス/旅行3倍", "ko": "메리어트 5배 + 식당/주유/여행 3배"}',
     '{"en": "Earn 5x points at participating Marriott Bonvoy properties, 3x on eligible gas, dining and travel, 2x on all other purchases.", "zh": "万豪酒店5倍积分，加油、餐饮、旅行3倍，其他消费2倍。", "fr": "Gagnez 5x aux hôtels Marriott, 3x sur essence, restos et voyages éligibles, 2x sur tout le reste.", "es": "Gane 5x en hoteles Marriott, 3x en gas, comida y viajes elegibles, 2x en todo lo demás.", "ja": "Marriottで5倍、対象のガソリン・飲食・旅行で3倍、その他すべて2倍。", "ko": "메리어트 5배, 적격 주유/식당/여행 3배, 기타 모두 2배."}',
     12, 1),
    -- REDEMPTION: Transfer Bonus
    (66, 'REDEMPTION',
     '{"en": "5,000 Bonus Miles on Transfer", "zh": "转点5,000里程奖励", "fr": "5 000 miles bonus au transfert", "es": "5,000 millas bonus al transferir", "ja": "転送で5,000ボーナスマイル", "ko": "전환 시 5,000 보너스 마일"}',
     '{"en": "Get 5,000 bonus miles when transferring 60,000 points to airline frequent flyer programs. Transfer to a wide selection of airlines.", "zh": "转60,000积分至航司里程计划可额外获得5,000里程。可转至多家航司。", "fr": "Recevez 5 000 miles bonus en transférant 60 000 pts vers les programmes aériens. Large choix de compagnies.", "es": "Obtenga 5,000 millas bonus al transferir 60,000 puntos a aerolíneas. Amplia selección de aerolíneas.", "ja": "60,000ポイントを航空会社に転送で5,000ボーナスマイル。多数の航空会社から選択可能。", "ko": "60,000 포인트 항공사 전환 시 5,000 보너스 마일. 다양한 항공사 선택 가능."}',
     11, 1),
    -- REDEMPTION: Redeem for Hotels
    (66, 'REDEMPTION',
     '{"en": "Free Nights at 6,700+ Hotels", "zh": "6,700+酒店免费住宿", "fr": "Nuits gratuites dans 6 700+ hôtels", "es": "Noches gratis en 6,700+ hoteles", "ja": "6,700+ホテルで無料宿泊", "ko": "6,700+ 호텔 무료 숙박"}',
     '{"en": "Redeem points for free nights with no blackout dates at over 6,700 extraordinary hotels including Sheraton, Westin, St. Regis, W Hotels, Le Méridien and more.", "zh": "在6,700+酒店兑换免费住宿，无黑日期限制，包括喜来登、威斯汀、瑞吉、W酒店、艾美等。", "fr": "Échangez vos points contre des nuits gratuites sans dates bloquées dans plus de 6 700 hôtels dont Sheraton, Westin, St. Regis, W Hotels.", "es": "Canjee puntos por noches gratis sin fechas restringidas en más de 6,700 hoteles incluyendo Sheraton, Westin, St. Regis, W Hotels.", "ja": "6,700+ホテルでポイントを無料宿泊に交換。ブラックアウト日なし。Sheraton、Westin、St. Regis、W Hotels等。", "ko": "6,700+ 호텔에서 블랙아웃 없이 무료 숙박 교환. Sheraton, Westin, St. Regis, W Hotels 등."}',
     10, 1),
    -- REDEMPTION: Marriott Bonvoy Moments
    (66, 'REDEMPTION',
     '{"en": "Marriott Bonvoy Moments", "zh": "万豪臻享时刻", "fr": "Marriott Bonvoy Moments", "es": "Marriott Bonvoy Moments", "ja": "Marriott Bonvoy Moments", "ko": "메리어트 본보이 모먼츠"}',
     '{"en": "Redeem points for once-in-a-lifetime experiences: meet and greets with A-list artists and athletes, backstage concert passes, pro golf clinics and more.", "zh": "用积分兑换独特体验：与明星艺人和运动员见面、后台音乐会通行证、职业高尔夫培训等。", "fr": "Échangez vos points pour des expériences uniques : rencontres avec célébrités, pass backstage, cliniques de golf pro.", "es": "Canjee puntos por experiencias únicas: encuentros con artistas y atletas, pases backstage, clínicas de golf profesional.", "ja": "ポイントで特別体験を交換：著名アーティストやアスリートとの交流、バックステージパス、プロゴルフクリニックなど。", "ko": "포인트로 특별한 경험 교환: 유명 아티스트/운동선수 만남, 백스테이지 패스, 프로 골프 클리닉 등."}',
     9, 1),
    -- PERK: Employee Misuse Protection
    (66, 'PERK',
     '{"en": "$100K Employee Misuse Protection", "zh": "$10万员工滥用保护", "fr": "Protection abus employé 100 000 $", "es": "Protección mal uso empleado $100K", "ja": "$10万従業員不正使用保護", "ko": "$10만 직원 오용 보호"}',
     '{"en": "Up to $100,000 coverage for unauthorized charges if you terminate an employee and cancel their supplementary Card within 2 business days.", "zh": "解雇员工并在2个工作日内取消其附属卡，可获最高$10万未授权消费保障。", "fr": "Jusqu''à 100 000 $ si vous licenciez un employé et annulez sa carte dans les 2 jours ouvrables.", "es": "Hasta $100,000 si despide a un empleado y cancela su tarjeta dentro de 2 días hábiles.", "ja": "従業員を解雇し2営業日以内に追加カードをキャンセルした場合、最大$10万の不正利用補償。", "ko": "직원 해고 후 2영업일 이내 추가 카드 취소 시 최대 $10만 무단 사용 보장."}',
     8, 1),
    -- PERK: Supplementary Cards
    (66, 'PERK',
     '{"en": "Supplementary Cards for Employees", "zh": "员工附属卡", "fr": "Cartes supplémentaires employés", "es": "Tarjetas suplementarias empleados", "ja": "従業員用追加カード", "ko": "직원용 추가 카드"}',
     '{"en": "Issue supplementary cards to employees to control expenses, track spending and accumulate points on your Marriott Bonvoy account.", "zh": "向员工发放附属卡，便于控制开支、追踪消费，并在您的万豪账户累积积分。", "fr": "Émettez des cartes supplémentaires aux employés pour contrôler les dépenses et accumuler des points.", "es": "Emita tarjetas suplementarias a empleados para controlar gastos y acumular puntos en su cuenta Marriott.", "ja": "従業員に追加カードを発行して経費管理、支出追跡、Marriott Bonvoyアカウントでポイント蓄積。", "ko": "직원에게 추가 카드 발급하여 비용 관리, 지출 추적, 메리어트 계정에 포인트 적립."}',
     7, 1),
    -- PERK: Payment Flexibility
    (66, 'PERK',
     '{"en": "Payment Flexibility", "zh": "灵活还款", "fr": "Flexibilité de paiement", "es": "Flexibilidad de pago", "ja": "支払い柔軟性", "ko": "결제 유연성"}',
     '{"en": "Leverage your cash flow with the option of carrying a balance or paying in full each month.", "zh": "可选择每月全额还款或分期付款，灵活管理现金流。", "fr": "Gérez votre trésorerie avec l''option de reporter le solde ou de payer en totalité chaque mois.", "es": "Administre su flujo de caja con la opción de mantener un saldo o pagar en su totalidad cada mes.", "ja": "毎月全額支払いまたは残高繰越を選択してキャッシュフローを管理。", "ko": "매월 전액 결제 또는 잔액 이월 선택으로 현금 흐름 관리."}',
     6, 1),
    -- INSURANCE: Travel Emergency Assistance
    (66, 'INSURANCE',
     '{"en": "24/7 Travel Emergency Assistance", "zh": "24/7旅行紧急援助", "fr": "Assistance voyage urgence 24/7", "es": "Asistencia emergencia viaje 24/7", "ja": "24/7旅行緊急アシスタンス", "ko": "24/7 여행 응급 지원"}',
     '{"en": "Access out-of-town worldwide emergency medical assistance services and legal referrals by phone, 24/7/365.", "zh": "全年无休24/7电话获取全球异地紧急医疗援助服务和法律咨询。", "fr": "Accédez aux services d''assistance médicale d''urgence et références juridiques par téléphone 24/7/365.", "es": "Acceda a servicios de asistencia médica de emergencia y referencias legales por teléfono 24/7/365.", "ja": "24時間365日、海外での緊急医療支援サービスと法的紹介を電話で利用可能。", "ko": "24/7/365 전화로 해외 응급 의료 지원 서비스 및 법적 상담 이용 가능."}',
     5, 1),
    -- INSURANCE: Travel Accident
    (66, 'INSURANCE',
     '{"en": "$500K Travel Accident Insurance", "zh": "$50万旅行意外保险", "fr": "Assurance accident voyage 500 000 $", "es": "Seguro accidente viaje $500K", "ja": "$50万旅行傷害保険", "ko": "$50만 여행 상해 보험"}',
     '{"en": "Up to $500,000 Accidental Death & Dismemberment coverage when you fully charge plane, train, ship, or bus tickets to your Card.", "zh": "使用此卡全额支付飞机、火车、轮船或巴士票可获最高$50万意外身故及伤残保险。", "fr": "Jusqu''à 500 000 $ décès et mutilation accidentels pour billets avion, train, bateau ou bus payés avec la Carte.", "es": "Hasta $500,000 muerte accidental y desmembramiento al cargar boletos de avión, tren, barco o bus a su Tarjeta.", "ja": "カードで飛行機、電車、船、バスのチケットを全額支払った場合、最大$50万の傷害死亡・後遺障害補償。", "ko": "카드로 비행기, 기차, 선박, 버스 티켓 전액 결제 시 최대 $50만 상해사망 및 후유장해 보장."}',
     4, 1),
    -- INSURANCE: Car Rental Insurance
    (66, 'INSURANCE',
     '{"en": "Car Rental Theft & Damage Insurance", "zh": "租车盗窃损坏保险", "fr": "Assurance vol/dommages location auto", "es": "Seguro robo/daños alquiler auto", "ja": "レンタカー盗難・損害保険", "ko": "렌터카 도난/손상 보험"}',
     '{"en": "Coverage for theft, loss and damage of rental cars with MSRP up to $85,000 for rentals of 48 days or less. Decline the rental agency CDW/LDW.", "zh": "租车48天以内、车价$8.5万以内的租车盗窃、丢失和损坏保险。需拒绝租车公司的CDW/LDW。", "fr": "Couverture vol, perte et dommages pour locations jusqu''à 48 jours, PDSF jusqu''à 85 000 $. Refusez le CDW/LDW.", "es": "Cobertura por robo, pérdida y daños para alquileres de hasta 48 días, MSRP hasta $85,000. Rechace el CDW/LDW.", "ja": "48日以内のレンタル、MSRP $8.5万以下の車両の盗難・紛失・損害補償。CDW/LDWは辞退必要。", "ko": "48일 이하 렌트, MSRP $8.5만 이하 차량 도난/분실/손상 보장. 렌터카 CDW/LDW 거절 필요."}',
     3, 1),
    -- INSURANCE: Flight & Baggage Delay
    (66, 'INSURANCE',
     '{"en": "Flight & Baggage Delay Insurance", "zh": "航班和行李延误保险", "fr": "Assurance retard vol/bagages", "es": "Seguro retraso vuelo/equipaje", "ja": "フライト・手荷物遅延保険", "ko": "항공편/수하물 지연 보험"}',
     '{"en": "Flight delay 4+ hours: up to $500 for accommodations and meals. Baggage delay 6+ hours: up to $500 for essential items within 4 days.", "zh": "航班延误4小时+：住宿和餐饮最高$500。行李延误6小时+：4天内必需品最高$500。", "fr": "Retard vol 4h+ : jusqu''à 500 $ hébergement/repas. Retard bagages 6h+ : jusqu''à 500 $ articles essentiels sous 4 jours.", "es": "Retraso vuelo 4h+: hasta $500 alojamiento/comidas. Retraso equipaje 6h+: hasta $500 artículos esenciales en 4 días.", "ja": "フライト4時間以上遅延：宿泊・食事最大$500。手荷物6時間以上遅延：4日以内の必需品最大$500。", "ko": "항공편 4시간+ 지연: 숙박/식사 최대 $500. 수하물 6시간+ 지연: 4일 내 필수품 최대 $500."}',
     2, 1),
    -- INSURANCE: Lost/Stolen Baggage & Hotel Burglary
    (66, 'INSURANCE',
     '{"en": "Baggage & Hotel Burglary Insurance", "zh": "行李丢失和酒店盗窃保险", "fr": "Assurance bagages perdus/vol hôtel", "es": "Seguro equipaje perdido/robo hotel", "ja": "手荷物紛失・ホテル盗難保険", "ko": "수하물 분실/호텔 도난 보험"}',
     '{"en": "Lost or stolen baggage: up to $500 per trip for checked and carry-on bags. Hotel burglary: up to $500 for personal items if your room is broken into.", "zh": "行李丢失或被盗：托运和手提行李每次旅行最高$500。酒店盗窃：房间被闯入时个人物品最高$500。", "fr": "Bagages perdus/volés : jusqu''à 500 $/voyage. Vol à l''hôtel : jusqu''à 500 $ pour effets personnels si effraction.", "es": "Equipaje perdido/robado: hasta $500/viaje. Robo hotel: hasta $500 por artículos personales si hay robo.", "ja": "手荷物紛失・盗難：預け・機内持込み荷物、1旅行最大$500。ホテル侵入盗：個人物品最大$500。", "ko": "수하물 분실/도난: 위탁/기내 수하물 여행당 최대 $500. 호텔 침입 도난: 개인 물품 최대 $500."}',
     1, 1),
    -- INSURANCE: Purchase Protection
    (66, 'INSURANCE',
     '{"en": "Purchase & Warranty Protection", "zh": "购物和保修保护", "fr": "Protection achats et garantie", "es": "Protección compras y garantía", "ja": "購入・保証保護", "ko": "구매 및 보증 보호"}',
     '{"en": "Purchase Protection: 90 days coverage up to $1,000 per occurrence for accidental damage or theft. Buyer''s Assurance: extends manufacturer warranty by 1 year.", "zh": "购物保护：90天内意外损坏或盗窃每次最高$1,000。延保保障：制造商保修延长1年。", "fr": "Protection achats : 90 jours jusqu''à 1 000 $/événement. Assurance acheteur : prolonge la garantie fabricant d''1 an.", "es": "Protección compras: 90 días hasta $1,000/evento. Garantía comprador: extiende garantía fabricante 1 año.", "ja": "購入保護：90日間、事故破損・盗難1回最大$1,000。保証延長：メーカー保証を1年延長。", "ko": "구매 보호: 90일간 사고 파손/도난 건당 최대 $1,000. 보증 연장: 제조사 보증 1년 연장."}',
     0, 1);

-- Aeroplan Business Reserve Card (ID: 67)
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, priority, is_active) VALUES
    -- BEST_USE: 3x Air Canada
    (67, 'BEST_USE',
     '{"en": "Maximize Air Canada Purchases", "zh": "加航消费最大化", "fr": "Maximiser les achats Air Canada", "es": "Maximizar compras Air Canada", "ja": "エアカナダ購入を最大化", "ko": "에어캐나다 구매 최대화"}',
     '{"en": "Earn 3x Aeroplan points per $1 on Air Canada and Air Canada Vacations purchases - the highest earning rate for business travel.", "zh": "加航及加航假期消费每$1获3倍Aeroplan积分，商务旅行最高返点率。", "fr": "Gagnez 3x pts Aeroplan par dollar sur Air Canada et Vacances Air Canada.", "es": "Gane 3x pts Aeroplan por $1 en Air Canada y Vacaciones Air Canada.", "ja": "Air CanadaとAir Canada Vacationsで$1あたり3倍Aeroplanポイント。", "ko": "에어 캐나다 및 에어 캐나다 베케이션 $1당 3배 에어로플랜 포인트."}',
     12, 1),
    -- BEST_USE: 2x Hotels/Cars
    (67, 'BEST_USE',
     '{"en": "Hotel & Car Rental Rewards", "zh": "酒店和租车奖励", "fr": "Récompenses hôtels et location", "es": "Recompensas de hoteles y autos", "ja": "ホテル・レンタカー報酬", "ko": "호텔 및 렌터카 리워드"}',
     '{"en": "Earn 2x Aeroplan points on eligible hotel stays and car rentals, plus 1.25x on all other purchases.", "zh": "酒店住宿和租车消费获2倍Aeroplan积分，其他消费获1.25倍积分。", "fr": "Gagnez 2x pts sur les hôtels et locations de voiture, plus 1,25x sur tous les autres achats.", "es": "Gane 2x pts en hoteles y alquiler de autos, más 1.25x en otras compras.", "ja": "ホテル・レンタカーで2倍、その他すべて1.25倍ポイント。", "ko": "호텔/렌터카 2배, 기타 모든 구매 1.25배 포인트."}',
     11, 1),
    -- PERK: Status Qualifying
    (67, 'PERK',
     '{"en": "Earn Status Qualifying Credits", "zh": "赚取精英资格积分", "fr": "Gagner des crédits de qualification", "es": "Ganar créditos de calificación", "ja": "ステータス資格クレジット獲得", "ko": "자격 크레딧 적립"}',
     '{"en": "Earn 1,000 SQM and 1 SQS for every $5,000 spent. Helps achieve Aeroplan Elite Status faster for priority benefits.", "zh": "每消费$5,000获得1,000 SQM和1 SQS。帮助更快达成Aeroplan精英会员资格。", "fr": "Gagnez 1 000 SQM et 1 SQS par 5 000 $ dépensés. Aide à obtenir le statut Élite plus rapidement.", "es": "Gane 1,000 SQM y 1 SQS por cada $5,000 gastados. Ayuda a lograr el estatus Élite más rápido.", "ja": "$5,000消費ごとに1,000 SQMと1 SQS獲得。Aeroplanエリートステータス達成を加速。", "ko": "$5,000 지출마다 1,000 SQM 및 1 SQS 적립. 에어로플랜 엘리트 자격 달성 가속화."}',
     10, 1),
    -- REDEMPTION: Companion Pass
    (67, 'REDEMPTION',
     '{"en": "Annual Worldwide Companion Pass", "zh": "年度全球同行票", "fr": "Billet accompagnateur mondial annuel", "es": "Pase de acompañante mundial anual", "ja": "年間ワールドワイドコンパニオンパス", "ko": "연간 월드와이드 동반자 패스"}',
     '{"en": "Earn a Worldwide Companion Pass after spending $25,000 annually. Companion pays only $99-$599 base fare for round-trip.", "zh": "年消费$25,000可获全球同行票。同行人仅需支付$99-$599基础票价即可获得往返机票。", "fr": "Obtenez un billet accompagnateur mondial après 25 000 $/an. Tarif de base de 99-599 $.", "es": "Obtenga pase de acompañante mundial gastando $25,000/año. Tarifa base de $99-$599.", "ja": "年間$25,000消費でワールドワイドコンパニオンパス。同行者は$99-$599基本運賃のみ。", "ko": "연간 $25,000 지출 시 월드와이드 동반자 패스. 동반자 $99-$599 기본 요금만."}',
     9, 1),
    -- TRAVEL_BENEFIT: Lounge Access
    (67, 'TRAVEL_BENEFIT',
     '{"en": "Maple Leaf Lounge Access", "zh": "枫叶贵宾室使用权", "fr": "Accès au salon Feuille d''érable", "es": "Acceso al salón Maple Leaf", "ja": "メープルリーフラウンジアクセス", "ko": "메이플 리프 라운지 이용"}',
     '{"en": "Complimentary access to Maple Leaf Lounges across North America when flying Air Canada, regardless of cabin class.", "zh": "乘坐加航时可免费使用北美枫叶贵宾室，不论舱位等级。", "fr": "Accès gratuit aux salons Feuille d''érable en Amérique du Nord sur vols Air Canada.", "es": "Acceso gratuito a salas Maple Leaf en Norteamérica en vuelos Air Canada.", "ja": "Air Canada搭乗時、キャビンクラスに関係なく北米メープルリーフラウンジ利用可。", "ko": "에어 캐나다 탑승 시 객실 등급 관계없이 북미 메이플 리프 라운지 이용."}',
     8, 1),
    -- TRAVEL_BENEFIT: Priority Services
    (67, 'TRAVEL_BENEFIT',
     '{"en": "Priority Check-in & Boarding", "zh": "优先值机和登机", "fr": "Enregistrement et embarquement prioritaires", "es": "Check-in y embarque prioritario", "ja": "優先チェックイン＆搭乗", "ko": "우선 체크인 및 탑승"}',
     '{"en": "Get Priority Zone 2 boarding, priority check-in, and free first checked bag for primary and supplementary cardholders.", "zh": "享受优先区域2登机、优先值机，主卡和附属卡持卡人均可免费托运第一件行李。", "fr": "Embarquement Zone 2, enregistrement prioritaire et 1er bagage gratuit pour titulaires principal et supplémentaires.", "es": "Embarque Zona 2, check-in prioritario y primer equipaje gratis para titulares principal y suplementarios.", "ja": "プライオリティゾーン2搭乗、優先チェックイン、主会員・追加会員の無料預け荷物。", "ko": "우선 존2 탑승, 우선 체크인, 주카드 및 추가 카드 소지자 첫 번째 수하물 무료."}',
     7, 1),
    -- TRAVEL_BENEFIT: NEXUS Credit
    (67, 'TRAVEL_BENEFIT',
     '{"en": "$100 NEXUS Credit", "zh": "$100 NEXUS抵扣", "fr": "Crédit NEXUS de 100 $", "es": "Crédito NEXUS de $100", "ja": "$100 NEXUSクレジット", "ko": "$100 NEXUS 크레딧"}',
     '{"en": "Receive a $100 credit towards NEXUS application or renewal fees for faster Canada-US border crossings.", "zh": "获得$100 NEXUS申请或续期费用抵扣，加快加美边境通关。", "fr": "Recevez 100 $ de crédit pour la demande ou le renouvellement NEXUS.", "es": "Reciba $100 de crédito para solicitud o renovación NEXUS.", "ja": "NEXUS申請・更新費用に$100クレジット。", "ko": "NEXUS 신청/갱신 비용에 $100 크레딧."}',
     6, 1),
    -- PERK: eUpgrade Extension
    (67, 'PERK',
     '{"en": "eUpgrade Validity Extension", "zh": "eUpgrade有效期延长", "fr": "Extension validité eUpgrade", "es": "Extensión validez eUpgrade", "ja": "eUpgrade有効期限延長", "ko": "eUpgrade 유효기간 연장"}',
     '{"en": "eUpgrade credits validity is extended by one additional year, giving more flexibility to use upgrades.", "zh": "eUpgrade积分有效期延长一年，提供更多使用升级的灵活性。", "fr": "La validité des crédits eUpgrade est prolongée d''un an supplémentaire.", "es": "La validez de créditos eUpgrade se extiende un año adicional.", "ja": "eUpgradeクレジットの有効期限が1年延長。アップグレード利用の柔軟性向上。", "ko": "eUpgrade 크레딧 유효기간 1년 추가 연장. 업그레이드 사용 유연성 향상."}',
     5, 1),
    -- INSURANCE: Emergency Medical
    (67, 'INSURANCE',
     '{"en": "$5M Emergency Medical", "zh": "$500万紧急医疗", "fr": "5 M$ urgences médicales", "es": "$5M emergencias médicas", "ja": "$500万緊急医療", "ko": "$500만 응급 의료"}',
     '{"en": "Up to $5 million emergency medical coverage for the first 15 days of your trip (cardholders under 65).", "zh": "旅行前15天最高$500万紧急医疗保险（65岁以下持卡人）。", "fr": "Jusqu''à 5 M$ de couverture médicale d''urgence pour les 15 premiers jours (moins de 65 ans).", "es": "Hasta $5M de cobertura médica de emergencia para los primeros 15 días (menores de 65).", "ja": "旅行最初の15日間、最大$500万緊急医療補償（65歳未満）。", "ko": "여행 첫 15일간 최대 $500만 응급 의료 보장 (65세 미만)."}',
     4, 1),
    -- INSURANCE: Trip & Car Rental
    (67, 'INSURANCE',
     '{"en": "Trip & Car Rental Insurance", "zh": "旅行和租车保险", "fr": "Assurance voyage et location auto", "es": "Seguro de viaje y alquiler de auto", "ja": "旅行・レンタカー保険", "ko": "여행 및 렌터카 보험"}',
     '{"en": "Trip cancellation/interruption up to $1,500/person, flight delay up to $1,000, and car rental coverage up to 48 days.", "zh": "旅行取消/中断每人最高$1,500、航班延误最高$1,000、租车保险最长48天。", "fr": "Annulation/interruption jusqu''à 1 500 $/personne, retard de vol jusqu''à 1 000 $, location auto jusqu''à 48 jours.", "es": "Cancelación/interrupción hasta $1,500/persona, retraso de vuelo hasta $1,000, alquiler de auto hasta 48 días.", "ja": "旅行キャンセル/中断最大$1,500/人、フライト遅延最大$1,000、レンタカー最大48日。", "ko": "여행 취소/중단 1인당 최대 $1,500, 항공편 지연 최대 $1,000, 렌터카 최대 48일."}',
     3, 1),
    -- PERK: Member Extras
    (67, 'PERK',
     '{"en": "$370 Annual Member Extras", "zh": "$370年度会员福利", "fr": "370 $ extras membres annuels", "es": "$370 extras anuales para miembros", "ja": "$370年間メンバー特典", "ko": "$370 연간 멤버 특전"}',
     '{"en": "Up to $350 in Somm & DINR credits (20% back on up to $1,750/year) plus $20 Instacart statement credits.", "zh": "最高$350 Somm & DINR返现（年消费$1,750的20%返还）加$20 Instacart账单抵扣。", "fr": "Jusqu''à 350 $ de crédits Somm & DINR (20% sur 1 750 $/an) plus 20 $ de crédits Instacart.", "es": "Hasta $350 en créditos Somm & DINR (20% en hasta $1,750/año) más $20 créditos Instacart.", "ja": "最大$350 Somm & DINRクレジット（年$1,750の20%還元）+ $20 Instacartクレジット。", "ko": "최대 $350 Somm & DINR 크레딧 (연간 $1,750의 20% 환급) + $20 Instacart 크레딧."}',
     2, 1),
    -- PERK: Referral Bonus
    (67, 'PERK',
     '{"en": "20,000 Points Referral Bonus", "zh": "推荐奖励20,000积分", "fr": "Bonus de parrainage 20 000 pts", "es": "Bono de referido 20,000 pts", "ja": "紹介ボーナス20,000ポイント", "ko": "추천 보너스 20,000 포인트"}',
     '{"en": "Earn 20,000 Aeroplan points for each approved referral, up to 150,000 points annually.", "zh": "每成功推荐一人获20,000 Aeroplan积分，每年最高150,000积分。", "fr": "Gagnez 20 000 pts Aeroplan par parrainage approuvé, jusqu''à 150 000 pts/an.", "es": "Gane 20,000 pts Aeroplan por cada referido aprobado, hasta 150,000 pts/año.", "ja": "承認された紹介ごとに20,000 Aeroplanポイント、年間最大150,000ポイント。", "ko": "승인된 추천 건당 20,000 에어로플랜 포인트, 연간 최대 150,000 포인트."}',
     1, 1),
    -- AVOID: High Annual Fee
    (67, 'AVOID',
     '{"en": "High Annual Fee", "zh": "高额年费", "fr": "Frais annuels élevés", "es": "Cuota anual alta", "ja": "高額年会費", "ko": "높은 연회비"}',
     '{"en": "The $599 annual fee ($199 per additional card) requires frequent Air Canada travel to justify the cost.", "zh": "$599年费（附属卡$199）需要频繁的加航旅行才能值回票价。", "fr": "Les frais de 599 $/an (199 $ par carte supplémentaire) nécessitent des voyages Air Canada fréquents.", "es": "La cuota de $599/año ($199 por tarjeta adicional) requiere viajes frecuentes en Air Canada.", "ja": "$599年会費（追加カード$199）はAir Canada頻繁利用者向け。", "ko": "$599 연회비 (추가 카드 $199)는 에어 캐나다 빈번한 이용 필요."}',
     0, 1),
    -- AVOID: 2026 Program Changes
    (67, 'AVOID',
     '{"en": "2026 Program Changes", "zh": "2026年计划变更", "fr": "Changements 2026", "es": "Cambios 2026", "ja": "2026年プログラム変更", "ko": "2026년 프로그램 변경"}',
     '{"en": "SQM ends Dec 31, 2025. Status Qualifying Credits (SQC) replace SQM starting Jan 1, 2026. SQM rollover converts to SQC at 5:1 ratio.", "zh": "SQM于2025年12月31日结束。2026年1月1日起SQC取代SQM。SQM结转按5:1比例转换为SQC。", "fr": "Les SQM prennent fin le 31 déc. 2025. Les SQC remplacent les SQM à partir du 1er janv. 2026. Conversion 5:1.", "es": "SQM termina el 31 dic 2025. SQC reemplaza SQM desde el 1 ene 2026. Conversión 5:1.", "ja": "SQMは2025年12月31日終了。2026年1月1日からSQCがSQMに代わる。SQM繰越は5:1でSQCに変換。", "ko": "SQM 2025년 12월 31일 종료. 2026년 1월 1일부터 SQC가 SQM 대체. SQM 이월 5:1 비율로 SQC 전환."}',
     0, 1),
    -- TRAVEL_BENEFIT: Priority Pass
    (67, 'TRAVEL_BENEFIT',
     '{"en": "Priority Pass Lounge Access", "zh": "Priority Pass贵宾室", "fr": "Accès salon Priority Pass", "es": "Acceso sala Priority Pass", "ja": "Priority Passラウンジ", "ko": "Priority Pass 라운지"}',
     '{"en": "Complimentary Priority Pass membership for access to 1,500+ airport lounges worldwide, beyond Maple Leaf Lounges.", "zh": "免费Priority Pass会员资格，可使用全球1,500+机场贵宾室，不限于枫叶贵宾室。", "fr": "Adhésion Priority Pass gratuite pour accéder à 1 500+ salons d''aéroport dans le monde.", "es": "Membresía Priority Pass gratuita para acceso a 1,500+ salas de aeropuerto en todo el mundo.", "ja": "世界1,500+空港ラウンジにアクセスできるPriority Pass会員資格が無料。", "ko": "전 세계 1,500+ 공항 라운지 이용 가능한 Priority Pass 멤버십 무료 제공."}',
     7, 1),
    -- TRAVEL_BENEFIT: Toronto Pearson Benefits
    (67, 'TRAVEL_BENEFIT',
     '{"en": "Toronto Pearson VIP Benefits", "zh": "多伦多皮尔逊VIP福利", "fr": "Avantages VIP Toronto Pearson", "es": "Beneficios VIP Toronto Pearson", "ja": "トロント・ピアソンVIP特典", "ko": "토론토 피어슨 VIP 혜택"}',
     '{"en": "Priority Security Lane access, complimentary valet service, 15% off parking and car care at Toronto Pearson Airport.", "zh": "多伦多皮尔逊机场优先安检通道、免费代客泊车、停车及汽车保养15%折扣。", "fr": "Accès prioritaire sécurité, service voiturier gratuit, 15% sur stationnement et entretien auto à Pearson.", "es": "Acceso prioritario seguridad, valet gratis, 15% descuento estacionamiento y cuidado auto en Pearson.", "ja": "ピアソン空港で優先セキュリティレーン、無料バレー、駐車・カーケア15%オフ。", "ko": "피어슨 공항 우선 보안 레인, 무료 발렛, 주차 및 차량 관리 15% 할인."}',
     6, 1),
    -- INSURANCE: Travel Accident
    (67, 'INSURANCE',
     '{"en": "$500K Travel Accident Insurance", "zh": "$50万旅行意外保险", "fr": "Assurance accident voyage 500 000 $", "es": "Seguro de accidente de viaje $500K", "ja": "$50万旅行傷害保険", "ko": "$50만 여행 상해 보험"}',
     '{"en": "Up to $500,000 Accidental Death & Dismemberment coverage when you charge travel tickets to your Card.", "zh": "使用此卡购买机票可获最高$50万意外身故及伤残保险。", "fr": "Jusqu''à 500 000 $ de couverture décès et mutilation accidentels pour billets achetés avec la Carte.", "es": "Hasta $500,000 de cobertura por muerte accidental y desmembramiento al cargar boletos a su Tarjeta.", "ja": "カードで旅行チケット購入時、最大$50万の傷害死亡・後遺障害補償。", "ko": "카드로 여행 티켓 구매 시 최대 $50만 상해사망 및 후유장해 보장."}',
     3, 1),
    -- PERK: Points Never Expire
    (67, 'PERK',
     '{"en": "Points Never Expire", "zh": "积分永不过期", "fr": "Points sans expiration", "es": "Puntos sin vencimiento", "ja": "ポイント無期限", "ko": "포인트 만료 없음"}',
     '{"en": "Your Aeroplan points will never expire as long as you remain an American Express Aeroplan Cardmember.", "zh": "只要您保持AMEX Aeroplan持卡人身份，Aeroplan积分永不过期。", "fr": "Vos points Aeroplan n''expirent jamais tant que vous êtes titulaire de carte Amex Aeroplan.", "es": "Sus puntos Aeroplan nunca vencen mientras sea titular de tarjeta Amex Aeroplan.", "ja": "Amex Aeroplanカード会員である限り、Aeroplanポイントは無期限。", "ko": "Amex Aeroplan 카드 소지 시 에어로플랜 포인트 만료 없음."}',
     5, 1),
    -- PERK: Employee Misuse Protection
    (67, 'PERK',
     '{"en": "$100K Employee Misuse Protection", "zh": "$10万员工滥用保护", "fr": "Protection abus employé 100 000 $", "es": "Protección mal uso empleado $100K", "ja": "$10万従業員不正使用保護", "ko": "$10만 직원 오용 보호"}',
     '{"en": "Business-exclusive benefit: Up to $100,000 coverage for unauthorized charges by terminated employees on supplementary cards.", "zh": "商务卡专属：附属卡被解雇员工未授权消费最高$10万保障。", "fr": "Avantage commercial exclusif : jusqu''à 100 000 $ pour frais non autorisés par employés licenciés.", "es": "Beneficio exclusivo comercial: hasta $100,000 por cargos no autorizados de empleados despedidos.", "ja": "ビジネス専用特典：解雇された従業員の追加カード不正利用に対し最大$10万補償。", "ko": "비즈니스 전용 혜택: 해고 직원의 추가 카드 무단 사용에 대해 최대 $10만 보장."}',
     4, 1);