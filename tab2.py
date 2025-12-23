import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import base64
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

def render_tab2(quant_df):
    """Render Tab 3: Economic Indicators Dashboard"""
    
    # Get API key from environment variable
    API_KEY = os.getenv('FRED_API_KEY')
    
    # Validate API key
    if not API_KEY:
        st.error("⚠️ FRED API key not found!")
        st.info("Please add your FRED_API_KEY to the .env file")
        return
    
    st.title("US Economic Indicators")
    
    # Add refresh button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Fetch all data
    with st.spinner("Loading economic data..."):
        data = fetch_all_economic_data(API_KEY)
    
    if data.get('error'):
        st.error(f"⚠️ {data['error']}")
        st.info("Make sure your FRED API key in the .env file is valid")
        return
    
    # Main Economic Indicators (Larger Cards)
    st.markdown("### Key Economic Indicators")
    col1, col2, col3, col4 = st.columns(4)

    debt_to_gdp = (data['debt']['value'] / data['gdp']['value']) * 100
    
    with col1:
        display_main_metric(
            "Real GDP",
            f"${data['gdp']['value']:,.2f}B",
            data['gdp']['trend'],
            data['gdp']['date'],
            ""
        )
    
    with col2:
        display_main_metric(
            "Inflation Rate",
            f"{data['inflation']['value']:.2f}%",
            data['inflation']['trend'],
            data['inflation']['date'],
            ""
        )
    
    with col3:
        display_main_metric(
            "Federal Debt",
            f"${data['debt']['value']:,.2f}B",
            data['debt']['trend'],
            data['debt']['date'],
            ""
        )

    with col4:
        # Calculate trend for Debt-to-GDP ratio
        if len(data['debt']['history']) >= 5 and len(data['gdp']['history']) >= 5:
            old_ratio = (float(data['debt']['history'][-5]['value']) / float(data['gdp']['history'][-5]['value'])) * 100
            debt_gdp_trend = debt_to_gdp - old_ratio
        else:
            debt_gdp_trend = 0
        
        display_main_metric(
            "Debt-to-GDP Ratio",
            f"{debt_to_gdp:.2f}%",
            debt_gdp_trend,
            data['debt']['date'],
            ""
        )
    
    # Commodity Prices
    st.markdown("---")
    st.markdown("### Commodity Prices")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_commodity_metric(
            "Natural Gas",
            f"${data['naturalGas']['value']:.2f}",
            "per MMBtu",
            data['naturalGas']['trend'],
            data['naturalGas']['date']
        )
    
    with col2:
        display_commodity_metric(
            "Crude Oil (WTI)",
            f"${data['crudeOil']['value']:.2f}",
            "per barrel",
            data['crudeOil']['trend'],
            data['crudeOil']['date']
        )
    
    with col3:
        display_commodity_metric(
            "Copper",
            f"${data['copper']['value']:,.2f}",
            "per metric ton",
            data['copper']['trend'],
            data['copper']['date']
        )
    
    # US Debt Clock Card with Image
    st.markdown("---")
    st.markdown("### 💰 External Resources")
    display_debt_clock_thumbnail()
    
    # Data update info
    st.markdown("---")
    st.caption("⚠️ Data source: Federal Reserve Economic Data (FRED)")


def fetch_all_economic_data(api_key):
    """Fetch all economic indicators from FRED API"""
    try:
        # Define all API endpoints
        endpoints = {
            'gdp': f"https://api.stlouisfed.org/fred/series/observations?series_id=GDPC1&api_key={api_key}&file_type=json",
            'inflation': f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json&units=pc1",
            'debt': f"https://api.stlouisfed.org/fred/series/observations?series_id=GFDEBTN&api_key={api_key}&file_type=json",
            'naturalGas': f"https://api.stlouisfed.org/fred/series/observations?series_id=DHHNGSP&api_key={api_key}&file_type=json",
            'crudeOil': f"https://api.stlouisfed.org/fred/series/observations?series_id=DCOILWTICO&api_key={api_key}&file_type=json",
            'copper': f"https://api.stlouisfed.org/fred/series/observations?series_id=PCOPPUSDM&api_key={api_key}&file_type=json"
        }
        
        data = {}
        
        for key, url in endpoints.items():
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            
            if 'observations' not in json_data or len(json_data['observations']) == 0:
                return {'error': f'No data available for {key}'}
            
            observations = json_data['observations']
            
            # Filter out observations with missing data (value = '.')
            valid_observations = [
                obs for obs in observations 
                if obs['value'] != '.' and obs['value'] != ''
            ]
            
            if len(valid_observations) == 0:
                return {'error': f'No valid data available for {key}'}
            
            latest = valid_observations[-1]
            
            # Calculate trend (last 5 valid observations)
            trend = 0
            if len(valid_observations) >= 5:
                try:
                    old_val = float(valid_observations[-5]['value'])
                    new_val = float(latest['value'])
                    if old_val != 0:
                        trend = ((new_val - old_val) / old_val) * 100
                except (ValueError, TypeError):
                    trend = 0
            
            # Get last 10 valid observations for history
            history = []
            for obs in valid_observations[-10:]:
                try:
                    history.append({
                        'date': obs['date'],
                        'value': float(obs['value'])
                    })
                except (ValueError, TypeError):
                    continue
            
            data[key] = {
                'value': float(latest['value']),
                'date': latest['date'],
                'trend': trend,
                'history': history
            }
        
        return data
        
    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {str(e)}'}
    except ValueError as e:
        return {'error': f'Invalid data format: {str(e)}'}
    except Exception as e:
        return {'error': f'Error fetching data: {str(e)}'}


def get_image_base64(image_path):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None


def display_debt_clock_thumbnail():
    """Display clickable thumbnail with uploaded US Debt Clock image - Full Width"""
    # Image path - in same folder as project
    image_path = "debt_clock.png"
    
    if Path(image_path).exists():
        img_base64 = get_image_base64(image_path)
        
        if img_base64:
            # Display with image thumbnail - Full Width
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
                    width: 100%;
                '>
                    <h3 style='color: white; text-align: center; margin-bottom: 20px; font-size: 20px;'>
                        🏛️ US Debt Clock - Live Dashboard
                    </h3>
                    <a href="https://www.usdebtclock.org/" target="_blank" style="text-decoration: none; display: block;">
                        <img 
                            src="data:image/png;base64,{img_base64}" 
                            style='
                                width: 100%;
                                border-radius: 10px;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                                transition: transform 0.3s ease, box-shadow 0.3s ease;
                                cursor: pointer;
                                display: block;
                            '
                            onmouseover="this.style.transform='scale(1.01)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.6)'"
                            onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.4)'"
                            alt="US Debt Clock Dashboard"
                        />
                    </a>
                    <div style='text-align: center; margin-top: 20px;'>
                        <a href="https://www.usdebtclock.org/" target="_blank"
                           style='
                               background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                               color: white;
                               padding: 14px 35px;
                               border-radius: 25px;
                               text-decoration: none;
                               font-weight: bold;
                               display: inline-block;
                               transition: all 0.3s ease;
                               box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                               font-size: 16px;
                           '
                           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.3)'"
                           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)'">
                            View Live Debt Clock ↗️
                        </a>
                    </div>
                    <p style='color: rgba(255,255,255,0.7); text-align: center; margin-top: 12px; font-size: 14px;'>
                        Click to view real-time US economic data, debt, spending, and more
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Failed to load debt_clock.png")
            display_debt_clock_card_fallback()
    else:
        st.warning("⚠️ Image file 'debt_clock.png' not found in project directory.")
        display_debt_clock_card_fallback()


def display_debt_clock_card_fallback():
    """Fallback card if image is not found"""
    st.markdown("""
        <a href="https://www.usdebtclock.org/" target="_blank" style="text-decoration: none;">
            <div style='
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                padding: 30px;
                border-radius: 15px;
                color: white;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
                text-align: center;
            ' onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 24px rgba(0,0,0,0.3)'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 16px rgba(0,0,0,0.2)'">
                
                <div style='font-size: 64px; margin-bottom: 15px;'>
                    🏛️
                </div>
                
                <h2 style='margin-bottom: 10px; color: white;'>
                    US Debt Clock
                </h2>
                
                <p style='font-size: 16px; opacity: 0.9; margin-bottom: 20px;'>
                    View real-time tracking of US national debt,<br/>
                    spending, revenue, and economic indicators
                </p>
                
                <div style='
                    display: inline-block;
                    background-color: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 20px;
                    font-weight: bold;
                '>
                    Click to Open Live Dashboard ↗️
                </div>
            </div>
        </a>
    """, unsafe_allow_html=True)


def display_main_metric(title, value, trend, date, icon):
    """Display main economic indicator with larger styling"""
    trend_color = "🟢" if trend > 0 else "🔴" if trend < 0 else "⚪"
    trend_text = f"{trend:+.2f}%" if trend != 0 else "0.00%"
    
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
        <h4 style="margin: 0; color: #555;">{icon} {title}</h4>
        <h1 style="margin: 10px 0; color: #1f77b4;">{value}</h1>
        <p style="margin: 5px; color: #888; font-size: 16px;">{trend_color} {trend_text} (5-period trend)</p>
        <p style="margin: 0; color: #888; font-size: 14px;">As of: {date}</p>
    </div>
    """, unsafe_allow_html=True)


def display_commodity_metric(title, value, unit, trend, date):
    """Display commodity price metric"""
    trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➖"
    trend_text = f"{trend:+.2f}%" if trend != 0 else "0.00%"
    
    st.markdown(f"**{title}**")
    st.metric(
        label=unit,
        value=value,
        delta=f"{trend_text} {trend_icon}"
    )
    st.caption(f"Updated: {date}")


def display_history_table(data, key, label):
    """Display historical data as table"""
    history = data[key]['history']
    df = pd.DataFrame([
        {
            'Date': obs['date'],
            label: float(obs['value'])
        }
        for obs in history
    ])
    df = df.sort_values('Date', ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_commodity_history(data, key):
    """Display commodity price history"""
    history = data[key]['history']
    for obs in reversed(history[-5:]):  # Show last 5
        st.text(f"{obs['date']}: ${float(obs['value']):.2f}")
