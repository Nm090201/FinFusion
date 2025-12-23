import os
from dotenv import load_dotenv
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import finnhub
from datetime import datetime
import plotly.express as px
import requests
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Import the tab rendering functions
from tab1 import render_tab1
from tab2 import render_tab2
from tab3 import render_tab3  # NEW Brave + OpenAI version
from tab4 import render_tab4

load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Page config
st.set_page_config(page_title="FinFusion", page_icon="📈", layout="wide")

# Enhanced CSS with bigger elements
st.markdown("""
<style>
    /* Base font size increase */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        max-width: 95% !important;
    }
    
/* Main title - BIGGER - WHITE */
    .main-title {
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: bold;
        color: white !important;
        padding: 20px 20px;
        margin-top: -20px;
        margin-bottom: 20px;
    }
    
    /* Tabs styling - BIGGER */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 90px !important;
        padding-left: 50px !important;
        padding-right: 50px !important;
        background-color: #2d2d44;
        border-radius: 12px;
        border: 2px solid #3d3d5c;
        font-size: 24px !important;
        font-weight: 700;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3d3d5c;
        border-color: #5a5a7a;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 25px;
    }
    
    /* Market indices - BIGGER */
    .market-indices {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        margin-top: 15px;
    }
    
    /* Headers - BIGGER */
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    h2 {
        font-size: 2.5rem !important;
        font-weight: 600 !important;
        margin-bottom: 1.2rem !important;
    }
    
    h3 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    h4 {
        font-size: 1.6rem !important;
        font-weight: 500 !important;
    }
    
    /* Metrics - BIGGER */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.2rem !important;
    }
    
    /* Buttons - BIGGER */
    .stButton > button {
        font-size: 1.2rem !important;
        padding: 15px 30px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        min-height: 55px !important;
    }
    
    /* Input fields - BIGGER */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        font-size: 1.1rem !important;
        padding: 12px !important;
        min-height: 50px !important;
    }
    
    /* Text areas - BIGGER */
    .stTextArea > div > div > textarea {
        font-size: 1.1rem !important;
        padding: 12px !important;
    }
    
    /* Dataframes - BIGGER */
    .dataframe {
        font-size: 1.1rem !important;
    }
    
    .dataframe th {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    .dataframe td {
        font-size: 1.1rem !important;
        padding: 10px !important;
    }
    
    /* Sidebar - BIGGER */
    [data-testid="stSidebar"] {
        padding: 2rem 1.5rem !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        font-size: 1.1rem !important;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 2rem !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 1.5rem !important;
    }
    
    /* Info boxes - BIGGER */
    .stAlert {
        font-size: 1.1rem !important;
        padding: 15px !important;
    }
    
    /* Expander - BIGGER */
    .streamlit-expanderHeader {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        padding: 15px !important;
    }
    
    /* Radio buttons and checkboxes - BIGGER */
    .stRadio > label,
    .stCheckbox > label {
        font-size: 1.2rem !important;
    }
    
    /* Captions - BIGGER */
    .caption, small, .stCaption {
        font-size: 1rem !important;
    }
    
    /* Plotly charts - ensure they're visible */
    .js-plotly-plot {
        min-height: 500px !important;
    }
    
    /* Cards and containers - BIGGER padding */
    div[data-testid="column"] > div {
        padding: 15px !important;
    }
    
    /* Markdown text - BIGGER */
    .markdown-text-container {
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
    }
    
    /* Lists - BIGGER */
    ul, ol {
        font-size: 1.1rem !important;
        line-height: 1.8 !important;
    }
    
    li {
        margin-bottom: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">FinFusion : AI-Powered Investment Portfolio Analyzer</h1>', unsafe_allow_html=True)

# SESSION STATE INITIALIZATION
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'memory' not in st.session_state:
    st.session_state.memory = None
if 'data_store' not in st.session_state:
    st.session_state.data_store = {'quant_df': None}
if 'latest_portfolio' not in st.session_state:
    st.session_state.latest_portfolio = None
if 'generate_portfolio' not in st.session_state:
    st.session_state.generate_portfolio = False
if 'portfolio_params' not in st.session_state:
    st.session_state.portfolio_params = None

# LOAD DATA (Cached)
@st.cache_data
def load_data():
    news_df = pd.read_csv('data/csv/fin_data/final_news.csv')
    quant_df = pd.read_csv('data/csv/fin_data/quantitative_summary.csv')
    return news_df, quant_df

news_df, quant_df = load_data()
st.session_state.data_store['quant_df'] = quant_df

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# ===========================
# MAIN UI WITH BIGGER TABS
# ===========================
tab1, tab2, tab3, tab4 = st.tabs([
    "Technical Analysis", 
    "Market Metrics", 
    "Strategy Assistant",  # Updated with Brave + OpenAI
    "Learn Trading"
]) 

# TAB 1: Chart
with tab1:
    render_tab1(finnhub_client)

# TAB 2: Economic Dashboard
with tab2:
    render_tab2(quant_df)

# TAB 3: AI Strategy Assistant (NOW with Brave + OpenAI)
with tab3:
    render_tab3(quant_df, news_df)  # CHANGED: Removed finnhub_client parameter

# TAB 4: Education
with tab4:
    render_tab4()

# SIDEBAR - Enhanced with bigger text
with st.sidebar:
    st.markdown("## FinFusion")
    st.markdown("*AI-Powered Market Intelligence*")
    
    st.markdown("---")
    
    st.info("""
    Transform complex financial data into actionable insights through real-time analysis and AI assistance.
    """)
    
    st.markdown("### What You Can Do")
    st.markdown("""
    - **Analyze** - Professional charts & indicators
    - **Monitor** - Real-time economic data
    - **Ask** - AI-powered insights (Brave + OpenAI)
    - **Learn** - Build your market knowledge
    """)
    
    st.markdown("---")
    
    st.caption("Built for traders, analysts, and students")
    st.caption("© 2024 FinFusion")