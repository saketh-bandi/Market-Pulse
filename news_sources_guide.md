# Market News Sources - Implementation Guide

## Current Implementation (v1.0)

### Status: Mock Data with Sources Added ✅

The Market News section now displays **mock headlines with professional news sources**:

```
📰 Market News
├─ NVDA Earnings Beat (Reuters • 2 hours ago)
├─ Fed Signals Rate Hold (Bloomberg • 5 hours ago)
├─ Tech Sector Rally (CNBC • 8 hours ago)
└─ Oil Prices Stabilize (WSJ • 12 hours ago)
```

### News Sources Used:
- **Reuters**: Breaking financial news, earnings reports
- **Bloomberg**: Central bank updates, macro events
- **CNBC**: Market trends, sector movements
- **Wall Street Journal (WSJ)**: Commodities, global markets

---

## Future Enhancement: Live News API Integration

### Recommended APIs (Ranked by Quality)

#### 1. **Financial Modeling Prep (FMP) - Press Releases API**
✅ Already using FMP for market data
✅ Free tier available
✅ Real-time news with timestamps

**Endpoint:**
```python
url = f"https://financialmodelingprep.com/api/v3/press-releases/{ticker}?apikey={FMP_API_KEY}"
url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit=5&apikey={FMP_API_KEY}"
```

**Response Format:**
```json
{
  "symbol": "NVDA",
  "publishedDate": "2024-01-15T14:30:00.000Z",
  "title": "NVIDIA Reports Record Q4 Earnings",
  "text": "NVIDIA Corp reported...",
  "site": "Reuters",
  "url": "https://reuters.com/..."
}
```

---

#### 2. **Alpha Vantage - News Sentiment API**
✅ Free tier: 25 API calls/day
✅ Sentiment analysis included
✅ Multiple news sources

**Endpoint:**
```python
url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={API_KEY}"
```

**Response Format:**
```json
{
  "feed": [
    {
      "title": "Fed Signals Rate Hold",
      "url": "https://...",
      "time_published": "20240115T140000",
      "source": "Bloomberg",
      "overall_sentiment_score": 0.15
    }
  ]
}
```

---

#### 3. **NewsAPI.org**
✅ 100 requests/day free
✅ 80,000+ news sources
✅ Search by keyword/category

**Endpoint:**
```python
url = f"https://newsapi.org/v2/everything?q=stocks+{ticker}&apiKey={API_KEY}"
```

**Response Format:**
```json
{
  "articles": [
    {
      "source": {"name": "Reuters"},
      "title": "NVDA Earnings Beat",
      "description": "...",
      "publishedAt": "2024-01-15T14:00:00Z",
      "url": "https://..."
    }
  ]
}
```

---

## Implementation Roadmap

### Phase 1: Mock Data with Sources ✅ **COMPLETE**
- Display static headlines
- Add news sources (Reuters, Bloomberg, CNBC, WSJ)
- Professional formatting with timestamps

### Phase 2: FMP News Integration (Recommended Next Step)
**Estimated Effort:** 2 hours

**Steps:**
1. Add FMP news endpoint to `fmp_loader.py`
2. Create `fetch_market_news()` function
3. Cache results (TTL: 5 minutes)
4. Parse and display in Market Overview
5. Add click-through links to full articles

**Code Template:**
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_market_news(limit: int = 4) -> List[Dict]:
    """Fetch latest market news from FMP"""
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_news?limit={limit}&apikey={FMP_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        news = response.json()
        
        return [
            {
                'title': item['title'],
                'source': item.get('site', 'Market Watch'),
                'time': parse_timestamp(item['publishedDate']),
                'url': item.get('url', '#')
            }
            for item in news
        ]
    except Exception as e:
        st.error(f"News API Error: {e}")
        return []
```

### Phase 3: Ticker-Specific News (Advanced)
- Display news relevant to active ticker in Stock Analysis view
- Add sentiment indicators (🟢 Bullish | 🔴 Bearish | ⚪ Neutral)
- Track news impact on price movements

### Phase 4: AI News Summarization (Premium)
- Use GPT/Claude to summarize key points
- Extract actionable insights
- Link news events to algorithm signals

---

## Design Considerations

### UI/UX:
- Keep news section compact (4 headlines max)
- Use color-coding for sentiment (green=positive, red=negative)
- Add hover tooltips with full headline
- Make headlines clickable to source URL

### Performance:
- Cache news for 5-15 minutes (not real-time critical)
- Lazy load: Only fetch when Market Overview is visible
- Limit API calls to avoid rate limits
- Fallback to mock data if API fails

### Data Quality:
- Filter out spam/low-quality sources
- Deduplicate similar headlines
- Prioritize institutional sources (Reuters, Bloomberg, WSJ)
- Show most recent news first

---

## API Cost Comparison

| API                  | Free Tier        | Paid Plans       | Best For              |
|----------------------|------------------|------------------|-----------------------|
| FMP (Press Releases) | 250 calls/day    | $15/mo unlimited | Already integrated    |
| Alpha Vantage        | 25 calls/day     | $49/mo           | Sentiment analysis    |
| NewsAPI.org          | 100 calls/day    | $449/mo          | Broad news coverage   |
| Finnhub              | 60 calls/min     | $9/mo            | Real-time updates     |

**Recommendation:** Start with **FMP** since we already use it for market data.

---

## Current Code Location

**File:** `/Users/sakethbandi/Desktop/market-pulse/web_app/app.py`  
**Lines:** 1265-1288  
**Function:** `render_market_overview()`

```python
# Market News Section (Mock Data with Sources)
<div style="color: #00ff88;">NVDA Earnings Beat</div>
<div style="font-size: 0.75rem; color: #64748b;">Reuters • 2 hours ago</div>
```

---

## Testing Checklist

When implementing live news:
- [ ] Test API rate limits with repeated requests
- [ ] Verify caching works (news doesn't refresh every second)
- [ ] Handle API errors gracefully (show fallback mock data)
- [ ] Validate news source attribution is correct
- [ ] Test with different tickers (NVDA, TSLA, AAPL)
- [ ] Check mobile responsiveness of news cards
- [ ] Ensure clickable links open in new tab
- [ ] Verify timestamps display correctly (relative time)

---

## Summary

✅ **Current:** Mock news with professional sources (Reuters, Bloomberg, CNBC, WSJ)  
⏳ **Next:** Integrate FMP news API for live headlines  
🚀 **Future:** Ticker-specific news, sentiment analysis, AI summarization

The foundation is in place—just need to swap mock data with live API calls when ready to scale.
