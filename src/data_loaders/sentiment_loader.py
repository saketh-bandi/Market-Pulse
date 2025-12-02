import praw
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta

# ---------------------------------------------------------
# CONFIG: REDDIT API CREDENTIALS
REDDIT_CLIENT_ID = "ccPs8O5MK0DHGJENBAYRdA"
REDDIT_SECRET = "BVMiUe74bchOGRz_FPZKWNBqWGRo_g"
USER_AGENT = "script:MarketPulse:v1.0 (by u/SASE_Job_Hunter)"
# ---------------------------------------------------------

def get_social_sentiment(ticker):
    """
    The 'Social Listener': Scrapes Reddit for chatter and scores emotion.
    Returns: Dict with Hype Score, Mention Volume, and Verdict.
    """
    print(f"\n--- 🗣️ RUNNING SENTIMENT ENGINE FOR {ticker} ---")
    
    # 1. Initialize the Tools
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_SECRET,
            user_agent=USER_AGENT
        )
        
        # Initialize VADER (The Sentiment Brain)
        vader = SentimentIntensityAnalyzer()
        
    except Exception as e:
        print(f"Login Failed: {e}")
        return None

    # 2. Define the Search Strategy
    # We look for the ticker symbol in the most relevant gambling dens
    query = ticker
    subreddits = "wallstreetbets+stocks+investing+options"
    
    print(f"Scanning r/{subreddits} for '{query}'...")
    
    posts_data = []
    
    try:
        # 3. Scrape the last 50 relevant posts
        # We sort by 'new' to get the current mood, not last month's news
        subreddit = reddit.subreddit(subreddits)
        for post in subreddit.search(query, sort='new', time_filter='day', limit=50):
            
            # Combine Title + Body for better context
            text = f"{post.title} {post.selftext}"
            
            # 4. Analyze Sentiment (The VADER Magic)
            # VADER handles emojis! 🚀 = Positive, 📉 = Negative
            scores = vader.polarity_scores(text)
            compound_score = scores['compound']
            
            posts_data.append({
                "Date": datetime.fromtimestamp(post.created_utc),
                "Title": post.title[:50], # Truncate for display
                "Score": compound_score,  # -1 to +1
                "Upvotes": post.score
            })
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

    # 5. Aggregate the Results
    if not posts_data:
        return {
            "Ticker": ticker,
            "Mentions": 0,
            "Sentiment Score": 0,
            "Verdict": "SILENCE (No Data)"
        }
        
    df = pd.DataFrame(posts_data)
    
    # Weighted Average? Or simple mean?
    # Simple mean is fine for MVP.
    avg_sentiment = df['Score'].mean()
    volume = len(df)
    
    # 6. Interpret the Score
    status = "NEUTRAL"
    if avg_sentiment > 0.2: status = "BULLISH (Hype)"
    if avg_sentiment > 0.5: status = "EUPHORIC (High Risk)"
    if avg_sentiment < -0.2: status = "BEARISH (Fear)"
    if avg_sentiment < -0.5: status = "PANIC (Extreme Fear)"

    return {
        "Ticker": ticker,
        "Daily Mentions": volume,
        "Average Sentiment": f"{avg_sentiment:.4f}",
        "Most Positive Post": df.loc[df['Score'].idxmax()]['Title'][:50] if volume > 0 else "N/A",
        "Most Negative Post": df.loc[df['Score'].idxmin()]['Title'][:50] if volume > 0 else "N/A",
        "SENTIMENT VERDICT": status
    }

if __name__ == "__main__":
    # Test on a "Hype" stock
    data = get_social_sentiment("NVDA")
    if data:
        print("\n🎯 === REDDIT SENTIMENT ANALYSIS === 🎯")
        print("=" * 50)
        for k, v in data.items():
            print(f"{k}: {v}")
        print("=" * 50)
        print("📱 Social Media Sentiment Complete! 🚀")
