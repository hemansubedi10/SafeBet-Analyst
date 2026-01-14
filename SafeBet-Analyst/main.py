import streamlit as st
from ui.dashboard import run_dashboard
from scraper.bet_scraper import BetScraper
from ai_analyzer.predictor import AIPredictor

def main():
    st.set_page_config(
        page_title="SpeedoVIP - Premium Football Analysis",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add a loading indicator
    with st.spinner('Loading SpeedoVIP Premium Football Analysis...'):
        run_dashboard()

if __name__ == "__main__":
    main()