import streamlit as st

def render_tab4():
    """Render Tab 4: Trading Fundamentals for Beginners"""
    
    # Professional styling - Dark theme to match dashboard
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
        }
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 2.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2.2rem;
            font-weight: 700;
        }
        .main-header p {
            color: rgba(255,255,255,0.95);
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
        }
        .term-card {
            background: #1e2128;
            border-radius: 8px;
            padding: 1.3rem 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .term-card:hover {
            box-shadow: 0 4px 16px rgba(102,126,234,0.4);
            transform: translateY(-1px);
            background: #252830;
        }
        .term-card h3 {
            color: #7c8adb;
            margin-top: 0;
            margin-bottom: 0.7rem;
            font-size: 1.2rem;
        }
        .term-card p {
            color: #c9d1d9;
            line-height: 1.6;
            margin-bottom: 0.6rem;
            font-size: 0.95rem;
        }
        .term-card .example {
            background: #1a3a1a;
            padding: 0.8rem 1rem;
            border-radius: 6px;
            margin-top: 0.8rem;
            border-left: 3px solid #28a745;
            font-size: 0.9rem;
            color: #c9d1d9;
        }
        .term-card .example strong {
            color: #4ade80;
        }
        .term-card .example p {
            color: #c9d1d9;
        }
        .step-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(102,126,234,0.3);
        }
        .step-card h4 {
            margin-top: 0;
            font-size: 1.1rem;
            margin-bottom: 0.6rem;
            color: white;
        }
        .step-card p {
            margin: 0 0 0.4rem 0;
            line-height: 1.5;
            opacity: 0.95;
            font-size: 0.9rem;
            color: rgba(255,255,255,0.95);
        }
        .info-banner {
            background: #1a2332;
            border-left: 4px solid #2196f3;
            padding: 1.2rem 1.3rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }
        .info-banner h4 {
            color: #5ca4f5;
            margin-top: 0;
            margin-bottom: 0.7rem;
            font-size: 1.1rem;
        }
        .info-banner ul {
            color: #c9d1d9;
            margin-bottom: 0;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        .info-banner li {
            margin-bottom: 0.4rem;
        }
        .warning-banner {
            background: #2a2317;
            border-left: 4px solid #ff9800;
            padding: 1.2rem 1.3rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }
        .warning-banner h4 {
            color: #ffb74d;
            margin-top: 0;
            margin-bottom: 0.7rem;
            font-size: 1.1rem;
        }
        .warning-banner ul {
            color: #c9d1d9;
            margin-bottom: 0;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        .warning-banner li {
            margin-bottom: 0.4rem;
        }
        .section-divider {
            height: 2px;
            background: linear-gradient(to right, #667eea, #764ba2);
            margin: 2rem 0;
            border: none;
            border-radius: 2px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>Trading Fundamentals</h1>
            <p>Essential knowledge for beginning your investment journey</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 1: BASIC TRADING TERMINOLOGY
    # ==========================================
    
    st.markdown("<h2 style='color: #7c8adb; font-size: 1.6rem; margin-bottom: 1.2rem; margin-top: 0.5rem;'>Essential Trading Terms</h2>", unsafe_allow_html=True)
    
    # Term 1: Stock/Share
    st.markdown("""
        <div class="term-card">
            <h3>Stock (Share)</h3>
            <p><strong>Definition:</strong> A unit of ownership in a company. When you buy a stock, you become a partial owner of that company.</p>
            <p><strong>How it works:</strong> Companies divide their ownership into shares and sell them to raise money. Each share represents a small piece of the company.</p>
            <div class="example">
                <strong>Example:</strong> If you buy 10 shares of Apple at $150 each, you've invested $1,500 and own a tiny fraction of Apple Inc.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 2: Market Order vs Limit Order
    st.markdown("""
        <div class="term-card">
            <h3>Market Order vs Limit Order</h3>
            <p><strong>Market Order:</strong> Buy or sell a stock immediately at the current market price. Guaranteed execution but not guaranteed price.</p>
            <p><strong>Limit Order:</strong> Buy or sell a stock only at a specific price or better. Guaranteed price but not guaranteed execution.</p>
            <div class="example">
                <strong>Example:</strong> Stock trading at $100<br>
                • Market Order: You'll buy immediately at ~$100<br>
                • Limit Order at $95: You'll only buy if price drops to $95 or lower
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 3: Bid and Ask
    st.markdown("""
        <div class="term-card">
            <h3>Bid and Ask Price</h3>
            <p><strong>Bid Price:</strong> The highest price a buyer is willing to pay for a stock.</p>
            <p><strong>Ask Price:</strong> The lowest price a seller is willing to accept for a stock.</p>
            <p><strong>Spread:</strong> The difference between bid and ask prices.</p>
            <div class="example">
                <strong>Example:</strong> Bid: $99.50 | Ask: $100.00 | Spread: $0.50<br>
                You can sell immediately at $99.50 or buy immediately at $100.00
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 4: Bull vs Bear Market
    st.markdown("""
        <div class="term-card">
            <h3>Bull Market vs Bear Market</h3>
            <p><strong>Bull Market:</strong> Period when stock prices are rising or expected to rise (generally 20%+ increase). Investors are optimistic.</p>
            <p><strong>Bear Market:</strong> Period when stock prices are falling or expected to fall (generally 20%+ decline). Investors are pessimistic.</p>
            <div class="example">
                <strong>Memory Tip:</strong> Bulls thrust their horns UP ↗️ | Bears swipe their paws DOWN ↘️
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 5: Portfolio
    st.markdown("""
        <div class="term-card">
            <h3>Portfolio</h3>
            <p><strong>Definition:</strong> The collection of all your investments (stocks, bonds, funds, etc.).</p>
            <p><strong>Diversification:</strong> Spreading investments across different assets to reduce risk.</p>
            <div class="example">
                <strong>Example Portfolio:</strong><br>
                • 50% in S&P 500 Index Fund<br>
                • 30% in Individual Tech Stocks<br>
                • 20% in Bonds
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 6: Dividend
    st.markdown("""
        <div class="term-card">
            <h3>Dividend</h3>
            <p><strong>Definition:</strong> A portion of a company's profits paid to shareholders, usually quarterly.</p>
            <p><strong>Dividend Yield:</strong> Annual dividend divided by stock price, expressed as a percentage.</p>
            <div class="example">
                <strong>Example:</strong> Stock at $100 pays $4 annual dividend = 4% dividend yield<br>
                If you own 100 shares, you receive $400 per year in dividends
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 7: Volatility
    st.markdown("""
        <div class="term-card">
            <h3>Volatility</h3>
            <p><strong>Definition:</strong> How much and how quickly a stock's price changes. High volatility = bigger price swings.</p>
            <p><strong>Beta:</strong> Measures volatility compared to the overall market. Beta > 1 = more volatile than market.</p>
            <div class="example">
                <strong>Example:</strong><br>
                • Low Volatility: Coca-Cola (stable, predictable)<br>
                • High Volatility: Tesla (large price swings)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Term 8: Index Fund
    st.markdown("""
        <div class="term-card">
            <h3>Index Fund</h3>
            <p><strong>Definition:</strong> A fund that tracks a specific market index (like S&P 500) by holding all or most of the stocks in that index.</p>
            <p><strong>Benefits:</strong> Instant diversification, low fees, less risky than individual stocks.</p>
            <div class="example">
                <strong>Example:</strong> An S&P 500 index fund gives you ownership in 500 large U.S. companies with just one purchase
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 2: HOW TO START TRADING
    # ==========================================
    
    st.markdown("<h2 style='color: #7c8adb; font-size: 1.6rem; margin-bottom: 1.2rem;'>How to Start Trading: Step-by-Step</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="step-card">
                <h4>Step 1: Choose a Brokerage</h4>
                <p>Select a platform to buy/sell stocks. Popular options: Fidelity, Charles Schwab, Robinhood, TD Ameritrade</p>
                <p><strong>Look for:</strong> Low/no fees, user-friendly app, good research tools</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="step-card">
                <h4>Step 3: Deposit Money</h4>
                <p>Link your bank account and transfer funds to your brokerage account</p>
                <p><strong>Beginner tip:</strong> Start with an amount you're comfortable potentially losing while learning</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="step-card">
                <h4>Step 5: Make Your First Trade</h4>
                <p>Search for a stock ticker, decide how many shares to buy, and choose order type (market or limit)</p>
                <p><strong>Tip:</strong> Consider starting with an index fund for diversification</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="step-card">
                <h4>Step 2: Open an Account</h4>
                <p>Provide personal information, link bank account, and complete identity verification</p>
                <p><strong>Account types:</strong> Individual, IRA (retirement), or Joint account</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="step-card">
                <h4>Step 4: Research Investments</h4>
                <p>Study companies, read financial news, analyze stock performance</p>
                <p><strong>Key metrics:</strong> P/E ratio, revenue growth, company news, industry trends</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="step-card">
                <h4>Step 6: Monitor & Learn</h4>
                <p>Track your investments regularly, learn from mistakes, adjust strategy as needed</p>
                <p><strong>Remember:</strong> Patience is key. Think long-term!</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 3: BEGINNER TIPS
    # ==========================================
    
    st.markdown("<h2 style='color: #7c8adb; font-size: 1.6rem; margin-bottom: 1.2rem;'>Golden Rules for Beginners</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="info-banner">
            <h4>DO These Things</h4>
            <ul>
                <li><strong>Start small:</strong> Begin with amounts you can afford to lose while learning</li>
                <li><strong>Diversify:</strong> Don't put all your money in one stock</li>
                <li><strong>Think long-term:</strong> Most wealth is built over years, not days</li>
                <li><strong>Keep learning:</strong> Read books, follow financial news, learn from mistakes</li>
                <li><strong>Use stop-losses:</strong> Set automatic sell orders to limit losses</li>
                <li><strong>Invest regularly:</strong> Dollar-cost averaging reduces timing risk</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="warning-banner">
            <h4>DON'T Do These Things</h4>
            <ul>
                <li><strong>Don't invest money you need:</strong> Only invest what you can afford to lose</li>
                <li><strong>Don't panic sell:</strong> Market drops are normal; avoid emotional decisions</li>
                <li><strong>Don't chase trends:</strong> By the time everyone's talking about a stock, you might be late</li>
                <li><strong>Don't day trade as a beginner:</strong> It's risky and most people lose money</li>
                <li><strong>Don't ignore fees:</strong> High fees eat into your returns over time</li>
                <li><strong>Don't invest in what you don't understand:</strong> Research before buying</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # ==========================================
    # SECTION 4: FIRST INVESTMENT STRATEGIES
    # ==========================================
    
    st.markdown("<h2 style='color: #7c8adb; font-size: 1.6rem; margin-bottom: 1.2rem;'>Best Strategies for Beginners</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="term-card">
                <h3>Index Fund Investing</h3>
                <p><strong>Best for:</strong> Complete beginners, hands-off investors</p>
                <p><strong>How it works:</strong> Buy an S&P 500 or total market index fund. You get instant diversification across hundreds of companies.</p>
                <p><strong>Risk level:</strong> Low to Medium</p>
                <div class="example">
                    <strong>Recommended:</strong> Start with 80% of your portfolio in index funds like VOO or VTI
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="term-card">
                <h3>Dollar-Cost Averaging</h3>
                <p><strong>Best for:</strong> Building wealth consistently</p>
                <p><strong>How it works:</strong> Invest a fixed amount regularly (e.g., $200/month) regardless of market conditions.</p>
                <p><strong>Risk level:</strong> Low</p>
                <div class="example">
                    <strong>Benefit:</strong> You buy more shares when prices are low, fewer when high - automatic smart buying
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="term-card">
                <h3>Blue-Chip Stocks</h3>
                <p><strong>Best for:</strong> Learning about individual stocks</p>
                <p><strong>How it works:</strong> Buy stock in large, established, financially stable companies (e.g., Apple, Microsoft, Johnson & Johnson).</p>
                <p><strong>Risk level:</strong> Low to Medium</p>
                <div class="example">
                    <strong>Tip:</strong> Start with companies whose products you use and understand
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="term-card">
                <h3>Robo-Advisors</h3>
                <p><strong>Best for:</strong> Completely hands-off investing</p>
                <p><strong>How it works:</strong> Automated services (like Betterment, Wealthfront) build and manage a diversified portfolio for you.</p>
                <p><strong>Risk level:</strong> Low to Medium</p>
                <div class="example">
                    <strong>Cost:</strong> Usually 0.25% annual fee - good for beginners who want professional management
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Final disclaimer
    st.markdown("""
        <div style="background: #1e2128; border-left: 4px solid #6c757d; padding: 1.2rem 1.3rem; border-radius: 8px; margin-top: 2rem;">
            <p style="margin: 0; color: #c9d1d9; font-size: 0.95rem;">
                <strong>⚠️ Important Disclaimer:</strong> This information is for educational purposes only and should not be considered financial advice. 
                Investing involves risk, including possible loss of principal. Always do your own research and consider consulting with a qualified 
                financial advisor before making investment decisions.
            </p>
        </div>
    """, unsafe_allow_html=True)