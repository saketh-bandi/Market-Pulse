import sys
import os
import math
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_loaders.fmp_loader import get_yahoo_valuation
from data_loaders.risk_loader import get_risk_analysis
from data_loaders.sentiment_loader import get_social_sentiment

def sigmoid(x):
    """
    Sigmoid activation function for non-linear combination.
    Squashes extreme outliers into smooth probability curves.
    """
    return 1 / (1 + math.exp(-x))

def get_current_vix():
    """
    Fetches current VIX (Fear Index) to determine market regime.
    Falls back to neutral regime if API fails.
    """
    try:
        # Using Yahoo Finance API for VIX
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        current_vix = data['chart']['result'][0]['meta']['regularMarketPrice']
        print(f"📊 Current VIX: {current_vix:.2f}")
        return float(current_vix)
    except Exception as e:
        print(f"⚠️ VIX fetch failed: {e}, using neutral regime (VIX=20)")
        return 20.0  # Default to neutral regime

def get_dynamic_weights(current_vix):
    """
    🎯 HEDGE FUND UPGRADE: Dynamic Regime-Based Weighting
    
    Adjusts weights based on market fear (VIX):
    - High VIX (>30): Fear Regime - Trust Math > Trust People
    - Low VIX (<15): Complacency Regime - Sentiment drives trends
    - Normal VIX: Balanced approach
    """
    if current_vix > 30:  # 🔥 FEAR REGIME - Market Crisis
        regime = "FEAR"
        weights = {
            'sentiment': 0.10,  # Ignore the panic
            'gamma': 0.50,     # Gamma explosion is real
            'volume': 0.30,    # Smart money moves
            'valuation': 0.10  # Fundamentals don't matter in panic
        }
    elif current_vix < 15:  # 😴 COMPLACENCY REGIME - Bull Market
        regime = "COMPLACENCY"
        weights = {
            'sentiment': 0.40,  # Hype drives everything
            'gamma': 0.20,     # Low volatility = low gamma
            'volume': 0.20,    # Less trading urgency
            'valuation': 0.20  # Fair value matters again
        }
    else:  # 📊 NORMAL REGIME - Balanced Market
        regime = "NORMAL"
        weights = {
            'sentiment': 0.20,  # Standard weighting
            'gamma': 0.30,
            'volume': 0.30,
            'valuation': 0.20
        }
    
    print(f"🎯 Market Regime: {regime} (VIX: {current_vix:.1f})")
    print(f"⚖️ Dynamic Weights: {weights}")
    return weights, regime

def calculate_z_scores(sentiment_score, gamma_score, volume_score, valuation_score):
    """
    🧮 QUANT UPGRADE: Calculate Z-scores for non-linear combination
    
    Converts raw scores to standard deviations from mean.
    This prevents single extreme values from dominating the signal.
    """
    # Historical means and standard deviations (can be calibrated with more data)
    means = {'sentiment': 50, 'gamma': 40, 'volume': 50, 'valuation': 45}
    stds = {'sentiment': 25, 'gamma': 30, 'volume': 30, 'valuation': 25}
    
    z_sentiment = (sentiment_score - means['sentiment']) / stds['sentiment']
    z_gamma = (gamma_score - means['gamma']) / stds['gamma'] 
    z_volume = (volume_score - means['volume']) / stds['volume']
    z_valuation = (valuation_score - means['valuation']) / stds['valuation']
    
    print(f"📊 Z-Scores: Sentiment={z_sentiment:.2f}, Gamma={z_gamma:.2f}, Volume={z_volume:.2f}, Valuation={z_valuation:.2f}")
    
    return z_sentiment, z_gamma, z_volume, z_valuation

def calculate_nonlinear_score(z_sentiment, z_gamma, z_volume, z_valuation, weights):
    """
    🎯 ADVANCED MATH: Non-linear combination using sigmoid activation
    
    Instead of simple weighted average, this uses:
    1. Z-score normalization (prevents outlier dominance)
    2. Sigmoid squashing (smooth probability curves)
    3. Dynamic weighting (regime-aware)
    """
    # Weighted combination of Z-scores
    raw_sum = (z_sentiment * weights['sentiment'] * 4 +  # Scale factor for sigmoid
               z_gamma * weights['gamma'] * 4 +
               z_volume * weights['volume'] * 4 +
               z_valuation * weights['valuation'] * 4)
    
    # Apply sigmoid to get smooth 0-100 probability
    sigmoid_result = sigmoid(raw_sum)
    final_score = sigmoid_result * 100
    
    print(f"🧮 Raw Sum: {raw_sum:.2f} → Sigmoid: {sigmoid_result:.3f} → Final: {final_score:.1f}")
    
    return final_score

def calculate_trade_signal(ticker):
    """
    🚀 HEDGE FUND GRADE: Advanced Signal Engine with Dynamic Regime Detection
    
    NEW FEATURES:
    - Dynamic VIX-based weighting (Fear vs Complacency regimes)
    - Non-linear sigmoid combination (prevents outlier dominance)
    - Z-score normalization (statistical rigor)
    - Regime-aware confidence scoring
    """
    print(f"\n🎯 === ADVANCED SIGNAL ENGINE FOR {ticker} === 🎯")
    print("🔍 Gathering multi-modal data...")
    
    # 1. GATHER RAW DATA FROM ALL ENGINES
    try:
        valuation_data = get_yahoo_valuation(ticker)
        risk_data = get_risk_analysis(ticker)
        sentiment_data = get_social_sentiment(ticker)
        
        if not all([valuation_data, risk_data, sentiment_data]):
            return {"Error": "Failed to gather complete data"}
            
    except Exception as e:
        return {"Error": f"Data collection failed: {e}"}
    
    # 2. NORMALIZE ALL SCORES (0-100 Scale)
    print("\n📊 Normalizing scores...")
    
    # A. SENTIMENT SCORE (-1 to +1 -> 0 to 100)
    raw_sentiment = float(sentiment_data['Average Sentiment'])
    sentiment_score = (raw_sentiment + 1) * 50  # -1 becomes 0, +1 becomes 100
    
    # B. GAMMA SCORE (Normalize gamma sensitivity)
    # High gamma (>0.05) = 100, Low gamma (<0.01) = 0
    gamma_str = risk_data['🚀 Gamma Sensitivity']
    raw_gamma = float(gamma_str)
    if raw_gamma > 0.05:
        gamma_score = 100
    elif raw_gamma < 0.01:
        gamma_score = 0
    else:
        gamma_score = (raw_gamma / 0.05) * 100
    
    # C. VOLUME BIAS SCORE (Put/Call Ratio Analysis)
    pcr_str = risk_data['⚖️ Put/Call Ratio']
    pcr = float(pcr_str)
    if pcr < 0.7:  # Heavy call buying = Bullish
        volume_score = 100
    elif pcr > 1.0:  # Heavy put buying = Bearish
        volume_score = 0
    else:  # Neutral territory
        volume_score = 50 + (0.7 - pcr) * 166.67  # Linear interpolation
    
    # D. VALUATION SCORE (P/E Based)
    # Extract upside from valuation data
    upside_str = valuation_data['📈 UPSIDE POTENTIAL']
    upside = float(upside_str.replace('%', '').replace('+', ''))
    if upside > 20:
        valuation_score = 100
    elif upside < -20:
        valuation_score = 0
    else:
        valuation_score = 50 + (upside / 20) * 50
    
    # 3. 🚀 HEDGE FUND UPGRADE: Dynamic Regime Detection + Advanced Math
    print("\n⚖️ Activating advanced algorithms...")
    
    # Get current market regime via VIX
    current_vix = get_current_vix()
    weights, regime = get_dynamic_weights(current_vix)
    
    # Calculate Z-scores for statistical normalization
    z_sentiment, z_gamma, z_volume, z_valuation = calculate_z_scores(
        sentiment_score, gamma_score, volume_score, valuation_score
    )
    
    # Non-linear combination with sigmoid activation
    final_score = calculate_nonlinear_score(
        z_sentiment, z_gamma, z_volume, z_valuation, weights
    )
    
    # Also calculate traditional linear score for comparison
    linear_score = (
        sentiment_score * weights['sentiment'] +
        gamma_score * weights['gamma'] +
        volume_score * weights['volume'] +
        valuation_score * weights['valuation']
    )
    
    print(f"📊 Linear vs Non-Linear: {linear_score:.1f} vs {final_score:.1f}")
    
    # 4. 🎯 REGIME-AWARE SIGNAL INTERPRETATION
    print(f"🎯 Generating {regime} regime signal...")
    
    # Regime-specific filters (the "hedge fund alpha")
    if regime == "FEAR" and gamma_score > 80:  # Crisis + High Gamma = Opportunity
        signal = "🚨 CRISIS OPPORTUNITY - Fear + Fuel"
        confidence = "HIGH"
    elif regime == "FEAR" and sentiment_score > 70:  # Crisis + Bullish Sentiment = Trap
        signal = "⚠️ FEAR TRAP - Ignore the Hype"
        confidence = "HIGH"
    elif regime == "COMPLACENCY" and sentiment_score > 90 and gamma_score < 20:
        signal = "⚠️ BUBBLE WARNING - All Hype, No Fuel"
        confidence = "MEDIUM"
    elif sentiment_score < 10 and volume_score > 80:
        signal = "🚨 CONTRARIAN BUY - Oversold with Smart Money"
        confidence = "HIGH"
    elif final_score > 85:
        signal = f"🚀 STRONG BUY - {regime} Confluence"
        confidence = "HIGH"
    elif final_score > 70:
        signal = f"📈 BUY - {regime} Positive"
        confidence = "MEDIUM"
    elif final_score < 15:
        signal = f"🔻 STRONG SELL - {regime} Breakdown"
        confidence = "HIGH"
    elif final_score < 30:
        signal = f"📉 SELL - {regime} Negative"
        confidence = "MEDIUM"
    else:
        signal = f"⏸️ HOLD - {regime} Mixed Signals"
        confidence = "LOW"
    
    # Adjust confidence based on regime clarity
    if abs(current_vix - 20) > 10:  # Clear regime (very high or very low VIX)
        confidence_boost = "REGIME-BOOSTED"
    else:
        confidence_boost = "STANDARD"
    
    # 5. 🎯 RETURN COMPREHENSIVE HEDGE FUND ANALYSIS
    return {
        "🎯 TICKER": ticker.upper(),
        "📊 FINAL SCORE": f"{final_score:.1f}/100",
        "🎪 TRADING SIGNAL": signal,
        "🎯 CONFIDENCE": f"{confidence} ({confidence_boost})",
        "📋 COMPONENT SCORES": {
            "💭 Sentiment": f"{sentiment_score:.1f}/100",
            "🚀 Gamma": f"{gamma_score:.1f}/100",
            "⚖️ Volume Bias": f"{volume_score:.1f}/100",
            "💰 Valuation": f"{valuation_score:.1f}/100"
        },
        "🔬 ADVANCED METRICS": {
            "Market Regime": f"{regime} (VIX: {current_vix:.1f})",
            "Linear Score": f"{linear_score:.1f}/100",
            "Non-Linear Score": f"{final_score:.1f}/100",
            "Z-Scores": f"S:{z_sentiment:.2f} G:{z_gamma:.2f} V:{z_volume:.2f} Val:{z_valuation:.2f}"
        },
        "🔍 RAW DATA": {
            "Sentiment": sentiment_data['Average Sentiment'],
            "Gamma": risk_data['🚀 Gamma Sensitivity'],
            "Put/Call": risk_data['⚖️ Put/Call Ratio'],
            "P/E Upside": valuation_data['📈 UPSIDE POTENTIAL'],
            "VIX": current_vix
        },
        "⚖️ DYNAMIC WEIGHTS": weights,
        "🚀 ALGORITHM": "Hedge Fund Grade v2.0"
    }

def run_full_analysis(ticker):
    """
    Master function that runs the complete Market Pulse analysis
    """
    print(f"\n🌟 ===== COMPLETE MARKET PULSE ANALYSIS ===== 🌟")
    print(f"🎯 Target: {ticker.upper()}")
    print("=" * 60)
    
    result = calculate_trade_signal(ticker)
    
    if "Error" in result:
        print(f"❌ {result['Error']}")
        return
    
    # Display results in a clean format
    print(f"\n🎯 FINAL VERDICT:")
    print(f"Signal: {result['🎪 TRADING SIGNAL']}")
    print(f"Score: {result['📊 FINAL SCORE']}")
    print(f"Confidence: {result['🎯 CONFIDENCE']}")
    
    print(f"\n📊 COMPONENT BREAKDOWN:")
    for component, score in result['📋 COMPONENT SCORES'].items():
        print(f"  {component}: {score}")
    
    print(f"\n🔍 RAW METRICS:")
    for metric, value in result['🔍 RAW DATA'].items():
        print(f"  {metric}: {value}")
    
    print("\n" + "=" * 60)
    print("🎉 ANALYSIS COMPLETE - Ready for your meeting! 📸")
    
    return result

if __name__ == "__main__":
    # Test the complete system
    ticker = "NVDA"
    run_full_analysis(ticker)
