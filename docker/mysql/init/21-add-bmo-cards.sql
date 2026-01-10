

-- 修改 credit_cards 表的 base_reward_rate 精度
ALTER TABLE credit_cards MODIFY base_reward_rate DECIMAL(6,5) DEFAULT 0.01;

-- 修改 reward_rules 表的 reward_rate 精度
ALTER TABLE reward_rules MODIFY reward_rate DECIMAL(6,5) NOT NULL;



-- ============================================
-- BMO 新增信用卡 SQL
-- 6张新卡
-- 创建时间: 2026-01-05
-- ============================================

-- ============================================
-- 1. BMO eclipse Visa Infinite Privilege
-- $599 年费，5x on travel/dining/grocery/gas/pharmacy
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'eclipse Visa Infinite Privilege', 'VISA', 599.00, 0.0067,
     '{"bonusAmount": 200000, "minSpend": 6000, "daysToComplete": 90, "description": {"en": "Up to 200,000 points + NEXUS Statement Credit + 0% intro rate on balance transfers for 12 months", "zh": "最高200,000积分 + NEXUS账单返现 + 余额转账12个月0%优惠利率", "fr": "Jusqu''à 200 000 points + crédit NEXUS + 0% sur transferts de solde pendant 12 mois", "es": "Hasta 200,000 puntos + crédito NEXUS + 0% en transferencias de saldo por 12 meses", "ko": "최대 200,000 포인트 + NEXUS 명세서 크레딧 + 잔액 이체 12개월 0% 금리", "ja": "最大200,000ポイント + NEXUSステートメントクレジット + 残高移行12ヶ月0%金利"}}',
     '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #333333 50%, #1a1a1a 100%)", "textColor": "white", "isMetallic": true}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-eclipse-visa-infinite-privilege/', 0, 1, 'POINTS', 0.0067, 'BMO Rewards');

-- ============================================
-- 2. BMO VIPorter World Elite Mastercard
-- $199 年费，Porter 航空联名卡
-- 3x Porter, 2x hotels/dining/transport/grocery, 1x other
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'VIPorter World Elite Mastercard', 'MASTERCARD', 199.00, 0.0150,
     '{"bonusAmount": 70000, "minSpend": 3000, "daysToComplete": 90, "description": {"en": "70,000 VIPorter points + companion pass (100% off base fare) + $1,000 qualifying spend + first year free", "zh": "70,000 VIPorter积分 + 同伴票(基础票价100%折扣) + $1,000资格消费 + 首年免年费", "fr": "70 000 pts VIPorter + passe accompagnateur (100% rabais tarif base) + 1 000$ dépenses admissibles + 1ère année gratuite", "es": "70,000 puntos VIPorter + pase acompañante (100% descuento tarifa base) + $1,000 gasto calificado + primer año gratis", "ko": "70,000 VIPorter 포인트 + 동반자 패스(기본 요금 100% 할인) + $1,000 적격 지출 + 첫해 무료", "ja": "70,000 VIPorterポイント + コンパニオンパス(基本運賃100%オフ) + $1,000適格支出 + 初年度無料"}}',
     '{"gradient": "linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-viporter-world-elite-mastercard/', 0, 1, 'POINTS', 0.0150, 'VIPorter');

-- ============================================
-- 3. BMO VIPorter Mastercard
-- $89 年费，Porter 航空联名卡（入门版）
-- 2x Porter, 1x gas/transit/grocery/dining/hotel, 0.5x other
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'VIPorter Mastercard', 'MASTERCARD', 89.00, 0.0075,
     '{"bonusAmount": 40000, "minSpend": 0, "daysToComplete": 90, "description": {"en": "40,000 VIPorter points + 35% off flight voucher + first year free (up to $1,800 value)", "zh": "40,000 VIPorter积分 + 35%机票折扣券 + 首年免年费（价值最高$1,800）", "fr": "40 000 pts VIPorter + bon 35% vol + 1ère année gratuite (jusqu''à 1 800$)", "es": "40,000 puntos VIPorter + cupón 35% vuelo + primer año gratis (hasta $1,800)", "ko": "40,000 VIPorter 포인트 + 35% 항공권 바우처 + 첫해 무료 (최대 $1,800 가치)", "ja": "40,000 VIPorterポイント + 35%フライトバウチャー + 初年度無料（最大$1,800相当）"}}',
     '{"gradient": "linear-gradient(135deg, #3d6a99 0%, #5a8ac4 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-viporter-mastercard/', 0, 1, 'POINTS', 0.0150, 'VIPorter');

-- ============================================
-- 4. BMO AIR MILES Mastercard
-- $0 年费，Air Miles 免年费卡
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'AIR MILES Mastercard', 'MASTERCARD', 0.00, 0.0042,
     '{"bonusAmount": 1200, "minSpend": 0, "daysToComplete": 90, "description": {"en": "1,200 AIR MILES Bonus Miles + 0.99% intro rate on balance transfers for 9 months", "zh": "1,200 AIR MILES奖励里程 + 余额转账9个月0.99%优惠利率", "fr": "1 200 milles AIR MILES bonus + taux de 0,99% sur transferts de solde pendant 9 mois", "es": "1,200 millas AIR MILES + tasa de 0.99% en transferencias de saldo por 9 meses", "ko": "1,200 AIR MILES 보너스 마일 + 잔액 이체 9개월 0.99% 우대 금리", "ja": "1,200 AIR MILESボーナスマイル + 残高移行9ヶ月0.99%優遇金利"}}',
     '{"gradient": "linear-gradient(135deg, #0066b2 0%, #004d86 100%)", "textColor": "white"}',
     'https://www.bmo.com/main/personal/credit-cards/bmo-airmiles-mastercard/', 0, 1, 'POINTS', 0.1050, 'AIR MILES');

-- ============================================
-- 5. BMO Preferred Rate Mastercard
-- $29 年费，低息卡，无奖励
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'Preferred Rate Mastercard', 'MASTERCARD', 29.00, 0.0000,
     '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": {"en": "0% intro rate on balance transfers for 9 months + first year fee waived", "zh": "余额转账9个月0%利率 + 首年免年费", "fr": "0% sur transferts de solde 9 mois + frais 1ère année annulés", "es": "0% en transferencias de saldo por 9 meses + primer año gratis", "ko": "잔액 이체 9개월 0% 금리 + 첫해 연회비 면제", "ja": "残高移行9ヶ月0%金利 + 初年度年会費無料"}}',
     '{"gradient": "linear-gradient(135deg, #4a90d9 0%, #2d6bb5 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/preferred-rate-mastercard/', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 6. BMO U.S. Dollar Mastercard
-- $49 USD 年费，美元卡，无奖励
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'U.S. Dollar Mastercard', 'MASTERCARD', 49.00, 0.0000,
     '{"bonusAmount": 0, "minSpend": 3000, "daysToComplete": 365, "description": {"en": "$49 annual fee rebated when you spend US$3,000+ annually", "zh": "年消费满$3,000美元可获得$49年费返还", "fr": "Frais annuels de 49 $ remboursés si vous dépensez 3 000 $ US+ par an", "es": "Cuota anual de $49 reembolsada al gastar US$3,000+ al año", "ko": "연간 US$3,000 이상 사용 시 $49 연회비 환급", "ja": "年間US$3,000以上利用で$49年会費キャッシュバック"}}',
     '{"gradient": "linear-gradient(135deg, #4a90d9 0%, #2d6bb5 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/us-dollar-mastercard/', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- REWARD RULES (使用子查询获取card_id)
-- ============================================

-- eclipse Visa Infinite Privilege (5x = 0.0067 × 5 = 0.0335)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.0335, NULL, '5x points on travel ($1 = 5 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.0335, NULL, '5x points on dining in and out ($1 = 5 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.0335, NULL, '5x points on groceries ($1 = 5 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.0335, NULL, '5x points on gas ($1 = 5 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'PHARMACY', 0.0335, NULL, '5x points on drugstore purchases ($1 = 5 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- VIPorter World Elite Mastercard (3x Porter, 2x hotels/dining/transport/grocery, 1x other)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.045, NULL, '3x points on Porter purchases' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'HOTEL', 0.03, NULL, '2x points on hotels' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.03, NULL, '2x points on dining' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.03, NULL, '2x points on gas & transportation' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRANSIT', 0.03, NULL, '2x points on transit' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.03, NULL, '2x points on grocery' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- VIPorter Mastercard (2x Porter, 1x gas/transit/grocery/dining/hotel)
-- 积分价值 0.015 = 1.5 cents/point，与 World Elite 版本一致
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRAVEL', 0.03, NULL, '2x points on Porter purchases ($1 = 2 pts)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GAS', 0.015, NULL, '1x points on gas & transportation ($1 = 1 pt)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'TRANSIT', 0.015, NULL, '1x points on transit ($1 = 1 pt)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.015, NULL, '1x points on groceries ($1 = 1 pt)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.015, NULL, '1x points on dining ($1 = 1 pt)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'HOTEL', 0.015, NULL, '1x points on hotel accommodations ($1 = 1 pt)' FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- AIR MILES Mastercard
-- 注意：AIR MILES Partners 3x奖励无法通过消费分类检测，已在card_usage_tips中说明
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.0084, NULL, '2x Miles at grocery stores (2 Miles per $25)' FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'WHOLESALE', 0.0084, NULL, '2x Miles at wholesale clubs like Costco (2 Miles per $25)' FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'LIQUOR', 0.0084, NULL, '2x Miles at liquor retailers (2 Miles per $25)' FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- No reward rules for Preferred Rate and U.S. Dollar Mastercard (no rewards)

-- ============================================
-- CARD USAGE TIPS (使用子查询获取card_id)
-- ============================================

-- BMO eclipse Visa Infinite Privilege (15条完整用卡攻略，6种语言)
-- BEST_USE: 5x Categories
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "5x on Daily Spending", "zh": "日常消费5倍积分", "fr": "5x sur dépenses quotidiennes", "es": "5x en gastos diarios", "ko": "일상 지출 5배 포인트", "ja": "日常支出で5倍ポイント"}',
    '{"en": "Earn 5x points on groceries, dining, drugstore, gas, and travel. Use for all daily purchases to maximize rewards.", "zh": "在超市、餐饮、药店、加油和旅行消费可获5倍积分。将此卡用于所有日常消费以最大化奖励。", "fr": "Gagnez 5x points sur épicerie, restaurants, pharmacie, essence et voyage. Utilisez pour toutes vos dépenses quotidiennes.", "es": "Gana 5x puntos en supermercados, restaurantes, farmacia, gasolina y viajes. Úsala para todas tus compras diarias.", "ko": "식료품, 외식, 약국, 주유, 여행에서 5배 포인트 적립. 모든 일상 구매에 사용하세요.", "ja": "食料品、外食、薬局、ガソリン、旅行で5倍ポイント。すべての日常購入に使用してください。"}',
    'star', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- BEST_USE: Add Authorized User for 25% bonus
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Add Authorized User for 25% Bonus", "zh": "添加副卡获25%额外积分", "fr": "Ajoutez un utilisateur pour 25% bonus", "es": "Agrega usuario autorizado para 25% extra", "ko": "추가 사용자 등록 시 25% 보너스", "ja": "追加カード会員で25%ボーナス"}',
    '{"en": "Add an authorized user to earn 25% more points on ALL purchases (6.25x on bonus categories, 1.25x on everything else).", "zh": "添加副卡持有人可在所有消费上额外获得25%积分（加成类别6.25倍，其他类别1.25倍）。", "fr": "Ajoutez un utilisateur autorisé pour 25% de points en plus sur TOUS les achats (6,25x sur catégories bonus).", "es": "Agrega un usuario autorizado para ganar 25% más puntos en TODAS las compras (6.25x en categorías bonus).", "ko": "추가 사용자 등록 시 모든 구매에서 25% 추가 포인트 적립 (보너스 카테고리 6.25배).", "ja": "追加カード会員を登録すると全購入で25%追加ポイント（ボーナスカテゴリ6.25倍）。"}',
    'users', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- PERK: $200 Anniversary Credit
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "$200 Anniversary Lifestyle Credit", "zh": "$200周年生活方式返现", "fr": "Crédit anniversaire de 200 $", "es": "Crédito aniversario de $200", "ko": "$200 기념일 라이프스타일 크레딧", "ja": "$200アニバーサリーライフスタイルクレジット"}',
    '{"en": "Receive $200 statement credit annually, effectively reducing the $599 annual fee to $399.", "zh": "每年获得$200账单返现，实际年费从$599降至$399。", "fr": "Recevez 200 $ de crédit annuellement, réduisant les frais de 599 $ à 399 $.", "es": "Recibe $200 de crédito anual, reduciendo la cuota de $599 a $399.", "ko": "매년 $200 명세서 크레딧을 받아 연회비를 $599에서 $399로 절감.", "ja": "年間$200のステートメントクレジットで、年会費$599が実質$399に。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- TRAVEL_BENEFIT: Airport Lounge Access
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'TRAVEL_BENEFIT',
    '{"en": "6 Free Airport Lounge Visits", "zh": "6次免费机场贵宾厅", "fr": "6 accès gratuits aux salons", "es": "6 visitas gratis a salas VIP", "ko": "공항 라운지 6회 무료", "ja": "空港ラウンジ6回無料"}',
    '{"en": "Visa Airport Companion membership with 6 complimentary lounge visits per year (worth $250+ USD). Enroll at visaairportcompanion.ca.", "zh": "Visa机场同行会员资格，每年6次免费贵宾厅访问（价值$250+美元）。在visaairportcompanion.ca注册。", "fr": "Adhésion Visa Airport Companion avec 6 accès gratuits aux salons par an (valeur 250 $+ USD).", "es": "Membresía Visa Airport Companion con 6 visitas gratuitas a salas VIP por año (valor $250+ USD).", "ko": "Visa 공항 컴패니언 멤버십으로 연간 6회 무료 라운지 이용 ($250+ USD 상당).", "ja": "Visa Airport Companionメンバーシップで年間6回のラウンジ無料利用（$250+ USD相当）。"}',
    'travel', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- TRAVEL_BENEFIT: Priority Security & Airport Perks
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'TRAVEL_BENEFIT',
    '{"en": "Priority Security & Airport Perks", "zh": "优先安检及机场特权", "fr": "Sécurité prioritaire et avantages aéroport", "es": "Seguridad prioritaria y beneficios de aeropuerto", "ko": "우선 보안 검색 및 공항 혜택", "ja": "優先セキュリティ＆空港特典"}',
    '{"en": "Get Priority Security Lane access, discounted airport parking and valet service at select Canadian airports.", "zh": "享受优先安检通道、机场停车及代客泊车折扣（限加拿大指定机场）。", "fr": "Accès prioritaire à la sécurité, stationnement et service de voiturier à prix réduit dans certains aéroports canadiens.", "es": "Acceso a carril de seguridad prioritario, estacionamiento y servicio de valet con descuento en aeropuertos canadienses.", "ko": "우선 보안 검색대 이용, 캐나다 공항 주차 및 발렛 서비스 할인.", "ja": "優先セキュリティレーン、カナダ空港での駐車場・バレーサービス割引。"}',
    'travel', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- TRAVEL_BENEFIT: Luxury Hotel Collection
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'TRAVEL_BENEFIT',
    '{"en": "Visa Infinite Luxury Hotels", "zh": "Visa无限豪华酒店礼遇", "fr": "Collection d''hôtels de luxe Visa Infinite", "es": "Colección de hoteles de lujo Visa Infinite", "ko": "Visa 인피니트 럭셔리 호텔", "ja": "Visa Infiniteラグジュアリーホテル"}',
    '{"en": "Access Visa Infinite Luxury Hotel Collection with exclusive benefits including complimentary breakfast, room upgrades, and late checkout.", "zh": "享受Visa无限豪华酒店系列礼遇，包括免费早餐、房型升级和延迟退房。", "fr": "Accès à la collection d''hôtels de luxe Visa Infinite avec petit-déjeuner gratuit, surclassement et départ tardif.", "es": "Acceso a la Colección de Hoteles de Lujo Visa Infinite con desayuno gratis, mejoras de habitación y salida tardía.", "ko": "Visa 인피니트 럭셔리 호텔 컬렉션 이용 - 무료 조식, 객실 업그레이드, 늦은 체크아웃.", "ja": "Visa Infiniteラグジュアリーホテルコレクション - 朝食無料、部屋アップグレード、レイトチェックアウト。"}',
    'hotel', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- PERK: Concierge Service
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "24/7 Concierge Service", "zh": "24/7礼宾服务", "fr": "Service de conciergerie 24/7", "es": "Servicio de conserjería 24/7", "ko": "24/7 컨시어지 서비스", "ja": "24時間コンシェルジュサービス"}',
    '{"en": "Visa Infinite Privilege Concierge - your personal assistant for travel bookings, restaurant reservations, event tickets, and more.", "zh": "Visa无限特权礼宾服务 - 您的私人助理，可预订旅行、餐厅、活动门票等。", "fr": "Concierge Visa Infinite Privilege - votre assistant personnel pour réservations de voyage, restaurants et billets.", "es": "Conserjería Visa Infinite Privilege - tu asistente personal para reservas de viaje, restaurantes y eventos.", "ko": "Visa 인피니트 프리빌리지 컨시어지 - 여행 예약, 레스토랑 예약, 이벤트 티켓 등을 위한 개인 비서.", "ja": "Visa Infiniteプリビレッジコンシェルジュ - 旅行予約、レストラン予約、イベントチケットなど。"}',
    'concierge', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- PERK: Dining & Wine Events
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Exclusive Dining & Wine Events", "zh": "专属美食美酒活动", "fr": "Événements gastronomiques exclusifs", "es": "Eventos exclusivos de gastronomía y vinos", "ko": "독점 다이닝 & 와인 이벤트", "ja": "独占ダイニング＆ワインイベント"}',
    '{"en": "Access unique dining experiences with Visa Infinite Dining Series and wine country events with Visa Infinite Wine Country.", "zh": "参加Visa无限美食系列独特用餐体验和Visa无限葡萄酒乡活动。", "fr": "Accès aux expériences culinaires Visa Infinite Dining Series et Visa Infinite Wine Country.", "es": "Acceso a experiencias gastronómicas únicas con Visa Infinite Dining Series y eventos de vino.", "ko": "Visa 인피니트 다이닝 시리즈와 와인 컨트리 이벤트로 독특한 미식 경험.", "ja": "Visa Infiniteダイニングシリーズとワインカントリーイベントで特別な体験。"}',
    'dining', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- PERK: Golf Benefits
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Troon Rewards Golf Benefits", "zh": "Troon高尔夫礼遇", "fr": "Avantages golf Troon Rewards", "es": "Beneficios de golf Troon Rewards", "ko": "트룬 리워드 골프 혜택", "ja": "Troon Rewardsゴルフ特典"}',
    '{"en": "Discounts at 95+ golf resorts and courses worldwide, plus access to select private clubs across the U.S.", "zh": "全球95+高尔夫度假村和球场折扣，以及美国部分私人俱乐部入场权。", "fr": "Réductions dans 95+ clubs de golf dans le monde et accès à des clubs privés aux États-Unis.", "es": "Descuentos en 95+ resorts de golf en el mundo y acceso a clubes privados en EE.UU.", "ko": "전 세계 95개 이상의 골프 리조트 할인 및 미국 프라이빗 클럽 이용.", "ja": "世界95以上のゴルフリゾート割引、米国のプライベートクラブアクセス。"}',
    'golf', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- INSURANCE: Emergency Medical
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Emergency Medical Insurance", "zh": "紧急医疗保险", "fr": "Assurance médicale d''urgence", "es": "Seguro médico de emergencia", "ko": "응급 의료 보험", "ja": "緊急医療保険"}',
    '{"en": "Up to $5 million per person for out-of-province/country emergency medical expenses, covering trips up to 22 consecutive days.", "zh": "每人最高$500万境外紧急医疗费用，涵盖最长连续22天的旅行。", "fr": "Jusqu''à 5 M$ par personne pour frais médicaux d''urgence hors province/pays, voyages jusqu''à 22 jours.", "es": "Hasta $5 millones por persona para emergencias médicas fuera de provincia/país, viajes hasta 22 días.", "ko": "해외 응급 의료비 1인당 최대 $500만, 최대 22일 연속 여행 보장.", "ja": "国外緊急医療費1人あたり最大$500万、最長22日間の旅行をカバー。"}',
    'medical', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- INSURANCE: Trip Protection
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Trip Cancellation & Interruption", "zh": "旅行取消及中断保险", "fr": "Annulation et interruption de voyage", "es": "Cancelación e interrupción de viaje", "ko": "여행 취소 및 중단 보험", "ja": "旅行キャンセル・中断保険"}',
    '{"en": "Trip cancellation/interruption insurance plus flight delay coverage up to $1,000 per trip and baggage insurance.", "zh": "旅行取消/中断保险，航班延误保障每次最高$1,000，以及行李保险。", "fr": "Assurance annulation/interruption de voyage, retard de vol jusqu''à 1 000 $/voyage et assurance bagages.", "es": "Seguro de cancelación/interrupción de viaje, retraso de vuelo hasta $1,000 por viaje y seguro de equipaje.", "ko": "여행 취소/중단 보험, 항공편 지연 최대 $1,000/여행, 수하물 보험.", "ja": "旅行キャンセル・中断保険、フライト遅延補償最大$1,000/旅行、手荷物保険。"}',
    'shield', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- INSURANCE: Mobile Device
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "移动设备保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo móvil", "ko": "모바일 기기 보험", "ja": "モバイルデバイス保険"}',
    '{"en": "Up to $1,000 protection for your smartphone or tablet against loss, theft or accidental damage worldwide.", "zh": "全球范围内为您的智能手机或平板电脑提供最高$1,000的丢失、被盗或意外损坏保障。", "fr": "Jusqu''à 1 000 $ de protection pour votre téléphone ou tablette contre perte, vol ou dommage accidentel.", "es": "Hasta $1,000 de protección para tu smartphone o tablet contra pérdida, robo o daño accidental.", "ko": "스마트폰 또는 태블릿 분실, 도난, 우발적 손상에 대해 최대 $1,000 보장.", "ja": "スマートフォンまたはタブレットの紛失・盗難・偶発的損傷に最大$1,000の保護。"}',
    'phone', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- INSURANCE: Purchase Protection & Extended Warranty
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection & Extended Warranty", "zh": "购物保护及延长保修", "fr": "Protection achats et garantie prolongée", "es": "Protección de compras y garantía extendida", "ko": "구매 보호 및 연장 보증", "ja": "購入保護＆延長保証"}',
    '{"en": "90-day purchase protection against theft/damage, plus extended warranty that doubles manufacturer warranty up to 1 additional year.", "zh": "90天购物保护（防盗/损坏），延长保修可将原厂保修延长一倍，最多额外1年。", "fr": "Protection achats 90 jours contre vol/dommage, garantie prolongée doublant la garantie fabricant jusqu''à 1 an.", "es": "Protección de compras 90 días contra robo/daño, garantía extendida que duplica la garantía del fabricante hasta 1 año.", "ko": "90일 구매 보호(도난/손상), 제조사 보증을 최대 1년 연장하는 연장 보증.", "ja": "90日間の購入保護（盗難・損傷）、メーカー保証を最大1年延長。"}',
    'warranty', 13, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- INSURANCE: Car Rental & Hotel Burglary
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Car Rental & Hotel Insurance", "zh": "租车及酒店保险", "fr": "Assurance location auto et hôtel", "es": "Seguro de auto de alquiler y hotel", "ko": "렌터카 및 호텔 보험", "ja": "レンタカー＆ホテル保険"}',
    '{"en": "Car rental collision/loss damage insurance, common carrier insurance, and hotel burglary insurance up to $2,500.", "zh": "租车碰撞/损失保险、公共交通保险、酒店盗窃保险最高$2,500。", "fr": "Assurance collision/perte location auto, assurance transporteur public et assurance vol hôtel jusqu''à 2 500 $.", "es": "Seguro de colisión/pérdida de auto de alquiler, seguro de transporte y seguro de robo de hotel hasta $2,500.", "ko": "렌터카 충돌/손실 보험, 공공 운송 보험, 호텔 도난 보험 최대 $2,500.", "ja": "レンタカー衝突・損失保険、公共交通機関保険、ホテル盗難保険最大$2,500。"}',
    'car', 14, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- AVOID: Foreign Transaction Fee
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transaction Fee Applies", "zh": "有外币交易费", "fr": "Frais de transaction étrangère", "es": "Se aplica tarifa de transacción extranjera", "ko": "해외 거래 수수료 있음", "ja": "外国取引手数料あり"}',
    '{"en": "This card charges 2.5% foreign transaction fee. Consider BMO eclipse Visa Infinite (no FX fee) for international purchases.", "zh": "此卡收取2.5%外币交易费。海外消费建议使用BMO eclipse Visa Infinite（无外汇费）。", "fr": "Cette carte facture 2,5% de frais de transaction étrangère. Considérez la BMO eclipse Visa Infinite pour les achats internationaux.", "es": "Esta tarjeta cobra 2.5% de tarifa de transacción extranjera. Considera la BMO eclipse Visa Infinite para compras internacionales.", "ko": "이 카드는 2.5% 해외 거래 수수료가 부과됩니다. 해외 구매 시 BMO eclipse Visa Infinite를 고려하세요.", "ja": "このカードは2.5%の外国取引手数料がかかります。海外購入にはBMO eclipse Visa Infiniteを検討してください。"}',
    'alert', 15, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse Visa Infinite Privilege';

-- BMO VIPorter World Elite Mastercard (12条完整用卡攻略，6种语言)
-- 1. BEST_USE - Porter消费3倍积分
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "3x on Porter Purchases", "zh": "Porter消费3倍积分", "fr": "3x sur achats Porter", "es": "3x en compras Porter", "ko": "Porter 구매 3배 포인트", "ja": "Porter購入3倍ポイント"}',
    '{"en": "Earn 3 VIPorter points per $1 on all Porter Airlines purchases. Use for flights, upgrades, and in-flight purchases.", "zh": "Porter航空所有消费每$1赚取3个VIPorter积分。可用于机票、升舱和机上购物。", "fr": "Gagnez 3 points VIPorter par 1$ sur tous les achats Porter Airlines. Vols, surclassements et achats à bord.", "es": "Gana 3 puntos VIPorter por $1 en todas las compras de Porter Airlines. Vuelos, upgrades y compras a bordo.", "ko": "Porter Airlines 모든 구매 시 $1당 3 VIPorter 포인트 적립. 항공편, 업그레이드, 기내 구매에 사용.", "ja": "Porter Airlines全購入で$1につき3 VIPorterポイント獲得。フライト、アップグレード、機内購入に。"}',
    'plane', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 2. PERK - 年度同伴票
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Annual Companion Pass", "zh": "年度同伴票", "fr": "Passe accompagnateur annuel", "es": "Pase anual de acompañante", "ko": "연간 동반자 패스", "ja": "年間コンパニオンパス"}',
    '{"en": "Receive a round-trip companion pass each year for 100% off a Porter base fare. Applies to up to 8 companions on the same booking.", "zh": "每年获得一张往返同伴票，Porter基础票价100%折扣。同一预订最多可适用于8位同伴。", "fr": "Recevez un passe accompagnateur aller-retour chaque année pour 100% de rabais sur le tarif de base Porter. Jusqu''à 8 accompagnateurs.", "es": "Recibe un pase de acompañante de ida y vuelta cada año con 100% de descuento en tarifa base Porter. Hasta 8 acompañantes.", "ko": "매년 Porter 기본 요금 100% 할인 왕복 동반자 패스를 받으세요. 동일 예약 시 최대 8명까지 적용.", "ja": "毎年Porter基本運賃100%オフの往復コンパニオンパスを受け取れます。同一予約で最大8名まで適用。"}',
    'ticket', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 3. PERK - Avid Traveller身份
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Automatic Avid Traveller Status", "zh": "自动获得Avid Traveller身份", "fr": "Statut Avid Traveller automatique", "es": "Estado Avid Traveller automático", "ko": "자동 Avid Traveller 자격", "ja": "自動Avid Travellerステータス"}',
    '{"en": "Automatically become a VIPorter Avid Traveller. Earn $1 qualifying spend toward next level for every $25 spent on your card.", "zh": "自动成为VIPorter Avid Traveller。每消费$25可获得$1资格消费，用于升级会员等级。", "fr": "Devenez automatiquement un VIPorter Avid Traveller. Gagnez 1$ de dépense admissible par 25$ dépensés.", "es": "Conviértete automáticamente en VIPorter Avid Traveller. Gana $1 de gasto calificado por cada $25 gastados.", "ko": "자동으로 VIPorter Avid Traveller가 됩니다. $25 지출마다 $1 적격 지출을 적립하여 다음 레벨로.", "ja": "自動的にVIPorter Avid Travellerになります。$25支出ごとに$1の適格支出を獲得し次のレベルへ。"}',
    'star', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 4. PERK - 免费行李
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Checked & Carry-on Bag", "zh": "免费托运和手提行李", "fr": "Bagage enregistré et cabine gratuits", "es": "Equipaje facturado y de mano gratis", "ko": "무료 위탁 및 기내 수하물", "ja": "無料預け入れ・機内持ち込み手荷物"}',
    '{"en": "1 complimentary checked bag and 1 carry-on bag on all Porter fare types. Applies to up to 8 companions on the same booking.", "zh": "所有Porter票价类型均享1件免费托运行李和1件手提行李。同一预订最多可适用于8位同伴。", "fr": "1 bagage enregistré et 1 bagage cabine gratuits sur tous les types de tarifs Porter. Jusqu''à 8 accompagnateurs.", "es": "1 equipaje facturado y 1 de mano gratis en todos los tipos de tarifa Porter. Hasta 8 acompañantes.", "ko": "모든 Porter 요금 유형에서 위탁 수하물 1개와 기내 수하물 1개 무료. 최대 8명까지 적용.", "ja": "全Porterの運賃タイプで預け入れ手荷物1個と機内持ち込み1個が無料。最大8名まで適用。"}',
    'briefcase', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 5. PERK - 优先服务
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Priority Services", "zh": "优先服务", "fr": "Services prioritaires", "es": "Servicios prioritarios", "ko": "우선 서비스", "ja": "優先サービス"}',
    '{"en": "Priority check-in, security screening, early boarding, and priority re-accommodation for flight delays.", "zh": "优先办理登机、安检、提前登机，以及航班延误时优先改签。", "fr": "Enregistrement prioritaire, contrôle de sécurité, embarquement anticipé et réaccommodation prioritaire.", "es": "Check-in prioritario, seguridad, embarque anticipado y re-acomodación prioritaria por retrasos.", "ko": "우선 체크인, 보안 검색, 조기 탑승, 지연 시 우선 재배치.", "ja": "優先チェックイン、セキュリティ、早期搭乗、遅延時の優先再予約。"}',
    'clock', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 6. INSURANCE - 旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Comprehensive Travel Insurance", "zh": "全面旅行保险", "fr": "Assurance voyage complète", "es": "Seguro de viaje completo", "ko": "종합 여행 보험", "ja": "総合旅行保険"}',
    '{"en": "21-day out-of-province emergency medical, trip cancellation/interruption/delay, flight delay, baggage, and hotel burglary insurance included.", "zh": "包含21天省外紧急医疗、行程取消/中断/延误、航班延误、行李和酒店盗窃保险。", "fr": "Assurance médicale d''urgence 21 jours hors province, annulation/interruption/retard de voyage, retard de vol, bagages et vol d''hôtel.", "es": "21 días de seguro médico de emergencia fuera de provincia, cancelación/interrupción/retraso de viaje, retraso de vuelo, equipaje y robo en hotel.", "ko": "21일 타주 응급 의료, 여행 취소/중단/지연, 항공편 지연, 수하물, 호텔 도난 보험 포함.", "ja": "21日間の州外緊急医療、旅行キャンセル/中断/遅延、フライト遅延、手荷物、ホテル盗難保険を含む。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 7. INSURANCE - 租车保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Car Rental Insurance", "zh": "租车保险", "fr": "Assurance location de voiture", "es": "Seguro de alquiler de auto", "ko": "렌터카 보험", "ja": "レンタカー保険"}',
    '{"en": "Car rental collision/loss damage insurance included. Save up to 20% on National/Alamo and 5% on Enterprise rentals worldwide.", "zh": "包含租车碰撞/损失险。National/Alamo全球租车最高省20%，Enterprise省5%。", "fr": "Assurance collision/perte pour location de voiture incluse. Économisez jusqu''à 20% chez National/Alamo et 5% chez Enterprise.", "es": "Seguro de colisión/pérdida de alquiler incluido. Ahorra hasta 20% en National/Alamo y 5% en Enterprise.", "ko": "렌터카 충돌/손실 보험 포함. National/Alamo 최대 20%, Enterprise 5% 할인.", "ja": "レンタカー衝突/損失保険含む。National/Alamoで最大20%、Enterpriseで5%オフ。"}',
    'car', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 8. PERK - 机场贵宾室
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Mastercard Travel Pass Lounge Access", "zh": "Mastercard贵宾室通行", "fr": "Accès salon Mastercard Travel Pass", "es": "Acceso a salas Mastercard Travel Pass", "ko": "Mastercard Travel Pass 라운지 이용", "ja": "Mastercard Travel Passラウンジアクセス"}',
    '{"en": "Complimentary Mastercard Travel Pass membership with lounge access for US$32 per person per visit. Registration required.", "zh": "免费Mastercard Travel Pass会员资格，每人每次进入贵宾室仅需US$32。需注册。", "fr": "Adhésion gratuite Mastercard Travel Pass avec accès salon pour 32 $ US par personne par visite. Inscription requise.", "es": "Membresía gratuita Mastercard Travel Pass con acceso a salas por US$32 por persona por visita. Requiere registro.", "ko": "무료 Mastercard Travel Pass 멤버십으로 1인당 방문당 US$32로 라운지 이용. 등록 필요.", "ja": "Mastercard Travel Pass無料会員で1人1回US$32でラウンジ利用可能。登録が必要。"}',
    'coffee', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 9. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty & Purchase Protection", "zh": "延长保修和购物保护", "fr": "Garantie prolongée et protection des achats", "es": "Garantía extendida y protección de compras", "ko": "연장 보증 및 구매 보호", "ja": "延長保証と購入保護"}',
    '{"en": "Shop with extended warranty and purchase protection on items bought with your card.", "zh": "使用此卡购物享受延长保修和购物保护。", "fr": "Magasinez avec garantie prolongée et protection des achats sur les articles achetés avec votre carte.", "es": "Compra con garantía extendida y protección de compras en artículos comprados con tu tarjeta.", "ko": "카드로 구매한 상품에 대해 연장 보증 및 구매 보호 혜택.", "ja": "カードで購入した商品に延長保証と購入保護が適用。"}',
    'warranty', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 10. PERK - 积分永不过期
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Points Never Expire", "zh": "积分永不过期", "fr": "Points sans expiration", "es": "Puntos sin vencimiento", "ko": "포인트 만료 없음", "ja": "ポイント有効期限なし"}',
    '{"en": "Your VIPorter points never expire as long as your account remains open and in good standing.", "zh": "只要账户保持开放且状态良好，VIPorter积分永不过期。", "fr": "Vos points VIPorter n''expirent jamais tant que votre compte reste ouvert et en règle.", "es": "Tus puntos VIPorter nunca expiran mientras tu cuenta permanezca abierta y en buen estado.", "ko": "계정이 열려 있고 양호한 상태인 한 VIPorter 포인트는 만료되지 않습니다.", "ja": "アカウントが有効である限り、VIPorterポイントは期限切れになりません。"}',
    'infinity', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 11. BEST_USE - 日常消费2倍
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "2x on Everyday Categories", "zh": "日常消费2倍积分", "fr": "2x sur catégories quotidiennes", "es": "2x en categorías diarias", "ko": "일상 카테고리 2배", "ja": "日常カテゴリ2倍"}',
    '{"en": "Earn 2x points on hotels, dining, gas, transit, and groceries everywhere you go.", "zh": "酒店、餐饮、加油、交通和杂货消费均可获得2倍积分。", "fr": "Gagnez 2x points sur hôtels, restaurants, essence, transport et épicerie partout.", "es": "Gana 2x puntos en hoteles, restaurantes, gasolina, transporte y supermercados.", "ko": "호텔, 식당, 주유, 교통, 식료품에서 2배 포인트 적립.", "ja": "ホテル、飲食、ガソリン、交通、食料品で2倍ポイント獲得。"}',
    'grid', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- 12. AVOID - 外币交易费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Transaction Fee", "zh": "外币交易费", "fr": "Frais de transaction étrangère", "es": "Cargo por transacción extranjera", "ko": "해외 거래 수수료", "ja": "海外取引手数料"}',
    '{"en": "This card charges 2.5% foreign transaction fee. Use a no-FX-fee card for international purchases outside Porter.", "zh": "此卡收取2.5%外币交易费。非Porter国际消费请使用无外汇费信用卡。", "fr": "Cette carte facture 2,5% de frais de transaction étrangère. Utilisez une carte sans frais FX pour les achats internationaux.", "es": "Esta tarjeta cobra 2.5% de cargo por transacción extranjera. Usa una tarjeta sin cargo FX para compras internacionales.", "ko": "이 카드는 2.5% 해외 거래 수수료가 부과됩니다. Porter 외 해외 구매 시 외환 수수료 면제 카드를 사용하세요.", "ja": "このカードは2.5%の海外取引手数料がかかります。Porter以外の海外購入には外国為替手数料なしカードを使用してください。"}',
    'alert', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter World Elite Mastercard';

-- BMO VIPorter Mastercard (12条完整用卡攻略，6种语言)
-- 1. BEST_USE - Porter消费2倍积分
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "2x on Porter Purchases", "zh": "Porter消费2倍积分", "fr": "2x sur les achats Porter", "es": "2x en compras Porter", "ko": "Porter 구매 2배 포인트", "ja": "Porterで2倍ポイント"}',
    '{"en": "Earn 2 VIPorter points for every $1 spent on Porter Airlines purchases including flights, seat selection, and in-flight purchases.", "zh": "在Porter航空消费（包括机票、座位选择和机上消费）每花$1可获得2个VIPorter积分。", "fr": "Gagnez 2 points VIPorter pour chaque 1$ dépensé sur Porter Airlines, incluant vols, sélection de siège et achats en vol.", "es": "Gana 2 puntos VIPorter por cada $1 gastado en Porter Airlines, incluyendo vuelos, selección de asiento y compras a bordo.", "ko": "Porter 항공 구매(항공권, 좌석 선택, 기내 구매)에서 $1당 2 VIPorter 포인트 적립.", "ja": "Porter航空（航空券、座席指定、機内購入）で1ドルごとに2 VIPorterポイント獲得。"}',
    'plane', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 2. PERK - 35%机票折扣券
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "35% Off Flight Voucher", "zh": "35%机票折扣券", "fr": "Bon de 35% sur un vol", "es": "Cupón de 35% en vuelo", "ko": "35% 항공권 바우처", "ja": "35%フライトバウチャー"}',
    '{"en": "Receive a voucher for 35% off one flight booking per year. Great for reducing the cost of your Porter travel.", "zh": "每年获得一张35%机票折扣券，可用于一次机票预订。大幅降低您的Porter旅行成本。", "fr": "Recevez un bon de 35% sur une réservation de vol par an. Idéal pour réduire le coût de vos voyages Porter.", "es": "Recibe un cupón de 35% de descuento en una reserva de vuelo por año. Ideal para reducir el costo de tus viajes con Porter.", "ko": "연간 1회 항공권 예약 시 35% 할인 바우처를 받으세요. Porter 여행 비용을 크게 절감할 수 있습니다.", "ja": "年間1回の航空券予約に使える35%割引バウチャーを受け取れます。Porter旅行のコスト削減に最適。"}',
    'ticket', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 3. TRAVEL_BENEFIT - 优先重新安排
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'TRAVEL_BENEFIT',
    '{"en": "Priority Re-accommodation", "zh": "优先重新安排", "fr": "Réhébergement prioritaire", "es": "Reubicación prioritaria", "ko": "우선 재배치", "ja": "優先再予約"}',
    '{"en": "Get priority re-accommodation when your flight is delayed or cancelled. Skip the line and get rebooked faster.", "zh": "航班延误或取消时享受优先重新安排。跳过排队，更快获得新航班。", "fr": "Bénéficiez d''un réhébergement prioritaire en cas de retard ou d''annulation de vol. Passez devant et soyez rééservé plus rapidement.", "es": "Obtén reubicación prioritaria cuando tu vuelo se retrase o cancele. Evita la fila y obtén un nuevo vuelo más rápido.", "ko": "항공편이 지연되거나 취소될 때 우선 재배치를 받으세요. 줄을 건너뛰고 더 빨리 재예약하세요.", "ja": "フライト遅延・キャンセル時に優先的に再予約。列を飛ばして素早く再予約。"}',
    'clock', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 4. TRAVEL_BENEFIT - 专属值机和优先登机
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'TRAVEL_BENEFIT',
    '{"en": "Dedicated Check-in & Early Boarding", "zh": "专属值机和优先登机", "fr": "Enregistrement dédié et embarquement prioritaire", "es": "Check-in dedicado y embarque anticipado", "ko": "전용 체크인 및 우선 탑승", "ja": "専用チェックイン＆優先搭乗"}',
    '{"en": "Enjoy dedicated check-in counters and early boarding privileges on Porter flights for a smoother travel experience.", "zh": "在Porter航班享受专属值机柜台和优先登机特权，让您的旅行更加顺畅。", "fr": "Profitez de comptoirs d''enregistrement dédiés et de l''embarquement prioritaire sur les vols Porter.", "es": "Disfruta de mostradores de check-in dedicados y privilegios de embarque anticipado en vuelos Porter.", "ko": "Porter 항공편에서 전용 체크인 카운터와 우선 탑승 혜택을 누리세요.", "ja": "Porterフライトで専用チェックインカウンターと優先搭乗をお楽しみください。"}',
    'check', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 5. PERK - 积分永不过期
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Points Expiry", "zh": "积分永不过期", "fr": "Pas d''expiration des points", "es": "Puntos sin expiración", "ko": "포인트 만료 없음", "ja": "ポイント有効期限なし"}',
    '{"en": "Your VIPorter points never expire as long as your card account is open and in good standing. Earn at your own pace.", "zh": "只要您的卡账户正常使用，VIPorter积分永不过期。按自己的节奏累积积分。", "fr": "Vos points VIPorter n''expirent jamais tant que votre compte est ouvert et en règle. Accumulez à votre rythme.", "es": "Tus puntos VIPorter nunca expiran mientras tu cuenta esté abierta y al día. Acumula a tu propio ritmo.", "ko": "카드 계정이 정상 상태로 유지되는 한 VIPorter 포인트는 만료되지 않습니다.", "ja": "カード口座が正常であれば、VIPorterポイントは有効期限がありません。"}',
    'infinity', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 6. PERK - Avid Traveller身份
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Automatic Avid Traveller Status", "zh": "自动获得Avid Traveller身份", "fr": "Statut Avid Traveller automatique", "es": "Estatus Avid Traveller automático", "ko": "자동 Avid Traveller 지위", "ja": "Avid Travellerステータス自動付与"}',
    '{"en": "Automatically become an Avid Traveller in the VIPorter program. Earn $1 of Qualifying Spend for every $25 spent on your card.", "zh": "自动成为VIPorter计划的Avid Traveller会员。每在卡上消费$25可获得$1的资格消费额度。", "fr": "Devenez automatiquement un Avid Traveller dans le programme VIPorter. Gagnez 1$ de dépenses admissibles pour chaque 25$ dépensés.", "es": "Conviértete automáticamente en Avid Traveller en el programa VIPorter. Gana $1 de gasto calificado por cada $25 gastados.", "ko": "VIPorter 프로그램에서 자동으로 Avid Traveller가 됩니다. $25 지출마다 $1의 적격 지출을 적립하세요.", "ja": "VIPorterプログラムで自動的にAvid Travellerに。25ドル利用ごとに1ドルの適格支出を獲得。"}',
    'star', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 7. INSURANCE - 境外医疗保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "8-Day Emergency Medical Insurance", "zh": "8天境外紧急医疗保险", "fr": "Assurance médicale d''urgence 8 jours", "es": "Seguro médico de emergencia 8 días", "ko": "8일 긴급 의료 보험", "ja": "8日間緊急医療保険"}',
    '{"en": "Get 8-day out-of-province or out-of-country emergency medical insurance when you travel. Covers unexpected medical emergencies.", "zh": "旅行时享有8天省外或境外紧急医疗保险。涵盖意外医疗紧急情况。", "fr": "Bénéficiez de 8 jours d''assurance médicale d''urgence hors province ou hors pays lorsque vous voyagez.", "es": "Obtén 8 días de seguro médico de emergencia fuera de la provincia o del país cuando viajes.", "ko": "여행 시 8일간의 타 지역 또는 해외 긴급 의료 보험을 받으세요.", "ja": "旅行時に8日間の州外・国外緊急医療保険が適用されます。"}',
    'medical', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 8. INSURANCE - 全面旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Comprehensive Travel Coverage", "zh": "全面旅行保险", "fr": "Couverture voyage complète", "es": "Cobertura de viaje completa", "ko": "종합 여행 보장", "ja": "総合旅行保険"}',
    '{"en": "Includes car rental collision/loss damage insurance, common carrier insurance, flight delay insurance, baggage insurance, and hotel burglary insurance.", "zh": "包括租车碰撞/丢失损害保险、公共承运人保险、航班延误保险、行李保险和酒店盗窃保险。", "fr": "Comprend assurance collision/perte location de voiture, assurance transporteur, assurance retard de vol, assurance bagages et assurance vol à l''hôtel.", "es": "Incluye seguro de colisión/pérdida de alquiler de autos, seguro de transportista común, seguro de retraso de vuelo, seguro de equipaje y seguro de robo en hotel.", "ko": "렌터카 충돌/분실 손해 보험, 대중 운송 보험, 항공편 지연 보험, 수하물 보험, 호텔 도난 보험 포함.", "ja": "レンタカー衝突・紛失保険、公共交通保険、フライト遅延保険、手荷物保険、ホテル盗難保険を含む。"}',
    'shield', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 9. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty & Purchase Protection", "zh": "延长保修和购物保护", "fr": "Garantie prolongée et protection des achats", "es": "Garantía extendida y protección de compras", "ko": "연장 보증 및 구매 보호", "ja": "延長保証＆購入保護"}',
    '{"en": "Shop confidently with extended warranty and purchase protection on items bought with your card.", "zh": "使用此卡购物可享受延长保修和购物保护，让您放心购物。", "fr": "Magasinez en toute confiance avec la garantie prolongée et la protection des achats sur les articles achetés avec votre carte.", "es": "Compra con confianza con garantía extendida y protección de compras en artículos comprados con tu tarjeta.", "ko": "카드로 구매한 상품에 대해 연장 보증 및 구매 보호로 안심하고 쇼핑하세요.", "ja": "カードで購入した商品の延長保証と購入保護で安心してお買い物。"}',
    'warranty', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 10. PERK - 租车折扣
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Car Rental Discounts", "zh": "租车折扣", "fr": "Rabais sur la location de voiture", "es": "Descuentos en alquiler de autos", "ko": "렌터카 할인", "ja": "レンタカー割引"}',
    '{"en": "Save up to 20% on National Car Rental and Alamo Rent A Car, plus up to 5% on Enterprise Rent-A-Car worldwide using the Car Rental Booking tool.", "zh": "使用租车预订工具，在National和Alamo租车可节省高达20%，在Enterprise租车可节省高达5%。", "fr": "Économisez jusqu''à 20% chez National et Alamo, et jusqu''à 5% chez Enterprise dans le monde entier via l''outil de réservation.", "es": "Ahorra hasta 20% en National y Alamo, y hasta 5% en Enterprise en todo el mundo usando la herramienta de reserva.", "ko": "렌터카 예약 도구를 사용하여 National과 Alamo에서 최대 20%, Enterprise에서 최대 5% 절약.", "ja": "レンタカー予約ツールでNational・Alamoで最大20%、Enterpriseで最大5%割引。"}',
    'car', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 11. PERK - 太阳马戏团折扣
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Cirque du Soleil Discounts", "zh": "太阳马戏团折扣", "fr": "Rabais Cirque du Soleil", "es": "Descuentos Cirque du Soleil", "ko": "태양의 서커스 할인", "ja": "シルク・ドゥ・ソレイユ割引"}',
    '{"en": "Get 20% off admission to Cirque du Soleil shows touring Canada, and 15% off resident shows in Las Vegas.", "zh": "在加拿大巡演的太阳马戏团演出可享20%折扣，拉斯维加斯驻场演出可享15%折扣。", "fr": "Obtenez 20% de rabais sur les spectacles du Cirque du Soleil en tournée au Canada et 15% sur les spectacles à Las Vegas.", "es": "Obtén 20% de descuento en espectáculos de Cirque du Soleil en gira por Canadá, y 15% en shows residentes en Las Vegas.", "ko": "캐나다 순회 태양의 서커스 공연 20% 할인, 라스베이거스 상주 공연 15% 할인.", "ja": "カナダツアーのシルク・ドゥ・ソレイユで20%割引、ラスベガス常設ショーで15%割引。"}',
    'entertainment', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- 12. AVOID - 海外消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Avoid Non-Porter Foreign Purchases", "zh": "避免非Porter海外消费", "fr": "Éviter les achats étrangers non-Porter", "es": "Evitar compras extranjeras no-Porter", "ko": "Porter 외 해외 구매 피하기", "ja": "Porter以外の海外購入を避ける"}',
    '{"en": "This card charges 2.5% foreign transaction fee. For non-Porter international purchases, use a no-FX-fee card instead.", "zh": "此卡收取2.5%外币交易费。非Porter的国际消费请使用无外汇费信用卡。", "fr": "Cette carte facture 2,5% de frais de transaction étrangère. Pour les achats internationaux non-Porter, utilisez une carte sans frais FX.", "es": "Esta tarjeta cobra 2.5% de cargo por transacción extranjera. Para compras internacionales no-Porter, usa una tarjeta sin cargo FX.", "ko": "이 카드는 2.5% 해외 거래 수수료가 부과됩니다. Porter 외 해외 구매 시 외환 수수료 면제 카드를 사용하세요.", "ja": "このカードは2.5%の海外取引手数料がかかります。Porter以外の海外購入には外国為替手数料なしカードを使用してください。"}',
    'alert', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'VIPorter Mastercard';

-- BMO AIR MILES Mastercard (10条完整用卡攻略，6种语言)
-- 1. BEST_USE - 在AIR MILES合作商家消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Shop at AIR MILES Partners", "zh": "在AIR MILES合作商家消费", "fr": "Magasinez chez les partenaires AIR MILES", "es": "Compra en socios AIR MILES", "ko": "AIR MILES 파트너에서 쇼핑", "ja": "AIR MILESパートナーで買い物"}',
    '{"en": "Earn 3 AIR MILES for every $25 spent at participating AIR MILES Partners like Shell, Sobeys, Safeway, and Metro for maximum rewards.", "zh": "在Shell、Sobeys、Safeway、Metro等AIR MILES合作商家每消费$25可获得3 AIR MILES，最大化您的积分收益。", "fr": "Gagnez 3 AIR MILES pour chaque 25$ dépensé chez les partenaires AIR MILES participants comme Shell, Sobeys, Safeway et Metro.", "es": "Gana 3 AIR MILES por cada $25 gastados en socios AIR MILES participantes como Shell, Sobeys, Safeway y Metro.", "ko": "Shell, Sobeys, Safeway, Metro 등 AIR MILES 파트너에서 $25 소비 시 3 AIR MILES를 적립하세요.", "ja": "Shell、Sobeys、Safeway、MetroなどのAIR MILESパートナーで25ドルごとに3 AIR MILESを獲得。"}',
    'store', 1, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 2. BEST_USE - 超市、仓储店和酒类商店
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Grocery, Wholesale & Liquor Stores", "zh": "超市、仓储店和酒类商店", "fr": "Épiceries, clubs-entrepôts et SAQ", "es": "Supermercados, mayoristas y licoreras", "ko": "식료품점, 창고형 매장 및 주류 매장", "ja": "食料品店・卸売店・酒類店"}',
    '{"en": "Earn 2 AIR MILES for every $25 spent at any grocery store, wholesale club (including Costco), and liquor retailer.", "zh": "在任何超市、仓储式商店（包括Costco）和酒类零售商每消费$25可获得2 AIR MILES。", "fr": "Gagnez 2 AIR MILES pour chaque 25$ dépensé dans les épiceries, clubs-entrepôts (incluant Costco) et détaillants de spiritueux.", "es": "Gana 2 AIR MILES por cada $25 en supermercados, clubes mayoristas (incluyendo Costco) y tiendas de licores.", "ko": "식료품점, 창고형 매장(Costco 포함), 주류 매장에서 $25당 2 AIR MILES 적립.", "ja": "食料品店、卸売クラブ（Costco含む）、酒類店で25ドルごとに2 AIR MILESを獲得。"}',
    'grocery', 2, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 3. BEST_USE - Costco购物
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Use at Costco", "zh": "在Costco使用", "fr": "Utiliser chez Costco", "es": "Usar en Costco", "ko": "Costco에서 사용", "ja": "Costcoで使用"}',
    '{"en": "As a Mastercard, this card is accepted at Costco where Visa is not. Earn 2 AIR MILES per $25 on all Costco purchases.", "zh": "作为Mastercard，此卡可在不接受Visa的Costco使用。在Costco每消费$25可获得2 AIR MILES。", "fr": "En tant que Mastercard, cette carte est acceptée chez Costco où Visa ne l''est pas. Gagnez 2 AIR MILES par 25$ chez Costco.", "es": "Como Mastercard, esta tarjeta es aceptada en Costco donde Visa no lo es. Gana 2 AIR MILES por cada $25 en Costco.", "ko": "Mastercard로서 Visa가 안 되는 Costco에서 사용 가능. $25당 2 AIR MILES 적립.", "ja": "MastercardなのでVisaが使えないCostcoでも利用可能。25ドルごとに2 AIR MILESを獲得。"}',
    'shopping', 3, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 4. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection des achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "Items purchased with your card are automatically insured against theft or damage for 90 days from date of purchase, up to $60,000 lifetime limit.", "zh": "使用此卡购买的物品自购买之日起90天内自动享有被盗或损坏保险，终身限额$60,000。", "fr": "Les articles achetés avec votre carte sont automatiquement assurés contre le vol ou les dommages pendant 90 jours, jusqu''à 60 000$ à vie.", "es": "Los artículos comprados con tu tarjeta están automáticamente asegurados contra robo o daño por 90 días, hasta $60,000 de por vida.", "ko": "카드로 구매한 물품은 구매일로부터 90일간 도난 또는 손상에 대해 자동 보험 적용, 평생 한도 $60,000.", "ja": "カードで購入した商品は購入日から90日間、盗難・破損に対して自動保険適用。生涯限度額$60,000。"}',
    'shield', 4, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 5. INSURANCE - 延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty", "zh": "延长保修", "fr": "Garantie prolongée", "es": "Garantía extendida", "ko": "연장 보증", "ja": "延長保証"}',
    '{"en": "Doubles the original manufacturer''s warranty period on eligible purchases, giving you extra peace of mind on electronics and appliances.", "zh": "符合条件的购买可延长原厂保修期一倍，为您的电子产品和家电提供额外保障。", "fr": "Double la période de garantie du fabricant sur les achats admissibles, offrant une tranquillité d''esprit supplémentaire.", "es": "Duplica el período de garantía del fabricante en compras elegibles, dándote tranquilidad extra en electrónicos y electrodomésticos.", "ko": "적격 구매에 대해 제조사 보증 기간을 두 배로 연장하여 전자제품 및 가전제품에 추가 안심을 제공.", "ja": "対象購入品のメーカー保証期間を2倍に延長。電子機器や家電に追加の安心を。"}',
    'warranty', 5, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 6. PERK - 无年费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "无年费", "fr": "Aucuns frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "Enjoy all the benefits of earning AIR MILES with no annual fee, making it a great everyday card for budget-conscious consumers.", "zh": "无需支付年费即可享受AIR MILES积分权益，是注重预算消费者的理想日常卡。", "fr": "Profitez de tous les avantages AIR MILES sans frais annuels, idéal pour les consommateurs soucieux de leur budget.", "es": "Disfruta de todos los beneficios de ganar AIR MILES sin cuota anual, ideal para consumidores conscientes del presupuesto.", "ko": "연회비 없이 AIR MILES 적립 혜택을 모두 누리세요. 예산을 중시하는 소비자에게 이상적인 일상 카드.", "ja": "年会費なしでAIR MILESの特典を全て享受。予算重視の消費者に最適な日常カード。"}',
    'gift', 6, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 7. PERK - 免费附属卡
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Additional Cardholder", "zh": "免费附属卡", "fr": "Titulaire supplémentaire gratuit", "es": "Titular adicional gratis", "ko": "무료 추가 카드 소지자", "ja": "追加カード会員無料"}',
    '{"en": "Add an additional cardholder at no extra cost. Combine household spending to earn AIR MILES faster on everyday purchases.", "zh": "免费添加附属卡持卡人。合并家庭消费，更快赚取AIR MILES积分。", "fr": "Ajoutez un titulaire supplémentaire sans frais. Combinez les dépenses familiales pour accumuler des AIR MILES plus rapidement.", "es": "Agrega un titular adicional sin costo extra. Combina gastos del hogar para ganar AIR MILES más rápido.", "ko": "추가 비용 없이 추가 카드 소지자를 등록하세요. 가족 지출을 합산하여 더 빠르게 AIR MILES를 적립.", "ja": "追加費用なしで追加カード会員を登録。家族の支出を合算してAIR MILESを早く貯める。"}',
    'users', 7, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 8. REDEMPTION - AIR MILES兑换建议
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
    '{"en": "Best Redemption Value", "zh": "最佳兑换价值", "fr": "Meilleure valeur d''échange", "es": "Mejor valor de canje", "ko": "최고의 적립금 가치", "ja": "最高の交換価値"}',
    '{"en": "Redeem AIR MILES Dream Miles for flights and travel packages to maximize value. Cash Miles offer flexibility but lower value per mile.", "zh": "兑换AIR MILES Dream Miles用于航班和旅行套餐可获得最大价值。Cash Miles更灵活但每里程价值较低。", "fr": "Échangez les Dream Miles pour des vols et forfaits voyage pour maximiser la valeur. Les Cash Miles offrent plus de flexibilité mais moins de valeur.", "es": "Canjea Dream Miles por vuelos y paquetes de viaje para maximizar el valor. Los Cash Miles ofrecen flexibilidad pero menor valor por milla.", "ko": "Dream Miles를 항공권 및 여행 패키지로 교환하면 가치가 극대화됩니다. Cash Miles는 유연하지만 마일당 가치가 낮습니다.", "ja": "Dream Milesを航空券や旅行パッケージに交換して価値を最大化。Cash Milesは柔軟だがマイル当たりの価値は低め。"}',
    'travel', 8, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 9. STACKING - 双重积分叠加
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'STACKING',
    '{"en": "Double Dip at Partners", "zh": "合作商家双重积分", "fr": "Double accumulation chez les partenaires", "es": "Acumulación doble en socios", "ko": "파트너에서 이중 적립", "ja": "パートナーでダブル獲得"}',
    '{"en": "Stack your card miles with AIR MILES collector card at participating partners like Shell, Sobeys, and Rexall to earn bonus miles on top of your credit card rewards.", "zh": "在Shell、Sobeys、Rexall等合作商家使用此卡的同时出示AIR MILES会员卡，可在信用卡积分基础上额外获得奖励里程。", "fr": "Combinez les miles de votre carte avec votre carte de collecteur AIR MILES chez les partenaires comme Shell, Sobeys et Rexall pour des miles bonus.", "es": "Combina las millas de tu tarjeta con tu tarjeta de coleccionista AIR MILES en socios como Shell, Sobeys y Rexall para ganar millas extra.", "ko": "Shell, Sobeys, Rexall 등 파트너에서 AIR MILES 회원 카드와 함께 사용하여 신용카드 적립 외 추가 마일을 적립하세요.", "ja": "Shell、Sobeys、RexallなどのパートナーでAIR MILESコレクターカードと併用し、クレカポイントに加えてボーナスマイルを獲得。"}',
    'layers', 9, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- 10. AVOID - 避免海外消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Avoid Foreign Transactions", "zh": "避免海外消费", "fr": "Éviter les transactions étrangères", "es": "Evitar transacciones extranjeras", "ko": "해외 거래 피하기", "ja": "海外取引を避ける"}',
    '{"en": "This card charges foreign transaction fees (typically 2.5%). Use a no-FX-fee card like BMO eclipse or Scotiabank Passport for international purchases.", "zh": "此卡收取外币交易费（通常2.5%）。海外消费建议使用BMO eclipse或Scotiabank Passport等免外币交易费的卡。", "fr": "Cette carte facture des frais de transaction étrangère (généralement 2,5%). Utilisez une carte sans frais comme BMO eclipse pour les achats internationaux.", "es": "Esta tarjeta cobra tarifas por transacciones extranjeras (típicamente 2.5%). Usa una tarjeta sin comisiones para compras internacionales.", "ko": "이 카드는 해외 거래 수수료(일반적으로 2.5%)가 부과됩니다. 해외 구매 시 수수료 없는 카드를 사용하세요.", "ja": "このカードは外国取引手数料（通常2.5%）がかかります。海外購入にはBMO eclipseなど手数料無料カードを使用してください。"}',
    'alert', 10, 1 FROM credit_cards WHERE bank = 'BMO' AND name = 'AIR MILES Mastercard';

-- BMO Preferred Rate Mastercard (10条完整用卡攻略，6种语言)
-- 1. BEST_USE - 0% 余额转账
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "0% Balance Transfer for 9 Months", "zh": "9个月0%余额转账", "fr": "0% transfert de solde 9 mois", "es": "0% en transferencias por 9 meses", "ko": "9개월 0% 잔액 이체", "ja": "9ヶ月0%残高移行"}',
    '{"en": "Transfer balances from other cards at 0% interest for 9 months with only 0.99% transfer fee. Pay down debt faster without interest charges.", "zh": "从其他卡转移余额，9个月内0%利息，仅需0.99%转账费。无利息更快还清债务。", "fr": "Transférez vos soldes à 0% pendant 9 mois avec seulement 0,99% de frais. Remboursez plus vite sans intérêts.", "es": "Transfiere saldos al 0% por 9 meses con solo 0.99% de comisión. Paga deudas más rápido sin intereses.", "ko": "다른 카드 잔액을 0.99% 수수료로 9개월간 0% 이자로 이체. 이자 없이 빠르게 부채 상환.", "ja": "他カードの残高を0.99%の手数料で9ヶ月間0%金利で移行。利息なしで早く返済。"}',
    'percent', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 2. BEST_USE - 低利率
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Low Interest Rate", "zh": "低利率", "fr": "Taux d''intérêt bas", "es": "Tasa de interés baja", "ko": "저금리", "ja": "低金利"}',
    '{"en": "13.99% APR is significantly lower than standard cards at 21.99%. Ideal if you occasionally carry a balance.", "zh": "13.99%年利率远低于标准卡的21.99%。适合偶尔持有余额的用户。", "fr": "13,99% APR est bien inférieur aux cartes standard à 21,99%. Idéal si vous gardez parfois un solde.", "es": "13.99% APR es mucho menor que las tarjetas estándar al 21.99%. Ideal si ocasionalmente mantienes un saldo.", "ko": "13.99% APR은 표준 카드 21.99%보다 훨씬 낮습니다. 가끔 잔액을 유지하는 경우 이상적입니다.", "ja": "13.99%APRは標準カードの21.99%より大幅に低い。時々残高を持つ方に最適。"}',
    'dollar', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 3. PERK - 首年免年费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "First Year Annual Fee Waived", "zh": "首年免年费", "fr": "Frais annuels 1ère année annulés", "es": "Primer año sin cuota anual", "ko": "첫해 연회비 면제", "ja": "初年度年会費無料"}',
    '{"en": "The $29 annual fee is waived for the first year, giving you time to pay down balances interest-free.", "zh": "$29年费首年免除，让您有时间免息还清余额。", "fr": "Les frais annuels de 29 $ sont annulés la première année.", "es": "La cuota anual de $29 se exonera el primer año.", "ko": "$29 연회비가 첫해 면제됩니다.", "ja": "$29の年会費が初年度免除されます。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 4. INSURANCE - 延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty", "zh": "延长保修", "fr": "Garantie prolongée", "es": "Garantía extendida", "ko": "연장 보증", "ja": "延長保証"}',
    '{"en": "Doubles the original manufacturer warranty up to 1 additional year on items purchased with your card.", "zh": "使用此卡购买的商品可延长原厂保修期一倍，最多额外1年。", "fr": "Double la garantie du fabricant jusqu''à 1 an supplémentaire sur les achats avec votre carte.", "es": "Duplica la garantía del fabricante hasta 1 año adicional en compras con tu tarjeta.", "ko": "카드로 구매한 상품의 제조사 보증을 최대 1년 추가 연장합니다.", "ja": "カードで購入した商品のメーカー保証を最大1年延長。"}',
    'warranty', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 5. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Security Insurance", "zh": "购物保护保险", "fr": "Assurance protection des achats", "es": "Seguro de protección de compras", "ko": "구매 보호 보험", "ja": "購入保護保険"}',
    '{"en": "Items purchased with your card are automatically insured against theft or damage for 90 days from purchase date.", "zh": "使用此卡购买的商品自购买之日起90天内自动享有被盗或损坏保险。", "fr": "Les articles achetés sont automatiquement assurés contre le vol ou les dommages pendant 90 jours.", "es": "Los artículos comprados están asegurados contra robo o daño por 90 días.", "ko": "카드로 구매한 상품은 구매일로부터 90일간 도난 또는 손상에 대해 자동 보험 적용.", "ja": "カードで購入した商品は購入日から90日間、盗難・破損に対して自動保険適用。"}',
    'shield', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 6. PERK - 免费副卡
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Additional Cardholder", "zh": "免费附属卡", "fr": "Titulaire supplémentaire gratuit", "es": "Titular adicional gratis", "ko": "무료 추가 카드", "ja": "追加カード無料"}',
    '{"en": "Add another cardholder at no extra cost to manage household expenses together.", "zh": "免费添加附属卡持卡人，共同管理家庭开支。", "fr": "Ajoutez un titulaire supplémentaire gratuitement pour gérer les dépenses familiales.", "es": "Agrega un titular adicional sin costo para manejar gastos del hogar juntos.", "ko": "추가 비용 없이 추가 카드 소지자를 등록하여 가계비를 함께 관리하세요.", "ja": "追加費用なしで追加カード会員を登録し、家計を一緒に管理。"}',
    'users', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 7. PERK - 零责任保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Zero Liability Protection", "zh": "零责任保护", "fr": "Protection zéro responsabilité", "es": "Protección de responsabilidad cero", "ko": "무책임 보호", "ja": "ゼロライアビリティ保護"}',
    '{"en": "You won''t be held responsible for unauthorized purchases made with your card.", "zh": "您无需为未经授权的卡片消费负责。", "fr": "Vous n''êtes pas responsable des achats non autorisés effectués avec votre carte.", "es": "No serás responsable por compras no autorizadas realizadas con tu tarjeta.", "ko": "카드로 이루어진 무단 구매에 대해 책임을 지지 않습니다.", "ja": "カードでの不正使用に対して責任を負いません。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 8. PERK - 24/7 紧急支持
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "24/7 Emergency Support", "zh": "24/7紧急支持", "fr": "Support d''urgence 24/7", "es": "Soporte de emergencia 24/7", "ko": "24/7 긴급 지원", "ja": "24時間緊急サポート"}',
    '{"en": "Mastercard assistance center available 24/7 for emergencies anywhere in the world.", "zh": "Mastercard援助中心全天候24/7提供全球紧急支持。", "fr": "Centre d''assistance Mastercard disponible 24/7 pour les urgences dans le monde entier.", "es": "Centro de asistencia Mastercard disponible 24/7 para emergencias en cualquier parte del mundo.", "ko": "전 세계 어디서나 긴급 상황 시 24/7 마스터카드 지원 센터 이용 가능.", "ja": "世界中どこでも緊急時に24時間対応のMastercardアシスタンスセンター。"}',
    'phone', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 9. AVOID - 无奖励
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Rewards Program", "zh": "无奖励计划", "fr": "Aucun programme de récompenses", "es": "Sin programa de recompensas", "ko": "리워드 프로그램 없음", "ja": "リワードプログラムなし"}',
    '{"en": "This card offers no cashback or points. If you pay your balance in full each month, consider a rewards card instead.", "zh": "此卡无返现或积分奖励。如果您每月全额还款，建议使用奖励信用卡。", "fr": "Cette carte n''offre ni remise ni points. Si vous payez en entier chaque mois, envisagez une carte récompenses.", "es": "Esta tarjeta no ofrece reembolsos ni puntos. Si pagas el saldo completo cada mes, considera una tarjeta de recompensas.", "ko": "이 카드는 캐시백이나 포인트가 없습니다. 매월 전액 결제하면 리워드 카드를 고려하세요.", "ja": "このカードはキャッシュバックやポイントがありません。毎月全額支払う場合はリワードカードを検討してください。"}',
    'alert', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- 10. AVOID - 无旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Travel Insurance Included", "zh": "不含旅行保险", "fr": "Assurance voyage non incluse", "es": "Sin seguro de viaje incluido", "ko": "여행 보험 미포함", "ja": "旅行保険なし"}',
    '{"en": "This card does not include travel insurance. BMO Travel Insurance is available as a separate purchase if needed.", "zh": "此卡不含旅行保险。如需要可单独购买BMO旅行保险。", "fr": "Cette carte ne comprend pas d''assurance voyage. L''assurance voyage BMO est disponible séparément.", "es": "Esta tarjeta no incluye seguro de viaje. El seguro de viaje BMO está disponible por separado.", "ko": "이 카드에는 여행 보험이 포함되어 있지 않습니다. 필요시 BMO 여행 보험을 별도로 구매할 수 있습니다.", "ja": "このカードには旅行保険が含まれていません。必要に応じてBMO旅行保険を別途購入できます。"}',
    'alert', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Preferred Rate Mastercard';

-- BMO U.S. Dollar Mastercard (10条完整用卡攻略，6种语言)
-- 1. BEST_USE - 美元消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "U.S. Dollar Purchases", "zh": "美元消费", "fr": "Achats en dollars américains", "es": "Compras en dólares estadounidenses", "ko": "미국 달러 구매", "ja": "米ドル購入"}',
    '{"en": "Pay in USD and settle in USD to avoid exchange rate fluctuations. Best for regular cross-border shoppers or snowbirds.", "zh": "用美元消费、美元还款，避免汇率波动。适合经常跨境购物或在美国过冬的人。", "fr": "Payez et réglez en USD pour éviter les fluctuations de taux. Idéal pour les acheteurs transfrontaliers ou les snowbirds.", "es": "Paga y liquida en USD para evitar fluctuaciones cambiarias. Ideal para compradores transfronterizos o snowbirds.", "ko": "USD로 결제하고 USD로 정산하여 환율 변동을 피하세요. 국경 간 쇼핑객이나 스노우버드에게 적합합니다.", "ja": "USDで支払い、USDで決済して為替変動を回避。越境ショッパーやスノーバードに最適。"}',
    'dollar', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 2. BEST_USE - 美国网购
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "U.S. Online Shopping", "zh": "美国网购", "fr": "Achats en ligne aux États-Unis", "es": "Compras en línea en EE.UU.", "ko": "미국 온라인 쇼핑", "ja": "米国オンラインショッピング"}',
    '{"en": "Shop on Amazon.com, eBay.com and other U.S. retailers. Pay the exact USD price without currency conversion fees.", "zh": "在Amazon.com、eBay.com等美国零售商购物。支付准确的美元价格，无需货币转换费。", "fr": "Achetez sur Amazon.com, eBay.com et autres détaillants américains. Payez le prix exact en USD sans frais de conversion.", "es": "Compra en Amazon.com, eBay.com y otros minoristas de EE.UU. Paga el precio exacto en USD sin cargos de conversión.", "ko": "Amazon.com, eBay.com 및 기타 미국 소매업체에서 쇼핑하세요. 환전 수수료 없이 정확한 USD 가격을 지불합니다.", "ja": "Amazon.com、eBay.comなど米国小売店で買い物。通貨換算手数料なしで正確なUSD価格を支払い。"}',
    'cart', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 3. PERK - 年费返还
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Annual Fee Rebate", "zh": "年费返还", "fr": "Remise des frais annuels", "es": "Reembolso de cuota anual", "ko": "연회비 환급", "ja": "年会費キャッシュバック"}',
    '{"en": "Spend US$3,000+ annually to get next year''s $49 annual fee rebated. That''s only US$250/month.", "zh": "年消费满US$3,000可获得次年$49年费返还。每月只需消费约US$250。", "fr": "Dépensez 3 000 $ US+ par an pour obtenir le remboursement des frais de 49 $ l''année suivante. Seulement 250 $ US/mois.", "es": "Gasta US$3,000+ al año para obtener el reembolso de la cuota de $49 del próximo año. Solo US$250/mes.", "ko": "연간 US$3,000 이상 사용하면 다음 해 $49 연회비가 환급됩니다. 월 US$250만 사용하면 됩니다.", "ja": "年間US$3,000以上利用で翌年の$49年会費がキャッシュバック。月US$250だけです。"}',
    'gift', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 4. BEST_USE - Snowbird适用
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Perfect for Snowbirds", "zh": "雪鸟族必备", "fr": "Parfait pour les snowbirds", "es": "Perfecto para snowbirds", "ko": "스노우버드에 완벽", "ja": "スノーバードに最適"}',
    '{"en": "Ideal for Canadians wintering in the U.S. Pay for accommodation, dining, and daily expenses in USD without conversion fees.", "zh": "非常适合在美国过冬的加拿大人。用美元支付住宿、餐饮和日常开支，无需货币转换费。", "fr": "Idéal pour les Canadiens qui hivernent aux États-Unis. Payez hébergement, repas et dépenses quotidiennes en USD sans frais de conversion.", "es": "Ideal para canadienses que pasan el invierno en EE.UU. Paga alojamiento, comidas y gastos diarios en USD sin cargos de conversión.", "ko": "미국에서 겨울을 보내는 캐나다인에게 이상적입니다. 환전 수수료 없이 숙박, 식사 및 일상 비용을 USD로 결제하세요.", "ja": "米国で冬を過ごすカナダ人に最適。宿泊、食事、日常経費をUSDで換算手数料なしで支払い。"}',
    'sun', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 5. INSURANCE - 延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty", "zh": "延长保修", "fr": "Garantie prolongée", "es": "Garantía extendida", "ko": "연장 보증", "ja": "延長保証"}',
    '{"en": "Doubles the original manufacturer warranty up to 1 additional year on items purchased with your card.", "zh": "使用此卡购买的商品可延长原厂保修期一倍，最多额外1年。", "fr": "Double la garantie du fabricant jusqu''à 1 an supplémentaire sur les achats avec votre carte.", "es": "Duplica la garantía del fabricante hasta 1 año adicional en compras con tu tarjeta.", "ko": "카드로 구매한 상품의 제조사 보증을 최대 1년 추가 연장합니다.", "ja": "カードで購入した商品のメーカー保証を最大1年延長。"}',
    'warranty', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 6. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Security Insurance", "zh": "购物保护保险", "fr": "Assurance protection des achats", "es": "Seguro de protección de compras", "ko": "구매 보호 보험", "ja": "購入保護保険"}',
    '{"en": "Items purchased with your card are automatically insured against theft or damage for 90 days from purchase date.", "zh": "使用此卡购买的商品自购买之日起90天内自动享有被盗或损坏保险。", "fr": "Les articles achetés sont automatiquement assurés contre le vol ou les dommages pendant 90 jours.", "es": "Los artículos comprados están asegurados contra robo o daño por 90 días.", "ko": "카드로 구매한 상품은 구매일로부터 90일간 도난 또는 손상에 대해 자동 보험 적용.", "ja": "カードで購入した商品は購入日から90日間、盗難・破損に対して自動保険適用。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 7. PERK - 零责任保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Zero Liability Protection", "zh": "零责任保护", "fr": "Protection zéro responsabilité", "es": "Protección de responsabilidad cero", "ko": "무책임 보호", "ja": "ゼロライアビリティ保護"}',
    '{"en": "You won''t be held responsible for unauthorized purchases made with your card.", "zh": "您无需为未经授权的卡片消费负责。", "fr": "Vous n''êtes pas responsable des achats non autorisés effectués avec votre carte.", "es": "No serás responsable por compras no autorizadas realizadas con tu tarjeta.", "ko": "카드로 이루어진 무단 구매에 대해 책임을 지지 않습니다.", "ja": "カードでの不正使用に対して責任を負いません。"}',
    'shield', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 8. AVOID - 非美元消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Non-USD Purchases", "zh": "非美元消费", "fr": "Achats non-USD", "es": "Compras no en USD", "ko": "비USD 구매", "ja": "非USD購入"}',
    '{"en": "2.5% foreign transaction fee applies to non-USD purchases. Use a no-FX-fee card for CAD or other currencies.", "zh": "非美元消费收取2.5%外币交易费。加元或其他货币消费请使用无外汇费信用卡。", "fr": "2,5% de frais sur les achats non-USD. Utilisez une carte sans frais FX pour CAD ou autres devises.", "es": "Se aplica 2.5% de cargo por transacción extranjera en compras no-USD. Usa una tarjeta sin cargo FX para CAD u otras monedas.", "ko": "비USD 구매 시 2.5% 해외 거래 수수료가 부과됩니다. CAD 또는 다른 통화에는 외환 수수료 면제 카드를 사용하세요.", "ja": "非USD購入には2.5%の外国取引手数料がかかります。CADや他通貨にはFX手数料なしカードを使用してください。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 9. AVOID - 无奖励
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Rewards Program", "zh": "无奖励计划", "fr": "Aucun programme de récompenses", "es": "Sin programa de recompensas", "ko": "리워드 프로그램 없음", "ja": "リワードプログラムなし"}',
    '{"en": "This card offers no cashback or points. It''s designed for USD convenience, not rewards earning.", "zh": "此卡无返现或积分奖励。它专为美元消费便利设计，而非赚取奖励。", "fr": "Cette carte n''offre ni remise ni points. Elle est conçue pour la commodité USD, pas pour les récompenses.", "es": "Esta tarjeta no ofrece reembolsos ni puntos. Está diseñada para conveniencia USD, no para ganar recompensas.", "ko": "이 카드는 캐시백이나 포인트가 없습니다. USD 편의성을 위해 설계되었으며 리워드 적립용이 아닙니다.", "ja": "このカードはキャッシュバックやポイントがありません。USD利便性のために設計されており、リワード獲得用ではありません。"}',
    'alert', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 10. AVOID - 无旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Travel Insurance Included", "zh": "不含旅行保险", "fr": "Assurance voyage non incluse", "es": "Sin seguro de viaje incluido", "ko": "여행 보험 미포함", "ja": "旅行保険なし"}',
    '{"en": "This card does not include travel insurance. BMO Travel Insurance is available as a separate purchase for single or multi-trip coverage.", "zh": "此卡不含旅行保险。可单独购买BMO旅行保险，提供单次或多次旅行保障。", "fr": "Cette carte ne comprend pas d''assurance voyage. L''assurance voyage BMO est disponible séparément pour une couverture simple ou multi-voyages.", "es": "Esta tarjeta no incluye seguro de viaje. El seguro de viaje BMO está disponible por separado para cobertura de viaje único o múltiple.", "ko": "이 카드에는 여행 보험이 포함되어 있지 않습니다. BMO 여행 보험을 별도로 구매하여 단일 또는 다중 여행 보장을 받을 수 있습니다.", "ja": "このカードには旅行保険が含まれていません。BMO旅行保険を別途購入して単一または複数旅行の補償を受けられます。"}',
    'alert', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 11. PERK - 免费附属卡
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Additional Cardholder", "zh": "免费附属卡", "fr": "Titulaire supplémentaire gratuit", "es": "Titular adicional gratis", "ko": "무료 추가 카드", "ja": "追加カード無料"}',
    '{"en": "Add another cardholder at no extra cost to share USD spending convenience.", "zh": "免费添加附属卡持卡人，共享美元消费便利。", "fr": "Ajoutez un titulaire supplémentaire gratuitement pour partager la commodité des dépenses en USD.", "es": "Agrega un titular adicional sin costo para compartir la conveniencia de gastos en USD.", "ko": "추가 비용 없이 추가 카드 소지자를 등록하여 USD 지출 편의성을 공유하세요.", "ja": "追加費用なしで追加カード会員を登録し、USD支出の便利さを共有。"}',
    'users', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- 12. PERK - 太阳马戏团折扣
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Cirque du Soleil Discount", "zh": "太阳马戏团折扣", "fr": "Rabais Cirque du Soleil", "es": "Descuento Cirque du Soleil", "ko": "태양의 서커스 할인", "ja": "シルク・ドゥ・ソレイユ割引"}',
    '{"en": "Get 20% off Cirque du Soleil shows touring Canada and 15% off resident shows in Las Vegas.", "zh": "加拿大巡演享8折，拉斯维加斯驻场演出享85折优惠。", "fr": "Obtenez 20% de rabais sur les spectacles en tournée au Canada et 15% sur les spectacles résidents à Las Vegas.", "es": "Obtén 20% de descuento en espectáculos en gira por Canadá y 15% en espectáculos residentes en Las Vegas.", "ko": "캐나다 투어 공연 20% 할인, 라스베가스 상주 공연 15% 할인.", "ja": "カナダツアー公演20%オフ、ラスベガス常設公演15%オフ。"}',
    'ticket', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'U.S. Dollar Mastercard';

-- ============================================
-- 7. Student BMO CashBack Mastercard
-- $0 年费，学生信用卡
-- 3% grocery, 1% recurring, 0.5% other
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'Student CashBack Mastercard', 'MASTERCARD', 0.00, 0.005,
     '{"bonusAmount": 125, "minSpend": 2500, "daysToComplete": 90, "description": {"en": "5% cashback on all purchases for the first 3 months (up to $2,500 spend, max $125 bonus).", "zh": "前3个月所有消费享5%返现（最高消费$2,500，最高返现$125）。", "fr": "5% de remise sur tous les achats les 3 premiers mois (jusqu''à 2 500$ de dépenses, max 125$).", "es": "5% de reembolso en todas las compras los primeros 3 meses (hasta $2,500 de gasto, máx $125).", "ko": "첫 3개월 모든 구매에서 5% 캐시백 (최대 $2,500 지출, 최대 $125 보너스).", "ja": "最初の3ヶ月すべての購入で5%キャッシュバック（最大$2,500利用、最大$125ボーナス）。"}}',
     '{"gradient": "linear-gradient(135deg, #1a5fb4 0%, #3584e4 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/student-bmo-cashback-mastercard/', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 8. BMO Prepaid Mastercard
-- $9.99 年费，预付卡，无奖励
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'Prepaid Mastercard', 'MASTERCARD', 9.99, 0.0000,
     '{"bonusAmount": 0, "minSpend": 0, "daysToComplete": 0, "description": {"en": "Reloadable prepaid card accepted at 30+ million locations worldwide. No credit check required.", "zh": "可充值预付卡，全球超过3000万商家接受。无需信用检查。", "fr": "Carte prépayée rechargeable acceptée dans plus de 30 millions de commerces. Aucune vérification de crédit requise.", "es": "Tarjeta prepagada recargable aceptada en más de 30 millones de ubicaciones. Sin verificación de crédito.", "ko": "전 세계 3천만 이상의 가맹점에서 사용 가능한 충전식 선불카드. 신용 조회 불필요.", "ja": "世界3000万以上の加盟店で使える充電式プリペイドカード。信用調査不要。"}}',
     '{"gradient": "linear-gradient(135deg, #1565c0 0%, #1e88e5 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/prepaid-credit-cards/', 0, 1, 'CASHBACK', NULL, NULL);

-- ============================================
-- 9. BMO eclipse rise Visa Card
-- $0 年费，入门级eclipse系列
-- 5x grocery/dining/recurring/takeout, 1x other (per $2)
-- ============================================
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active, reward_type, point_value, point_program) VALUES
    ('BMO', 'eclipse rise Visa', 'VISA', 0.00, 0.00335,
     '{"bonusAmount": 25000, "minSpend": 0, "daysToComplete": 90, "description": {"en": "25,000 welcome points + 0.99% intro rate on balance transfers for 9 months (2% fee). Plus earn up to 5,000 bonus points yearly!", "zh": "25,000开卡积分 + 余额转账9个月0.99%利率(2%手续费)。每年还可获最高5,000奖励积分！", "fr": "25 000 points de bienvenue + taux de 0,99% sur transferts de solde pendant 9 mois (frais de 2%). Plus jusqu''à 5 000 points bonus par an!", "es": "25,000 puntos de bienvenida + 0.99% en transferencias de saldo por 9 meses (2% de cargo). Además gana hasta 5,000 puntos bonus al año!", "ko": "25,000 웰컴 포인트 + 잔액 이체 9개월 0.99% 금리 (2% 수수료). 매년 최대 5,000 보너스 포인트 추가 적립!", "ja": "25,000ウェルカムポイント + 残高移行9ヶ月0.99%金利(2%手数料)。さらに年間最大5,000ボーナスポイント獲得!"}}',
     '{"gradient": "linear-gradient(135deg, #0055a4 0%, #1e90ff 100%)", "textColor": "white"}',
     'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-eclipse-rise-visa/', 0, 1, 'POINTS', 0.0067, 'BMO Rewards');

-- ============================================
-- REWARD RULES for new cards
-- ============================================

-- Student CashBack Mastercard (3% grocery, 1% recurring, 0.5% other)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.03, 500, '3% cashback on groceries (up to $500/statement period)' FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RECURRING', 0.01, 500, '1% cashback on recurring bill payments (up to $500/statement period)' FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- eclipse rise Visa (2.5x on grocery/dining/recurring, 0.5x other)
-- 5 points per $2 = 2.5 points per $1, point value 0.0067, so 2.5 * 0.0067 = 0.01675
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'GROCERY', 0.01675, NULL, '2.5x points on groceries (5 pts per $2)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'DINING', 0.01675, NULL, '2.5x points on dining & takeout/food delivery (5 pts per $2)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
SELECT id, 'RECURRING', 0.01675, NULL, '2.5x points on recurring bill payments (5 pts per $2)' FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- ============================================
-- CARD USAGE TIPS for new cards
-- ============================================

-- Student CashBack Mastercard (10条用卡攻略)
-- 1. BEST_USE - 杂货消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Grocery Shopping", "zh": "杂货购物", "fr": "Courses d''épicerie", "es": "Compras de supermercado", "ko": "식료품 쇼핑", "ja": "食料品の買い物"}',
    '{"en": "Earn 3% cashback on groceries up to $500 per statement period. Perfect for weekly grocery runs.", "zh": "杂货消费可获3%返现，每账单周期最高$500。非常适合每周采购。", "fr": "Gagnez 3% de remise sur l''épicerie jusqu''à 500$ par période. Parfait pour les courses hebdomadaires.", "es": "Gana 3% en supermercados hasta $500 por período. Perfecto para compras semanales.", "ko": "명세서 기간당 최대 $500까지 식료품에서 3% 캐시백. 주간 장보기에 완벽.", "ja": "明細期間ごと$500まで食料品で3%キャッシュバック。毎週の買い物に最適。"}',
    'cart', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 2. BEST_USE - 循环账单
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Recurring Bills", "zh": "循环账单", "fr": "Factures récurrentes", "es": "Facturas recurrentes", "ko": "정기 청구서", "ja": "定期請求"}',
    '{"en": "Earn 1% cashback on recurring bill payments like phone, internet, and streaming services up to $500/period.", "zh": "手机、网络、流媒体等循环账单可获1%返现，每周期最高$500。", "fr": "Gagnez 1% sur les paiements récurrents comme téléphone, internet et streaming jusqu''à 500$/période.", "es": "Gana 1% en pagos recurrentes como teléfono, internet y streaming hasta $500/período.", "ko": "전화, 인터넷, 스트리밍 등 정기 결제에서 기간당 최대 $500까지 1% 캐시백.", "ja": "電話、インターネット、ストリーミングなどの定期支払いで期間あたり$500まで1%キャッシュバック。"}',
    'refresh', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 3. PERK - 建立信用
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Build Credit History", "zh": "建立信用记录", "fr": "Bâtir son historique de crédit", "es": "Construir historial crediticio", "ko": "신용 기록 구축", "ja": "信用履歴の構築"}',
    '{"en": "Build your credit score as a student by paying your balance in full every month. Great for establishing credit history.", "zh": "学生时期通过每月全额还款建立信用评分。非常适合建立信用记录。", "fr": "Bâtissez votre cote de crédit en payant le solde intégral chaque mois. Excellent pour établir un historique.", "es": "Construye tu puntaje crediticio pagando el saldo completo cada mes. Ideal para establecer historial.", "ko": "매월 잔액을 전액 결제하여 학생 시절 신용 점수를 구축하세요. 신용 기록 수립에 좋습니다.", "ja": "毎月残高を全額支払うことで学生時代に信用スコアを構築。信用履歴の確立に最適。"}',
    'trending-up', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 4. PERK - 免年费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "免年费", "fr": "Sans frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "Enjoy all the benefits of a cashback card without paying any annual fee. Perfect for students on a budget.", "zh": "享受返现卡的所有好处，无需支付年费。非常适合预算有限的学生。", "fr": "Profitez de tous les avantages d''une carte remise sans frais annuels. Parfait pour les étudiants.", "es": "Disfruta todos los beneficios de una tarjeta de reembolso sin cuota anual. Perfecto para estudiantes.", "ko": "연회비 없이 캐시백 카드의 모든 혜택을 누리세요. 예산이 제한된 학생에게 완벽.", "ja": "年会費なしでキャッシュバックカードのすべての特典を享受。予算が限られた学生に最適。"}',
    'dollar', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 5. PERK - 开卡奖励
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Welcome Bonus", "zh": "开卡奖励", "fr": "Bonus de bienvenue", "es": "Bono de bienvenida", "ko": "가입 보너스", "ja": "ウェルカムボーナス"}',
    '{"en": "Get 5% cashback on all purchases in your first 3 months, up to $2,500 in spending (max $125 cashback).", "zh": "前3个月所有消费享5%返现，消费上限$2,500（最高返现$125）。", "fr": "Obtenez 5% de remise sur tous les achats les 3 premiers mois, jusqu''à 2 500$ de dépenses (max 125$).", "es": "Obtén 5% de reembolso en todas las compras los primeros 3 meses, hasta $2,500 (máx $125).", "ko": "첫 3개월 모든 구매에서 5% 캐시백, 최대 $2,500 지출 (최대 $125 캐시백).", "ja": "最初の3ヶ月すべての購入で5%キャッシュバック、最大$2,500利用（最大$125キャッシュバック）。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 6. INSURANCE - 购物保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection", "zh": "购物保护", "fr": "Protection des achats", "es": "Protección de compras", "ko": "구매 보호", "ja": "購入保護"}',
    '{"en": "90-day protection against theft or damage for items purchased with your card.", "zh": "使用此卡购买的商品享有90天被盗或损坏保护。", "fr": "Protection de 90 jours contre le vol ou les dommages pour les achats avec votre carte.", "es": "Protección de 90 días contra robo o daño para artículos comprados con tu tarjeta.", "ko": "카드로 구매한 상품에 대해 90일간 도난 또는 손상 보호.", "ja": "カードで購入した商品は90日間、盗難・破損から保護。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 7. INSURANCE - 延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Extended Warranty", "zh": "延长保修", "fr": "Garantie prolongée", "es": "Garantía extendida", "ko": "연장 보증", "ja": "延長保証"}',
    '{"en": "Extends the original manufacturer warranty by up to 1 additional year on eligible purchases.", "zh": "符合条件的购买可延长原厂保修期最多1年。", "fr": "Prolonge la garantie du fabricant jusqu''à 1 an supplémentaire sur les achats admissibles.", "es": "Extiende la garantía del fabricante hasta 1 año adicional en compras elegibles.", "ko": "적격 구매에 대해 제조사 보증을 최대 1년 연장.", "ja": "対象購入品のメーカー保証を最大1年延長。"}',
    'warranty', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 8. AVOID - 外币消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Foreign Currency Purchases", "zh": "外币消费", "fr": "Achats en devises étrangères", "es": "Compras en moneda extranjera", "ko": "외화 결제", "ja": "外貨での購入"}',
    '{"en": "2.5% foreign transaction fee applies. Use a no-FX-fee card for international purchases.", "zh": "外币交易收取2.5%手续费。国际消费请使用无外汇费信用卡。", "fr": "2,5% de frais sur les transactions étrangères. Utilisez une carte sans frais FX pour les achats internationaux.", "es": "Se aplica 2.5% de cargo por transacción extranjera. Usa una tarjeta sin cargo FX para compras internacionales.", "ko": "해외 거래 수수료 2.5%가 부과됩니다. 해외 구매에는 외환 수수료 면제 카드를 사용하세요.", "ja": "外国取引手数料2.5%がかかります。海外購入にはFX手数料なしカードを使用してください。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 9. AVOID - 超过消费上限
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Spending Over Category Caps", "zh": "超过类别上限", "fr": "Dépasser les plafonds de catégorie", "es": "Gastar sobre los límites de categoría", "ko": "카테고리 한도 초과 지출", "ja": "カテゴリ上限を超える支出"}',
    '{"en": "After hitting the $500/period cap on grocery or recurring bills, you only earn 0.5%. Consider splitting purchases.", "zh": "超过每周期$500的杂货或循环账单上限后，只能获得0.5%。考虑分拆消费。", "fr": "Après avoir atteint le plafond de 500$/période sur épicerie ou récurrent, vous ne gagnez que 0,5%.", "es": "Después de alcanzar el límite de $500/período en supermercado o recurrente, solo ganas 0.5%.", "ko": "식료품 또는 정기 결제에서 기간당 $500 한도에 도달한 후에는 0.5%만 적립됩니다.", "ja": "食料品または定期支払いで期間あたり$500の上限に達した後は0.5%のみ獲得。"}',
    'alert', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 10. AVOID - 无旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Travel Insurance", "zh": "无旅行保险", "fr": "Pas d''assurance voyage", "es": "Sin seguro de viaje", "ko": "여행 보험 없음", "ja": "旅行保険なし"}',
    '{"en": "This card does not include travel insurance. Consider purchasing separate coverage for trips.", "zh": "此卡不含旅行保险。旅行时请考虑购买单独的保险。", "fr": "Cette carte ne comprend pas d''assurance voyage. Envisagez une couverture séparée pour les voyages.", "es": "Esta tarjeta no incluye seguro de viaje. Considera comprar cobertura separada para viajes.", "ko": "이 카드에는 여행 보험이 포함되어 있지 않습니다. 여행 시 별도 보험 구매를 고려하세요.", "ja": "このカードには旅行保険が含まれていません。旅行時は別途保険の購入を検討してください。"}',
    'alert', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 11. PERK - 太阳马戏团折扣
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Cirque du Soleil Discount", "zh": "太阳马戏团折扣", "fr": "Rabais Cirque du Soleil", "es": "Descuento Cirque du Soleil", "ko": "태양의 서커스 할인", "ja": "シルク・ドゥ・ソレイユ割引"}',
    '{"en": "Get 20% off Cirque du Soleil shows touring Canada and 15% off resident shows in Las Vegas.", "zh": "加拿大巡演享8折，拉斯维加斯驻场演出享85折优惠。", "fr": "Obtenez 20% de rabais sur les spectacles en tournée au Canada et 15% sur les spectacles résidents à Las Vegas.", "es": "Obtén 20% de descuento en espectáculos en gira por Canadá y 15% en espectáculos residentes en Las Vegas.", "ko": "캐나다 투어 공연 20% 할인, 라스베가스 상주 공연 15% 할인.", "ja": "カナダツアー公演20%オフ、ラスベガス常設公演15%オフ。"}',
    'ticket', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- 12. PERK - 免费附属卡
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Additional Card", "zh": "免费附属卡", "fr": "Carte supplémentaire gratuite", "es": "Tarjeta adicional gratis", "ko": "무료 추가 카드", "ja": "無料追加カード"}',
    '{"en": "Add another cardholder for free. Share the benefits with family or roommates.", "zh": "可免费添加附属卡持卡人。与家人或室友共享福利。", "fr": "Ajoutez un autre titulaire de carte gratuitement. Partagez les avantages avec famille ou colocataires.", "es": "Agrega otro titular de tarjeta gratis. Comparte los beneficios con familia o compañeros.", "ko": "무료로 추가 카드 소지자를 추가할 수 있습니다. 가족이나 룸메이트와 혜택을 공유하세요.", "ja": "無料で別のカード会員を追加できます。家族やルームメイトと特典を共有しましょう。"}',
    'users', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Student CashBack Mastercard';

-- BMO Prepaid Mastercard (10条用卡攻略)
-- 1. BEST_USE - 旅行消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Travel Spending", "zh": "旅行消费", "fr": "Dépenses de voyage", "es": "Gastos de viaje", "ko": "여행 지출", "ja": "旅行での支出"}',
    '{"en": "Use for travel bookings and purchases worldwide. Accepted at 30+ million locations and safer than cash. Get cash at over 1 million ATMs.", "zh": "用于全球旅行预订和消费。超过3000万商家接受，比现金更安全。可在超过100万台ATM取现。", "fr": "Utilisez pour réservations et achats de voyage dans le monde. Acceptée dans plus de 30 millions de commerces, plus de 1 million de guichets.", "es": "Usa para reservas y compras de viaje en todo el mundo. Aceptada en más de 30 millones de ubicaciones. Retira en más de 1 millón de cajeros.", "ko": "전 세계 여행 예약 및 구매에 사용하세요. 3천만 이상의 가맹점, 100만 이상의 ATM에서 사용 가능.", "ja": "世界中での旅行予約や購入に使用。3000万以上の加盟店、100万以上のATMで使用可能。"}',
    'plane', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 2. BEST_USE - 预算管理
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Budget Control", "zh": "预算管理", "fr": "Contrôle du budget", "es": "Control de presupuesto", "ko": "예산 관리", "ja": "予算管理"}',
    '{"en": "Only spend what you load. Perfect for controlling spending or giving to teens with set limits.", "zh": "只能消费已充值的金额。非常适合控制开支或给孩子设定消费限额。", "fr": "Dépensez uniquement ce que vous chargez. Parfait pour contrôler les dépenses ou donner aux ados.", "es": "Solo gasta lo que cargas. Perfecto para controlar gastos o dar a adolescentes con límites.", "ko": "충전한 금액만 사용 가능. 지출 통제나 청소년에게 한도를 설정해 주기에 완벽.", "ja": "チャージした金額のみ使用可能。支出管理や10代への限度設定に最適。"}',
    'wallet', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 3. PERK - 不影响信用评分
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Credit Impact", "zh": "不影响信用评分", "fr": "Aucun impact sur le crédit", "es": "Sin impacto crediticio", "ko": "신용 점수 영향 없음", "ja": "信用スコアへの影響なし"}',
    '{"en": "Soft credit check required to open account, but it will not impact your credit score.", "zh": "开户需要软信用查询，但不会影响您的信用评分。", "fr": "Vérification de crédit souple requise pour ouvrir un compte, mais n''affecte pas votre score.", "es": "Se requiere verificación de crédito suave para abrir cuenta, pero no afecta tu puntaje.", "ko": "계좌 개설 시 소프트 신용 조회가 필요하지만 신용 점수에는 영향이 없습니다.", "ja": "口座開設にはソフト信用照会が必要ですが、信用スコアには影響しません。"}',
    'check', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 4. PERK - 租车折扣
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Car Rental Discounts", "zh": "租车折扣", "fr": "Rabais location de voiture", "es": "Descuentos en alquiler de autos", "ko": "렌터카 할인", "ja": "レンタカー割引"}',
    '{"en": "Save up to 20% on National and Alamo, up to 5% on Enterprise Rent-A-Car worldwide.", "zh": "National和Alamo租车享高达20%折扣，Enterprise租车享高达5%折扣，全球通用。", "fr": "Économisez jusqu''à 20% chez National et Alamo, jusqu''à 5% chez Enterprise dans le monde.", "es": "Ahorra hasta 20% en National y Alamo, hasta 5% en Enterprise en todo el mundo.", "ko": "National 및 Alamo에서 최대 20%, Enterprise에서 최대 5% 할인, 전 세계 적용.", "ja": "NationalとAlamoで最大20%、Enterpriseで最大5%割引、世界中で適用。"}',
    'car', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 5. PERK - Zero Liability 保护
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Zero Liability Protection", "zh": "零责任保护", "fr": "Protection responsabilité zéro", "es": "Protección de responsabilidad cero", "ko": "무책임 보호", "ja": "ゼロ責任保護"}',
    '{"en": "Zero Liability safeguards you if there is any monetary loss resulting from fraudulent card use.", "zh": "如果因欺诈性卡片使用造成任何金钱损失，零责任保护将保障您。", "fr": "La protection zéro responsabilité vous protège contre toute perte due à une utilisation frauduleuse.", "es": "La protección de responsabilidad cero te protege de pérdidas por uso fraudulento de la tarjeta.", "ko": "카드 부정 사용으로 인한 금전적 손실에 대해 무책임 보호가 적용됩니다.", "ja": "カードの不正使用による金銭的損失からゼロ責任保護で守られます。"}',
    'lock', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 6. INSURANCE - 购物保护和延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection & Warranty", "zh": "购物保护和延长保修", "fr": "Protection achats et garantie", "es": "Protección de compras y garantía", "ko": "구매 보호 및 보증", "ja": "購入保護と延長保証"}',
    '{"en": "Extended warranty and purchase protection included. Protects your purchases against damage and theft.", "zh": "包含延长保修和购物保护。保护您的购物免受损坏和盗窃。", "fr": "Garantie prolongée et protection des achats incluses. Protège vos achats contre dommages et vol.", "es": "Garantía extendida y protección de compras incluidas. Protege tus compras contra daños y robo.", "ko": "연장 보증 및 구매 보호 포함. 구매품을 손상 및 도난으로부터 보호합니다.", "ja": "延長保証と購入保護が含まれています。購入品を破損や盗難から保護します。"}',
    'shield', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 7. PERK - 安全功能
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Security Features", "zh": "安全功能", "fr": "Fonctionnalités de sécurité", "es": "Funciones de seguridad", "ko": "보안 기능", "ja": "セキュリティ機能"}',
    '{"en": "Mastercard Identity Check adds extra security online. BMO Alerts confirm your transactions and monitor suspicious activity.", "zh": "Mastercard Identity Check提供额外在线安全。BMO Alerts确认您的交易并监控可疑活动。", "fr": "Mastercard Identity Check ajoute une sécurité en ligne. Les alertes BMO confirment vos transactions.", "es": "Mastercard Identity Check agrega seguridad en línea. Las alertas BMO confirman tus transacciones.", "ko": "Mastercard Identity Check로 온라인 보안 강화. BMO Alerts로 거래 확인 및 의심 활동 모니터링.", "ja": "Mastercard Identity Checkでオンラインセキュリティ強化。BMO Alertsで取引確認と不審な活動を監視。"}',
    'lock', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 8. AVOID - 无返现
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Rewards", "zh": "无奖励", "fr": "Aucune récompense", "es": "Sin recompensas", "ko": "리워드 없음", "ja": "リワードなし"}',
    '{"en": "This card offers no cashback or points. It''s designed for convenience and budget control, not rewards.", "zh": "此卡无返现或积分奖励。它专为便利和预算控制设计，而非赚取奖励。", "fr": "Cette carte n''offre ni remise ni points. Elle est conçue pour la commodité, pas les récompenses.", "es": "Esta tarjeta no ofrece reembolsos ni puntos. Está diseñada para conveniencia, no recompensas.", "ko": "이 카드는 캐시백이나 포인트가 없습니다. 편의성과 예산 관리를 위해 설계되었습니다.", "ja": "このカードはキャッシュバックやポイントがありません。便利さと予算管理のために設計されています。"}',
    'alert', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 9. AVOID - 无法建立信用
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Does Not Build Credit", "zh": "无法建立信用", "fr": "Ne bâtit pas le crédit", "es": "No construye crédito", "ko": "신용 구축 불가", "ja": "信用構築不可"}',
    '{"en": "This is a prepaid card, not a credit card. Using it will not help build your credit history.", "zh": "这是预付卡，不是信用卡。使用它不会帮助建立信用记录。", "fr": "C''est une carte prépayée, pas une carte de crédit. L''utiliser n''aidera pas à bâtir votre crédit.", "es": "Esta es una tarjeta prepagada, no de crédito. Usarla no ayudará a construir tu historial.", "ko": "이것은 선불카드이며 신용카드가 아닙니다. 사용해도 신용 기록 구축에 도움이 되지 않습니다.", "ja": "これはプリペイドカードであり、クレジットカードではありません。使用しても信用履歴の構築には役立ちません。"}',
    'alert', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- 10. AVOID - 有年费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "Annual Fee", "zh": "有年费", "fr": "Frais annuels", "es": "Cuota anual", "ko": "연회비 있음", "ja": "年会費あり"}',
    '{"en": "$9.99 annual fee applies to this prepaid card. Consider if the convenience is worth the cost for your needs.", "zh": "此预付卡需缴纳$9.99年费。请考虑这种便利是否值得您为此付费。", "fr": "Frais annuels de 9,99$ pour cette carte prépayée. Évaluez si la commodité vaut le coût pour vous.", "es": "Cuota anual de $9.99 aplica a esta tarjeta. Considera si la conveniencia vale el costo para ti.", "ko": "이 선불카드에는 $9.99 연회비가 부과됩니다. 편의성이 비용 대비 가치가 있는지 고려하세요.", "ja": "このプリペイドカードには年会費$9.99がかかります。便利さがコストに見合うか検討してください。"}',
    'alert', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'Prepaid Mastercard';

-- BMO eclipse rise Visa (12条用卡攻略)
-- 1. BEST_USE - 杂货消费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Grocery Shopping", "zh": "杂货购物", "fr": "Courses d''épicerie", "es": "Compras de supermercado", "ko": "식료품 쇼핑", "ja": "食料品の買い物"}',
    '{"en": "Earn 2.5x points (5 pts per $2) on groceries. You need to eat, so why not get rewarded at the same time?", "zh": "杂货消费可获2.5倍积分（每$2获5积分）。吃饭是必须的，何不同时获得奖励呢？", "fr": "Gagnez 2,5x points (5 pts par 2$) sur l''épicerie. Vous devez manger, pourquoi ne pas être récompensé?", "es": "Gana 2.5x puntos (5 pts por $2) en supermercados. Tienes que comer, por qué no obtener recompensas?", "ko": "식료품에서 2.5배 포인트 적립 (매 $2당 5포인트). 먹어야 하니까, 동시에 리워드도 받으세요!", "ja": "食料品で2.5倍ポイント（$2あたり5ポイント）獲得。食事は必要だから、同時にリワードも獲得！"}',
    'cart', 1, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 2. BEST_USE - 餐饮和外卖
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Dining & Takeout", "zh": "餐饮和外卖", "fr": "Restaurants et livraison", "es": "Restaurantes y delivery", "ko": "식당 및 테이크아웃", "ja": "飲食とテイクアウト"}',
    '{"en": "Earn 2.5x points (5 pts per $2) on dining out and takeout/food delivery. You''ve got great taste - get rewarded for it!", "zh": "餐厅用餐和外卖可获2.5倍积分（每$2获5积分）。您品味不凡，应该获得奖励！", "fr": "Gagnez 2,5x points (5 pts par 2$) aux restaurants et livraisons. Vous avez bon goût - soyez récompensé!", "es": "Gana 2.5x puntos (5 pts por $2) en restaurantes y delivery. Tienes buen gusto - obtén recompensas!", "ko": "레스토랑과 테이크아웃/배달에서 2.5배 포인트 (매 $2당 5포인트). 훌륭한 취향에 리워드를 받으세요!", "ja": "レストランとテイクアウト/デリバリーで2.5倍ポイント（$2あたり5ポイント）。素晴らしい味覚にリワードを！"}',
    'utensils', 2, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 3. BEST_USE - 循环账单
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
    '{"en": "Recurring Bills", "zh": "循环账单", "fr": "Factures récurrentes", "es": "Facturas recurrentes", "ko": "정기 청구서", "ja": "定期請求"}',
    '{"en": "Earn 2.5x points (5 pts per $2) on recurring bill payments - streaming, gym memberships, cellphone bills and more!", "zh": "循环账单可获2.5倍积分（每$2获5积分）- 流媒体、健身会员、手机账单等！", "fr": "2,5x points (5 pts par 2$) sur paiements récurrents - streaming, gym, téléphone et plus!", "es": "2.5x puntos (5 pts por $2) en pagos recurrentes - streaming, gimnasio, celular y más!", "ko": "정기 결제에서 2.5배 포인트 (매 $2당 5포인트) - 스트리밍, 헬스장, 휴대폰 요금 등!", "ja": "定期支払いで2.5倍ポイント（$2あたり5ポイント）- ストリーミング、ジム、携帯料金など！"}',
    'refresh', 3, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 4. PERK - 免年费
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "No Annual Fee", "zh": "免年费", "fr": "Sans frais annuels", "es": "Sin cuota anual", "ko": "연회비 없음", "ja": "年会費無料"}',
    '{"en": "No annual fee and no income requirement. Perfect entry-level card for Gen Z and Millennials.", "zh": "无年费，无收入要求。非常适合Z世代和千禧一代的入门卡。", "fr": "Sans frais annuels ni exigence de revenu. Carte d''entrée parfaite pour Gen Z et Millennials.", "es": "Sin cuota anual ni requisito de ingresos. Tarjeta perfecta para Gen Z y Millennials.", "ko": "연회비 없음, 소득 요건 없음. Z세대와 밀레니얼 세대를 위한 완벽한 입문 카드.", "ja": "年会費なし、収入要件なし。Z世代とミレニアル世代に最適な入門カード。"}',
    'dollar', 4, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 5. PERK - 开卡奖励
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Welcome Bonus", "zh": "开卡奖励", "fr": "Bonus de bienvenue", "es": "Bono de bienvenida", "ko": "가입 보너스", "ja": "ウェルカムボーナス"}',
    '{"en": "Get 25,000 welcome points + 0.99% intro rate on balance transfers for 9 months (2% transfer fee).", "zh": "获得25,000开卡积分 + 余额转账9个月0.99%优惠利率（2%手续费）。", "fr": "25 000 points de bienvenue + taux de 0,99% sur transferts de solde 9 mois (frais 2%).", "es": "25,000 puntos de bienvenida + 0.99% en transferencias de saldo 9 meses (2% cargo).", "ko": "25,000 웰컴 포인트 + 잔액 이체 9개월 0.99% 우대 금리 (2% 수수료).", "ja": "25,000ウェルカムポイント + 残高移行9ヶ月0.99%金利（2%手数料）。"}',
    'gift', 5, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 6. PERK - 年度奖励积分
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Annual Bonus Points", "zh": "年度奖励积分", "fr": "Points bonus annuels", "es": "Puntos bonus anuales", "ko": "연간 보너스 포인트", "ja": "年間ボーナスポイント"}',
    '{"en": "Earn up to 5,000 bonus points yearly: 2,500 for paying full balance 12 consecutive months + 2,500 for redeeming 12,000+ points annually.", "zh": "每年最高获5,000奖励积分：连续12个月全额还款获2,500 + 年度兑换12,000+积分获2,500。", "fr": "Jusqu''à 5 000 points bonus/an: 2 500 pour paiement 12 mois + 2 500 pour échange 12 000+ pts.", "es": "Hasta 5,000 puntos bonus anuales: 2,500 por pagar 12 meses + 2,500 por canjear 12,000+ puntos.", "ko": "연간 최대 5,000 보너스: 12개월 전액 결제 시 2,500 + 12,000+ 포인트 사용 시 2,500.", "ja": "年間最大5,000ボーナス：12ヶ月全額支払いで2,500 + 12,000ポイント以上交換で2,500。"}',
    'star', 6, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 7. PERK - Instacart+ 福利
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free Instacart+", "zh": "免费Instacart+会员", "fr": "Instacart+ gratuit", "es": "Instacart+ gratis", "ko": "무료 Instacart+", "ja": "無料Instacart+"}',
    '{"en": "Get 3 months of complimentary Instacart+ and a $5 monthly Instacart credit when you enroll your card.", "zh": "注册卡片即可获得3个月免费Instacart+会员和每月$5 Instacart返现。", "fr": "3 mois d''Instacart+ gratuit et crédit mensuel de 5$ en inscrivant votre carte.", "es": "3 meses de Instacart+ gratis y crédito mensual de $5 al registrar tu tarjeta.", "ko": "카드 등록 시 3개월 무료 Instacart+ 및 월 $5 크레딧 제공.", "ja": "カード登録で3ヶ月無料Instacart+と月$5クレジット獲得。"}',
    'cart', 7, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 8. PERK - BMO PaySmart
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Free BMO PaySmart Plan", "zh": "免费BMO PaySmart计划", "fr": "Plan BMO PaySmart gratuit", "es": "Plan BMO PaySmart gratis", "ko": "무료 BMO PaySmart 플랜", "ja": "無料BMO PaySmartプラン"}',
    '{"en": "Get one free BMO PaySmart plan for purchases up to $1,000 every two years. Turn large purchases into smaller monthly payments.", "zh": "每两年可享一次免费BMO PaySmart计划（最高$1,000）。将大额消费分成小额月付。", "fr": "Un plan PaySmart gratuit jusqu''à 1 000$ tous les deux ans. Transformez gros achats en petits paiements.", "es": "Un plan PaySmart gratis hasta $1,000 cada dos años. Convierte compras grandes en pagos mensuales.", "ko": "2년마다 최대 $1,000 구매에 무료 PaySmart 플랜 1회. 대형 구매를 월별 소액 결제로 전환.", "ja": "2年ごとに最大$1,000の購入に無料PaySmartプラン1回。大きな買い物を月々の少額払いに。"}',
    'credit-card', 8, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 9. INSURANCE - 手机保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Mobile Device Insurance", "zh": "手机保险", "fr": "Assurance appareil mobile", "es": "Seguro de dispositivo móvil", "ko": "모바일 기기 보험", "ja": "モバイルデバイス保険"}',
    '{"en": "Up to $1,000 protection for smartphone/tablet against loss, theft or damage worldwide when you pay phone bill or purchase device with card.", "zh": "全球范围内为手机/平板提供最高$1,000的丢失、被盗或损坏保护。用卡支付手机账单或购买设备即可。", "fr": "Jusqu''à 1 000$ de protection pour smartphone/tablette contre perte, vol ou dommage. Payez forfait ou achetez appareil avec la carte.", "es": "Hasta $1,000 de protección para smartphone/tablet contra pérdida, robo o daño. Paga plan o compra dispositivo con la tarjeta.", "ko": "전 세계에서 스마트폰/태블릿의 분실, 도난, 손상에 최대 $1,000 보호. 카드로 요금 결제 또는 기기 구매 시 적용.", "ja": "スマホ/タブレットの紛失・盗難・破損に世界中で最大$1,000保護。カードで料金支払いまたはデバイス購入時に適用。"}',
    'smartphone', 9, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 10. INSURANCE - 购物保护和延长保修
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'INSURANCE',
    '{"en": "Purchase Protection & Warranty", "zh": "购物保护和延长保修", "fr": "Protection achats et garantie", "es": "Protección de compras y garantía", "ko": "구매 보호 및 보증", "ja": "購入保護と延長保証"}',
    '{"en": "90-day purchase protection against theft/damage + extended warranty that doubles manufacturer warranty up to 1 additional year.", "zh": "90天购物保护（防盗/损坏）+ 延长保修（原厂保修期延长一倍，最多1年）。", "fr": "Protection 90 jours contre vol/dommage + garantie prolongée doublant garantie fabricant jusqu''à 1 an.", "es": "Protección 90 días contra robo/daño + garantía extendida duplicando garantía del fabricante hasta 1 año.", "ko": "90일 구매 보호 (도난/손상) + 제조사 보증을 최대 1년 연장하는 연장 보증.", "ja": "90日間の購入保護（盗難/破損）+ メーカー保証を最大1年延長する延長保証。"}',
    'shield', 10, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 11. PERK - 环保卡片
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'PERK',
    '{"en": "Eco-Friendly Card", "zh": "环保卡片", "fr": "Carte écologique", "es": "Tarjeta ecológica", "ko": "친환경 카드", "ja": "エコフレンドリーカード"}',
    '{"en": "Your card is made with recyclable PVC, helping reduce CO2 emissions and environmental impact.", "zh": "您的卡片采用可回收PVC制成，有助于减少二氧化碳排放和环境影响。", "fr": "Votre carte est faite de PVC recyclable, aidant à réduire les émissions de CO2.", "es": "Tu tarjeta está hecha con PVC reciclable, ayudando a reducir emisiones de CO2.", "ko": "카드는 재활용 가능한 PVC로 제작되어 CO2 배출과 환경 영향을 줄이는 데 기여합니다.", "ja": "カードはリサイクル可能なPVCで作られ、CO2排出と環境への影響を軽減します。"}',
    'leaf', 11, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';

-- 12. AVOID - 无旅行保险
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
    '{"en": "No Travel Insurance", "zh": "无旅行保险", "fr": "Pas d''assurance voyage", "es": "Sin seguro de viaje", "ko": "여행 보험 없음", "ja": "旅行保険なし"}',
    '{"en": "This card does not include travel insurance. BMO offers separate Single Trip and Multi-Trip travel insurance plans you can purchase.", "zh": "此卡不含旅行保险。BMO提供单次旅行和多次旅行保险计划可单独购买。", "fr": "Cette carte ne comprend pas d''assurance voyage. BMO offre des plans voyage simple ou multi-voyages à acheter.", "es": "Esta tarjeta no incluye seguro de viaje. BMO ofrece planes de viaje único o múltiple que puedes comprar.", "ko": "이 카드에는 여행 보험이 포함되어 있지 않습니다. BMO에서 단일 또는 다중 여행 보험을 별도로 구매할 수 있습니다.", "ja": "このカードには旅行保険が含まれていません。BMOでは単一旅行または複数旅行保険プランを別途購入できます。"}',
    'alert', 12, 1
FROM credit_cards WHERE bank = 'BMO' AND name = 'eclipse rise Visa';
