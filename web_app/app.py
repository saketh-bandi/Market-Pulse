import streamlit as st
import sys
import os

# Fix path so we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your engines
from src.data_loaders.fmp_loader import get_yahoo_valuation
from src.data_loaders.risk_loader import get_risk_analysis
from src.data_loaders.sentiment_loader import get_social_sentiment
from src.analysis.signals import calculate_trade_signal

# --- PAGE CONFIG ---
st.set_page_config(page_title="MarketPulse", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for that "Bloomberg Terminal" look
st.markdown("""
    <style>
    .stApp { 
        background-color: #0e1117; 
        color: #ffffff; 
    }
    .metric-card { 
        background-color: #262730; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #444; 
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .status-green {
        color: #00ff88;
        font-weight: bold;
    }
    .status-red {
        color: #ff4444;
        font-weight: bold;
    }
    .status-yellow {
        color: #ffaa00;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ MarketPulse: Trident Engine")
st.markdown("### 🎯 **Hybrid Financial Intelligence Dashboard**")
st.markdown("*Combining Valuation, Risk Analytics, and Social Sentiment*")

# --- SIDEBAR INPUT ---
with st.sidebar:
    st.header("🎛️ Configuration")
    ticker = st.text_input("Enter Ticker Symbol", value="NVDA").upper()
    
    st.markdown("---")
    st.markdown("### 🔧 Engine Status")
    st.success("✅ Valuation Engine: Online")
    st.success("✅ Risk Engine: Online") 
    st.success("✅ Sentiment Engine: Online")
    st.success("✅ Signal Processor: Online")
    
    st.markdown("---")
    run_analysis = st.button("🚀 **RUN FULL ANALYSIS**", type="primary")
    
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()

# --- MAIN DASHBOARD ---
if run_analysis and ticker:
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Run the unified analysis
        status_text.text("🔍 Initializing Market Pulse Analysis...")
        progress_bar.progress(20)
        
        with st.spinner(f"🎯 Analyzing {ticker} across all engines..."):
            result = calculate_trade_signal(ticker)
            progress_bar.progress(100)
            status_text.text("✅ Analysis Complete!")
        
        if "Error" in result:
            st.error(f"❌ Analysis Failed: {result['Error']}")
        else:
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # --- THE BIG VERDICT ---
            st.markdown("---")
            
            # Determine color based on signal
            if "BUY" in result['🎪 TRADING SIGNAL']:
                color_class = "status-green"
            elif "SELL" in result['🎪 TRADING SIGNAL']:
                color_class = "status-red"
            else:
                color_class = "status-yellow"
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"<div class='big-font {color_class}' style='text-align: center;'>{result['🎪 TRADING SIGNAL']}</div>", 
                           unsafe_allow_html=True)
                
                # Score visualization
                score_value = float(result['📊 FINAL SCORE'].split('/')[0])
                st.progress(score_value / 100)
                st.markdown(f"<div style='text-align: center;'>**Confidence Score: {result['📊 FINAL SCORE']}**</div>", 
                           unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center;'>Confidence Level: **{result['🎯 CONFIDENCE']}**</div>", 
                           unsafe_allow_html=True)
            
            st.markdown("---")
            
            # --- COMPONENT BREAKDOWN ---
            st.subheader("📊 **Component Analysis**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sent_score = float(result['📋 COMPONENT SCORES']['💭 Sentiment'].split('/')[0])
                st.metric(
                    "💭 **Social Sentiment**", 
                    f"{sent_score:.1f}/100",
                    delta="Bullish" if sent_score > 60 else ("Bearish" if sent_score < 40 else "Neutral")
                )
                
            with col2:
                gamma_score = float(result['📋 COMPONENT SCORES']['🚀 Gamma'].split('/')[0])
                st.metric(
                    "🚀 **Gamma Power**", 
                    f"{gamma_score:.1f}/100",
                    delta="High Volatility" if gamma_score > 70 else ("Low Volatility" if gamma_score < 30 else "Moderate")
                )
                
            with col3:
                vol_score = float(result['📋 COMPONENT SCORES']['⚖️ Volume Bias'].split('/')[0])
                st.metric(
                    "⚖️ **Volume Bias**", 
                    f"{vol_score:.1f}/100",
                    delta="Call Heavy" if vol_score > 60 else ("Put Heavy" if vol_score < 40 else "Balanced")
                )
                
            with col4:
                val_score = float(result['📋 COMPONENT SCORES']['💰 Valuation'].split('/')[0])
                st.metric(
                    "💰 **Valuation**", 
                    f"{val_score:.1f}/100",
                    delta="Undervalued" if val_score > 60 else ("Overvalued" if val_score < 40 else "Fair Value")
                )
            
            st.markdown("---")
            
            # --- DETAILED METRICS ---
            st.subheader("🔍 **Raw Market Data**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 **Key Metrics**")
                for metric, value in result['🔍 RAW DATA'].items():
                    st.write(f"**{metric}**: {value}")
                    
            with col2:
                st.markdown("#### ⚖️ **Algorithm Weights**")
                for weight, value in result['⚖️ WEIGHTS USED'].items():
                    st.write(f"**{weight.capitalize()}**: {value*100:.0f}%")
            
            # --- INTERPRETATION GUIDE ---
            st.markdown("---")
            st.subheader("🧠 **How to Read This Analysis**")
            
            with st.expander("📚 **Understanding the Signals**", expanded=False):
                st.markdown("""
                **🎯 Signal Interpretation:**
                - **STRONG BUY**: All systems aligned bullishly (Score > 85)
                - **BUY**: Positive confluence of factors (Score 70-85) 
                - **HOLD**: Mixed signals, wait for clarity (Score 30-70)
                - **SELL**: Negative confluence (Score 15-30)
                - **STRONG SELL**: All systems bearish (Score < 15)
                
                **📊 Component Weights:**
                - **Sentiment (20%)**: Social media and news sentiment
                - **Gamma (30%)**: Options market structure and volatility
                - **Volume (30%)**: Put/call ratios and smart money flow  
                - **Valuation (20%)**: Fundamental fair value analysis
                
                **⚠️ Special Filters:**
                - **"No Fuel"**: High hype but low gamma = unreliable momentum
                - **"Contrarian"**: Oversold with smart money buying = opportunity
                """)
            
            # --- DISCLAIMER ---
            st.markdown("---")
            st.warning("""
            ⚠️ **DISCLAIMER**: This is an algorithmic analysis tool for educational purposes. 
            Not financial advice. Always do your own research before making investment decisions.
            """)
    
    except Exception as e:
        st.error(f"🚨 **System Error**: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

else:
    # Landing page when no analysis is running
    st.info("👈 **Enter a ticker symbol in the sidebar and click 'RUN FULL ANALYSIS' to start your market intelligence report.**")
    
    # Show system capabilities
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 💭 **Sentiment Engine**
        - Scans Reddit (WSB, r/stocks)
        - VADER NLP sentiment analysis
        - Real-time social media mood
        """)
        
    with col2:
        st.markdown("""
        ### 🚀 **Risk Engine** 
        - Options chain analysis
        - Gamma exposure calculation
        - Put/call ratio tracking
        """)
        
    with col3:
        st.markdown("""
        ### 💰 **Valuation Engine**
        - P/E ratio analysis  
        - Fair value estimation
        - Fundamental screening
        """)
    
    st.markdown("---")
    st.markdown("### 🎯 **Sample Tickers to Try:**")
    st.write("**Popular**: NVDA, TSLA, AAPL, MSFT, GOOGL, AMZN, META")
    st.write("**Volatile**: GME, AMC, PLTR, ARKK, COIN, HOOD")
    st.write("**Defensive**: KO, JNJ, PG, WMT, VZ, T")
