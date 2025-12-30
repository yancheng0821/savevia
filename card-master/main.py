"""
Card Master - Credit Card Rewards Ranking Tool
Main FastAPI application entry point.

Usage:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000 in your browser.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Fix asyncio nested event loop issue for Crawl4ai in FastAPI
# 必须在 import uvicorn 之前禁用 uvloop
import asyncio
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

import nest_asyncio
nest_asyncio.apply()

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api import router as api_router


# Create FastAPI app
app = FastAPI(
    title="Card Master",
    description="Credit Card Rewards Ranking Tool - 信用卡返现排行工具",
    version="1.0.0",
)

# Include API router
app.include_router(api_router)

# Setup templates
templates_dir = Path(__file__).parent / "src" / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Static files (if needed)
static_dir = Path(__file__).parent / "src" / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main frontend page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "card-master"}


# Startup event - load sample data if no data exists
@app.on_event("startup")
async def startup_event():
    """Load sample data on startup if no data file exists"""
    from src.services.storage import CardStorage

    storage = CardStorage()
    data_file = storage.cards_file

    if not data_file.exists():
        print("No data file found. Please import data via POST /api/import")
        print("Or run: python scripts/import_savevia_data.py")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
