package com.savevia.user.service;

import com.savevia.common.constants.MemoryConstants;
import com.savevia.user.dto.MemoryContextDTO;
import com.savevia.user.entity.UserConversationSummary;
import com.savevia.user.entity.UserProfileFact;
import com.savevia.user.mapper.UserConversationSummaryMapper;
import com.savevia.user.mapper.UserProfileFactMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class MemoryServiceImpl implements MemoryService {

    private final UserProfileFactMapper profileFactMapper;
    private final UserConversationSummaryMapper summaryMapper;

    private static final Set<String> CORE_CATEGORIES = Set.of(
            MemoryConstants.Category.IDENTITY,
            MemoryConstants.Category.PREFERENCE,
            MemoryConstants.Category.EXCLUSION
    );

    private static final Set<String> EXTENDED_CATEGORIES = Set.of(
            MemoryConstants.Category.SPENDING,
            MemoryConstants.Category.LIFESTYLE
    );

    @Override
    @Transactional
    public void saveProfileFact(Long userId, String category, String key, String value, String source) {
        UserProfileFact fact = UserProfileFact.builder()
                .userId(userId)
                .factCategory(category)
                .factKey(key)
                .factValue(value)
                .source(source != null ? source : MemoryConstants.Source.INFERRED)
                .build();
        profileFactMapper.upsert(fact);
        log.debug("Saved profile fact for user {}: {}.{} = {}", userId, category, key, value);
    }

    @Override
    public List<UserProfileFact> getProfileFacts(Long userId) {
        return profileFactMapper.selectByUserId(userId);
    }

    @Override
    public List<UserProfileFact> getProfileFactsByCategories(Long userId, Set<String> categories) {
        if (categories == null || categories.isEmpty()) {
            return getProfileFacts(userId);
        }
        return profileFactMapper.selectByUserIdAndCategories(userId, new ArrayList<>(categories));
    }

    @Override
    @Transactional
    public void deleteProfileFact(Long userId, String category, String key) {
        profileFactMapper.deleteByUserIdAndCategoryAndKey(userId, category, key);
        log.debug("Deleted profile fact for user {}: {}.{}", userId, category, key);
    }

    @Override
    @Transactional
    public void saveSummary(Long userId, String summary, String keyTopics,
                           String recommendations, String sourceConversationIds) {
        UserConversationSummary summaryEntity = UserConversationSummary.builder()
                .userId(userId)
                .summary(summary)
                .keyTopics(keyTopics)
                .recommendations(recommendations)
                .sourceConversationIds(sourceConversationIds)
                .build();
        summaryMapper.insert(summaryEntity);
        log.debug("Saved conversation summary for user {}", userId);
    }

    @Override
    public List<UserConversationSummary> getRecentSummaries(Long userId, int limit) {
        return summaryMapper.selectRecentByUserId(userId, limit);
    }

    @Override
    public MemoryContextDTO getUserMemoryContext(Long userId, Set<String> requestedCategories) {
        // Determine which categories to fetch
        Set<String> categoriesToFetch = new HashSet<>(CORE_CATEGORIES);
        if (requestedCategories != null) {
            categoriesToFetch.addAll(requestedCategories);
        }

        // Fetch facts
        List<UserProfileFact> facts = profileFactMapper.selectByUserIdAndCategories(
                userId, new ArrayList<>(categoriesToFetch));

        // Fetch recent summaries
        List<UserConversationSummary> summaries = summaryMapper.selectRecentByUserId(userId, 2);

        // Build structured facts map
        Map<String, Map<String, String>> structuredFacts = facts.stream()
                .collect(Collectors.groupingBy(
                        UserProfileFact::getFactCategory,
                        Collectors.toMap(
                                UserProfileFact::getFactKey,
                                UserProfileFact::getFactValue,
                                (v1, v2) -> v2  // Keep latest on conflict
                        )
                ));

        // Build core memory text
        String coreMemory = buildCoreMemoryText(structuredFacts);

        // Build extended memory text
        String extendedMemory = buildExtendedMemoryText(structuredFacts, requestedCategories);

        // Build summaries list
        List<String> summaryTexts = summaries.stream()
                .map(UserConversationSummary::getSummary)
                .collect(Collectors.toList());

        boolean hasMemory = !facts.isEmpty() || !summaries.isEmpty();

        return MemoryContextDTO.builder()
                .coreMemory(coreMemory)
                .extendedMemory(extendedMemory)
                .recentSummaries(summaryTexts)
                .structuredFacts(structuredFacts)
                .hasMemory(hasMemory)
                .build();
    }

    @Override
    @Transactional
    public void clearUserMemory(Long userId) {
        profileFactMapper.deleteByUserId(userId);
        summaryMapper.deleteByUserId(userId);
        log.info("Cleared all memory for user {}", userId);
    }

    /**
     * Build core memory text from identity, preference, and exclusion facts.
     */
    private String buildCoreMemoryText(Map<String, Map<String, String>> structuredFacts) {
        StringBuilder sb = new StringBuilder();

        // Identity section
        Map<String, String> identity = structuredFacts.get(MemoryConstants.Category.IDENTITY);
        if (identity != null && !identity.isEmpty()) {
            sb.append("[Identity]\n");
            appendIdentityText(sb, identity);
        }

        // Preference section
        Map<String, String> preference = structuredFacts.get(MemoryConstants.Category.PREFERENCE);
        if (preference != null && !preference.isEmpty()) {
            sb.append("[Preferences]\n");
            appendPreferenceText(sb, preference);
        }

        // Exclusion section
        Map<String, String> exclusion = structuredFacts.get(MemoryConstants.Category.EXCLUSION);
        if (exclusion != null && !exclusion.isEmpty()) {
            sb.append("[Exclusions]\n");
            appendExclusionText(sb, exclusion);
        }

        return sb.toString().trim();
    }

    /**
     * Build extended memory text from spending and lifestyle facts.
     */
    private String buildExtendedMemoryText(Map<String, Map<String, String>> structuredFacts,
                                           Set<String> requestedCategories) {
        StringBuilder sb = new StringBuilder();

        // Only include if specifically requested
        if (requestedCategories == null) {
            return "";
        }

        // Spending section
        if (requestedCategories.contains(MemoryConstants.Category.SPENDING)) {
            Map<String, String> spending = structuredFacts.get(MemoryConstants.Category.SPENDING);
            if (spending != null && !spending.isEmpty()) {
                sb.append("[Spending Patterns]\n");
                appendSpendingText(sb, spending);
            }
        }

        // Lifestyle section
        if (requestedCategories.contains(MemoryConstants.Category.LIFESTYLE)) {
            Map<String, String> lifestyle = structuredFacts.get(MemoryConstants.Category.LIFESTYLE);
            if (lifestyle != null && !lifestyle.isEmpty()) {
                sb.append("[Lifestyle]\n");
                appendLifestyleText(sb, lifestyle);
            }
        }

        return sb.toString().trim();
    }

    private void appendIdentityText(StringBuilder sb, Map<String, String> identity) {
        String userType = identity.get(MemoryConstants.IdentityKey.USER_TYPE);
        String years = identity.get(MemoryConstants.IdentityKey.RESIDENCY_YEARS);
        String occupation = identity.get(MemoryConstants.IdentityKey.OCCUPATION);
        String income = identity.get(MemoryConstants.IdentityKey.INCOME_RANGE);

        if (userType != null) {
            sb.append("- User type: ").append(formatUserType(userType));
            if (years != null) {
                sb.append(" (").append(years).append(" years in Canada)");
            }
            sb.append("\n");
        }
        if (occupation != null) {
            sb.append("- Occupation: ").append(occupation).append("\n");
        }
        if (income != null) {
            sb.append("- Income range: ").append(formatIncomeRange(income)).append("\n");
        }
    }

    private void appendPreferenceText(StringBuilder sb, Map<String, String> preference) {
        String feeTolerance = preference.get(MemoryConstants.PreferenceKey.ANNUAL_FEE_TOLERANCE);
        String rewardType = preference.get(MemoryConstants.PreferenceKey.REWARD_TYPE);
        String banks = preference.get(MemoryConstants.PreferenceKey.PREFERRED_BANKS);
        String networks = preference.get(MemoryConstants.PreferenceKey.PREFERRED_NETWORKS);

        if (feeTolerance != null) {
            sb.append("- Annual fee tolerance: $").append(feeTolerance).append("\n");
        }
        if (rewardType != null) {
            sb.append("- Preferred reward type: ").append(rewardType).append("\n");
        }
        if (banks != null) {
            sb.append("- Preferred banks: ").append(banks).append("\n");
        }
        if (networks != null) {
            sb.append("- Preferred networks: ").append(networks).append("\n");
        }
    }

    private void appendExclusionText(StringBuilder sb, Map<String, String> exclusion) {
        String banks = exclusion.get(MemoryConstants.ExclusionKey.EXCLUDED_BANKS);
        String networks = exclusion.get(MemoryConstants.ExclusionKey.EXCLUDED_NETWORKS);
        String cards = exclusion.get(MemoryConstants.ExclusionKey.EXCLUDED_CARDS);

        if (banks != null) {
            sb.append("- Excluded banks: ").append(banks).append("\n");
        }
        if (networks != null) {
            sb.append("- Excluded networks: ").append(networks).append("\n");
        }
        if (cards != null) {
            sb.append("- Excluded cards: ").append(cards).append("\n");
        }
    }

    private void appendSpendingText(StringBuilder sb, Map<String, String> spending) {
        Map<String, String> labels = Map.of(
                MemoryConstants.SpendingKey.MONTHLY_GROCERY, "Grocery",
                MemoryConstants.SpendingKey.MONTHLY_GAS, "Gas",
                MemoryConstants.SpendingKey.MONTHLY_DINING, "Dining",
                MemoryConstants.SpendingKey.MONTHLY_ONLINE, "Online shopping",
                MemoryConstants.SpendingKey.MONTHLY_TRAVEL, "Travel",
                MemoryConstants.SpendingKey.MONTHLY_TOTAL, "Total"
        );

        for (Map.Entry<String, String> entry : spending.entrySet()) {
            String label = labels.getOrDefault(entry.getKey(), entry.getKey());
            sb.append("- ").append(label).append(": ~$").append(entry.getValue()).append("/month\n");
        }
    }

    private void appendLifestyleText(StringBuilder sb, Map<String, String> lifestyle) {
        String travel = lifestyle.get(MemoryConstants.LifestyleKey.TRAVEL_FREQUENCY);
        String children = lifestyle.get(MemoryConstants.LifestyleKey.HAS_CHILDREN);
        String pets = lifestyle.get(MemoryConstants.LifestyleKey.HAS_PETS);
        String commute = lifestyle.get(MemoryConstants.LifestyleKey.COMMUTE_METHOD);

        if (travel != null) {
            sb.append("- Travel frequency: ").append(travel).append("\n");
        }
        if (commute != null) {
            sb.append("- Commute: ").append(commute).append("\n");
        }
        if ("true".equals(children)) {
            sb.append("- Has children\n");
        }
        if ("true".equals(pets)) {
            sb.append("- Has pets\n");
        }
    }

    private String formatUserType(String userType) {
        return switch (userType) {
            case "new_immigrant" -> "New immigrant";
            case "pr_holder" -> "Permanent resident";
            case "work_permit" -> "Work permit holder";
            case "student" -> "International student";
            case "citizen" -> "Canadian citizen";
            case "visitor" -> "Visitor";
            default -> userType;
        };
    }

    private String formatIncomeRange(String income) {
        return switch (income) {
            case "under_30k" -> "Under $30,000";
            case "30k_60k" -> "$30,000 - $60,000";
            case "60k_100k" -> "$60,000 - $100,000";
            case "100k_plus" -> "Over $100,000";
            default -> income;
        };
    }
}
