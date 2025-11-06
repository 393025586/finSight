"""
Data Processing Utilities
Common data cleaning and transformation functions
"""

import pandas as pd
import numpy as np
from typing import Optional, List
from datetime import datetime


def clean_dataframe(df: pd.DataFrame, drop_duplicates: bool = True,
                   reset_index: bool = True) -> pd.DataFrame:
    """
    Clean a dataframe by removing duplicates and resetting index

    Args:
        df: Input dataframe
        drop_duplicates: Whether to drop duplicate rows
        reset_index: Whether to reset the index

    Returns:
        Cleaned dataframe
    """
    df_clean = df.copy()

    if drop_duplicates:
        df_clean = df_clean.drop_duplicates()

    if reset_index:
        df_clean = df_clean.reset_index(drop=True)

    return df_clean


def fill_missing_values(df: pd.DataFrame, method: str = 'ffill',
                       columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Fill missing values in dataframe

    Args:
        df: Input dataframe
        method: Fill method ('ffill', 'bfill', 'mean', 'median', 'zero')
        columns: Specific columns to fill (None for all)

    Returns:
        Dataframe with filled values
    """
    df_filled = df.copy()

    if columns is None:
        columns = df.columns.tolist()

    for col in columns:
        if col not in df.columns:
            continue

        if method == 'ffill':
            df_filled[col] = df_filled[col].fillna(method='ffill')
        elif method == 'bfill':
            df_filled[col] = df_filled[col].fillna(method='bfill')
        elif method == 'mean':
            df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
        elif method == 'median':
            df_filled[col] = df_filled[col].fillna(df_filled[col].median())
        elif method == 'zero':
            df_filled[col] = df_filled[col].fillna(0)

    return df_filled


def calculate_returns(prices: pd.Series, period: int = 1) -> pd.Series:
    """
    Calculate returns from price series

    Args:
        prices: Price series
        period: Period for return calculation (1 for daily, 252 for annual)

    Returns:
        Returns series
    """
    if period == 1:
        # Simple returns
        returns = prices.pct_change()
    else:
        # Period returns
        returns = prices.pct_change(periods=period)

    return returns


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate logarithmic returns from price series

    Args:
        prices: Price series

    Returns:
        Log returns series
    """
    log_returns = np.log(prices / prices.shift(1))
    return log_returns


def normalize_series(series: pd.Series, method: str = 'minmax') -> pd.Series:
    """
    Normalize a series

    Args:
        series: Input series
        method: Normalization method ('minmax', 'zscore')

    Returns:
        Normalized series
    """
    if method == 'minmax':
        # Min-Max normalization to [0, 1]
        normalized = (series - series.min()) / (series.max() - series.min())
    elif method == 'zscore':
        # Z-score normalization
        normalized = (series - series.mean()) / series.std()
    else:
        normalized = series

    return normalized


def resample_ohlc(df: pd.DataFrame, freq: str = 'W',
                 price_col: str = 'close') -> pd.DataFrame:
    """
    Resample OHLC data to different frequency

    Args:
        df: Input dataframe with OHLC data
        freq: Target frequency ('D', 'W', 'M', 'Q', 'Y')
        price_col: Main price column name

    Returns:
        Resampled dataframe
    """
    df_resampled = df.resample(freq).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    return df_resampled


def detect_outliers(series: pd.Series, method: str = 'iqr',
                   threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in a series

    Args:
        series: Input series
        method: Detection method ('iqr', 'zscore')
        threshold: Threshold for outlier detection

    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        outliers = (series < (Q1 - threshold * IQR)) | (series > (Q3 + threshold * IQR))
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = z_scores > threshold
    else:
        outliers = pd.Series([False] * len(series), index=series.index)

    return outliers


def align_dataframes(*dfs: pd.DataFrame, join: str = 'inner') -> List[pd.DataFrame]:
    """
    Align multiple dataframes by their index

    Args:
        *dfs: Variable number of dataframes
        join: Join method ('inner', 'outer', 'left', 'right')

    Returns:
        List of aligned dataframes
    """
    if len(dfs) < 2:
        return list(dfs)

    # Get common index
    indices = [df.index for df in dfs]

    if join == 'inner':
        common_index = indices[0]
        for idx in indices[1:]:
            common_index = common_index.intersection(idx)
    elif join == 'outer':
        common_index = indices[0]
        for idx in indices[1:]:
            common_index = common_index.union(idx)
    else:
        common_index = indices[0]

    # Reindex all dataframes
    aligned_dfs = [df.reindex(common_index) for df in dfs]

    return aligned_dfs


def validate_data(df: pd.DataFrame, required_columns: List[str],
                 date_column: Optional[str] = None) -> bool:
    """
    Validate dataframe structure

    Args:
        df: Input dataframe
        required_columns: List of required column names
        date_column: Optional date column to validate

    Returns:
        True if valid, False otherwise
    """
    # Check required columns
    if not all(col in df.columns for col in required_columns):
        return False

    # Check date column if specified
    if date_column and date_column in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            return False

    # Check for completely empty dataframe
    if df.empty:
        return False

    return True
