# finSight
> **Asset Insight | Investment Journal | Free and Ready to Use**

A comprehensive financial analysis platform focusing on Chinese and U.S. market movements, featuring AI-powered insights, real-time data, and advanced portfolio management.

## ✨ Highlights

- 🌏 **Multi-Market Support**: Focus on Chinese (A-Share, Hong Kong) and U.S. markets
- 🤖 **AI-Powered Analysis**: Intelligent insights using Gemini AI
- 📊 **Comprehensive Metrics**: Returns, volatility, Beta, Sharpe Ratio, and more
- 📰 **Real-Time News**: Financial news with sentiment analysis
- 📈 **Advanced Visualization**: Interactive charts and performance analysis
- 📝 **Investment Journal**: Track your trading rationale and observations

---

## 🎯 Key Features

### **Asset Analysis**
| Feature | Description |
|:---|:---|
| `Return & Performance` | Historical pricing, returns, and performance benchmarks |
| `Risk Profile` | Volatility (σ), systematic market exposure (β), and Sharpe Ratio |
| `Inter-Asset Relations` | Correlation and co-movement for portfolio diversification |

### **Macro Derivations**
| Feature | Description |
|:---|:---|
| `Key Metrics` | GDP, inflation, PMI, and labor market health |
| `Political Events` | Impact of policy changes, trade actions, and conflicts |

### **Daily Memo**
| Feature | Description |
|:---|:---|
| `What Happened Today` | AI-generated market activities summary |
| `Notebook` | Personal trade rationales and market observations |

---

## 🏗️ Architecture

### Technology Stack

**Backend (Python)**
- FastAPI - Modern async web framework
- SQLAlchemy - Database ORM
- akshare - Chinese market data
- yfinance - Global market data
- Gemini AI - Intelligent analysis
- Plotly - Interactive visualizations

**Frontend (React)**
- React 18 - UI framework
- TypeScript - Type safety
- React Router - Navigation
- Axios - API client
- Vite - Build tool

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- pip and npm

### Backend Setup

```bash
cd backend_python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Initialize database
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); db.create_all_tables()"

# Run server
python main.py
```

Server will start at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint
# Edit vite.config.ts if needed

# Start development server
npm run dev
```

Frontend will start at `http://localhost:3000`

---

## 🚀 Quick Start

### 1. Register an Account
Navigate to `http://localhost:3000/register` and create your account.

### 2. Add Assets to Portfolio
Search for stocks, crypto, or other assets and add them to your portfolio.

### 3. View Analysis
Click on any asset to view:
- Historical performance
- Risk metrics (Beta, Sharpe Ratio, Volatility)
- AI-powered investment insights
- Recent news with sentiment analysis

### 4. Track Macro Trends
Visit the Macro Metrics page to monitor economic indicators.

### 5. Keep a Journal
Use the Notebook feature to document your investment decisions and market observations.

---

## 📚 API Documentation

### Authentication Endpoints

```
POST /api/auth/register  - Register new user
POST /api/auth/login     - Login user
GET  /api/auth/me        - Get current user info
```

### Asset Endpoints

```
GET  /api/assets/search              - Search assets
GET  /api/assets/{symbol}/info       - Get asset information
GET  /api/assets/{symbol}/history    - Get historical prices
GET  /api/assets/{symbol}/realtime   - Get real-time price
GET  /api/assets/{symbol}/analysis   - Get comprehensive analysis
```

### Portfolio Endpoints

```
GET    /api/portfolio        - Get user portfolio
POST   /api/portfolio        - Add asset to portfolio
DELETE /api/portfolio/{id}   - Remove from portfolio
```

### Macro & News Endpoints

```
GET /api/macro/{country}              - Get macro metrics
GET /api/macro/{country}/analysis     - AI analysis of metrics
GET /api/news/market/{market}         - Get market news
GET /api/news/asset/{symbol}          - Get asset-specific news
```

### Notebook Endpoints

```
GET    /api/notebook          - Get all entries
POST   /api/notebook          - Create entry
PUT    /api/notebook/{id}     - Update entry
DELETE /api/notebook/{id}     - Delete entry
```

---

## 🔧 Configuration

### Global Configuration
Edit `backend_python/configs/global_config.yaml`:
- Market settings (timezones, currencies)
- Data fetcher settings (cache, rate limits)
- Metrics calculation parameters
- AI analysis settings
- Visualization preferences

### Asset List
Edit `backend_python/configs/asset_list.yaml`:
- Add popular assets for each market
- Define asset categories
- Configure indices

---

## 📊 Calculated Metrics

### Performance Metrics
- **Total Return**: Cumulative return over period
- **Annualized Return**: Yearly return rate
- **Cumulative Returns**: Compounded growth

### Risk Metrics
- **Volatility (σ)**: Standard deviation of returns
- **Beta (β)**: Systematic risk vs. market
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Downside Deviation**: Volatility of negative returns

### Risk-Adjusted Returns
- **Sharpe Ratio**: Excess return per unit of risk
- **Sortino Ratio**: Return per unit of downside risk
- **Alpha (α)**: Excess return vs. expected return
- **Information Ratio**: Active return vs. tracking error

### Value at Risk
- **VaR (95%)**: Maximum expected loss at 95% confidence
- **CVaR (95%)**: Expected loss beyond VaR threshold

---

## 🤖 AI Features

### Asset Analysis
- Performance evaluation
- Risk assessment
- Investment outlook
- Buy/Hold/Sell recommendations

### Market Summary
- Daily market movements
- Key drivers identification
- Sector performance highlights
- Market direction outlook

### Macro Analysis
- Economic health assessment
- Trend identification
- Policy implications
- Investment impact analysis

---

## 🛠️ Development

### Project Structure

```
finSight/
├── backend_python/          # Python FastAPI backend
│   ├── configs/            # Configuration files
│   ├── database/           # Database models and manager
│   ├── data_fetchers/      # Data acquisition modules
│   ├── user_management/    # Authentication and user config
│   ├── metrics_calculator/ # Financial metrics calculation
│   ├── visualization/      # Chart generation
│   ├── ai_analysis/        # AI-powered analysis
│   ├── utils/              # Utility functions
│   └── main.py             # FastAPI application
│
└── frontend/                # React TypeScript frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── services/       # API services
    │   └── types/          # TypeScript types
    └── vite.config.ts      # Vite configuration
```

### Running Tests

```bash
# Backend tests
cd backend_python
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🔐 Security Notes

- **JWT Tokens**: 7-day expiration, stored securely
- **Password Hashing**: bcrypt with salt rounds
- **API Keys**: Store in `.env`, never commit
- **CORS**: Configure allowed origins for production

---

## 🌐 Deployment

### Backend Deployment
1. Use PostgreSQL for production database
2. Set strong JWT_SECRET
3. Configure proper CORS origins
4. Use environment variables for all secrets
5. Deploy with gunicorn or uvicorn workers

### Frontend Deployment
1. Build production bundle: `npm run build`
2. Deploy `dist/` folder to static hosting
3. Configure API endpoint for production

---

## 📝 License

MIT License - Feel free to use for personal or commercial projects.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API endpoints documentation

---

## 🎉 Credits

**Data Sources:**
- akshare - Chinese market data
- yfinance - Global market data
- Google Gemini AI - Intelligent analysis

**Built with:**
- FastAPI, SQLAlchemy, Plotly
- React, TypeScript, Vite

---

**finSight** - Empowering informed investment decisions through data and intelligence.
