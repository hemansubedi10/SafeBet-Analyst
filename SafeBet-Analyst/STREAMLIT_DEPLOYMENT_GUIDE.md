# Streamlit Sharing Deployment Guide for SpeedoVIP

## Repository Structure Required for Streamlit Sharing

```
your-repo-name/
├── .streamlit/
│   └── config.toml
├── scraper/
│   └── bet_scraper.py
├── ai_analyzer/
│   ├── predictor.py
│   └── upcoming_predictor.py
├── ui/
│   └── dashboard.py
├── utils/
│   ├── data_utils.py
│   └── live_score_updater.py
├── main.py
├── requirements.txt
├── setup.sh
└── README.md
```

## Deployment Steps

1. **Create a new GitHub repository** with your code
2. **Add all files** to match the structure above
3. **Push to GitHub**
4. **Go to share.streamlit.io**
5. **Connect your GitHub repository**
6. **Set the main file path to `main.py`**
7. **Click "Deploy"**

## Important Notes for Streamlit Sharing

- The application will run in a containerized environment
- Playwright browsers need to be installed via setup.sh
- Some features may be limited due to security restrictions
- Web scraping may be restricted in some environments
- API keys should be set as secrets in Streamlit Sharing settings

## Environment Variables (Set in Streamlit Sharing Secrets)

In your Streamlit Sharing app settings, add these secrets:

```toml
QWEN_API_KEY = "your_qwen_api_key"
OPENAI_API_KEY = "your_openai_api_key"
XBET_USERNAME = "your_username"  # Optional
XBET_PASSWORD = "your_password"  # Optional
```

## Troubleshooting Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are in requirements.txt
2. **Playwright errors**: Ensure setup.sh installs Playwright browsers
3. **Permission errors**: Some features may not work due to sandbox restrictions
4. **Timeout errors**: Streamlit Sharing has timeout limits for free tier

## Features Available in Streamlit Sharing

Due to security restrictions, the following features work:
- AI Predictions and analysis
- Live scores simulation (mock data)
- VIP sections with best probability picks
- Prediction history tracking
- Dashboard interface

Features that may be limited:
- Actual 1xBet account login and data scraping
- Real-time live score updates from external APIs

## Performance Tips

- Minimize heavy computations
- Cache results when possible
- Use efficient data structures
- Limit the number of API calls