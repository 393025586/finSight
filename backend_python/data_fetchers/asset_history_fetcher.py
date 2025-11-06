"""
Asset History Fetcher
Fetches historical price data for assets from various sources
"""

import pandas as pd
import yfinance as yf
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional, Dict
import time
from loguru import logger


class AssetHistoryFetcher:
    """Fetch historical asset price data"""

    def __init__(self):
        """Initialize asset history fetcher"""
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)

    def fetch_history(self, symbol: str, market: str = "US",
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for an asset

        Args:
            symbol: Asset symbol
            market: Market code (CN, HK, US)
            start_date: Start date for historical data
            end_date: End date for historical data
            period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, adj_close
        """
        # Check cache
        cache_key = f"{symbol}_{market}_{start_date}_{end_date}_{period}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Returning cached data for {symbol}")
                return cached_data

        try:
            if market == "CN":
                df = self._fetch_china_a_share(symbol, start_date, end_date)
            elif market == "HK":
                df = self._fetch_hong_kong(symbol, start_date, end_date)
            elif market in ["US", "CRYPTO", "FOREX", "COMMODITY"]:
                df = self._fetch_yfinance(symbol, start_date, end_date, period)
            else:
                logger.warning(f"Unknown market: {market}, defaulting to yfinance")
                df = self._fetch_yfinance(symbol, start_date, end_date, period)

            if df is not None and not df.empty:
                # Cache the result
                self.cache[cache_key] = (df, datetime.now())
                logger.info(f"Successfully fetched {len(df)} records for {symbol}")
                return df
            else:
                logger.warning(f"No data returned for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {str(e)}")
            return None

    def _fetch_china_a_share(self, symbol: str, start_date: Optional[datetime],
                            end_date: Optional[datetime]) -> Optional[pd.DataFrame]:
        """Fetch China A-share data using akshare"""
        try:
            # Format dates for akshare
            if start_date is None:
                start_date = datetime.now() - timedelta(days=365)
            if end_date is None:
                end_date = datetime.now()

            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")

            # Fetch data using akshare
            # akshare expects symbol format like "sh600519" or "sz000858"
            if symbol.startswith("6"):
                ak_symbol = f"sh{symbol}"
            else:
                ak_symbol = f"sz{symbol}"

            df = ak.stock_zh_a_hist(symbol=ak_symbol, start_date=start_str,
                                   end_date=end_str, adjust="qfq")

            if df is None or df.empty:
                return None

            # Rename columns to standard format
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            }

            df = df.rename(columns=column_mapping)

            # Select and reorder columns
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]

            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Add adjusted close (same as close for Chinese stocks after qfq adjustment)
            df['adj_close'] = df['close']

            # Sort by date
            df = df.sort_values('date')

            return df

        except Exception as e:
            logger.error(f"Error fetching China A-share data for {symbol}: {str(e)}")
            return None

    def _fetch_hong_kong(self, symbol: str, start_date: Optional[datetime],
                        end_date: Optional[datetime]) -> Optional[pd.DataFrame]:
        """Fetch Hong Kong stock data"""
        try:
            # For HK stocks, use yfinance with .HK suffix
            if not symbol.endswith(".HK"):
                # Format: 00700 -> 0700.HK
                formatted_symbol = symbol.lstrip('0') + ".HK"
            else:
                formatted_symbol = symbol

            return self._fetch_yfinance(formatted_symbol, start_date, end_date)

        except Exception as e:
            logger.error(f"Error fetching Hong Kong data for {symbol}: {str(e)}")
            return None

    def _fetch_yfinance(self, symbol: str, start_date: Optional[datetime],
                       end_date: Optional[datetime], period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch data using yfinance (US stocks, crypto, etc.)"""
        try:
            ticker = yf.Ticker(symbol)

            # Fetch historical data
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date)
            else:
                df = ticker.history(period=period)

            if df is None or df.empty:
                return None

            # Reset index to make date a column
            df = df.reset_index()

            # Rename columns to lowercase
            df.columns = df.columns.str.lower()

            # Rename 'dividends' and 'stock splits' if present
            df = df.rename(columns={'dividends': 'dividend', 'stock splits': 'split'})

            # Select relevant columns
            columns_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in columns_to_keep if col in df.columns]]

            # Add adjusted close if not present
            if 'adj_close' not in df.columns:
                df['adj_close'] = df['close']

            # Convert date to datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])

            return df

        except Exception as e:
            logger.error(f"Error fetching yfinance data for {symbol}: {str(e)}")
            return None

    def fetch_multiple(self, symbols: list, market: str = "US", **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols

        Args:
            symbols: List of symbols
            market: Market code
            **kwargs: Additional arguments for fetch_history

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}

        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}")
            df = self.fetch_history(symbol, market, **kwargs)

            if df is not None:
                results[symbol] = df

            # Rate limiting
            time.sleep(0.5)

        return results

    def clear_cache(self):
        """Clear the cache"""
        self.cache = {}
        logger.info("Cache cleared")
