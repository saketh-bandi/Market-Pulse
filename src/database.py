from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# 1. DATABASE SETUP (Production-Ready Configuration)
DATABASE_URL = "sqlite:///./market_pulse.db"

# Create engine with production settings
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False  # Set to True for SQL debugging
)

# Session management (Thread-safe)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DATABASE SCHEMA (Wall Street Grade)

class StockCache(Base):
    """
    The Smart Cache: Stores analysis results to avoid API rate limits.
    If 1000 users check NVDA, we hit the APIs once and serve from cache.
    """
    __tablename__ = "stock_cache"
    
    # Primary key
    ticker = Column(String, primary_key=True, index=True)
    
    # Core price data
    current_price = Column(Float)
    fair_value = Column(Float)
    upside_percent = Column(Float)
    
    # Component scores (normalized 0-100)
    sentiment_score = Column(Float)
    gamma_score = Column(Float)
    volume_score = Column(Float)
    valuation_score = Column(Float)
    
    # Final algorithm output
    final_score = Column(Float)
    trading_signal = Column(String)
    confidence = Column(String)
    
    # Raw data (for debugging/analysis)
    raw_sentiment = Column(Float)
    raw_gamma = Column(Float)
    raw_put_call_ratio = Column(Float)
    
    # Cache metadata
    last_updated = Column(DateTime, default=datetime.utcnow, index=True)
    is_stale = Column(Boolean, default=False)  # Mark for refresh

class User(Base):
    """
    User management system for portfolio tracking and authentication.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Watchlist(Base):
    """
    User watchlists with custom alert thresholds.
    """
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Foreign key to users
    ticker = Column(String, index=True)
    alert_threshold = Column(Float, default=75.0)  # Signal score threshold
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisLog(Base):
    """
    Historical log of all analysis results for backtesting and performance tracking.
    """
    __tablename__ = "analysis_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    trading_signal = Column(String)
    final_score = Column(Float)
    actual_price_change_1d = Column(Float)  # For backtesting accuracy
    actual_price_change_7d = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class APIUsage(Base):
    """
    Track API usage to manage rate limits across all data sources.
    """
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String, index=True)  # 'yfinance', 'reddit', 'fmp'
    endpoint = Column(String)
    calls_today = Column(Integer, default=0)
    last_call = Column(DateTime, default=datetime.utcnow)
    rate_limit_hit = Column(Boolean, default=False)

# 3. DATABASE UTILITY FUNCTIONS

def get_db():
    """
    Dependency injection for FastAPI routes.
    Ensures proper session management and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database with all tables.
    Safe to run multiple times (idempotent).
    """
    print("🏗️  Initializing MarketPulse Database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"✅ Database initialized with {len(tables)} tables:")
    for table in tables:
        print(f"   📋 {table}")
    
    return True

def reset_db():
    """
    DANGER: Drops all tables and recreates them.
    Use only in development!
    """
    print("⚠️  RESETTING DATABASE - ALL DATA WILL BE LOST!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset complete.")

def check_cache_freshness(ticker: str, max_age_minutes: int = 60) -> bool:
    """
    Check if cached data for a ticker is still fresh.
    Returns True if data exists and is within max_age_minutes.
    """
    db = SessionLocal()
    try:
        cache_entry = db.query(StockCache).filter(StockCache.ticker == ticker).first()
        
        if not cache_entry:
            return False
            
        age_minutes = (datetime.utcnow() - cache_entry.last_updated).total_seconds() / 60
        return age_minutes < max_age_minutes
        
    finally:
        db.close()

def get_cached_analysis(ticker: str):
    """
    Retrieve cached analysis result if available and fresh.
    """
    db = SessionLocal()
    try:
        return db.query(StockCache).filter(StockCache.ticker == ticker).first()
    finally:
        db.close()

def cache_analysis_result(ticker: str, analysis_result: dict):
    """
    Store analysis result in cache for fast future retrieval.
    """
    db = SessionLocal()
    try:
        # Check if ticker already exists
        existing = db.query(StockCache).filter(StockCache.ticker == ticker).first()
        
        if existing:
            # Update existing record
            for key, value in analysis_result.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.last_updated = datetime.utcnow()
        else:
            # Create new cache entry
            cache_entry = StockCache(ticker=ticker, **analysis_result)
            db.add(cache_entry)
        
        db.commit()
        print(f"💾 Cached analysis result for {ticker}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error caching result for {ticker}: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize the database when run directly
    init_db()
    
    # Demo: Show database statistics
    db = SessionLocal()
    try:
        cache_count = db.query(StockCache).count()
        user_count = db.query(User).count()
        print(f"\n📊 Database Stats:")
        print(f"   🎯 Cached Stocks: {cache_count}")
        print(f"   👥 Users: {user_count}")
        print(f"\n🚀 Database ready for production!")
    finally:
        db.close()
