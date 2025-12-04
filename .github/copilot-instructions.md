# GitHub Copilot Instructions for MarketPulse

## Sequential Thinking Protocol
Before answering any request, you must:

1. **Plan**: Break the request into clear, logical steps
2. **Analyze**: Consider edge cases, dependencies, and potential issues
3. **Validate**: Check for logic errors, performance concerns, and best practices
4. **Execute**: Write code only after thorough planning

## Project Context

### Project Type
- **MarketPulse**: Professional financial intelligence platform
- **Tech Stack**: Python (backend), Streamlit (web app), Next.js (frontend)
- **Purpose**: Real-time trading signals with institutional-grade analytics

### Code Quality Standards

#### Always:
- Use type hints in Python functions
- Write comprehensive docstrings
- Handle errors gracefully with try-except blocks
- Validate user inputs before processing
- Cache expensive operations (@st.cache_data)
- Use meaningful variable names (no single letters except loops)
- Follow PEP 8 style guide for Python
- Keep functions focused and under 50 lines when possible

#### Never:
- Use hardcoded API keys or secrets
- Skip error handling for external API calls
- Create functions without docstrings
- Use deprecated libraries or methods
- Write code that could cause look-ahead bias in backtesting
- Mix business logic with UI code

### Financial Domain Rules

1. **Backtesting Integrity**: Never use future data to make past decisions
2. **Risk Management**: Always include position sizing and stop-loss logic
3. **Data Validation**: Verify all market data before using in calculations
4. **Performance Metrics**: Only display empirically validated statistics
5. **Transparency**: Make algorithm logic explainable and auditable

### UI/UX Guidelines

- **Style**: Bloomberg Terminal aesthetic (dark theme, monospaced numbers, professional colors)
- **Layout**: Use Streamlit tabs, expanders, and columns for organization
- **Performance**: Lazy-load data, use caching, minimize re-renders
- **Accessibility**: Include proper labels and help text
- **Responsiveness**: Test on different screen sizes

### Common Patterns

#### API Calls
```python
@st.cache_data(ttl=300)
def fetch_data(ticker: str) -> dict:
    """Fetch data with caching and error handling."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {e}")
        return {}
```

#### Streamlit Components
```python
# Use tabs for navigation
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Analytics", "⚙️ Settings"])

# Use expanders for optional details
with st.expander("📊 View Details"):
    st.dataframe(data)

# Use columns for layout
col1, col2, col3 = st.columns(3)
```

#### Bloomberg Terminal Styling
```python
st.markdown(f"""
<div style="
    background: #1e293b; 
    border: 1px solid #475569; 
    border-radius: 12px; 
    padding: 20px;
">
    <div style="color: #00ff88; font-family: 'Roboto Mono';">{value}</div>
</div>
""", unsafe_allow_html=True)
```

### Before Making Changes

Ask yourself:
1. Does this change affect algorithm performance or validation?
2. Will this break existing functionality?
3. Is this the most maintainable approach?
4. Have I considered edge cases?
5. Is the code testable and debuggable?

### Testing Approach

- Test with multiple tickers (NVDA, TSLA, AAPL, etc.)
- Verify algorithm signals match expected logic
- Check UI rendering on different screen sizes
- Validate data integrity and error handling
- Ensure caching works correctly

## Response Format

When responding to requests:

1. **Acknowledge**: Confirm understanding of the request
2. **Plan**: Outline the approach in bullet points
3. **Identify**: List files that need to be modified
4. **Implement**: Make changes with clear explanations
5. **Verify**: Test the changes and report results
6. **Document**: Create summary files for major changes

## Special Considerations

- **Performance**: This is a real-time trading platform - optimize for speed
- **Accuracy**: Financial data must be precise - validate everything
- **Transparency**: Users need to trust the algorithm - explain decisions
- **Compliance**: Avoid claims that could be considered financial advice
- **Scalability**: Code should handle multiple concurrent users

## Remember

The goal is to build a professional, institutional-grade financial intelligence platform that traders can rely on for making informed decisions. Every line of code should reflect this standard.
