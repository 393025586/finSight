"""
Macro Metrics Fetcher
Fetches macroeconomic indicators and data
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from loguru import logger


class MacroMetricsFetcher:
    """Fetch macroeconomic metrics"""

    def __init__(self):
        """Initialize macro metrics fetcher"""
        pass

    def fetch_gdp(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch GDP data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with GDP data
        """
        try:
            if country == "CN":
                # China GDP quarterly data
                df = ak.macro_china_gdp()
                df = df.rename(columns={
                    '季度': 'date',
                    '国内生产总值-绝对值': 'gdp_absolute',
                    '国内生产总值-同比增长': 'gdp_yoy_growth'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            elif country == "US":
                # US GDP data
                logger.warning("US GDP data not yet implemented")
                return None
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching GDP for {country}: {str(e)}")
            return None

    def fetch_cpi(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch CPI (Consumer Price Index) data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with CPI data
        """
        try:
            if country == "CN":
                # China CPI monthly data
                df = ak.macro_china_cpi_monthly()
                df = df.rename(columns={
                    '月份': 'date',
                    '全国当月': 'cpi_monthly',
                    '全国同比增长': 'cpi_yoy_growth',
                    '全国累计': 'cpi_cumulative'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            elif country == "US":
                logger.warning("US CPI data not yet implemented")
                return None
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching CPI for {country}: {str(e)}")
            return None

    def fetch_pmi(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch PMI (Purchasing Managers Index) data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with PMI data
        """
        try:
            if country == "CN":
                # China PMI data
                df = ak.macro_china_pmi()
                df = df.rename(columns={
                    '月份': 'date',
                    '制造业-指数': 'manufacturing_pmi',
                    '非制造业-指数': 'non_manufacturing_pmi'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            elif country == "US":
                logger.warning("US PMI data not yet implemented")
                return None
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching PMI for {country}: {str(e)}")
            return None

    def fetch_interest_rate(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch central bank interest rate data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with interest rate data
        """
        try:
            if country == "CN":
                # China interest rate (LPR - Loan Prime Rate)
                df = ak.rate_interbank()
                df = df.rename(columns={
                    '报告日': 'date',
                    '利率': 'rate'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            elif country == "US":
                logger.warning("US interest rate data not yet implemented")
                return None
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching interest rate for {country}: {str(e)}")
            return None

    def fetch_money_supply(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch money supply data (M0, M1, M2)

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with money supply data
        """
        try:
            if country == "CN":
                # China money supply
                df = ak.macro_china_money_supply()
                df = df.rename(columns={
                    '月份': 'date',
                    '货币和准货币(M2)数量(亿元)': 'm2',
                    '货币(M1)数量(亿元)': 'm1',
                    '流通中的现金(M0)(亿元)': 'm0'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching money supply for {country}: {str(e)}")
            return None

    def fetch_foreign_exchange_reserves(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch foreign exchange reserves data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with FX reserves data
        """
        try:
            if country == "CN":
                # China foreign exchange reserves
                df = ak.macro_china_fx_reserves_yearly()
                df = df.rename(columns={
                    '年份': 'date',
                    '外汇储备(亿美元)': 'fx_reserves_usd'
                })
                df['date'] = pd.to_datetime(df['date'].astype(str) + '-01-01')
                return df
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching FX reserves for {country}: {str(e)}")
            return None

    def fetch_trade_balance(self, country: str = "CN") -> Optional[pd.DataFrame]:
        """
        Fetch trade balance data

        Args:
            country: Country code (CN, US)

        Returns:
            DataFrame with trade balance data
        """
        try:
            if country == "CN":
                # China import/export data
                df = ak.macro_china_trade_balance()
                df = df.rename(columns={
                    '月份': 'date',
                    '出口金额': 'exports',
                    '进口金额': 'imports',
                    '贸易差额': 'trade_balance'
                })
                df['date'] = pd.to_datetime(df['date'])
                return df
            else:
                return None

        except Exception as e:
            logger.error(f"Error fetching trade balance for {country}: {str(e)}")
            return None

    def fetch_all_metrics(self, country: str = "CN") -> Dict[str, pd.DataFrame]:
        """
        Fetch all available macro metrics for a country

        Args:
            country: Country code

        Returns:
            Dictionary mapping metric name to DataFrame
        """
        metrics = {}

        logger.info(f"Fetching all macro metrics for {country}")

        # GDP
        gdp_data = self.fetch_gdp(country)
        if gdp_data is not None:
            metrics["gdp"] = gdp_data

        # CPI
        cpi_data = self.fetch_cpi(country)
        if cpi_data is not None:
            metrics["cpi"] = cpi_data

        # PMI
        pmi_data = self.fetch_pmi(country)
        if pmi_data is not None:
            metrics["pmi"] = pmi_data

        # Interest Rate
        rate_data = self.fetch_interest_rate(country)
        if rate_data is not None:
            metrics["interest_rate"] = rate_data

        # Money Supply
        money_data = self.fetch_money_supply(country)
        if money_data is not None:
            metrics["money_supply"] = money_data

        # Trade Balance
        trade_data = self.fetch_trade_balance(country)
        if trade_data is not None:
            metrics["trade_balance"] = trade_data

        logger.info(f"Successfully fetched {len(metrics)} macro metrics for {country}")

        return metrics

    def get_latest_values(self, country: str = "CN") -> Dict[str, Dict]:
        """
        Get latest values for all macro metrics

        Args:
            country: Country code

        Returns:
            Dictionary with latest values for each metric
        """
        all_metrics = self.fetch_all_metrics(country)

        latest_values = {}

        for metric_name, df in all_metrics.items():
            if df is not None and not df.empty:
                latest_row = df.iloc[-1]
                latest_values[metric_name] = {
                    "date": latest_row['date'].isoformat() if pd.notna(latest_row['date']) else None,
                    "values": {col: float(latest_row[col]) if pd.notna(latest_row[col]) else None
                              for col in df.columns if col != 'date'}
                }

        return latest_values
