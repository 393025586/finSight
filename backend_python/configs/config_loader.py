"""
Configuration Loader
Loads and manages YAML configuration files
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Configuration loader for YAML files"""

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration loader"""
        if config_dir is None:
            # Default to configs directory
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)

        self._global_config = None
        self._asset_list = None

    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file"""
        file_path = self.config_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def global_config(self) -> Dict[str, Any]:
        """Get global configuration (cached)"""
        if self._global_config is None:
            self._global_config = self.load_yaml('global_config.yaml')
        return self._global_config

    @property
    def asset_list(self) -> Dict[str, Any]:
        """Get asset list configuration (cached)"""
        if self._asset_list is None:
            self._asset_list = self.load_yaml('asset_list.yaml')
        return self._asset_list

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key (e.g., 'app.name')"""
        keys = key.split('.')
        value = self.global_config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_market_config(self, market_code: str) -> Optional[Dict[str, Any]]:
        """Get market configuration by code (CN, HK, US)"""
        markets = self.get('markets.supported', [])
        for market in markets:
            if market.get('code') == market_code:
                return market
        return None

    def get_risk_free_rate(self, market_code: str) -> float:
        """Get risk-free rate for a market"""
        return self.get(f'metrics.risk_free_rate.{market_code}', 0.03)

    def get_ai_provider_config(self, provider: str = 'gemini') -> Optional[Dict[str, Any]]:
        """Get AI provider configuration"""
        providers = self.get('ai.providers', [])
        for p in providers:
            if p.get('name') == provider and p.get('enabled'):
                return p
        return None

    def get_popular_assets(self, market: str) -> list:
        """Get popular assets for a market"""
        market_key_map = {
            'CN': 'china_a_share',
            'HK': 'hong_kong',
            'US': 'us_stocks'
        }

        market_key = market_key_map.get(market)
        if not market_key:
            return []

        assets_data = self.asset_list.get(market_key, {})
        popular = assets_data.get('popular_stocks', [])
        indices = assets_data.get('indices', [])

        return indices + popular

    def reload(self):
        """Reload all configurations"""
        self._global_config = None
        self._asset_list = None


# Global config instance
config = ConfigLoader()
