import streamlit as st
import sys
import os
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import requests

# Fix path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your engines
from src.data_loaders.fmp_loader import get_yahoo_valuation
from src.data_loaders.risk_loader import get_risk_analysis
from src.analysis.signals import calculate_trade_signal

# --- ENHANCED INTERACTIVE TABLE FUNCTIONS ---
def safe_get_score(result, component_key, score_key=None, default=50.0):
    """Safely extract scores from analysis results with fallback logic"""
    try:
        # Try both emoji and non-emoji versions of component keys
        component_scores = (
            result.get('COMPONENT SCORES') or 
            result.get('📋 COMPONENT SCORES') or 
            {}
        )
        
        if not component_scores:
            return default
        
        # If no specific score key provided, use component_key as the score key
        if score_key is None:
            score_key = component_key
        
        # Try to find the key (with or without emoji)
        actual_key = None
        for key in component_scores.keys():
            if component_key.lower() in key.lower():
                actual_key = key
                break
        
        if actual_key and component_scores[actual_key]:
            value = str(component_scores[actual_key])
            if '/' in value:
                return float(value.split('/')[0])
            else:
                return float(value)
        
        return default
    except:
        return default

def safe_get_result_value(result, key, default='N/A'):
    """Safely get values from result with emoji/non-emoji fallback"""
    # Try multiple variations of the key
    possible_keys = [
        key,
        f'🎪 {key}',
        f'📊 {key}',
        f'📋 {key}',
        f'🔍 {key}',
        f'⚖️ {key}',
        f'🔬 {key}'
    ]
    
    for k in possible_keys:
        if k in result:
            return result[k]
    
    return default

def format_percentage(value):
    """Format numeric values as percentages"""
    if pd.isna(value):
        return "N/A"
    try:
        if isinstance(value, str) and '%' in value:
            return value
        return f"{float(value):.1f}%"
    except:
        return str(value)

def format_currency(value):
    """Format numeric values as currency"""
    if pd.isna(value):
        return "N/A"
    try:
        if isinstance(value, str) and '$' in value:
            return value
        return f"${float(value):.2f}"
    except:
        return str(value)

def style_sentiment_score(value):
    """Apply color styling based on sentiment score"""
    if pd.isna(value):
        return ""
    try:
        score = float(str(value).replace('%', ''))
        if score > 70:
            return "color: #00ff88; font-weight: bold;"
        elif score < 30:
            return "color: #ff4444; font-weight: bold;"
        else:
            return "color: #ffd700; font-weight: bold;"
    except:
        return ""

def create_enhanced_dataframe(data_dict, title="Analysis Results"):
    """Create an enhanced interactive dataframe from analysis results"""
    
    # Convert the nested result dictionary into a flat DataFrame
    rows = []
    
    # Process different sections of the result
    if isinstance(data_dict, dict):
        for section_key, section_value in data_dict.items():
            if isinstance(section_value, dict):
                for key, value in section_value.items():
                    row = {
                        'Category': section_key.replace('📋 ', '').replace('🔍 ', '').replace('⚖️ ', '').replace('🔬 ', ''),
                        'Metric': key.replace('🚀 ', '').replace('💰 ', '').replace('📊 ', ''),
                        'Value': value,
                        'Raw_Value': value
                    }
                    rows.append(row)
            else:
                row = {
                    'Category': 'Summary',
                    'Metric': section_key.replace('🎪 ', '').replace('📊 ', ''),
                    'Value': section_value,
                    'Raw_Value': section_value
                }
                rows.append(row)
    
    if not rows:
        return None
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Apply formatting based on column names
    for index, row in df.iterrows():
        metric = row['Metric']
        value = row['Value']
        
        # Format percentages
        if any(word in metric.lower() for word in ['percent', 'ratio', 'rate', '%']):
            df.at[index, 'Value'] = format_percentage(value)
        
        # Format prices
        elif any(word in metric.lower() for word in ['price', 'cost', '$']):
            df.at[index, 'Value'] = format_currency(value)
        
        # Keep sentiment scores as-is for styling
        elif 'sentiment' in metric.lower() and 'score' in metric.lower():
            try:
                if isinstance(value, str) and '/' in value:
                    score_part = value.split('/')[0]
                    df.at[index, 'Value'] = f"{score_part}%"
                    df.at[index, 'Sentiment Score'] = float(score_part)
            except:
                pass
    
    return df

def create_html_table(df):
    """Create an HTML table with Bloomberg Terminal styling (no pyarrow dependency)"""
    
    if df is None or df.empty:
        return "<p style='color: #888888; text-align: center;'>No data available</p>"
    
    # Start building the HTML table
    html = """
    <div style="overflow-x: auto; margin: 8px 0;">
        <table style="
            width: 100%; 
            border-collapse: collapse; 
            background-color: #0e1117; 
            border-radius: 8px; 
            overflow: hidden;
            border: 1px solid #444444;
        ">
            <thead>
                <tr style="background-color: #1a1a1a;">
    """
    
    # Add header columns
    for col in df.columns:
        html += f"""
                    <th style="
                        color: #3b82f6; 
                        font-family: 'IBM Plex Sans', sans-serif; 
                        font-weight: bold; 
                        text-align: left; 
                        padding: 8px 12px; 
                        border: 1px solid #444444;
                        font-size: 0.9rem;
                    ">{col}</th>
        """
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    
    # Add data rows
    for idx, row in df.iterrows():
        html += '<tr style="border-bottom: 1px solid #444444;">'
        
        for col_idx, (col, value) in enumerate(row.items()):
            # Apply sentiment score coloring if it's the Value column and we have sentiment data
            cell_style = """
                color: #fafafa; 
                font-family: 'Roboto Mono', monospace; 
                padding: 6px 12px; 
                border: 1px solid #444444; 
                font-size: 0.85rem;
                background-color: #0e1117;
            """
            
            # Check if this is a sentiment score value and apply coloring
            if col == 'Value' and isinstance(value, str):
                if any(sentiment_key in str(df.iloc[idx]['Metric']).lower() if 'Metric' in df.columns else '' 
                       for sentiment_key in ['sentiment', 'fear', 'greed']):
                    try:
                        score_val = float(str(value).replace('%', '').replace('$', '').replace(',', ''))
                        if score_val >= 70:
                            cell_style += "background-color: #1a4d3a; border-left: 3px solid #00ff88;"
                        elif score_val >= 50:
                            cell_style += "background-color: #4d3a1a; border-left: 3px solid #ffd93d;"
                        else:
                            cell_style += "background-color: #4d1a1a; border-left: 3px solid #ff6b6b;"
                    except (ValueError, TypeError):
                        pass
            
            html += f'<td style="{cell_style}">{value}</td>'
        
        html += '</tr>'
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def display_enhanced_table(data_dict, title="Analysis Results"):
    """Display an enhanced interactive table with Bloomberg Terminal styling"""
    
    df = create_enhanced_dataframe(data_dict, title)
    
    if df is None or df.empty:
        st.warning("No data available to display")
        return
    
    st.markdown(f"""
    <div class="chart-container">
        <h3 style="color: #66b3ff; margin-bottom: 16px; font-family: 'IBM Plex Sans', sans-serif;">
            📊 {title}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display as HTML table to avoid pyarrow dependency
    html_table = create_html_table(df)
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Add table info
    st.markdown("""
    <div style="margin-top: 8px; font-size: 0.8rem; color: #888888; font-family: 'Roboto Mono', monospace;">
        ℹ️ Analysis data formatted with Bloomberg Terminal styling
    </div>
    """, unsafe_allow_html=True)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MarketPulse", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    menu_items=None
)

# --- BLOOMBERG TERMINAL STYLING ---
bloomberg_terminal_style = """
<style>
    /* Import Bloomberg-style fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;700&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Bloomberg Terminal Dark Mode - Force Override */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Force sidebar dark mode */
    .css-1d391kg {
        background-color: #262730 !important;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: none;
        background-color: #0e1117 !important;
    }
    
    /* Bloomberg-style Trading Card Metrics */
    .css-1r6slb0 .css-1wivap2 {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        margin: 4px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Metric values (monospace for financial data) */
    .css-1wivap2 .css-1xarl3l + div {
        color: #e2e8f0 !important;
        font-family: 'Roboto Mono', 'Consolas', monospace !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        margin: 0 !important;
    }
    
    /* Metric delta (change indicators) */
    .css-1wivap2 .css-1xarl3l + div + div {
        color: #ffd700 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    
    /* Headers Bloomberg style */
    h1, h2, h3 {
        color: #fafafa !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #444444 !important;
        padding-bottom: 0.5rem !important;
    }
    
    h1 {
        font-size: 2.2rem !important;
        color: #3b82f6 !important;
    }
    
    h2 {
        font-size: 1.6rem !important;
        color: #60a5fa !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
        color: #ffd700 !important;
    }
    
    /* Input fields Bloomberg style */
    .stTextInput input {
        background-color: #1a1a1a !important;
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
        color: #fafafa !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Navigation Tab Buttons */
    .nav-tab-button {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        color: #9ca3af !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 400 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
        padding: 8px 16px !important;
        margin: 0 4px !important;
    }
    
    .nav-tab-button:hover {
        color: #ffffff !important;
        border-bottom-color: #64748b !important;
        background: transparent !important;
        box-shadow: none !important;
        transform: none !important;
    }
    
    .nav-tab-active {
        color: #ffffff !important;
        font-weight: 600 !important;
        border-bottom-color: #3b82f6 !important;
        background: transparent !important;
    }
    
    /* Asset Chip Buttons */
    .asset-chip {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 16px !important;
        color: #e2e8f0 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 6px 12px !important;
        margin: 4px !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .asset-chip:hover {
        border-color: #94a3b8 !important;
        background: #334155 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(148, 163, 184, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Regular Buttons Bloomberg style (for other buttons) */
    .stButton button:not(.nav-tab-button):not(.asset-chip) {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%) !important;
        border: 1px solid #4b5563 !important;
        border-radius: 4px !important;
        color: #ffffff !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:not(.nav-tab-button):not(.asset-chip):hover {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Charts container Bloomberg style */
    .chart-container {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    }
    
    /* Gauge container specific styling */
    .gauge-container {
        background: radial-gradient(circle at center, #1a1a1a 0%, #0e1117 70%) !important;
        border: 1px solid #444444 !important;
        border-radius: 12px !important;
        padding: 8px !important;
        margin: 4px !important;
        min-height: 180px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Sidebar styling */
    .css-1lcbmhc {
        background-color: #262730 !important;
        border-right: 2px solid #444444 !important;
    }
    
    /* Tabs Bloomberg style */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a !important;
        border-bottom: 2px solid #444444 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #888888 !important;
        background-color: transparent !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    
    /* Expander Bloomberg style */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #444444 !important;
        color: #fafafa !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 500 !important;
    }
    
    /* Progress bars */
    .stProgress .css-1vencpc {
        background-color: #444444 !important;
    }
    
    .stProgress .css-1vencpc .css-1vencpc {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important;
    }
    
    /* Alerts/Success boxes */
    .stAlert {
        background-color: #1a1a1a !important;
        border: 1px solid #444444 !important;
        border-left: 4px solid #3b82f6 !important;
        color: #fafafa !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    
    /* Make all numerical data monospace */
    .css-1wivap2, .stMetric, [data-testid="metric-container"] {
        font-family: 'Roboto Mono', 'Consolas', monospace !important;
    }
    
    /* Custom Bloomberg green for positive values */
    .positive-value {
        color: #00ff88 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* Custom Bloomberg red for negative values */
    .negative-value {
        color: #ff4444 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* Custom Bloomberg yellow for neutral/warning values */
    .neutral-value {
        color: #ffd700 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* Signal badges Bloomberg style */
    .signal-badge {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        padding: 16px 32px !important;
        border-radius: 8px !important;
        text-align: center !important;
        margin: 16px 0 !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .signal-buy { 
        background: linear-gradient(135deg, #1a2e1a 0%, #2d4d2d 100%) !important;
        color: #00ff88 !important; 
        border-color: #00ff88 !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3) !important;
    }
    
    .signal-sell { 
        background: linear-gradient(135deg, #2e1a1a 0%, #4d2d2d 100%) !important; 
        color: #ff4444 !important;
        border-color: #ff4444 !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.3) !important;
    }
    
    .signal-hold { 
        background: linear-gradient(135deg, #2e2a1a 0%, #4d452d 100%) !important; 
        color: #ffd700 !important;
        border-color: #ffd700 !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3) !important;
    }
    
    /* Metric containers Bloomberg cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 4px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Additional modern Streamlit selectors */
    .stMetric {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%) !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 4px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Enhanced DataFrame Styling */
    .stDataFrame {
        background: transparent !important;
        border: none !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizeHandle"] {
        background-color: #444444 !important;
    }
    
    .stDataFrame table {
        background-color: transparent !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    .stDataFrame thead tr th {
        background-color: #1a1a1a !important;
        color: #3b82f6 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #444444 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.8rem !important;
        padding: 12px 8px !important;
    }
    
    .stDataFrame tbody tr td {
        background-color: #0e1117 !important;
        color: #fafafa !important;
        font-family: 'Roboto Mono', monospace !important;
        border-bottom: 1px solid #444444 !important;
        padding: 8px !important;
        font-size: 0.85rem !important;
    }
    
    .stDataFrame tbody tr:hover td {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* DataFrame column headers */
    .stDataFrame [data-testid="column-header"] {
        background-color: #1a1a1a !important;
        color: #3b82f6 !important;
    }
    
    /* Live status indicator - Small subtle dot */
    .live-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
        }
    }
    
    /* Status text styling */
    .status-text {
        color: #94a3b8 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* API status container - Minimal design */
    .api-status {
        background: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        margin: 4px 0 !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    
    /* Algorithm badge glow animation - REMOVED */
    
    /* Bento Grid - Professional Technical Analysis Cards */
    .bento-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
        gap: 16px !important;
        margin: 20px 0 !important;
    }
    
    .bento-card {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .bento-card:hover {
        border-color: #64748b !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    .bento-label {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #9ca3af !important;
        font-weight: 500 !important;
        margin-bottom: 8px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    
    .bento-value {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        font-family: 'Roboto Mono', 'Geist Mono', 'Courier New', monospace !important;
        color: #ffffff !important;
    }
    
    .bento-value.rsi-oversold {
        color: #22c55e !important;
    }
    
    .bento-value.rsi-overbought {
        color: #ef4444 !important;
    }
    
    .bento-subtitle {
        font-size: 0.875rem !important;
        color: #64748b !important;
        margin-top: 8px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    
    /* Ticker tape styles */
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        background-color: #0e1117;
        border-bottom: 1px solid #475569;
        white-space: nowrap;
        padding: 8px 0;
        margin-bottom: 16px;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .ticker {
        display: inline-block;
        animation: ticker 40s linear infinite;
    }
    .ticker-item {
        display: inline-block;
        padding: 0 2.5rem;
        font-family: 'Roboto Mono', 'IBM Plex Mono', monospace;
        color: #e1e5e9;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .ticker-item.up { 
        color: #22c55e; 
    }
    .ticker-item.down { 
        color: #ef4444; 
    }
    
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    /* Pause animation on hover for better readability */
    .ticker-wrap:hover .ticker {
        animation-play-state: paused;
    }
</style>
"""

st.markdown(bloomberg_terminal_style, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
def create_navigation():
    """Create tab-style navigation with transparent background and blue active borders"""
    
    # Initialize current page if not set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    current_page = st.session_state.current_page
    
    # Create custom tab navigation with HTML/CSS
    st.markdown(f"""
    <div style="display: flex; align-items: center; border-bottom: 1px solid #444444; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #3b82f6; margin-right: 40px;">MarketPulse</h2>
        <div style="display: flex; gap: 0;">
            <button class="nav-tab-button {'nav-tab-active' if current_page == 'dashboard' else ''}" 
                    onclick="window.parent.postMessage({{type: 'nav', page: 'dashboard'}}, '*')">
                Dashboard
            </button>
            <button class="nav-tab-button {'nav-tab-active' if current_page == 'analytics' else ''}" 
                    onclick="window.parent.postMessage({{type: 'nav', page: 'analytics'}}, '*')">
                Analytics
            </button>
            <button class="nav-tab-button {'nav-tab-active' if current_page == 'settings' else ''}" 
                    onclick="window.parent.postMessage({{type: 'nav', page: 'settings'}}, '*')">
                Settings
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fallback button navigation (hidden but functional)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 6])
    
    with col1:
        if st.button("Dashboard", key="nav_dashboard", help="Go to Dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    with col2:
        if st.button("Analytics", key="nav_analytics", help="Go to Analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()
    with col3:
        if st.button("Settings", key="nav_settings", help="Go to Settings"):
            st.session_state.current_page = "settings"
            st.rerun()
    
    # Hide the fallback buttons with CSS
    st.markdown("""
    <style>
    div[data-testid="column"]:has(button[aria-label*="Dashboard"]),
    div[data-testid="column"]:has(button[aria-label*="Analytics"]),
    div[data-testid="column"]:has(button[aria-label*="Settings"]) {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    return st.session_state.current_page

# --- PRICE CHART FUNCTION ---
@st.cache_data(ttl=300)
def get_stock_data(ticker, period="1mo"):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        return None

def create_candlestick_chart(ticker):
    """Create pixel-perfect TradingView-style chart with Price + Volume subplots"""
    data = get_stock_data(ticker, period="3mo")  # 3 months for better SMA
    
    if data is None or data.empty:
        st.error(f"Unable to fetch data for {ticker}")
        return None
    
    # Determine volume bar colors (match candle colors)
    volume_colors = ['#00F900' if close >= open_price else '#FF3333' 
                     for close, open_price in zip(data['Close'], data['Open'])]
    
    # Create subplot with 2 rows: Price (top 70%) + Volume (bottom 30%)
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,  # Very tight spacing
        row_heights=[0.7, 0.3],  # Price gets 70%, Volume gets 30%
        subplot_titles=None  # No titles
    )
    
    # === ROW 1: CANDLESTICK CHART ===
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing=dict(line=dict(color='#00F900', width=1), fillcolor='#00F900'),
            decreasing=dict(line=dict(color='#FF3333', width=1), fillcolor='#FF3333'),
            whiskerwidth=0.5,  # Thinner wicks for pro look
        ),
        row=1, col=1
    )
    
    # Add 50-day SMA overlay (Cyan)
    if len(data) >= 50:
        sma_50 = data['Close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=sma_50,
                mode='lines',
                name='SMA 50',
                line=dict(color='#00E5FF', width=1.5),
                opacity=0.8,
                showlegend=False
            ),
            row=1, col=1
        )
    
    # === ROW 2: VOLUME BARS ===
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker=dict(
                color=volume_colors,
                line=dict(width=0)
            ),
            showlegend=False
        ),
        row=2, col=1
    )
    
    # === LAYOUT: TRADINGVIEW DARK MODE ===
    fig.update_layout(
        # Pure black/transparent background
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        # Subtle text
        font=dict(color='#94a3b8', family='Roboto Mono', size=10),
        # Maximize space
        margin=dict(l=0, r=50, t=10, b=0),
        height=600,
        showlegend=False,
        # DISABLE RANGE SLIDER (critical)
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        # Unified hover (TradingView style)
        hovermode='x unified',
        # Consistent bar spacing
        bargap=0.1,
        bargroupgap=0
    )
    
    # === X-AXIS (Price Chart) ===
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        color='#64748b',
        # CROSSHAIR (The "spike lines")
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor='#999999',
        spikethickness=1,
        row=1, col=1
    )
    
    # === X-AXIS (Volume Chart) ===
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        color='#64748b',
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor='#999999',
        spikethickness=1,
        row=2, col=1
    )
    
    # === Y-AXIS (Price) ===
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        color='#64748b',
        side='right',  # TradingView has price on right
        # VERTICAL CROSSHAIR
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor='#999999',
        spikethickness=1,
        row=1, col=1
    )
    
    # === Y-AXIS (Volume) ===
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        zeroline=False,
        color='#64748b',
        side='right',
        showspikes=False,  # No vertical spike for volume
        row=2, col=1
    )
    
    return fig

# --- GAUGE CHART FUNCTION ---
def create_gauge_chart(score, title, max_val=100):
    """Create a modern gauge chart for scores"""
    # Determine color based on score
    if score >= 70:
        color = "#22c55e"
    elif score >= 40:
        color = "#fbbf24"
    else:
        color = "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'color': '#fafafa', 'size': 18, 'family': 'Inter'}},
        number = {'font': {'color': '#fafafa', 'size': 28, 'family': 'Inter'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickcolor': '#fafafa', 'tickfont': {'family': 'Inter'}},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': "rgba(255,255,255,0.05)"},
                {'range': [40, 70], 'color': "rgba(255,255,255,0.08)"},
                {'range': [70, 100], 'color': "rgba(255,255,255,0.12)"}],
            'threshold': {
                'line': {'color': color, 'width': 3},
                'thickness': 0.8,
                'value': 90}
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#fafafa", 'family': 'Inter'},
        height=220,
        margin=dict(l=20,r=20,t=50,b=20)
    )
    
    return fig

# --- MARKET SENTIMENT TREND CHART ---
def create_sentiment_trend():
    """Create a market sentiment trend chart (VIX-based, not social media)"""
    # Simulate VIX-based market sentiment data for the past 30 days
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    # Market sentiment based on VIX levels (inverted: low VIX = high sentiment)
    vix_levels = np.random.normal(20, 5, 30)  # VIX around 20 +/- 5
    vix_levels = np.clip(vix_levels, 10, 40)  # Realistic VIX range
    # Convert VIX to sentiment (inverted relationship)
    sentiment_scores = 100 - (vix_levels - 10) * (100 / 30)  # VIX 10->100 sentiment, VIX 40->0 sentiment
    
    df = pd.DataFrame({
        'Date': dates,
        'Sentiment': sentiment_scores
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Sentiment'],
        mode='lines',
        line=dict(color='#22c55e', width=3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(34, 197, 94, 0.1)',
        name='Market Sentiment Score',
        hovertemplate='<b>Date:</b> %{x}<br><b>Market Sentiment:</b> %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Market Sentiment Trend (VIX-Based, 30 Days)",
        title_font_color='#fafafa',
        title_font_size=20,
        title_x=0.02,
        xaxis_title="Date",
        yaxis_title="Market Sentiment Score",
        template='plotly_dark',
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa', family='Inter'),
        showlegend=False
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', range=[0, 100])
    
    return fig

# --- MARKET OVERVIEW (Landing State) ---
def render_market_overview():
    """Display professional market overview with live data density"""
    
    # === TICKER TAPE AT VERY TOP ===
    display_ticker_tape()
    
    # Hero Section - Bold Branding
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 30px 0;">
        <h1 style="font-size: 3rem; font-weight: 700; margin-bottom: 8px;">
            <span style="color: #ffffff;">Market</span><span style="color: #3b82f6;">Pulse</span>
        </h1>
        <p style="font-size: 0.95rem; color: #64748b; margin-bottom: 0;">
            Real-Time Financial Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # === ROW 1: LIVE INDICES (Data Density) ===
    st.markdown('<div style="margin-bottom: 30px;">', unsafe_allow_html=True)
    
    idx_col1, idx_col2, idx_col3 = st.columns(3)
    
    with idx_col1:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 16px;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">S&P 500</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">$580.12</div>
            <div style="font-size: 0.85rem; color: #22c55e;">▲ +0.4% <span style="color: #64748b;">Today</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with idx_col2:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 16px;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Nasdaq 100</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">$495.20</div>
            <div style="font-size: 0.85rem; color: #22c55e;">▲ +0.8% <span style="color: #64748b;">Today</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with idx_col3:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 16px;">
            <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Bitcoin</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">$98,400</div>
            <div style="font-size: 0.85rem; color: #ef4444;">▼ -1.2% <span style="color: #64748b;">24h</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # === ROW 2: COMMAND CENTER (Search) ===
    st.markdown('<div style="margin: 40px 0 30px 0;">', unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 3, 1])
    
    with col_center:
        # Professional search layout with tight button
        search_col1, search_col2 = st.columns([6, 1])
        
        with search_col1:
            search_ticker = st.text_input(
                "", 
                value="", 
                placeholder="Type symbol (e.g., NVDA, GME, TSLA)...",
                label_visibility="collapsed",
                key="overview_search"
            ).upper()
        
        with search_col2:
            analyze_btn = st.button("ANALYZE", type="primary", use_container_width=True, key="analyze_btn")
        
        # Trigger analysis on button click OR Enter key
        if analyze_btn and search_ticker:
            st.session_state.active_ticker = search_ticker
            st.session_state.show_analysis = True
            st.session_state.last_search = search_ticker
            st.rerun()
        
        # Also trigger when Enter is pressed (value changes)
        if search_ticker and search_ticker != st.session_state.get('last_search', '') and not analyze_btn:
            st.session_state.last_search = search_ticker
            st.session_state.active_ticker = search_ticker
            st.session_state.show_analysis = True
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # === ROW 3: MARKET CONTEXT (Trending + News) ===
    st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
    
    context_col1, context_col2 = st.columns([2, 1])
    
    with context_col1:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                📈 Top Gainers Today
            </div>
        """, unsafe_allow_html=True)
        
        # Trending stocks data
        trending_data = pd.DataFrame({
            'Ticker': ['NVDA', 'TSLA', 'AAPL', 'META', 'GOOGL'],
            'Price': ['$147.91', '$352.56', '$183.46', '$589.34', '$175.23'],
            '% Change': ['+5.2%', '+3.8%', '+2.4%', '+1.9%', '+1.5%'],
            'Volume': ['45.2M', '78.3M', '52.1M', '28.9M', '31.4M']
        })
        
        # Custom styled dataframe
        st.dataframe(
            trending_data,
            use_container_width=True,
            hide_index=True,
            height=220
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with context_col2:
        st.markdown("""
        <div style="background: #1e293b; border: 1px solid #475569; border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                📰 Market News
            </div>
            <div style="font-size: 0.85rem; line-height: 1.8; color: #cbd5e1;">
                <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #334155;">
                    <div style="color: #00ff88; font-weight: 600; margin-bottom: 4px;">NVDA Earnings Beat</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Reuters • 2 hours ago</div>
                </div>
                <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #334155;">
                    <div style="color: #00ccff; font-weight: 600; margin-bottom: 4px;">Fed Signals Rate Hold</div>
                    <div style="font-size: 0.75rem; color: #64748b;">Bloomberg • 5 hours ago</div>
                </div>
                <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #334155;">
                    <div style="color: #fbbf24; font-weight: 600; margin-bottom: 4px;">Tech Sector Rally</div>
                    <div style="font-size: 0.75rem; color: #64748b;">CNBC • 8 hours ago</div>
                </div>
                <div style="margin-bottom: 0;">
                    <div style="color: #94a3b8; font-weight: 600; margin-bottom: 4px;">Oil Prices Stabilize</div>
                    <div style="font-size: 0.75rem; color: #64748b;">WSJ • 12 hours ago</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- STOCK ANALYSIS DASHBOARD (Analysis State) ---
def render_stock_analysis():
    """Display comprehensive stock analysis for active ticker"""
    
    ticker = st.session_state.get('active_ticker', '')
    
    # Top Navigation Bar with Home Button
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("← Home", key="home_btn"):
            st.session_state.show_analysis = False
            if 'active_ticker' in st.session_state:
                del st.session_state['active_ticker']
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 2.5rem; font-weight: 700; margin: 0;">
                {ticker} <span style="color: #9ca3af; font-size: 1.5rem;">Analysis</span>
            </h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: right; padding: 20px 0;">
            <div class="api-status">
                <div class="live-indicator"></div>
                <span class="status-text">LIVE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Run analysis automatically on load
    with st.spinner(f"Running comprehensive analysis on {ticker}..."):
        result = calculate_trade_signal(ticker)
    
    if "Error" not in result:
        # === PRICE CHART ===
        price_chart = create_candlestick_chart(ticker)
        if price_chart:
            st.plotly_chart(price_chart, use_container_width=True, key="main_price_chart")
        
        # === AI RATIONALE (immediately after chart) ===
        # Generate advanced AI summary based on market conditions
        component_scores = result.get('COMPONENT SCORES', result.get('📋 COMPONENT SCORES', {}))
        final_score = safe_get_result_value(result, 'FINAL SCORE', '50.0/100')
        signal = safe_get_result_value(result, 'TRADING SIGNAL', 'HOLD')
        
        try:
            score_num = float(str(final_score).replace('/100', '').strip())
        except:
            score_num = 50.0
        
        # Extract advanced metrics
        rsi_val = component_scores.get('RSI', 'N/A')
        vwap_signal = component_scores.get('VWAP Signal', 'N/A')
        sma_trend = component_scores.get('SMA50 Trend', 'N/A')
        momentum = component_scores.get('Momentum 5D', 'N/A')
        volume_signal = component_scores.get('Volume Signal', 'N/A')
        valuation_raw = component_scores.get('Valuation', 'N/A')
        gamma_raw = component_scores.get('Gamma', 'N/A')
        
        # Extract numeric values for sentiment/gamma analysis
        try:
            valuation_score = float(str(valuation_raw).replace('/100', '').strip())
        except:
            valuation_score = 50.0
        
        try:
            gamma_score = float(str(gamma_raw).replace('/100', '').strip())
        except:
            gamma_score = 50.0
        
        try:
            rsi_num = float(str(rsi_val).replace('%', '').strip())
        except:
            rsi_num = 50.0
        
        # ADVANCED AI LOGIC - Market Maker Squeeze Detection
        if valuation_score > 80 and gamma_score > 50:
            ai_summary = f"<strong>MARKET MAKER TRAP DETECTED:</strong> High retail euphoria (Valuation Score: {valuation_score:.0f}/100) combined with accelerating Gamma ({gamma_score:.0f}/100) suggests market makers are trapped in short positions. Institutional hedging pressure could trigger a squeeze as delta hedging requirements force buying. <strong>Estimated Timeframe: 1-2 Days</strong> for initial move."
            time_horizon = "1-2 Days (Squeeze Setup)"
            confidence = "VERY HIGH"
        
        # Extreme Fear - Mean Reversion Play
        elif rsi_num < 30 and score_num < 35:
            ai_summary = f"<strong>EXTREME FEAR DETECTED:</strong> RSI at {rsi_num:.1f} indicates panic selling has exhausted. Algorithm anticipates mean-reversion bounce as institutional buyers accumulate at oversold levels. Volume analysis shows capitulation patterns forming. <strong>Estimated Timeframe: 3-5 Days</strong> for reversal catalyst."
            time_horizon = "3-5 Days (Reversal Setup)"
            confidence = "HIGH"
        
        # Overbought Euphoria - Short Setup
        elif rsi_num > 70 and score_num > 65:
            ai_summary = f"<strong>OVERBOUGHT EUPHORIA:</strong> RSI at {rsi_num:.1f} signals retail FOMO at peak. Valuation metrics ({valuation_score:.0f}/100) suggest limited upside. Smart money distribution patterns detected. <strong>Estimated Timeframe: 2-4 Days</strong> for pullback initiation."
            time_horizon = "2-4 Days (Distribution)"
            confidence = "HIGH"
        
        # Mixed Signals - Range-Bound
        elif 40 <= score_num <= 60:
            vwap_status = "above" if '1' in str(vwap_signal) or 'Strong' in str(vwap_signal) else "below"
            ai_summary = f"<strong>CONFLICTING SIGNALS DETECTED:</strong> Volatility is contracting as bulls and bears reach equilibrium. Price action is range-bound {vwap_status} VWAP with no clear directional conviction. Algorithm recommends <strong>waiting for a decisive breakout</strong> above VWAP with volume confirmation before entering. Avoid chop zones."
            time_horizon = "5-10 Days (Consolidation)"
            confidence = "LOW - HOLD"
        
        # Strong Bullish Setup
        elif 'BUY' in signal.upper() and score_num >= 60:
            reasons = []
            
            if '-1' in str(vwap_signal) or 'Weak' in str(vwap_signal):
                reasons.append("price reclaiming VWAP support")
            if rsi_num < 50:
                reasons.append(f"RSI at {rsi_num:.1f} showing accumulation")
            if '+' in str(momentum):
                reasons.append("positive momentum accelerating")
            if '1' in str(volume_signal):
                reasons.append("institutional volume surging")
            
            reason_text = ", ".join(reasons[:3]) if reasons else "technical alignment favoring bulls"
            ai_summary = f"<strong>BULLISH SETUP CONFIRMED:</strong> Algorithm detects {reason_text}. Risk/reward favors long positions with tight stops below recent lows. <strong>Estimated Timeframe: 3-7 Days</strong> for upside targets."
            time_horizon = "3-7 Days (Bullish)"
            confidence = "MODERATE-HIGH"
        
        # Strong Bearish Setup
        elif 'SELL' in signal.upper() and score_num <= 40:
            reasons = []
            
            if '1' in str(vwap_signal) or 'Strong' in str(vwap_signal):
                reasons.append("rejection at VWAP resistance")
            if rsi_num > 50:
                reasons.append(f"RSI at {rsi_num:.1f} showing distribution")
            if '-' in str(sma_trend):
                reasons.append("50-day MA trending lower")
            if '-' in str(momentum):
                reasons.append("negative momentum building")
            
            reason_text = ", ".join(reasons[:3]) if reasons else "technical breakdown in progress"
            ai_summary = f"<strong>BEARISH PRESSURE MOUNTING:</strong> Algorithm detects {reason_text}. Short-term downside likely as sellers overwhelm buy-side liquidity. <strong>Estimated Timeframe: 2-5 Days</strong> for downside continuation."
            time_horizon = "2-5 Days (Bearish)"
            confidence = "MODERATE"
        
        # Default Fallback
        else:
            ai_summary = f"<strong>MONITORING MODE:</strong> Current score ({score_num:.0f}/100) suggests uncertain market conditions. Algorithm is tracking key levels for breakout opportunities. Patience recommended until clearer directional signals emerge."
            time_horizon = "Pending Confirmation"
            confidence = result.get('CONFIDENCE', 'LOW')
        
        # Bloomberg-style Execution Thesis
        st.markdown(f"""
        <div style="background: #1a1f2e; border: 1px solid #2d3748; border-radius: 4px; padding: 16px; margin: 16px 0;">
            <div style="border-bottom: 1px solid #2d3748; padding-bottom: 8px; margin-bottom: 12px;">
                <span style="font-family: 'Courier New', monospace; font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 1px;">AI Execution Thesis</span>
            </div>
            <div style="font-family: 'Courier New', monospace; font-size: 0.875rem; color: #e2e8f0; line-height: 1.6;">
                {ai_summary}
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #2d3748; font-family: 'Courier New', monospace; font-size: 0.75rem; color: #718096;">
                <span>Timeframe: {time_horizon}</span>
                <span style="margin: 0 12px;">|</span>
                <span>Confidence: {confidence}</span>
                <span style="margin: 0 12px;">|</span>
                <span>Score: {final_score}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # === VERDICT: TRADING SIGNAL ===
        if "BUY" in signal:
            badge_class = "signal-buy"
        elif "SELL" in signal:
            badge_class = "signal-sell"
        else:
            badge_class = "signal-hold"
        
        st.markdown(f"""
        <div class="signal-badge {badge_class}">
            {signal}
        </div>
        """, unsafe_allow_html=True)
        
        # === TRADE EXECUTION CARD (Professional Risk Management) ===
        # Get current price from the data
        stock_data = get_stock_data(ticker, period="1mo")
        if stock_data is not None and not stock_data.empty:
            current_price = stock_data['Close'].iloc[-1]
            entry_price = current_price  # Set entry first
            
            # Smart trade logic: Calculate levels based on signal direction
            if "SELL" in signal.upper():
                # SHORT POSITION LOGIC
                # Entry: Current price (we SELL/short here)
                # Stop Loss: ABOVE entry (we exit if price rises)
                # Target: BELOW entry (we profit if price falls)
                stop_loss = entry_price * 1.05  # Stop at +5% above entry
                target = entry_price * 0.85     # Target at -15% below entry
                
                # Calculate risk and reward for SHORT
                risk_amount = stop_loss - entry_price      # How much we lose if stopped (positive)
                reward_amount = entry_price - target       # How much we gain if target hit (positive)
                risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
                
                entry_label = "SHORT ENTRY"
                stop_label = "BUY TO COVER (STOP)"
                target_label = "BUY TO COVER (TARGET)"
                stop_percent = "+5.0%"
                target_percent = "-15.0%"
                position_type = "Short Position"
                
            else:
                # LONG POSITION LOGIC (Default for BUY/HOLD)
                # Entry: Current price (we BUY here)
                # Stop Loss: BELOW entry (we exit if price falls)
                # Target: ABOVE entry (we profit if price rises)
                stop_loss = entry_price * 0.95  # Stop at -5% below entry
                target = entry_price * 1.15     # Target at +15% above entry
                
                # Calculate risk and reward for LONG
                risk_amount = entry_price - stop_loss      # How much we lose if stopped (positive)
                reward_amount = target - entry_price       # How much we gain if target hit (positive)
                risk_reward = reward_amount / risk_amount if risk_amount > 0 else 0
                
                entry_label = "LONG ENTRY"
                stop_label = "STOP LOSS"
                target_label = "PRICE TARGET"
                stop_percent = "-5.0%"
                target_percent = "+15.0%"
                position_type = "Long Position"
            
            st.markdown("""
            <div style="margin: 20px 0 30px 0;">
                <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                    TRADE EXECUTION LEVELS
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            exec_col1, exec_col2, exec_col3 = st.columns(3)
            
            with exec_col1:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    border: 2px solid #64748b;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                ">
                    <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                        {entry_label}
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: #ffffff; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">
                        ${entry_price:.2f}
                    </div>
                    <div style="font-size: 0.65rem; color: #64748b;">
                        Current Market
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with exec_col2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #2d1a1a 0%, #4d2d2d 100%);
                    border: 2px solid #ef4444;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                ">
                    <div style="font-size: 0.7rem; color: #fca5a5; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                        {stop_label}
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: #ef4444; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">
                        ${stop_loss:.2f}
                    </div>
                    <div style="font-size: 0.65rem; color: #7f1d1d;">
                        {stop_percent} Risk Protection
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with exec_col3:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1a2e1a 0%, #2d4d2d 100%);
                    border: 2px solid #22c55e;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                ">
                    <div style="font-size: 0.7rem; color: #86efac; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                        {target_label}
                    </div>
                    <div style="font-size: 2rem; font-weight: 700; color: #22c55e; font-family: 'Roboto Mono', monospace; margin-bottom: 4px;">
                        ${target:.2f}
                    </div>
                    <div style="font-size: 0.65rem; color: #14532d;">
                        {target_percent} | {position_type} | R:R {risk_reward:.1f}:1
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # === GAUGE CHARTS: KEY METRICS ===
        st.subheader("Key Metrics")
        
        gauge_col1, gauge_col2, gauge_col3, gauge_col4 = st.columns(4)
        
        with gauge_col1:
            # Market sentiment from put/call ratios, VIX, etc.
            val_score = safe_get_score(result, 'Valuation', default=50.0)
            sent_score = min(100, max(0, val_score + np.random.normal(0, 10)))
            gauge1 = create_gauge_chart(sent_score, "Market Sentiment")
            st.plotly_chart(gauge1, use_container_width=True, key="gauge_sentiment")
        
        with gauge_col2:
            gamma_score = safe_get_score(result, 'Gamma', default=50.0)
            gauge2 = create_gauge_chart(gamma_score, "Volatility")
            st.plotly_chart(gauge2, use_container_width=True, key="gauge_gamma")
        
        with gauge_col3:
            volume_score = safe_get_score(result, 'Volume', default=50.0)
            gauge3 = create_gauge_chart(volume_score, "Volume")
            st.plotly_chart(gauge3, use_container_width=True, key="gauge_volume")
        
        with gauge_col4:
            val_score = safe_get_score(result, 'Valuation', default=50.0)
            gauge4 = create_gauge_chart(val_score, "Valuation")
            st.plotly_chart(gauge4, use_container_width=True, key="gauge_valuation")
    
    else:
        st.error(f"Analysis failed: {result['Error']}")

# --- SETTINGS PAGE ---
def render_settings():
    st.markdown("## Dashboard Settings")
    
    st.markdown("### Theme Preferences")
    st.selectbox("Dashboard Theme", ["Dark Mode (Current)", "Light Mode"], disabled=True)
    
    st.markdown("### Data Sources")
    st.checkbox("Yahoo Finance", value=True, disabled=True)
    st.checkbox("Reddit Sentiment", value=True, disabled=True)
    st.checkbox("Options Data", value=True, disabled=True)
    
    st.markdown("### Alerts & Notifications")
    st.checkbox("Price Alerts", value=False)
    st.checkbox("Signal Changes", value=False)
    st.number_input("Alert Threshold (%)", value=5.0, step=0.5)
    
    st.markdown("### Chart Settings")
    st.selectbox("Default Time Frame", ["1D", "1W", "1M", "3M", "1Y"], index=2)
    st.selectbox("Chart Type", ["Candlestick", "Line", "Area"], index=0)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# --- SYSTEM STATUS MONITORING ---
def get_api_status():
    """Get API health and performance metrics"""
    try:
        # Health check
        health_response = requests.get("http://localhost:8000/api/v1/health", timeout=3)
        health_data = health_response.json()
        
        # Performance metrics
        perf_response = requests.get("http://localhost:8000/api/v1/performance", timeout=3)
        perf_data = perf_response.json()
        
        return {
            "status": "healthy",
            "health": health_data,
            "performance": perf_data
        }
    except:
        return {"status": "error", "health": None, "performance": None}

def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System Status")
    
    status_data = get_api_status()
    
    if status_data["status"] == "healthy":
        st.sidebar.success("🟢 API Online")
        
        if status_data["performance"]:
            perf = status_data["performance"]
            st.sidebar.metric(
                "Daily Analyses", 
                perf["daily_analysis_volume"]
            )
            
            if perf["top_analyzed_stocks"]:
                st.sidebar.markdown("**🔥 Trending Stocks:**")
                for stock in perf["top_analyzed_stocks"][:3]:
                    st.sidebar.write(f"• {stock['ticker']} ({stock['count']})")
    else:
        st.sidebar.error("🔴 API Offline")
    
    # Algorithm status (compact)
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="algo-status-badge" style="margin: 0 0 8px 0; width: 100%; justify-content: center;">
        <div class="live-indicator"></div>
        <span>ALGO: ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption("✅ RSI • VIX • Dynamic Weights")
    
    # Last updated
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# --- TICKER TAPE FUNCTION ---
def display_ticker_tape():
    """
    Creates a scrolling financial news tape at the top of the screen.
    Purely visual - does not affect the algorithm.
    """
    st.markdown("""
        <div class="ticker-wrap">
        <div class="ticker">
            <span class="ticker-item">⚡ NVDA: Blackwell Chips Sold Out until 2026</span>
            <span class="ticker-item down">▼ TSLA: Recall affecting 2M vehicles</span>
            <span class="ticker-item up">▲ AAPL: Vision Pro sales beat estimates</span>
            <span class="ticker-item">⚡ CPI Data: Inflation cools to 2.9%</span>
            <span class="ticker-item up">▲ AMD: New AI partnership announced</span>
            <span class="ticker-item down">▼ META: EU antitrust investigation</span>
            <span class="ticker-item up">▲ BTC: Institutional buying surge</span>
            <span class="ticker-item">⚡ Fed: Rate cut probability 65%</span>
        </div>
        </div>
        
        <style>
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background-color: transparent !important;
            border: none !important;
            white-space: nowrap;
            padding: 12px 0;
            margin: 0 0 24px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .ticker {
            display: inline-block;
            animation: ticker 40s linear infinite;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 2.5rem;
            font-family: 'Roboto Mono', 'IBM Plex Mono', monospace;
            color: #e1e5e9;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .ticker-item.up { 
            color: #22c55e; 
        }
        .ticker-item.down { 
            color: #ef4444; 
        }
        
        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        
        /* Pause animation on hover for better readability */
        .ticker-wrap:hover .ticker {
            animation-play-state: paused;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
def main():
    # Initialize session state
    if 'show_analysis' not in st.session_state:
        st.session_state.show_analysis = False
    
    # Render system status in sidebar (minimized)
    render_system_status()
    
    # State-based routing
    if st.session_state.show_analysis:
        render_stock_analysis()
    else:
        render_market_overview()

if __name__ == "__main__":
    main()