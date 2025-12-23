# FinFusion: AI-Powered Financial Analysis Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-Agents-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple)

Real-time financial analysis combining market data APIs, technical indicators, and multi-model LLM orchestration.

</div>

---

## 🎯 Overview

Financial intelligence platform featuring:
- **Live Market Data**: Real-time stock prices, IPO tracking, economic indicators
- **AI Assistant**: Multi-model LLM (GPT-4, Gemini) with LangChain agents
- **Portfolio Tools**: Risk-based construction, stock comparison, analysis
- **Education**: Trading fundamentals and strategy guides

| Module | Technology | Key Features |
|--------|------------|--------------|
| Technical Analysis | Finnhub API, TradingView | Live charts, IPO alerts, Slack notifications |
| Economic Dashboard | FRED API | US indicators, commodities, debt metrics |
| AI Strategy Assistant | LangChain, GPT-4, Gemini | Chat analysis, portfolio building, comparisons |
| Education Hub | Structured content | Trading fundamentals, strategies |


## 🤖 GenAI Implementation

### 1. Multi-Model LLM System

**Provider Architecture:**
- Abstract base class for unified interface
- OpenAI: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- Gemini: 2.5-pro, 2.5-flash, 2.5-flash-lite
- Runtime model switching with automatic fallback
- Temperature: 0.1, Max tokens: 4000

### 2. Query Processing Pipeline

**Four-Stage Flow:**

1. **Intent Detection**: Regex ticker extraction, keyword classification → portfolio/comparison/price/general
2. **Data Enrichment**: Multi-source aggregation (Finnhub → yFinance → Yahoo) with validation
3. **Prompt Engineering**: Role + capabilities + live data + news + historical context
4. **Response**: LLM inference → validation → fallback templates if needed

### 3. LangChain Agent (ReAct)

**Components:**
- **Tools**: Stock price lookup, news retrieval, portfolio builder, comparator
- **Memory**: 5-message conversation buffer
- **Capabilities**: Autonomous tool selection, multi-step reasoning, error recovery

### 4. Portfolio Intelligence

**Risk Profiles:**
- Conservative: 40/50/10 (stocks/bonds/cash)
- Moderate: 60/30/10
- Aggressive: 80/15/5
- Very Aggressive: 95/5/0

**Algorithm**: NLP risk detection → asset allocation → stock selection from 6 categories → position sizing → rebalancing rules

**Comparison Engine**: Parallel fetching → metric normalization → ranking → AI insights

### 5. Prompt Engineering

**Techniques:**
- Role-playing (Expert Financial Assistant)
- Few-shot learning (example Q&A)
- Chain-of-thought reasoning
- Context injection (real-time data + trends + news)
- Safety constraints (disclaimers, format specifications)

### 6. Error Handling

**Multi-Layer Fallback:**
Primary LLM → Alternative LLM → Template Response → Error Message

**Resilience**: Exponential backoff, circuit breakers, health checks, graceful degradation

---

## 📊 Technical Stack

**Frontend**: Streamlit (reactive UI), Plotly (charts), TradingView (widgets)

**AI/ML**: LangChain (orchestration), OpenAI GPT-4, Google Gemini 2.5

**Data**: Finnhub (stocks), FRED (economics), Brave Search (news), yfinance (backup)

**Infrastructure**: Pandas/NumPy (processing), REST APIs, Slack webhooks

---

## 🚀 Quick Start

**Installation:**
1. Install: `pip install -r requirements.txt`
2. Configure .env with API keys: FINNHUB, FRED, OPENAI, GEMINI, BRAVE
3. Add data files: final_news.csv, quantitative_summary.csv
4. Run: `streamlit run app.py`

**API Keys Required:**
- Finnhub (stock data)
- FRED (economic data)
- OpenAI (GPT models)
- Google AI (Gemini)
- Brave Search (news)
- Slack webhook (optional)

---

## ⚙️ Key Features

### Data Processing
- **Real-time Stock Data**: Cascading fallback across 3 providers with validation
- **Economic Indicators**: FRED API with 5-period trend analysis
- **News Aggregation**: Brave Search with relevance filtering

### AI Capabilities
- Natural language ticker extraction (70+ company mappings)
- Intent classification for query routing
- Multi-step reasoning for complex questions
- Context-aware recommendations
- Conversation memory (5-turn window)

### Performance
- Streamlit caching for static data
- Session state for API results
- Parallel data fetching
- 1-minute refresh for live prices
- Exponential backoff for rate limits

---

## 🔐 Security

- API keys in .env (gitignored)
- Input validation (ticker format, ranges)
- Rate limiting on external APIs
- No sensitive data logging
- Financial disclaimer enforcement

---

## 📝 License

MIT License

---

<div align="center">

**Built for Traders • Data Engineers • GenAI Engineers**

⭐ Real-time Analysis • AI-Powered Insights • Production-Ready

</div>
