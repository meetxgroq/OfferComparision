# 🚀 OfferCompare Pro - Quick Setup Guide

## Overview
OfferCompare Pro now supports **multiple AI providers** including Google Gemini (free tier available), OpenAI GPT, and Anthropic Claude. You only need **one API key** to get started!

## ⚡ Quick Start (Recommended - Google Gemini)

### 1. Get a Free Gemini API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" 
4. Copy your API key

### 2. Set Up Environment
```bash
# Option A: Automated Setup (Recommended)
python scripts/setup_local.py

# Option B: Manual Setup
cp .env.example .env
# Edit .env file and add your API key
```

### 3. Configure API Key
Add to your `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
DEFAULT_AI_PROVIDER=gemini
```

### 4. Install Dependencies
```bash
# With Conda (Recommended)
conda env create -f environment.yml
conda activate offercompare-pro

# Or with pip
pip install -r requirements.txt
```

### 5. Run OfferCompare Pro
```bash
python main.py
```

## 🔧 Alternative Setup Options

### OpenAI GPT (Paid)
```bash
# Get API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_api_key_here
DEFAULT_AI_PROVIDER=openai
```

### Anthropic Claude (Paid)
```bash
# Get API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_api_key_here
DEFAULT_AI_PROVIDER=anthropic
```

## 🧪 Testing Your Setup

### Quick Test
```bash
python main.py
# Select option 4: Test Utilities
# Select option 1: AI Provider Configuration
```

### Manual Test
```bash
python -c "from utils.call_llm import call_llm; print(call_llm('Hello from OfferCompare Pro!'))"
```

## 📊 Sample Usage

### Full Analysis
```bash
python main.py
# Select option 1: Full Interactive Analysis
```

### Quick Demo
```bash
python main.py
# Select option 2: Quick Demo with Sample Data
```

## 🛠️ Environment Configuration Options

Your `.env` file can include:

```bash
# AI Provider Settings
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
DEFAULT_AI_PROVIDER=gemini

# Application Settings
ENVIRONMENT=development
DEBUG=true
DEFAULT_BASE_LOCATION=San Francisco, CA

# Performance Settings
ENABLE_CACHING=true
CACHE_TIMEOUT=3600
MAX_CONCURRENT_REQUESTS=5
```

## 🎯 What Each Provider Offers

| Provider | Cost | Best For | Models Available |
|----------|------|----------|------------------|
| **Google Gemini** | **Free tier available** | **Getting started** | gemini-1.5-pro, gemini-1.5-flash |
| OpenAI GPT | Paid (usage-based) | Production use | gpt-4o, gpt-4o-mini |
| Anthropic Claude | Paid (usage-based) | Advanced analysis | claude-3-5-sonnet |

## 🔄 Provider Fallback

OfferCompare Pro automatically falls back to other providers if your primary choice fails:
- If Gemini fails → tries OpenAI → tries Claude
- Configure multiple API keys for maximum reliability

## 📞 Need Help?

### Run the guided setup:
```bash
python scripts/setup_local.py
```

### Check configuration:
```bash
python main.py
# Select option 5: Configuration & Setup
```

### Test individual components:
```bash
python main.py
# Select option 4: Test Utilities
```

---

## 🎉 You're Ready!

Once setup is complete:
1. Run `python main.py`
2. Choose "Full Interactive Analysis"
3. Enter your job offers
4. Get AI-powered recommendations!

**Pro Tip**: Start with the demo to see the full system in action before entering your own offers. 