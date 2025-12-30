"""
FastAPI routes for credit card API.
"""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.models import CATEGORY_CN_NAMES
from src.services import CardService, CardStorage, Database
from src.agents.bank_scraper import BankScraper, PLAYWRIGHT_AVAILABLE
from src.agents.card_analyzer import create_analysis_prompt, parse_llm_response


router = APIRouter(prefix="/api", tags=["cards"])

# Initialize services
storage = CardStorage()
database = Database()
card_service = CardService(storage, database)


# Response models
class CardResponse(BaseModel):
    """Credit card response model for JSON serialization"""
    id: int
    bank: str
    name: str
    card_type: str
    annual_fee: float
    base_reward_rate: float
    base_reward_rate_percent: str
    image_url: Optional[str]
    apply_url: Optional[str]
    no_fx_fee: bool
    signup_bonus: Optional[dict]
    reward_rules: list[dict]

    class Config:
        from_attributes = True


class RankItemResponse(BaseModel):
    """Card ranking item response"""
    card_id: int
    bank: str
    card_name: str
    card_type: str
    annual_fee: float
    category: str
    category_cn: str
    reward_rate: float
    reward_rate_percent: str
    monthly_cap: Optional[float]
    description: Optional[str]
    apply_url: Optional[str]


class CategoryResponse(BaseModel):
    """Spending category response"""
    code: str
    name: str


class StatsResponse(BaseModel):
    """Summary statistics response"""
    total_cards: int
    total_banks: int
    no_annual_fee_cards: int
    no_fx_fee_cards: int
    avg_annual_fee: float


def card_to_response(card) -> dict:
    """Convert CreditCard to response dict"""
    signup_bonus = None
    if card.signup_bonus:
        signup_bonus = {
            "bonusAmount": card.signup_bonus.bonus_amount,
            "minSpend": card.signup_bonus.min_spend,
            "daysToComplete": card.signup_bonus.days_to_complete,
            "description": card.signup_bonus.description,
        }

    reward_rules = [
        {
            "id": rule.id,
            "category": rule.category,
            "categoryCn": rule.category_cn,
            "categoryIcon": rule.category_icon,
            "rewardRate": float(rule.reward_rate),
            "rewardRatePercent": rule.reward_rate_percent,
            "monthlyCapAmount": float(rule.monthly_cap_amount) if rule.monthly_cap_amount else None,
            "description": rule.description,
        }
        for rule in card.reward_rules
    ]

    return {
        "id": card.id,
        "bank": card.bank,
        "name": card.name,
        "cardType": card.card_type,
        "annualFee": float(card.annual_fee),
        "baseRewardRate": float(card.base_reward_rate),
        "baseRewardRatePercent": card.base_reward_rate_percent,
        "imageUrl": card.image_url,
        "applyUrl": card.apply_url,
        "noFxFee": card.no_fx_fee,
        "signupBonus": signup_bonus,
        "rewardRules": reward_rules,
    }


@router.get("/cards")
async def get_all_cards(
    bank: Optional[str] = Query(None, description="Filter by bank name"),
    no_annual_fee: bool = Query(False, description="Only show cards with no annual fee"),
    no_fx_fee: bool = Query(False, description="Only show cards with no FX fee"),
):
    """Get all credit cards with optional filters"""
    if bank:
        cards = card_service.get_cards_by_bank(bank)
    else:
        cards = card_service.get_all_cards()

    if no_annual_fee:
        cards = [c for c in cards if c.annual_fee == 0]

    if no_fx_fee:
        cards = [c for c in cards if c.no_fx_fee]

    return {
        "code": 200,
        "message": "success",
        "data": [card_to_response(card) for card in cards],
        "count": len(cards),
    }


@router.get("/cards/{card_id}")
async def get_card_by_id(card_id: int):
    """Get a specific card by ID"""
    card = card_service.get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return {
        "code": 200,
        "message": "success",
        "data": card_to_response(card),
    }


@router.get("/cards/rank/{category}")
async def rank_cards_by_category(
    category: str,
    limit: Optional[int] = Query(None, description="Max number of cards to return"),
    include_base_rate: bool = Query(True, description="Include cards with only base rate"),
):
    """
    Rank cards by reward rate for a specific spending category.
    Returns cards sorted by reward rate (highest first).
    """
    # Validate category
    valid_categories = list(CATEGORY_CN_NAMES.keys())
    if category.upper() not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid categories: {', '.join(valid_categories)}",
        )

    ranked = card_service.rank_cards_by_category(
        category=category.upper(),
        limit=limit,
        include_base_rate=include_base_rate,
    )

    data = [
        {
            "cardId": item.card.id,
            "bank": item.card.bank,
            "cardName": item.card.name,
            "cardType": item.card.card_type,
            "annualFee": float(item.card.annual_fee),
            "category": item.category,
            "categoryCn": item.category_cn,
            "rewardRate": float(item.reward_rate),
            "rewardRatePercent": item.reward_rate_percent,
            "monthlyCap": float(item.monthly_cap) if item.monthly_cap else None,
            "description": item.description,
            "applyUrl": item.card.apply_url,
            "imageUrl": item.card.image_url,
            "noFxFee": item.card.no_fx_fee,
        }
        for item in ranked
    ]

    return {
        "code": 200,
        "message": "success",
        "category": category.upper(),
        "categoryCn": CATEGORY_CN_NAMES.get(category.upper(), category),
        "data": data,
        "count": len(data),
    }


@router.get("/categories")
async def get_categories():
    """Get all spending categories that have at least one card"""
    categories = card_service.get_all_categories()

    return {
        "code": 200,
        "message": "success",
        "data": categories,
    }


@router.get("/banks")
async def get_banks():
    """Get all unique bank names"""
    banks = card_service.get_all_banks()

    return {
        "code": 200,
        "message": "success",
        "data": banks,
    }


@router.get("/stats")
async def get_stats():
    """Get summary statistics"""
    stats = card_service.get_summary_stats()

    return {
        "code": 200,
        "message": "success",
        "data": stats,
    }


@router.get("/search")
async def search_cards(q: str = Query(..., description="Search query")):
    """Search cards by name or bank"""
    cards = card_service.search_cards(q)

    return {
        "code": 200,
        "message": "success",
        "data": [card_to_response(card) for card in cards],
        "count": len(cards),
    }


# Import cards from savevia.app API format
class ImportRequest(BaseModel):
    data: list[dict]


@router.post("/import")
async def import_cards(request: ImportRequest):
    """Import cards from savevia.app API format"""
    try:
        cards = storage.save_cards_from_api(request.data)
        return {
            "code": 200,
            "message": f"Successfully imported {len(cards)} cards",
            "count": len(cards),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================
# Scraping API - Discover and scrape credit cards from banks
# ============================================================

@router.get("/scraper/banks")
async def get_supported_banks():
    """Get list of supported banks for scraping"""
    scraper = BankScraper()
    banks = []
    for bank, url in scraper.BANK_CARD_LISTINGS.items():
        banks.append({
            "name": bank,
            "listingUrl": url,
        })

    return {
        "code": 200,
        "message": "success",
        "data": banks,
        "playwrightAvailable": PLAYWRIGHT_AVAILABLE,
    }


class DiscoverRequest(BaseModel):
    bank: str


@router.post("/scraper/discover")
async def discover_bank_cards(request: DiscoverRequest):
    """Discover credit cards from a bank's website"""
    if not PLAYWRIGHT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Playwright not installed. Run: pip install playwright && playwright install"
        )

    scraper = BankScraper()
    try:
        cards = await scraper.discover_cards_for_bank(request.bank)

        # Save URLs to database
        for card in cards:
            database.save_bank_card_url(
                bank=request.bank,
                url=card.url,
                card_name=card.name,
            )

        return {
            "code": 200,
            "message": f"Discovered {len(cards)} cards",
            "data": [
                {
                    "bank": card.bank,
                    "name": card.name,
                    "url": card.url,
                }
                for card in cards
            ],
            "count": len(cards),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await scraper.close()


class ScrapeRequest(BaseModel):
    url: str
    bank: Optional[str] = None


@router.post("/scraper/scrape")
async def scrape_card_page(request: ScrapeRequest):
    """Scrape a credit card page and return analysis prompt"""
    if not PLAYWRIGHT_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Playwright not installed. Run: pip install playwright && playwright install"
        )

    scraper = BankScraper()
    try:
        page = await scraper.scrape_card_page(request.url)

        # Guess bank from URL if not provided
        bank = request.bank
        if not bank:
            url_lower = request.url.lower()
            if "bmo.com" in url_lower:
                bank = "BMO"
            elif "td.com" in url_lower:
                bank = "TD"
            elif "rbc" in url_lower:
                bank = "RBC"
            elif "cibc.com" in url_lower:
                bank = "CIBC"
            elif "scotiabank.com" in url_lower:
                bank = "Scotiabank"
            elif "americanexpress.com" in url_lower:
                bank = "AMEX"
            elif "tangerine.ca" in url_lower:
                bank = "Tangerine"
            elif "simplii.com" in url_lower:
                bank = "Simplii"
            elif "rogers" in url_lower:
                bank = "Rogers"
            elif "desjardins.com" in url_lower:
                bank = "Desjardins"
            elif "hsbc.ca" in url_lower:
                bank = "HSBC"
            elif "nbc.ca" in url_lower:
                bank = "National Bank"
            else:
                bank = "Unknown"

        # Generate analysis prompt for LLM
        prompt = create_analysis_prompt(
            page_content=page.text_content,
            bank=bank,
            url=request.url,
        )

        return {
            "code": 200,
            "message": "success",
            "data": {
                "url": request.url,
                "bank": bank,
                "title": page.title,
                "contentLength": len(page.text_content),
                "contentPreview": page.text_content[:2000],
                "analysisPrompt": prompt,
            },
        }
    finally:
        await scraper.close()


class SaveCardRequest(BaseModel):
    bank: str
    sourceUrl: str
    analysisResult: str  # JSON string from LLM analysis


@router.post("/scraper/save")
async def save_analyzed_card(request: SaveCardRequest):
    """Save a card from LLM analysis result"""
    try:
        analyzed = parse_llm_response(
            response_text=request.analysisResult,
            bank=request.bank,
            source_url=request.sourceUrl,
            raw_content="",
        )

        # Get next card ID
        stats = database.get_stats()
        next_id = stats.get("total_cards", 0) + 1

        # Convert to CreditCard and save
        card = analyzed.to_credit_card(card_id=next_id)
        card_id = database.save_card(card, source_url=request.sourceUrl)

        # Mark URL as scraped
        database.mark_url_scraped(request.sourceUrl)

        return {
            "code": 200,
            "message": "Card saved successfully",
            "data": {
                "cardId": card_id,
                "bank": card.bank,
                "name": card.name,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scraper/unscraped")
async def get_unscraped_urls(bank: Optional[str] = None):
    """Get URLs that haven't been scraped yet"""
    urls = database.get_unscraped_urls(bank)

    return {
        "code": 200,
        "message": "success",
        "data": urls,
        "count": len(urls),
    }


@router.get("/db/stats")
async def get_database_stats():
    """Get database statistics"""
    stats = database.get_stats()

    return {
        "code": 200,
        "message": "success",
        "data": stats,
    }


# ============================================================
# Agno Agent API - Automatic card collection using LLM
# ============================================================

from src.agents.card_collector_agent import CardCollectorAgent, LLMProvider
import json
from pathlib import Path


# ============================================================
# Scraped Card Images API - View scraped card images
# ============================================================

@router.get("/scraped-images")
async def get_scraped_images(bank: Optional[str] = None):
    """
    Get all scraped card images from the data/images directory.
    Prioritizes curated list, then falls back to scraped files.
    Returns images grouped by bank.
    """
    images_dir = Path(__file__).parent.parent.parent / "data" / "images"

    if not images_dir.exists():
        return {
            "code": 200,
            "message": "No scraped images found",
            "data": [],
            "count": 0,
        }

    all_images = []
    seen_ids = set()

    # First, load curated images (highest priority)
    curated_file = images_dir / "savevia_cards_curated.json"
    if curated_file.exists():
        try:
            with open(curated_file, "r", encoding="utf-8") as f:
                curated = json.load(f)
            for img in curated:
                if img.get("image_url"):
                    img["source"] = "curated"
                    all_images.append(img)
                    seen_ids.add(img.get("id"))
        except Exception as e:
            print(f"Error reading curated file: {e}")

    # Then load from scraped files for any missing cards
    for json_file in sorted(images_dir.glob("savevia_cards_*.json"), reverse=True):
        if json_file.name == "savevia_cards_curated.json":
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                images = json.load(f)

            for img in images:
                card_id = img.get("id")
                if card_id not in seen_ids and img.get("image_url"):
                    img["source"] = "scraped"
                    img["source_file"] = json_file.name
                    all_images.append(img)
                    seen_ids.add(card_id)

        except Exception as e:
            print(f"Error reading {json_file}: {e}")
            continue

    # Filter by bank if specified
    if bank:
        all_images = [img for img in all_images if img.get("bank", "").upper() == bank.upper()]

    # Group by bank
    banks_dict = {}
    for img in all_images:
        bank_name = img.get("bank", "Unknown")
        if bank_name not in banks_dict:
            banks_dict[bank_name] = []
        banks_dict[bank_name].append(img)

    # Convert to list format
    grouped_data = [
        {
            "bank": bank_name,
            "images": images,
            "count": len(images),
        }
        for bank_name, images in sorted(banks_dict.items())
    ]

    return {
        "code": 200,
        "message": "success",
        "data": grouped_data,
        "totalCount": len(all_images),
        "bankCount": len(grouped_data),
    }


@router.get("/scraped-images/files")
async def list_scraped_image_files():
    """List all scraped image JSON files"""
    images_dir = Path(__file__).parent.parent.parent / "data" / "images"

    if not images_dir.exists():
        return {
            "code": 200,
            "message": "No scraped images directory",
            "data": [],
        }

    files = []
    for json_file in sorted(images_dir.glob("*_images_*.json"), reverse=True):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                images = json.load(f)

            bank = json_file.stem.split("_images_")[0]
            timestamp = json_file.stem.split("_images_")[1] if "_images_" in json_file.stem else None

            files.append({
                "filename": json_file.name,
                "bank": bank,
                "timestamp": timestamp,
                "imageCount": len([i for i in images if i.get("image_url")]),
                "totalEntries": len(images),
            })
        except Exception as e:
            files.append({
                "filename": json_file.name,
                "error": str(e),
            })

    return {
        "code": 200,
        "message": "success",
        "data": files,
    }


@router.get("/agent/providers")
async def get_llm_providers():
    """Get list of supported LLM providers"""
    providers = [
        {
            "id": "volces",
            "name": "火山引擎 (默认)",
            "defaultModel": "deepseek-v3-1-250821",
            "envVar": "VOLCES_API_KEY",
            "isDefault": True,
        },
        {
            "id": "openai",
            "name": "OpenAI",
            "defaultModel": "gpt-4o",
            "envVar": "OPENAI_API_KEY",
        },
        {
            "id": "claude",
            "name": "Anthropic Claude",
            "defaultModel": "claude-sonnet-4-20250514",
            "envVar": "ANTHROPIC_API_KEY",
        },
        {
            "id": "gemini",
            "name": "Google Gemini",
            "defaultModel": "gemini-2.0-flash-001",
            "envVar": "GOOGLE_API_KEY",
        },
        {
            "id": "groq",
            "name": "Groq",
            "defaultModel": "llama-3.3-70b-versatile",
            "envVar": "GROQ_API_KEY",
        },
        {
            "id": "deepseek",
            "name": "DeepSeek",
            "defaultModel": "deepseek-chat",
            "envVar": "DEEPSEEK_API_KEY",
        },
        {
            "id": "ollama",
            "name": "Ollama (Local)",
            "defaultModel": "llama3.2:latest",
            "envVar": None,
        },
    ]

    return {
        "code": 200,
        "message": "success",
        "data": providers,
    }


@router.get("/agent/banks")
async def get_agent_supported_banks():
    """Get list of banks supported by the agent (from database)"""
    banks = database.get_all_banks(active_only=True)

    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": bank["id"],
                "name": bank["name"],
                "listingUrl": bank["cards_url"],
                "logoUrl": bank.get("logo_url"),
            }
            for bank in banks
        ],
    }


# ==================== Bank Management API ====================

class AddBankRequest(BaseModel):
    """Request to add a new bank"""
    name: str
    cardsUrl: str
    logoUrl: Optional[str] = None


class UpdateBankRequest(BaseModel):
    """Request to update a bank"""
    name: Optional[str] = None
    cardsUrl: Optional[str] = None
    logoUrl: Optional[str] = None
    isActive: Optional[bool] = None


@router.post("/banks")
async def add_bank(request: AddBankRequest):
    """Add a new bank for card collection"""
    # Check if bank already exists
    existing = database.get_bank_by_name(request.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"Bank '{request.name}' already exists")

    try:
        bank_id = database.add_bank(
            name=request.name,
            cards_url=request.cardsUrl,
            logo_url=request.logoUrl
        )
        return {
            "code": 200,
            "message": "Bank added successfully",
            "data": {
                "id": bank_id,
                "name": request.name,
                "cardsUrl": request.cardsUrl,
                "logoUrl": request.logoUrl,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/banks/{bank_id}")
async def update_bank(bank_id: int, request: UpdateBankRequest):
    """Update a bank's information"""
    existing = database.get_bank_by_id(bank_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Bank with ID {bank_id} not found")

    try:
        success = database.update_bank(
            bank_id=bank_id,
            name=request.name,
            cards_url=request.cardsUrl,
            logo_url=request.logoUrl,
            is_active=request.isActive
        )
        if success:
            updated = database.get_bank_by_id(bank_id)
            return {
                "code": 200,
                "message": "Bank updated successfully",
                "data": updated
            }
        else:
            return {"code": 200, "message": "No changes made", "data": existing}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/banks/{bank_id}")
async def delete_bank(bank_id: int):
    """Delete a bank"""
    existing = database.get_bank_by_id(bank_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Bank with ID {bank_id} not found")

    try:
        success = database.delete_bank(bank_id)
        if success:
            return {"code": 200, "message": "Bank deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete bank")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentCollectRequest(BaseModel):
    """Request to collect a card using Agno Agent"""
    url: str
    bank: Optional[str] = None
    provider: str = "volces"
    modelId: Optional[str] = None


@router.post("/agent/collect")
async def agent_collect_card(request: AgentCollectRequest):
    """
    Collect a single credit card using Agno Agent.

    This endpoint uses the configured LLM to automatically:
    1. Visit the card URL
    2. Extract card information
    3. Save to SQLite database
    """
    try:
        provider = LLMProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Supported: {CardCollectorAgent.get_supported_providers()}"
        )

    try:
        agent = CardCollectorAgent(
            provider=provider,
            model_id=request.modelId,
            database=database,
        )

        card = agent.collect_card_from_url(
            url=request.url,
            bank=request.bank,
        )

        return {
            "code": 200,
            "message": "Card collected successfully",
            "data": {
                "cardId": card.id,
                "bank": card.bank,
                "name": card.name,
                "cardType": card.card_type,
                "annualFee": float(card.annual_fee),
                "baseRewardRate": float(card.base_reward_rate),
                "noFxFee": card.no_fx_fee,
                "rewardRulesCount": len(card.reward_rules),
            },
        }
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependencies: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentCollectBankRequest(BaseModel):
    """Request to collect all cards from a bank"""
    bank: str
    provider: str = "volces"
    modelId: Optional[str] = None
    maxCards: Optional[int] = None


@router.post("/agent/collect-bank")
async def agent_collect_bank_cards(request: AgentCollectBankRequest):
    """
    Collect all credit cards from a bank using Agno Agent.

    This endpoint uses the configured LLM to automatically:
    1. Visit the bank's card listing page
    2. Discover all credit card URLs
    3. Visit each card page and extract information
    4. Save all cards to SQLite database
    """
    try:
        provider = LLMProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Supported: {CardCollectorAgent.get_supported_providers()}"
        )

    # Validate bank from database
    supported_banks = list(database.get_bank_card_listings().keys())
    if request.bank not in supported_banks:
        raise HTTPException(
            status_code=400,
            detail=f"Bank not supported. Supported: {supported_banks}"
        )

    try:
        agent = CardCollectorAgent(
            provider=provider,
            model_id=request.modelId,
            database=database,
        )

        cards = agent.collect_bank_cards(
            bank=request.bank,
            max_cards=request.maxCards,
        )

        return {
            "code": 200,
            "message": f"Collected {len(cards)} cards from {request.bank}",
            "data": [
                {
                    "cardId": card.id,
                    "bank": card.bank,
                    "name": card.name,
                    "annualFee": float(card.annual_fee),
                    "rewardRulesCount": len(card.reward_rules),
                }
                for card in cards
            ],
            "count": len(cards),
        }
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependencies: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentSearchRequest(BaseModel):
    """Request to search for bank cards"""
    bank: str
    provider: str = "volces"
    modelId: Optional[str] = None


@router.post("/agent/search")
async def agent_search_bank_cards(request: AgentSearchRequest):
    """
    Search for credit card URLs from a bank using web search.

    Uses DuckDuckGo to find official bank credit card pages.
    """
    try:
        provider = LLMProvider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Supported: {CardCollectorAgent.get_supported_providers()}"
        )

    try:
        agent = CardCollectorAgent(
            provider=provider,
            model_id=request.modelId,
            database=database,
        )

        results = agent.search_bank_cards(bank=request.bank)

        return {
            "code": 200,
            "message": "Search completed",
            "data": results,
        }
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Missing dependencies: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
