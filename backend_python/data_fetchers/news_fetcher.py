"""
News Fetcher
Fetches financial news from various sources
"""

import akshare as ak
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from loguru import logger


class NewsFetcher:
    """Fetch financial news"""

    def __init__(self):
        """Initialize news fetcher"""
        pass

    def fetch_stock_news(self, symbol: str, market: str = "CN", limit: int = 20) -> Optional[List[Dict]]:
        """
        Fetch news for a specific stock

        Args:
            symbol: Stock symbol
            market: Market code (CN, HK, US)
            limit: Maximum number of news articles

        Returns:
            List of news dictionaries
        """
        try:
            if market == "CN":
                return self._fetch_china_stock_news(symbol, limit)
            else:
                logger.warning(f"News fetching for market {market} not yet implemented")
                return None

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return None

    def _fetch_china_stock_news(self, symbol: str, limit: int = 20) -> Optional[List[Dict]]:
        """Fetch news for China A-share stocks"""
        try:
            # Get stock news using akshare
            df = ak.stock_news_em(symbol=symbol)

            if df is None or df.empty:
                return None

            news_list = []

            for idx, row in df.head(limit).iterrows():
                news_item = {
                    "title": row.get('新闻标题', ''),
                    "content": row.get('新闻内容', ''),
                    "source": row.get('文章来源', 'Unknown'),
                    "published_at": row.get('发布时间', datetime.now().isoformat()),
                    "url": row.get('新闻链接', ''),
                }

                # Convert published_at to ISO format if it's a datetime
                if isinstance(news_item['published_at'], pd.Timestamp):
                    news_item['published_at'] = news_item['published_at'].isoformat()

                news_list.append(news_item)

            return news_list

        except Exception as e:
            logger.error(f"Error fetching China stock news for {symbol}: {str(e)}")
            return None

    def fetch_market_news(self, market: str = "CN", limit: int = 50) -> Optional[List[Dict]]:
        """
        Fetch general market news

        Args:
            market: Market code (CN, HK, US)
            limit: Maximum number of news articles

        Returns:
            List of news dictionaries
        """
        try:
            if market == "CN":
                return self._fetch_china_market_news(limit)
            else:
                logger.warning(f"Market news for {market} not yet implemented")
                return None

        except Exception as e:
            logger.error(f"Error fetching market news for {market}: {str(e)}")
            return None

    def _fetch_china_market_news(self, limit: int = 50) -> Optional[List[Dict]]:
        """Fetch general China market news"""
        try:
            # Get financial news from Sina Finance
            df = ak.stock_zh_a_alerts_cls()

            if df is None or df.empty:
                return None

            news_list = []

            for idx, row in df.head(limit).iterrows():
                news_item = {
                    "title": row.get('title', ''),
                    "content": row.get('content', ''),
                    "source": "Sina Finance",
                    "published_at": row.get('datetime', datetime.now().isoformat()),
                }

                if isinstance(news_item['published_at'], pd.Timestamp):
                    news_item['published_at'] = news_item['published_at'].isoformat()

                news_list.append(news_item)

            return news_list

        except Exception as e:
            logger.error(f"Error fetching China market news: {str(e)}")
            # Try alternative source
            try:
                df = ak.stock_notice_report()
                if df is not None and not df.empty:
                    news_list = []
                    for idx, row in df.head(limit).iterrows():
                        news_item = {
                            "title": row.get('公告标题', ''),
                            "source": "East Money",
                            "published_at": row.get('公告日期', datetime.now().isoformat()),
                        }
                        news_list.append(news_item)
                    return news_list
            except:
                pass

            return None

    def fetch_sector_news(self, sector: str, market: str = "CN", limit: int = 20) -> Optional[List[Dict]]:
        """
        Fetch news for a specific sector

        Args:
            sector: Sector name
            market: Market code
            limit: Maximum number of news articles

        Returns:
            List of news dictionaries
        """
        # This would require sector-specific news APIs
        # For now, return market news with sector filter
        logger.info(f"Fetching sector news for {sector} in {market}")
        return self.fetch_market_news(market, limit)

    def fetch_top_headlines(self, market: str = "CN", limit: int = 10) -> Optional[List[Dict]]:
        """
        Fetch top headlines for a market

        Args:
            market: Market code
            limit: Maximum number of headlines

        Returns:
            List of headline dictionaries
        """
        return self.fetch_market_news(market, limit)

    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of news text (basic implementation)

        Args:
            text: News text

        Returns:
            Sentiment ('positive', 'negative', 'neutral')
        """
        # Simple keyword-based sentiment analysis
        positive_keywords = ['上涨', '增长', '利好', '突破', '创新高', '盈利', '收益']
        negative_keywords = ['下跌', '下降', '利空', '亏损', '风险', '警告', '调查']

        text_lower = text.lower()

        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def fetch_and_analyze(self, symbol: str, market: str = "CN", limit: int = 20) -> Optional[List[Dict]]:
        """
        Fetch news and add sentiment analysis

        Args:
            symbol: Stock symbol
            market: Market code
            limit: Maximum number of news articles

        Returns:
            List of news dictionaries with sentiment
        """
        news_list = self.fetch_stock_news(symbol, market, limit)

        if news_list:
            for news_item in news_list:
                text = f"{news_item.get('title', '')} {news_item.get('content', '')}"
                news_item['sentiment'] = self.analyze_sentiment(text)

        return news_list
