"""
Metrics Calculator
Calculates financial metrics: returns, volatility, beta, Sharpe ratio, etc.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional, Dict, Tuple
from loguru import logger


class MetricsCalculator:
    """Calculate financial metrics for assets"""

    def __init__(self, risk_free_rate: float = 0.03):
        """
        Initialize metrics calculator

        Args:
            risk_free_rate: Annual risk-free rate (default 3%)
        """
        self.risk_free_rate = risk_free_rate
        self.trading_days_per_year = 252

    # ==================== Returns Calculation ====================

    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate simple returns"""
        return prices.pct_change()

    def calculate_log_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate logarithmic returns"""
        return np.log(prices / prices.shift(1))

    def calculate_cumulative_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate cumulative returns"""
        returns = self.calculate_returns(prices)
        return (1 + returns).cumprod() - 1

    def calculate_period_return(self, prices: pd.Series, periods: int = None) -> float:
        """
        Calculate return over a specific period

        Args:
            prices: Price series
            periods: Number of periods (if None, use entire series)

        Returns:
            Period return as percentage
        """
        if prices.empty:
            return 0.0

        if periods is not None and periods < len(prices):
            prices = prices.iloc[-periods:]

        if len(prices) < 2:
            return 0.0

        return ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100

    def calculate_annualized_return(self, prices: pd.Series) -> float:
        """
        Calculate annualized return

        Args:
            prices: Price series

        Returns:
            Annualized return as percentage
        """
        if len(prices) < 2:
            return 0.0

        total_days = (prices.index[-1] - prices.index[0]).days
        if total_days == 0:
            return 0.0

        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        years = total_days / 365.25

        annualized = (1 + total_return) ** (1 / years) - 1

        return annualized * 100

    # ==================== Risk Metrics ====================

    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        """
        Calculate volatility (standard deviation of returns)

        Args:
            returns: Returns series
            annualize: Whether to annualize the volatility

        Returns:
            Volatility as percentage
        """
        if returns.empty or len(returns) < 2:
            return 0.0

        volatility = returns.std()

        if annualize:
            volatility = volatility * np.sqrt(self.trading_days_per_year)

        return volatility * 100

    def calculate_downside_deviation(self, returns: pd.Series, target_return: float = 0,
                                    annualize: bool = True) -> float:
        """
        Calculate downside deviation

        Args:
            returns: Returns series
            target_return: Target return threshold
            annualize: Whether to annualize

        Returns:
            Downside deviation
        """
        downside_returns = returns[returns < target_return]

        if downside_returns.empty:
            return 0.0

        downside_dev = np.sqrt(np.mean(downside_returns ** 2))

        if annualize:
            downside_dev = downside_dev * np.sqrt(self.trading_days_per_year)

        return downside_dev * 100

    def calculate_max_drawdown(self, prices: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
        """
        Calculate maximum drawdown

        Args:
            prices: Price series

        Returns:
            Tuple of (max_drawdown_pct, peak_date, trough_date)
        """
        if prices.empty or len(prices) < 2:
            return 0.0, None, None

        # Calculate cumulative returns
        cumulative = (1 + self.calculate_returns(prices)).cumprod()

        # Calculate running maximum
        running_max = cumulative.expanding().max()

        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max

        # Find maximum drawdown
        max_dd = drawdown.min()
        trough_date = drawdown.idxmin()

        # Find peak date (last maximum before trough)
        peak_date = running_max[:trough_date].idxmax()

        return max_dd * 100, peak_date, trough_date

    # ==================== Beta Calculation ====================

    def calculate_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate beta (systematic risk)

        Args:
            asset_returns: Asset returns series
            market_returns: Market returns series

        Returns:
            Beta value
        """
        if asset_returns.empty or market_returns.empty:
            return 1.0

        # Align the series
        df = pd.DataFrame({
            'asset': asset_returns,
            'market': market_returns
        }).dropna()

        if len(df) < 2:
            return 1.0

        # Calculate covariance and variance
        covariance = df['asset'].cov(df['market'])
        market_variance = df['market'].var()

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance

        return beta

    def calculate_alpha(self, asset_returns: pd.Series, market_returns: pd.Series,
                       beta: Optional[float] = None) -> float:
        """
        Calculate alpha (excess return)

        Args:
            asset_returns: Asset returns series
            market_returns: Market returns series
            beta: Pre-calculated beta (if None, will calculate)

        Returns:
            Annualized alpha as percentage
        """
        if beta is None:
            beta = self.calculate_beta(asset_returns, market_returns)

        # Calculate average returns
        avg_asset_return = asset_returns.mean() * self.trading_days_per_year
        avg_market_return = market_returns.mean() * self.trading_days_per_year

        # Alpha = Asset Return - (Risk-free Rate + Beta * (Market Return - Risk-free Rate))
        alpha = avg_asset_return - (self.risk_free_rate + beta * (avg_market_return - self.risk_free_rate))

        return alpha * 100

    # ==================== Sharpe Ratio ====================

    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: Optional[float] = None) -> float:
        """
        Calculate Sharpe Ratio

        Args:
            returns: Returns series
            risk_free_rate: Annual risk-free rate (if None, use class default)

        Returns:
            Sharpe ratio
        """
        if returns.empty or len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate

        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / self.trading_days_per_year

        # Calculate excess returns
        excess_returns = returns - daily_rf

        # Calculate Sharpe ratio
        if excess_returns.std() == 0:
            return 0.0

        sharpe = excess_returns.mean() / excess_returns.std()

        # Annualize
        sharpe = sharpe * np.sqrt(self.trading_days_per_year)

        return sharpe

    def calculate_sortino_ratio(self, returns: pd.Series, target_return: float = 0,
                                risk_free_rate: Optional[float] = None) -> float:
        """
        Calculate Sortino Ratio (Sharpe ratio using downside deviation)

        Args:
            returns: Returns series
            target_return: Target return threshold
            risk_free_rate: Annual risk-free rate

        Returns:
            Sortino ratio
        """
        if returns.empty or len(returns) < 2:
            return 0.0

        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate

        daily_rf = risk_free_rate / self.trading_days_per_year

        # Calculate excess returns
        excess_returns = returns - daily_rf

        # Calculate downside deviation
        downside_dev = self.calculate_downside_deviation(returns, target_return, annualize=False)

        if downside_dev == 0:
            return 0.0

        sortino = excess_returns.mean() / (downside_dev / 100)

        # Annualize
        sortino = sortino * np.sqrt(self.trading_days_per_year)

        return sortino

    # ==================== Value at Risk ====================

    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns: Returns series
            confidence_level: Confidence level (e.g., 0.95 for 95%)

        Returns:
            VaR as percentage
        """
        if returns.empty:
            return 0.0

        var = np.percentile(returns, (1 - confidence_level) * 100)

        return var * 100

    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)

        Args:
            returns: Returns series
            confidence_level: Confidence level

        Returns:
            CVaR as percentage
        """
        if returns.empty:
            return 0.0

        var = self.calculate_var(returns, confidence_level) / 100

        # Calculate average of returns below VaR
        cvar = returns[returns <= var].mean()

        return cvar * 100

    # ==================== Correlation ====================

    def calculate_correlation(self, returns1: pd.Series, returns2: pd.Series) -> float:
        """
        Calculate correlation between two assets

        Args:
            returns1: First asset returns
            returns2: Second asset returns

        Returns:
            Correlation coefficient
        """
        df = pd.DataFrame({
            'asset1': returns1,
            'asset2': returns2
        }).dropna()

        if len(df) < 2:
            return 0.0

        return df['asset1'].corr(df['asset2'])

    def calculate_correlation_matrix(self, returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        Calculate correlation matrix for multiple assets

        Args:
            returns_dict: Dictionary mapping asset symbol to returns series

        Returns:
            Correlation matrix DataFrame
        """
        df = pd.DataFrame(returns_dict)
        return df.corr()

    # ==================== Information Ratio ====================

    def calculate_information_ratio(self, asset_returns: pd.Series,
                                   benchmark_returns: pd.Series) -> float:
        """
        Calculate Information Ratio

        Args:
            asset_returns: Asset returns series
            benchmark_returns: Benchmark returns series

        Returns:
            Information ratio
        """
        # Align series
        df = pd.DataFrame({
            'asset': asset_returns,
            'benchmark': benchmark_returns
        }).dropna()

        if len(df) < 2:
            return 0.0

        # Calculate active returns
        active_returns = df['asset'] - df['benchmark']

        # Calculate tracking error
        tracking_error = active_returns.std()

        if tracking_error == 0:
            return 0.0

        # Calculate information ratio
        ir = active_returns.mean() / tracking_error

        # Annualize
        ir = ir * np.sqrt(self.trading_days_per_year)

        return ir

    # ==================== Comprehensive Analysis ====================

    def calculate_all_metrics(self, prices: pd.Series,
                             market_prices: Optional[pd.Series] = None) -> Dict:
        """
        Calculate all available metrics for an asset

        Args:
            prices: Asset price series
            market_prices: Market/benchmark price series (optional)

        Returns:
            Dictionary with all calculated metrics
        """
        if prices.empty or len(prices) < 2:
            return {}

        # Calculate returns
        returns = self.calculate_returns(prices)
        returns = returns.dropna()

        metrics = {
            # Returns
            "total_return": self.calculate_period_return(prices),
            "annualized_return": self.calculate_annualized_return(prices),

            # Risk
            "volatility": self.calculate_volatility(returns),
            "downside_deviation": self.calculate_downside_deviation(returns),
            "max_drawdown": self.calculate_max_drawdown(prices)[0],

            # Risk-adjusted returns
            "sharpe_ratio": self.calculate_sharpe_ratio(returns),
            "sortino_ratio": self.calculate_sortino_ratio(returns),

            # VaR
            "var_95": self.calculate_var(returns, 0.95),
            "cvar_95": self.calculate_cvar(returns, 0.95),
        }

        # Add market-related metrics if market data is provided
        if market_prices is not None and not market_prices.empty:
            market_returns = self.calculate_returns(market_prices).dropna()

            metrics["beta"] = self.calculate_beta(returns, market_returns)
            metrics["alpha"] = self.calculate_alpha(returns, market_returns, metrics["beta"])
            metrics["information_ratio"] = self.calculate_information_ratio(returns, market_returns)
            metrics["correlation_with_market"] = self.calculate_correlation(returns, market_returns)

        return metrics
