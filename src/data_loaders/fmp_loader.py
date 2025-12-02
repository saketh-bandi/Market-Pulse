import requests
import pandas as pd
import yfinance as yf

# ---------------------------------------------------------
# CONFIG: Get your Free Key from https://financialmodelingprep.com/developer/docs
API_KEY = "LfIDP2tUs29gCAtYb2OANIKIiMuS8qnr" 
# ---------------------------------------------------------

def get_intrinsic_value(ticker):
    """
    Fetches stock data and calculates a simple valuation analysis.
    Uses available FMP endpoints to get price and financial metrics.
    Returns: Dict with Current Price vs Financial Analysis.
    """
    try:
        # Get current stock price
        quote_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()
        
        if not quote_data:
            print("No quote data available")
            return None
            
        current_price = quote_data[0]['price']
        market_cap = quote_data[0]['marketCap']
        pe_ratio = quote_data[0]['pe']
        
        # Get key metrics for valuation context
        metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={API_KEY}&limit=1"
        metrics_response = requests.get(metrics_url)
        metrics_data = metrics_response.json()
        
        # Get financial ratios
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={API_KEY}&limit=1"
        ratios_response = requests.get(ratios_url)
        ratios_data = ratios_response.json()
        
        # Simple valuation logic based on available metrics
        pb_ratio = ratios_data[0]['priceToBookRatio'] if ratios_data and 'priceToBookRatio' in ratios_data[0] else None
        
        # Create a simple "fair value" estimate (this is a simplified example)
        # In reality, you'd use more sophisticated models
        industry_avg_pe = 25  # Tech industry average PE (approximate)
        estimated_fair_pe = min(industry_avg_pe, 30)  # Cap at reasonable level
        
        if pe_ratio and pe_ratio > 0:
            # Simple PE-based valuation
            earnings_per_share = current_price / pe_ratio
            estimated_fair_value = earnings_per_share * estimated_fair_pe
        else:
            # Fallback: assume fair value is current price (neutral)
            estimated_fair_value = current_price
        
        # Calculate upside/downside
        upside = ((estimated_fair_value - current_price) / current_price) * 100
        
        # Determine verdict based on multiple factors
        verdict = "NEUTRAL"
        if upside > 15:
            verdict = "UNDERVALUED (Buy)"
        elif upside < -15:
            verdict = "OVERVALUED (Sell)"
        
        return {
            "Ticker": ticker,
            "Current Price": f"${current_price:.2f}",
            "Estimated Fair Value": f"${estimated_fair_value:.2f}",
            "Market Cap": f"${market_cap/1e9:.1f}B" if market_cap else "N/A",
            "P/E Ratio": f"{pe_ratio:.1f}" if pe_ratio else "N/A",
            "P/B Ratio": f"{pb_ratio:.1f}" if pb_ratio else "N/A",
            "Upside Potential": f"{upside:.1f}%",
            "Verdict": verdict,
            "Note": "Simplified valuation using P/E analysis"
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_yahoo_valuation(ticker):
    """
    Get stock valuation using Yahoo Finance (FREE alternative)
    Returns: Dict with current price and valuation metrics
    """
    try:
        # Get stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        
        # Get current price and basic info
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        # Get key financial metrics
        pe_ratio = info.get('trailingPE', None)
        pb_ratio = info.get('priceToBook', None)
        market_cap = info.get('marketCap', None)
        forward_pe = info.get('forwardPE', None)
        
        # Industry/sector averages for comparison (approximations)
        sector = info.get('sector', 'Technology')
        industry_pe_averages = {
            'Technology': 25,
            'Healthcare': 20,
            'Financial Services': 12,
            'Consumer Cyclical': 18,
            'Communication Services': 22,
            'Consumer Defensive': 16,
            'Industrials': 18,
            'Energy': 15,
            'Materials': 16,
            'Real Estate': 20,
            'Utilities': 18
        }
        
        target_pe = industry_pe_averages.get(sector, 20)
        
        # Calculate estimated fair value using P/E method
        if pe_ratio and pe_ratio > 0:
            earnings_per_share = current_price / pe_ratio
            estimated_fair_value = earnings_per_share * target_pe
        else:
            # Use forward PE if available
            if forward_pe and forward_pe > 0:
                estimated_fair_value = current_price * (target_pe / forward_pe)
            else:
                estimated_fair_value = current_price  # Neutral if no PE data
        
        # Calculate upside potential
        upside = ((estimated_fair_value - current_price) / current_price) * 100
        
        # Determine verdict
        if upside > 20:
            verdict = "STRONG BUY - Significantly Undervalued"
        elif upside > 10:
            verdict = "BUY - Undervalued"
        elif upside > -10:
            verdict = "HOLD - Fairly Valued"
        elif upside > -20:
            verdict = "SELL - Overvalued"
        else:
            verdict = "STRONG SELL - Significantly Overvalued"
        
        return {
            "🎯 TICKER": ticker.upper(),
            "💰 CURRENT PRICE": f"${current_price:.2f}",
            "📊 FAIR VALUE ESTIMATE": f"${estimated_fair_value:.2f}",
            "📈 UPSIDE POTENTIAL": f"{upside:+.1f}%",
            "🏭 SECTOR": sector,
            "📋 P/E RATIO": f"{pe_ratio:.1f}" if pe_ratio else "N/A",
            "📋 P/B RATIO": f"{pb_ratio:.1f}" if pb_ratio else "N/A",
            "💎 MARKET CAP": f"${market_cap/1e9:.1f}B" if market_cap else "N/A",
            "🎯 VERDICT": verdict,
            "📝 METHOD": f"P/E Analysis (Target P/E: {target_pe})"
        }
        
    except Exception as e:
        print(f"Error getting Yahoo Finance data: {e}")
        return None

# Quick API key test
def test_api_key(ticker):
    """Test if API key works with basic quote endpoint"""
    test_url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={API_KEY}"
    try:
        response = requests.get(test_url)
        print(f"Test API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"✅ API Key works! Current {ticker} price: ${data[0]['price']}")
                return True
        else:
            print(f"❌ API Error: {response.json()}")
        return False
    except Exception as e:
        print(f"❌ API Test failed: {e}")
        return False

# --- RUN THIS BLOCK TO TEST ---
if __name__ == "__main__":
    ticker = "NVDA" 
    print(f"\n🚀 === MARKET PULSE ANALYZER === 🚀")
    print(f"📊 ANALYZING {ticker} USING YAHOO FINANCE")
    print("=" * 50)
    
    # Use Yahoo Finance (FREE and reliable)
    result = get_yahoo_valuation(ticker)
    
    if result:
        for key, value in result.items():
            print(f"{key}: {value}")
        print("=" * 50)
        print("✅ ANALYSIS COMPLETE! Screenshot this for your meeting! 📸")
    else:
        print("❌ Failed to get data. Please check ticker symbol.")
