"""
Asset Info Fetcher
Fetches basic asset information and financial metrics
"""

import yfinance as yf
import akshare as ak
from typing import Optional, Dict
from loguru import logger


class AssetInfoFetcher:
    """Fetch asset basic information and financial metrics"""

    def __init__(self):
        """Initialize asset info fetcher"""
        pass

    def fetch_asset_info(self, symbol: str, market: str = "US") -> Optional[Dict]:
        """
        Fetch basic asset information

        Args:
            symbol: Asset symbol
            market: Market code (CN, HK, US)

        Returns:
            Dictionary with asset information
        """
        try:
            if market == "CN":
                return self._fetch_china_info(symbol)
            elif market == "HK":
                return self._fetch_hong_kong_info(symbol)
            else:
                return self._fetch_yfinance_info(symbol)

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return None

    def _fetch_china_info(self, symbol: str) -> Optional[Dict]:
        """Fetch China A-share stock information"""
        try:
            # Get stock info using akshare
            # Format symbol
            if symbol.startswith("6"):
                ak_symbol = f"sh{symbol}"
            else:
                ak_symbol = f"sz{symbol}"

            # Get basic stock info
            stock_info = ak.stock_individual_info_em(symbol=symbol)

            if stock_info is None or stock_info.empty:
                return None

            # Extract information
            info_dict = {}
            for _, row in stock_info.iterrows():
                key = row['item']
                value = row['value']
                info_dict[key] = value

            result = {
                "symbol": symbol,
                "name": info_dict.get('股票简称', ''),
                "market": "CN",
                "sector": info_dict.get('行业', ''),
                "description": info_dict.get('公司简介', ''),
                "currency": "CNY",
                "metadata": info_dict
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching China info for {symbol}: {str(e)}")
            return None

    def _fetch_hong_kong_info(self, symbol: str) -> Optional[Dict]:
        """Fetch Hong Kong stock information"""
        try:
            # Format symbol for yfinance
            if not symbol.endswith(".HK"):
                formatted_symbol = symbol.lstrip('0') + ".HK"
            else:
                formatted_symbol = symbol

            return self._fetch_yfinance_info(formatted_symbol)

        except Exception as e:
            logger.error(f"Error fetching Hong Kong info for {symbol}: {str(e)}")
            return None

    def _fetch_yfinance_info(self, symbol: str) -> Optional[Dict]:
        """Fetch asset information using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                return None

            result = {
                "symbol": symbol,
                "name": info.get('longName') or info.get('shortName', ''),
                "asset_type": self._determine_asset_type(info),
                "market": self._determine_market(symbol, info),
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                "description": info.get('longBusinessSummary', ''),
                "currency": info.get('currency', 'USD'),
                "website": info.get('website', ''),
                "employees": info.get('fullTimeEmployees'),
                "metadata": {
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE'),
                    "dividend_yield": info.get('dividendYield'),
                    "beta": info.get('beta'),
                    "52_week_high": info.get('fiftyTwoWeekHigh'),
                    "52_week_low": info.get('fiftyTwoWeekLow'),
                    "average_volume": info.get('averageVolume'),
                    "revenue": info.get('totalRevenue'),
                    "profit_margin": info.get('profitMargins'),
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching yfinance info for {symbol}: {str(e)}")
            return None

    def _determine_asset_type(self, info: Dict) -> str:
        """Determine asset type from yfinance info"""
        quote_type = info.get('quoteType', '').upper()

        if quote_type == 'EQUITY':
            return 'stock'
        elif quote_type == 'ETF':
            return 'etf'
        elif quote_type == 'CRYPTOCURRENCY':
            return 'crypto'
        elif quote_type == 'INDEX':
            return 'index'
        elif quote_type == 'MUTUALFUND':
            return 'mutual_fund'
        elif 'CURRENCY' in quote_type:
            return 'forex'
        else:
            return 'other'

    def _determine_market(self, symbol: str, info: Dict) -> str:
        """Determine market from symbol and info"""
        exchange = info.get('exchange', '')

        if 'HKG' in exchange or '.HK' in symbol:
            return 'HK'
        elif 'SHG' in exchange or 'SHH' in exchange or 'SHZ' in exchange:
            return 'CN'
        elif any(x in exchange for x in ['NYSE', 'NASDAQ', 'AMEX', 'US']):
            return 'US'
        else:
            return 'US'  # Default to US

    def fetch_financial_metrics(self, symbol: str, market: str = "US") -> Optional[Dict]:
        """
        Fetch financial metrics for an asset

        Args:
            symbol: Asset symbol
            market: Market code

        Returns:
            Dictionary with financial metrics
        """
        try:
            if market != "CN" or market != "HK":
                ticker = yf.Ticker(symbol)
                info = ticker.info

                metrics = {
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE'),
                    "forward_pe": info.get('forwardPE'),
                    "peg_ratio": info.get('pegRatio'),
                    "price_to_book": info.get('priceToBook'),
                    "price_to_sales": info.get('priceToSalesTrailing12Months'),
                    "dividend_yield": info.get('dividendYield'),
                    "payout_ratio": info.get('payoutRatio'),
                    "beta": info.get('beta'),
                    "eps": info.get('trailingEps'),
                    "revenue": info.get('totalRevenue'),
                    "revenue_growth": info.get('revenueGrowth'),
                    "profit_margin": info.get('profitMargins'),
                    "operating_margin": info.get('operatingMargins'),
                    "roe": info.get('returnOnEquity'),
                    "roa": info.get('returnOnAssets'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "current_ratio": info.get('currentRatio'),
                    "quick_ratio": info.get('quickRatio'),
                }

                return metrics

            return None

        except Exception as e:
            logger.error(f"Error fetching financial metrics for {symbol}: {str(e)}")
            return None
