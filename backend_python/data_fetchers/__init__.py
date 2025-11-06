"""Data fetchers package"""
from .asset_history_fetcher import AssetHistoryFetcher
from .asset_info_fetcher import AssetInfoFetcher
from .macro_metrics_fetcher import MacroMetricsFetcher
from .realtime_fetcher import RealtimeFetcher
from .news_fetcher import NewsFetcher

__all__ = [
    'AssetHistoryFetcher',
    'AssetInfoFetcher',
    'MacroMetricsFetcher',
    'RealtimeFetcher',
    'NewsFetcher'
]
