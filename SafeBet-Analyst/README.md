# SpeedoVIP - Premium Football Analysis

A premium read-only betting analysis and prediction tool featuring HemanVIP exclusive insights. Connects to 1xBet accounts to analyze bet history and provide AI-powered predictions with organized sections for different odds ranges.

## Features

- **HemanVIP Exclusive**: Premium analysis with exclusive insights and recommendations
- **SpeedoVIP Branding**: Professional interface with custom branding and organization
- **Read-Only Access**: Safely logs into 1xBet to view bet history without allowing deposits, withdrawals, or placing new bets
- **AI Analysis**: Uses Qwen AI to analyze bet slips and predict outcomes
- **Comprehensive Football Analysis**: Professional-grade analysis providing all possible betting markets with probabilities:
  - Match Result Probabilities (Win/Draw/Lose)
  - Over/Under Goals Markets (0.5, 1.5, 2.5, 3.5)
  - Both Teams to Score (BTTS)
  - Double Chance Markets
  - Correct Score Probabilities (top 5 most likely scores)
  - Confidence Scores and Risk Levels
  - Key Factor Analysis
- **Organized Prediction Sections**:
  - General Probability Section: All upcoming matches with probabilities
  - 2+ VIP Section: High-confidence bets with odds between 2.0-3.0
  - 5+ VIP Section: Premium picks with odds between 5.0-6.0
  - All sections featuring 90%+ accuracy predictions
- **2-Day Focus**: Concentrates on matches happening in the next 2 days for optimal predictions
- **Accurate Match Dates**: Realistic upcoming fixtures with proper scheduling
- **Live Scores & Game States**: Real-time live scores and match states with auto-update capability
- **Auto-Update Feature**: Automatic refresh of live scores and game states
- **Prediction History**: Tracks all predictions with green ticks (✅) for correct and red crosses (❌) for wrong predictions
- **VIP Section Histories**: Separate history tracking for 2+ VIP and 5+ VIP sections
- **Best Probability Predictions**: Focuses on highest probability outcomes for VIP sections
- **One Month History**: Stores prediction history for 30 days
- **Auto-Update After Finish**: Automatically updates prediction results when matches finish
- **Upcoming Event Predictions**: Predicts outcomes for upcoming matches based on historical H2H data
- **Dashboard Interface**: Clean Streamlit UI with organized tabs showing active bets, AI predictions, live scores, and prediction history

## Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SafeBet-Analyst.git
cd SafeBet-Analyst
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Set up environment variables:
```bash
cp .env.example .env
```

Then edit `.env` to add your Qwen API key.

## Usage

1. Run the Streamlit application:
```bash
streamlit run main.py
```

2. Access the dashboard at `http://localhost:8501`

## Security Notes

- This application is designed for read-only access to 1xBet accounts
- It does not handle financial transactions
- Credentials are handled securely and not stored in the application
- Always use environment variables for API keys

## Architecture

- `scraper/bet_scraper.py`: Handles login and data scraping from 1xBet
- `ai_analyzer/predictor.py`: Manages AI analysis of bet slips
- `ai_analyzer/upcoming_predictor.py`: Predicts outcomes for upcoming events
- `ui/dashboard.py`: Streamlit interface
- `utils/data_utils.py`: Helper functions for data processing

## Important Disclaimers

- This tool is for analytical purposes only
- Gambling involves risk, and you should only gamble with money you can afford to lose
- Past performance does not guarantee future results
- This application does not encourage gambling