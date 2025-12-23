"""
AI Stock Assistant Chatbot - OPTIMIZED VERSION
===============================================
Features:
- Live USA stock prices (Brave API + yfinance)
- Stock comparison with investment recommendations
- Portfolio builder based on risk profile
- OpenAI or Gemini model selection
- Chat history with clear option
- Refactored with DRY principles and better structure
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List, Tuple, Callable, Any
import json
from abc import ABC, abstractmethod

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Centralized configuration"""
    BRAVE_API_KEY = os.getenv('BRAVE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    
    OPENAI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    GEMINI_MODELS = ["gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
    
    MAX_TOKENS = 4000
    TEMPERATURE = 0.1

config = Config()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_api_key(key: Optional[str], key_name: str) -> None:
    """Validate API key exists"""
    if not key:
        raise ValueError(f"{key_name} not found in .env file")

def safe_api_call(func: Callable, error_msg: str, default_return: Any = None, 
                  *args, **kwargs) -> Any:
    """Safely execute API calls with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_msg}: {e}")
        return default_return

def format_currency(value: float) -> str:
    """Format number as currency"""
    if value >= 1_000_000_000_000:
        return f"${value/1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    else:
        return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format percentage with color indicator"""
    sign = "+" if value > 0 else ""
    color = "green" if value > 0 else "red" if value < 0 else "gray"
    return f":{color}[{sign}{value:.2f}%]"

# ============================================================================
# SESSION STATE MANAGER
# ============================================================================

class SessionStateManager:
    """Manage Streamlit session state"""
    
    DEFAULTS = {
        'chat_history_stock': [],
        'selected_model': 'gpt-4o-mini',
        'selected_provider': 'OpenAI',
        'show_chat': True,
    }
    
    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        for key, default in SessionStateManager.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default
    
    @staticmethod
    def clear_chat():
        """Clear chat history"""
        st.session_state.chat_history_stock = []
    
    @staticmethod
    def add_message(role: str, content: str):
        """Add message to chat history"""
        st.session_state.chat_history_stock.append((role, content))

# ============================================================================
# BRAVE SEARCH API
# ============================================================================

class BraveSearchAPI:
    """Brave Search for real-time market data"""
    
    def __init__(self, api_key: str):
        validate_api_key(api_key, "Brave API key")
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'X-Subscription-Token': api_key
        })
    
    def search(self, query: str, count: int = 5) -> Optional[Dict]:
        """Perform Brave search"""
        def _search():
            params = {
                'q': query,
                'count': min(count, 20),
                'text_decorations': False
            }
            response = self.session.get(
                f"{self.base_url}/web/search", 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        return safe_api_call(_search, "Brave search error", default_return=None)
    
    def get_stock_news(self, ticker: str) -> List[Dict]:
        """Get latest news for a stock"""
        results = self.search(f"{ticker} stock news latest", count=5)
        
        if not results or 'web' not in results:
            return []
        
        return [
            {
                'title': item.get('title', ''),
                'description': item.get('description', ''),
                'url': item.get('url', '')
            }
            for item in results['web']['results'][:5]
        ]

# ============================================================================
# STOCK DATA PROVIDERS (ABSTRACTED)
# ============================================================================

class StockDataProvider(ABC):
    """Abstract base class for stock data providers"""
    
    @abstractmethod
    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get stock quote data"""
        pass
    
    @abstractmethod
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company information"""
        pass

class FinnhubProvider(StockDataProvider):
    """Finnhub data provider"""
    
    def __init__(self, api_key: str):
        validate_api_key(api_key, "Finnhub API key")
        import finnhub
        self.client = finnhub.Client(api_key=api_key)
    
    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get quote from Finnhub"""
        def _get_quote():
            quote = self.client.quote(ticker)
            if quote and quote.get('c') and quote['c'] > 0:
                return {
                    'price': quote['c'],
                    'previous_close': quote['pc'],
                    'change': quote['d'],
                    'change_percent': quote['dp'],
                    'high': quote.get('h'),
                    'low': quote.get('l'),
                    'open': quote.get('o'),
                }
            return None
        
        return safe_api_call(_get_quote, f"Finnhub quote error for {ticker}")
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company profile and metrics"""
        info = {}
        
        # Get profile (market cap)
        def _get_profile():
            profile = self.client.company_profile2(symbol=ticker)
            if profile:
                market_cap = profile.get('marketCapitalization')
                return {
                    'market_cap': market_cap * 1_000_000 if market_cap else None,
                    'name': profile.get('name'),
                    'industry': profile.get('finnhubIndustry')
                }
            return {}
        
        profile_data = safe_api_call(_get_profile, f"Finnhub profile error for {ticker}", {})
        info.update(profile_data)
        
        # Get metrics (P/E ratio)
        def _get_metrics():
            metrics = self.client.company_basic_financials(ticker, 'all')
            if metrics and 'metric' in metrics:
                return {
                    'pe_ratio': (metrics['metric'].get('peBasicExclExtraTTM') or 
                                metrics['metric'].get('peTTM'))
                }
            return {}
        
        metrics_data = safe_api_call(_get_metrics, f"Finnhub metrics error for {ticker}", {})
        info.update(metrics_data)
        
        return info if info else None

class YFinanceProvider(StockDataProvider):
    """Yahoo Finance data provider (fallback)"""
    
    def __init__(self):
        import yfinance as yf
        self.yf = yf
    
    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get quote from yfinance"""
        def _get_quote():
            stock = self.yf.Ticker(ticker)
            info = stock.info
            
            if not info or 'currentPrice' not in info:
                return None
            
            current = info.get('currentPrice') or info.get('regularMarketPrice')
            prev_close = info.get('previousClose')
            
            if current and prev_close:
                change = current - prev_close
                change_pct = (change / prev_close) * 100
                
                return {
                    'price': current,
                    'previous_close': prev_close,
                    'change': change,
                    'change_percent': change_pct,
                    'high': info.get('dayHigh'),
                    'low': info.get('dayLow'),
                    'open': info.get('open'),
                    'volume': info.get('volume'),
                }
            return None
        
        return safe_api_call(_get_quote, f"yfinance quote error for {ticker}")
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company info from yfinance"""
        def _get_info():
            stock = self.yf.Ticker(ticker)
            info = stock.info
            
            return {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'volume': info.get('volume'),
                'name': info.get('longName') or info.get('shortName'),
                'industry': info.get('industry'),
                'sector': info.get('sector'),
            }
        
        return safe_api_call(_get_info, f"yfinance info error for {ticker}", {})

class StockDataFetcher:
    """Unified stock data fetcher with fallback mechanism"""
    
    def __init__(self, finnhub_key: Optional[str] = None):
        self.providers = []
        
        # Add Finnhub if available
        if finnhub_key:
            try:
                self.providers.append(FinnhubProvider(finnhub_key))
            except Exception as e:
                logger.warning(f"Finnhub provider unavailable: {e}")
        
        # Always add yfinance as fallback
        try:
            self.providers.append(YFinanceProvider())
        except Exception as e:
            logger.error(f"yfinance provider unavailable: {e}")
    
    def get_live_stock_price(self, ticker: str) -> Optional[Dict]:
        """Get live stock price with fallback mechanism"""
        if not self.providers:
            logger.error("No stock data providers available")
            return None
        
        result = {}
        
        # Try each provider for quote data
        for provider in self.providers:
            quote = provider.get_quote(ticker)
            if quote:
                result.update(quote)
                break
        
        if not result:
            return None
        
        # Try to supplement with company info
        for provider in self.providers:
            company_info = provider.get_company_info(ticker)
            if company_info:
                # Only add missing fields
                for key, value in company_info.items():
                    if key not in result and value is not None:
                        result[key] = value
        
        result['ticker'] = ticker.upper()
        result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return result

# ============================================================================
# TICKER EXTRACTION
# ============================================================================

class TickerExtractor:
    """Extract ticker symbols from natural language"""
    
    COMPANY_MAP = {
        'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
        'amazon': 'AMZN', 'tesla': 'TSLA', 'meta': 'META', 'facebook': 'META',
        'nvidia': 'NVDA', 'netflix': 'NFLX', 'amd': 'AMD', 'intel': 'INTC',
        'ibm': 'IBM', 'oracle': 'ORCL', 'salesforce': 'CRM', 'adobe': 'ADBE',
        'paypal': 'PYPL', 'qualcomm': 'QCOM', 'cisco': 'CSCO', 'jpmorgan': 'JPM',
        'jp morgan': 'JPM', 'bank of america': 'BAC', 'wells fargo': 'WFC',
        'goldman sachs': 'GS', 'morgan stanley': 'MS', 'citigroup': 'C',
        'walmart': 'WMT', 'target': 'TGT', 'costco': 'COST', 'home depot': 'HD',
        'nike': 'NKE', 'starbucks': 'SBUX', 'mcdonalds': 'MCD', 'coca cola': 'KO',
        'pepsi': 'PEP', 'pfizer': 'PFE', 'johnson': 'JNJ', 'merck': 'MRK',
        'exxon': 'XOM', 'chevron': 'CVX', 'boeing': 'BA', 'disney': 'DIS',
        'comcast': 'CMCSA', 'verizon': 'VZ', 'att': 'T', 'ford': 'F',
        'gm': 'GM', 'general motors': 'GM', 'uber': 'UBER', 'lyft': 'LYFT',
        'airbnb': 'ABNB', 'spotify': 'SPOT', 'snap': 'SNAP', 'twitter': 'TWTR',
        'zoom': 'ZM', 'shopify': 'SHOP', 'square': 'SQ', 'robinhood': 'HOOD'
    }
    
    @classmethod
    def extract(cls, user_input: str) -> Optional[str]:
        """Extract ticker from natural language input"""
        import re
        
        text = user_input.lower().strip()
        
        # Pattern 1: Already a ticker (2-5 uppercase letters)
        ticker_match = re.search(r'\b([A-Z]{2,5})\b', user_input.upper())
        if ticker_match:
            return ticker_match.group(1)
        
        # Pattern 2: Check company name mapping
        for company, ticker in cls.COMPANY_MAP.items():
            if company in text:
                return ticker
        
        # Pattern 3: Extract potential ticker from text
        words = text.split()
        for word in words:
            word_clean = re.sub(r'[^a-z]', '', word)
            if 2 <= len(word_clean) <= 5 and word_clean.upper() in cls.COMPANY_MAP.values():
                return word_clean.upper()
        
        # Pattern 4: Last resort
        text_clean = re.sub(r'[^a-zA-Z]', '', text)
        if 2 <= len(text_clean) <= 5:
            return text_clean.upper()
        
        return None

# ============================================================================
# LLM INTERFACE (ABSTRACTED)
# ============================================================================

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from LLM"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        validate_api_key(api_key, "OpenAI API key")
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from OpenAI"""
        def _generate():
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )
            return response.choices[0].message.content
        
        result = safe_api_call(_generate, "OpenAI API error")
        return result if result else "Failed to get response from OpenAI"

class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        validate_api_key(api_key, "Gemini API key")
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from Gemini"""
        def _generate():
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        
        result = safe_api_call(_generate, "Gemini API error")
        return result if result else "Failed to get response from Gemini"

class LLMManager:
    """Manage LLM providers"""
    
    @staticmethod
    def get_provider(provider_name: str, model: str) -> Optional[LLMProvider]:
        """Get LLM provider instance"""
        try:
            if provider_name == "OpenAI":
                return OpenAIProvider(config.OPENAI_API_KEY, model)
            elif provider_name == "Gemini":
                return GeminiProvider(config.GEMINI_API_KEY, model)
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize {provider_name}: {e}")
            return None

# ============================================================================
# RESPONSE TEMPLATES
# ============================================================================

class ResponseTemplates:
    """Pre-defined response templates for common queries"""
    
    AI_TRENDS = """
# 🤖 AI Trends in Finance

AI is revolutionizing finance in several key ways:

## 1. Algorithmic Trading 
High-frequency trading using machine learning, pattern recognition in market data, and automated execution at optimal prices. Examples include Renaissance Technologies and Two Sigma.

## 2. Robo-Advisors 
Automated portfolio management (Betterment, Wealthfront) with personalized recommendations and lower fees. Growing rapidly with $1.4 trillion+ under management.

## 3. Fraud Detection & Security 
Real-time transaction monitoring with anomaly detection using neural networks, reducing fraud losses by 30-50%.

## 4. Risk Management 
Credit risk assessment with alternative data, market risk prediction models, and portfolio optimization algorithms.

## 5. NLP & Sentiment Analysis 
Analyzing news and social media to predict market movements. Bloomberg Terminal uses these sentiment tools.

## 6. Customer Service 
AI chatbots for 24/7 support, personalized financial advice, and natural language understanding.

## Future Trends:
Quantum computing for portfolio optimization
Deep learning for market prediction
Decentralized AI in DeFi
Hyper-personalized wealth management

**Bottom Line:** AI is making finance faster, smarter, and more accessible!
"""

    STOCK_INSIGHTS = """
# Stock Market Insights

## Key Points:

**Market Analysis:**
Stock markets are influenced by earnings, economic data, and sentiment. Technical and fundamental analysis help evaluate opportunities. Diversification is crucial for risk management.

**Current Trends:**
- Tech stocks remain dominant but volatile
- Value investing gaining attention
- ESG (Environmental, Social, Governance) growing importance
- AI and automation transforming industries

**Investment Considerations:**
1. **Research thoroughly** - Understand the business
2. **Check fundamentals** - P/E ratio, revenue growth, debt levels
3. **Consider valuation** - Is it overpriced or undervalued?
4. **Think long-term** - Don't chase short-term gains
5. **Manage risk** - Never invest more than you can afford to lose

*For specific stock prices or comparisons, ask about specific tickers!*
"""

    PORTFOLIO_STRATEGY = """
# Investment Strategy Insights

## Portfolio Building Principles:

**1. Diversification **
Spread across different assets (stocks, bonds, real estate), multiple sectors and geographies. Reduces overall risk.

**2. Asset Allocation **
- **Aggressive (80/20):** 80% stocks, 20% bonds
- **Moderate (60/40):** Balanced growth and stability  
- **Conservative (40/60):** Lower risk, steady returns

**3. Risk Management ⚖️**
Only invest what you can afford to lose. Build emergency fund first (3-6 months expenses). Regular rebalancing (quarterly or annually).

**4. Time Horizon **
- Long-term (10+ years): More stocks, higher growth
- Medium-term (5-10 years): Balanced approach
- Short-term (<5 years): More conservative, bonds/cash

**5. Dollar-Cost Averaging 💰**
Invest fixed amounts regularly. Reduces timing risk and takes emotion out of investing.
"""

    MARKET_ANALYSIS = """
# Market & Economic Analysis

## Current Economic Landscape:

**Key Factors Affecting Markets:**

**1. Interest Rates **
Fed policy drives borrowing costs. Higher rates mean slower growth and stronger dollar. Lower rates mean economic stimulus but higher inflation risk.

**2. Inflation **
CPI and PCE are key metrics. Affects purchasing power and returns. Central banks target 2% inflation.

**3. Economic Growth **
GDP growth indicates economic health. Employment data shows consumer strength. Manufacturing and services PMI data matter.

**4. Geopolitical Events **
Trade policies, tariffs, international conflicts, and currency fluctuations all impact markets.

**Market Cycles:**
- **Bull Markets:** Rising prices, optimism
- **Bear Markets:** Declining prices, pessimism
- **Corrections:** 10-20% temporary declines
- **Crashes:** >20% rapid declines

**Stay Informed:**
Follow economic indicators, read financial news (WSJ, Bloomberg, Reuters), understand correlation between events and markets. Think long-term and avoid panic selling.

*Markets are cyclical - patience and strategy matter!*
"""

    TRADING_CONCEPTS = """
# Trading Strategies & Concepts

## Trading Styles:

**1. Day Trading ⚡**
Buy and sell within same day. High risk, high stress. Requires significant capital and experience. 90% of day traders lose money.

**2. Swing Trading **
Hold positions for days to weeks. Capture medium-term trends. Less stressful than day trading. Technical analysis focused.

**3. Position Trading **
Hold for months to years. Based on fundamental analysis. Lower transaction costs and more tax efficient (long-term capital gains).

**Key Concepts:**

**Technical Analysis:**
Chart patterns (head & shoulders, triangles), indicators (RSI, MACD, Moving Averages), support and resistance levels, volume analysis.

**Risk Management:**
Stop losses to limit downside, position sizing (never risk >2% per trade), risk-reward ratio (aim for 1:2 or better), diversification across trades.

**Psychology:**
Control emotions (fear and greed), stick to your strategy, accept losses as part of the game, continuous learning.

⚠️ **Warning:** Trading is risky. Most traders lose money. Start with paper trading first!
"""

    @classmethod
    def get_fallback_response(cls, question: str) -> str:
        """Get appropriate fallback response based on question"""
        q = question.lower()
        
        if 'ai' in q and any(word in q for word in ['trend', 'future', 'impact']):
            return cls.AI_TRENDS
        elif any(word in q for word in ['stock', 'share', 'equity', 'ticker']):
            return f"{cls.STOCK_INSIGHTS}\n\n**Your question:** {question}"
        elif any(word in q for word in ['portfolio', 'invest', 'allocation', 'diversif']):
            return f"{cls.PORTFOLIO_STRATEGY}\n\n**Your question:** {question}"
        elif any(word in q for word in ['market', 'economy', 'recession', 'inflation', 'fed']):
            return f"{cls.MARKET_ANALYSIS}\n\n**Your question:** {question}"
        elif any(word in q for word in ['trading', 'day trade', 'swing', 'options', 'futures']):
            return cls.TRADING_CONCEPTS
        else:
            return f"""
# 💡 General Financial Guidance

**Your question:** {question}

I can help you with:
- Live stock prices (just ask "price of AAPL" or "Tesla stock")
- Stock comparisons
- Portfolio recommendations
- Market analysis
- Trading strategies
- Economic insights

Please ask a more specific question about stocks, investing, or markets!
"""

# ============================================================================
# PORTFOLIO BUILDER
# ============================================================================

class PortfolioBuilder:
    """Build investment portfolios based on risk profiles"""
    
    RISK_PROFILES = {
        'Conservative': {
            'description': 'Low risk, steady returns',
            'allocation': {'stocks': 40, 'bonds': 50, 'cash': 10},
            'expected_return': '4-6%',
            'volatility': 'Low'
        },
        'Moderate': {
            'description': 'Balanced growth and stability',
            'allocation': {'stocks': 60, 'bonds': 30, 'cash': 10},
            'expected_return': '6-8%',
            'volatility': 'Medium'
        },
        'Aggressive': {
            'description': 'High growth potential, higher risk',
            'allocation': {'stocks': 80, 'bonds': 15, 'cash': 5},
            'expected_return': '8-12%',
            'volatility': 'High'
        },
        'Very Aggressive': {
            'description': 'Maximum growth, maximum risk',
            'allocation': {'stocks': 95, 'bonds': 5, 'cash': 0},
            'expected_return': '10-15%',
            'volatility': 'Very High'
        }
    }
    
    STOCK_CATEGORIES = {
        'Large Cap Tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA'],
        'Large Cap Value': ['JPM', 'JNJ', 'PG', 'KO', 'WMT'],
        'Growth Stocks': ['TSLA', 'NFLX', 'SHOP', 'SPOT', 'SQ'],
        'Dividend Stocks': ['T', 'VZ', 'PFE', 'XOM', 'CVX'],
        'Financial': ['JPM', 'BAC', 'GS', 'MS', 'C'],
        'Healthcare': ['JNJ', 'PFE', 'UNH', 'MRK', 'ABBV'],
    }
    
    @classmethod
    def build_portfolio(cls, risk_profile: str, investment_amount: float, 
                       include_categories: List[str] = None) -> Dict:
        """Build a portfolio based on risk profile"""
        
        if risk_profile not in cls.RISK_PROFILES:
            raise ValueError(f"Invalid risk profile: {risk_profile}")
        
        profile = cls.RISK_PROFILES[risk_profile]
        allocation = profile['allocation']
        
        # Calculate amounts per asset class
        stock_amount = investment_amount * (allocation['stocks'] / 100)
        bond_amount = investment_amount * (allocation['bonds'] / 100)
        cash_amount = investment_amount * (allocation['cash'] / 100)
        
        # Select stocks from categories
        if include_categories is None:
            include_categories = list(cls.STOCK_CATEGORIES.keys())[:3]
        
        selected_stocks = []
        for category in include_categories:
            if category in cls.STOCK_CATEGORIES:
                selected_stocks.extend(cls.STOCK_CATEGORIES[category][:2])
        
        # Distribute stock amount
        stock_per_position = stock_amount / len(selected_stocks) if selected_stocks else 0
        
        portfolio = {
            'risk_profile': risk_profile,
            'profile_details': profile,
            'total_investment': investment_amount,
            'allocation': {
                'stocks': {
                    'amount': stock_amount,
                    'percentage': allocation['stocks'],
                    'positions': {stock: stock_per_position for stock in selected_stocks}
                },
                'bonds': {
                    'amount': bond_amount,
                    'percentage': allocation['bonds'],
                    'recommendations': ['BND (Total Bond)', 'AGG (Core Bond)', 'TLT (Long-term Treasury)']
                },
                'cash': {
                    'amount': cash_amount,
                    'percentage': allocation['cash'],
                    'recommendations': ['High-yield savings', 'Money market funds']
                }
            }
        }
        
        return portfolio
    
    @classmethod
    def get_rebalancing_advice(cls, current_allocation: Dict, target_profile: str) -> str:
        """Get advice on rebalancing portfolio"""
        target = cls.RISK_PROFILES[target_profile]['allocation']
        
        advice = f"### Rebalancing to {target_profile} Portfolio\n\n"
        
        for asset_class, target_pct in target.items():
            current_pct = current_allocation.get(asset_class, 0)
            diff = target_pct - current_pct
            
            if abs(diff) > 5:  # More than 5% difference
                if diff > 0:
                    advice += f"- **Increase {asset_class}** by {diff:.1f}%\n"
                else:
                    advice += f"- **Decrease {asset_class}** by {abs(diff):.1f}%\n"
        
        return advice

# ============================================================================
# STOCK COMPARISON
# ============================================================================

class StockComparator:
    """Compare multiple stocks"""
    
    def __init__(self, stock_fetcher: StockDataFetcher):
        self.stock_fetcher = stock_fetcher
    
    def compare_stocks(self, tickers: List[str]) -> Dict:
        """Compare multiple stocks"""
        comparison = {}
        
        for ticker in tickers:
            data = self.stock_fetcher.get_live_stock_price(ticker)
            if data:
                comparison[ticker] = data
        
        return comparison
    
    def generate_comparison_report(self, tickers: List[str]) -> str:
        """Generate a detailed comparison report"""
        comparison = self.compare_stocks(tickers)
        
        if not comparison:
            return "Could not fetch data for comparison"
        
        report = f"# Stock Comparison: {', '.join(tickers)}\n\n"
        
        # Price comparison
        report += "## Current Prices\n\n"
        report += "| Ticker | Price | Change | Change % |\n"
        report += "|--------|-------|--------|----------|\n"
        
        for ticker, data in comparison.items():
            report += f"| {ticker} | ${data['price']:.2f} | "
            report += f"${data['change']:+.2f} | {data['change_percent']:+.2f}% |\n"
        
        # Valuation comparison
        report += "\n## Valuation Metrics\n\n"
        report += "| Ticker | P/E Ratio | Market Cap |\n"
        report += "|--------|-----------|------------|\n"
        
        for ticker, data in comparison.items():
            pe = f"{data.get('pe_ratio', 0):.2f}" if data.get('pe_ratio') else "N/A"
            mcap = format_currency(data['market_cap']) if data.get('market_cap') else "N/A"
            report += f"| {ticker} | {pe} | {mcap} |\n"
        
        # Analysis
        report += "\n## Quick Analysis\n\n"
        
        # Find best performer
        best_performer = max(comparison.items(), key=lambda x: x[1]['change_percent'])
        worst_performer = min(comparison.items(), key=lambda x: x[1]['change_percent'])
        
        report += f"**Best Performer Today:** {best_performer[0]} "
        report += f"({best_performer[1]['change_percent']:+.2f}%)\n\n"
        report += f"**Worst Performer Today:** {worst_performer[0]} "
        report += f"({worst_performer[1]['change_percent']:+.2f}%)\n\n"
        
        # P/E comparison
        stocks_with_pe = {k: v for k, v in comparison.items() if v.get('pe_ratio')}
        if stocks_with_pe:
            lowest_pe = min(stocks_with_pe.items(), key=lambda x: x[1]['pe_ratio'])
            report += f"**Lowest P/E (Most Undervalued):** {lowest_pe[0]} "
            report += f"(P/E: {lowest_pe[1]['pe_ratio']:.2f})\n\n"
        
        report += "\n💡 *Remember: Past performance doesn't guarantee future results. "
        report += "Always do your own research!*"
        
        return report

# ============================================================================
# CHATBOT LOGIC
# ============================================================================

class StockChatbot:
    """Main chatbot orchestrator"""
    
    def __init__(self, quant_df: Optional[pd.DataFrame] = None):
        self.quant_df = quant_df
        self.stock_fetcher = StockDataFetcher(config.FINNHUB_API_KEY)
        self.comparator = StockComparator(self.stock_fetcher)
        self.brave_api = None
        
        if config.BRAVE_API_KEY:
            try:
                self.brave_api = BraveSearchAPI(config.BRAVE_API_KEY)
            except Exception as e:
                logger.warning(f"Brave API unavailable: {e}")
    
    def create_system_prompt(self) -> str:
        """Create system prompt with context"""
        context = ""
        if self.quant_df is not None and not self.quant_df.empty:
            context = f"\n\nAvailable stocks data:\n{self.quant_df.to_string()}"
        
        return f"""You are an expert AI Stock Market Assistant with advanced capabilities.

Your capabilities:
- Provide live stock prices and market data
- Compare multiple stocks side-by-side
- Build personalized investment portfolios based on risk profiles
- Analyze stocks and make comparisons
- Offer investment insights and portfolio recommendations
- Explain market trends and economic concepts
- Answer questions about trading and finance

Guidelines:
- Be concise and informative
- Use data when available
- Provide actionable insights
- Include relevant disclaimers for investment advice
- Format responses with markdown for readability
- When comparing stocks, provide detailed metrics
- When building portfolios, consider user's risk tolerance{context}

Remember: Always mention that this is not financial advice and users should do their own research."""
    
    def detect_query_type(self, query: str) -> str:
        """Detect the type of query"""
        q = query.lower()
        
        # Portfolio building keywords
        if any(word in q for word in ['portfolio', 'build', 'create portfolio', 'invest', 
                                       'allocation', 'diversif', 'risk profile']):
            return 'portfolio'
        
        # Comparison keywords
        if any(word in q for word in ['compare', 'vs', 'versus', 'better', 
                                       'difference between']):
            # Check if multiple tickers mentioned
            import re
            tickers = re.findall(r'\b([A-Z]{2,5})\b', query)
            if len(tickers) >= 2:
                return 'comparison'
        
        # Price lookup
        ticker = TickerExtractor.extract(query)
        if ticker and any(word in q for word in ['price', 'stock', 'quote', 'trading at']):
            return 'price'
        
        # General chat
        return 'general'
    
    def handle_portfolio_query(self, query: str, provider_name: str, model: str) -> str:
        """Handle portfolio building queries"""
        q = query.lower()
        
        # Detect risk profile
        risk_profile = 'Moderate'  # Default
        if any(word in q for word in ['conservative', 'safe', 'low risk']):
            risk_profile = 'Conservative'
        elif any(word in q for word in ['aggressive', 'high risk', 'growth']):
            risk_profile = 'Aggressive'
        elif any(word in q for word in ['very aggressive', 'maximum growth']):
            risk_profile = 'Very Aggressive'
        
        # Try to extract investment amount
        import re
        amount_match = re.search(r'\$?([\d,]+)', query)
        investment_amount = 10000  # Default
        if amount_match:
            investment_amount = float(amount_match.group(1).replace(',', ''))
        
        # Build portfolio
        portfolio = PortfolioBuilder.build_portfolio(
            risk_profile, 
            investment_amount,
            include_categories=['Large Cap Tech', 'Large Cap Value', 'Dividend Stocks']
        )
        
        # Format response
        response = f"# 💼 Custom Portfolio: {risk_profile}\n\n"
        response += f"**Investment Amount:** ${investment_amount:,.2f}\n\n"
        response += f"**Profile:** {portfolio['profile_details']['description']}\n"
        response += f"**Expected Return:** {portfolio['profile_details']['expected_return']}\n"
        response += f"**Volatility:** {portfolio['profile_details']['volatility']}\n\n"
        
        response += "## Asset Allocation\n\n"
        
        # Stocks
        stock_alloc = portfolio['allocation']['stocks']
        response += f"### Stocks ({stock_alloc['percentage']}% - ${stock_alloc['amount']:,.2f})\n"
        response += "| Ticker | Allocation |\n|--------|------------|\n"
        for stock, amount in stock_alloc['positions'].items():
            response += f"| {stock} | ${amount:,.2f} |\n"
        response += "\n"
        
        # Bonds
        bond_alloc = portfolio['allocation']['bonds']
        response += f"### Bonds ({bond_alloc['percentage']}% - ${bond_alloc['amount']:,.2f})\n"
        response += "**Recommended ETFs:**\n"
        for bond in bond_alloc['recommendations']:
            response += f"- {bond}\n"
        response += "\n"
        
        # Cash
        cash_alloc = portfolio['allocation']['cash']
        if cash_alloc['percentage'] > 0:
            response += f"### Cash ({cash_alloc['percentage']}% - ${cash_alloc['amount']:,.2f})\n"
            response += "**Recommended options:**\n"
            for option in cash_alloc['recommendations']:
                response += f"- {option}\n"
            response += "\n"
        
        response += "\n## Key Recommendations\n\n"
        response += "1. **Diversify** across sectors and asset classes\n"
        response += "2. **Rebalance** quarterly or when allocation drifts >5%\n"
        response += "3. **Dollar-cost average** for consistent investing\n"
        response += "4. **Review annually** and adjust based on goals\n"
        response += "5. **Emergency fund** first - keep 3-6 months expenses\n\n"
        
        response += "⚠️ *This is not financial advice. Consult with a financial advisor.*"
        
        return response
    
    def handle_comparison_query(self, query: str) -> str:
        """Handle stock comparison queries"""
        import re
        tickers = re.findall(r'\b([A-Z]{2,5})\b', query)
        
        if len(tickers) < 2:
            return "Please provide at least 2 stock tickers to compare (e.g., 'Compare AAPL vs MSFT')"
        
        return self.comparator.generate_comparison_report(tickers[:5])  # Limit to 5 stocks
    
    def process_query(self, user_query: str, provider_name: str, model: str) -> str:
        """Process user query and generate response"""
        
        query_type = self.detect_query_type(user_query)
        
        # Handle specific query types
        if query_type == 'portfolio':
            return self.handle_portfolio_query(user_query, provider_name, model)
        
        if query_type == 'comparison':
            return self.handle_comparison_query(user_query)
        
        # Handle price lookups and general queries
        ticker = TickerExtractor.extract(user_query)
        enhanced_prompt = user_query
        
        if ticker:
            stock_data = self.stock_fetcher.get_live_stock_price(ticker)
            
            if stock_data:
                # Format stock data
                price_info = f"""
**Live Stock Data for {ticker}:**
- Current Price: ${stock_data['price']:.2f}
- Change: {format_percentage(stock_data['change_percent'])}
- Previous Close: ${stock_data['previous_close']:.2f}
"""
                if stock_data.get('pe_ratio'):
                    price_info += f"- P/E Ratio: {stock_data['pe_ratio']:.2f}\n"
                if stock_data.get('market_cap'):
                    price_info += f"- Market Cap: {format_currency(stock_data['market_cap'])}\n"
                if stock_data.get('volume'):
                    price_info += f"- Volume: {stock_data['volume']:,}\n"
                
                price_info += f"- Last Updated: {stock_data['timestamp']}\n"
                
                enhanced_prompt = f"{user_query}\n\n{price_info}"
                
                # Try to get news
                if self.brave_api:
                    news = self.brave_api.get_stock_news(ticker)
                    if news:
                        news_text = "\n\n**Recent News:**\n"
                        for item in news[:3]:
                            news_text += f"- {item['title']}\n"
                        enhanced_prompt += news_text
        
        # Get LLM response for general queries
        llm = LLMManager.get_provider(provider_name, model)
        
        if llm:
            return llm.generate_response(enhanced_prompt, self.create_system_prompt())
        else:
            return ResponseTemplates.get_fallback_response(user_query)

# ============================================================================
# STREAMLIT UI
# ============================================================================

def render_stock_price_display(ticker: str, stock_data: Dict):
    """Render stock price in a nice card format"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"{ticker} Price",
            value=f"${stock_data['price']:.2f}",
            delta=f"{stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)"
        )
    
    with col2:
        if stock_data.get('pe_ratio'):
            st.metric("P/E Ratio", f"{stock_data['pe_ratio']:.2f}")
    
    with col3:
        if stock_data.get('market_cap'):
            st.metric("Market Cap", format_currency(stock_data['market_cap']))

def render_chat_interface(chatbot: StockChatbot):
    """Render the chat interface"""
    
    # Model selection
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        provider = st.selectbox(
            "AI Provider",
            ["OpenAI", "Gemini"],
            key="provider_select"
        )
        st.session_state.selected_provider = provider
    
    with col2:
        if provider == "OpenAI":
            models = config.OPENAI_MODELS
        else:
            models = config.GEMINI_MODELS
        
        model = st.selectbox("Model", models, key="model_select")
        st.session_state.selected_model = model
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            SessionStateManager.clear_chat()
            st.rerun()
    
    # Display chat history
    for role, message in st.session_state.chat_history_stock:
        with st.chat_message(role):
            st.markdown(message)
    
    # Chat input
    if prompt := st.chat_input("Ask about stocks, prices, or market insights..."):
        # Add user message
        SessionStateManager.add_message("user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chatbot.process_query(
                        prompt,
                        st.session_state.selected_provider,
                        st.session_state.selected_model
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    response = ResponseTemplates.get_fallback_response(prompt)
                
                st.markdown(response)
        
        # Save response
        SessionStateManager.add_message("assistant", response)
        st.rerun()

def render_tab3(quant_df: Optional[pd.DataFrame] = None, news_df: Optional[pd.DataFrame] = None):
    """Main render function for Tab 3"""
    
    # Initialize session state
    SessionStateManager.initialize()
    
    st.title("AI Stock Market Assistant")
    st.markdown("Get live prices, compare stocks, build portfolios, and receive AI-powered investment insights!")
    
    # Create sub-tabs
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "Quick Lookup", 
        "Compare Stocks", 
        "Portfolio Builder",
        "AI Chat"
    ])
    
    # Initialize chatbot once
    chatbot = StockChatbot(quant_df)
    
    # ========== TAB 1: AI CHAT ==========
    with sub_tab4:
        st.markdown("### Chat with AI Stock Assistant")
        st.markdown("Ask me anything about stocks, markets, investing, or finance!")
        
        render_chat_interface(chatbot)
        
        # Example queries
        with st.expander("Example Questions", expanded=False):
            examples = [
                "What's the current price of Apple?",
                "Compare Tesla and Ford stocks",
                "Should I invest in tech stocks?",
                "Explain P/E ratio",
                "What are the AI trends in finance?",
                "Build me a balanced portfolio for $10,000"
            ]
            
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    st.markdown(f"• {example}")
    
    # ========== TAB 2: COMPARE STOCKS ==========
    with sub_tab2:
        st.markdown("### Stock Comparison Tool")
        st.markdown("Compare multiple stocks side-by-side with detailed metrics")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            tickers_input = st.text_input(
                "Enter stock tickers (comma-separated)",
                placeholder="e.g., AAPL, MSFT, GOOGL, AMZN",
                key="compare_tickers"
            )
        
        with col2:
            compare_button = st.button("Compare", use_container_width=True, type="primary")
        
        if compare_button and tickers_input:
            tickers = [t.strip().upper() for t in tickers_input.split(',')]
            
            if len(tickers) < 2:
                st.error("Please enter at least 2 tickers to compare")
            elif len(tickers) > 5:
                st.warning("Comparing first 5 stocks only")
                tickers = tickers[:5]
            
            with st.spinner("Fetching stock data..."):
                report = chatbot.comparator.generate_comparison_report(tickers)
                st.markdown(report)
        
        # Quick comparison presets
        st.markdown("#### Quick Comparisons")
        
        preset_cols = st.columns(3)
        
        with preset_cols[0]:
            if st.button("Big Tech (FAANG)", use_container_width=True):
                report = chatbot.comparator.generate_comparison_report(
                    ['META', 'AAPL', 'AMZN', 'NFLX', 'GOOGL']
                )
                st.markdown(report)
        
        with preset_cols[1]:
            if st.button("Banks", use_container_width=True):
                report = chatbot.comparator.generate_comparison_report(
                    ['JPM', 'BAC', 'WFC', 'C', 'GS']
                )
                st.markdown(report)
        
        with preset_cols[2]:
            if st.button("Auto Industry", use_container_width=True):
                report = chatbot.comparator.generate_comparison_report(
                    ['TSLA', 'F', 'GM', 'TM']
                )
                st.markdown(report)
        
        # Show quant data if available
        if quant_df is not None and not quant_df.empty:
            st.markdown("---")
            st.markdown("#### Quantitative Analysis Data")
            st.dataframe(quant_df, use_container_width=True)
    
    # ========== TAB 3: PORTFOLIO BUILDER ==========
    with sub_tab3:
        st.markdown("### Personalized Portfolio Builder")
        st.markdown("Build a customized investment portfolio based on your risk profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_profile = st.selectbox(
                "Select Your Risk Profile",
                options=list(PortfolioBuilder.RISK_PROFILES.keys()),
                index=1,  # Default to Moderate
                key="portfolio_risk"
            )
            
            # Show risk profile details
            profile_details = PortfolioBuilder.RISK_PROFILES[risk_profile]
            st.info(f"""
**{profile_details['description']}**

- Expected Return: {profile_details['expected_return']}
- Volatility: {profile_details['volatility']}
- Stock Allocation: {profile_details['allocation']['stocks']}%
- Bond Allocation: {profile_details['allocation']['bonds']}%
- Cash Allocation: {profile_details['allocation']['cash']}%
            """)
        
        with col2:
            investment_amount = st.number_input(
                "Investment Amount ($)",
                min_value=1000,
                max_value=10000000,
                value=10000,
                step=1000,
                key="portfolio_amount"
            )
            
            st.markdown("#### Select Investment Categories")
            categories = st.multiselect(
                "Choose stock categories to include",
                options=list(PortfolioBuilder.STOCK_CATEGORIES.keys()),
                default=['Large Cap Tech', 'Large Cap Value', 'Dividend Stocks'],
                key="portfolio_categories"
            )
        
        if st.button("Build My Portfolio", use_container_width=True, type="primary"):
            with st.spinner("Building your personalized portfolio..."):
                portfolio = PortfolioBuilder.build_portfolio(
                    risk_profile,
                    investment_amount,
                    include_categories=categories if categories else None
                )
                
                # Display portfolio
                st.success("Portfolio created successfully!")
                
                st.markdown(f"## Your {risk_profile} Portfolio")
                st.markdown(f"**Total Investment:** ${investment_amount:,.2f}")
                
                # Asset allocation pie chart
                st.markdown("### Asset Allocation")
                
                allocation_data = pd.DataFrame({
                    'Asset Class': ['Stocks', 'Bonds', 'Cash'],
                    'Percentage': [
                        portfolio['allocation']['stocks']['percentage'],
                        portfolio['allocation']['bonds']['percentage'],
                        portfolio['allocation']['cash']['percentage']
                    ],
                    'Amount': [
                        portfolio['allocation']['stocks']['amount'],
                        portfolio['allocation']['bonds']['amount'],
                        portfolio['allocation']['cash']['amount']
                    ]
                })
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.dataframe(allocation_data, use_container_width=True, hide_index=True)
                
                with col2:
                    # Simple text representation since we don't have plotly
                    st.markdown("**Allocation Breakdown:**")
                    for _, row in allocation_data.iterrows():
                        st.markdown(f"- **{row['Asset Class']}:** {row['Percentage']}% (${row['Amount']:,.2f})")
                
                # Stock positions
                st.markdown("### Stock Positions")
                stock_positions = portfolio['allocation']['stocks']['positions']
                
                stock_df = pd.DataFrame([
                    {'Ticker': ticker, 'Allocation': f"${amount:,.2f}"}
                    for ticker, amount in stock_positions.items()
                ])
                
                st.dataframe(stock_df, use_container_width=True, hide_index=True)
                
                # Bonds and Cash recommendations
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Bond Recommendations")
                    for bond in portfolio['allocation']['bonds']['recommendations']:
                        st.markdown(f"- {bond}")
                
                with col2:
                    if portfolio['allocation']['cash']['percentage'] > 0:
                        st.markdown("### 💵 Cash Recommendations")
                        for option in portfolio['allocation']['cash']['recommendations']:
                            st.markdown(f"- {option}")
                
                # Key recommendations
                st.markdown("---")
                st.markdown("### Key Investment Principles")
                st.markdown("""
1. **Diversify** across sectors and asset classes to reduce risk
2. **Rebalance** quarterly or when allocation drifts more than 5%
3. **Dollar-cost average** by investing regularly rather than timing the market
4. **Review annually** and adjust based on changing goals and circumstances
5. **Emergency fund first** - maintain 3-6 months of expenses before investing
6. **Long-term focus** - avoid emotional reactions to short-term market volatility
7. **Tax efficiency** - consider tax-advantaged accounts (401k, IRA, etc.)
                """)
                
                st.warning("**Disclaimer:** This is not financial advice. Please consult with a certified financial advisor before making investment decisions.")
    
    # ========== TAB 4: QUICK LOOKUP ==========
    with sub_tab1:
        st.markdown("### Quick Stock Price Lookup")
        st.markdown("Get instant stock prices and key metrics")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            quick_ticker = st.text_input(
                "Enter ticker or company name",
                placeholder="e.g., AAPL, Tesla, Microsoft",
                key="quick_lookup_ticker"
            )
        
        with col2:
            lookup_button = st.button("Get Price", use_container_width=True, type="primary")
        
        if lookup_button and quick_ticker:
            ticker = TickerExtractor.extract(quick_ticker)
            
            if ticker:
                with st.spinner(f"Fetching data for {ticker}..."):
                    data = chatbot.stock_fetcher.get_live_stock_price(ticker)
                    
                    if data:
                        render_stock_price_display(ticker, data)
                        
                        # Additional details
                        with st.expander("Detailed Information", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if data.get('open'):
                                    st.metric("Open", f"${data['open']:.2f}")
                                if data.get('high'):
                                    st.metric("Day High", f"${data['high']:.2f}")
                            
                            with col2:
                                if data.get('low'):
                                    st.metric("Day Low", f"${data['low']:.2f}")
                                if data.get('volume'):
                                    st.metric("Volume", f"{data['volume']:,}")
                            
                            with col3:
                                if data.get('name'):
                                    st.markdown(f"**Company:** {data['name']}")
                                if data.get('industry'):
                                    st.markdown(f"**Industry:** {data['industry']}")
                                if data.get('sector'):
                                    st.markdown(f"**Sector:** {data['sector']}")
                        
                        # Try to get news
                        if chatbot.brave_api:
                            with st.spinner("Fetching latest news..."):
                                news = chatbot.brave_api.get_stock_news(ticker)
                                
                                if news:
                                    st.markdown("---")
                                    st.markdown("### 📰 Latest News")
                                    
                                    for item in news[:5]:
                                        with st.container():
                                            st.markdown(f"**[{item['title']}]({item['url']})**")
                                            if item['description']:
                                                st.markdown(item['description'])
                                            st.markdown("")
                    else:
                        st.error(f"Could not fetch data for {ticker}")
            else:
                st.error("Could not identify ticker from input")
        
        # Popular stocks quick buttons
        st.markdown("---")
        st.markdown("#### Popular Stocks")
        
        popular_cols = st.columns(6)
        popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
        
        for i, ticker in enumerate(popular_stocks):
            with popular_cols[i]:
                if st.button(ticker, use_container_width=True):
                    data = chatbot.stock_fetcher.get_live_stock_price(ticker)
                    if data:
                        st.metric(
                            ticker,
                            f"${data['price']:.2f}",
                            f"{data['change_percent']:+.2f}%"
                        )

# ============================================================================
# STANDALONE TEST
# ============================================================================

def main():
    """For standalone testing"""
    st.set_page_config(
        page_title="AI Stock Assistant", 
        page_icon="🤖", 
        layout="wide"
    )
    
    st.title("AI Stock Assistant - Optimized Version")
    st.info("**Integration Instructions:** Import and use `render_tab3(quant_df, news_df)` in your main app")
    
    # Demo data
    demo_data = {
        'Stock': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM'],
        'Cumulative Return (%)': [45.2, 38.7, 52.3, 28.9, 125.4, 62.1, 189.3, 22.5],
        'Volatility (%)': [22.5, 20.1, 25.8, 28.3, 55.2, 32.1, 48.9, 18.7],
        'Sharpe Ratio': [1.92, 1.85, 1.98, 0.95, 2.15, 1.87, 3.72, 1.15]
    }
    quant_df = pd.DataFrame(demo_data)
    quant_df.set_index('Stock', inplace=True)
    
    render_tab3(quant_df)

if __name__ == "__main__":
    main()