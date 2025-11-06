"""
User Configuration Manager
Manages user preferences, watchlists, and alerts
"""

from typing import List, Dict, Optional
from datetime import datetime

from database.db_manager import DatabaseManager
from database.models import Watchlist, Alert


class UserConfigManager:
    """User configuration manager"""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize user config manager"""
        self.db = db_manager

    # ==================== Watchlist Management ====================

    def create_watchlist(self, user_id: int, name: str, description: Optional[str] = None,
                        asset_symbols: Optional[List[str]] = None) -> Dict:
        """Create a new watchlist"""
        with self.db.get_session() as session:
            watchlist = Watchlist(
                user_id=user_id,
                name=name,
                description=description,
                asset_symbols=asset_symbols or []
            )
            session.add(watchlist)
            session.flush()
            session.refresh(watchlist)

            return self._watchlist_to_dict(watchlist)

    def get_user_watchlists(self, user_id: int) -> List[Dict]:
        """Get all watchlists for a user"""
        with self.db.get_session() as session:
            watchlists = session.query(Watchlist).filter(
                Watchlist.user_id == user_id
            ).all()

            return [self._watchlist_to_dict(w) for w in watchlists]

    def get_watchlist(self, watchlist_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific watchlist"""
        with self.db.get_session() as session:
            watchlist = session.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()

            return self._watchlist_to_dict(watchlist) if watchlist else None

    def update_watchlist(self, watchlist_id: int, user_id: int, **kwargs) -> Optional[Dict]:
        """Update a watchlist"""
        with self.db.get_session() as session:
            watchlist = session.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()

            if not watchlist:
                return None

            for key, value in kwargs.items():
                if hasattr(watchlist, key):
                    setattr(watchlist, key, value)

            session.flush()
            session.refresh(watchlist)

            return self._watchlist_to_dict(watchlist)

    def delete_watchlist(self, watchlist_id: int, user_id: int) -> bool:
        """Delete a watchlist"""
        with self.db.get_session() as session:
            result = session.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).delete()

            return result > 0

    def add_asset_to_watchlist(self, watchlist_id: int, user_id: int, asset_symbol: str) -> Optional[Dict]:
        """Add an asset to a watchlist"""
        with self.db.get_session() as session:
            watchlist = session.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()

            if not watchlist:
                return None

            if watchlist.asset_symbols is None:
                watchlist.asset_symbols = []

            if asset_symbol not in watchlist.asset_symbols:
                watchlist.asset_symbols = watchlist.asset_symbols + [asset_symbol]
                session.flush()
                session.refresh(watchlist)

            return self._watchlist_to_dict(watchlist)

    def remove_asset_from_watchlist(self, watchlist_id: int, user_id: int, asset_symbol: str) -> Optional[Dict]:
        """Remove an asset from a watchlist"""
        with self.db.get_session() as session:
            watchlist = session.query(Watchlist).filter(
                Watchlist.id == watchlist_id,
                Watchlist.user_id == user_id
            ).first()

            if not watchlist:
                return None

            if watchlist.asset_symbols and asset_symbol in watchlist.asset_symbols:
                symbols = watchlist.asset_symbols.copy()
                symbols.remove(asset_symbol)
                watchlist.asset_symbols = symbols
                session.flush()
                session.refresh(watchlist)

            return self._watchlist_to_dict(watchlist)

    # ==================== Alert Management ====================

    def create_alert(self, user_id: int, asset_symbol: str, alert_type: str,
                    target_value: float, message: Optional[str] = None) -> Dict:
        """Create a price alert"""
        with self.db.get_session() as session:
            alert = Alert(
                user_id=user_id,
                asset_symbol=asset_symbol,
                alert_type=alert_type,
                target_value=target_value,
                message=message
            )
            session.add(alert)
            session.flush()
            session.refresh(alert)

            return self._alert_to_dict(alert)

    def get_user_alerts(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all alerts for a user"""
        with self.db.get_session() as session:
            query = session.query(Alert).filter(Alert.user_id == user_id)

            if active_only:
                query = query.filter(Alert.is_active == True)

            alerts = query.all()
            return [self._alert_to_dict(a) for a in alerts]

    def update_alert(self, alert_id: int, user_id: int, **kwargs) -> Optional[Dict]:
        """Update an alert"""
        with self.db.get_session() as session:
            alert = session.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()

            if not alert:
                return None

            for key, value in kwargs.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)

            session.flush()
            session.refresh(alert)

            return self._alert_to_dict(alert)

    def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        with self.db.get_session() as session:
            result = session.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).delete()

            return result > 0

    def trigger_alert(self, alert_id: int) -> bool:
        """Mark an alert as triggered"""
        with self.db.get_session() as session:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()

            if not alert:
                return False

            alert.is_triggered = True
            alert.triggered_at = datetime.utcnow()
            alert.is_active = False

            session.flush()
            return True

    def check_alerts(self, user_id: int, asset_symbol: str, current_price: float) -> List[Dict]:
        """Check if any alerts should be triggered for an asset"""
        with self.db.get_session() as session:
            alerts = session.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.asset_symbol == asset_symbol,
                Alert.is_active == True
            ).all()

            triggered_alerts = []

            for alert in alerts:
                should_trigger = False

                if alert.alert_type == 'price_above' and current_price >= alert.target_value:
                    should_trigger = True
                elif alert.alert_type == 'price_below' and current_price <= alert.target_value:
                    should_trigger = True

                if should_trigger:
                    alert.is_triggered = True
                    alert.triggered_at = datetime.utcnow()
                    alert.is_active = False
                    triggered_alerts.append(self._alert_to_dict(alert))

            session.flush()

            return triggered_alerts

    # ==================== Helper Methods ====================

    @staticmethod
    def _watchlist_to_dict(watchlist: Watchlist) -> Dict:
        """Convert watchlist to dictionary"""
        return {
            "id": watchlist.id,
            "user_id": watchlist.user_id,
            "name": watchlist.name,
            "description": watchlist.description,
            "asset_symbols": watchlist.asset_symbols or [],
            "created_at": watchlist.created_at.isoformat() if watchlist.created_at else None,
            "updated_at": watchlist.updated_at.isoformat() if watchlist.updated_at else None
        }

    @staticmethod
    def _alert_to_dict(alert: Alert) -> Dict:
        """Convert alert to dictionary"""
        return {
            "id": alert.id,
            "user_id": alert.user_id,
            "asset_symbol": alert.asset_symbol,
            "alert_type": alert.alert_type,
            "target_value": alert.target_value,
            "is_active": alert.is_active,
            "is_triggered": alert.is_triggered,
            "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
            "message": alert.message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        }
