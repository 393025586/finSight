"""
finSight - Main Application
FastAPI backend for financial analysis platform
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import modules
from database.db_manager import DatabaseManager
from user_management.auth import AuthManager
from user_management.user_config import UserConfigManager
from data_fetchers import (
    AssetHistoryFetcher,
    AssetInfoFetcher,
    MacroMetricsFetcher,
    RealtimeFetcher,
    NewsFetcher
)
from metrics_calculator import MetricsCalculator
from visualization import Plotter
from ai_analysis import AIAnalyzer
from configs import config
from loguru import logger

# Initialize FastAPI app
app = FastAPI(
    title="finSight API",
    description="Asset Insight | Investment Journal",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
db = DatabaseManager()
auth_manager = AuthManager(db)
user_config_manager = UserConfigManager(db)

# Initialize fetchers
history_fetcher = AssetHistoryFetcher()
info_fetcher = AssetInfoFetcher()
macro_fetcher = MacroMetricsFetcher()
realtime_fetcher = RealtimeFetcher()
news_fetcher = NewsFetcher()

# Initialize calculator and analyzer
metrics_calculator = MetricsCalculator()
plotter = Plotter()
ai_analyzer = AIAnalyzer()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db.create_all_tables()
    logger.info("finSight API started successfully")


# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    identifier: str  # email or username
    password: str


class AssetAdd(BaseModel):
    symbol: str
    quantity: Optional[float] = 0
    average_cost: Optional[float] = None
    notes: Optional[str] = None


class NotebookEntry(BaseModel):
    title: str
    content: str
    entry_date: Optional[str] = None
    tags: Optional[List[str]] = None
    asset_symbols: Optional[List[str]] = None


class AlertCreate(BaseModel):
    asset_symbol: str
    alert_type: str  # price_above, price_below
    target_value: float
    message: Optional[str] = None


# ==================== Auth Dependency ====================

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = authorization.replace("Bearer ", "")
        user = auth_manager.validate_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# ==================== Authentication Routes ====================

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        result = auth_manager.register_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    try:
        result = auth_manager.login(
            identifier=credentials.identifier,
            password=credentials.password
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/api/auth/me")
async def get_me(current_user=Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }


# ==================== Asset Routes ====================

@app.get("/api/assets/search")
async def search_assets(q: str, market: Optional[str] = None, current_user=Depends(get_current_user)):
    """Search for assets"""
    assets = db.search_assets(q, market=market)
    return [{"id": a.id, "symbol": a.symbol, "name": a.name, "market": a.market} for a in assets]


@app.get("/api/assets/{symbol}/info")
async def get_asset_info(symbol: str, market: str = "US", current_user=Depends(get_current_user)):
    """Get asset information"""
    info = info_fetcher.fetch_asset_info(symbol, market)
    if not info:
        raise HTTPException(status_code=404, detail="Asset not found")
    return info


@app.get("/api/assets/{symbol}/history")
async def get_asset_history(symbol: str, market: str = "US", period: str = "1y",
                           current_user=Depends(get_current_user)):
    """Get historical price data"""
    df = history_fetcher.fetch_history(symbol, market, period=period)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No historical data found")

    return {
        "symbol": symbol,
        "data": df.to_dict(orient="records")
    }


@app.get("/api/assets/{symbol}/realtime")
async def get_realtime_price(symbol: str, market: str = "US", current_user=Depends(get_current_user)):
    """Get real-time price"""
    price = realtime_fetcher.fetch_realtime_price(symbol, market)
    if not price:
        raise HTTPException(status_code=404, detail="Price data not available")
    return price


@app.get("/api/assets/{symbol}/analysis")
async def analyze_asset(symbol: str, market: str = "US", period: str = "1y",
                       current_user=Depends(get_current_user)):
    """Get comprehensive asset analysis"""
    # Fetch data
    df = history_fetcher.fetch_history(symbol, market, period=period)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data available for analysis")

    # Calculate metrics
    prices = df.set_index('date')['close']
    metrics = metrics_calculator.calculate_all_metrics(prices)

    # Get asset info
    info = info_fetcher.fetch_asset_info(symbol, market)

    # Get news
    news = news_fetcher.fetch_stock_news(symbol, market, limit=10)

    # AI analysis
    ai_analysis = ai_analyzer.analyze_asset(symbol, info or {}, metrics, news)

    return {
        "symbol": symbol,
        "info": info,
        "metrics": metrics,
        "news": news,
        "ai_analysis": ai_analysis
    }


# ==================== User Portfolio Routes ====================

@app.get("/api/portfolio")
async def get_user_portfolio(current_user=Depends(get_current_user)):
    """Get user's portfolio"""
    user_assets = db.get_user_assets(current_user.id)

    portfolio = []
    for ua in user_assets:
        asset = db.get_asset_by_id(ua.asset_id)
        if asset:
            # Get latest price
            latest_price = db.get_latest_price(asset.id)

            portfolio.append({
                "id": ua.id,
                "symbol": asset.symbol,
                "name": asset.name,
                "market": asset.market,
                "quantity": ua.quantity,
                "average_cost": ua.average_cost,
                "current_price": latest_price.close if latest_price else None,
                "notes": ua.notes
            })

    return portfolio


@app.post("/api/portfolio")
async def add_to_portfolio(asset_data: AssetAdd, current_user=Depends(get_current_user)):
    """Add asset to portfolio"""
    # Check if asset exists, if not create it
    asset = db.get_asset_by_symbol(asset_data.symbol)

    if not asset:
        # Fetch asset info and create
        info = info_fetcher.fetch_asset_info(asset_data.symbol)
        if info:
            asset = db.create_asset(
                symbol=info['symbol'],
                name=info['name'],
                asset_type=info.get('asset_type', 'stock'),
                market=info.get('market', 'US'),
                sector=info.get('sector')
            )
        else:
            raise HTTPException(status_code=404, detail="Asset not found")

    # Add to user portfolio
    user_asset = db.add_user_asset(
        user_id=current_user.id,
        asset_id=asset.id,
        quantity=asset_data.quantity,
        average_cost=asset_data.average_cost,
        notes=asset_data.notes
    )

    return {"message": "Asset added to portfolio", "id": user_asset.id}


@app.delete("/api/portfolio/{asset_id}")
async def remove_from_portfolio(asset_id: int, current_user=Depends(get_current_user)):
    """Remove asset from portfolio"""
    success = db.delete_user_asset(current_user.id, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found in portfolio")
    return {"message": "Asset removed from portfolio"}


# ==================== Macro Metrics Routes ====================

@app.get("/api/macro/{country}")
async def get_macro_metrics(country: str, current_user=Depends(get_current_user)):
    """Get macroeconomic metrics for a country"""
    metrics = macro_fetcher.fetch_all_metrics(country)
    if not metrics:
        raise HTTPException(status_code=404, detail="No macro data available")

    latest_values = macro_fetcher.get_latest_values(country)

    return {
        "country": country,
        "latest_values": latest_values,
        "data": {k: v.to_dict(orient="records") for k, v in metrics.items()}
    }


@app.get("/api/macro/{country}/analysis")
async def analyze_macro_metrics(country: str, current_user=Depends(get_current_user)):
    """Get AI analysis of macro metrics"""
    latest_values = macro_fetcher.get_latest_values(country)

    if not latest_values:
        raise HTTPException(status_code=404, detail="No macro data available")

    analysis = ai_analyzer.analyze_macro_metrics(country, latest_values)

    return {
        "country": country,
        "metrics": latest_values,
        "analysis": analysis
    }


# ==================== News Routes ====================

@app.get("/api/news/market/{market}")
async def get_market_news(market: str, limit: int = 50, current_user=Depends(get_current_user)):
    """Get market news"""
    news = news_fetcher.fetch_market_news(market, limit)
    if not news:
        raise HTTPException(status_code=404, detail="No news available")
    return news


@app.get("/api/news/asset/{symbol}")
async def get_asset_news(symbol: str, market: str = "CN", limit: int = 20,
                        current_user=Depends(get_current_user)):
    """Get news for specific asset"""
    news = news_fetcher.fetch_and_analyze(symbol, market, limit)
    if not news:
        raise HTTPException(status_code=404, detail="No news available")
    return news


# ==================== Notebook Routes ====================

@app.get("/api/notebook")
async def get_notebook_entries(current_user=Depends(get_current_user)):
    """Get user's notebook entries"""
    entries = db.get_notebook_entries(current_user.id)
    return [{
        "id": e.id,
        "title": e.title,
        "content": e.content,
        "entry_date": e.entry_date.isoformat(),
        "tags": e.tags,
        "asset_symbols": e.asset_symbols,
        "created_at": e.created_at.isoformat() if e.created_at else None
    } for e in entries]


@app.post("/api/notebook")
async def create_notebook_entry(entry: NotebookEntry, current_user=Depends(get_current_user)):
    """Create a notebook entry"""
    entry_date = datetime.fromisoformat(entry.entry_date) if entry.entry_date else datetime.now()

    notebook = db.add_notebook_entry(
        user_id=current_user.id,
        title=entry.title,
        content=entry.content,
        entry_date=entry_date,
        tags=entry.tags,
        asset_symbols=entry.asset_symbols
    )

    return {"message": "Notebook entry created", "id": notebook.id}


@app.put("/api/notebook/{entry_id}")
async def update_notebook_entry(entry_id: int, entry: NotebookEntry,
                               current_user=Depends(get_current_user)):
    """Update a notebook entry"""
    updated = db.update_notebook_entry(
        entry_id=entry_id,
        title=entry.title,
        content=entry.content,
        tags=entry.tags,
        asset_symbols=entry.asset_symbols
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"message": "Entry updated"}


@app.delete("/api/notebook/{entry_id}")
async def delete_notebook_entry(entry_id: int, current_user=Depends(get_current_user)):
    """Delete a notebook entry"""
    success = db.delete_notebook_entry(entry_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted"}


# ==================== Daily Summary Route ====================

@app.get("/api/daily-summary")
async def get_daily_summary(date: Optional[str] = None, market: str = "GLOBAL",
                           current_user=Depends(get_current_user)):
    """Get daily market summary"""
    if date:
        summary_date = datetime.fromisoformat(date)
    else:
        summary_date = datetime.now().date()

    # Check if summary exists
    summary = db.get_daily_summary(summary_date, market)

    if not summary:
        # Generate new summary
        market_data = realtime_fetcher.fetch_market_overview(market)

        if market_data:
            ai_summary = ai_analyzer.generate_daily_summary(
                summary_date.isoformat(),
                market_data.get('indices', {}),
                {},  # Top movers would need additional data
                []   # News would need to be fetched
            )

            summary = db.save_daily_summary(
                summary_date=summary_date,
                market=market,
                summary=ai_summary or "Summary not available",
                ai_analysis=ai_summary
            )

    if summary:
        return {
            "date": summary.summary_date.isoformat(),
            "market": summary.market,
            "summary": summary.summary,
            "ai_analysis": summary.ai_analysis
        }
    else:
        raise HTTPException(status_code=404, detail="Summary not available")


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
