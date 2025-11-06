"""
Plotter
Generates charts and visualizations for financial data
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
import io
import base64
from loguru import logger


class Plotter:
    """Generate financial charts and visualizations"""

    def __init__(self, theme: str = "plotly_white"):
        """
        Initialize plotter

        Args:
            theme: Plotly theme
        """
        self.theme = theme
        self.default_width = 1200
        self.default_height = 600

    def plot_price_chart(self, df: pd.DataFrame, title: str = "Price Chart",
                        show_volume: bool = True) -> go.Figure:
        """
        Create price chart with optional volume

        Args:
            df: DataFrame with columns: date, open, high, low, close, volume
            title: Chart title
            show_volume: Whether to show volume subplot

        Returns:
            Plotly figure
        """
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(title, 'Volume')
            )

            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                ),
                row=1, col=1
            )

            # Volume bars
            colors = ['red' if close < open else 'green'
                     for close, open in zip(df['close'], df['open'])]

            fig.add_trace(
                go.Bar(
                    x=df['date'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors
                ),
                row=2, col=1
            )

        else:
            fig = go.Figure()

            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Price'
                )
            )

            fig.update_layout(title=title)

        fig.update_layout(
            template=self.theme,
            xaxis_rangeslider_visible=False,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_line_chart(self, data: Dict[str, pd.Series], title: str = "Line Chart",
                       ylabel: str = "Value") -> go.Figure:
        """
        Create line chart for multiple series

        Args:
            data: Dictionary mapping label to Series
            title: Chart title
            ylabel: Y-axis label

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        for label, series in data.items():
            fig.add_trace(
                go.Scatter(
                    x=series.index,
                    y=series.values,
                    mode='lines',
                    name=label
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title=ylabel,
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_returns_distribution(self, returns: pd.Series,
                                  title: str = "Returns Distribution") -> go.Figure:
        """
        Create histogram of returns distribution

        Args:
            returns: Returns series
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns',
                marker_color='lightblue',
                opacity=0.7
            )
        )

        # Add normal distribution overlay
        mean = returns.mean()
        std = returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)

        # Scale to match histogram
        y = y * len(returns) * (returns.max() - returns.min()) / 50

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name='Normal Distribution',
                line=dict(color='red', width=2)
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Returns",
            yaxis_title="Frequency",
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_correlation_matrix(self, corr_matrix: pd.DataFrame,
                               title: str = "Correlation Matrix") -> go.Figure:
        """
        Create correlation matrix heatmap

        Args:
            corr_matrix: Correlation matrix DataFrame
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title=title,
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_drawdown(self, prices: pd.Series, title: str = "Drawdown Chart") -> go.Figure:
        """
        Create drawdown chart

        Args:
            prices: Price series
            title: Chart title

        Returns:
            Plotly figure
        """
        # Calculate cumulative returns
        returns = prices.pct_change()
        cumulative = (1 + returns).cumprod()

        # Calculate running maximum
        running_max = cumulative.expanding().max()

        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max * 100

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown.values,
                fill='tozeroy',
                name='Drawdown',
                line=dict(color='red')
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_moving_averages(self, df: pd.DataFrame, ma_periods: List[int] = [20, 50, 200],
                           title: str = "Price with Moving Averages") -> go.Figure:
        """
        Create price chart with moving averages

        Args:
            df: DataFrame with 'date' and 'close' columns
            ma_periods: List of MA periods
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        # Price line
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['close'],
                mode='lines',
                name='Price',
                line=dict(color='black', width=1)
            )
        )

        # Moving averages
        colors = ['blue', 'orange', 'green', 'red', 'purple']

        for i, period in enumerate(ma_periods):
            ma = df['close'].rolling(window=period).mean()
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=ma,
                    mode='lines',
                    name=f'MA{period}',
                    line=dict(color=colors[i % len(colors)], width=1.5)
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_performance_comparison(self, data: Dict[str, pd.Series],
                                   title: str = "Performance Comparison") -> go.Figure:
        """
        Create normalized performance comparison chart

        Args:
            data: Dictionary mapping label to price series
            title: Chart title

        Returns:
            Plotly figure
        """
        fig = go.Figure()

        for label, series in data.items():
            # Normalize to 100
            normalized = (series / series.iloc[0]) * 100

            fig.add_trace(
                go.Scatter(
                    x=normalized.index,
                    y=normalized.values,
                    mode='lines',
                    name=label
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Normalized Price (Base = 100)",
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def plot_risk_return_scatter(self, metrics: Dict[str, Dict],
                                title: str = "Risk-Return Analysis") -> go.Figure:
        """
        Create risk-return scatter plot

        Args:
            metrics: Dictionary mapping asset name to metrics dict
            title: Chart title

        Returns:
            Plotly figure
        """
        assets = []
        returns = []
        volatilities = []
        sharpe_ratios = []

        for asset, metric in metrics.items():
            assets.append(asset)
            returns.append(metric.get('annualized_return', 0))
            volatilities.append(metric.get('volatility', 0))
            sharpe_ratios.append(metric.get('sharpe_ratio', 0))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=volatilities,
                y=returns,
                mode='markers+text',
                text=assets,
                textposition='top center',
                marker=dict(
                    size=15,
                    color=sharpe_ratios,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Sharpe Ratio")
                ),
                name='Assets'
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Volatility (%)",
            yaxis_title="Annualized Return (%)",
            template=self.theme,
            width=self.default_width,
            height=self.default_height
        )

        return fig

    def export_to_html(self, fig: go.Figure) -> str:
        """
        Export figure to HTML string

        Args:
            fig: Plotly figure

        Returns:
            HTML string
        """
        return fig.to_html(include_plotlyjs='cdn')

    def export_to_json(self, fig: go.Figure) -> str:
        """
        Export figure to JSON string

        Args:
            fig: Plotly figure

        Returns:
            JSON string
        """
        return fig.to_json()

    def export_to_image(self, fig: go.Figure, format: str = 'png') -> bytes:
        """
        Export figure to image bytes

        Args:
            fig: Plotly figure
            format: Image format ('png', 'jpg', 'svg', 'pdf')

        Returns:
            Image bytes
        """
        return fig.to_image(format=format)
