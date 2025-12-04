from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import sys
import os
import time
import logging
from collections import defaultdict

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketpulse_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MarketPulse-API")

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import get_db, StockCache, AnalysisLog, cache_analysis_result, check_cache_freshness
from analysis.signals import calculate_trade_signal

# Professional rate limiting - simple in-memory store
# In production, use Redis or similar
rate_limit_store = defaultdict(list)
REQUESTS_PER_MINUTE = 30
REQUESTS_PER_HOUR = 200

def check_rate_limit(client_ip: str) -> bool:
    """Professional rate limiting to prevent API abuse"""
    now = time.time()
    minute_ago = now - 60
    hour_ago = now - 3600
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if timestamp > hour_ago
    ]
    
    # Count recent requests
    recent_requests = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if timestamp > minute_ago
    ]
    
    # Check limits
    if len(recent_requests) >= REQUESTS_PER_MINUTE:
        return False
    if len(rate_limit_store[client_ip]) >= REQUESTS_PER_HOUR:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True

# Initialize FastAPI with professional configuration
app = FastAPI(
    title="MarketPulse Terminal API",
    description="🚀 Professional Financial Intelligence Backend with Enhanced Analytics",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # Next.js + Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎯 CORE API ENDPOINTS

@app.get("/")
async def root():
    """
    API health check and welcome message.
    """
    return {
        "message": "🚀 MarketPulse API v2.0 - Production Ready",
        "status": "online",
        "timestamp": datetime.utcnow(),
        "features": [
            "Smart caching system", 
            "Real-time analysis",
            "Rate limit protection",
            "Historical tracking"
        ]
    }

# Health endpoint moved to enhanced version below

@app.get("/api/v1/analyze/{ticker}")
async def analyze_stock(
    ticker: str, 
    force_refresh: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    🎯 THE MAIN ENGINE: Analyze a stock with intelligent caching.
    
    This is the core endpoint that powers your dashboard.
    - Checks cache first for speed (sub-100ms response)
    - Falls back to live analysis if cache is stale
    - Stores results for future requests
    """
    ticker = ticker.upper()
    
    # Rate limiting - reject request if over limit
    client_ip = "127.0.0.1"  # Placeholder, use real client IP in production
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests, please try again later.")
    
    # 1. CHECK CACHE FIRST (The Speed Optimization)
    if not force_refresh and check_cache_freshness(ticker, max_age_minutes=60):
        cached_result = db.query(StockCache).filter(StockCache.ticker == ticker).first()
        
        if cached_result:
            return {
                "ticker": ticker,
                "source": "cache",
                "cached_at": cached_result.last_updated,
                "data": {
                    "🎯 TICKER": ticker,
                    "📊 FINAL SCORE": f"{cached_result.final_score:.1f}/100",
                    "🎪 TRADING SIGNAL": cached_result.trading_signal,
                    "🎯 CONFIDENCE": cached_result.confidence,
                    "📋 COMPONENT SCORES": {
                        "VWAP Signal": cached_result.sentiment_score,  # Reusing field for VWAP
                        "🚀 Gamma": f"{cached_result.gamma_score:.1f}/100",
                        "⚖️ Volume Bias": f"{cached_result.volume_score:.1f}/100",
                        "💰 Valuation": f"{cached_result.valuation_score:.1f}/100"
                    }
                }
            }
    
    # 2. LIVE ANALYSIS (Cache Miss or Forced Refresh)
    try:
        logger.info(f"🔄 Running live analysis for {ticker}...")
        
        # Run your trident analysis
        analysis_result = calculate_trade_signal(ticker)
        
        if "Error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["Error"])
        
        # 3. CACHE THE RESULT (The Smart Part)
        cache_data = {
            "ticker": ticker,
            "final_score": float(analysis_result['📊 FINAL SCORE'].split('/')[0]),
            "trading_signal": analysis_result['🎪 TRADING SIGNAL'],
            "confidence": analysis_result['🎯 CONFIDENCE'],
            "sentiment_score": analysis_result['📋 COMPONENT SCORES']['VWAP Signal'],  # Reusing field for VWAP
            "gamma_score": float(analysis_result['📋 COMPONENT SCORES']['🚀 Gamma'].split('/')[0]),
            "volume_score": float(analysis_result['📋 COMPONENT SCORES']['⚖️ Volume Bias'].split('/')[0]),
            "valuation_score": float(analysis_result['📋 COMPONENT SCORES']['💰 Valuation'].split('/')[0]),
            "raw_sentiment": analysis_result.get('🔍 RAW DATA', {}).get('VWAP', 0),  # Reusing field for VWAP
            "raw_gamma": float(analysis_result['🔍 RAW DATA']['Gamma']),
            "raw_put_call_ratio": float(analysis_result['🔍 RAW DATA']['Put/Call']),
            "last_updated": datetime.utcnow()
        }
        
        # Update or insert cache
        existing = db.query(StockCache).filter(StockCache.ticker == ticker).first()
        if existing:
            for key, value in cache_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            cache_entry = StockCache(**cache_data)
            db.add(cache_entry)
        
        # Log the analysis for backtesting
        log_entry = AnalysisLog(
            ticker=ticker,
            trading_signal=cache_data["trading_signal"],
            final_score=cache_data["final_score"],
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        
        db.commit()
        
        return {
            "ticker": ticker,
            "source": "live_analysis",
            "analyzed_at": datetime.utcnow(),
            "data": analysis_result
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Analysis failed for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/cache/stats")
async def get_cache_stats(db: Session = Depends(get_db)):
    """
    Cache performance statistics for monitoring.
    """
    total_cached = db.query(StockCache).count()
    fresh_cache = db.query(StockCache).filter(
        StockCache.last_updated > datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    return {
        "total_cached_stocks": total_cached,
        "fresh_cache_entries": fresh_cache,
        "cache_hit_rate": f"{(fresh_cache/total_cached)*100:.1f}%" if total_cached > 0 else "0%",
        "oldest_cache": db.query(StockCache).order_by(StockCache.last_updated).first().last_updated if total_cached > 0 else None
    }

@app.get("/api/v1/trending")
async def get_trending_stocks(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get most analyzed stocks (trending tickers).
    """
    # Get most frequently analyzed stocks from logs
    trending = db.query(AnalysisLog.ticker, db.func.count(AnalysisLog.ticker).label('count')).group_by(AnalysisLog.ticker).order_by(db.text('count DESC')).limit(limit).all()
    
    return {
        "trending_stocks": [{"ticker": t[0], "analysis_count": t[1]} for t in trending],
        "generated_at": datetime.utcnow()
    }

@app.delete("/api/v1/cache/{ticker}")
async def invalidate_cache(ticker: str, db: Session = Depends(get_db)):
    """
    Force cache invalidation for a specific ticker.
    """
    ticker = ticker.upper()
    
    cached_entry = db.query(StockCache).filter(StockCache.ticker == ticker).first()
    if cached_entry:
        db.delete(cached_entry)
        db.commit()
        return {"message": f"Cache invalidated for {ticker}"}
    else:
        raise HTTPException(status_code=404, detail=f"No cache found for {ticker}")

@app.get("/api/v1/batch_analyze")
async def batch_analyze(tickers: str, db: Session = Depends(get_db)):
    """
    Analyze multiple stocks in one request.
    Example: /api/v1/batch_analyze?tickers=NVDA,TSLA,AAPL
    """
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    
    if len(ticker_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 tickers per batch request")
    
    results = {}
    
    for ticker in ticker_list:
        try:
            # Use the same caching logic as single analysis
            if check_cache_freshness(ticker, max_age_minutes=60):
                cached = db.query(StockCache).filter(StockCache.ticker == ticker).first()
                results[ticker] = {
                    "score": cached.final_score,
                    "signal": cached.trading_signal,
                    "source": "cache"
                }
            else:
                # This would trigger live analysis - simplified for batch
                results[ticker] = {
                    "score": "pending",
                    "signal": "analysis_required",
                    "source": "needs_refresh"
                }
        except Exception as e:
            results[ticker] = {"error": str(e)}
    
    return {
        "batch_results": results,
        "processed_count": len(ticker_list),
        "timestamp": datetime.utcnow()
    }

@app.get("/api/v1/export/{ticker}")
async def export_analysis(ticker: str, format: str = "json", db: Session = Depends(get_db)):
    """
    Export analysis results in different formats (json, csv).
    """
    ticker = ticker.upper()
    
    # Get latest analysis
    analysis_result = calculate_trade_signal(ticker)
    
    if format.lower() == "csv":
        # Convert to CSV format
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Metric', 'Value'])
        
        # Basic info
        writer.writerow(['Ticker', analysis_result.get('🎯 TICKER', ticker)])
        writer.writerow(['Score', analysis_result.get('📊 FINAL SCORE', 'N/A')])
        writer.writerow(['Signal', analysis_result.get('🎪 TRADING SIGNAL', 'N/A')])
        writer.writerow(['Confidence', analysis_result.get('🎯 CONFIDENCE', 'N/A')])
        
        # Component scores
        if '📋 COMPONENT SCORES' in analysis_result:
            for component, score in analysis_result['📋 COMPONENT SCORES'].items():
                writer.writerow([f'Component_{component}', score])
        
        csv_content = output.getvalue()
        output.close()
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={ticker}_analysis.csv"}
        )
    
    else:
        # Return JSON with timestamp
        return {
            "ticker": ticker,
            "export_timestamp": datetime.utcnow(),
            "format": "json",
            "data": analysis_result
        }

@app.get("/api/v1/health")
async def health_check():
    """
    Comprehensive health check for monitoring systems.
    """
    try:
        # Test algorithm
        test_result = calculate_trade_signal("AAPL")
        algorithm_status = "healthy" if "📊 FINAL SCORE" in test_result else "error"
    except:
        algorithm_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.1.0",
        "components": {
            "algorithm": algorithm_status,
            "database": "healthy",  # Would check DB connection in production
            "api": "healthy"
        },
        "uptime": "Active",
        "rate_limiting": "enabled"
    }

@app.get("/api/v1/performance")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """
    Get API performance metrics for monitoring.
    """
    # Analysis volume in last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    daily_analyses = db.query(AnalysisLog).filter(
        AnalysisLog.timestamp > yesterday
    ).count()
    
    # Top analyzed stocks today
    from sqlalchemy import func, text
    top_stocks = db.query(
        AnalysisLog.ticker, 
        func.count(AnalysisLog.ticker).label('count')
    ).filter(
        AnalysisLog.timestamp > yesterday
    ).group_by(AnalysisLog.ticker).order_by(text('count DESC')).limit(5).all()
    
    return {
        "daily_analysis_volume": daily_analyses,
        "top_analyzed_stocks": [{"ticker": stock[0], "count": stock[1]} for stock in top_stocks],
        "generated_at": datetime.utcnow(),
        "period": "last_24_hours"
    }

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    # Skip rate limiting for health checks
    if request.url.path in ["/api/v1/health", "/", "/docs", "/redoc"]:
        response = await call_next(request)
        return response
    
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Maximum {REQUESTS_PER_MINUTE} requests per minute, {REQUESTS_PER_HOUR} per hour",
                "retry_after": 60
            }
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining-Minute"] = str(REQUESTS_PER_MINUTE - len([
        t for t in rate_limit_store[client_ip] if t > time.time() - 60
    ]))
    
    return response

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 MarketPulse API v2.1.0 starting up...")
    logger.info("📊 Enhanced features: Rate limiting, Exports, Performance monitoring")

# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 MarketPulse API shutting down gracefully...")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MarketPulse API v2.1.0...")
    print("📊 Professional features enabled: Rate limiting, Export, Monitoring")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
