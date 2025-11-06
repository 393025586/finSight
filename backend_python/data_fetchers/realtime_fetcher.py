"""
Realtime Fetcher
Fetches real-time or latest price data for assets
"""

import yfinance as yf
import akshare as ak
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger


class RealtimeFetcher:
    """Fetch real-time asset prices"""

    def __init__(self):
        """Initialize realtime fetcher"""
        pass

    def fetch_realtime_price(self, symbol: str, market: str = "US") -> Optional[Dict]:
        """
        Fetch real-time or latest price for an asset

        Args:
            symbol: Asset symbol
            market: Market code (CN, HK, US)

        Returns:
            Dictionary with price information
        """
        try:
            if market == "CN":
                return self._fetch_china_realtime(symbol)
            elif market == "HK":
                return self._fetch_hong_kong_realtime(symbol)
            else:
                return self._fetch_yfinance_realtime(symbol)

        except Exception as e:
            logger.error(f"Error fetching realtime price for {symbol}: {str(e)}")
            return None

    def _fetch_china_realtime(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time price for China A-share stocks"""
        try:
            # Get real-time quote using akshare
            df = ak.stock_zh_a_spot_em()

            if df is None or df.empty:
                return None

            # Find the stock
            stock_data = df[df['代码'] == symbol]

            if stock_data.empty:
                logger.warning(f"Stock {symbol} not found in realtime data")
                return None

            row = stock_data.iloc[0]

            result = {
                "symbol": symbol,
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌额']),
                "change_percent": float(row['涨跌幅']),
                "open": float(row['今开']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "volume": float(row['成交量']),
                "amount": float(row['成交额']),
                "timestamp": datetime.now().isoformat(),
                "market": "CN",
                "currency": "CNY"
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching China realtime for {symbol}: {str(e)}")
            return None

    def _fetch_hong_kong_realtime(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time price for Hong Kong stocks"""
        try:
            # Format symbol for yfinance
            if not symbol.endswith(".HK"):
                formatted_symbol = symbol.lstrip('0') + ".HK"
            else:
                formatted_symbol = symbol

            return self._fetch_yfinance_realtime(formatted_symbol)

        except Exception as e:
            logger.error(f"Error fetching Hong Kong realtime for {symbol}: {str(e)}")
            return None

    def _fetch_yfinance_realtime(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time price using yfinance"""
        try:
            ticker = yf.Ticker(symbol)

            # Get fast info (real-time data)
            info = ticker.fast_info if hasattr(ticker, 'fast_info') else ticker.info

            # Get latest price data
            hist = ticker.history(period="1d", interval="1m")

            if hist.empty:
                # Fallback to daily data
                hist = ticker.history(period="1d")

            if hist.empty:
                logger.warning(f"No price data available for {symbol}")
                return None

            latest = hist.iloc[-1]

            # Calculate change
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                current_price = latest['Close']
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100
            else:
                change = 0
                change_percent = 0

            result = {
                "symbol": symbol,
                "price": float(latest['Close']),
                "change": float(change),
                "change_percent": float(change_percent),
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "volume": float(latest['Volume']),
                "timestamp": hist.index[-1].isoformat(),
                "currency": info.get('currency', 'USD') if isinstance(info, dict) else 'USD'
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching yfinance realtime for {symbol}: {str(e)}")
            return None

    def fetch_multiple_realtime(self, symbols: List[str], market: str = "US") -> Dict[str, Dict]:
        """
        Fetch real-time prices for multiple symbols

        Args:
            symbols: List of symbols
            market: Market code

        Returns:
            Dictionary mapping symbol to price data
        """
        results = {}

        for symbol in symbols:
            data = self.fetch_realtime_price(symbol, market)
            if data:
                results[symbol] = data

        return results

    def fetch_market_overview(self, market: str = "US") -> Optional[Dict]:
        """
        Fetch market overview/indices

        Args:
            market: Market code

        Returns:
            Dictionary with market indices data
        """
        try:
            if market == "CN":
                indices = ["000001", "399001", "399006"]  # 上证, 深成, 创业板
                market_name = "China"
            elif market == "HK":
                indices = ["^HSI"]  # Hang Seng
                market_name = "Hong Kong"
            elif market == "US":
                indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow, Nasdaq
                market_name = "United States"
            else:
                return None

            overview = {
                "market": market,
                "market_name": market_name,
                "indices": {}
            }

            for index in indices:
                data = self.fetch_realtime_price(index, market)
                if data:
                    overview["indices"][index] = data

            return overview

        except Exception as e:
            logger.error(f"Error fetching market overview for {market}: {str(e)}")
            return None
