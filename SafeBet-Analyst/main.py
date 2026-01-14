import streamlit as st
from ui.dashboard import run_dashboard
from scraper.bet_scraper import BetScraper
from ai_analyzer.predictor import AIPredictor

def main():
    st.set_page_config(
        page_title="SafeBet Analyst",
        page_icon="📊",
        layout="wide"
    )
    
    run_dashboard()

if __name__ == "__main__":
    main()