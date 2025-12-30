"""
Credit Card Collector Agent - Uses Agno framework to scrape credit card info from bank websites.

Supports multiple LLM providers: OpenAI, Claude, Gemini, Groq, DeepSeek, Ollama.
"""

import os
from decimal import Decimal
from enum import Enum
from textwrap import dedent
from typing import Optional, Literal

from pydantic import BaseModel, Field

from src.models import CreditCard, SignupBonus, RewardRule
from src.services.database import Database


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    VOLCES = "volces"  # 火山引擎（默认）
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"


# Default model IDs for each provider
DEFAULT_MODELS = {
    LLMProvider.VOLCES: os.environ.get("DEFAULT_LLM_MODEL", "deepseek-v3-1-250821"),
    LLMProvider.OPENAI: "gpt-4o-mini",
    LLMProvider.CLAUDE: "claude-sonnet-4-20250514",
    LLMProvider.GEMINI: "gemini-2.0-flash-001",
    LLMProvider.GROQ: "llama-3.3-70b-versatile",
    LLMProvider.DEEPSEEK: "deepseek-chat",
    LLMProvider.OLLAMA: "llama3.2:latest",
}

# 默认提供商
DEFAULT_PROVIDER = LLMProvider(os.environ.get("DEFAULT_LLM_PROVIDER", "volces"))


# Pydantic schema for structured output from LLM
class DiscoveredCard(BaseModel):
    """Discovered credit card from listing page"""
    name: str = Field(..., description="Credit card name")
    url: str = Field(..., description="Full URL to the card's product page")


class DiscoveredCardList(BaseModel):
    """List of discovered credit cards"""
    cards: list[DiscoveredCard] = Field(
        default_factory=list,
        description="List of discovered credit cards with their URLs"
    )


class ExtractedRewardRule(BaseModel):
    """Extracted reward rule from web content"""
    category: str = Field(
        ...,
        description="Spending category. Must be one of: DINING, GROCERY, GAS, TRAVEL, TRANSIT, STREAMING, ENTERTAINMENT, PERSONAL_SERVICES, RETAIL, HOME_IMPROVEMENT, RECURRING, PHARMACY, FOREIGN, ONLINE_SHOPPING, EV_CHARGING, TELECOM, INSURANCE, RENT, WHOLESALE, OTHER",
    )
    reward_rate: float = Field(
        ...,
        description="Reward rate as decimal (e.g., 0.05 for 5%). Points multipliers should be converted: 5x = 0.05",
    )
    monthly_cap_amount: Optional[float] = Field(
        default=None,
        description="Monthly spending cap in dollars, if any",
    )
    description: str = Field(
        ...,
        description="Original description of the reward rule",
    )


class ExtractedSignupBonus(BaseModel):
    """Extracted signup bonus from web content"""
    bonus_amount: int = Field(
        default=0,
        description="Bonus amount in points or dollars",
    )
    min_spend: int = Field(
        default=0,
        description="Minimum spend required to earn bonus",
    )
    days_to_complete: int = Field(
        default=90,
        description="Days to complete the minimum spend",
    )
    description: Optional[str] = Field(
        default=None,
        description="Full description of the signup bonus",
    )


class ExtractedCreditCard(BaseModel):
    """Extracted credit card information from web content"""
    bank: str = Field(..., description="Bank or issuer name (e.g., 'AMEX', 'Chase', 'CIBC')")
    name: str = Field(..., description="Credit card name (e.g., 'Cobalt Card', 'Sapphire Preferred')")
    card_type: str = Field(
        default="VISA",
        description="Card network: VISA, MASTERCARD, or AMEX",
    )
    annual_fee: float = Field(
        default=0.0,
        description="Annual fee in dollars",
    )
    base_reward_rate: float = Field(
        default=0.01,
        description="Base reward rate as decimal (e.g., 0.01 for 1%)",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL to the credit card image/artwork (the card face picture, usually a PNG or JPG)",
    )
    apply_url: Optional[str] = Field(
        default=None,
        description="URL to apply for the card",
    )
    no_fx_fee: bool = Field(
        default=False,
        description="Whether the card has no foreign transaction fee",
    )
    signup_bonus: Optional[ExtractedSignupBonus] = Field(
        default=None,
        description="Signup bonus information",
    )
    reward_rules: list[ExtractedRewardRule] = Field(
        default_factory=list,
        description="List of reward rules by spending category",
    )


def create_llm_model(
    provider: LLMProvider,
    model_id: Optional[str] = None,
    **kwargs
):
    """
    Create an LLM model instance based on provider.

    Args:
        provider: LLM provider (volces, openai, claude, gemini, groq, deepseek, ollama)
        model_id: Specific model ID (optional, uses default if not provided)
        **kwargs: Additional model-specific parameters

    Returns:
        Configured model instance
    """
    model_id = model_id or DEFAULT_MODELS[provider]

    if provider == LLMProvider.VOLCES:
        # 火山引擎使用 OpenAI 兼容 API
        # 注意: Agno 默认把 system 映射到 developer，但火山引擎不支持 developer role
        from agno.models.openai import OpenAIChat
        role_map = {
            "system": "system",  # 火山引擎不支持 developer，必须用 system
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant",
        }
        return OpenAIChat(
            id=model_id,
            api_key=os.environ.get("VOLCES_API_KEY"),
            base_url=os.environ.get("VOLCES_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            role_map=role_map,
            strict_output=False,  # 火山引擎不支持 strict mode
            **kwargs
        )

    elif provider == LLMProvider.OPENAI:
        from agno.models.openai import OpenAIChat
        return OpenAIChat(id=model_id, **kwargs)

    elif provider == LLMProvider.CLAUDE:
        from agno.models.anthropic import Claude
        return Claude(id=model_id, **kwargs)

    elif provider == LLMProvider.GEMINI:
        from agno.models.google import Gemini
        return Gemini(id=model_id, **kwargs)

    elif provider == LLMProvider.GROQ:
        from agno.models.groq import Groq
        return Groq(id=model_id, **kwargs)

    elif provider == LLMProvider.DEEPSEEK:
        from agno.models.deepseek import DeepSeek
        return DeepSeek(id=model_id, **kwargs)

    elif provider == LLMProvider.OLLAMA:
        from agno.models.ollama import Ollama
        return Ollama(id=model_id, **kwargs)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


class CardCollectorAgent:
    """
    Agent for collecting credit card information from bank websites.
    Uses Agno framework with web scraping tools and configurable LLM.

    Supports: OpenAI, Claude, Gemini, Groq, DeepSeek, Ollama
    """

    def __init__(
        self,
        provider: LLMProvider = DEFAULT_PROVIDER,
        model_id: Optional[str] = None,
        database: Optional[Database] = None,
        **model_kwargs
    ):
        """
        Initialize the card collector agent.

        Args:
            provider: LLM provider to use (default: openai)
            model_id: Specific model ID (optional)
            database: SQLite database for storage (optional, creates new if not provided)
            **model_kwargs: Additional model-specific parameters
        """
        self.provider = provider
        self.model_id = model_id
        self.model_kwargs = model_kwargs
        self.database = database or Database()
        self._agent = None
        self._search_agent = None

    @property
    def BANK_CARD_LISTINGS(self) -> dict[str, str]:
        """Get bank card listings from database (dynamic, not hardcoded)."""
        return self.database.get_bank_card_listings()

    def _create_model(self):
        """Create the LLM model instance"""
        return create_llm_model(
            provider=self.provider,
            model_id=self.model_id,
            **self.model_kwargs
        )

    def _create_agent(self):
        """Create Agno agent with web scraping tools"""
        try:
            from agno.agent import Agent
            from agno.tools.crawl4ai import Crawl4aiTools
        except ImportError:
            raise ImportError(
                "Please install agno and crawl4ai: pip install agno crawl4ai"
            )

        instructions = dedent("""
            You are a credit card information extraction expert. Your job is to extract
            detailed credit card reward information from bank websites.

            When extracting credit card information:
            1. Identify the bank/issuer name and card name
            2. Find the annual fee (if free, use 0)
            3. Identify the base reward rate (default 1% if not specified)
            4. Extract all category-specific reward rates:
               - Convert points multipliers to percentages (5x points = 5% = 0.05)
               - Note any monthly or yearly spending caps
               - Map to standard categories: DINING, GROCERY, GAS, TRAVEL, TRANSIT,
                 STREAMING, ENTERTAINMENT, PERSONAL_SERVICES, RETAIL, HOME_IMPROVEMENT,
                 RECURRING, PHARMACY, FOREIGN, ONLINE_SHOPPING, EV_CHARGING, TELECOM,
                 INSURANCE, RENT, WHOLESALE, OTHER
            5. Extract signup bonus details if available
            6. Note if there's no foreign transaction fee
            7. IMPORTANT: Find the credit card image URL (the card face picture).
               Look for <img> tags with the card artwork, usually PNG or JPG files.
               The image URL often contains words like 'card', 'image', or the card name.

            Be thorough and accurate. If information is unclear, make reasonable assumptions
            based on industry standards.
        """).strip()

        model = self._create_model()

        # 限制爬取内容长度，提高处理效率
        # 火山引擎 DeepSeek-V3-terminus 支持 128K 上下文
        # 设置合理的 max_length 避免不必要的内容，同时保留足够信息
        self._agent = Agent(
            model=model,
            tools=[Crawl4aiTools(
                max_length=20000,  # 20K 字符，避免 token 超限
                use_pruning=True,
                pruning_threshold=0.5,  # 更激进裁剪
                headless=True,
            )],
            instructions=instructions,
            output_schema=ExtractedCreditCard,
            structured_outputs=False,  # 火山引擎不支持 strict mode
            use_json_mode=True,  # 使用 JSON mode 代替
            markdown=True,
        )
        return self._agent

    def _create_search_agent(self):
        """Create Agno agent for web search"""
        try:
            from agno.agent import Agent
            from agno.tools.duckduckgo import DuckDuckGoTools
        except ImportError:
            raise ImportError(
                "Please install agno and duckduckgo-search: pip install agno duckduckgo-search"
            )

        model = self._create_model()

        self._search_agent = Agent(
            model=model,
            tools=[DuckDuckGoTools()],
            instructions="Search for credit card information and return official URLs.",
            markdown=True,
        )
        return self._search_agent

    @property
    def agent(self):
        """Get or create the scraping agent"""
        if self._agent is None:
            self._create_agent()
        return self._agent

    @property
    def search_agent(self):
        """Get or create the search agent"""
        if self._search_agent is None:
            self._create_search_agent()
        return self._search_agent

    def _extract_card_image(self, page_url: str, bank: str, card_name: str) -> Optional[str]:
        """
        Extract the credit card image URL from the page HTML.

        Uses crawl4ai to fetch the page and then extracts the first card-related image.
        """
        import re
        import asyncio
        from src.agents.custom_crawl_tool import OptimizedCrawler

        try:
            crawler = OptimizedCrawler(delay=2.0, max_length=None)
            result = asyncio.run(crawler.crawl(page_url))

            if not result['success']:
                return None

            html = result['html']

            # Find all image URLs
            all_imgs = re.findall(r'src="([^"]+\.(?:png|jpg|jpeg|webp))"', html, re.IGNORECASE)

            if not all_imgs:
                return None

            # Bank-specific image patterns
            bank_patterns = {
                'BMO': [
                    r'/dist/images/.*credit-cards/.*\.png',
                    r'/dist/images/.*credit-cards/.*\.jpg',
                ],
                'TD': [
                    r'/content/dam/.*credit-cards.*\.png',
                    r'/content/dam/.*credit-cards.*\.jpg',
                ],
                'RBC': [
                    r'/.*card.*\.png',
                    r'/.*card.*\.jpg',
                ],
                'CIBC': [
                    r'/.*card.*\.png',
                    r'/.*card.*\.jpg',
                ],
                'Scotiabank': [
                    r'/.*card.*\.png',
                    r'/.*card.*\.jpg',
                ],
            }

            # Get patterns for this bank
            patterns = bank_patterns.get(bank, [])

            # Try bank-specific patterns first
            for pattern in patterns:
                for img in all_imgs:
                    if re.search(pattern, img, re.IGNORECASE):
                        # Make URL absolute if needed
                        if img.startswith('/'):
                            from urllib.parse import urlparse
                            parsed = urlparse(page_url)
                            img = f"{parsed.scheme}://{parsed.netloc}{img}"
                        return img

            # Fallback: look for first image with card-related keywords
            card_keywords = ['card', 'credit', 'mastercard', 'visa', 'amex']
            for img in all_imgs:
                if any(kw in img.lower() for kw in card_keywords):
                    # Skip product page images, icons, logos
                    skip_keywords = ['icon', 'logo', 'banner', 'hero', 'background', 'apply-now', 'product-page']
                    if any(skip in img.lower() for skip in skip_keywords):
                        continue
                    # Make URL absolute if needed
                    if img.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(page_url)
                        img = f"{parsed.scheme}://{parsed.netloc}{img}"
                    return img

            return None

        except Exception as e:
            print(f"   ⚠️ Error extracting image: {e}")
            return None

    def collect_card_from_url(self, url: str, bank: Optional[str] = None) -> CreditCard:
        """
        Collect credit card information from a URL using LLM.

        Args:
            url: URL of the credit card page
            bank: Bank name (optional, will be extracted if not provided)

        Returns:
            CreditCard object with extracted information
        """
        import json
        import re

        print(f"\n{'='*60}")
        print(f"🎯 开始采集卡片: {url}")
        if bank:
            print(f"   🏦 银行: {bank}")

        prompt = f"""
        Please scrape and extract all credit card reward information from this URL:
        {url}

        Extract:
        - Bank name and card name
        - Annual fee
        - Base reward rate
        - All category-specific reward rates with any spending caps
        - Signup bonus details
        - Whether it has no foreign transaction fee
        - IMPORTANT: The credit card image URL (card face artwork). Look for <img> tags
          containing the card picture, usually a PNG or JPG file. The URL often contains
          keywords like 'card', 'image', or the card name. Return the full absolute URL.

        Return the result as a valid JSON object matching the ExtractedCreditCard schema.
        """

        print(f"   🤖 调用 Agent 爬取页面...")
        try:
            result = self.agent.run(prompt)
            content = result.content
            print(f"   ✅ Agent 返回成功，内容类型: {type(content).__name__}")
        except Exception as e:
            print(f"   ❌ Agent 调用失败: {e}")
            raise

        # Handle different content types - LLM可能返回字符串或对象
        if isinstance(content, ExtractedCreditCard):
            print(f"   ✅ 直接获得 ExtractedCreditCard 对象")
            extracted = content
        elif isinstance(content, dict):
            print(f"   📦 收到 dict，转换为 ExtractedCreditCard...")
            extracted = ExtractedCreditCard(**content)
        elif isinstance(content, str):
            print(f"   📝 收到字符串 ({len(content)} 字符)，尝试解析 JSON...")
            # Try to parse JSON from string response
            try:
                # Remove markdown code blocks if present
                json_str = content
                if "```json" in json_str:
                    json_str = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
                    json_str = json_str.group(1) if json_str else content
                    print(f"   📝 从 markdown 代码块提取 JSON")
                elif "```" in json_str:
                    json_str = re.search(r'```\s*(.*?)\s*```', json_str, re.DOTALL)
                    json_str = json_str.group(1) if json_str else content

                data = json.loads(json_str)
                extracted = ExtractedCreditCard(**data)
                print(f"   ✅ JSON 解析成功")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"   ❌ JSON 解析失败: {e}")
                print(f"   📝 原始内容预览: {content[:300]}")
                raise ValueError(f"Failed to parse LLM response as JSON: {e}\nContent: {content[:500]}")
        else:
            print(f"   ❌ 未知内容类型: {type(content)}")
            raise ValueError(f"Unexpected content type: {type(content)}\nContent: {content}")

        # Override bank if provided
        if bank:
            extracted.bank = bank

        # Get next card ID from database
        stats = self.database.get_stats()
        next_id = stats.get("total_cards", 0) + 1

        # Convert to our CreditCard model
        signup_bonus = None
        if extracted.signup_bonus:
            signup_bonus = SignupBonus(
                bonus_amount=extracted.signup_bonus.bonus_amount,
                min_spend=extracted.signup_bonus.min_spend,
                days_to_complete=extracted.signup_bonus.days_to_complete,
                description=extracted.signup_bonus.description,
            )

        reward_rules = [
            RewardRule(
                category=rule.category,
                reward_rate=Decimal(str(rule.reward_rate)),
                monthly_cap_amount=(
                    Decimal(str(rule.monthly_cap_amount))
                    if rule.monthly_cap_amount
                    else None
                ),
                description=rule.description,
            )
            for rule in extracted.reward_rules
        ]

        # Validate and fix image URL if needed
        image_url = extracted.image_url
        if image_url:
            # Check if it's a valid image URL (should end with image extension)
            image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif')
            if not any(image_url.lower().endswith(ext) or ext + '?' in image_url.lower() for ext in image_extensions):
                print(f"   ⚠️ Invalid image URL detected: {image_url[:80]}...")
                # Try to extract real image URL from the page
                image_url = self._extract_card_image(url, extracted.bank, extracted.name)
                if image_url:
                    print(f"   ✅ Extracted correct image: {image_url}")
                else:
                    print(f"   ❌ Could not find card image")
                    image_url = None

        card = CreditCard(
            id=next_id,
            bank=extracted.bank,
            name=extracted.name,
            card_type=extracted.card_type,
            annual_fee=Decimal(str(extracted.annual_fee)),
            base_reward_rate=Decimal(str(extracted.base_reward_rate)),
            image_url=image_url,
            apply_url=extracted.apply_url or url,
            no_fx_fee=extracted.no_fx_fee,
            signup_bonus=signup_bonus,
            reward_rules=reward_rules,
        )

        # Save to SQLite database
        card_id = self.database.save_card(card, source_url=url)
        card.id = card_id

        # Mark URL as scraped
        self.database.mark_url_scraped(url)

        return card

    def _create_discover_agent(self):
        """Create Agent for discovering card URLs from listing pages"""
        try:
            from agno.agent import Agent
            from agno.tools.crawl4ai import Crawl4aiTools
        except ImportError:
            raise ImportError("Please install agno and crawl4ai")

        model = self._create_model()

        instructions = """
        You are a credit card URL discovery expert. Your job is to find all individual
        credit card product page URLs from a bank's card listing page.

        When analyzing a page:
        1. Look for links to individual credit card product pages
        2. Extract the card name and full URL for each card
        3. Only include actual card product pages, not category or comparison pages
        4. Make sure URLs are complete (not relative paths)
        """

        return Agent(
            model=model,
            tools=[Crawl4aiTools(
                max_length=40000,  # 发现 URL 需要足够内容识别链接
                use_pruning=True,
                pruning_threshold=0.3,
                headless=True,
            )],
            instructions=instructions,
            output_schema=DiscoveredCardList,
            structured_outputs=False,
            use_json_mode=True,
            markdown=True,
        )

    def discover_bank_cards(self, bank: str, use_custom_crawler: bool = True) -> list[dict]:
        """
        Discover credit card URLs from a bank's website.

        Args:
            bank: Bank name (must be in BANK_CARD_LISTINGS)
            use_custom_crawler: Use optimized custom crawler (recommended)

        Returns:
            List of discovered card info dicts with 'name' and 'url'
        """
        import json

        if bank not in self.BANK_CARD_LISTINGS:
            raise ValueError(
                f"Bank '{bank}' not supported. Supported banks: {list(self.BANK_CARD_LISTINGS.keys())}"
            )

        listing_url = self.BANK_CARD_LISTINGS[bank]

        print(f"🔍 正在发现 {bank} 的信用卡...")
        print(f"   📄 列表页: {listing_url}")

        # Use custom optimized crawler first (more reliable for JS-heavy sites)
        if use_custom_crawler:
            print(f"   🕷️ 使用优化爬虫...")
            try:
                from src.agents.custom_crawl_tool import discover_cards_sync
                cards = discover_cards_sync(listing_url, bank=bank)
                if cards:
                    print(f"   ✅ 发现 {len(cards)} 张卡片")
                    return cards
                else:
                    print(f"   ⚠️ 优化爬虫未发现卡片，回退到 Agent...")
            except Exception as e:
                print(f"   ⚠️ 优化爬虫失败: {e}，回退到 Agent...")

        # Fallback to LLM Agent
        print(f"   🤖 调用 Agent 爬取页面...")
        discover_agent = self._create_discover_agent()

        prompt = f"""
        Visit this credit card listing page and find ALL individual credit card product pages:
        {listing_url}

        For each credit card found, extract:
        1. The card name (e.g., "BMO CashBack Mastercard")
        2. The full URL to its dedicated product page

        Rules:
        - Only include actual credit card product pages
        - Do NOT include the listing page itself
        - Do NOT include category pages or comparison pages
        - URLs must be complete (starting with https://)
        """

        try:
            result = discover_agent.run(prompt)
            content = result.content
            print(f"   ✅ Agent 返回成功，内容类型: {type(content).__name__}")
            if isinstance(content, str):
                print(f"   📝 内容长度: {len(content)} 字符")
                print(f"   📝 内容预览: {content[:200]}...")
        except Exception as e:
            print(f"   ❌ Agent 调用失败: {e}")
            return []

        # Handle LLM response - 让 Agent 直接返回结构化数据
        cards = []
        discovered_list = None

        if isinstance(content, DiscoveredCardList):
            print(f"   ✅ 直接获得 DiscoveredCardList 对象")
            discovered_list = content
        elif isinstance(content, dict):
            print(f"   📦 收到 dict，转换为 DiscoveredCardList...")
            discovered_list = DiscoveredCardList(**content)
        elif isinstance(content, str):
            print(f"   📝 收到字符串，尝试解析 JSON...")
            # Try to parse JSON string
            try:
                import re
                json_str = content
                if "```json" in json_str:
                    match = re.search(r'```json\s*(.*?)\s*```', json_str, re.DOTALL)
                    json_str = match.group(1) if match else content
                    print(f"   📝 从 markdown 代码块提取 JSON")
                elif "```" in json_str:
                    match = re.search(r'```\s*(.*?)\s*```', json_str, re.DOTALL)
                    json_str = match.group(1) if match else content

                data = json.loads(json_str)
                discovered_list = DiscoveredCardList(**data)
                print(f"   ✅ JSON 解析成功")
            except Exception as e:
                print(f"   ⚠️ LLM 返回格式解析失败: {e}")
                print(f"   📝 原始内容: {content[:500]}")
        else:
            print(f"   ⚠️ 未知内容类型: {type(content)}")

        if discovered_list and discovered_list.cards:
            print(f"   📋 解析到 {len(discovered_list.cards)} 张卡片")
            for card in discovered_list.cards:
                # Save to database
                self.database.save_bank_card_url(
                    bank=bank,
                    url=card.url,
                    card_name=card.name,
                )
                cards.append({
                    "bank": bank,
                    "name": card.name,
                    "url": card.url,
                })
                print(f"   📎 发现: {card.name}")
                print(f"      🔗 {card.url}")
        else:
            print(f"   ⚠️ 未发现任何卡片")

        print(f"✅ 共发现 {len(cards)} 张 {bank} 信用卡")
        print("=" * 60)
        return cards

    def collect_bank_cards(self, bank: str, max_cards: Optional[int] = None) -> list[CreditCard]:
        """
        Collect all credit cards from a bank.

        Args:
            bank: Bank name
            max_cards: Maximum number of cards to collect (optional)

        Returns:
            List of collected CreditCard objects
        """
        # First discover cards
        discovered = self.discover_bank_cards(bank)

        # Save discovered URLs to database for tracking
        for card_info in discovered:
            self.database.save_bank_card_url(
                bank=bank,
                url=card_info['url'],
                card_name=card_info.get('name'),
            )

        print(f"✅ 共发现 {len(discovered)} 张 {bank} 信用卡")
        print("=" * 60)

        # Now collect each discovered card
        collected = []
        for i, card_info in enumerate(discovered):
            if max_cards and i >= max_cards:
                print(f"⚠️ 达到最大采集数量 {max_cards}，停止采集")
                break

            url = card_info['url']
            print(f"\n{'=' * 60}")
            print(f"🎯 开始采集卡片: {url}")
            print(f"   🏦 银行: {bank}")

            try:
                card = self.collect_card_from_url(
                    url=url,
                    bank=bank,
                )
                collected.append(card)
                # Mark URL as scraped
                self.database.mark_url_scraped(url)
                print(f"✅ Collected: {card.bank} - {card.name}")
            except Exception as e:
                print(f"❌ Error collecting from {url}: {e}")
                continue

        print(f"\n{'=' * 60}")
        print(f"✅ 采集完成！共采集 {len(collected)}/{len(discovered)} 张卡片")
        return collected

    def search_bank_cards(self, bank: str) -> list[dict]:
        """
        Search for credit card URLs using web search.

        Args:
            bank: Bank name to search for

        Returns:
            List of search results with URLs
        """
        query = f"{bank} credit cards cashback rewards official site Canada"

        prompt = f"""
        Search for "{query}" and find the official credit card pages.
        Return the top 10 most relevant URLs for {bank} credit cards.
        Focus on official bank websites, not comparison sites.
        """

        result = self.search_agent.run(prompt)

        return [{
            "bank": bank,
            "query": query,
            "response": str(result.content) if result.content else "",
        }]

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported LLM providers"""
        return [p.value for p in LLMProvider]

    def get_supported_banks(self) -> list[str]:
        """Get list of supported banks from database."""
        return list(self.BANK_CARD_LISTINGS.keys())
