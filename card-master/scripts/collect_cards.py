#!/usr/bin/env python3
"""
Collect credit card information from bank websites using Agno Agent.

Supports multiple LLM providers: Volces (默认), OpenAI, Claude, Gemini, Groq, DeepSeek, Ollama.

Usage:
    # Collect a single card by URL (uses default provider: volces)
    python scripts/collect_cards.py <url>

    # Collect all cards from a bank
    python scripts/collect_cards.py --bank BMO

    # Use a specific provider
    python scripts/collect_cards.py --bank BMO --provider openai

    # List supported banks and providers
    python scripts/collect_cards.py --list

Examples:
    python scripts/collect_cards.py https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/
    python scripts/collect_cards.py --bank BMO --max-cards 3
    python scripts/collect_cards.py --bank TD --provider claude --model claude-sonnet-4-20250514
"""

import sys
import os
import argparse
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.card_collector_agent import CardCollectorAgent, LLMProvider, DEFAULT_MODELS
from src.services.database import Database


def print_card_details(card):
    """Print card details in a formatted way"""
    print(f"\n{'='*60}")
    print(f"✅ {card.bank} - {card.name}")
    print(f"{'='*60}")
    print(f"  Card Type: {card.card_type}")
    print(f"  Annual Fee: ${card.annual_fee}")
    print(f"  Base Reward Rate: {card.base_reward_rate_percent}")
    print(f"  No FX Fee: {card.no_fx_fee}")

    if card.signup_bonus:
        print(f"\n  🎁 Signup Bonus:")
        print(f"     Bonus: {card.signup_bonus.bonus_amount}")
        print(f"     Min Spend: ${card.signup_bonus.min_spend}")
        print(f"     Days: {card.signup_bonus.days_to_complete}")

    if card.reward_rules:
        print(f"\n  💰 Reward Rules ({len(card.reward_rules)} categories):")
        for rule in card.reward_rules:
            cap = f" (cap: ${rule.monthly_cap_amount}/mo)" if rule.monthly_cap_amount else ""
            print(f"     - {rule.category}: {rule.reward_rate_percent}{cap}")


def list_info():
    """List supported banks and providers"""
    print("\n" + "="*60)
    print("📊 Card Master - Agno Agent Information")
    print("="*60)

    print("\n🏦 Supported Banks:")
    for bank in CardCollectorAgent.get_supported_banks():
        url = CardCollectorAgent.BANK_CARD_LISTINGS.get(bank, "")
        print(f"   - {bank}: {url}")

    print("\n🤖 Supported LLM Providers:")
    for provider in LLMProvider:
        default_model = DEFAULT_MODELS.get(provider, "unknown")
        env_vars = {
            LLMProvider.VOLCES: "VOLCES_API_KEY (默认)",
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.CLAUDE: "ANTHROPIC_API_KEY",
            LLMProvider.GEMINI: "GOOGLE_API_KEY",
            LLMProvider.GROQ: "GROQ_API_KEY",
            LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
            LLMProvider.OLLAMA: "(no key needed)",
        }
        env_var = env_vars.get(provider, "unknown")
        is_default = " ⭐" if provider == LLMProvider.VOLCES else ""
        print(f"   - {provider.value}: {default_model} (env: {env_var}){is_default}")


def collect_single_url(url: str, provider: LLMProvider, model_id: str = None, bank: str = None):
    """Collect a single card from URL"""
    print(f"\n{'='*60}")
    print(f"🔍 Collecting credit card info from:")
    print(f"   URL: {url}")
    print(f"   Provider: {provider.value}")
    print(f"   Model: {model_id or DEFAULT_MODELS[provider]}")
    print(f"{'='*60}\n")

    db = Database()
    agent = CardCollectorAgent(
        provider=provider,
        model_id=model_id,
        database=db,
    )

    card = agent.collect_card_from_url(url, bank=bank)
    print_card_details(card)

    return card


def collect_bank_cards(bank: str, provider: LLMProvider, model_id: str = None, max_cards: int = None):
    """Collect all cards from a bank"""
    print(f"\n{'='*60}")
    print(f"🏦 Collecting all credit cards from {bank}")
    print(f"   Provider: {provider.value}")
    print(f"   Model: {model_id or DEFAULT_MODELS[provider]}")
    if max_cards:
        print(f"   Max Cards: {max_cards}")
    print(f"{'='*60}\n")

    db = Database()
    agent = CardCollectorAgent(
        provider=provider,
        model_id=model_id,
        database=db,
    )

    cards = agent.collect_bank_cards(bank, max_cards=max_cards)

    print(f"\n{'='*60}")
    print(f"✅ Collected {len(cards)} cards from {bank}")
    print(f"{'='*60}")

    for card in cards:
        print_card_details(card)

    return cards


def main():
    parser = argparse.ArgumentParser(
        description="Collect credit card information using Agno Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="URL of the credit card page to scrape",
    )
    parser.add_argument(
        "--bank",
        help="Bank name to collect all cards from",
    )
    parser.add_argument(
        "--provider",
        choices=["volces", "openai", "claude", "gemini", "groq", "deepseek", "ollama"],
        default="volces",
        help="LLM provider to use (default: volces)",
    )
    parser.add_argument(
        "--model",
        help="Specific model ID to use (optional)",
    )
    parser.add_argument(
        "--max-cards",
        type=int,
        help="Maximum number of cards to collect from a bank",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List supported banks and providers",
    )

    args = parser.parse_args()

    # Show list if requested
    if args.list:
        list_info()
        return

    # Validate arguments
    if not args.url and not args.bank:
        parser.print_help()
        print("\n❌ Error: Please provide either a URL or --bank argument")
        sys.exit(1)

    # Convert provider string to enum
    provider = LLMProvider(args.provider)

    # Check for API key (except Ollama)
    env_vars = {
        LLMProvider.VOLCES: "VOLCES_API_KEY",
        LLMProvider.OPENAI: "OPENAI_API_KEY",
        LLMProvider.CLAUDE: "ANTHROPIC_API_KEY",
        LLMProvider.GEMINI: "GOOGLE_API_KEY",
        LLMProvider.GROQ: "GROQ_API_KEY",
        LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
    }

    if provider != LLMProvider.OLLAMA:
        env_var = env_vars.get(provider)
        if env_var and not os.environ.get(env_var):
            print(f"\n❌ Error: {env_var} environment variable not set!")
            print(f"   Please set it: export {env_var}='your-api-key'")
            print(f"   Or create a .env file with the key")
            sys.exit(1)

    try:
        if args.bank:
            # Collect all cards from a bank
            if args.bank not in CardCollectorAgent.get_supported_banks():
                print(f"\n❌ Error: Bank '{args.bank}' not supported")
                print(f"   Supported banks: {CardCollectorAgent.get_supported_banks()}")
                sys.exit(1)

            collect_bank_cards(
                bank=args.bank,
                provider=provider,
                model_id=args.model,
                max_cards=args.max_cards,
            )
        else:
            # Collect single card from URL
            collect_single_url(
                url=args.url,
                provider=provider,
                model_id=args.model,
            )

        # Print database stats
        db = Database()
        stats = db.get_stats()
        print(f"\n📊 Database Stats:")
        print(f"   Total Cards: {stats.get('total_cards', 0)}")
        print(f"   Total Banks: {stats.get('total_banks', 0)}")

    except ImportError as e:
        print(f"\n❌ Error: Missing dependencies")
        print(f"   {e}")
        print(f"\n   Please install required packages:")
        print(f"   pip install agno crawl4ai duckduckgo-search")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
