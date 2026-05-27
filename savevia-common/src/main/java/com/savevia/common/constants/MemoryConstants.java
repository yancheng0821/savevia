package com.savevia.common.constants;

/**
 * Constants for user memory system.
 */
public final class MemoryConstants {

    private MemoryConstants() {}

    /**
     * Memory fact categories
     */
    public static final class Category {
        public static final String IDENTITY = "identity";
        public static final String SPENDING = "spending";
        public static final String PREFERENCE = "preference";
        public static final String EXCLUSION = "exclusion";
        public static final String LIFESTYLE = "lifestyle";

        private Category() {}
    }

    /**
     * Identity fact keys
     */
    public static final class IdentityKey {
        public static final String USER_TYPE = "user_type";
        public static final String RESIDENCY_YEARS = "residency_years";
        public static final String OCCUPATION = "occupation";
        public static final String INCOME_RANGE = "income_range";

        private IdentityKey() {}
    }

    /**
     * Spending fact keys
     */
    public static final class SpendingKey {
        public static final String MONTHLY_GROCERY = "monthly_grocery";
        public static final String MONTHLY_GAS = "monthly_gas";
        public static final String MONTHLY_DINING = "monthly_dining";
        public static final String MONTHLY_ONLINE = "monthly_online";
        public static final String MONTHLY_TRAVEL = "monthly_travel";
        public static final String MONTHLY_TOTAL = "monthly_total";

        private SpendingKey() {}
    }

    /**
     * Preference fact keys
     */
    public static final class PreferenceKey {
        public static final String ANNUAL_FEE_TOLERANCE = "annual_fee_tolerance";
        public static final String REWARD_TYPE = "reward_type";
        public static final String PREFERRED_BANKS = "preferred_banks";
        public static final String PREFERRED_NETWORKS = "preferred_networks";

        private PreferenceKey() {}
    }

    /**
     * Exclusion fact keys
     */
    public static final class ExclusionKey {
        public static final String EXCLUDED_BANKS = "excluded_banks";
        public static final String EXCLUDED_NETWORKS = "excluded_networks";
        public static final String EXCLUDED_CARDS = "excluded_cards";

        private ExclusionKey() {}
    }

    /**
     * Lifestyle fact keys
     */
    public static final class LifestyleKey {
        public static final String TRAVEL_FREQUENCY = "travel_frequency";
        public static final String HAS_CHILDREN = "has_children";
        public static final String HAS_PETS = "has_pets";
        public static final String COMMUTE_METHOD = "commute_method";

        private LifestyleKey() {}
    }

    /**
     * Fact source types
     */
    public static final class Source {
        public static final String EXPLICIT = "explicit";
        public static final String INFERRED = "inferred";

        private Source() {}
    }

    /**
     * Extraction log status
     */
    public static final class ExtractionStatus {
        public static final String PENDING = "pending";
        public static final String SUCCESS = "success";
        public static final String FAILED = "failed";

        private ExtractionStatus() {}
    }

    /**
     * User type values
     */
    public static final class UserType {
        public static final String STUDENT = "student";
        public static final String NEW_IMMIGRANT = "new_immigrant";
        public static final String PR_HOLDER = "pr_holder";
        public static final String CITIZEN = "citizen";
        public static final String WORK_PERMIT = "work_permit";
        public static final String VISITOR = "visitor";

        private UserType() {}
    }

    /**
     * Reward type values
     */
    public static final class RewardType {
        public static final String CASHBACK = "cashback";
        public static final String POINTS = "points";
        public static final String TRAVEL_MILES = "travel_miles";

        private RewardType() {}
    }
}
