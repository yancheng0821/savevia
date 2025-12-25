-- Seed data for Card Usage Tips
-- This script adds usage tips and updates card reward metadata for sample cards

-- ============================================
-- Update card reward type metadata
-- ============================================

-- AMEX Cobalt Card (id=1)
UPDATE credit_cards SET
  reward_type = 'POINTS',
  point_value = 0.02,
  point_program = 'Membership Rewards',
  transfer_partners_json = '[
    {"name": "Aeroplan", "ratio": "1:1", "value": {"en": "~1.5-2 cents/point", "zh": "约1.5-2分/积分", "fr": "~1,5-2 cents/point", "es": "~1,5-2 centavos/punto", "ja": "約1.5-2セント/ポイント", "ko": "약 1.5-2센트/포인트"}},
    {"name": "Marriott Bonvoy", "ratio": "1:1.2", "value": {"en": "~0.8 cents/point", "zh": "约0.8分/积分", "fr": "~0,8 cents/point", "es": "~0,8 centavos/punto", "ja": "約0.8セント/ポイント", "ko": "약 0.8센트/포인트"}},
    {"name": "Hilton Honors", "ratio": "1:2", "value": {"en": "~0.5 cents/point", "zh": "约0.5分/积分", "fr": "~0,5 cents/point", "es": "~0,5 centavos/punto", "ja": "約0.5セント/ポイント", "ko": "약 0.5센트/포인트"}}
  ]'
WHERE name = 'Cobalt Card' AND bank = 'AMEX';

-- AMEX Platinum Card (id=3)
UPDATE credit_cards SET
  reward_type = 'POINTS',
  point_value = 0.02,
  point_program = 'Membership Rewards',
  transfer_partners_json = '[
    {"name": "Aeroplan", "ratio": "1:1", "value": {"en": "~1.5-2 cents/point", "zh": "约1.5-2分/积分", "fr": "~1,5-2 cents/point", "es": "~1,5-2 centavos/punto", "ja": "約1.5-2セント/ポイント", "ko": "약 1.5-2센트/포인트"}},
    {"name": "British Airways", "ratio": "1:1", "value": {"en": "~1.2 cents/point", "zh": "约1.2分/积分", "fr": "~1,2 cents/point", "es": "~1,2 centavos/punto", "ja": "約1.2セント/ポイント", "ko": "약 1.2센트/포인트"}},
    {"name": "Marriott Bonvoy", "ratio": "1:1.2", "value": {"en": "~0.8 cents/point", "zh": "约0.8分/积分", "fr": "~0,8 cents/point", "es": "~0,8 centavos/punto", "ja": "約0.8セント/ポイント", "ko": "약 0.8센트/포인트"}}
  ]'
WHERE name = 'Platinum Card' AND bank = 'AMEX';

-- AMEX SimplyCash Preferred (id=4)
UPDATE credit_cards SET
  reward_type = 'CASHBACK',
  point_value = 0.01,
  point_program = NULL,
  transfer_partners_json = NULL
WHERE name = 'SimplyCash Preferred' AND bank = 'AMEX';

-- Scotiabank Passport Visa Infinite (id=17)
UPDATE credit_cards SET
  reward_type = 'POINTS',
  point_value = 0.01,
  point_program = 'Scene+',
  transfer_partners_json = NULL
WHERE name = 'Passport Visa Infinite' AND bank = 'Scotiabank';

-- TD Cash Back Visa Infinite (id=8)
UPDATE credit_cards SET
  reward_type = 'CASHBACK',
  point_value = 0.01,
  point_program = NULL,
  transfer_partners_json = NULL
WHERE name = 'Cash Back Visa Infinite' AND bank = 'TD';

-- ============================================
-- Insert usage tips
-- ============================================

-- AMEX Cobalt Card Tips
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "Dining and Food Delivery", "zh": "餐饮和外卖", "fr": "Restaurants et livraison", "es": "Restaurantes y delivery", "ja": "飲食とデリバリー", "ko": "외식 및 배달"}',
  '{"en": "Earn 5x points on dining, food delivery apps like Uber Eats, DoorDash, and SkipTheDishes", "zh": "在餐厅和Uber Eats、DoorDash等外卖平台可获得5倍积分", "fr": "Gagnez 5x points sur les restaurants et les apps de livraison comme Uber Eats, DoorDash", "es": "Gana 5x puntos en restaurantes y apps de delivery como Uber Eats, DoorDash", "ja": "レストランやUber Eats、DoorDashなどのデリバリーアプリで5倍ポイント", "ko": "음식점과 Uber Eats, DoorDash 등 배달 앱에서 5배 포인트 적립"}',
  'dining', 1, true
FROM credit_cards WHERE name = 'Cobalt Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "Grocery and Streaming", "zh": "超市和流媒体", "fr": "Épicerie et streaming", "es": "Supermercado y streaming", "ja": "食料品とストリーミング", "ko": "식료품 및 스트리밍"}',
  '{"en": "Earn 5x points at grocery stores and on streaming services like Netflix, Spotify, Disney+", "zh": "在超市和Netflix、Spotify、Disney+等流媒体服务可获得5倍积分", "fr": "Gagnez 5x points dans les épiceries et sur les services de streaming comme Netflix, Spotify", "es": "Gana 5x puntos en supermercados y servicios de streaming como Netflix, Spotify", "ja": "食料品店やNetflix、Spotifyなどのストリーミングサービスで5倍ポイント", "ko": "식료품점과 Netflix, Spotify 등 스트리밍 서비스에서 5배 포인트 적립"}',
  'grocery', 2, true
FROM credit_cards WHERE name = 'Cobalt Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
  '{"en": "Transfer to Aeroplan for Best Value", "zh": "转到Aeroplan获取最佳价值", "fr": "Transférez vers Aeroplan pour la meilleure valeur", "es": "Transfiere a Aeroplan para el mejor valor", "ja": "Aeroplanへの移行が最高価値", "ko": "최고 가치를 위해 Aeroplan으로 전환"}',
  '{"en": "Transfer points 1:1 to Aeroplan and book Air Canada flights for ~2 cents per point value. Business class redemptions can yield even higher value.", "zh": "以1:1比例转积分到Aeroplan兑换加航机票，每点价值约2美分。商务舱兑换可获得更高价值。", "fr": "Transférez les points 1:1 vers Aeroplan et réservez des vols Air Canada pour environ 2 cents par point. Les échanges en classe affaires offrent une valeur encore plus élevée.", "es": "Transfiere puntos 1:1 a Aeroplan y reserva vuelos de Air Canada por ~2 centavos por punto. Los canjes en clase ejecutiva ofrecen mayor valor.", "ja": "1:1でAeroplanに移行し、エアカナダの航空券を1ポイント約2セントで予約。ビジネスクラスの交換はさらに高い価値を得られます。", "ko": "1:1로 Aeroplan으로 전환하고 에어캐나다 항공권을 포인트당 약 2센트 가치로 예약하세요. 비즈니스 클래스 교환은 더 높은 가치를 제공합니다."}',
  'redemption', 1, true
FROM credit_cards WHERE name = 'Cobalt Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'STACKING',
  '{"en": "Stack with Rakuten for Extra Cashback", "zh": "配合Rakuten获取额外返现", "fr": "Combinez avec Rakuten pour du cashback supplémentaire", "es": "Combina con Rakuten para cashback extra", "ja": "Rakutenと併用で追加キャッシュバック", "ko": "Rakuten과 함께 사용하여 추가 캐시백 획득"}',
  '{"en": "Use Rakuten (formerly Ebates) portal before shopping online to earn additional cashback on top of your Cobalt points.", "zh": "在网购前通过Rakuten（原Ebates）门户进入，在Cobalt积分基础上获得额外返现。", "fr": "Utilisez le portail Rakuten (anciennement Ebates) avant de faire des achats en ligne pour gagner du cashback supplémentaire en plus de vos points Cobalt.", "es": "Usa el portal Rakuten (anteriormente Ebates) antes de comprar en línea para ganar cashback adicional además de tus puntos Cobalt.", "ja": "オンラインショッピング前にRakuten（旧Ebates）ポータルを使用すると、Cobaltポイントに加えて追加のキャッシュバックを獲得できます。", "ko": "온라인 쇼핑 전에 Rakuten(이전 Ebates) 포털을 사용하여 Cobalt 포인트 외에 추가 캐시백을 획득하세요."}',
  'stacking', 1, true
FROM credit_cards WHERE name = 'Cobalt Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'AVOID',
  '{"en": "Avoid Fixed Points Travel", "zh": "避免固定积分兑换", "fr": "Évitez les voyages à points fixes", "es": "Evita viajes con puntos fijos", "ja": "固定ポイントの旅行を避ける", "ko": "고정 포인트 여행 피하기"}',
  '{"en": "Avoid using points for Fixed Points Travel bookings through AMEX Travel as you typically get less than 1 cent per point value.", "zh": "避免通过AMEX Travel使用固定积分兑换机票，这种方式每点价值通常不到1美分，不划算。", "fr": "Évitez d utiliser des points pour les réservations Fixed Points Travel via AMEX Travel car vous obtenez généralement moins de 1 cent par point.", "es": "Evita usar puntos para reservas de Fixed Points Travel a través de AMEX Travel ya que normalmente obtienes menos de 1 centavo por punto.", "ja": "AMEX TravelのFixed Points Travelで予約すると、通常1ポイント1セント未満の価値になるため避けましょう。", "ko": "AMEX Travel을 통한 Fixed Points Travel 예약은 일반적으로 포인트당 1센트 미만의 가치를 제공하므로 피하세요."}',
  'avoid', 1, true
FROM credit_cards WHERE name = 'Cobalt Card' AND bank = 'AMEX';

-- AMEX Platinum Card Tips
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "Travel Bookings", "zh": "旅行预订", "fr": "Réservations de voyage", "es": "Reservas de viaje", "ja": "旅行予約", "ko": "여행 예약"}',
  '{"en": "Earn 3x points on travel booked through AMEX Travel or directly with airlines/hotels. Best for premium travel purchases.", "zh": "通过AMEX Travel或直接在航空公司/酒店预订可获得3倍积分。最适合高端旅行消费。", "fr": "Gagnez 3x points sur les voyages réservés via AMEX Travel ou directement avec les compagnies aériennes/hôtels.", "es": "Gana 3x puntos en viajes reservados a través de AMEX Travel o directamente con aerolíneas/hoteles.", "ja": "AMEX Travelまたは航空会社/ホテルで直接予約すると3倍ポイント。プレミアム旅行に最適。", "ko": "AMEX Travel 또는 항공사/호텔에서 직접 예약 시 3배 포인트 적립. 프리미엄 여행에 최적."}',
  'travel', 1, true
FROM credit_cards WHERE name = 'Platinum Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
  '{"en": "Transfer to Airline Partners", "zh": "转换到航空公司伙伴", "fr": "Transférez vers les partenaires aériens", "es": "Transfiere a socios de aerolíneas", "ja": "航空会社パートナーへ移行", "ko": "항공사 파트너로 전환"}',
  '{"en": "Transfer to Aeroplan or British Airways for premium cabin redemptions. Sweet spot: Asia/Europe business class for maximum value.", "zh": "转到Aeroplan或英航兑换高端舱位。甜点：亚洲/欧洲商务舱兑换价值最高。", "fr": "Transférez vers Aeroplan ou British Airways pour des échanges en cabine premium. Point idéal : classe affaires Asie/Europe pour une valeur maximale.", "es": "Transfiere a Aeroplan o British Airways para canjes en cabina premium. Punto ideal: clase ejecutiva a Asia/Europa para máximo valor.", "ja": "Aeroplanまたはブリティッシュ・エアウェイズに移行してプレミアムキャビンを交換。スイートスポット：アジア/ヨーロッパのビジネスクラスが最高価値。", "ko": "Aeroplan 또는 British Airways로 전환하여 프리미엄 캐빈 교환. 스위트 스팟: 아시아/유럽 비즈니스 클래스로 최대 가치 획득."}',
  'redemption', 1, true
FROM credit_cards WHERE name = 'Platinum Card' AND bank = 'AMEX';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'STACKING',
  '{"en": "Maximize Lounge Access", "zh": "最大化贵宾厅使用", "fr": "Maximisez l accès aux salons", "es": "Maximiza el acceso a lounges", "ja": "ラウンジアクセスを最大限活用", "ko": "라운지 접근 최대화"}',
  '{"en": "Use complimentary Priority Pass, Centurion Lounge, and Plaza Premium access. Each visit can be worth $30-50+ in value.", "zh": "使用免费的Priority Pass、百夫长休息室和Plaza Premium。每次使用价值$30-50以上。", "fr": "Utilisez l accès gratuit Priority Pass, Centurion Lounge et Plaza Premium. Chaque visite peut valoir plus de 30-50$.", "es": "Usa el acceso gratuito a Priority Pass, Centurion Lounge y Plaza Premium. Cada visita puede valer más de $30-50.", "ja": "無料のPriority Pass、Centurion Lounge、Plaza Premiumアクセスを活用。各訪問は$30-50以上の価値があります。", "ko": "무료 Priority Pass, Centurion Lounge, Plaza Premium 접근을 활용하세요. 각 방문은 $30-50 이상의 가치가 있습니다."}',
  'stacking', 1, true
FROM credit_cards WHERE name = 'Platinum Card' AND bank = 'AMEX';

-- TD Cash Back Visa Infinite Tips
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "Recurring Bill Payments", "zh": "固定账单支付", "fr": "Paiements de factures récurrentes", "es": "Pagos de facturas recurrentes", "ja": "定期請求書の支払い", "ko": "정기 청구서 결제"}',
  '{"en": "Earn 3% cashback on recurring bills like utilities, phone, internet, and insurance. Set up autopay for all your bills.", "zh": "水电费、电话费、网费、保险等固定账单可获得3%返现。建议设置自动支付。", "fr": "Gagnez 3% de remise sur les factures récurrentes comme les services publics, téléphone, internet et assurance.", "es": "Gana 3% de cashback en facturas recurrentes como servicios, teléfono, internet y seguros.", "ja": "公共料金、電話、インターネット、保険などの定期請求書で3%キャッシュバック。", "ko": "공과금, 전화, 인터넷, 보험 등 정기 청구서에서 3% 캐시백 적립."}',
  'recurring', 1, true
FROM credit_cards WHERE name = 'Cash Back Visa Infinite' AND bank = 'TD';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "Gas and Grocery", "zh": "加油和超市", "fr": "Essence et épicerie", "es": "Gasolina y supermercado", "ja": "ガソリンと食料品", "ko": "주유 및 식료품"}',
  '{"en": "Earn 3% cashback at gas stations and grocery stores. Great for everyday spending categories.", "zh": "在加油站和超市可获得3%返现。非常适合日常消费。", "fr": "Gagnez 3% de remise dans les stations-service et les épiceries. Idéal pour les dépenses quotidiennes.", "es": "Gana 3% de cashback en gasolineras y supermercados. Ideal para gastos cotidianos.", "ja": "ガソリンスタンドと食料品店で3%キャッシュバック。日常の出費に最適。", "ko": "주유소와 식료품점에서 3% 캐시백 적립. 일상 지출에 최적."}',
  'gas', 2, true
FROM credit_cards WHERE name = 'Cash Back Visa Infinite' AND bank = 'TD';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
  '{"en": "Automatic Statement Credit", "zh": "自动账单抵扣", "fr": "Crédit automatique sur relevé", "es": "Crédito automático en estado de cuenta", "ja": "自動明細クレジット", "ko": "자동 명세서 크레딧"}',
  '{"en": "Cashback is automatically credited to your statement - no action needed. Simple and straightforward with no point devaluation risk.", "zh": "返现自动抵扣账单，无需任何操作。简单直接，无积分贬值风险。", "fr": "Le cashback est automatiquement crédité sur votre relevé - aucune action requise. Simple et direct sans risque de dévaluation.", "es": "El cashback se acredita automáticamente a tu estado de cuenta - no se requiere acción. Simple y directo sin riesgo de devaluación.", "ja": "キャッシュバックは自動的に明細にクレジットされます。シンプルで直接的、ポイント価値下落リスクなし。", "ko": "캐시백은 자동으로 명세서에 적립됩니다. 간단하고 직접적이며 포인트 가치 하락 위험이 없습니다."}',
  'redemption', 1, true
FROM credit_cards WHERE name = 'Cash Back Visa Infinite' AND bank = 'TD';

-- Scotiabank Passport Visa Infinite Tips
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'BEST_USE',
  '{"en": "International Travel", "zh": "国际旅行", "fr": "Voyages internationaux", "es": "Viajes internacionales", "ja": "海外旅行", "ko": "해외 여행"}',
  '{"en": "No foreign transaction fees! Use this card for all purchases abroad. Earn 2 points per $1 on dining, entertainment, and transit.", "zh": "无外币手续费！海外消费首选。餐饮、娱乐、交通每消费1加元可获得2积分。", "fr": "Aucun frais de transaction à l étranger! Utilisez cette carte pour tous vos achats à l étranger. Gagnez 2 points par 1$ sur les restaurants, divertissements et transports.", "es": "¡Sin comisiones por transacciones en el extranjero! Usa esta tarjeta para todas las compras en el exterior. Gana 2 puntos por $1 en restaurantes, entretenimiento y transporte.", "ja": "海外取引手数料なし！海外でのすべての買い物にこのカードを使用。飲食、エンターテインメント、交通で$1あたり2ポイント。", "ko": "해외 거래 수수료 없음! 해외에서의 모든 구매에 이 카드를 사용하세요. 외식, 엔터테인먼트, 교통에서 $1당 2포인트 적립."}',
  'travel', 1, true
FROM credit_cards WHERE name = 'Passport Visa Infinite' AND bank = 'Scotiabank';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'REDEMPTION',
  '{"en": "Scene+ Movie Redemptions", "zh": "Scene+电影兑换", "fr": "Échanges de films Scene+", "es": "Canjes de películas Scene+", "ja": "Scene+映画交換", "ko": "Scene+ 영화 교환"}',
  '{"en": "Redeem Scene+ points for free movies at Cineplex. 1,000 points = 1 movie ticket (~$15 value), giving good redemption value.", "zh": "用Scene+积分在Cineplex兑换免费电影票。1,000积分=1张电影票（约$15价值），兑换价值较高。", "fr": "Échangez vos points Scene+ contre des films gratuits chez Cineplex. 1 000 points = 1 billet de cinéma (~15$ de valeur).", "es": "Canjea puntos Scene+ por películas gratis en Cineplex. 1,000 puntos = 1 entrada de cine (~$15 de valor).", "ja": "Scene+ポイントをCineplexの無料映画に交換。1,000ポイント=映画チケット1枚（約$15相当）。", "ko": "Scene+ 포인트를 Cineplex에서 무료 영화로 교환. 1,000포인트 = 영화 티켓 1장 (약 $15 가치)."}',
  'redemption', 1, true
FROM credit_cards WHERE name = 'Passport Visa Infinite' AND bank = 'Scotiabank';

INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
SELECT id, 'STACKING',
  '{"en": "Combine with Travel Portal", "zh": "配合旅行门户使用", "fr": "Combinez avec le portail de voyage", "es": "Combina con el portal de viajes", "ja": "トラベルポータルと併用", "ko": "여행 포털과 함께 사용"}',
  '{"en": "Use the Scotia Rewards travel portal to redeem points for travel at 100 points = $1. Works well for hotels and car rentals.", "zh": "通过Scotia Rewards旅行门户兑换积分，100积分=$1。非常适合酒店和租车兑换。", "fr": "Utilisez le portail de voyage Scotia Rewards pour échanger des points à 100 points = 1$. Idéal pour les hôtels et locations de voitures.", "es": "Usa el portal de viajes Scotia Rewards para canjear puntos a 100 puntos = $1. Funciona bien para hoteles y alquiler de autos.", "ja": "Scotia Rewardsトラベルポータルで100ポイント=$1でポイントを交換。ホテルやレンタカーに最適。", "ko": "Scotia Rewards 여행 포털을 사용하여 100포인트 = $1로 포인트 교환. 호텔 및 렌터카에 적합."}',
  'stacking', 1, true
FROM credit_cards WHERE name = 'Passport Visa Infinite' AND bank = 'Scotiabank';
