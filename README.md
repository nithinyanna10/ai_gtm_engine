# 🚀 AI GTM Engine

**Intelligent Go-To-Market Automation with Real-Time Signal Detection**

An AI-powered engine that automatically discovers, scores, and generates personalized outreach for high-intent prospects using real-time data from GitHub, news APIs, and community discussions.

## 🎯 What It Does

The AI GTM Engine transforms how you find and engage prospects by:

- **🔍 Real-Time Signal Detection**: Monitors GitHub repositories, news articles, and community discussions for authentication/security issues
- **🎯 Intelligent Scoring**: Uses AI to score prospects based on intent signals and company fit
- **🤖 AI-Powered Insights**: Generates personalized outreach strategies with ChatGPT-style analysis
- **📊 Beautiful Analytics**: Real-time dashboard with data source transparency and performance metrics
- **📧 Multi-Channel Outreach**: Prioritizes leads and suggests optimal outreach approaches

## ✨ Key Features

### 🔍 **Real Data Sources**
- **GitHub API**: Finds repositories with authentication/security vulnerabilities
- **Event Registry API**: Discovers security-related news mentions
- **Reddit API**: Monitors community discussions about security issues
- **Real-time Signal Collection**: No mock data - everything is live

### 🤖 **AI-Powered Intelligence**
- **Intent Scoring**: Algorithm that combines multiple signal types
- **Business Impact Assessment**: AI analysis of security challenges
- **Personalized Outreach**: Company-specific recommendations
- **Priority Classification**: High/Medium/Low priority scoring

### 📊 **Beautiful Dashboard**
- **Real-time Analytics**: Live metrics and performance tracking
- **Data Source Transparency**: See exactly where signals come from
- **Signal Visualization**: Interactive charts and timelines
- **Lead Management**: Comprehensive prospect tracking

### 🎯 **Smart Targeting**
- **10+ Real Companies**: Shopify, Stripe, Robinhood, DoorDash, and more
- **Industry-Specific Signals**: Tailored for fintech, SaaS, and tech companies
- **Technographic Insights**: Tech stack analysis and security needs
- **Revenue-Based Prioritization**: Focus on high-value prospects

## 🏗️ Architecture

```
AI GTM Engine/
├── 📊 Dashboard (Streamlit)
│   ├── Real-time Analytics
│   ├── Lead Management
│   ├── Signal Monitoring
│   └── Outreach Management
├── 🔌 API Layer (FastAPI)
│   ├── Signal Collection
│   ├── Lead Scoring
│   └── Data Processing
├── 🔍 Data Collectors
│   ├── GitHub API
│   ├── Event Registry API
│   ├── Reddit API
│   └── Tech Stack Analysis
└── 🤖 AI Processing
    ├── Intent Scoring
    ├── Content Generation
    └── Outreach Strategy
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Git
- API Keys (see Configuration section)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/nithinyanna10/ai_gtm_engine.git
cd ai_gtm_engine
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API keys** (see Configuration section)

5. **Start the engine**
```bash
python3 start.py
```

### Access Points
- **Dashboard**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## ⚙️ Configuration

### Required API Keys

Create a `.env` file in the root directory:

```env
# OpenAI API (for AI analysis)
OPENAI_API_KEY=sk-your-openai-key

# GitHub API (for repository analysis)
GITHUB_TOKEN=ghp-your-github-token

# Event Registry API (for news analysis)
NEWS_API_KEY=your-event-registry-key

# Reddit API (for community monitoring)
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# Email Services (for outreach)
RESEND_API_KEY=your-resend-key
```

### Free API Setup

The engine is designed to work with free APIs:

- **GitHub**: Free tier with 5,000 requests/hour
- **Event Registry**: Free tier with 2,000 tokens
- **Reddit**: Free API access
- **Resend**: Free tier with 3,000 emails/month

## 📊 Dashboard Features

### 🎯 **Leads Page**
- **10 Real Companies**: Shopify, Stripe, Robinhood, DoorDash, Notion, Discord, Figma, Linear, Vercel, Plaid
- **Data Source Transparency**: See exactly where signals come from
- **AI Analysis**: Company-specific insights and recommendations
- **Real-time Signal Collection**: Live data from APIs

### 📡 **Signal Monitoring**
- **Real-time Metrics**: Total signals, data sources, confidence scores
- **Interactive Charts**: Signals by type and source
- **Timeline Visualization**: Recent signal activity
- **Performance Analytics**: Signal distribution and trends

### 📧 **Outreach Management**
- **Priority Classification**: High/Medium/Low priority leads
- **AI-Generated Strategies**: Personalized outreach approaches
- **Company Analysis**: Detailed insights for each prospect
- **Signal-Based Recommendations**: Data-driven outreach suggestions

### 📈 **Analytics Dashboard**
- **Key Performance Metrics**: Leads, signals, conversion rates
- **Company Distribution**: Industry and intent score analysis
- **Signal Analysis**: Source and confidence distribution
- **Performance Trends**: Historical data and projections

## 🔍 How It Works

### 1. **Signal Detection**
The engine continuously monitors multiple data sources:

```python
# GitHub repositories with authentication issues
search_queries = [
    "shopify authentication",
    "shopify security", 
    "shopify login"
]

# News articles about security
news_queries = [
    "Shopify authentication",
    "Shopify security",
    "Shopify login"
]
```

### 2. **Intent Scoring**
Combines multiple signal types with configurable weights:

```python
intent_score = (
    github_signals * 0.4 +
    news_signals * 0.3 +
    reddit_signals * 0.2 +
    tech_stack_fit * 0.1
)
```

### 3. **AI Analysis**
Generates personalized insights using GPT-4:

```python
analysis_prompt = f"""
Company: {company_name}
Industry: {industry}
Signals Found: {signal_count}

Provide:
1. Key security challenges identified
2. Business impact assessment  
3. Recommended outreach approach
4. Priority level (High/Medium/Low)
"""
```

## 🎯 Use Cases

### **For Sales Teams**
- **Prospect Discovery**: Find companies with immediate security needs
- **Intent Scoring**: Prioritize leads based on real signals
- **Personalized Outreach**: AI-generated messaging strategies
- **Performance Tracking**: Monitor outreach effectiveness

### **For Marketing Teams**
- **Content Opportunities**: Identify trending security topics
- **Account-Based Marketing**: Target high-intent companies
- **Campaign Optimization**: Data-driven messaging decisions
- **ROI Measurement**: Track signal-to-conversion rates

### **For Security Companies**
- **Lead Generation**: Find companies with security vulnerabilities
- **Market Intelligence**: Monitor security trends and needs
- **Competitive Analysis**: Track competitor mentions and activities
- **Product-Market Fit**: Validate security solution demand

## 🔧 Technical Details

### **Tech Stack**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: Streamlit, Plotly
- **AI**: OpenAI GPT-4, Custom scoring algorithms
- **APIs**: GitHub, Event Registry, Reddit, Resend
- **Deployment**: Docker-ready, cloud-native

### **Data Flow**
1. **Collection**: Real-time API calls to GitHub, news, Reddit
2. **Processing**: Signal extraction and scoring
3. **Storage**: Database persistence with metadata
4. **Analysis**: AI-powered insights generation
5. **Visualization**: Real-time dashboard updates

### **Scalability**
- **Modular Architecture**: Easy to add new data sources
- **Background Processing**: Celery for async signal collection
- **Caching**: Redis for API response caching
- **Horizontal Scaling**: Containerized deployment ready

## 🚀 Roadmap

### **Phase 1: Core Features** ✅
- [x] Real-time signal collection
- [x] AI-powered scoring
- [x] Beautiful dashboard
- [x] Multi-source data integration

### **Phase 2: Advanced Features** 🚧
- [ ] LinkedIn API integration
- [ ] Video content generation
- [ ] Advanced AI analysis
- [ ] Automated outreach

### **Phase 3: Enterprise Features** 📋
- [ ] Multi-tenant architecture
- [ ] Advanced analytics
- [ ] Custom scoring models
- [ ] API marketplace

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
git clone https://github.com/nithinyanna10/ai_gtm_engine.git
cd ai_gtm_engine
pip install -r requirements-dev.txt
python3 -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 integration
- **GitHub** for repository analysis APIs
- **Event Registry** for news data
- **Streamlit** for the beautiful dashboard
- **FastAPI** for the robust API framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/nithinyanna10/ai_gtm_engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nithinyanna10/ai_gtm_engine/discussions)
- **Email**: support@aigtmengine.com

---

**Built with ❤️ for smarter Go-To-Market automation**

*Transform how you find and engage prospects with AI-powered intelligence*
