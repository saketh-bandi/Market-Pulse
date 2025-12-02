import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from py_vollib.black_scholes.greeks.analytical import delta, gamma, vega

def get_risk_analysis(ticker):
    """
    The 'Bookie': Analyzes the Options Market to find Fear & Greed.
    Returns: Dict with IV, Put/Call Ratio, and Risk Status.
    """
    try:
        print(f"\n--- 🎲 RUNNING RISK ENGINE FOR {ticker} ---")
        stock = yf.Ticker(ticker)
        
        # 1. Get Current Price
        # We need this to find 'At The Money' (ATM) options
        hist = stock.history(period="1d")
        if hist.empty: return None
        current_price = hist['Close'].iloc[-1]
        
        # 2. Get the Option Chain (Nearest Expiration)
        # We use the nearest date because that's where the 'Action' is
        exps = stock.options
        if not exps: return None
        
        target_date = exps[0] # Front-month options
        print(f"Analyzing Contracts Expiring: {target_date}")
        
        opt = stock.option_chain(target_date)
        calls = opt.calls
        puts = opt.puts
        
        # 3. METRIC 1: PUT/CALL RATIO (Sentiment)
        # Volume = How many traded today. Open Interest = How many held overnight.
        # High Put Volume = Bearish betting.
        total_call_vol = calls['volume'].sum()
        total_put_vol = puts['volume'].sum()
        pc_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 0
        
        # 4. METRIC 2: IMPLIED VOLATILITY (Fear)
        # We only look at ATM options (Strikes close to Stock Price)
        # This gives the purest read on market anxiety.
        atm_mask = (calls['strike'] > current_price * 0.95) & (calls['strike'] < current_price * 1.05)
        atm_calls = calls[atm_mask]
        
        avg_iv = atm_calls['impliedVolatility'].mean()
        
        # 5. METRIC 3: GAMMA EXPOSURE (Acceleration)
        # We calculate Gamma for the ATM option manually using Black-Scholes
        # This tells us if price moves will be 'explosive'
        
        # Time to Expiration (Years)
        exp_dt = datetime.strptime(target_date, "%Y-%m-%d")
        today = datetime.now()
        days_to_exp = (exp_dt - today).days
        T = max(days_to_exp / 365.0, 0.001) # Avoid divide by zero
        
        # Risk Free Rate (Approx 4.5%)
        r = 0.045 
        
        # Calculate Gamma for the specific ATM strike
        if not atm_calls.empty:
            strike = atm_calls.iloc[0]['strike']
            sigma = atm_calls.iloc[0]['impliedVolatility']
            
            # py_vollib requires lower case 'c' for call
            atm_gamma = gamma('c', current_price, strike, T, r, sigma)
        else:
            atm_gamma = 0

        # --- INTERPRETATION LOGIC ---
        risk_status = "NEUTRAL"
        
        # IV Interpretation
        if avg_iv > 0.50: risk_status = "EXTREME FEAR (High IV)"
        elif avg_iv < 0.20: risk_status = "COMPLACENT (Low IV)"
        
        # Skew Interpretation
        sentiment = "NEUTRAL"
        if pc_ratio > 1.0: sentiment = "BEARISH (High Put Volume)"
        elif pc_ratio < 0.7: sentiment = "BULLISH (High Call Volume)"

        return {
            "Ticker": ticker,
            "Price": f"${current_price:.2f}",
            "⚠️ Market Fear (IV)": f"{avg_iv:.2%}",
            "⚖️ Put/Call Ratio": f"{pc_ratio:.2f}",
            "🚀 Gamma Sensitivity": f"{atm_gamma:.4f}",
            "STATUS": risk_status,
            "SENTIMENT": sentiment
        }

    except Exception as e:
        print(f"Risk Engine Error: {e}")
        return None

if __name__ == "__main__":
    # Run a test on a volatile stock
    data = get_risk_analysis("NVDA")
    if data:
        for k, v in data.items():
            print(f"{k}: {v}")
