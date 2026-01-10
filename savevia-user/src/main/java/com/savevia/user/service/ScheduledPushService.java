package com.savevia.user.service;

import com.savevia.user.dto.UserCardRewardInfo;
import com.savevia.user.entity.UserDevice;
import com.savevia.user.mapper.PushNotificationMapper;
import com.savevia.user.mapper.UserCardMapper;
import com.savevia.user.mapper.UserDeviceMapper;
import com.savevia.user.mapper.UserEventMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;

/**
 * Smart push notification service with personalized content
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ScheduledPushService {

    private final PushNotificationService pushNotificationService;
    private final UserDeviceMapper userDeviceMapper;
    private final UserCardMapper userCardMapper;
    private final PushNotificationMapper pushNotificationMapper;
    private final UserEventMapper userEventMapper;

    // Common spending categories
    private static final List<String> COMMON_CATEGORIES = List.of(
        "GROCERY", "DINING", "GAS", "DRUGSTORE", "TRANSIT", "TRAVEL", "ONLINE"
    );

    // Category translations
    private static final Map<String, Map<String, String>> CATEGORY_NAMES = Map.of(
        "grocery", Map.of("en", "groceries", "zh", "超市", "fr", "épicerie", "ja", "スーパー", "ko", "마트", "es", "supermercado"),
        "dining", Map.of("en", "dining", "zh", "餐厅", "fr", "restaurant", "ja", "レストラン", "ko", "식당", "es", "restaurante"),
        "gas", Map.of("en", "gas", "zh", "加油", "fr", "essence", "ja", "ガソリン", "ko", "주유", "es", "gasolina"),
        "drugstore", Map.of("en", "pharmacy", "zh", "药店", "fr", "pharmacie", "ja", "薬局", "ko", "약국", "es", "farmacia"),
        "transit", Map.of("en", "transit", "zh", "交通", "fr", "transport", "ja", "交通", "ko", "교통", "es", "transporte"),
        "travel", Map.of("en", "travel", "zh", "旅行", "fr", "voyage", "ja", "旅行", "ko", "여행", "es", "viaje"),
        "online", Map.of("en", "online shopping", "zh", "网购", "fr", "achats en ligne", "ja", "ネット通販", "ko", "온라인쇼핑", "es", "compras online")
    );

    /**
     * Message type enum for variety
     */
    private enum MessageType {
        HIGH_REWARD_CATEGORY,    // Type A: Specific category with high reward
        CASHBACK_CHECK,          // Type B: Remind to check cashback balance
        POINTS_CHECK,            // Type C: Remind to check points
        CONTEXTUAL,              // Type D: Time-based contextual reminder
        BEST_CARD_SUGGESTION,    // Suggest best card for common spending
        MONTHLY_CAP_RESET        // Type E: Monthly reward cap has reset
    }

    /**
     * Get user's preferred locale
     */
    private String getUserLocale(Long userId) {
        List<UserDevice> devices = userDeviceMapper.findActiveByUserId(userId);
        if (devices.isEmpty()) return "en";
        String locale = devices.get(0).getLocale();
        return locale != null ? locale : "en";
    }

    /**
     * Get localized category name
     */
    private String getLocalizedCategory(String category, String locale) {
        Map<String, String> names = CATEGORY_NAMES.get(category.toLowerCase());
        if (names == null) return category;
        return names.getOrDefault(locale, names.get("en"));
    }

    /**
     * Format reward rate for display
     */
    private String formatRewardRate(UserCardRewardInfo info) {
        if (info.getRewardRate() == null) return "";
        int rate = info.getRewardRate().multiply(BigDecimal.valueOf(100)).intValue();
        return rate + (info.isCashbackCard() ? "%" : "x");
    }

    /**
     * Check if user received notification recently (within last 2 days)
     */
    private boolean hasRecentNotification(Long userId) {
        LocalDateTime twoDaysAgo = LocalDateTime.now().minusDays(2);
        int count = pushNotificationMapper.countRecentByUserId(userId, twoDaysAgo);
        return count > 0;
    }

    /**
     * Get recent message types for diversity tracking
     */
    private Set<String> getRecentMessageTypes(Long userId) {
        LocalDateTime oneWeekAgo = LocalDateTime.now().minusDays(7);
        List<String> types = pushNotificationMapper.findRecentMessageTypes(userId, oneWeekAgo, 3);
        return new HashSet<>(types);
    }

    /**
     * Select appropriate message type based on user's cards, context, and diversity
     */
    private MessageType selectMessageType(Long userId, List<UserCardRewardInfo> cardRewards, String locale) {
        boolean hasCashbackCards = cardRewards.stream().anyMatch(UserCardRewardInfo::isCashbackCard);
        boolean hasPointsCards = cardRewards.stream().anyMatch(UserCardRewardInfo::isPointsCard);
        boolean hasHighRewardCategories = cardRewards.stream()
            .anyMatch(r -> r.getRewardRate() != null && r.getRewardRate().compareTo(BigDecimal.valueOf(0.02)) > 0);
        boolean hasCardsWithCap = cardRewards.stream()
            .anyMatch(r -> r.getMonthlyCap() != null && r.getMonthlyCap().compareTo(BigDecimal.ZERO) > 0);

        DayOfWeek today = LocalDate.now().getDayOfWeek();
        int dayOfMonth = LocalDate.now().getDayOfMonth();

        // Get recent message types for diversity
        Set<String> recentTypes = getRecentMessageTypes(userId);

        List<MessageType> candidates = new ArrayList<>();

        // Month start - reward cap reset (days 1-3)
        if (dayOfMonth <= 3 && hasCardsWithCap && !recentTypes.contains("MONTHLY_CAP_RESET")) {
            candidates.add(MessageType.MONTHLY_CAP_RESET);
            candidates.add(MessageType.MONTHLY_CAP_RESET); // Higher weight at month start
        }

        // Always consider high reward category if available
        if (hasHighRewardCategories && !recentTypes.contains("HIGH_REWARD_CATEGORY")) {
            candidates.add(MessageType.HIGH_REWARD_CATEGORY);
            candidates.add(MessageType.HIGH_REWARD_CATEGORY); // Higher weight
        }

        // Cashback check - more relevant near month end
        if (hasCashbackCards && !recentTypes.contains("CASHBACK_CHECK")) {
            candidates.add(MessageType.CASHBACK_CHECK);
            if (dayOfMonth >= 25) {
                candidates.add(MessageType.CASHBACK_CHECK); // Higher weight near month end
            }
        }

        // Points check
        if (hasPointsCards && !recentTypes.contains("POINTS_CHECK")) {
            candidates.add(MessageType.POINTS_CHECK);
        }

        // Contextual - weekends
        if ((today == DayOfWeek.SATURDAY || today == DayOfWeek.SUNDAY) && !recentTypes.contains("CONTEXTUAL")) {
            candidates.add(MessageType.CONTEXTUAL);
            candidates.add(MessageType.CONTEXTUAL);
        }

        // Best card suggestion - always a good fallback
        if (!recentTypes.contains("BEST_CARD_SUGGESTION")) {
            candidates.add(MessageType.BEST_CARD_SUGGESTION);
        }

        // If all types were recently used, reset and allow any type
        if (candidates.isEmpty()) {
            if (hasHighRewardCategories) candidates.add(MessageType.HIGH_REWARD_CATEGORY);
            if (hasCashbackCards) candidates.add(MessageType.CASHBACK_CHECK);
            if (hasPointsCards) candidates.add(MessageType.POINTS_CHECK);
            candidates.add(MessageType.BEST_CARD_SUGGESTION);
        }

        // Random selection
        return candidates.get(ThreadLocalRandom.current().nextInt(candidates.size()));
    }

    /**
     * Build message based on type and user's card data
     */
    private Map<String, String> buildSmartMessage(Long userId, String locale, List<UserCardRewardInfo> cardRewards, MessageType type) {
        switch (type) {
            case HIGH_REWARD_CATEGORY:
                return buildHighRewardCategoryMessage(locale, cardRewards);
            case CASHBACK_CHECK:
                return buildCashbackCheckMessage(locale, cardRewards);
            case POINTS_CHECK:
                return buildPointsCheckMessage(locale, cardRewards);
            case CONTEXTUAL:
                return buildContextualMessage(userId, locale, cardRewards);
            case BEST_CARD_SUGGESTION:
                return buildBestCardSuggestionMessage(userId, locale);
            case MONTHLY_CAP_RESET:
                return buildMonthlyCapResetMessage(locale, cardRewards);
            default:
                return buildHighRewardCategoryMessage(locale, cardRewards);
        }
    }

    /**
     * Type A: High reward category message
     */
    private Map<String, String> buildHighRewardCategoryMessage(String locale, List<UserCardRewardInfo> cardRewards) {
        // Find highest reward rate card/category combo
        Optional<UserCardRewardInfo> bestReward = cardRewards.stream()
            .filter(r -> r.getRewardRate() != null && r.getCategory() != null)
            .max(Comparator.comparing(UserCardRewardInfo::getRewardRate));

        if (bestReward.isEmpty()) {
            return buildGenericMessage(locale);
        }

        UserCardRewardInfo reward = bestReward.get();
        String cardName = reward.getCardName();
        String category = getLocalizedCategory(reward.getCategory(), locale);
        String rate = formatRewardRate(reward);

        String title, body;
        switch (locale) {
            case "zh":
                title = "💳 今天消费用这张";
                body = String.format("您的 %s 在%s消费可获得 %s 返还！今天消费别忘了带上", cardName, category, rate);
                break;
            case "fr":
                title = "💳 Utilisez cette carte";
                body = String.format("Votre %s offre %s sur %s! N'oubliez pas de l'utiliser", cardName, rate, category);
                break;
            case "ja":
                title = "💳 今日はこのカードで";
                body = String.format("%sで%sを使うと%s還元！お忘れなく", category, cardName, rate);
                break;
            case "ko":
                title = "💳 오늘은 이 카드로";
                body = String.format("%s에서 %s 사용 시 %s 적립! 잊지 마세요", category, cardName, rate);
                break;
            case "es":
                title = "💳 Usa esta tarjeta hoy";
                body = String.format("Tu %s ofrece %s en %s! No olvides usarla", cardName, rate, category);
                break;
            default:
                title = "💳 Use this card today";
                body = String.format("Your %s earns %s on %s! Don't forget to use it", cardName, rate, category);
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Type B: Cashback check reminder
     */
    private Map<String, String> buildCashbackCheckMessage(String locale, List<UserCardRewardInfo> cardRewards) {
        Optional<UserCardRewardInfo> cashbackCard = cardRewards.stream()
            .filter(UserCardRewardInfo::isCashbackCard)
            .findFirst();

        String cardName = cashbackCard.map(UserCardRewardInfo::getCardName).orElse("");

        String title, body;
        int dayOfMonth = LocalDate.now().getDayOfMonth();
        boolean isMonthEnd = dayOfMonth >= 25;

        switch (locale) {
            case "zh":
                title = isMonthEnd ? "📊 月底返现查看" : "💰 返现余额查询";
                if (!cardName.isEmpty()) {
                    body = isMonthEnd
                        ? String.format("月底了！看看您的 %s 这个月累积了多少返现", cardName)
                        : String.format("您的 %s 可能已累积不少返现，记得去银行App查看", cardName);
                } else {
                    body = "记得去银行App查看您的信用卡返现余额！";
                }
                break;
            case "fr":
                title = isMonthEnd ? "📊 Bilan mensuel" : "💰 Solde cashback";
                body = !cardName.isEmpty()
                    ? String.format("N'oubliez pas de vérifier le cashback de votre %s dans l'app bancaire!", cardName)
                    : "Pensez à vérifier votre solde cashback dans l'app bancaire!";
                break;
            case "ja":
                title = isMonthEnd ? "📊 月末キャッシュバック確認" : "💰 キャッシュバック残高";
                body = !cardName.isEmpty()
                    ? String.format("%sのキャッシュバック、銀行アプリで確認を！", cardName)
                    : "銀行アプリでキャッシュバック残高を確認しましょう！";
                break;
            case "ko":
                title = isMonthEnd ? "📊 월말 캐시백 확인" : "💰 캐시백 알림";
                body = !cardName.isEmpty()
                    ? String.format("%s 캐시백, 은행 앱에서 확인하세요!", cardName)
                    : "은행 앱에서 캐시백 잔액을 확인하세요!";
                break;
            case "es":
                title = isMonthEnd ? "📊 Resumen mensual" : "💰 Recordatorio de cashback";
                body = !cardName.isEmpty()
                    ? String.format("Recuerda revisar el cashback de tu %s en la app del banco", cardName)
                    : "¡Revisa tu saldo de cashback en la app del banco!";
                break;
            default:
                title = isMonthEnd ? "📊 Month-end cashback check" : "💰 Cashback reminder";
                body = !cardName.isEmpty()
                    ? String.format("Remember to check your %s cashback in your bank app!", cardName)
                    : "Check your credit card cashback balance in your bank app!";
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Type C: Points check reminder
     */
    private Map<String, String> buildPointsCheckMessage(String locale, List<UserCardRewardInfo> cardRewards) {
        Optional<UserCardRewardInfo> pointsCard = cardRewards.stream()
            .filter(UserCardRewardInfo::isPointsCard)
            .findFirst();

        String cardName = pointsCard.map(UserCardRewardInfo::getCardName).orElse("");
        String bank = pointsCard.map(UserCardRewardInfo::getBank).orElse("");

        // Determine points program name
        String pointsProgram = "";
        if (cardName.contains("Aeroplan")) pointsProgram = "Aeroplan";
        else if (cardName.contains("Avion")) pointsProgram = "Avion";
        else if (cardName.contains("Scene")) pointsProgram = "Scene+";
        else if (cardName.contains("Cobalt") || cardName.contains("Gold Rewards")) pointsProgram = "MR";
        else if (cardName.contains("Air Miles")) pointsProgram = "Air Miles";
        else if (cardName.contains("PC ") || cardName.contains("Optimum")) pointsProgram = "PC Optimum";

        String title, body;
        switch (locale) {
            case "zh":
                title = "✨ 积分余额查询";
                if (!pointsProgram.isEmpty()) {
                    body = String.format("记得查看您的 %s 积分余额，看看能兑换什么好东西！", pointsProgram);
                } else if (!cardName.isEmpty()) {
                    body = String.format("您的 %s 积分可能已经累积不少了，记得去银行App查看", cardName);
                } else {
                    body = "查看您的信用卡积分余额，发现兑换好礼！";
                }
                break;
            case "fr":
                title = "✨ Vérifiez vos points";
                body = !pointsProgram.isEmpty()
                    ? String.format("N'oubliez pas de vérifier votre solde %s dans l'app bancaire!", pointsProgram)
                    : "Pensez à vérifier vos points dans l'app bancaire!";
                break;
            case "ja":
                title = "✨ ポイント残高確認";
                body = !pointsProgram.isEmpty()
                    ? String.format("%sポイントの残高、銀行アプリで確認を！", pointsProgram)
                    : "銀行アプリでポイント残高を確認しましょう！";
                break;
            case "ko":
                title = "✨ 포인트 잔액 알림";
                body = !pointsProgram.isEmpty()
                    ? String.format("%s 포인트 잔액, 은행 앱에서 확인하세요!", pointsProgram)
                    : "은행 앱에서 포인트 잔액을 확인하세요!";
                break;
            case "es":
                title = "✨ Revisa tus puntos";
                body = !pointsProgram.isEmpty()
                    ? String.format("¡Recuerda revisar tu saldo de %s en la app del banco!", pointsProgram)
                    : "¡Recuerda revisar tus puntos en la app del banco!";
                break;
            default:
                title = "✨ Check your points";
                body = !pointsProgram.isEmpty()
                    ? String.format("Remember to check your %s points balance in your bank app!", pointsProgram)
                    : "Remember to check your points balance in your bank app!";
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Type D: Contextual message based on time/day
     */
    private Map<String, String> buildContextualMessage(Long userId, String locale, List<UserCardRewardInfo> cardRewards) {
        DayOfWeek today = LocalDate.now().getDayOfWeek();
        boolean isWeekend = today == DayOfWeek.SATURDAY || today == DayOfWeek.SUNDAY;

        // For weekends, suggest grocery or dining cards
        String targetCategory = isWeekend ? "GROCERY" : "DINING";
        UserCardRewardInfo bestCard = userCardMapper.selectBestCardForCategory(userId, targetCategory);

        if (bestCard == null) {
            // Fallback to highest reward card
            bestCard = cardRewards.stream()
                .filter(r -> r.getRewardRate() != null)
                .max(Comparator.comparing(UserCardRewardInfo::getRewardRate))
                .orElse(null);
        }

        String title, body;
        String category = getLocalizedCategory(targetCategory, locale);

        switch (locale) {
            case "zh":
                if (isWeekend) {
                    title = "🛒 周末购物提醒";
                    body = bestCard != null
                        ? String.format("周末去%s？用 %s 可获得 %s 返还！", category, bestCard.getCardName(), formatRewardRate(bestCard))
                        : "周末购物前，查看哪张卡最划算！";
                } else {
                    title = "🍽️ 用餐提醒";
                    body = bestCard != null
                        ? String.format("今天外出用餐？%s 在%s可获得 %s！", bestCard.getCardName(), category, formatRewardRate(bestCard))
                        : "外出用餐前，看看用哪张卡最划算！";
                }
                break;
            case "fr":
                title = isWeekend ? "🛒 Rappel weekend" : "🍽️ Rappel resto";
                body = bestCard != null
                    ? String.format("Utilisez %s pour %s sur %s!", bestCard.getCardName(), formatRewardRate(bestCard), category)
                    : "Consultez la meilleure carte avant de dépenser!";
                break;
            case "ja":
                title = isWeekend ? "🛒 週末のお買い物" : "🍽️ お食事リマインダー";
                body = bestCard != null
                    ? String.format("%sで%sを使えば%s還元！", category, bestCard.getCardName(), formatRewardRate(bestCard))
                    : "お出かけ前に最適なカードをチェック！";
                break;
            case "ko":
                title = isWeekend ? "🛒 주말 쇼핑 알림" : "🍽️ 식사 알림";
                body = bestCard != null
                    ? String.format("%s에서 %s 사용 시 %s 적립!", category, bestCard.getCardName(), formatRewardRate(bestCard))
                    : "외출 전 최적의 카드를 확인하세요!";
                break;
            case "es":
                title = isWeekend ? "🛒 Recordatorio de fin de semana" : "🍽️ Recordatorio de comida";
                body = bestCard != null
                    ? String.format("¡Usa %s para %s en %s!", bestCard.getCardName(), formatRewardRate(bestCard), category)
                    : "¡Consulta la mejor tarjeta antes de gastar!";
                break;
            default:
                title = isWeekend ? "🛒 Weekend shopping" : "🍽️ Dining reminder";
                body = bestCard != null
                    ? String.format("Use %s for %s on %s!", bestCard.getCardName(), formatRewardRate(bestCard), category)
                    : "Check which card gives the best rewards before spending!";
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Best card suggestion for random common category
     */
    private Map<String, String> buildBestCardSuggestionMessage(Long userId, String locale) {
        // Pick a random common category
        String category = COMMON_CATEGORIES.get(ThreadLocalRandom.current().nextInt(COMMON_CATEGORIES.size()));
        UserCardRewardInfo bestCard = userCardMapper.selectBestCardForCategory(userId, category);

        if (bestCard == null) {
            return buildGenericMessage(locale);
        }

        String localizedCategory = getLocalizedCategory(category, locale);
        String rate = formatRewardRate(bestCard);

        String title, body;
        switch (locale) {
            case "zh":
                title = "💡 用卡小贴士";
                body = String.format("您在%s消费的最佳选择是 %s，可获得 %s 返还", localizedCategory, bestCard.getCardName(), rate);
                break;
            case "fr":
                title = "💡 Conseil carte";
                body = String.format("Pour %s, utilisez %s pour %s de remise", localizedCategory, bestCard.getCardName(), rate);
                break;
            case "ja":
                title = "💡 カード活用ヒント";
                body = String.format("%sには%sがベスト！%s還元", localizedCategory, bestCard.getCardName(), rate);
                break;
            case "ko":
                title = "💡 카드 활용 팁";
                body = String.format("%s에는 %s가 최고! %s 적립", localizedCategory, bestCard.getCardName(), rate);
                break;
            case "es":
                title = "💡 Tip de tarjeta";
                body = String.format("Para %s, usa %s para %s de recompensa", localizedCategory, bestCard.getCardName(), rate);
                break;
            default:
                title = "💡 Card tip";
                body = String.format("For %s, your best card is %s with %s rewards", localizedCategory, bestCard.getCardName(), rate);
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Type E: Monthly cap reset message (for month start)
     */
    private Map<String, String> buildMonthlyCapResetMessage(String locale, List<UserCardRewardInfo> cardRewards) {
        // Find cards with monthly caps
        Optional<UserCardRewardInfo> cardWithCap = cardRewards.stream()
            .filter(r -> r.getMonthlyCap() != null && r.getMonthlyCap().compareTo(BigDecimal.ZERO) > 0)
            .findFirst();

        String cardName = cardWithCap.map(UserCardRewardInfo::getCardName).orElse("");

        String title, body;
        switch (locale) {
            case "zh":
                title = "🔄 新月新开始";
                if (!cardName.isEmpty()) {
                    body = String.format("您的 %s 返现上限已重置！新的一个月，别忘了多用这张卡", cardName);
                } else {
                    body = "新的一个月开始了，您的信用卡返现上限已重置，尽情消费吧！";
                }
                break;
            case "fr":
                title = "🔄 Nouveau mois, nouveau départ";
                body = !cardName.isEmpty()
                    ? String.format("Le plafond de remise de votre %s a été réinitialisé!", cardName)
                    : "Votre plafond de cashback mensuel a été réinitialisé!";
                break;
            case "ja":
                title = "🔄 新しい月の始まり";
                body = !cardName.isEmpty()
                    ? String.format("%sの還元上限がリセットされました！今月もお得に使いましょう", cardName)
                    : "毎月の還元上限がリセットされました！";
                break;
            case "ko":
                title = "🔄 새 달이 시작되었습니다";
                body = !cardName.isEmpty()
                    ? String.format("%s의 캐시백 한도가 초기화되었습니다!", cardName)
                    : "월별 캐시백 한도가 초기화되었습니다!";
                break;
            case "es":
                title = "🔄 Nuevo mes, nuevo comienzo";
                body = !cardName.isEmpty()
                    ? String.format("¡El límite de cashback de tu %s se ha reiniciado!", cardName)
                    : "¡Tu límite de cashback mensual se ha reiniciado!";
                break;
            default:
                title = "🔄 New month, fresh start";
                body = !cardName.isEmpty()
                    ? String.format("Your %s monthly reward cap has reset! Time to maximize your rewards", cardName)
                    : "Your monthly cashback limits have reset! Time to start earning rewards again";
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Generic fallback message
     */
    private Map<String, String> buildGenericMessage(String locale) {
        String title, body;
        switch (locale) {
            case "zh":
                title = "💳 SaveVia 提醒";
                body = "打开 SaveVia 查看最佳用卡推荐，最大化您的返现！";
                break;
            case "fr":
                title = "💳 Rappel SaveVia";
                body = "Consultez SaveVia pour les meilleures recommandations de carte!";
                break;
            case "ja":
                title = "💳 SaveVia リマインダー";
                body = "SaveViaで最適なカードをチェックして還元を最大化！";
                break;
            case "ko":
                title = "💳 SaveVia 알림";
                body = "SaveVia에서 최적의 카드 추천을 확인하세요!";
                break;
            case "es":
                title = "💳 Recordatorio SaveVia";
                body = "¡Consulta SaveVia para las mejores recomendaciones de tarjeta!";
                break;
            default:
                title = "💳 SaveVia reminder";
                body = "Check SaveVia for the best card recommendations to maximize rewards!";
        }
        return Map.of("title", title, "body", body);
    }

    /**
     * Inactive user reminder - for users who haven't used app in 14 days
     * Based on user_events table (last activity > 14 days ago)
     * Runs daily at 6:00 PM Vancouver time
     */
    @Scheduled(cron = "0 0 18 * * *", zone = "America/Vancouver")
    public void sendInactiveUserReminder() {
        log.info("Running inactive user reminder push task...");

        // Find users whose last activity was more than 14 days ago
        LocalDateTime fourteenDaysAgo = LocalDateTime.now().minusDays(14);
        List<Long> inactiveUserIds = userEventMapper.getInactiveUserIds(fourteenDaysAgo);

        log.info("Found {} inactive users (no activity in 14 days)", inactiveUserIds.size());

        for (Long userId : inactiveUserIds) {
            try {
                // Skip if user received notification in last 2 days
                if (hasRecentNotification(userId)) {
                    continue;
                }

                List<Long> cardIds = userCardMapper.selectCardIdsByUserId(userId);
                if (cardIds.isEmpty()) {
                    continue;
                }

                String locale = getUserLocale(userId);
                List<UserCardRewardInfo> cardRewards = userCardMapper.selectUserCardRewardInfo(userId);

                // Select message type and build personalized message
                MessageType messageType = selectMessageType(userId, cardRewards, locale);
                Map<String, String> message = buildSmartMessage(userId, locale, cardRewards, messageType);

                Map<String, Object> data = new HashMap<>();
                data.put("type", "inactive_reminder");
                data.put("messageType", messageType.name());

                pushNotificationService.sendPushToUser(
                    userId,
                    "inactive_reminder",
                    message.get("title"),
                    message.get("body"),
                    data
                );

                log.debug("Sent {} notification to user {}", messageType, userId);
            } catch (Exception e) {
                log.error("Failed to send inactive reminder to user {}: {}", userId, e.getMessage());
            }
        }
    }

    /**
     * Smart spending reminder - personalized based on user's cards
     * Sends to active users (had activity in last 14 days)
     * Runs every 2 days at 10:00 AM Vancouver time
     */
    @Scheduled(cron = "0 0 10 */2 * *", zone = "America/Vancouver")
    public void sendSmartSpendingReminder() {
        log.info("Running smart spending reminder push task...");

        // Find users who have been active in the last 14 days
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime fourteenDaysAgo = now.minusDays(14);
        List<Long> userIds = userEventMapper.getActiveUserIds(fourteenDaysAgo, now);

        log.info("Found {} active users (activity in last 14 days)", userIds.size());

        for (Long userId : userIds) {
            try {
                // Skip if user received notification in last 2 days
                if (hasRecentNotification(userId)) {
                    continue;
                }

                List<Long> cardIds = userCardMapper.selectCardIdsByUserId(userId);
                if (cardIds.isEmpty()) {
                    continue;
                }

                String locale = getUserLocale(userId);
                List<UserCardRewardInfo> cardRewards = userCardMapper.selectUserCardRewardInfo(userId);

                // Select message type and build personalized message
                MessageType messageType = selectMessageType(userId, cardRewards, locale);
                Map<String, String> message = buildSmartMessage(userId, locale, cardRewards, messageType);

                Map<String, Object> data = new HashMap<>();
                data.put("type", "spending_reminder");
                data.put("messageType", messageType.name());

                pushNotificationService.sendPushToUser(
                    userId,
                    "spending_reminder",
                    message.get("title"),
                    message.get("body"),
                    data
                );

                log.debug("Sent {} notification to user {}", messageType, userId);
            } catch (Exception e) {
                log.error("Failed to send spending reminder to user {}: {}", userId, e.getMessage());
            }
        }
    }

}
