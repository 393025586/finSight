"""
Database Manager
Handles all database connections and CRUD operations
"""

from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os

from .models import (
    Base, User, Asset, PriceHistory, UserAsset, Watchlist,
    MacroMetric, PoliticalEvent, News, Notebook, Alert,
    CalculatedMetric, AssetCorrelation, DailyMarketSummary
)


class DatabaseManager:
    """Database manager for all CRUD operations"""

    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./finsight.db")

        # SQLite specific configuration
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(database_url, pool_pre_ping=True)

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_all_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_all_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== User Operations ====================

    def create_user(self, email: str, username: str, password_hash: str) -> User:
        """Create a new user"""
        with self.get_session() as session:
            user = User(email=email, username=username, password_hash=password_hash)
            session.add(user)
            session.flush()
            session.refresh(user)
            # Extract data before session closes
            user_id = user.id
            user_email = user.email
            user_username = user.username
            user_created_at = user.created_at

        # Create detached user object with data
        detached_user = User(
            email=user_email,
            username=user_username,
            password_hash=password_hash
        )
        detached_user.id = user_id
        detached_user.created_at = user_created_at
        return detached_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with self.get_session() as session:
            user = session.query(User).filter(User.email == email).first()
            if user:
                detached = User(email=user.email, username=user.username, password_hash=user.password_hash)
                detached.id = user.id
                detached.created_at = user.created_at
                detached.is_active = user.is_active
                return detached
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                detached = User(email=user.email, username=user.username, password_hash=user.password_hash)
                detached.id = user.id
                detached.created_at = user.created_at
                detached.is_active = user.is_active
                return detached
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                detached = User(email=user.email, username=user.username, password_hash=user.password_hash)
                detached.id = user.id
                detached.created_at = user.created_at
                detached.is_active = user.is_active
                return detached
            return None

    # ==================== Asset Operations ====================

    def create_asset(self, symbol: str, name: str, asset_type: str, **kwargs) -> Asset:
        """Create a new asset"""
        with self.get_session() as session:
            asset = Asset(symbol=symbol, name=name, asset_type=asset_type, **kwargs)
            session.add(asset)
            session.flush()
            session.refresh(asset)
            return asset

    def get_asset_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol"""
        with self.get_session() as session:
            return session.query(Asset).filter(Asset.symbol == symbol).first()

    def get_asset_by_id(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID"""
        with self.get_session() as session:
            return session.query(Asset).filter(Asset.id == asset_id).first()

    def search_assets(self, query: str, market: Optional[str] = None, asset_type: Optional[str] = None) -> List[Asset]:
        """Search assets by name or symbol"""
        with self.get_session() as session:
            q = session.query(Asset).filter(
                or_(
                    Asset.symbol.ilike(f"%{query}%"),
                    Asset.name.ilike(f"%{query}%")
                )
            )
            if market:
                q = q.filter(Asset.market == market)
            if asset_type:
                q = q.filter(Asset.asset_type == asset_type)
            return q.limit(50).all()

    def get_all_assets(self, asset_type: Optional[str] = None, market: Optional[str] = None) -> List[Asset]:
        """Get all assets with optional filters"""
        with self.get_session() as session:
            q = session.query(Asset)
            if asset_type:
                q = q.filter(Asset.asset_type == asset_type)
            if market:
                q = q.filter(Asset.market == market)
            return q.all()

    # ==================== Price History Operations ====================

    def add_price_history(self, asset_id: int, date: datetime, close: float, **kwargs) -> PriceHistory:
        """Add price history record"""
        with self.get_session() as session:
            # Check if record exists
            existing = session.query(PriceHistory).filter(
                and_(PriceHistory.asset_id == asset_id, PriceHistory.date == date)
            ).first()

            if existing:
                # Update existing record
                for key, value in kwargs.items():
                    setattr(existing, key, value)
                existing.close = close
                session.flush()
                session.refresh(existing)
                return existing
            else:
                # Create new record
                price = PriceHistory(asset_id=asset_id, date=date, close=close, **kwargs)
                session.add(price)
                session.flush()
                session.refresh(price)
                return price

    def bulk_add_price_history(self, price_records: List[Dict[str, Any]]) -> int:
        """Bulk add price history records"""
        with self.get_session() as session:
            for record in price_records:
                price = PriceHistory(**record)
                session.merge(price)  # Merge will insert or update
            session.flush()
            return len(price_records)

    def get_price_history(self, asset_id: int, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None, limit: int = 1000) -> List[PriceHistory]:
        """Get price history for an asset"""
        with self.get_session() as session:
            q = session.query(PriceHistory).filter(PriceHistory.asset_id == asset_id)

            if start_date:
                q = q.filter(PriceHistory.date >= start_date)
            if end_date:
                q = q.filter(PriceHistory.date <= end_date)

            return q.order_by(PriceHistory.date.desc()).limit(limit).all()

    def get_latest_price(self, asset_id: int) -> Optional[PriceHistory]:
        """Get latest price for an asset"""
        with self.get_session() as session:
            return session.query(PriceHistory).filter(
                PriceHistory.asset_id == asset_id
            ).order_by(PriceHistory.date.desc()).first()

    # ==================== User Asset Operations ====================

    def add_user_asset(self, user_id: int, asset_id: int, **kwargs) -> UserAsset:
        """Add asset to user's portfolio"""
        with self.get_session() as session:
            # Check if exists
            existing = session.query(UserAsset).filter(
                and_(UserAsset.user_id == user_id, UserAsset.asset_id == asset_id)
            ).first()

            if existing:
                # Update existing
                for key, value in kwargs.items():
                    setattr(existing, key, value)
                session.flush()
                session.refresh(existing)
                return existing
            else:
                # Create new
                user_asset = UserAsset(user_id=user_id, asset_id=asset_id, **kwargs)
                session.add(user_asset)
                session.flush()
                session.refresh(user_asset)
                return user_asset

    def get_user_assets(self, user_id: int) -> List[UserAsset]:
        """Get all assets for a user"""
        with self.get_session() as session:
            return session.query(UserAsset).filter(UserAsset.user_id == user_id).all()

    def delete_user_asset(self, user_id: int, asset_id: int) -> bool:
        """Delete asset from user's portfolio"""
        with self.get_session() as session:
            result = session.query(UserAsset).filter(
                and_(UserAsset.user_id == user_id, UserAsset.asset_id == asset_id)
            ).delete()
            return result > 0

    # ==================== Macro Metrics Operations ====================

    def add_macro_metric(self, metric_code: str, metric_name: str, country: str,
                        date: datetime, value: float, **kwargs) -> MacroMetric:
        """Add macroeconomic metric"""
        with self.get_session() as session:
            metric = MacroMetric(
                metric_code=metric_code,
                metric_name=metric_name,
                country=country,
                date=date,
                value=value,
                **kwargs
            )
            session.merge(metric)
            session.flush()
            return metric

    def get_macro_metrics(self, metric_code: str, country: str,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[MacroMetric]:
        """Get macro metrics"""
        with self.get_session() as session:
            q = session.query(MacroMetric).filter(
                and_(MacroMetric.metric_code == metric_code, MacroMetric.country == country)
            )
            if start_date:
                q = q.filter(MacroMetric.date >= start_date)
            if end_date:
                q = q.filter(MacroMetric.date <= end_date)
            return q.order_by(MacroMetric.date.desc()).all()

    # ==================== News Operations ====================

    def add_news(self, title: str, published_at: datetime, **kwargs) -> News:
        """Add news article"""
        with self.get_session() as session:
            news = News(title=title, published_at=published_at, **kwargs)
            session.add(news)
            session.flush()
            session.refresh(news)
            return news

    def get_news(self, asset_id: Optional[int] = None, limit: int = 50) -> List[News]:
        """Get news articles"""
        with self.get_session() as session:
            q = session.query(News)
            if asset_id:
                q = q.filter(News.asset_id == asset_id)
            return q.order_by(News.published_at.desc()).limit(limit).all()

    # ==================== Notebook Operations ====================

    def add_notebook_entry(self, user_id: int, title: str, content: str,
                          entry_date: datetime, **kwargs) -> Notebook:
        """Add notebook entry"""
        with self.get_session() as session:
            notebook = Notebook(
                user_id=user_id,
                title=title,
                content=content,
                entry_date=entry_date,
                **kwargs
            )
            session.add(notebook)
            session.flush()
            session.refresh(notebook)
            return notebook

    def get_notebook_entries(self, user_id: int, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> List[Notebook]:
        """Get notebook entries"""
        with self.get_session() as session:
            q = session.query(Notebook).filter(Notebook.user_id == user_id)
            if start_date:
                q = q.filter(Notebook.entry_date >= start_date)
            if end_date:
                q = q.filter(Notebook.entry_date <= end_date)
            return q.order_by(Notebook.entry_date.desc()).all()

    def update_notebook_entry(self, entry_id: int, **kwargs) -> Optional[Notebook]:
        """Update notebook entry"""
        with self.get_session() as session:
            entry = session.query(Notebook).filter(Notebook.id == entry_id).first()
            if entry:
                for key, value in kwargs.items():
                    setattr(entry, key, value)
                session.flush()
                session.refresh(entry)
            return entry

    def delete_notebook_entry(self, entry_id: int, user_id: int) -> bool:
        """Delete notebook entry"""
        with self.get_session() as session:
            result = session.query(Notebook).filter(
                and_(Notebook.id == entry_id, Notebook.user_id == user_id)
            ).delete()
            return result > 0

    # ==================== Calculated Metrics Operations ====================

    def save_calculated_metrics(self, asset_symbol: str, calculation_date: datetime,
                               period_days: int, metrics: Dict[str, float]) -> CalculatedMetric:
        """Save calculated financial metrics"""
        with self.get_session() as session:
            calc_metric = CalculatedMetric(
                asset_symbol=asset_symbol,
                calculation_date=calculation_date,
                period_days=period_days,
                **metrics
            )
            session.merge(calc_metric)
            session.flush()
            return calc_metric

    def get_calculated_metrics(self, asset_symbol: str, period_days: int) -> Optional[CalculatedMetric]:
        """Get latest calculated metrics"""
        with self.get_session() as session:
            return session.query(CalculatedMetric).filter(
                and_(
                    CalculatedMetric.asset_symbol == asset_symbol,
                    CalculatedMetric.period_days == period_days
                )
            ).order_by(CalculatedMetric.calculation_date.desc()).first()

    # ==================== Daily Summary Operations ====================

    def save_daily_summary(self, summary_date: datetime, market: str, **kwargs) -> DailyMarketSummary:
        """Save daily market summary"""
        with self.get_session() as session:
            summary = DailyMarketSummary(
                summary_date=summary_date,
                market=market,
                **kwargs
            )
            session.merge(summary)
            session.flush()
            return summary

    def get_daily_summary(self, date: datetime, market: str = "GLOBAL") -> Optional[DailyMarketSummary]:
        """Get daily market summary"""
        with self.get_session() as session:
            return session.query(DailyMarketSummary).filter(
                and_(
                    DailyMarketSummary.summary_date == date,
                    DailyMarketSummary.market == market
                )
            ).first()
