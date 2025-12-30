#!/usr/bin/env python3
"""
Sync banks from Savevia MySQL to Card-master SQLite.

This script:
1. Fetches all unique banks from savevia.credit_cards
2. Compares with card-master banks table
3. Adds missing banks with their credit card listing URLs
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table

from src.services.savevia_mysql import SaveviaMySQLDatabase
from src.services.database import Database

console = Console()

# Bank listing page URLs (official credit card pages)
BANK_LISTING_URLS = {
    # Big 5 Banks
    "TD": "https://www.td.com/ca/en/personal-banking/products/credit-cards",
    "RBC": "https://www.rbcroyalbank.com/credit-cards/",
    "BMO": "https://www.bmo.com/main/personal/credit-cards/",
    "Scotiabank": "https://www.scotiabank.com/ca/en/personal/credit-cards.html",
    "CIBC": "https://www.cibc.com/en/personal-banking/credit-cards.html",
    # Other Major Banks
    "National Bank": "https://www.nbc.ca/personal/credit-cards.html",
    "Laurentian Bank": "https://www.laurentianbank.ca/en/personal/credit-cards.html",
    "Desjardins": "https://www.desjardins.com/ca/personal/loans-credit/credit-cards/index.jsp",
    "ATB Financial": "https://www.atb.com/personal/bank-accounts/credit-cards/",
    # Digital Banks
    "Tangerine": "https://www.tangerine.ca/en/products/spending/creditcard",
    "Simplii": "https://www.simplii.com/en/credit-cards.html",
    # Card Networks & Issuers
    "AMEX": "https://www.americanexpress.com/en-ca/credit-cards/",
    "MBNA": "https://www.mbna.ca/en/credit-cards/",
    "Rogers": "https://www.rogersbank.com/en/credit_cards",
    "Home Trust": "https://www.hometrust.ca/credit-cards/",
    # Fintech
    "Neo": "https://www.neofinancial.com/credit",
    "Brim Financial": "https://bfrb.io/all-cards",
    "Wealthsimple": "https://www.wealthsimple.com/en-ca/credit-card",
    # Retail Cards
    "Canadian Tire": "https://triangle.canadiantire.ca/en/credit-cards.html",
    "PC Financial": "https://www.pcfinancial.ca/en/credit-cards/",
    "Walmart": "https://www.walmartrewards.ca/en/creditcards",
    # Credit Unions
    "Coast Capital": "https://www.coastcapitalsavings.com/everyday-banking/credit-cards",
    "Vancity": "https://www.vancity.com/bank/credit-cards/",
    "Meridian": "https://www.meridiancu.ca/personal/credit-cards",
    "Affinity Credit Union": "https://www.affinitycu.ca/personal/credit-cards",
    "Servus Credit Union": "https://www.servus.ca/spending/credit-cards",
    "First Calgary": "https://www.firstcalgary.com/Personal/Credit-Cards/",
    "Conexus Credit Union": "https://www.conexus.ca/Personal/CreditCards/",
}


def sync_banks():
    """Sync banks from Savevia to Card-master."""
    console.print("\n[bold blue]Bank Sync - Savevia -> Card-master[/bold blue]")
    console.print("=" * 50)

    # Connect to databases
    console.print("\n[yellow]Connecting to databases...[/yellow]")
    try:
        savevia_db = SaveviaMySQLDatabase()
        cardmaster_db = Database()
        console.print("[green]Connected![/green]")
    except Exception as e:
        console.print(f"[red]Failed to connect: {e}[/red]")
        sys.exit(1)

    # Get banks from Savevia
    savevia_cards = savevia_db.get_all_cards()
    savevia_banks = sorted(set(c.bank for c in savevia_cards))
    console.print(f"\n[cyan]Savevia banks: {len(savevia_banks)}[/cyan]")

    # Get banks from Card-master
    cardmaster_banks = cardmaster_db.get_all_banks(active_only=False)
    cardmaster_bank_names = {b["name"] for b in cardmaster_banks}
    console.print(f"[cyan]Card-master banks: {len(cardmaster_bank_names)}[/cyan]")

    # Find missing banks
    missing_banks = [b for b in savevia_banks if b not in cardmaster_bank_names]
    console.print(f"[yellow]Missing in Card-master: {len(missing_banks)}[/yellow]")

    if not missing_banks:
        console.print("\n[green]All banks are synced![/green]")
        return

    # Show missing banks
    table = Table(title="Banks to Add")
    table.add_column("Bank", style="cyan")
    table.add_column("Listing URL", style="dim")
    table.add_column("Status", style="green")

    for bank in missing_banks:
        url = BANK_LISTING_URLS.get(bank, "")
        status = "URL found" if url else "[red]No URL[/red]"
        table.add_row(bank, url[:60] + "..." if len(url) > 60 else url, status)

    console.print(table)

    # Add missing banks
    console.print(f"\n[yellow]Adding {len(missing_banks)} banks...[/yellow]")
    added = 0
    for bank in missing_banks:
        url = BANK_LISTING_URLS.get(bank, "")
        if not url:
            console.print(f"  [red]Skipping {bank} - no URL[/red]")
            continue

        try:
            bank_id = cardmaster_db.add_bank(
                name=bank,
                cards_url=url,
                logo_url=None,
            )
            console.print(f"  [green]Added: {bank} (ID: {bank_id})[/green]")
            added += 1
        except Exception as e:
            console.print(f"  [red]Failed to add {bank}: {e}[/red]")

    console.print(f"\n[green]Sync complete! Added {added} banks.[/green]")

    # Show final state
    console.print("\n[bold]Current Card-master Banks:[/bold]")
    final_banks = cardmaster_db.get_all_banks(active_only=False)
    for b in final_banks:
        console.print(f"  - {b['name']}: {b['cards_url'][:50]}...")


if __name__ == "__main__":
    sync_banks()
