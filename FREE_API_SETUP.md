# 🆓 Free API Setup Guide

## 🚀 **Quick Start: Get Free API Keys**

### **1. OpenAI (Already Configured)**
- ✅ **Status**: Already set up with your key
- 💰 **Cost**: $5 free credit
- 📊 **Usage**: Content generation, lead analysis, all AI features

### **2. GitHub API (Free)**
- 🔗 **URL**: https://github.com/settings/tokens
- 📝 **Steps**:
  1. Go to GitHub Settings → Developer settings → Personal access tokens
  2. Click "Generate new token (classic)"
  3. Select scopes: `public_repo`, `read:user`
  4. Copy the token and add to `config/api_keys.yaml`

### **3. Reddit API (Free)**
- 🔗 **URL**: https://www.reddit.com/prefs/apps
- 📝 **Steps**:
  1. Go to Reddit → User Settings → Apps
  2. Click "Create App" or "Create Another App"
  3. Select "script" as app type
  4. Copy Client ID and Client Secret to `config/api_keys.yaml`

### **4. NewsAPI (Free)**
- 🔗 **URL**: https://newsapi.org/register
- 📝 **Steps**:
  1. Register for free account
  2. Get API key from dashboard
  3. Add to `config/api_keys.yaml`
- 📊 **Limit**: 1,000 requests/day

### **5. Logo.dev (Free)**
- ✅ **Status**: Already configured with your key
- 💰 **Cost**: Free tier available
- 📊 **Usage**: Company intelligence, logos, descriptions

### **6. Tech Stack Analysis (Free)**
- 🆓 **Cost**: Free (web scraping)
- 📊 **Usage**: Technology detection via website analysis
- 🔧 **Implementation**: Built-in analyzer (no API key needed)

### **7. Email Services (Free Alternatives to SendGrid)**

#### **Option A: Mailgun**
- 🔗 **URL**: https://www.mailgun.com/pricing
- 📝 **Steps**:
  1. Sign up for free account
  2. Get API key and domain
  3. Add to `config/api_keys.yaml`
- 📊 **Limit**: 5,000 emails/month for 3 months

#### **Option B: Resend**
- 🔗 **URL**: https://resend.com/pricing
- 📝 **Steps**:
  1. Sign up for free account
  2. Get API key
  3. Add to `config/api_keys.yaml`
- 📊 **Limit**: 3,000 emails/month

#### **Option C: Brevo**
- 🔗 **URL**: https://www.brevo.com/pricing/
- 📝 **Steps**:
  1. Sign up for free account
  2. Get API key
  3. Add to `config/api_keys.yaml`
- 📊 **Limit**: 300 emails/day

---

## ⚙️ **Configuration**

### **Update API Keys**
Edit `config/api_keys.yaml`:

```yaml
# GitHub API (Free: 5,000 requests/hour)
github_token: "ghp_your_github_token_here"

# Reddit API (Free: Unlimited)
reddit_client_id: "your_reddit_client_id_here"
reddit_client_secret: "your_reddit_client_secret_here"
reddit_user_agent: "AI_GTM_Engine/1.0"

# News API (Free: 1,000 requests/day)
news_api_key: "d7bfc483-4825-4b03-9ff1-91f6c392ce6a"

# Logo.dev (Free tier - company intelligence)
logo_dev_api_key: "pk_IRbXeb26QEK4FFTc60gBxg"

# Tech Stack Analysis (Free - built-in web scraping)
# No API key needed

# SendGrid (Free: 100 emails/day)
sendgrid_api_key: "your_sendgrid_api_key_here"
```

### **Test Configuration**
Run the test script to verify all APIs:

```bash
python test_apis.py
```

---

## 🎯 **What You Get with Free APIs**

### **Signal Collection**
- 🔍 **GitHub**: Code repositories, security discussions
- 💬 **Reddit**: Community discussions, pain points
- 📰 **News**: Company mentions, industry news
- 🛠️ **BuiltWith**: Tech stack analysis

### **Content Generation**
- ✉️ **Emails**: Personalized outreach messages
- 🔗 **LinkedIn**: Connection request messages
- 📞 **Phone Scripts**: Cold calling scripts
- 🎥 **Video Scripts**: Personalized video content

### **Delivery**
- 📧 **Email**: Automated email sending
- 📊 **Analytics**: Delivery tracking and metrics

---

## 📊 **Free Tier Limits**

| API | Requests | Cost | Best For |
|-----|----------|------|----------|
| **GitHub** | 5,000/hour | Free | Code analysis |
| **Reddit** | Unlimited | Free | Community signals |
| **NewsAPI** | 1,000/day | Free | News monitoring |
| **Logo.dev** | Free tier | Free | Company intelligence |
| **Tech Stack** | Unlimited | Free | Web scraping analysis |
| **Mailgun** | 5,000/month | Free | Email delivery |
| **Resend** | 3,000/month | Free | Email delivery |
| **Brevo** | 300/day | Free | Email delivery |
| **OpenAI** | $5 credit | Free | All AI content generation |

---

## 🚀 **Next Steps**

### **Immediate Actions**
1. ✅ Set up GitHub API key
2. ✅ Set up Reddit API keys
3. ✅ Set up NewsAPI key
4. ✅ Set up BuiltWith API key
5. ✅ Set up SendGrid API key
6. ✅ Test all integrations

### **Demo Results**
With free APIs, you can:
- 📊 **Collect signals** from 5+ sources
- 🤖 **Generate content** for 100+ leads
- 📧 **Send emails** to 100 leads/day
- 📈 **Track analytics** in real-time
- 🎯 **Score leads** with multi-factor analysis

### **Scaling Path**
When you hit free tier limits:
1. **NewsAPI**: Upgrade to $449/month for 100,000 requests
2. **BuiltWith**: Upgrade to $295/month for 10,000 requests
3. **SendGrid**: Upgrade to $89/month for 50,000 emails
4. **OpenAI**: Pay-as-you-go after $5 credit

---

## 🎉 **Success Metrics**

### **Free Tier Targets**
- **Leads Processed**: 50-100/month
- **Signals Collected**: 500-1,000/month
- **Emails Sent**: 100/month
- **Response Rate**: 10-15%
- **Cost**: $0 (free tier only)

### **ROI Calculation**
- **Time Saved**: 20-40 hours/month
- **Leads Generated**: 50-100/month
- **Revenue Potential**: $5,000-50,000/month
- **ROI**: Infinite (free tier)

---

## 🔧 **Troubleshooting**

### **Common Issues**
1. **Rate Limiting**: Implement delays between requests
2. **API Errors**: Check API key format and permissions
3. **Missing Data**: Some APIs may not have data for all domains
4. **Email Delivery**: Verify SendGrid domain authentication

### **Support**
- 📧 **Email**: Check API documentation for each service
- 💬 **Community**: GitHub issues for technical problems
- 📚 **Documentation**: Each API has comprehensive guides

---

## 🎯 **Ready to Scale?**

Once you've validated the free tier:
1. **Review the Scaling Plan** in `SCALING_PLAN.md`
2. **Identify bottlenecks** in your current usage
3. **Calculate ROI** from free tier results
4. **Plan Phase 1 upgrades** based on performance

The free tier gives you everything you need to prove the concept and start generating revenue!
