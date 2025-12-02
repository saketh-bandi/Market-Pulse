# MarketPulse Terminal 🚀

**Hedge Fund Grade Financial Intelligence Platform**

A sophisticated algorithmic trading signal generator that combines sentiment analysis, options flow data, and fundamental valuation into actionable trading insights using advanced mathematical techniques.

## 🎯 Features

### Core Algorithm
- **Dynamic Regime Detection**: VIX-based market state analysis (Fear/Normal/Complacency)
- **Non-Linear Signal Combination**: Sigmoid activation functions prevent single-factor dominance
- **Z-Score Normalization**: Statistical standardization for robust scoring
- **Multi-Modal Data Fusion**: Combines 4 different data types into unified signals

### Data Sources
- 📊 **Sentiment Analysis**: Reddit sentiment via PRAW + VADER
- 🎲 **Options Flow**: Gamma sensitivity and Put/Call ratios
- 💰 **Valuation**: P/E-based fundamental analysis  
- 📈 **Market Regime**: Real-time VIX fear index

### Technology Stack
- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Next.js 16, TypeScript, TailwindCSS
- **Data**: yfinance, PRAW, NLTK, pandas
- **Visualization**: Professional gauge charts and regime indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Reddit API credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saketh-bandi/Market-Pulse.git
   cd Market-Pulse
   ```

2. **Backend Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend API**
   ```bash
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Frontend** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Terminal**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 📊 Algorithm Details

### Signal Components

| Component | Weight | Description |
|-----------|--------|-------------|
| **Sentiment** | 10-40% | Social media sentiment analysis |
| **Gamma** | 20-50% | Options market structure |
| **Volume Bias** | 20-30% | Put/call ratio analysis |
| **Valuation** | 10-20% | Fundamental fair value |

*Weights adjust dynamically based on VIX regime*

### Market Regimes

- **Fear Regime (VIX >30)**: Heavy gamma weighting, ignore sentiment noise
- **Complacency (VIX <15)**: Sentiment-driven, hype matters
- **Normal Market**: Balanced 20/30/30/20 allocation

## 🎨 Interface

### Professional Dashboard
- **Dynamic signal display** with color-coded verdicts
- **Component gauge charts** with real-time scoring
- **Regime indicator** showing current market state
- **Advanced metrics** panel with linear vs non-linear comparison

### Sample Analysis Output
```json
{
  "ticker": "NVDA",
  "signal": "STRONG BUY - NORMAL Confluence",
  "score": "86.2/100",
  "confidence": "HIGH",
  "regime": "NORMAL (VIX: 20.0)",
  "components": {
    "sentiment": "85.5/100",
    "gamma": "43.4/100", 
    "volume": "100.0/100",
    "valuation": "0.0/100"
  }
}
```

## 🔬 Technical Implementation

### Advanced Features
- **Sigmoid Activation**: `f(x) = 1/(1 + e^(-x))` for smooth probability curves
- **Z-Score Normalization**: Statistical standardization prevents outlier dominance  
- **Dynamic Weighting**: Real-time VIX-based regime detection
- **Non-Linear Combination**: Prevents single extreme value from dominating signal

### API Endpoints
- `GET /api/v1/analyze/{ticker}` - Generate trading signal
- `GET /api/v1/health` - System health check
- `GET /docs` - Interactive API documentation

## ⚠️ Disclaimer

**This is experimental software for educational purposes only.**

- Not financial advice
- Past performance doesn't guarantee future results  
- Algorithm requires backtesting and validation
- Use at your own risk

## 🛠️ Development

### Project Structure
```
market-pulse/
├── api/                 # FastAPI backend
├── src/                 # Core analysis engines
│   ├── analysis/        # Signal generation
│   └── data_loaders/    # Data collection
├── frontend/            # Next.js dashboard
├── web_app/             # Streamlit interface
└── requirements.txt     # Python dependencies
```

### Next Steps
- [ ] Historical backtesting framework
- [ ] Machine learning optimization
- [ ] Additional data sources
- [ ] Portfolio-level risk management

## 📈 Performance

*Backtesting results coming soon...*

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the future of algorithmic trading**
