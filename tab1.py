import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def send_slack_notification(webhook_url, ipo_data):
    """
    Send IPO notification to Slack channel
    
    Args:
        webhook_url: Slack webhook URL
        ipo_data: Dictionary containing IPO details
    """
    try:
        # Format price
        price_str = f"${ipo_data['price']}" if ipo_data['price'] and ipo_data['price'] != 'N/A' else "TBD"
        
        # Format number of shares
        shares_str = f"{int(ipo_data['numberOfShares']):,}" if ipo_data['numberOfShares'] else "N/A"
        
        # Create Slack message with rich formatting
        slack_message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New IPO Alert!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Company:*\n{ipo_data['name']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Symbol:*\n{ipo_data['symbol']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*IPO Date:*\n{ipo_data['date']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Price:*\n{price_str}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Shares Offered:*\n{shares_str}"
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
        }
        
        # Send POST request to Slack webhook
        response = requests.post(
            webhook_url,
            data=json.dumps(slack_message),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            st.error(f"Failed to send Slack notification: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Error sending Slack notification: {e}")
        return False

def render_tab1(finnhub_client):
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    """
    Renders the Chart tab content
    
    Args:
        finnhub_client: Initialized Finnhub client object
    """
    
    # ===========================
    # TRADINGVIEW LIVE CHART
    # ===========================
    st.markdown('<h1 style="text-align:center; font-size:2.5rem;">Live Trading Chart</h1>', unsafe_allow_html=True)
    st.markdown("")
    
    # Symbol selector for the chart
    col_chart1, col_chart2, col_chart3 = st.columns([1, 2, 1])
    
    with col_chart2:
        chart_symbol = st.selectbox(
            "Select Symbol:",
            ["SP500", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"],
            index=0,
            key="chart_symbol_selector"
        )
    
    # TradingView Advanced Chart Widget
    tradingview_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:100%; width:100%; margin:0; padding:0;">
      <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px); width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
      {{
      "width": "100%",
      "height": "600",
      "symbol": "{chart_symbol}",
      "interval": "D",
      "timezone": "America/New_York",
      "theme": "light",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "calendar": false,
      "hide_top_toolbar": false,
      "hide_legend": false,
      "save_image": false,
      "support_host": "https://www.tradingview.com"
    }}
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    
    # Render the TradingView chart
    components.html(tradingview_html, height=650, scrolling=False)
    
    st.markdown("---")
    # ===========================
    # LIVE INDEX PRICES (SMALLER)
    # ===========================
    st.markdown("")
    
    # Create two columns for the indices
    col1, col2 = st.columns(2)
    
    # Placeholder for live data
    try:
        # Fetch live data for VOO (S&P 500 ETF) and QQQ (NASDAQ-100 ETF)
        voo_quote = finnhub_client.quote('VOO')
        qqq_quote = finnhub_client.quote('QQQ')
        
        # VOO (S&P 500)
        with col1:
            voo_price = voo_quote['c']  # current price
            voo_change = voo_quote['d']  # change
            voo_change_pct = voo_quote['dp']  # change percentage
            
            # Determine color based on change
            voo_color = '#22c55e' if voo_change >= 0 else '#ef4444'
            voo_symbol = '▲' if voo_change >= 0 else '▼'
            
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid {voo_color};">
                    <h3 style="margin: 0; color: #333; font-size: 1.1rem;">S&P 500 (VOO)</h3>
                    <h2 style="margin: 8px 0; font-size: 1.8rem; font-weight: bold; color: #000;">${voo_price:.2f}</h2>
                    <p style="margin: 0; color: {voo_color}; font-weight: bold; font-size: 1rem;">
                        {voo_symbol} ${abs(voo_change):.2f} ({voo_change_pct:+.2f}%)
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # QQQ (NASDAQ-100)
        with col2:
            qqq_price = qqq_quote['c']  # current price
            qqq_change = qqq_quote['d']  # change
            qqq_change_pct = qqq_quote['dp']  # change percentage
            
            # Determine color based on change
            qqq_color = '#22c55e' if qqq_change >= 0 else '#ef4444'
            qqq_symbol = '▲' if qqq_change >= 0 else '▼'
            
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid {qqq_color};">
                    <h3 style="margin: 0; color: #333; font-size: 1.1rem;">NASDAQ-100 (QQQ)</h3>
                    <h2 style="margin: 8px 0; font-size: 1.8rem; font-weight: bold; color: #000;">${qqq_price:.2f}</h2>
                    <p style="margin: 0; color: {qqq_color}; font-weight: bold; font-size: 1rem;">
                        {qqq_symbol} ${abs(qqq_change):.2f} ({qqq_change_pct:+.2f}%)
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error fetching live index data: {e}")
        
        # Fallback display if API fails
        with col1:
            st.markdown("""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #333; font-size: 1.1rem;">S&P 500 (VOO)</h3>
                    <h2 style="margin: 8px 0; font-size: 1.8rem; font-weight: bold; color: #000;">Loading...</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                    <h3 style="margin: 0; color: #333; font-size: 1.1rem;">NASDAQ-100 (QQQ)</h3>
                    <h2 style="margin: 8px 0; font-size: 1.8rem; font-weight: bold; color: #000;">Loading...</h2>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===========================
    # MARKET MOVERS & IPO CALENDAR IN ONE LINE
    # ===========================
    
    # Create two columns - Market Movers | IPO Calendar
    movers_col, ipo_col = st.columns([1.5, 1.5])

    # COLUMN 1 - MARKET MOVERS
    with movers_col:
        st.markdown('<div style="padding-right: 15px;">', unsafe_allow_html=True)
        st.markdown("## Top Movers")
        st.markdown("")
        
        try:
            # Fetch data from Alpha Vantage
            url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=HMBC15KFXX2F7LOH'
            r = requests.get(url)
            data = r.json()
            
            # Convert to DataFrames
            top_gainers = pd.DataFrame(data.get('top_gainers', []))
            top_losers = pd.DataFrame(data.get('top_losers', []))
            most_active = pd.DataFrame(data.get('most_actively_traded', []))

            # FILTER OUT PENNY STOCKS AND LOW VOLUME
            def filter_stocks(df, min_price=5.0, min_volume=100000):
                """Filter out penny stocks and low volume stocks"""
                if df.empty:
                    return df
                
                # Convert price and volume to numeric
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
                
                # Filter: price >= $5 and volume >= 100k
                filtered = df[(df['price'] >= min_price) & (df['volume'] >= min_volume)]
                
                return filtered
            
            # Apply filters
            top_gainers = filter_stocks(top_gainers)
            top_losers = filter_stocks(top_losers)
            most_active = filter_stocks(most_active)
            
            # Create tabs
            tab_gainers, tab_losers, tab_volume = st.tabs(["Gainers", "Losers", "Volume"])
            
            # GAINERS TAB
            with tab_gainers:
                if not top_gainers.empty:
                    top_3_gainers = top_gainers.head(3).copy()
                    
                    for idx, row in top_3_gainers.iterrows():
                        ticker = row.get('ticker', 'N/A')
                        price = float(row.get('price', 0))
                        change_pct = row.get('change_percentage', '0%')
                        volume = row.get('volume', 0)
                        
                        st.markdown(f"**{ticker}** - ${price:.2f}")
                        st.markdown(f"<span style='color: #22c55e; font-weight: bold;'>{change_pct}</span>", unsafe_allow_html=True)
                        st.caption(f"Vol: {int(volume):,}")
                        st.markdown("---")
                else:
                    st.info("No significant gainers")
            
            # LOSERS TAB
            with tab_losers:
                if not top_losers.empty:
                    top_3_losers = top_losers.head(3).copy()
                    
                    for idx, row in top_3_losers.iterrows():
                        ticker = row.get('ticker', 'N/A')
                        price = float(row.get('price', 0))
                        change_pct = row.get('change_percentage', '0%')
                        volume = row.get('volume', 0)
                        
                        st.markdown(f"**{ticker}** - ${price:.2f}")
                        st.markdown(f"<span style='color: #ef4444; font-weight: bold;'>{change_pct}</span>", unsafe_allow_html=True)
                        st.caption(f"Vol: {int(volume):,}")
                        st.markdown("---")
                else:
                    st.info("No significant losers")
            
            # VOLUME TAB
            with tab_volume:
                if not most_active.empty:
                    top_3_active = most_active.head(3).copy()
                    
                    for idx, row in top_3_active.iterrows():
                        ticker = row.get('ticker', 'N/A')
                        price = float(row.get('price', 0))
                        change_pct = row.get('change_percentage', '0%')
                        volume = row.get('volume', 0)
                        
                        change_val = float(change_pct.replace('%', ''))
                        color = '#22c55e' if change_val >= 0 else '#ef4444'
                        
                        st.markdown(f"**{ticker}** - ${price:.2f}")
                        st.markdown(f"<span style='color: {color}; font-weight: bold;'>{change_pct}</span>", unsafe_allow_html=True)
                        st.caption(f"Vol: {int(volume):,}")
                        st.markdown("---")
                else:
                    st.info("No significant volume")
            
        except Exception as e:
            st.error(f"Unable to fetch market movers: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # COLUMN 2 - IPO CALENDAR WITH SLACK NOTIFICATIONS
    with ipo_col:
        st.markdown('<div style="padding-left: 15px;">', unsafe_allow_html=True)
        st.markdown("## IPO Calendar")
        st.markdown("")
        
        # Initialize session state for tracking sent notifications
        if 'notified_ipos' not in st.session_state:
            st.session_state.notified_ipos = set()
        
        # Check if Slack webhook is configured
        if not SLACK_WEBHOOK_URL:
            st.warning("Slack webhook not configured in .env file")
            enable_notifications = False
        else:
            enable_notifications = st.text("")
        
        try:
            # Calculate date range (today and next 30 days)
            today = datetime.now()
            end_date = today + timedelta(days=30)
            
            # Format dates as YYYY-MM-DD
            from_date = today.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Fetch IPO calendar
            ipo_data = finnhub_client.ipo_calendar(_from=from_date, to=to_date)
            ipo_list = ipo_data.get('ipoCalendar', [])
            
            if ipo_list:
                # Create a dataframe for better display
                ipo_df = pd.DataFrame(ipo_list)
                
                # Select only the columns we want
                if not ipo_df.empty:
                    display_df = ipo_df[['date', 'name', 'symbol', 'numberOfShares', 'price']].copy()
                    
                    # Sort by date and limit to 5
                    display_df = display_df.sort_values('date').head(5)
                    
                    # Check for new IPOs and send notifications
                    if enable_notifications and SLACK_WEBHOOK_URL:
                        new_notifications = 0
                        
                        for idx, row in display_df.iterrows():
                            # Create unique identifier for IPO
                            ipo_id = f"{row['symbol']}_{row['date']}"
                            
                            # Check if already notified in this session
                            if ipo_id not in st.session_state.notified_ipos:
                                ipo_notification_data = {
                                    'name': row['name'],
                                    'symbol': row['symbol'],
                                    'date': row['date'],
                                    'price': row.get('price', 'N/A'),
                                    'numberOfShares': row.get('numberOfShares', 'N/A'),
                                    'exchange': row.get('exchange', 'N/A')
                                }
                                
                                if send_slack_notification(SLACK_WEBHOOK_URL, ipo_notification_data):
                                    st.session_state.notified_ipos.add(ipo_id)
                                    new_notifications += 1
                        
                        if new_notifications > 0:
                            st.success(f"🔔 {new_notifications} new IPO notification(s) sent to Slack!")
                    
                    # Display compact list
                    for idx, row in display_df.iterrows():
                        date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%b %d')
                        
                        st.markdown(f"**{row['symbol']}**")
                        st.caption(f"{formatted_date}")
                        st.caption(f"{row['name'][:40]}{'...' if len(row['name']) > 40 else ''}")
                        st.markdown("---")
                    
                    st.caption(f"{len(display_df)} upcoming")
                else:
                    st.info("No upcoming IPOs")
            else:
                st.info("No IPOs")
                
        except Exception as e:
            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ===========================
    # MARKET NEWS (FULL WIDTH BELOW)
    # ===========================
    
    st.markdown("# Market News")
    st.markdown("")

    try:
        # Fetch general news once
        general_news = finnhub_client.general_news('general', min_id=0)
        
        # Extract unique categories
        available_categories = set()
        for article in general_news:
            category = article.get('category', 'general')
            if category:
                available_categories.add(category.title())
        
        # Category filter dropdown
        category_options = ["All Categories"] + sorted(list(available_categories))
        selected_category = st.selectbox(
            "Filter by category:",
            category_options,
            index=0,
            key="news_filter"
        )
        
        st.markdown("")
        
        # Category color mapping
        category_colors = {
            'technology': '#3b82f6',
            'business': '#10b981',
            'finance': '#f59e0b',
            'general': '#6b7280'
        }
        
        # Filter news
        if selected_category == "All Categories":
            filtered_news = general_news
        else:
            filtered_news = [
                article for article in general_news 
                if article.get('category', 'general').title() == selected_category
            ]
        
        # Display news
        if not filtered_news:
            st.info(f"No news in {selected_category} category")
        else:
            for article in filtered_news[:6]:  # Show 6 articles
                category = article.get('category', 'general')
                color = category_colors.get(category.lower(), '#6b7280')
                
                st.markdown(f"**{article['headline']}**")
                
                date = datetime.fromtimestamp(article['datetime']).strftime('%b %d')
                source = article.get('source', 'Unknown')
                
                st.markdown(f"""
                    <span style="color: #666; font-size: 0.8rem;">📅 {date} | 🔗 {source}</span>
                """, unsafe_allow_html=True)
                
                st.markdown(f"[Read more →]({article['url']})")
                st.markdown("---")
            
    except Exception as e:
        st.error(f"Error loading news: {e}")