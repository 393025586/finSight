"""
AI Analyzer
Uses LLM (Gemini) for intelligent financial analysis
"""

import google.generativeai as genai
import os
from typing import Optional, Dict, List
from loguru import logger
import json


class AIAnalyzer:
    """AI-powered financial analysis using Gemini"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        """
        Initialize AI analyzer

        Args:
            api_key: Gemini API key (if None, will use env variable)
            model: Model name
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("Gemini API key not found. AI analysis will not be available.")
            self.enabled = False
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model)
            self.enabled = True
            logger.info(f"AI Analyzer initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.enabled = False

    def analyze_asset(self, symbol: str, asset_info: Dict, metrics: Dict,
                     news: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Analyze an asset comprehensively

        Args:
            symbol: Asset symbol
            asset_info: Basic asset information
            metrics: Financial metrics
            news: Recent news articles

        Returns:
            Analysis text
        """
        if not self.enabled:
            return "AI analysis is not available. Please configure Gemini API key."

        try:
            prompt = self._build_asset_analysis_prompt(symbol, asset_info, metrics, news)

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error analyzing asset {symbol}: {str(e)}")
            return None

    def generate_daily_summary(self, date: str, market_data: Dict,
                             top_movers: Dict, news: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Generate daily market summary

        Args:
            date: Date string
            market_data: Market indices data
            top_movers: Top gainers and losers
            news: Top news headlines

        Returns:
            Summary text
        """
        if not self.enabled:
            return "AI analysis is not available."

        try:
            prompt = self._build_daily_summary_prompt(date, market_data, top_movers, news)

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error generating daily summary: {str(e)}")
            return None

    def analyze_macro_metrics(self, country: str, metrics_data: Dict) -> Optional[str]:
        """
        Analyze macroeconomic indicators

        Args:
            country: Country code
            metrics_data: Dictionary of macro metrics

        Returns:
            Analysis text
        """
        if not self.enabled:
            return "AI analysis is not available."

        try:
            prompt = self._build_macro_analysis_prompt(country, metrics_data)

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error analyzing macro metrics: {str(e)}")
            return None

    def analyze_portfolio(self, portfolio: List[Dict], metrics: Dict) -> Optional[str]:
        """
        Analyze a portfolio

        Args:
            portfolio: List of portfolio holdings
            metrics: Portfolio metrics

        Returns:
            Analysis text
        """
        if not self.enabled:
            return "AI analysis is not available."

        try:
            prompt = self._build_portfolio_analysis_prompt(portfolio, metrics)

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return None

    def suggest_investment(self, user_profile: Dict, market_conditions: Dict) -> Optional[str]:
        """
        Generate investment suggestions

        Args:
            user_profile: User risk profile and preferences
            market_conditions: Current market conditions

        Returns:
            Investment suggestions
        """
        if not self.enabled:
            return "AI analysis is not available."

        try:
            prompt = self._build_investment_suggestion_prompt(user_profile, market_conditions)

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error generating investment suggestions: {str(e)}")
            return None

    # ==================== Prompt Builders ====================

    def _build_asset_analysis_prompt(self, symbol: str, asset_info: Dict,
                                    metrics: Dict, news: Optional[List[Dict]]) -> str:
        """Build prompt for asset analysis"""
        prompt = f"""
Analyze the following asset and provide investment insights:

**Asset Information:**
- Symbol: {symbol}
- Name: {asset_info.get('name', 'N/A')}
- Sector: {asset_info.get('sector', 'N/A')}
- Market: {asset_info.get('market', 'N/A')}

**Performance Metrics:**
- Annualized Return: {metrics.get('annualized_return', 'N/A'):.2f}%
- Volatility: {metrics.get('volatility', 'N/A'):.2f}%
- Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A'):.2f}
- Beta: {metrics.get('beta', 'N/A')}
- Max Drawdown: {metrics.get('max_drawdown', 'N/A'):.2f}%

"""

        if news and len(news) > 0:
            prompt += "\n**Recent News:**\n"
            for i, article in enumerate(news[:5], 1):
                prompt += f"{i}. {article.get('title', 'N/A')}\n"

        prompt += """
Please provide:
1. **Performance Analysis**: Evaluate the asset's historical performance and risk profile
2. **Risk Assessment**: Analyze the risk factors and volatility
3. **Investment Outlook**: Provide a forward-looking perspective
4. **Recommendation**: Give a clear buy/hold/sell recommendation with rationale

Keep the analysis concise (200-300 words) and actionable.
"""

        return prompt

    def _build_daily_summary_prompt(self, date: str, market_data: Dict,
                                   top_movers: Dict, news: Optional[List[Dict]]) -> str:
        """Build prompt for daily market summary"""
        prompt = f"""
Generate a comprehensive daily market summary for {date}:

**Market Indices:**
"""
        for index, data in market_data.items():
            change = data.get('change_percent', 0)
            prompt += f"- {index}: {data.get('price', 'N/A')} ({change:+.2f}%)\n"

        prompt += "\n**Top Movers:**\n"
        if 'gainers' in top_movers:
            prompt += "Gainers:\n"
            for stock in top_movers['gainers'][:5]:
                prompt += f"- {stock['symbol']}: +{stock.get('change_percent', 0):.2f}%\n"

        if 'losers' in top_movers:
            prompt += "\nLosers:\n"
            for stock in top_movers['losers'][:5]:
                prompt += f"- {stock['symbol']}: {stock.get('change_percent', 0):.2f}%\n"

        if news and len(news) > 0:
            prompt += "\n**Key Headlines:**\n"
            for i, article in enumerate(news[:5], 1):
                prompt += f"{i}. {article.get('title', 'N/A')}\n"

        prompt += """
Please provide:
1. **Market Overview**: Summarize today's market movements
2. **Key Drivers**: Identify main factors affecting the market
3. **Sector Performance**: Highlight sector trends
4. **Outlook**: Brief perspective on market direction

Keep it concise (250-350 words) and informative.
"""

        return prompt

    def _build_macro_analysis_prompt(self, country: str, metrics_data: Dict) -> str:
        """Build prompt for macroeconomic analysis"""
        prompt = f"""
Analyze the macroeconomic indicators for {country}:

**Economic Metrics:**
"""
        for metric_name, metric_data in metrics_data.items():
            prompt += f"\n{metric_name.upper()}:\n"
            if isinstance(metric_data, dict):
                for key, value in metric_data.get('values', {}).items():
                    if value is not None:
                        prompt += f"  - {key}: {value}\n"

        prompt += """
Please provide:
1. **Economic Health**: Assess the overall economic condition
2. **Key Trends**: Identify important trends in the data
3. **Policy Implications**: Discuss potential policy impacts
4. **Investment Impact**: How might these indicators affect investments?

Keep the analysis concise (250-350 words) and focused on investment implications.
"""

        return prompt

    def _build_portfolio_analysis_prompt(self, portfolio: List[Dict], metrics: Dict) -> str:
        """Build prompt for portfolio analysis"""
        prompt = """
Analyze the following investment portfolio:

**Holdings:**
"""
        for holding in portfolio:
            prompt += f"- {holding.get('symbol')}: {holding.get('quantity', 0)} shares @ ${holding.get('average_cost', 0):.2f}\n"

        prompt += f"""
**Portfolio Metrics:**
- Total Value: ${metrics.get('total_value', 0):,.2f}
- Total Return: {metrics.get('total_return', 0):.2f}%
- Portfolio Beta: {metrics.get('beta', 0):.2f}
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}

Please provide:
1. **Diversification Analysis**: Assess portfolio diversification
2. **Risk Profile**: Evaluate overall portfolio risk
3. **Performance Review**: Analyze returns and risk-adjusted performance
4. **Recommendations**: Suggest improvements or rebalancing strategies

Keep it concise (250-350 words) and actionable.
"""

        return prompt

    def _build_investment_suggestion_prompt(self, user_profile: Dict,
                                           market_conditions: Dict) -> str:
        """Build prompt for investment suggestions"""
        prompt = f"""
Generate personalized investment suggestions:

**User Profile:**
- Risk Tolerance: {user_profile.get('risk_tolerance', 'Moderate')}
- Investment Horizon: {user_profile.get('investment_horizon', 'Medium-term')}
- Investment Goals: {user_profile.get('goals', 'Growth')}
- Available Capital: ${user_profile.get('capital', 0):,.2f}

**Current Market Conditions:**
- Market Trend: {market_conditions.get('trend', 'Neutral')}
- Volatility: {market_conditions.get('volatility', 'Normal')}

Please provide:
1. **Asset Allocation**: Suggest allocation across asset classes
2. **Specific Recommendations**: Recommend 3-5 specific investments
3. **Strategy**: Outline investment strategy and approach
4. **Risk Management**: Suggest risk management techniques

Keep it practical and tailored to the user's profile (300-400 words).
"""

        return prompt

    def chat(self, message: str, context: Optional[str] = None) -> Optional[str]:
        """
        General chat interface for financial queries

        Args:
            message: User message
            context: Optional context information

        Returns:
            AI response
        """
        if not self.enabled:
            return "AI chat is not available. Please configure Gemini API key."

        try:
            prompt = message

            if context:
                prompt = f"Context: {context}\n\nQuestion: {message}"

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return None
