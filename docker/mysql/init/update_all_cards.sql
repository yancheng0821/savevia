-- ============================================
-- SaveVia Credit Cards Master Update Script
-- ============================================
-- Description: All credit card updates (signup bonus, tips, etc.)
-- Usage: Run this file to update all card data in production
-- Last Updated: 2025-12-26
-- ============================================

START TRANSACTION;
-- 1. AMEX Aeroplan Card
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
        'bonusAmount', 40000,
        'minSpend', 3000,
        'daysToComplete', 90,
        'description', JSON_OBJECT(
                'en', 'Earn 30,000 pts after $3,000 spend in 3 months + 10,000 pts after $1,000 spend in month 13',
                'zh', '3个月内消费$3,000可获30,000积分 + 第13个月消费$1,000可获10,000积分',
                'fr', 'Obtenez 30 000 pts après 3 000 $ en 3 mois + 10 000 pts après 1 000 $ au 13e mois',
                'es', 'Gana 30,000 pts después de $3,000 en 3 meses + 10,000 pts después de $1,000 en el mes 13',
                'ja', '3ヶ月で$3,000利用後30,000ポイント + 13ヶ月目に$1,000利用後10,000ポイント',
                'ko', '3개월 내 $3,000 사용 시 30,000 포인트 + 13개월차 $1,000 사용 시 10,000 포인트'
                       )
                        )
WHERE bank = 'AMEX' AND name = 'Aeroplan Card';
-- ============================================
-- SECTION 2: AMEX AEROPLAN RESERVE CARD (id=7)
-- ============================================

-- 2.1 Update Aeroplan Reserve Card basic info (color is correct, no change needed)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aeroplan',
    point_value = 0.0160,
    apply_url = 'https://www.americanexpress.com/en-ca/credit-cards/aeroplan-reserve/'
WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card';

-- Note: Reward rules updated in update_all_reward_rules.sql
-- Base: 1.25x, TRAVEL: 3x, DINING: 2x, NO GROCERY

-- 2.2 Update Aeroplan Reserve Card signup bonus (i18n)
-- Total: 85,000 points
-- 60,000 pts after $7,500 spend in 3 months + 25,000 pts after $2,500 spend in month 13
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 85000,
    'minSpend', 7500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', 'Earn 60,000 pts after $7,500 spend in 3 months + 25,000 pts after $2,500 spend in month 13',
        'zh', '3个月内消费$7,500可获60,000积分 + 第13个月消费$2,500可获25,000积分',
        'fr', 'Obtenez 60 000 pts après 7 500 $ en 3 mois + 25 000 pts après 2 500 $ au 13e mois',
        'es', 'Gana 60,000 pts después de $7,500 en 3 meses + 25,000 pts después de $2,500 en el mes 13',
        'ja', '3ヶ月で$7,500利用後60,000ポイント + 13ヶ月目に$2,500利用後25,000ポイント',
        'ko', '3개월 내 $7,500 사용 시 60,000 포인트 + 13개월차 $2,500 사용 시 25,000 포인트'
    )
)
WHERE bank = 'AMEX' AND name = 'Aeroplan Reserve Card';


-- ============================================
-- SECTION 3: AMEX COBALT CARD (id=1)
-- ============================================

-- 3.1 Update Cobalt Card basic info
-- Note: Clear transfer_partners_json (should not show fixed transfer partners)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Membership Rewards',
    point_value = 0.0100,
    apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/',
    transfer_partners_json = NULL
WHERE bank = 'AMEX' AND name = 'Cobalt Card';

-- 3.2 Update Cobalt Card signup bonus (i18n)
-- Total: Up to 15,000 MR points
-- Earn 1,250 pts for each month spending $750 in first year (12 months)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 15000,
    'minSpend', 750,
    'daysToComplete', 365,
    'description', JSON_OBJECT(
        'en', 'Earn 1,250 pts for each month you spend $750 in your first year (up to 15,000 pts total)',
        'zh', '第一年每月消费$750可获1,250积分（最高可获15,000积分）',
        'fr', 'Gagnez 1 250 pts pour chaque mois où vous dépensez 750 $ la première année (jusqu''à 15 000 pts)',
        'es', 'Gana 1,250 pts por cada mes que gastes $750 en tu primer año (hasta 15,000 pts)',
        'ja', '初年度毎月$750利用で1,250ポイント獲得（最大15,000ポイント）',
        'ko', '첫해 매월 $750 사용 시 1,250 포인트 적립 (최대 15,000 포인트)'
    )
)
WHERE bank = 'AMEX' AND name = 'Cobalt Card';


-- ============================================
-- SECTION 4: AMEX GOLD REWARDS CARD (id=2)
-- ============================================

-- 4.1 Update Gold Rewards Card basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Membership Rewards',
    point_value = 0.0100,
    apply_url = 'https://www.americanexpress.com/en-ca/credit-cards/gold-rewards-card/'
WHERE bank = 'AMEX' AND name = 'Gold Rewards Card';

-- 4.2 Update Gold Rewards Card signup bonus (i18n)
-- Total: Up to 60,000 MR points
-- Earn 5,000 pts for each month spending $1,000 in first year (12 months)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 60000,
    'minSpend', 1000,
    'daysToComplete', 365,
    'description', JSON_OBJECT(
        'en', 'Earn 5,000 pts for each month you spend $1,000 in your first year (up to 60,000 pts total)',
        'zh', '第一年每月消费$1,000可获5,000积分（最高可获60,000积分）',
        'fr', 'Gagnez 5 000 pts pour chaque mois où vous dépensez 1 000 $ la première année (jusqu''à 60 000 pts)',
        'es', 'Gana 5,000 pts por cada mes que gastes $1,000 en tu primer año (hasta 60,000 pts)',
        'ja', '初年度毎月$1,000利用で5,000ポイント獲得（最大60,000ポイント）',
        'ko', '첫해 매월 $1,000 사용 시 5,000 포인트 적립 (최대 60,000 포인트)'
    )
)
WHERE bank = 'AMEX' AND name = 'Gold Rewards Card';


-- ============================================
-- SECTION 5: AMEX PLATINUM CARD (id=3)
-- ============================================

-- 5.1 Update Platinum Card basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Membership Rewards',
    point_value = 0.0200,
    apply_url = 'https://www.americanexpress.com/en-ca/charge-cards/the-platinum-card/',
    amex_travel_bonus_rate = 0.01
WHERE bank = 'AMEX' AND name = 'Platinum Card';

-- 5.2 Update Platinum Card signup bonus (i18n)
-- Total: Up to 100,000 MR points
-- 70,000 pts after $10,000 spend in 3 months + 30,000 pts on purchase in months 15-17
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 100000,
    'minSpend', 10000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '70,000 pts after $10,000 spend in 3 months + 30,000 pts on purchase in months 15-17',
        'zh', '3个月内消费$10,000可获70,000积分 + 第15-17个月消费可获30,000积分',
        'fr', '70 000 pts après 10 000 $ en 3 mois + 30 000 pts sur achat aux mois 15-17',
        'es', '70,000 pts después de $10,000 en 3 meses + 30,000 pts en compra en meses 15-17',
        'ja', '3ヶ月で$10,000利用後70,000ポイント + 15-17ヶ月目の購入で30,000ポイント',
        'ko', '3개월 내 $10,000 사용 시 70,000 포인트 + 15-17개월차 구매 시 30,000 포인트'
    )
)
WHERE bank = 'AMEX' AND name = 'Platinum Card';


-- ============================================
-- SECTION 6: AMEX SIMPLYCASH CARD (id=5)
-- ============================================

-- 6.1 Update SimplyCash Card basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/simply-cash/'
WHERE bank = 'AMEX' AND name = 'SimplyCash';

-- 6.2 Update SimplyCash Card signup bonus (i18n)
-- Bonus 5% cash back on all purchases up to $2,000 in first 3 months = up to $100
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 100,
    'minSpend', 2000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', 'Bonus 5% cash back on all purchases (up to $2,000) in first 3 months, on top of regular rates',
        'zh', '前3个月所有消费额外5%返现（最高$2,000消费），在常规返现基础上叠加',
        'fr', 'Bonus 5 % sur tous les achats (jusqu''à 2 000 $) les 3 premiers mois, en plus des taux réguliers',
        'es', 'Bono 5% en todas las compras (hasta $2,000) en los primeros 3 meses, además de las tasas regulares',
        'ja', '最初の3ヶ月、全購入で5%ボーナス還元（$2,000まで）、通常還元に加算',
        'ko', '첫 3개월 모든 구매에 보너스 5% 캐시백 ($2,000까지), 기본 적립률에 추가'
    )
)
WHERE bank = 'AMEX' AND name = 'SimplyCash';


-- ============================================
-- SECTION 7: AMEX SIMPLYCASH PREFERRED CARD (id=4)
-- ============================================

-- 7.1 Update SimplyCash Preferred Card basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    apply_url = 'https://www.americanexpress.com/ca/en/credit-cards/simply-cash-preferred/'
WHERE bank = 'AMEX' AND name = 'SimplyCash Preferred';

-- 7.2 Update SimplyCash Preferred Card signup bonus (i18n)
-- 10% bonus cash back on all purchases up to $2,000 in first 3 months = $200
-- + $50 statement credit when you make a purchase in month 13
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 250,
    'minSpend', 2000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '10% bonus cash back on purchases (up to $2,000) in first 3 months + $50 credit in month 13',
        'zh', '前3个月消费额外10%返现（最高$2,000）+ 第13个月消费获$50抵扣',
        'fr', '10 % bonus sur achats (jusqu''à 2 000 $) les 3 premiers mois + 50 $ au mois 13',
        'es', '10% bono en compras (hasta $2,000) en primeros 3 meses + $50 crédito en mes 13',
        'ja', '最初の3ヶ月、購入で10%ボーナス還元（$2,000まで）+ 13ヶ月目に$50クレジット',
        'ko', '첫 3개월 구매에 10% 보너스 캐시백 ($2,000까지) + 13개월차 $50 크레딧'
    )
)
WHERE bank = 'AMEX' AND name = 'SimplyCash Preferred';


-- ============================================
-- SECTION 8: BMO AIR MILES WORLD ELITE MASTERCARD (id=29)
-- ============================================

-- 8.1 Update Air Miles World Elite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'AIR MILES',
    point_value = 0.0105,
    apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-air-miles-world-elite-mastercard/'
WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard';

-- 8.2 Update Air Miles World Elite signup bonus (i18n)
-- Up to 7,000 AIR MILES + first year free ($120) = ~$1,000 value
-- 3,000 miles after $4,500 in 110 days + 2,000 miles after $1,000 at grocery/wholesale + 2,000 miles varies
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 7000,
    'minSpend', 4500,
    'daysToComplete', 110,
    'description', JSON_OBJECT(
        'en', 'Up to 7,000 AIR MILES: 3,000 after $4,500 spend + 2,000 at grocery/wholesale + 2,000 bonus. First year free ($120 value).',
        'zh', '最高7,000 AIR MILES积分：消费$4,500获3,000 + 超市/仓储店获2,000 + 额外2,000。首年免$120年费。',
        'fr', 'Jusqu''à 7 000 AIR MILES : 3 000 après 4 500 $ + 2 000 épicerie/entrepôt + 2 000 bonus. 1re année gratuite (120 $).',
        'es', 'Hasta 7,000 AIR MILES: 3,000 después de $4,500 + 2,000 en supermercado/mayorista + 2,000 bono. Primer año gratis ($120).',
        'ja', '最大7,000 AIR MILES：$4,500利用で3,000 + 食料品/倉庫店で2,000 + ボーナス2,000。初年度無料（$120相当）。',
        'ko', '최대 7,000 AIR MILES: $4,500 사용 시 3,000 + 식료품/창고형매장 2,000 + 보너스 2,000. 첫해 무료 ($120 가치).'
    )
)
WHERE bank = 'BMO' AND name = 'Air Miles World Elite Mastercard';


-- ============================================
-- SECTION 9: BMO ASCEND WORLD ELITE MASTERCARD (id=55)
-- ============================================

-- 9.1 Update Ascend World Elite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'BMO Rewards',
    point_value = 0.0067,
    apply_url = 'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-ascend-world-elite-mastercard/',
    image_url = '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)", "textColor": "#ffffff"}'
WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard';

-- 9.2 Update Ascend World Elite signup bonus (i18n)
-- Up to 100,000 BMO Rewards points (segmented) + first year free ($150)
-- 45,000 after $5,000 in 110 days + 20,000 after $10,000 in 180 days + 35,000 after $20,000 in 365 days
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 100000,
    'minSpend', 5000,
    'daysToComplete', 110,
    'description', JSON_OBJECT(
        'en', 'Up to 100,000 pts: 45,000 after $5,000 (110 days) + 20,000 after $10,000 (180 days) + 35,000 after $20,000 (365 days). First year free ($150).',
        'zh', '最高100,000积分：$5,000消费获45,000 + $10,000消费获20,000 + $20,000消费获35,000。首年免$150年费。',
        'fr', 'Jusqu''à 100 000 pts : 45 000 après 5 000 $ (110 j) + 20 000 après 10 000 $ (180 j) + 35 000 après 20 000 $ (365 j). 1re année gratuite (150 $).',
        'es', 'Hasta 100,000 pts: 45,000 después de $5,000 (110 días) + 20,000 después de $10,000 (180 días) + 35,000 después de $20,000 (365 días). Primer año gratis ($150).',
        'ja', '最大100,000ポイント：$5,000で45,000 + $10,000で20,000 + $20,000で35,000。初年度無料（$150相当）。',
        'ko', '최대 100,000 포인트: $5,000 시 45,000 + $10,000 시 20,000 + $20,000 시 35,000. 첫해 무료 ($150 가치).'
    )
)
WHERE bank = 'BMO' AND name = 'Ascend World Elite Mastercard';


-- ============================================
-- SECTION 10: BMO CASHBACK MASTERCARD (id=30)
-- ============================================

-- 10.1 Update CashBack Mastercard basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/',
    image_url = '{"gradient": "linear-gradient(135deg, #0079c1 0%, #005a91 100%)", "textColor": "#ffffff"}'
WHERE bank = 'BMO' AND name = 'CashBack Mastercard';

-- 10.2 Update CashBack Mastercard signup bonus (i18n)
-- 5% cash back on first $2,500 in 3 months = up to $125 + potential $50 bonus
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 125,
    'minSpend', 2500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '5% cash back on up to $2,500 spent in first 3 months (up to $125). Plus potential $50 bonus for up to $175 first year value.',
        'zh', '前3个月消费最高$2,500享5%返现（最高$125）。另有$50奖励机会，首年价值最高$175。',
        'fr', '5 % sur jusqu''à 2 500 $ les 3 premiers mois (jusqu''à 125 $). Plus bonus potentiel de 50 $ pour 175 $ la 1re année.',
        'es', '5% en hasta $2,500 en primeros 3 meses (hasta $125). Más bono potencial de $50 para $175 el primer año.',
        'ja', '最初の3ヶ月$2,500まで5%還元（最大$125）。$50ボーナスで初年度最大$175の価値。',
        'ko', '첫 3개월 $2,500까지 5% 캐시백 (최대 $125). $50 보너스로 첫해 최대 $175 가치.'
    )
)
WHERE bank = 'BMO' AND name = 'CashBack Mastercard';


-- ============================================
-- SECTION 11: BMO CASHBACK WORLD ELITE MASTERCARD (id=28)
-- ============================================

-- 11.1 Update CashBack World Elite basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    apply_url = 'https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-cashback-world-elite-mastercard/',
    image_url = '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #333333 100%)", "textColor": "#ffffff"}'
WHERE bank = 'BMO' AND name = 'CashBack World Elite Mastercard';

-- 11.2 Update CashBack World Elite signup bonus (i18n)
-- $40/month for 12 months = $480 + $120 fee waived + $69 Roadside = $650 total
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 480,
    'minSpend', 2000,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '$40 cash back/month when you spend $2,000 (up to $480). First year fee waived ($120) + Roadside Assistance ($69). Total $650 value.',
        'zh', '每月消费$2,000获$40返现（最高$480）。首年免$120年费 + 道路救援（$69）。总价值$650。',
        'fr', '40 $/mois quand vous dépensez 2 000 $ (jusqu''à 480 $). 1re année gratuite (120 $) + Assistance routière (69 $). Valeur 650 $.',
        'es', '$40/mes al gastar $2,000 (hasta $480). Primer año gratis ($120) + Asistencia vial ($69). Valor total $650.',
        'ja', '毎月$2,000利用で$40還元（最大$480）。初年度無料（$120）+ ロードサービス（$69）。総額$650の価値。',
        'ko', '매월 $2,000 사용 시 $40 (최대 $480). 첫해 무료 ($120) + 로드 어시스턴스 ($69). 총 가치 $650.'
    )
)
WHERE bank = 'BMO' AND name = 'CashBack World Elite Mastercard';


-- ============================================
-- SECTION 12: BMO ECLIPSE VISA INFINITE (id=27)
-- ============================================

-- 12.1 Update Eclipse Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'BMO Rewards',
    point_value = 0.0067,
    apply_url = 'https://www.bmo.com/main/personal/credit-cards/bmo-eclipse-visa-infinite/',
    image_url = '{"gradient": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)", "textColor": "#ffffff"}'
WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite';

-- 12.2 Update Eclipse Visa Infinite signup bonus (i18n)
-- Up to 70,000 pts: 40,000 after $3,000 in 3 months + 30,000 at renewal
-- Plus: $120 fee waived + $50 lifestyle credit + $240 streaming credits = $1,150 value
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 70000,
    'minSpend', 3000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '40,000 pts after $3,000 (3 months) + 30,000 at renewal. First year free ($120) + $50 lifestyle credit + $20/month streaming credit. Up to $1,150 value.',
        'zh', '$3,000消费获40,000积分 + 续卡获30,000。首年免$120年费 + $50年度抵扣 + 每月$20流媒体抵扣。总价值$1,150。',
        'fr', '40 000 pts après 3 000 $ (3 mois) + 30 000 au renouvellement. 1re année gratuite (120 $) + crédit 50 $ + 20 $/mois streaming. Valeur 1 150 $.',
        'es', '40,000 pts después de $3,000 (3 meses) + 30,000 al renovar. Primer año gratis ($120) + $50 crédito + $20/mes streaming. Valor $1,150.',
        'ja', '$3,000で40,000ポイント + 更新時30,000。初年度無料（$120）+ $50クレジット + 月$20ストリーミング。総額$1,150の価値。',
        'ko', '$3,000 사용 시 40,000 포인트 + 갱신 시 30,000. 첫해 무료 ($120) + $50 크레딧 + 월 $20 스트리밍. 총 가치 $1,150.'
    )
)
WHERE bank = 'BMO' AND name = 'Eclipse Visa Infinite';


-- ============================================
-- SECTION 13: TRIANGLE WORLD ELITE MASTERCARD (id=49)
-- ============================================

-- 13.1 Update Triangle World Elite basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    point_program = 'CT Money',
    apply_url = 'https://triangle.canadiantire.ca/en/credit-cards/triangle-world-elite-mastercard.html',
    image_url = '{"gradient": "linear-gradient(135deg, #1f2937 0%, #111827 100%)", "textColor": "#ffffff"}'
WHERE bank = 'Canadian Tire' AND name = 'Triangle World Elite Mastercard';

-- 13.2 Update Triangle World Elite signup bonus (i18n)
-- $150 CT Money welcome bonus (limited time offer, apply online)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 150,
    'minSpend', 1,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '$150 CT Money bonus when you apply online and make first purchase within 30 days. Limited time offer.',
        'zh', '在线申请并在30天内完成首笔消费可获$150 CT Money奖励。限时优惠。',
        'fr', 'Bonus de 150 $ en Argent CT en appliquant en ligne et en faisant un achat dans les 30 jours. Offre à durée limitée.',
        'es', 'Bono de $150 CT Money al aplicar en línea y hacer primera compra en 30 días. Oferta por tiempo limitado.',
        'ja', 'オンライン申請後30日以内の初回購入で$150 CT Moneyボーナス。期間限定オファー。',
        'ko', '온라인 신청 후 30일 내 첫 구매 시 $150 CT Money 보너스. 한정 기간 제공.'
    )
)
WHERE bank = 'Canadian Tire' AND name = 'Triangle World Elite Mastercard';


-- ============================================
-- SECTION 14: TRIANGLE MASTERCARD (id=50)
-- ============================================

-- 14.1 Update Triangle Mastercard basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    point_program = 'CT Money',
    apply_url = 'https://triangle.canadiantire.ca/en/credit-cards/triangle-mastercard.html',
    image_url = '{"gradient": "linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%)", "textColor": "#1f2937"}'
WHERE bank = 'Canadian Tire' AND name = 'Triangle Mastercard';

-- 14.2 Update Triangle Mastercard signup bonus (i18n)
-- $150 CT Money welcome bonus (limited time offer, apply online)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 150,
    'minSpend', 1,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '$150 CT Money bonus when you apply online and make first purchase within 30 days. Limited time offer.',
        'zh', '在线申请并在30天内完成首笔消费可获$150 CT Money奖励。限时优惠。',
        'fr', 'Bonus de 150 $ en Argent CT en appliquant en ligne et en faisant un achat dans les 30 jours. Offre à durée limitée.',
        'es', 'Bono de $150 CT Money al aplicar en línea y hacer primera compra en 30 días. Oferta por tiempo limitado.',
        'ja', 'オンライン申請後30日以内の初回購入で$150 CT Moneyボーナス。期間限定オファー。',
        'ko', '온라인 신청 후 30일 내 첫 구매 시 $150 CT Money 보너스. 한정 기간 제공.'
    )
)
WHERE bank = 'Canadian Tire' AND name = 'Triangle Mastercard';


-- ============================================
-- SECTION 15: CIBC ADAPTA MASTERCARD (id=53)
-- ============================================

-- 15.1 Update CIBC Adapta Mastercard basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Adapta Points',
    point_value = 0.0067,
    apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/adapta-mastercard.html',
    image_url = '{"gradient": "linear-gradient(135deg, #ffffff 0%, #f5f5f5 50%, #e8e8e8 100%)", "textColor": "#1a1a1a"}'
WHERE bank = 'CIBC' AND name = 'Adapta Mastercard';

-- 15.2 Update CIBC Adapta Mastercard signup bonus (i18n)
-- Up to 12,000 Adapta Points: 3,000 on first purchase + 9,000 after $1,000 spend in 4 months
-- Value: $80 cashback or $100 on CIBC products + $50 Roadside = up to $150
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 12000,
    'minSpend', 1000,
    'daysToComplete', 120,
    'description', JSON_OBJECT(
        'en', 'Up to 12,000 Adapta Points (~$100 value): 3,000 on first purchase + 9,000 after $1,000 spend in 4 months. Plus $50 Roadside Assistance.',
        'zh', '最高12,000 Adapta积分（约$100价值）：首笔消费获3,000 + 4个月内消费$1,000获9,000。另含$50道路救援。',
        'fr', 'Jusqu''à 12 000 points Adapta (~100 $) : 3 000 au 1er achat + 9 000 après 1 000 $ en 4 mois. Plus assistance routière 50 $.',
        'es', 'Hasta 12,000 puntos Adapta (~$100): 3,000 en primera compra + 9,000 después de $1,000 en 4 meses. Más $50 asistencia vial.',
        'ja', '最大12,000 Adaptaポイント（約$100相当）：初回購入で3,000 + 4ヶ月で$1,000利用後9,000。$50ロードサービス付き。',
        'ko', '최대 12,000 Adapta 포인트 (~$100 가치): 첫 구매 시 3,000 + 4개월 내 $1,000 사용 시 9,000. $50 로드 어시스턴스 포함.'
    )
)
WHERE bank = 'CIBC' AND name = 'Adapta Mastercard';


-- ============================================
-- SECTION 16: CIBC AEROPLAN VISA CARD (id=62)
-- ============================================

-- 16.1 Update CIBC Aeroplan Visa Card basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aeroplan',
    point_value = 0.016,
    apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-card.html',
    image_url = '{"gradient": "linear-gradient(135deg, #d4d4d4 0%, #b8b8b8 100%)", "textColor": "#1a1a1a"}'
WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card';

-- 16.2 Update CIBC Aeroplan Visa Card signup bonus (i18n)
-- Up to 10,000 Aeroplan points: 2.5K on first purchase + 2.5K after $1.5K in 4 months + 5K anniversary on $10K in 12 months
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 10000,
    'minSpend', 1500,
    'daysToComplete', 120,
    'description', JSON_OBJECT(
        'en', '2,500 pts on first purchase + 2,500 after $1,500 in 4 months + 5,000 anniversary bonus after $10,000 in 12 months. No annual fee!',
        'zh', '首笔消费获2,500积分 + 4个月内消费$1,500获2,500 + 12个月消费$10,000获5,000周年奖励。无年费！',
        'fr', '2 500 pts au 1er achat + 2 500 après 1 500 $ en 4 mois + 5 000 bonus anniversaire après 10 000 $ en 12 mois. Sans frais annuels!',
        'es', '2,500 pts en primera compra + 2,500 después de $1,500 en 4 meses + 5,000 bono aniversario después de $10,000 en 12 meses. ¡Sin cuota anual!',
        'ja', '初回購入で2,500ポイント + 4ヶ月で$1,500利用後2,500 + 12ヶ月で$10,000利用後5,000周年ボーナス。年会費無料！',
        'ko', '첫 구매 시 2,500 포인트 + 4개월 내 $1,500 사용 시 2,500 + 12개월 내 $10,000 사용 시 5,000 기념 보너스. 연회비 무료!'
    )
)
WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Card';


-- ============================================
-- SECTION 17: CIBC AEROPLAN VISA INFINITE (id=24)
-- ============================================

-- 17.1 Update CIBC Aeroplan Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aeroplan',
    point_value = 0.016,
    apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-infinite-card.html',
    image_url = '{"gradient": "linear-gradient(135deg, #4b5563 0%, #374151 100%)", "textColor": "#ffffff"}'
WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite';

-- 17.2 Update CIBC Aeroplan Visa Infinite signup bonus (i18n)
-- Up to 45,000 pts: 10K after $6K in 6 months + 25K anniversary after $12K in 12 months
-- Plus: $139 fee waived + $50 per authorized user (up to 3) = up to $289 + free checked bag ($140)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 45000,
    'minSpend', 6000,
    'daysToComplete', 180,
    'description', JSON_OBJECT(
        'en', 'Up to 45,000 pts: 10,000 after $6,000 in 6 months + 25,000 anniversary after $12,000 in 12 months. First year free ($139) + free checked bag.',
        'zh', '最高45,000积分：6个月内消费$6,000获10,000 + 12个月消费$12,000获25,000周年奖励。首年免$139年费 + 免费托运行李。',
        'fr', 'Jusqu''à 45 000 pts : 10 000 après 6 000 $ en 6 mois + 25 000 anniversaire après 12 000 $ en 12 mois. 1re année gratuite (139 $) + bagage gratuit.',
        'es', 'Hasta 45,000 pts: 10,000 después de $6,000 en 6 meses + 25,000 aniversario después de $12,000 en 12 meses. Primer año gratis ($139) + equipaje gratis.',
        'ja', '最大45,000ポイント：6ヶ月で$6,000利用後10,000 + 12ヶ月で$12,000利用後25,000周年ボーナス。初年度無料（$139）+ 無料預け荷物。',
        'ko', '최대 45,000 포인트: 6개월 내 $6,000 사용 시 10,000 + 12개월 내 $12,000 사용 시 25,000 기념 보너스. 첫해 무료 ($139) + 무료 위탁 수하물.'
    )
)
WHERE bank = 'CIBC' AND name = 'Aeroplan Visa Infinite';


-- ============================================
-- SECTION 18: CIBC AVENTURA VISA INFINITE (id=22)
-- ============================================

-- 18.1 Update CIBC Aventura Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aventura',
    point_value = 0.01,
    base_reward_rate = 0.01,
    apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-card.html',
    image_url = '{"gradient": "linear-gradient(135deg, #374151 0%, #1f2937 100%)", "textColor": "#ffffff"}'
WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite';

-- 18.2 Update CIBC Aventura Visa Infinite signup bonus (i18n)
-- Up to 45,000 Aventura Points: 15K on first purchase + 30K after $3K in 4 months
-- Plus: 4 lounge visits/year, $160 NEXUS discount
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 45000,
    'minSpend', 3000,
    'daysToComplete', 120,
    'description', JSON_OBJECT(
        'en', '15,000 pts on first purchase + 30,000 after $3,000 in 4 months. 4 airport lounge visits/year + $160 NEXUS fee discount.',
        'zh', '首笔消费获15,000积分 + 4个月内消费$3,000获30,000。每年4次机场贵宾厅 + $160 NEXUS费用折扣。',
        'fr', '15 000 pts au 1er achat + 30 000 après 3 000 $ en 4 mois. 4 visites salon/an + rabais NEXUS 160 $.',
        'es', '15,000 pts en primera compra + 30,000 después de $3,000 en 4 meses. 4 visitas a salas VIP/año + descuento NEXUS $160.',
        'ja', '初回購入で15,000ポイント + 4ヶ月で$3,000利用後30,000。年4回空港ラウンジ + NEXUS$160割引。',
        'ko', '첫 구매 시 15,000 포인트 + 4개월 내 $3,000 사용 시 30,000. 연 4회 공항 라운지 + NEXUS $160 할인.'
    )
)
WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite';


-- ============================================
-- SECTION 19: CIBC AVENTURA VISA INFINITE PRIVILEGE (id=23)
-- ============================================

-- 19.1 Update CIBC Aventura Visa Infinite Privilege basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aventura',
    point_value = 0.01,
    base_reward_rate = 0.0125,
    apply_url = 'https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-privilege-card.html',
    image_url = '{"gradient": "linear-gradient(135deg, #1f2937 0%, #111827 100%)", "textColor": "#ffffff"}'
WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege';

-- 19.2 Update CIBC Aventura Visa Infinite Privilege signup bonus (i18n)
-- Up to 80,000 Aventura Points: 25K after $3K + 25K after $6K in 4 months + 30K on year 2 renewal
-- Plus: $200 travel credit, 6 lounge visits, $200 NEXUS rebate
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 80000,
    'minSpend', 6000,
    'daysToComplete', 120,
    'description', JSON_OBJECT(
        'en', 'Up to 80,000 pts: 25,000 after $3,000 + 25,000 after $6,000 in 4 months + 30,000 on year 2 renewal. $200 travel credit + 6 lounge visits.',
        'zh', '最高80,000积分：$3,000获25,000 + $6,000获25,000（4个月）+ 续卡获30,000。$200旅行抵扣 + 6次贵宾厅。',
        'fr', 'Jusqu''à 80 000 pts : 25 000 après 3 000 $ + 25 000 après 6 000 $ en 4 mois + 30 000 au renouvellement. Crédit voyage 200 $ + 6 visites salon.',
        'es', 'Hasta 80,000 pts: 25,000 después de $3,000 + 25,000 después de $6,000 en 4 meses + 30,000 al renovar año 2. Crédito viaje $200 + 6 visitas salas VIP.',
        'ja', '最大80,000ポイント：$3,000で25,000 + $6,000で25,000（4ヶ月）+ 2年目更新で30,000。$200旅行クレジット + 6回ラウンジ。',
        'ko', '최대 80,000 포인트: $3,000 시 25,000 + $6,000 시 25,000 (4개월) + 2년차 갱신 시 30,000. $200 여행 크레딧 + 6회 라운지.'
    )
)
WHERE bank = 'CIBC' AND name = 'Aventura Visa Infinite Privilege';


-- ============================================
-- SECTION 20: CIBC DIVIDEND VISA INFINITE (id=25)
-- ============================================
-- Up to $450 in value: 10% cashback up to $300 + $50 pre-auth bonus + $120 fee rebate
-- Annual fee: $120 (first year rebated)

-- 20.1 Update CIBC Dividend Visa Infinite signup bonus (i18n)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 450,
    'minSpend', 3000,
    'daysToComplete', 120,
    'description', JSON_OBJECT(
        'en', 'Up to $450 value: 10% cashback (up to $300) on first 4 statements + $50 pre-authorized payment bonus + $120 first-year fee rebate.',
        'zh', '最高$450价值：首4期账单10%返现(最高$300) + $50预授权付款奖励 + $120首年年费减免。',
        'fr', 'Jusqu''à 450 $ de valeur : 10 % de remise (max 300 $) sur 4 premiers relevés + 50 $ bonus paiement préautorisé + 120 $ de frais remboursés.',
        'es', 'Hasta $450 en valor: 10% cashback (hasta $300) en primeros 4 estados + $50 bono pago preautorizado + $120 reembolso cuota primer año.',
        'ja', '最大$450相当：最初の4明細で10%キャッシュバック(最大$300) + $50事前承認支払いボーナス + $120初年度年会費リベート。',
        'ko', '최대 $450 가치: 첫 4개 명세서에서 10% 캐시백(최대 $300) + $50 사전 승인 결제 보너스 + $120 첫해 연회비 환급.'
    )
)
WHERE bank = 'CIBC' AND name = 'Dividend Visa Infinite';


-- ============================================
-- SECTION 21: DESJARDINS CASH BACK MASTERCARD (id=48)
-- ============================================
-- Fix base_reward_rate: 1% → 0.5%
-- No signup bonus

-- 21.1 Update Desjardins Cash Back Mastercard basic info
UPDATE credit_cards
SET base_reward_rate = 0.005,
    apply_url = 'https://www.desjardins.com/en/credit-cards/cash-back-mastercard.html'
WHERE bank = 'Desjardins' AND name = 'Cash Back Mastercard';


-- ============================================
-- SECTION 22: DESJARDINS CASH BACK WORLD ELITE MASTERCARD (id=47)
-- ============================================
-- Update signup bonus to i18n format
-- Annual fee: $100, Signup bonus: $100

-- 22.1 Update Desjardins Cash Back World Elite Mastercard signup bonus (i18n)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 100,
    'minSpend', 0,
    'daysToComplete', 0,
    'description', JSON_OBJECT(
        'en', '$100 cash back welcome bonus. Auto-credited when you reach $100 in rewards.',
        'zh', '$100开卡返现奖励。累积$100后自动入账。',
        'fr', 'Prime de bienvenue de 100 $ en remise. Créditée automatiquement à 100 $ de récompenses.',
        'es', 'Bono de bienvenida de $100 en cashback. Acreditado automáticamente al alcanzar $100.',
        'ja', '$100キャッシュバックウェルカムボーナス。報酬$100達成時に自動クレジット。',
        'ko', '$100 캐시백 웰컴 보너스. 리워드 $100 도달 시 자동 적립.'
    )
),
    apply_url = 'https://www.desjardins.com/en/credit-cards/cash-back-world-elite-mastercard.html'
WHERE bank = 'Desjardins' AND name = 'Cash Back World Elite Mastercard';


-- ============================================
-- SECTION 23: MBNA AMAZON.CA REWARDS MASTERCARD (id=57)
-- ============================================

-- 23.1 Update Amazon.ca Rewards Mastercard basic info and card image
UPDATE credit_cards
SET image_url = '{"gradient": "linear-gradient(135deg, #1a365d 0%, #0d1b2a 100%)", "textColor": "white"}',
    apply_url = 'https://www.mbna.ca/en/credit-cards/retail-store/amazon-rewards-mastercard'
WHERE bank = 'MBNA' AND name = 'Amazon.ca Rewards Mastercard';

-- 23.2 Update signup bonus with i18n (5% intro offer for 6 months)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 0,
    'minSpend', 0,
    'daysToComplete', 180,
    'description', JSON_OBJECT(
        'en', '5% back at Amazon.ca, Whole Foods, grocery & restaurants for first 6 months (up to $3,000 spend).',
        'zh', '前6个月在Amazon.ca、Whole Foods、超市和餐厅消费享5%返现（最高$3,000消费）。',
        'fr', '5 % sur Amazon.ca, Whole Foods, épiceries et restaurants pendant 6 mois (max 3 000 $ d''achats).',
        'es', '5% en Amazon.ca, Whole Foods, supermercados y restaurantes por 6 meses (hasta $3,000 de gasto).',
        'ja', '最初の6ヶ月間、Amazon.ca、Whole Foods、食料品店、レストランで5%還元（$3,000まで）。',
        'ko', '첫 6개월간 Amazon.ca, Whole Foods, 식료품점, 레스토랑에서 5% 적립 ($3,000 지출까지).'
    )
)
WHERE bank = 'MBNA' AND name = 'Amazon.ca Rewards Mastercard';


-- ============================================
-- SECTION 24: MBNA REWARDS WORLD ELITE MASTERCARD (id=40)
-- ============================================

-- 24.1 Fix reward type and card image (should be POINTS, not CASHBACK)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'MBNA Rewards',
    point_value = 0.0100,
    image_url = '{"gradient": "linear-gradient(135deg, #6b7280 0%, #9ca3af 50%, #6b7280 100%)", "textColor": "white"}',
    apply_url = 'https://www.mbna.ca/en/credit-cards/rewards/mbna-rewards-world-elite-mastercard'
WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard';

-- 24.2 Update signup bonus with i18n (20k + 10k e-statement bonus)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 20000,
    'minSpend', 2000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '20,000 points after $2,000 spend in 90 days. Plus 10,000 bonus points for enrolling in e-statements.',
        'zh', '90天内消费$2,000后获20,000积分。注册电子账单再获10,000积分。',
        'fr', '20 000 points après 2 000 $ en 90 jours. Plus 10 000 points pour les relevés électroniques.',
        'es', '20,000 puntos tras gastar $2,000 en 90 días. Más 10,000 puntos por inscribirse en estados de cuenta electrónicos.',
        'ja', '90日以内に$2,000消費で20,000ポイント。電子明細登録でさらに10,000ポイント。',
        'ko', '90일 내 $2,000 지출 후 20,000 포인트. 전자 명세서 등록 시 10,000 포인트 추가.'
    )
)
WHERE bank = 'MBNA' AND name = 'Rewards World Elite Mastercard';


-- ============================================
-- SECTION 25: MBNA TRUE LINE GOLD MASTERCARD (id=41)
-- ============================================
-- Note: This is a LOW INTEREST card, not a rewards card

-- 25.1 Ensure reward_type is NONE (low interest card, no rewards)
UPDATE credit_cards
SET reward_type = 'NONE',
    base_reward_rate = 0.0000,
    point_program = NULL,
    point_value = NULL
WHERE bank = 'MBNA' AND name = 'True Line Gold Mastercard';


-- ============================================
-- SECTION 26: MERIDIAN VISA CASH BACK (id=59)
-- ============================================

-- 26.1 Fix reward type and base rate (should be POINTS with 0.5% base)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Meridian Rewards',
    point_value = 0.0100,
    base_reward_rate = 0.0050
WHERE bank = 'Meridian' AND name = 'Visa Cash Back';


-- ============================================
-- SECTION 27: MERIDIAN VISA INFINITE CASH BACK (id=58)
-- ============================================

-- 27.1 Fix reward type (should be POINTS, earns Meridian Rewards Points)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Meridian Rewards',
    point_value = 0.0100
WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back';

-- 27.2 Update signup bonus with i18n
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 7000,
    'minSpend', 0,
    'daysToComplete', 0,
    'description', JSON_OBJECT(
        'en', '7,000 bonus points ($70 value) + first year annual fee waived. Up to 5% back in first 3 months.',
        'zh', '7,000积分奖励（价值$70）+ 首年年费减免。前3个月最高5%返现。',
        'fr', '7 000 points bonus (valeur 70 $) + frais annuels de la 1re année annulés. Jusqu''à 5 % les 3 premiers mois.',
        'es', '7,000 puntos de bonificación (valor $70) + cuota anual del primer año gratis. Hasta 5% los primeros 3 meses.',
        'ja', '7,000ボーナスポイント（$70相当）+ 初年度年会費無料。最初の3ヶ月は最大5%還元。',
        'ko', '7,000 보너스 포인트 ($70 가치) + 첫해 연회비 면제. 처음 3개월 최대 5% 적립.'
    )
)
WHERE bank = 'Meridian' AND name = 'Visa Infinite Cash Back';


-- ============================================
-- SECTION 28: NATIONAL BANK WORLD ELITE MASTERCARD (id=42)
-- ============================================

-- 28.1 Fix reward type (should be POINTS, not CASHBACK) and base rate (should be 1%)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'À la carte Rewards',
    point_value = 0.0100,
    base_reward_rate = 0.0100
WHERE bank = 'National Bank' AND name = 'World Elite Mastercard';

-- 28.2 Update signup bonus with i18n
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 30000,
    'minSpend', 1500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '30,000 points ($300 value) after $1,500 spend in 90 days. Plus $250/year travel credit.',
        'zh', '90天内消费$1,500后获30,000积分（价值$300）。另有每年$250旅行额度。',
        'fr', '30 000 points (valeur 300 $) après 1 500 $ en 90 jours. Plus 250 $/an en crédit voyage.',
        'es', '30,000 puntos (valor $300) tras gastar $1,500 en 90 días. Más $250/año en crédito de viaje.',
        'ja', '90日以内に$1,500消費で30,000ポイント（$300相当）。年間$250の旅行クレジット付き。',
        'ko', '90일 내 $1,500 지출 후 30,000 포인트 ($300 가치). 연간 $250 여행 크레딧 추가.'
    )
)
WHERE bank = 'National Bank' AND name = 'World Elite Mastercard';


-- ============================================
-- SECTION 29: NEO WORLD ELITE MASTERCARD (id=35)
-- ============================================

-- 29.1 Update signup bonus with i18n
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 50,
    'minSpend', 500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '$50 welcome bonus after $500 spend in 90 days. Plus 5%+ at Neo partner stores.',
        'zh', '90天内消费$500后获$50开卡奖励。Neo合作商户可获5%+返现。',
        'fr', '50 $ de bienvenue après 500 $ en 90 jours. Plus 5 %+ chez les partenaires Neo.',
        'es', '$50 de bienvenida tras gastar $500 en 90 días. Más 5%+ en tiendas asociadas Neo.',
        'ja', '90日以内に$500消費で$50ウェルカムボーナス。Neoパートナー店舗で5%+。',
        'ko', '90일 내 $500 지출 후 $50 웰컴 보너스. Neo 파트너 매장에서 5%+.'
    )
)
WHERE bank = 'Neo' AND name = 'World Elite Mastercard';


-- ============================================
-- SECTION 30: NEO WORLD MASTERCARD (id=36)
-- ============================================

-- 30.1 Update signup bonus with i18n
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 25,
    'minSpend', 500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '$25 welcome bonus after $500 spend in 90 days. Plus 5%+ at Neo partner stores.',
        'zh', '90天内消费$500后获$25开卡奖励。Neo合作商户可获5%+返现。',
        'fr', '25 $ de bienvenue après 500 $ en 90 jours. Plus 5 %+ chez les partenaires Neo.',
        'es', '$25 de bienvenida tras gastar $500 en 90 días. Más 5%+ en tiendas asociadas Neo.',
        'ja', '90日以内に$500消費で$25ウェルカムボーナス。Neoパートナー店舗で5%+。',
        'ko', '90일 내 $500 지출 후 $25 웰컴 보너스. Neo 파트너 매장에서 5%+.'
    )
)
WHERE bank = 'Neo' AND name = 'World Mastercard';


-- ============================================
-- SECTION 31: PC FINANCIAL WORLD ELITE MASTERCARD (id=37)
-- ============================================

-- 31.1 Fix reward type (should be POINTS - earns PC Optimum points)
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'PC Optimum',
    point_value = 0.0010
WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard';

-- 31.2 Update signup bonus with i18n
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 20000,
    'minSpend', 1000,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '20,000 PC Optimum points ($20 value) after $1,000 spend in 30 days.',
        'zh', '30天内消费$1,000后获20,000 PC Optimum积分（价值$20）。',
        'fr', '20 000 points PC Optimum (valeur 20 $) après 1 000 $ en 30 jours.',
        'es', '20,000 puntos PC Optimum (valor $20) tras gastar $1,000 en 30 días.',
        'ja', '30日以内に$1,000消費で20,000 PC Optimumポイント（$20相当）。',
        'ko', '30일 내 $1,000 지출 후 20,000 PC Optimum 포인트 ($20 가치).'
    )
)
WHERE bank = 'PC Financial' AND name = 'World Elite Mastercard';


-- ============================================
-- SECTION 32: PC FINANCIAL WORLD MASTERCARD (id=38)
-- ============================================

-- 32.1 Update PC Financial World Mastercard basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'PC Optimum',
    point_value = 0.0010
WHERE bank = 'PC Financial' AND name = 'World Mastercard';

-- 32.2 Update PC Financial World Mastercard signup bonus (i18n)
-- 10,000 PC Optimum points ($10 value) welcome offer
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 10000,
    'minSpend', 500,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '10,000 PC Optimum points ($10 value) after $500 spend in 30 days.',
        'zh', '30天内消费$500后获10,000 PC Optimum积分（价值$10）。',
        'fr', '10 000 points PC Optimum (valeur 10 $) après 500 $ en 30 jours.',
        'es', '10,000 puntos PC Optimum (valor $10) tras gastar $500 en 30 días.',
        'ja', '30日以内に$500消費で10,000 PC Optimumポイント（$10相当）。',
        'ko', '30일 내 $500 지출 후 10,000 PC Optimum 포인트 ($10 가치).'
    )
)
WHERE bank = 'PC Financial' AND name = 'World Mastercard';


-- ============================================
-- SECTION 33: RBC AVION VISA INFINITE (id=13)
-- ============================================

-- 33.1 Update RBC Avion Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'RBC Avion Rewards',
    point_value = 0.0100
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite';

-- 33.2 Update RBC Avion Visa Infinite signup bonus (i18n)
-- 35,000 Avion points after $5,000 spend in 90 days
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 35000,
    'minSpend', 5000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '35,000 Avion points after $5,000 spend in 3 months. Worth up to $350 in travel.',
        'zh', '3个月内消费$5,000后获35,000 Avion积分。旅行价值最高$350。',
        'fr', '35 000 points Avion après 5 000 $ en 3 mois. Valeur jusqu''à 350 $ en voyage.',
        'es', '35,000 puntos Avion tras gastar $5,000 en 3 meses. Valor hasta $350 en viajes.',
        'ja', '3ヶ月で$5,000消費後35,000 Avionポイント。旅行で最大$350相当。',
        'ko', '3개월 내 $5,000 지출 후 35,000 Avion 포인트. 여행 시 최대 $350 가치.'
    )
)
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite';


-- ============================================
-- SECTION 34: RBC AVION VISA INFINITE PRIVILEGE (id=14)
-- ============================================

-- 34.1 Update RBC Avion Visa Infinite Privilege basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'RBC Avion Rewards',
    point_value = 0.0100
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege';

-- 34.2 Update RBC Avion Visa Infinite Privilege signup bonus (i18n)
-- Up to 70,000 Avion points (travel value up to $1,500)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 70000,
    'minSpend', 5000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', 'Up to 70,000 Avion points after $5,000 spend in 3 months. Travel value up to $1,500.',
        'zh', '3个月内消费$5,000后可获最高70,000 Avion积分。旅行价值最高$1,500。',
        'fr', 'Jusqu''à 70 000 points Avion après 5 000 $ en 3 mois. Valeur voyage jusqu''à 1 500 $.',
        'es', 'Hasta 70,000 puntos Avion tras gastar $5,000 en 3 meses. Valor de viaje hasta $1,500.',
        'ja', '3ヶ月で$5,000消費後最大70,000 Avionポイント。旅行価値最大$1,500。',
        'ko', '3개월 내 $5,000 지출 후 최대 70,000 Avion 포인트. 여행 가치 최대 $1,500.'
    )
)
WHERE bank = 'RBC' AND name = 'Avion Visa Infinite Privilege';


-- ============================================
-- SECTION 35: RBC CASH BACK MASTERCARD (id=16)
-- ============================================

-- 35.1 Update RBC Cash Back Mastercard signup bonus (i18n)
-- Up to 7% cash back for first 3 months on up to $1,000 (max $70) - Limited time offer
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 70,
    'minSpend', 1000,
    'daysToComplete', 90,
    'isLimitedTime', true,
    'offerEndDate', '2026-03-25',
    'description', JSON_OBJECT(
        'en', 'Limited Time: Up to 7% cash back for first 3 months on up to $1,000 in purchases (max $70). Apply by Mar 25, 2026.',
        'zh', '限时优惠：前3个月消费最高$1,000可获7%返现（最高$70）。需在2026年3月25日前申请。',
        'fr', 'Offre limitée : Jusqu''à 7 % les 3 premiers mois sur 1 000 $ (max 70 $). Demandez avant le 25 mars 2026.',
        'es', 'Oferta limitada: Hasta 7% en los primeros 3 meses en hasta $1,000 (máx $70). Solicita antes del 25 mar 2026.',
        'ja', '期間限定：最初の3ヶ月間、最大$1,000で7%キャッシュバック（最大$70）。2026年3月25日までに申請。',
        'ko', '한정 오퍼: 첫 3개월간 최대 $1,000에 7% 캐시백 (최대 $70). 2026년 3월 25일까지 신청.'
    )
)
WHERE bank = 'RBC' AND name = 'Cash Back Mastercard';


-- ============================================
-- SECTION 36: RBC ION VISA (id=17)
-- ============================================

-- 36.1 Update RBC ION Visa basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'RBC Avion Rewards',
    point_value = 0.0100
WHERE bank = 'RBC' AND name = 'ION Visa';

-- 36.2 Update RBC ION Visa signup bonus (i18n)
-- 7,000 Avion points upon approval, no spend required
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 7000,
    'minSpend', 0,
    'daysToComplete', 60,
    'description', JSON_OBJECT(
        'en', '7,000 Avion welcome points upon approval. No spending required. Worth ~$50 in gift cards.',
        'zh', '开卡即获7,000 Avion欢迎积分。无需消费。价值约$50礼品卡。',
        'fr', '7 000 points Avion de bienvenue à l''approbation. Aucune dépense requise. Valeur ~50 $ en cartes-cadeaux.',
        'es', '7,000 puntos Avion de bienvenida al aprobar. Sin gasto requerido. Valor ~$50 en tarjetas regalo.',
        'ja', '承認時に7,000 Avion歓迎ポイント。消費不要。ギフトカードで約$50相当。',
        'ko', '승인 시 7,000 Avion 웰컴 포인트. 지출 필요 없음. 기프트 카드로 약 $50 가치.'
    )
)
WHERE bank = 'RBC' AND name = 'ION Visa';


-- ============================================
-- SECTION 37: RBC ION+ VISA (id=54)
-- ============================================

-- 37.1 Update RBC ION+ Visa basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'RBC Avion Rewards',
    point_value = 0.0100,
    image_url = '{"gradient": "linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 50%, #a8a8a8 100%)", "textColor": "black"}'
WHERE bank = 'RBC' AND name = 'ION+ Visa';

-- 37.2 Update RBC ION+ Visa signup bonus (i18n)
-- 14,000 Avion points upon approval + limited time grocery bonus
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 14000,
    'minSpend', 0,
    'daysToComplete', 60,
    'isLimitedTime', true,
    'offerEndDate', '2026-03-31',
    'description', JSON_OBJECT(
        'en', '14,000 Avion welcome points upon approval (~$100 value). Plus up to $150 in groceries with Moi. Apply by Mar 31, 2026.',
        'zh', '开卡即获14,000 Avion欢迎积分（约$100价值）。另加Moi最高$150超市优惠。需在2026年3月31日前申请。',
        'fr', '14 000 points Avion à l''approbation (~100 $ valeur). Plus jusqu''à 150 $ d''épicerie avec Moi. Demandez avant le 31 mars 2026.',
        'es', '14,000 puntos Avion al aprobar (~$100 valor). Más hasta $150 en supermercado con Moi. Solicita antes del 31 mar 2026.',
        'ja', '承認時に14,000 Avionポイント（約$100価値）。Moiで最大$150の食料品も。2026年3月31日までに申請。',
        'ko', '승인 시 14,000 Avion 포인트 (~$100 가치). Moi로 최대 $150 식료품 추가. 2026년 3월 31일까지 신청.'
    )
)
WHERE bank = 'RBC' AND name = 'ION+ Visa';


-- ============================================
-- SECTION 38: RBC WESTJET WORLD ELITE MASTERCARD (id=15)
-- ============================================

-- 38.1 Update RBC WestJet World Elite Mastercard basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'WestJet Rewards',
    point_value = 0.0100
WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard';

-- 38.2 Update RBC WestJet World Elite Mastercard signup bonus (i18n)
-- Up to 70,000 WestJet points + companion voucher - Limited time offer
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 70000,
    'minSpend', 5000,
    'daysToComplete', 90,
    'isLimitedTime', true,
    'offerEndDate', '2026-02-04',
    'description', JSON_OBJECT(
        'en', 'Up to 70,000 WestJet points (~$700): 30,000 on first purchase + 30,000 after $5,000 spend + 10,000 anniversary. Plus companion voucher from $119. Apply by Feb 4, 2026.',
        'zh', '最高70,000 WestJet积分（约$700）：首次消费30,000 + $5,000消费后30,000 + 周年10,000。另附$119起同行券。需在2026年2月4日前申请。',
        'fr', 'Jusqu''à 70 000 points WestJet (~700 $) : 30 000 au 1er achat + 30 000 après 5 000 $ + 10 000 anniversaire. Plus billet accompagnateur dès 119 $. Avant le 4 fév 2026.',
        'es', 'Hasta 70,000 puntos WestJet (~$700): 30,000 en primera compra + 30,000 tras $5,000 + 10,000 aniversario. Más voucher acompañante desde $119. Antes del 4 feb 2026.',
        'ja', '最大70,000 WestJetポイント（約$700）：初回購入30,000 + $5,000消費後30,000 + 記念日10,000。$119〜のコンパニオンバウチャー付き。2026年2月4日まで。',
        'ko', '최대 70,000 WestJet 포인트 (~$700): 첫 구매 30,000 + $5,000 지출 후 30,000 + 주년 10,000. $119부터 동반자 바우처. 2026년 2월 4일까지 신청.'
    )
)
WHERE bank = 'RBC' AND name = 'WestJet World Elite Mastercard';


-- ============================================
-- SECTION 39: ROGERS RED MASTERCARD (id=32)
-- ============================================

-- 39.1 Rename Rogers Platinum Mastercard to Rogers Red Mastercard
UPDATE credit_cards
SET name = 'Red Mastercard'
WHERE bank = 'Rogers' AND name = 'Platinum Mastercard';

-- 39.2 Rename Rogers World Elite Mastercard to Rogers Red World Elite Mastercard
UPDATE credit_cards
SET name = 'Red World Elite Mastercard'
WHERE bank = 'Rogers' AND name = 'World Elite Mastercard';

-- 39.3 Update Rogers Red Mastercard signup bonus (i18n)
-- $30 cash back ($45 value when redeemed on Rogers/Fido/Shaw) after $3,000 spend + mobile wallet purchase
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 45,
    'minSpend', 3000,
    'daysToComplete', 105,
    'description', JSON_OBJECT(
        'en', '$30 cash back ($45 value on Rogers) after $3,000 spend + 1 mobile wallet purchase in 105 days.',
        'zh', '105天内消费$3,000+1次移动钱包支付后获$30返现（Rogers兑换价值$45）。',
        'fr', '30 $ remise (45 $ chez Rogers) après 3 000 $ + 1 achat portefeuille mobile en 105 jours.',
        'es', '$30 reembolso ($45 en Rogers) tras $3,000 + 1 compra con billetera móvil en 105 días.',
        'ja', '105日以内に$3,000消費+モバイルウォレット1回で$30キャッシュバック（Rogers交換で$45価値）。',
        'ko', '105일 내 $3,000 지출 + 모바일 월렛 1회 후 $30 캐시백 (Rogers 교환 시 $45 가치).'
    )
)
WHERE bank = 'Rogers' AND name = 'Red Mastercard';


-- ============================================
-- SECTION 40: ROGERS RED WORLD ELITE MASTERCARD (id=31)
-- ============================================

-- 40.1 Update Rogers Red World Elite Mastercard basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0150,
    apply_url = 'https://www.rogersbank.com/en/rogers_red_worldelite_mastercard_details/'
WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard';

-- 40.2 Update Rogers Red World Elite Mastercard signup bonus (currently no bonus)
UPDATE credit_cards
SET signup_bonus_json = NULL
WHERE bank = 'Rogers' AND name = 'Red World Elite Mastercard';


-- ============================================
-- SECTION 41: SCOTIABANK GOLD AMERICAN EXPRESS (id=18)
-- ============================================

-- 41.1 Update Scotiabank Gold Amex basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Scene+',
    point_value = 0.0100,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/american-express/gold-card.html'
WHERE bank = 'Scotiabank' AND name = 'Gold American Express';

-- 41.2 Update Scotiabank Gold Amex signup bonus (i18n)
-- 50,000 Scene+ points ($500 value) - 30K after $2K/3mo + 20K after $7.5K/12mo
-- Limited time offer: Oct 31, 2025 - Jan 1, 2026
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 50000,
    'minSpend', 2000,
    'daysToComplete', 90,
    'isLimitedTime', true,
    'offerEndDate', '2026-01-01',
    'description', JSON_OBJECT(
        'en', '50,000 Scene+ pts ($500): 30K after $2K/3mo + 20K after $7.5K/12mo. First year fee waived.',
        'zh', '50,000 Scene+积分（$500）：3个月消费$2K获30K + 12个月消费$7.5K获20K。首年免年费。',
        'fr', '50 000 pts Scene+ (500 $) : 30K après 2K $/3 mois + 20K après 7,5K $/12 mois. 1re année gratuite.',
        'es', '50,000 pts Scene+ ($500): 30K tras $2K/3mo + 20K tras $7.5K/12mo. Primer año sin cuota.',
        'ja', '50,000 Scene+ポイント（$500）：3ヶ月$2Kで30K + 12ヶ月$7.5Kで20K。初年度年会費無料。',
        'ko', '50,000 Scene+ 포인트 ($500): 3개월 $2K 사용 시 30K + 12개월 $7.5K 사용 시 20K. 첫해 연회비 면제.'
    )
)
WHERE bank = 'Scotiabank' AND name = 'Gold American Express';


-- ============================================
-- SECTION 42: SCOTIABANK MOMENTUM VISA INFINITE (id=20)
-- ============================================

-- 42.1 Update Scotiabank Momentum Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0100,
    apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-infinite-card.html'
WHERE bank = 'Scotiabank' AND name = 'Momentum Visa Infinite';

-- 42.2 Update Scotiabank Momentum Visa Infinite signup bonus (i18n)
-- 10% cash back on first $2,000 = $200 cash back. First year fee waived.
-- Limited time: Oct 31, 2025 - Apr 30, 2026
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 200,
    'minSpend', 2000,
    'daysToComplete', 90,
    'isLimitedTime', true,
    'offerEndDate', '2026-04-30',
    'description', JSON_OBJECT(
        'en', '10% cash back on first $2,000 spent ($200 value). First year $120 annual fee waived.',
        'zh', '前$2,000消费10%返现（价值$200）。首年$120年费免除。',
        'fr', '10 % sur les premiers 2 000 $ (valeur 200 $). Frais annuels de 120 $ gratuits la 1re année.',
        'es', '10% en los primeros $2,000 gastados (valor $200). Cuota anual de $120 gratis el primer año.',
        'ja', '最初の$2,000利用で10%キャッシュバック（$200相当）。初年度$120年会費無料。',
        'ko', '첫 $2,000 사용 시 10% 캐시백 ($200 가치). 첫해 $120 연회비 면제.'
    )
)
WHERE bank = 'Scotiabank' AND name = 'Momentum Visa Infinite';


-- ============================================
-- SECTION 43: SCOTIABANK PASSPORT VISA INFINITE (id=19)
-- ============================================

-- 43.1 Update Scotiabank Passport Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Scene+',
    point_value = 0.0100,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/passport-infinite-card.html'
WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';

-- 43.2 Update Scotiabank Passport Visa Infinite signup bonus (i18n)
-- 35,000 Scene+ points after $2,000 spend in 3 months
-- Plus ongoing: 10,000 pts/year for $40K spend
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 35000,
    'minSpend', 2000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '35,000 Scene+ pts ($350) after $2,000 in 3 months. Plus 10,000 pts/year for $40K annual spend.',
        'zh', '3个月消费$2,000获35,000 Scene+积分（$350）。另外年消费$4万可获10,000积分。',
        'fr', '35 000 pts Scene+ (350 $) après 2 000 $ en 3 mois. Plus 10 000 pts/an pour 40 K$ de dépenses.',
        'es', '35,000 pts Scene+ ($350) tras $2,000 en 3 meses. Más 10,000 pts/año por $40K de gasto anual.',
        'ja', '3ヶ月で$2,000利用後35,000 Scene+ポイント（$350）。年間$4万利用で10,000ポイント追加。',
        'ko', '3개월 $2,000 사용 시 35,000 Scene+ 포인트 ($350). 연간 $4만 사용 시 10,000 포인트 추가.'
    )
)
WHERE bank = 'Scotiabank' AND name = 'Passport Visa Infinite';


-- ============================================
-- SECTION 44: SCOTIABANK SCENE+ VISA (id=21)
-- ============================================

-- 44.1 Update Scotiabank Scene+ Visa basic info
-- Fix: reward_type was CASHBACK, should be POINTS
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Scene+',
    point_value = 0.0100,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scene-card.html'
WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa';

-- 44.2 Update Scotiabank Scene+ Visa signup bonus (i18n)
-- 5,000 Scene+ points: 2,500 after $250 + 2,500 after $1,000 total in 3 months
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 5000,
    'minSpend', 1000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '5,000 Scene+ pts ($50): 2,500 after $250 + 2,500 after $1,000 total in 3 months.',
        'zh', '5,000 Scene+积分（$50）：消费$250获2,500 + 总消费$1,000再获2,500，3个月内完成。',
        'fr', '5 000 pts Scene+ (50 $) : 2 500 après 250 $ + 2 500 après 1 000 $ total en 3 mois.',
        'es', '5,000 pts Scene+ ($50): 2,500 tras $250 + 2,500 tras $1,000 total en 3 meses.',
        'ja', '5,000 Scene+ポイント（$50）：$250で2,500 + 合計$1,000で2,500、3ヶ月以内。',
        'ko', '5,000 Scene+ 포인트 ($50): $250 사용 시 2,500 + 총 $1,000 사용 시 2,500, 3개월 내.'
    )
)
WHERE bank = 'Scotiabank' AND name = 'Scene+ Visa';


-- ============================================
-- SECTION 45: SIMPLII CASH BACK VISA (id=39)
-- ============================================

-- 45.1 Update Simplii Cash Back Visa basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0050,
    apply_url = 'https://www.simplii.com/en/credit-cards/cash-back-visa.html'
WHERE bank = 'Simplii' AND name = 'Cash Back Visa Card';

-- 45.2 Update Simplii Cash Back Visa signup bonus (i18n)
-- Double cashback (8% instead of 4%) on restaurants for first 3 months (up to $80) + $50 PRESTO voucher
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 130,
    'minSpend', 0,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', 'Double restaurant cashback (8%) for 3 months (up to $80) + $50 PRESTO voucher.',
        'zh', '前3个月餐饮双倍返现（8%，最高$80）+ $50 PRESTO券。',
        'fr', 'Double remise restos (8 %) pendant 3 mois (jusqu''à 80 $) + bon PRESTO de 50 $.',
        'es', 'Doble cashback restaurantes (8%) por 3 meses (hasta $80) + voucher PRESTO $50.',
        'ja', '3ヶ月間レストラン2倍キャッシュバック（8%、最大$80）+ $50 PRESTOバウチャー。',
        'ko', '3개월간 레스토랑 더블 캐시백(8%, 최대 $80) + $50 PRESTO 바우처.'
    )
)
WHERE bank = 'Simplii' AND name = 'Cash Back Visa Card';


-- ============================================
-- SECTION 46: TANGERINE MONEY-BACK CREDIT CARD (id=33)
-- ============================================

-- 46.1 Update Tangerine Money-Back basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0050,
    apply_url = 'https://www.tangerine.ca/en/personal/spend/credit-cards/money-back-credit-card'
WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card';

-- 46.2 Update Tangerine Money-Back signup bonus (i18n)
-- 10% cash back for 2 months on up to $1,000 = up to $100
-- Limited time: until January 30, 2026
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 100,
    'minSpend', 0,
    'daysToComplete', 60,
    'isLimitedTime', true,
    'offerEndDate', '2026-01-30',
    'description', JSON_OBJECT(
        'en', '10% cash back for 2 months on up to $1,000 purchases (up to $100 value).',
        'zh', '前2个月消费最高$1,000可获10%返现（最高$100）。',
        'fr', '10 % pendant 2 mois sur achats jusqu''à 1 000 $ (valeur jusqu''à 100 $).',
        'es', '10% por 2 meses en compras hasta $1,000 (hasta $100 de valor).',
        'ja', '2ヶ月間最大$1,000の購入で10%キャッシュバック（最大$100）。',
        'ko', '2개월간 최대 $1,000 구매에서 10% 캐시백 (최대 $100 가치).'
    )
)
WHERE bank = 'Tangerine' AND name = 'Money-Back Credit Card';


-- ============================================
-- SECTION 47: TANGERINE WORLD MASTERCARD (id=34)
-- ============================================

-- 47.1 Update Tangerine World Mastercard basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0050,
    apply_url = 'https://www.tangerine.ca/en/products/spending/creditcard/world'
WHERE bank = 'Tangerine' AND name = 'World Mastercard';

-- 47.2 Update Tangerine World Mastercard signup bonus (i18n)
-- $120 after spending $1,500 in first 3 months
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 120,
    'minSpend', 1500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '$120 cash back after spending $1,500 in first 3 months.',
        'zh', '3个月内消费$1,500可获$120返现。',
        'fr', '120 $ après 1 500 $ de dépenses en 3 mois.',
        'es', '$120 después de gastar $1,500 en los primeros 3 meses.',
        'ja', '3ヶ月以内に$1,500利用で$120キャッシュバック。',
        'ko', '3개월 내 $1,500 사용 시 $120 캐시백.'
    )
)
WHERE bank = 'Tangerine' AND name = 'World Mastercard';


-- ============================================
-- SECTION 48: TD AEROPLAN VISA INFINITE (id=10)
-- ============================================

-- 48.1 Update TD Aeroplan Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aeroplan',
    point_value = 0.0150,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-card'
WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite';

-- 48.2 Update TD Aeroplan Visa Infinite signup bonus (i18n)
-- Current offer: 10,000 pts on first purchase + 15,000 pts after $7,500 spend in 180 days
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 25000,
    'minSpend', 7500,
    'daysToComplete', 180,
    'description', JSON_OBJECT(
        'en', '10,000 points on first purchase + 15,000 bonus points after spending $7,500 in 180 days. First year annual fee waived.',
        'zh', '首次消费获10,000积分 + 180天内消费$7,500再获15,000积分。首年年费减免。',
        'fr', '10 000 points sur premier achat + 15 000 points après 7 500 $ en 180 jours. Frais annuels exonérés la 1re année.',
        'es', '10,000 puntos en primera compra + 15,000 puntos después de $7,500 en 180 días. Cuota anual exonerada el primer año.',
        'ja', '初回購入で10,000ポイント + 180日以内に$7,500利用で15,000ポイント。初年度年会費無料。',
        'ko', '첫 구매 시 10,000 포인트 + 180일 내 $7,500 사용 시 15,000 포인트. 첫해 연회비 면제.'
    )
)
WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite';


-- ============================================
-- SECTION 49: TD AEROPLAN VISA INFINITE PRIVILEGE (id=11)
-- ============================================

-- 49.1 Update TD Aeroplan Visa Infinite Privilege basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Aeroplan',
    point_value = 0.0150,
    base_reward_rate = 0.0125,
    apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-privilege-card'
WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege';

-- 49.2 Update TD Aeroplan Visa Infinite Privilege signup bonus (i18n)
-- Current offer: 20,000 pts on first purchase + 35,000 pts after $12,000 spend in 180 days
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 55000,
    'minSpend', 12000,
    'daysToComplete', 180,
    'description', JSON_OBJECT(
        'en', '20,000 points on first purchase + 35,000 points after spending $12,000 in 180 days. Plus 30,000 anniversary bonus.',
        'zh', '首次消费获20,000积分 + 180天内消费$12,000再获35,000积分。另有30,000周年奖励。',
        'fr', '20 000 points au 1er achat + 35 000 points après 12 000 $ en 180 jours. Plus 30 000 pts anniversaire.',
        'es', '20,000 puntos en primera compra + 35,000 puntos después de $12,000 en 180 días. Más 30,000 pts aniversario.',
        'ja', '初回購入で20,000ポイント + 180日以内に$12,000利用で35,000ポイント。さらに30,000pt周年ボーナス。',
        'ko', '첫 구매 시 20,000 포인트 + 180일 내 $12,000 사용 시 35,000 포인트. 추가로 30,000pt 주년 보너스.'
    )
)
WHERE bank = 'TD' AND name = 'Aeroplan Visa Infinite Privilege';


-- ============================================
-- SECTION 50: TD CASH BACK VISA (id=12)
-- ============================================

-- 50.1 Update TD Cash Back Visa basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    base_reward_rate = 0.0050,
    apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-card'
WHERE bank = 'TD' AND name = 'Cash Back Visa';

-- 50.2 Update TD Cash Back Visa signup bonus (i18n)
-- Current offer: $10 on first purchase + $40 after $1,500 in 3 months = $50
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 50,
    'minSpend', 1500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '$10 on first purchase + $40 after spending $1,500 in 3 months. No annual fee.',
        'zh', '首次消费获$10 + 3个月内消费$1,500再获$40。免年费。',
        'fr', '10 $ au 1er achat + 40 $ après 1 500 $ en 3 mois. Sans frais annuels.',
        'es', '$10 en primera compra + $40 después de $1,500 en 3 meses. Sin cuota anual.',
        'ja', '初回購入で$10 + 3ヶ月以内に$1,500利用で$40。年会費無料。',
        'ko', '첫 구매 시 $10 + 3개월 내 $1,500 사용 시 $40. 연회비 무료.'
    )
)
WHERE bank = 'TD' AND name = 'Cash Back Visa';


-- ============================================
-- SECTION 51: TD CASH BACK VISA INFINITE (id=8)
-- ============================================

-- 51.1 Update TD Cash Back Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    point_value = NULL,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card'
WHERE bank = 'TD' AND name = 'Cash Back Visa Infinite';

-- 51.2 Update TD Cash Back Visa Infinite signup bonus (i18n)
-- Current offer: 10% on bonus categories first 3 months (up to $3,500 spend = $350) + first year fee waived ($139)
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 350,
    'minSpend', 3500,
    'daysToComplete', 90,
    'isLimitedTime', false,
    'description', JSON_OBJECT(
        'en', '10% cash back on bonus categories for first 3 months (up to $3,500 spend). First year $139 fee waived.',
        'zh', '前3个月奖励类别10%返现（最高消费$3,500）。首年$139年费减免。',
        'fr', '10 % sur catégories bonus pendant 3 mois (jusqu''à 3 500 $). Frais de 139 $ exonérés la 1re année.',
        'es', '10% en categorías bonus por 3 meses (hasta $3,500 de gasto). Cuota de $139 exonerada el primer año.',
        'ja', '最初の3ヶ月間ボーナスカテゴリで10%（最大$3,500まで）。初年度$139年会費無料。',
        'ko', '첫 3개월간 보너스 카테고리에서 10% (최대 $3,500 지출). 첫해 $139 연회비 면제.'
    )
)
WHERE bank = 'TD' AND name = 'Cash Back Visa Infinite';


-- ============================================
-- SECTION 52: TD FIRST CLASS VISA INFINITE (id=9)
-- ============================================

-- 52.1 Update TD First Class Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'TD Rewards',
    point_value = 0.0050,
    base_reward_rate = 0.0200,
    apply_url = 'https://www.td.com/ca/en/personal-banking/products/credit-cards/travel-rewards/first-class-travel-visa-infinite-card'
WHERE bank = 'TD' AND name = 'First Class Visa Infinite';

-- 52.2 Update TD First Class Visa Infinite signup bonus (i18n)
-- Current offer: 20,000 pts on first purchase + 145,000 pts after $7,500 in 180 days = 165,000 total
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 165000,
    'minSpend', 7500,
    'daysToComplete', 180,
    'description', JSON_OBJECT(
        'en', '20,000 points on first purchase + 145,000 points after $7,500 in 180 days. First year $139 fee waived.',
        'zh', '首次消费获20,000积分 + 180天内消费$7,500再获145,000积分。首年$139年费减免。',
        'fr', '20 000 points au 1er achat + 145 000 points après 7 500 $ en 180 jours. Frais de 139 $ exonérés la 1re année.',
        'es', '20,000 puntos en primera compra + 145,000 puntos después de $7,500 en 180 días. Cuota de $139 exonerada el primer año.',
        'ja', '初回購入で20,000ポイント + 180日以内に$7,500利用で145,000ポイント。初年度$139年会費無料。',
        'ko', '첫 구매 시 20,000 포인트 + 180일 내 $7,500 사용 시 145,000 포인트. 첫해 $139 연회비 면제.'
    )
)
WHERE bank = 'TD' AND name = 'First Class Visa Infinite';


-- ============================================
-- SECTION 53: VANCITY ENVIRO VISA CLASSIC (id=52)
-- ============================================

-- 53.1 Update Vancity enviro Visa Classic basic info
-- Note: 1 point per $2 = 1x base, point_value adjusted to 0.5 cents so effective rate = 0.5%
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Vancity Rewards',
    point_value = 0.0050,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.vancity.com/bank/credit-cards/enviro-classic/'
WHERE bank = 'Vancity' AND name = 'enviro Visa Classic';

-- 53.2 Update Vancity enviro Visa Classic signup bonus (i18n)
-- Current offer: 5,000 points ($50 value) after $1,500 in 3 months
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 50,
    'minSpend', 1500,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '5,000 Vancity Rewards points ($50 value) after spending $1,500 in first 3 months.',
        'zh', '3个月内消费$1,500可获5,000 Vancity积分（价值$50）。',
        'fr', '5 000 points Vancity (valeur 50 $) après 1 500 $ en 3 mois.',
        'es', '5,000 puntos Vancity ($50 valor) después de $1,500 en 3 meses.',
        'ja', '3ヶ月で$1,500利用後5,000 Vancityポイント（$50相当）。',
        'ko', '3개월 내 $1,500 사용 시 5,000 Vancity 포인트 ($50 가치).'
    )
)
WHERE bank = 'Vancity' AND name = 'enviro Visa Classic';


-- ============================================
-- SECTION 54: VANCITY ENVIRO VISA INFINITE (id=51)
-- ============================================

-- 54.1 Update Vancity enviro Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'POINTS',
    point_program = 'Vancity Rewards',
    point_value = 0.0100,
    base_reward_rate = 0.0125,
    apply_url = 'https://www.vancity.com/bank/credit-cards/enviro-infinite/'
WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite';

-- 54.2 Update Vancity enviro Visa Infinite signup bonus (i18n)
-- Current offer: 5,000 pts on first purchase + 13,000 pts after $3,000 in 3 months = 18,000 total
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 180,
    'minSpend', 3000,
    'daysToComplete', 90,
    'description', JSON_OBJECT(
        'en', '5,000 points on first purchase + 13,000 points after $3,000 in 3 months. First year $120 fee waived.',
        'zh', '首次消费获5,000积分 + 3个月内消费$3,000再获13,000积分。首年$120年费减免。',
        'fr', '5 000 points au 1er achat + 13 000 points après 3 000 $ en 3 mois. Frais de 120 $ exonérés la 1re année.',
        'es', '5,000 puntos en primera compra + 13,000 puntos después de $3,000 en 3 meses. Cuota de $120 exonerada el primer año.',
        'ja', '初回購入で5,000ポイント + 3ヶ月以内に$3,000利用で13,000ポイント。初年度$120年会費無料。',
        'ko', '첫 구매 시 5,000 포인트 + 3개월 내 $3,000 사용 시 13,000 포인트. 첫해 $120 연회비 면제.'
    )
)
WHERE bank = 'Vancity' AND name = 'enviro Visa Infinite';


-- ============================================
-- SECTION 55: WALMART REWARDS MASTERCARD (id=56)
-- ============================================

-- 55.1 Update Walmart Rewards Mastercard basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    point_program = NULL,
    point_value = NULL,
    base_reward_rate = 0.0100,
    apply_url = 'https://www.walmartrewards.ca/en/creditcards'
WHERE bank = 'Walmart' AND name = 'Rewards Mastercard';

-- 55.2 Update Walmart Rewards Mastercard signup bonus (i18n)
-- $25 Walmart Reward Dollars after $75 spend in 30 days
UPDATE credit_cards
SET signup_bonus_json = JSON_OBJECT(
    'bonusAmount', 25,
    'minSpend', 75,
    'daysToComplete', 30,
    'description', JSON_OBJECT(
        'en', '$25 Walmart Reward Dollars after spending $75 in first 30 days',
        'zh', '30天内消费$75可获$25沃尔玛奖励金',
        'fr', '25 $ en Dollars Récompenses Walmart après 75 $ en 30 jours',
        'es', '$25 en Dólares de Recompensa Walmart después de gastar $75 en 30 días',
        'ja', '30日以内に$75利用で$25ウォルマートリワードドル獲得',
        'ko', '30일 내 $75 사용 시 $25 월마트 리워드 달러 획득'
    )
)
WHERE bank = 'Walmart' AND name = 'Rewards Mastercard';


-- ============================================
-- SECTION 56: WEALTHSIMPLE VISA INFINITE (id=46)
-- ============================================

-- 56.1 Update Wealthsimple Visa Infinite basic info
UPDATE credit_cards
SET reward_type = 'CASHBACK',
    point_program = NULL,
    point_value = NULL,
    base_reward_rate = 0.0200,
    apply_url = 'https://www.wealthsimple.com/en-ca/credit-card'
WHERE bank = 'Wealthsimple' AND name = 'Visa Infinite';

-- 56.2 No welcome bonus - set to NULL
-- Fee waiver with $100K assets or $4K/month direct deposit is not a signup bonus
UPDATE credit_cards
SET signup_bonus_json = NULL
WHERE bank = 'Wealthsimple' AND name = 'Visa Infinite';


-- ============================================
-- SECTION 57: [ADD MORE CARDS BELOW]
-- ============================================
-- Template for adding new card updates:
--
-- -- X.1 Update [Card Name] basic info
-- UPDATE credit_cards
-- SET reward_type = 'POINTS',  -- or 'CASHBACK'
--     point_program = 'Program Name',
--     point_value = 0.0100,
--     apply_url = 'https://...'
-- WHERE bank = 'BANK' AND name = 'Card Name';
--
-- -- X.2 Update [Card Name] signup bonus (i18n)
-- UPDATE credit_cards
-- SET signup_bonus_json = JSON_OBJECT(
--     'bonusAmount', 50000,
--     'minSpend', 3000,
--     'daysToComplete', 90,
--     'description', JSON_OBJECT(
--         'en', 'English description',
--         'zh', '中文描述',
--         'fr', 'Description française',
--         'es', 'Descripción en español',
--         'ja', '日本語の説明',
--         'ko', '한국어 설명'
--     )
-- )
-- WHERE bank = 'BANK' AND name = 'Card Name';




COMMIT;
