#!/usr/bin/env python3
"""
Sync Savevia Cards - Scrape official bank pages and generate SQL updates.

This script:
1. Fetches all credit cards from savevia MySQL database
2. Uses AI agent to scrape each card's official page
3. Compares scraped data with existing data
4. Generates UPDATE SQL statements for changes

Usage:
    python scripts/sync_savevia_cards.py                    # Process all cards
    python scripts/sync_savevia_cards.py --bank AMEX        # Process only AMEX cards
    python scripts/sync_savevia_cards.py --card-id 1        # Process only card ID 1
    python scripts/sync_savevia_cards.py --dry-run          # Don't scrape, just show cards
    python scripts/sync_savevia_cards.py --output updates.sql  # Save SQL to file
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Fix asyncio for crawl4ai
import asyncio
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
import nest_asyncio
nest_asyncio.apply()

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.services.savevia_mysql import SaveviaMySQLDatabase, SaveviaCard
from src.agents.card_collector_agent import CardCollectorAgent, LLMProvider, ExtractedCreditCard

console = Console()


@dataclass
class CardDiff:
    """Differences between existing and scraped card data."""
    card_id: int
    bank: str
    card_name: str
    field: str
    old_value: any
    new_value: any


@dataclass
class SyncResult:
    """Result of syncing a card."""
    card_id: int
    bank: str
    card_name: str
    success: bool
    scraped_data: Optional[ExtractedCreditCard] = None
    diffs: list[CardDiff] = field(default_factory=list)
    error: Optional[str] = None


def compare_cards(existing: SaveviaCard, scraped: ExtractedCreditCard) -> list[CardDiff]:
    """Compare existing card data with scraped data and return differences."""
    diffs = []

    # Compare annual fee
    scraped_fee = Decimal(str(scraped.annual_fee))
    if existing.annual_fee != scraped_fee:
        diffs.append(CardDiff(
            card_id=existing.id,
            bank=existing.bank,
            card_name=existing.name,
            field="annual_fee",
            old_value=float(existing.annual_fee),
            new_value=float(scraped_fee),
        ))

    # Compare base reward rate
    scraped_rate = Decimal(str(scraped.base_reward_rate))
    if existing.base_reward_rate != scraped_rate:
        diffs.append(CardDiff(
            card_id=existing.id,
            bank=existing.bank,
            card_name=existing.name,
            field="base_reward_rate",
            old_value=float(existing.base_reward_rate),
            new_value=float(scraped_rate),
        ))

    # Compare no_fx_fee
    if existing.no_fx_fee != scraped.no_fx_fee:
        diffs.append(CardDiff(
            card_id=existing.id,
            bank=existing.bank,
            card_name=existing.name,
            field="no_fx_fee",
            old_value=existing.no_fx_fee,
            new_value=scraped.no_fx_fee,
        ))

    # Compare image_url (only if scraped has one)
    if scraped.image_url and scraped.image_url != existing.image_url:
        diffs.append(CardDiff(
            card_id=existing.id,
            bank=existing.bank,
            card_name=existing.name,
            field="image_url",
            old_value=existing.image_url,
            new_value=scraped.image_url,
        ))

    # Compare signup bonus
    if scraped.signup_bonus:
        existing_bonus = existing.signup_bonus_json or {}
        scraped_bonus = {
            "bonusAmount": scraped.signup_bonus.bonus_amount,
            "minSpend": scraped.signup_bonus.min_spend,
            "daysToComplete": scraped.signup_bonus.days_to_complete,
            "description": scraped.signup_bonus.description,
        }

        # Check if bonus amounts differ
        if existing_bonus.get("bonusAmount") != scraped_bonus["bonusAmount"]:
            diffs.append(CardDiff(
                card_id=existing.id,
                bank=existing.bank,
                card_name=existing.name,
                field="signup_bonus_json",
                old_value=existing_bonus,
                new_value=scraped_bonus,
            ))

    # Compare reward rules
    existing_rules = {r["category"]: r for r in existing.reward_rules}
    scraped_rules = {r.category: r for r in scraped.reward_rules}

    # Find new or changed rules
    for category, rule in scraped_rules.items():
        if category not in existing_rules:
            diffs.append(CardDiff(
                card_id=existing.id,
                bank=existing.bank,
                card_name=existing.name,
                field=f"reward_rule:{category}",
                old_value=None,
                new_value={
                    "category": rule.category,
                    "reward_rate": rule.reward_rate,
                    "monthly_cap_amount": rule.monthly_cap_amount,
                    "description": rule.description,
                },
            ))
        else:
            existing_rule = existing_rules[category]
            if abs(existing_rule["reward_rate"] - rule.reward_rate) > 0.0001:
                diffs.append(CardDiff(
                    card_id=existing.id,
                    bank=existing.bank,
                    card_name=existing.name,
                    field=f"reward_rule:{category}:reward_rate",
                    old_value=existing_rule["reward_rate"],
                    new_value=rule.reward_rate,
                ))

    return diffs


def generate_sql_updates(results: list[SyncResult], output_file: str = None) -> str:
    """Generate SQL UPDATE statements from sync results."""
    sql_lines = []
    sql_lines.append(f"-- Card Master Sync SQL Updates")
    sql_lines.append(f"-- Generated: {datetime.now().isoformat()}")
    sql_lines.append(f"-- Total cards processed: {len(results)}")
    sql_lines.append(f"-- Cards with changes: {len([r for r in results if r.diffs])}")
    sql_lines.append("")

    for result in results:
        if not result.success or not result.diffs:
            continue

        sql_lines.append(f"-- {result.bank} - {result.card_name} (ID: {result.card_id})")

        # Group diffs by table
        credit_card_updates = {}
        reward_rule_inserts = []
        reward_rule_updates = []

        for diff in result.diffs:
            if diff.field.startswith("reward_rule:"):
                parts = diff.field.split(":")
                if len(parts) == 2:
                    # New reward rule
                    reward_rule_inserts.append(diff)
                elif len(parts) == 3:
                    # Update reward rate
                    reward_rule_updates.append(diff)
            else:
                credit_card_updates[diff.field] = diff

        # Generate credit_cards UPDATE
        if credit_card_updates:
            set_clauses = []
            for field, diff in credit_card_updates.items():
                if field == "signup_bonus_json":
                    value = json.dumps(diff.new_value, ensure_ascii=False)
                    set_clauses.append(f"  {field} = '{value}'")
                elif field == "no_fx_fee":
                    set_clauses.append(f"  {field} = {1 if diff.new_value else 0}")
                elif field == "image_url":
                    set_clauses.append(f"  {field} = '{diff.new_value}'")
                else:
                    set_clauses.append(f"  {field} = {diff.new_value}")

            if set_clauses:
                sql_lines.append(f"UPDATE credit_cards SET")
                sql_lines.append(",\n".join(set_clauses))
                sql_lines.append(f"WHERE id = {result.card_id};")
                sql_lines.append("")

        # Generate reward_rules INSERT
        for diff in reward_rule_inserts:
            rule = diff.new_value
            monthly_cap = rule["monthly_cap_amount"] if rule["monthly_cap_amount"] else "NULL"
            description = rule["description"].replace("'", "''") if rule["description"] else ""
            sql_lines.append(f"INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)")
            sql_lines.append(f"VALUES ({result.card_id}, '{rule['category']}', {rule['reward_rate']}, {monthly_cap}, '{description}');")
            sql_lines.append("")

        # Generate reward_rules UPDATE
        for diff in reward_rule_updates:
            parts = diff.field.split(":")
            category = parts[1]
            sql_lines.append(f"UPDATE reward_rules SET reward_rate = {diff.new_value}")
            sql_lines.append(f"WHERE card_id = {result.card_id} AND category = '{category}';")
            sql_lines.append("")

    sql_content = "\n".join(sql_lines)

    if output_file:
        Path(output_file).write_text(sql_content)
        console.print(f"[green]SQL saved to: {output_file}[/green]")

    return sql_content


def scrape_card(agent: CardCollectorAgent, card: SaveviaCard) -> SyncResult:
    """Scrape a single card and return sync result."""
    result = SyncResult(
        card_id=card.id,
        bank=card.bank,
        card_name=card.name,
        success=False,
    )

    if not card.apply_url:
        result.error = "No apply_url"
        return result

    try:
        console.print(f"  [cyan]Scraping: {card.apply_url}[/cyan]")

        # Use the agent to scrape the card page
        scraped = agent.collect_card_from_url(
            url=card.apply_url,
            bank=card.bank,
        )

        # Convert CreditCard back to ExtractedCreditCard for comparison
        from src.agents.card_collector_agent import ExtractedCreditCard, ExtractedRewardRule, ExtractedSignupBonus

        scraped_data = ExtractedCreditCard(
            bank=scraped.bank,
            name=scraped.name,
            card_type=scraped.card_type,
            annual_fee=float(scraped.annual_fee),
            base_reward_rate=float(scraped.base_reward_rate),
            image_url=scraped.image_url,
            apply_url=scraped.apply_url,
            no_fx_fee=scraped.no_fx_fee,
            signup_bonus=ExtractedSignupBonus(
                bonus_amount=scraped.signup_bonus.bonus_amount,
                min_spend=scraped.signup_bonus.min_spend,
                days_to_complete=scraped.signup_bonus.days_to_complete,
                description=scraped.signup_bonus.description,
            ) if scraped.signup_bonus else None,
            reward_rules=[
                ExtractedRewardRule(
                    category=r.category,
                    reward_rate=float(r.reward_rate),
                    monthly_cap_amount=float(r.monthly_cap_amount) if r.monthly_cap_amount else None,
                    description=r.description,
                )
                for r in scraped.reward_rules
            ],
        )

        result.scraped_data = scraped_data
        result.diffs = compare_cards(card, scraped_data)
        result.success = True

    except Exception as e:
        result.error = str(e)
        console.print(f"  [red]Error: {e}[/red]")

    return result


def main():
    parser = argparse.ArgumentParser(description="Sync Savevia cards from official bank pages")
    parser.add_argument("--bank", help="Only process cards from this bank")
    parser.add_argument("--card-id", type=int, help="Only process this card ID")
    parser.add_argument("--dry-run", action="store_true", help="Don't scrape, just show cards")
    parser.add_argument("--output", "-o", help="Output SQL file path")
    parser.add_argument("--provider", default="openai", help="LLM provider (default: openai)")
    parser.add_argument("--model", help="LLM model ID")
    parser.add_argument("--limit", type=int, help="Maximum number of cards to process")
    args = parser.parse_args()

    console.print("\n[bold blue]Card Master - Savevia Sync[/bold blue]")
    console.print("=" * 50)

    # Connect to MySQL
    console.print("\n[yellow]Connecting to Savevia MySQL...[/yellow]")
    try:
        db = SaveviaMySQLDatabase()
        stats = db.get_stats()
        console.print(f"[green]Connected! {stats['total_cards']} cards in database[/green]")
    except Exception as e:
        console.print(f"[red]Failed to connect to MySQL: {e}[/red]")
        console.print("[yellow]Make sure MySQL is running and .env is configured[/yellow]")
        sys.exit(1)

    # Fetch cards
    cards = db.get_all_cards()

    # Filter by bank
    if args.bank:
        cards = [c for c in cards if c.bank.lower() == args.bank.lower()]
        console.print(f"[cyan]Filtered to {len(cards)} cards from {args.bank}[/cyan]")

    # Filter by card ID
    if args.card_id:
        cards = [c for c in cards if c.id == args.card_id]
        console.print(f"[cyan]Filtered to card ID {args.card_id}[/cyan]")

    # Apply limit
    if args.limit:
        cards = cards[:args.limit]
        console.print(f"[cyan]Limited to {len(cards)} cards[/cyan]")

    if not cards:
        console.print("[red]No cards found matching criteria[/red]")
        sys.exit(1)

    # Show cards table
    table = Table(title=f"Cards to Process ({len(cards)})")
    table.add_column("ID", style="cyan")
    table.add_column("Bank", style="green")
    table.add_column("Name", style="white")
    table.add_column("Apply URL", style="dim")

    for card in cards:
        url = card.apply_url[:50] + "..." if card.apply_url and len(card.apply_url) > 50 else card.apply_url or "N/A"
        table.add_row(str(card.id), card.bank, card.name, url)

    console.print(table)

    if args.dry_run:
        console.print("\n[yellow]Dry run mode - no scraping performed[/yellow]")
        return

    # Confirm
    console.print(f"\n[bold]Ready to scrape {len(cards)} cards using {args.provider}[/bold]")
    response = input("Continue? [y/N]: ")
    if response.lower() != "y":
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Create agent
    console.print(f"\n[yellow]Initializing {args.provider} agent...[/yellow]")
    try:
        provider = LLMProvider(args.provider)
        agent = CardCollectorAgent(
            provider=provider,
            model_id=args.model,
        )
        console.print(f"[green]Agent ready![/green]")
    except Exception as e:
        console.print(f"[red]Failed to create agent: {e}[/red]")
        sys.exit(1)

    # Process cards
    results = []
    for i, card in enumerate(cards, 1):
        console.print(f"\n[bold][{i}/{len(cards)}] {card.bank} - {card.name}[/bold]")
        result = scrape_card(agent, card)
        results.append(result)

        if result.success:
            if result.diffs:
                console.print(f"  [yellow]Found {len(result.diffs)} differences[/yellow]")
                for diff in result.diffs:
                    console.print(f"    - {diff.field}: {diff.old_value} -> {diff.new_value}")
            else:
                console.print(f"  [green]No changes detected[/green]")
        else:
            console.print(f"  [red]Failed: {result.error}[/red]")

    # Summary
    console.print("\n" + "=" * 50)
    console.print("[bold]Sync Summary[/bold]")
    console.print(f"  Total cards: {len(results)}")
    console.print(f"  Successful: {len([r for r in results if r.success])}")
    console.print(f"  With changes: {len([r for r in results if r.diffs])}")
    console.print(f"  Failed: {len([r for r in results if not r.success])}")

    # Generate SQL
    if any(r.diffs for r in results):
        output_file = args.output or f"output/sync_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        sql = generate_sql_updates(results, output_file)
        console.print(f"\n[green]SQL updates generated: {output_file}[/green]")


if __name__ == "__main__":
    main()
