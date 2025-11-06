"""
Database Models for finSight
SQLAlchemy ORM models for all entities
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    assets = relationship("UserAsset", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    notebooks = relationship("Notebook", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Asset(Base):
    """Asset master data (stocks, crypto, etc.)"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False, index=True)  # stock, crypto, commodity, forex, index
    market = Column(String(10), index=True)  # CN, HK, US
    sector = Column(String(100))
    currency = Column(String(10))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Metadata
    metadata_json = Column(JSON)  # Additional flexible data

    # Relationships
    price_history = relationship("PriceHistory", back_populates="asset", cascade="all, delete-orphan")
    user_assets = relationship("UserAsset", back_populates="asset", cascade="all, delete-orphan")
    news = relationship("News", back_populates="asset", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_asset_type_market', 'asset_type', 'market'),
    )

    def __repr__(self):
        return f"<Asset(symbol='{self.symbol}', name='{self.name}')>"


class PriceHistory(Base):
    """Historical price data for assets"""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)

    # OHLCV data
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Float)

    # Adjusted prices
    adj_close = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    asset = relationship("Asset", back_populates="price_history")

    __table_args__ = (
        UniqueConstraint('asset_id', 'date', name='uq_asset_date'),
        Index('idx_asset_date', 'asset_id', 'date'),
    )

    def __repr__(self):
        return f"<PriceHistory(asset_id={self.asset_id}, date={self.date}, close={self.close})>"


class UserAsset(Base):
    """User's asset portfolio"""
    __tablename__ = "user_assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Portfolio data
    quantity = Column(Float, default=0)
    average_cost = Column(Float)
    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="assets")
    asset = relationship("Asset", back_populates="user_assets")

    __table_args__ = (
        UniqueConstraint('user_id', 'asset_id', name='uq_user_asset'),
        Index('idx_user_asset', 'user_id', 'asset_id'),
    )

    def __repr__(self):
        return f"<UserAsset(user_id={self.user_id}, asset_id={self.asset_id})>"


class Watchlist(Base):
    """User's watchlist for assets"""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    asset_symbols = Column(JSON)  # List of asset symbols
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlists")

    def __repr__(self):
        return f"<Watchlist(user_id={self.user_id}, name='{self.name}')>"


class MacroMetric(Base):
    """Macroeconomic metrics"""
    __tablename__ = "macro_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_code = Column(String(50), nullable=False, index=True)  # GDP, CPI, UNEMPLOYMENT, etc.
    metric_name = Column(String(255), nullable=False)
    country = Column(String(10), nullable=False, index=True)  # CN, US, etc.
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    frequency = Column(String(20))  # daily, monthly, quarterly, yearly
    source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('metric_code', 'country', 'date', name='uq_metric_country_date'),
        Index('idx_metric_country_date', 'metric_code', 'country', 'date'),
    )

    def __repr__(self):
        return f"<MacroMetric(code='{self.metric_code}', country='{self.country}', date={self.date})>"


class PoliticalEvent(Base):
    """Political events and policy changes"""
    __tablename__ = "political_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    event_type = Column(String(50), index=True)  # policy, election, trade, conflict, etc.
    country = Column(String(10), index=True)
    impact_level = Column(String(20))  # low, medium, high
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(255))
    source_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PoliticalEvent(title='{self.title}', date={self.event_date})>"


class News(Base):
    """Financial news articles"""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)  # Null for general market news
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(100))
    source_url = Column(String(500), unique=True)
    author = Column(String(255))
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    sentiment = Column(String(20))  # positive, negative, neutral
    relevance_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    asset = relationship("Asset", back_populates="news")

    __table_args__ = (
        Index('idx_asset_published', 'asset_id', 'published_at'),
    )

    def __repr__(self):
        return f"<News(title='{self.title[:50]}...', published={self.published_at})>"


class Notebook(Base):
    """User's daily memo and trade journal"""
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False, index=True)
    tags = Column(JSON)  # List of tags
    asset_symbols = Column(JSON)  # Related asset symbols
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="notebooks")

    __table_args__ = (
        Index('idx_user_entry_date', 'user_id', 'entry_date'),
    )

    def __repr__(self):
        return f"<Notebook(user_id={self.user_id}, title='{self.title}', date={self.entry_date})>"


class Alert(Base):
    """Price alerts and notifications"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_symbol = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # price_above, price_below, change_percent, etc.
    target_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime(timezone=True))
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="alerts")

    __table_args__ = (
        Index('idx_user_symbol_active', 'user_id', 'asset_symbol', 'is_active'),
    )

    def __repr__(self):
        return f"<Alert(user_id={self.user_id}, symbol='{self.asset_symbol}', type='{self.alert_type}')>"


class CalculatedMetric(Base):
    """Pre-calculated financial metrics for performance"""
    __tablename__ = "calculated_metrics"

    id = Column(Integer, primary_key=True, index=True)
    asset_symbol = Column(String(50), nullable=False, index=True)
    calculation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_days = Column(Integer, nullable=False)  # 30, 90, 252, etc.

    # Performance metrics
    returns = Column(Float)
    cumulative_returns = Column(Float)
    annualized_returns = Column(Float)

    # Risk metrics
    volatility = Column(Float)
    beta = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)

    # Additional metrics
    var_95 = Column(Float)  # Value at Risk 95%
    cvar_95 = Column(Float)  # Conditional VaR

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('asset_symbol', 'calculation_date', 'period_days', name='uq_metric_symbol_date_period'),
        Index('idx_symbol_date_period', 'asset_symbol', 'calculation_date', 'period_days'),
    )

    def __repr__(self):
        return f"<CalculatedMetric(symbol='{self.asset_symbol}', date={self.calculation_date}, period={self.period_days})>"


class AssetCorrelation(Base):
    """Asset correlation matrix for portfolio analysis"""
    __tablename__ = "asset_correlations"

    id = Column(Integer, primary_key=True, index=True)
    asset_symbol_1 = Column(String(50), nullable=False, index=True)
    asset_symbol_2 = Column(String(50), nullable=False, index=True)
    calculation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_days = Column(Integer, nullable=False)
    correlation = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('asset_symbol_1', 'asset_symbol_2', 'calculation_date', 'period_days',
                        name='uq_corr_symbols_date_period'),
        Index('idx_symbols_date', 'asset_symbol_1', 'asset_symbol_2', 'calculation_date'),
    )

    def __repr__(self):
        return f"<AssetCorrelation({self.asset_symbol_1}-{self.asset_symbol_2}, corr={self.correlation})>"


class DailyMarketSummary(Base):
    """Daily market summary generated by AI"""
    __tablename__ = "daily_market_summaries"

    id = Column(Integer, primary_key=True, index=True)
    summary_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    market = Column(String(10), nullable=False)  # CN, HK, US, GLOBAL

    # Summary content
    title = Column(String(500))
    summary = Column(Text, nullable=False)
    key_events = Column(JSON)  # List of key events
    top_gainers = Column(JSON)  # List of top gainers
    top_losers = Column(JSON)  # List of top losers
    sector_performance = Column(JSON)  # Sector performance data

    # AI-generated insights
    ai_analysis = Column(Text)
    sentiment = Column(String(20))  # bullish, bearish, neutral

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DailyMarketSummary(date={self.summary_date}, market='{self.market}')>"
