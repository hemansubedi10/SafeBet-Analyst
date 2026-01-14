"""
SafeBet Analyst - Streamlit Dashboard
Main UI for displaying bet data and AI predictions
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from ai_analyzer.upcoming_predictor import UpcomingEventPredictor
from scraper.bet_scraper import BetScraper
from ai_analyzer.predictor import AIPredictor
from utils.live_score_updater import live_updater
import asyncio

def run_dashboard():
    # Custom header with SpeedoVIP branding
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🚀 SpeedoVIP - Premium Football Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #50C878;'>AI-Powered Betting Analysis & Prediction Tool</h3>", unsafe_allow_html=True)

    # Add a custom logo/text representation for HemanVIP
    st.markdown("<div style='text-align: center; background-color: #f0f8ff; padding: 10px; border-radius: 10px; margin-bottom: 20px;'><h2 style='color: #FF6B35;'>🔥 HemanVIP Exclusive 🔥</h2></div>", unsafe_allow_html=True)

    # Initialize session state
    if 'bets_data' not in st.session_state:
        st.session_state.bets_data = {'active': [], 'historical': []}
    if 'predictions' not in st.session_state:
        st.session_state.predictions = []
    if 'live_scores' not in st.session_state:
        st.session_state.live_scores = {}
    if 'auto_update_enabled' not in st.session_state:
        st.session_state.auto_update_enabled = False
    if 'prediction_history' not in st.session_state:
        st.session_state.prediction_history = []
    if 'best_2plus_predictions' not in st.session_state:
        st.session_state.best_2plus_predictions = []
    if 'best_5plus_predictions' not in st.session_state:
        st.session_state.best_5plus_predictions = []
    if 'scraper' not in st.session_state:
        st.session_state.scraper = None
    if 'ai_predictor' not in st.session_state:
        st.session_state.ai_predictor = AIPredictor()

    # Initialize predictor
    predictor = UpcomingEventPredictor()

    # Auto-update live scores if enabled
    if st.session_state.auto_update_enabled and not live_updater.is_running:
        live_updater.start_auto_update()
    elif not st.session_state.auto_update_enabled and live_updater.is_running:
        live_updater.stop_auto_update()

    # Update live scores in session state
    if st.session_state.auto_update_enabled:
        st.session_state.live_scores = live_updater.live_matches

    # Update prediction history
    st.session_state.prediction_history = live_updater.get_prediction_history()

    # Update best predictions for VIP sections
    st.session_state.best_2plus_predictions = predictor.get_2plus_best_predictions(top_n=10)
    st.session_state.best_5plus_predictions = predictor.get_5plus_best_predictions(top_n=10)

    # Sidebar for navigation and settings
    st.sidebar.header("🎯 SpeedoVIP Navigation")
    page = st.sidebar.selectbox("Choose a page", ["🏠 Dashboard", "🎫 My Bets", "🔮 AI Predictions", "⚽ Live Scores", "📊 Prediction History", "⚙️ Settings"])

    # Auto-update toggle
    st.sidebar.header("📡 Live Updates")
    auto_update = st.sidebar.checkbox("Enable Auto-Update", value=st.session_state.auto_update_enabled)
    if auto_update != st.session_state.auto_update_enabled:
        st.session_state.auto_update_enabled = auto_update
        if auto_update:
            live_updater.start_auto_update()
        else:
            live_updater.stop_auto_update()
        st.rerun()

    # Manual refresh buttons
    st.sidebar.header("🔄 Data Control")
    if st.sidebar.button("🔄 Refresh Bet Data"):
        st.session_state.bets_data = {'active': [], 'historical': []}
        st.rerun()

    if st.sidebar.button("🔮 Refresh AI Predictions"):
        st.session_state.predictions = predictor.predict_top_matches(count=3)
        st.rerun()

    if st.sidebar.button("⚽ Refresh Live Scores"):
        live_updater.update_live_data()
        st.session_state.live_scores = live_updater.live_matches
        st.rerun()

    # Get AI predictions
    if not st.session_state.predictions:
        try:
            st.session_state.predictions = predictor.predict_top_matches(count=3)
        except Exception as e:
            st.error(f"Error getting AI predictions: {str(e)}")
            st.session_state.predictions = []

    if page == "🏠 Dashboard":
        show_dashboard(st.session_state.bets_data['active'], st.session_state.bets_data['historical'], st.session_state.predictions)
    elif page == "🎫 My Bets":
        show_my_bets(st.session_state.bets_data['active'], st.session_state.bets_data['historical'])
    elif page == "🔮 AI Predictions":
        show_ai_predictions(st.session_state.predictions)
    elif page == "⚽ Live Scores":
        show_live_scores(st.session_state.live_scores)
    elif page == "📊 Prediction History":
        show_prediction_history(st.session_state.prediction_history)
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard(active_bets, historical_bets, ai_predictions):
    st.markdown("## 🏠 SpeedoVIP Dashboard Overview")

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)

    total_staked = sum([bet.get('stake', 0) for bet in active_bets])
    potential_winnings = sum([bet.get('potential_win', 0) for bet in active_bets if bet.get('status', '').lower() in ['active', 'pending']])
    wins = len([bet for bet in historical_bets if bet.get('status', '').lower() == 'won'])
    losses = len([bet for bet in historical_bets if bet.get('status', '').lower() == 'lost'])

    with col1:
        st.metric(label="Active Bets", value=len(active_bets))
    with col2:
        st.metric(label="Total Staked", value=f"${total_staked:.2f}")
    with col3:
        st.metric(label="Potential Winnings", value=f"${potential_winnings:.2f}")
    with col4:
        win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
        st.metric(label="Win Rate", value=f"{win_rate:.1f}%")

    # Active bets section
    st.subheader("📈 My Active Bets")
    if active_bets:
        active_df = pd.DataFrame(active_bets)
        if not active_df.empty:
            columns_to_show = [col for col in ['match_name', 'bet_type', 'odds', 'stake', 'potential_win', 'status', 'time_left'] if col in active_df.columns]
            active_df_display = active_df[columns_to_show]
            st.dataframe(active_df_display, use_container_width=True)
        else:
            st.info("No data to display")
    else:
        st.info("No active bets found")

    # Recent activity
    st.subheader("📋 Recent Activity")
    if historical_bets:
        hist_df = pd.DataFrame(historical_bets)
        if not hist_df.empty:
            columns_to_show = [col for col in ['match_name', 'bet_type', 'stake', 'status', 'date', 'actual_win'] if col in hist_df.columns]
            hist_df_display = hist_df[columns_to_show]
            hist_df_display = hist_df_display.copy()  # Avoid SettingWithCopyWarning
            if 'date' in hist_df_display.columns:
                hist_df_display['date'] = pd.to_datetime(hist_df_display['date']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(hist_df_display, use_container_width=True)
        else:
            st.info("No data to display")
    else:
        st.info("No historical data found")

    # AI Predictions for tomorrow
    st.subheader("🤖 AI Predictions for Upcoming Events")
    if ai_predictions:
        for i, pred in enumerate(ai_predictions[:3]):  # Show top 3
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{pred['match']}**")
                    st.write(f"Prediction: {pred['predicted_outcome']}")
                    st.write(f"H2H Stats: {pred['h2h_stats']}")
                with col2:
                    st.metric(label="Confidence", value=f"{pred['confidence']}%")

                # Key factors
                with st.expander("Key Factors"):
                    for factor in pred['key_factors']:
                        st.write(f"- {factor}")

                st.markdown("---")
    else:
        st.info("No AI predictions available")

def show_my_bets(active_bets, historical_bets):
    st.markdown("## 🎫 SpeedoVIP My Bets")

    tab1, tab2 = st.tabs(["Active Bets", "History"])

    with tab1:
        if active_bets:
            df = pd.DataFrame(active_bets)
            if not df.empty:
                columns_to_show = [col for col in ['match_name', 'bet_type', 'odds', 'stake', 'potential_win', 'status', 'time_left', 'timestamp'] if col in df.columns]
                df_display = df[columns_to_show]
                df_display = df_display.copy()  # Avoid SettingWithCopyWarning
                if 'timestamp' in df_display.columns:
                    df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("No data to display")
        else:
            st.info("No active bets found")

    with tab2:
        if historical_bets:
            df = pd.DataFrame(historical_bets)
            if not df.empty:
                columns_to_show = [col for col in ['match_name', 'bet_type', 'odds', 'stake', 'status', 'actual_win', 'date'] if col in df.columns]
                df_display = df[columns_to_show]
                df_display = df_display.copy()  # Avoid SettingWithCopyWarning
                if 'date' in df_display.columns:
                    df_display['date'] = pd.to_datetime(df_display['date']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("No data to display")
        else:
            st.info("No historical data found")

def show_ai_predictions(predictions):
    st.header("🤖 AI Predictions")

    # Initialize predictor to get specialized sections
    predictor = UpcomingEventPredictor()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["General Probability", "2+ VIP Section", "5+ VIP Section", "Slip Format"])

    with tab1:
        st.subheader("General Probability Section")
        if predictions:
            for i, pred in enumerate(predictions):
                with st.expander(f"{pred['match']} - {pred['predicted_outcome']} ({pred['confidence']}% confidence)", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Match:** {pred['match']}")
                        st.write(f"**Prediction:** {pred['predicted_outcome']}")
                        # Format the match date properly
                        match_date = pred.get('match_date', 'TBD')
                        if match_date != 'TBD':
                            # Try to parse and format the date
                            try:
                                from datetime import datetime
                                parsed_date = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                                formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")
                                st.write(f"**Match Date:** {formatted_date}")
                            except:
                                st.write(f"**Match Date:** {match_date}")
                        else:
                            st.write(f"**Match Date:** {match_date}")
                    with col2:
                        st.metric(label="Confidence Level", value=f"{pred['confidence']}%")
                        st.metric(label="Risk Level", value=pred['betting_markets']['RiskLevel'])

                    # Match Result Probabilities
                    st.subheader("Match Result Probabilities:")
                    result_cols = st.columns(3)
                    with result_cols[0]:
                        st.metric(label="Home Win", value=f"{pred['betting_markets']['MatchResult']['Win']}%")
                    with result_cols[1]:
                        st.metric(label="Draw", value=f"{pred['betting_markets']['MatchResult']['Draw']}%")
                    with result_cols[2]:
                        st.metric(label="Away Win", value=f"{pred['betting_markets']['MatchResult']['Lose']}%")

                    # Over/Under Markets
                    st.subheader("Over/Under Goals Markets:")
                    under_cols = st.columns(4)
                    thresholds = ['0.5', '1.5', '2.5', '3.5']
                    for idx, threshold in enumerate(thresholds):
                        with under_cols[idx]:
                            st.metric(
                                label=f"O/U {threshold}",
                                value=f"{pred['betting_markets']['OverUnder'][threshold]['Over']}%",
                                delta=f"{pred['betting_markets']['OverUnder'][threshold]['Under']}%"
                            )

                    # BTTS and Double Chance
                    st.subheader("Special Markets:")
                    special_cols = st.columns(3)
                    with special_cols[0]:
                        st.metric(label="BTTS Yes", value=f"{pred['betting_markets']['BTTS']['Yes']}%")
                        st.metric(label="BTTS No", value=f"{pred['betting_markets']['BTTS']['No']}%")
                    with special_cols[1]:
                        st.metric(label="Home/Draw", value=f"{pred['betting_markets']['DoubleChance']['TeamA/Draw']}%")
                        st.metric(label="Away/Draw", value=f"{pred['betting_markets']['DoubleChance']['TeamB/Draw']}%")
                    with special_cols[2]:
                        st.metric(label="Home/Away", value=f"{pred['betting_markets']['DoubleChance']['TeamA/TeamB']}%")

                    # Correct Scores
                    st.subheader("Top 5 Correct Scores:")
                    score_cols = st.columns(5)
                    scores = list(pred['betting_markets']['CorrectScores'].items())
                    for idx, (score, prob) in enumerate(scores[:5]):
                        with score_cols[idx]:
                            st.metric(label=score, value=f"{prob}%")

                    # Key Factors
                    st.subheader("Key Factors:")
                    for factor in pred['betting_markets']['KeyFactors']:
                        st.write(f"- {factor}")

                    # H2H stats
                    st.subheader("Historical Head-to-Head:")
                    st.write(pred['h2h_stats'])
        else:
            st.info("No AI predictions available")

    with tab2:
        st.subheader("2+ VIP Section (Best Probability Predictions)")
        # Use the best probability predictions for 2+ odds
        best_2plus_predictions = st.session_state.best_2plus_predictions
        high_conf_2plus = [p for p in best_2plus_predictions if p['confidence'] >= 80]  # Lowered threshold to show more

        if high_conf_2plus:
            # Group into slips of 2-3 matches each
            slips = []
            for i in range(0, len(high_conf_2plus), 3):
                slip = high_conf_2plus[i:i+3]
                slips.append(slip)

            # Display up to 5 slips
            for idx, slip in enumerate(slips[:5]):
                with st.container():
                    st.markdown(f"### 🎫 **VIP Slip #{idx+1}**")
                    for match_pred in slip:
                        # Determine the recommended bet based on highest probability
                        match_result = match_pred['betting_markets']['MatchResult']
                        max_result = max(match_result, key=match_result.get)

                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                            with col1:
                                st.write(f"**{match_pred['match']}**")
                                st.caption(f"Predicted: {max_result} ({match_result[max_result]}%)")

                            with col2:
                                st.metric(label="Odds", value=f"{match_pred['calculated_odd']}")

                            with col3:
                                st.metric(label="Confidence", value=f"{match_pred['confidence']}%")

                            with col4:
                                if match_pred['confidence'] >= 90:
                                    st.success("🎯 TOP")
                                elif match_pred['confidence'] >= 80:
                                    st.success("⭐ HIGH")
                                else:
                                    st.info("⚡ MED")

                            # Key factors
                            with st.expander("Key Factors"):
                                for factor in match_pred['betting_markets']['KeyFactors'][:2]:
                                    st.write(f"- {factor}")

                            st.divider()
                    st.markdown("---")
        else:
            st.info("No high-confidence predictions available for 2+ odds range")

    with tab3:
        st.subheader("5+ VIP Section (Premium High-Odds Predictions)")
        # Use the best probability predictions for 5+ odds
        best_5plus_predictions = st.session_state.best_5plus_predictions
        high_conf_5plus = [p for p in best_5plus_predictions if p['confidence'] >= 70]  # Lowered threshold to show more

        if high_conf_5plus:
            # Group into slips of 1-2 matches each (since 5+ odds are rarer)
            slips = []
            for i in range(0, len(high_conf_5plus), 2):
                slip = high_conf_5plus[i:i+2]
                slips.append(slip)

            # Display up to 5 slips
            for idx, slip in enumerate(slips[:5]):
                with st.container():
                    st.markdown(f"### 💎 **PREMIUM Slip #{idx+1}**")
                    for match_pred in slip:
                        # Determine the recommended bet based on highest probability
                        match_result = match_pred['betting_markets']['MatchResult']
                        max_result = max(match_result, key=match_result.get)

                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                            with col1:
                                st.write(f"**{match_pred['match']}**")
                                st.caption(f"Predicted: {max_result} ({match_result[max_result]}%)")

                            with col2:
                                st.metric(label="Odds", value=f"{match_pred['calculated_odd']}")

                            with col3:
                                st.metric(label="Confidence", value=f"{match_pred['confidence']}%")

                            with col4:
                                if match_pred['confidence'] >= 85:
                                    st.success("🏆 LEGEND")
                                elif match_pred['confidence'] >= 75:
                                    st.success("🎯 PREMIUM")
                                else:
                                    st.warning("⚡ GOOD")

                            # Key factors
                            with st.expander("Key Factors"):
                                for factor in match_pred['betting_markets']['KeyFactors'][:2]:
                                    st.write(f"- {factor}")

                            st.divider()
                    st.markdown("---")
        else:
            st.info("No high-confidence predictions available for 5+ odds range")

    with tab4:
        st.subheader("Slip Format View")
        # Show slip format for different odd thresholds
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 2+ Odds Slips")
            two_plus_slips = predictor.get_slip_format_predictions(odd_threshold=2.0)
            high_conf_2_slips = [s for s in two_plus_slips if s['confidence'] >= 90]

            for i, slip in enumerate(high_conf_2_slips[:3]):
                with st.container(border=True):
                    st.write(f"**{slip['match']}**")
                    st.write(f"Recommended: {slip['recommended_bet']}")
                    st.write(f"Probability: {slip['probability']}%")
                    st.write(f"Odds: {slip['implied_odd']}")
                    st.write(f"Confidence: {slip['confidence']}%")
                    if slip['confidence'] >= 90:
                        st.success("🎯 HIGH CONFIDENCE")

        with col2:
            st.markdown("### 5+ Odds Slips")
            five_plus_slips = predictor.get_slip_format_predictions(odd_threshold=5.0)
            high_conf_5_slips = [s for s in five_plus_slips if s['confidence'] >= 90]

            for i, slip in enumerate(high_conf_5_slips[:3]):
                with st.container(border=True):
                    st.write(f"**{slip['match']}**")
                    st.write(f"Recommended: {slip['recommended_bet']}")
                    st.write(f"Probability: {slip['probability']}%")
                    st.write(f"Odds: {slip['implied_odd']}")
                    st.write(f"Confidence: {slip['confidence']}%")
                    if slip['confidence'] >= 90:
                        st.success("💎 PREMIUM PICK")

def show_settings():
    st.markdown("## ⚙️ SpeedoVIP Settings")

    st.subheader("API Configuration")
    api_key = st.text_input("Qwen API Key", type="password",
                           help="Enter your Qwen API key for AI analysis",
                           value=os.getenv("QWEN_API_KEY", ""))

    if api_key:
        os.environ["QWEN_API_KEY"] = api_key
        st.success("API key saved!")

    st.subheader("Account Information")
    username = st.text_input("1xBet Username",
                            help="Enter your 1xBet username for data access",
                            value=os.getenv("XBET_USERNAME", ""))
    password = st.text_input("1xBet Password", type="password",
                            help="Enter your 1xBet password for data access",
                            value=os.getenv("XBET_PASSWORD", ""))

    if username and password:
        os.environ["XBET_USERNAME"] = username
        os.environ["XBET_PASSWORD"] = password
        st.success("Account credentials saved!")

    st.subheader("Scraping Settings")
    auto_refresh = st.checkbox("Auto-refresh bet data", value=False)
    refresh_interval = st.slider("Refresh interval (minutes)", 1, 60, 10)

    st.subheader("Notification Settings")
    notify_new_bets = st.checkbox("Notify on new bets", value=True)
    notify_ai_updates = st.checkbox("Notify on AI prediction updates", value=True)

    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

        # Initialize scraper if credentials are provided
        if username and password and api_key:
            try:
                scraper = BetScraper()
                st.session_state.scraper = scraper
                st.success("Scraper initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing scraper: {str(e)}")


def show_live_scores(live_scores):
    st.markdown("## ⚽ SpeedoVIP Live Scores & Game States")

    # Auto-update status
    if st.session_state.auto_update_enabled:
        st.success(f"📡 Auto-update enabled (refreshing every {live_updater.update_interval}s)")
    else:
        st.info("📡 Auto-update disabled - use 'Refresh Live Scores' button to update")

    # Get live matches
    live_matches = {k: v for k, v in live_scores.items() if v['status'] == 'LIVE'}
    finished_matches = {k: v for k, v in live_scores.items() if v['status'] == 'FINISHED'}

    # Tabs for different match states
    live_tab, finished_tab = st.tabs([f"🔴 Live Matches ({len(live_matches)})", f"✅ Finished ({len(finished_matches)})"])

    with live_tab:
        if live_matches:
            for match_id, match_data in live_matches.items():
                with st.container():
                    # Match header
                    st.markdown(f"### {match_data['home_team']} vs {match_data['away_team']}")
                    st.markdown(f"*{match_data['league']} | {match_data['venue']}*")

                    # Score display
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"#### {match_data['home_team']}")
                    with col2:
                        st.markdown(f"### {match_data['home_score']} - {match_data['away_score']}")
                        st.markdown(f"**{match_data['minute']}'**")
                    with col3:
                        st.markdown(f"#### {match_data['away_team']}")

                    # Status indicator
                    st.success(f"🔴 LIVE - {match_data['minute']}' minute")

                    # Last update time
                    try:
                        last_update = datetime.fromisoformat(match_data['last_update'].replace('Z', '+00:00'))
                        st.caption(f"Last updated: {last_update.strftime('%H:%M:%S')}")
                    except:
                        st.caption("Last updated: Just now")

                    st.divider()
        else:
            st.info("No live matches currently. Check back later!")

    with finished_tab:
        if finished_matches:
            for match_id, match_data in finished_matches.items():
                with st.container():
                    # Match header
                    st.markdown(f"### {match_data['home_team']} vs {match_data['away_team']}")
                    st.markdown(f"*{match_data['league']} | FT*")

                    # Score display
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col1:
                        st.markdown(f"#### {match_data['home_team']}")
                    with col2:
                        st.markdown(f"### {match_data['home_score']} - {match_data['away_score']}")
                        st.markdown("**FT**")
                    with col3:
                        st.markdown(f"#### {match_data['away_team']}")

                    # Status indicator
                    st.info("✅ FINISHED")

                    # Last update time
                    try:
                        last_update = datetime.fromisoformat(match_data['last_update'].replace('Z', '+00:00'))
                        st.caption(f"Finished: {last_update.strftime('%H:%M')}")
                    except:
                        st.caption("Status: Final")

                    st.divider()
        else:
            st.info("No recently finished matches.")

    # Additional stats
    st.markdown("### 📊 Live Match Statistics")
    if live_matches:
        total_live = len(live_matches)
        total_goals = sum(m['home_score'] + m['away_score'] for m in live_matches.values())
        avg_minute = sum(int(m['minute']) if isinstance(m['minute'], int) else 0 for m in live_matches.values()) / total_live if total_live > 0 else 0

        stats_col1, stats_col2, stats_col3 = st.columns(3)
        with stats_col1:
            st.metric("Live Matches", total_live)
        with stats_col2:
            st.metric("Total Goals", total_goals)
        with stats_col3:
            st.metric("Avg. Minute", f"{avg_minute:.0f}")
    else:
        st.info("No live matches to show statistics for.")


def show_prediction_history(history):
    st.markdown("## 📊 SpeedoVIP Prediction History")

    if not history:
        st.info("No prediction history available yet. Predictions will appear here after they are completed.")
        return

    # Tabs for overall history and VIP sections
    overall_tab, two_plus_tab, five_plus_tab = st.tabs([
        f"📈 Overall History ({len(history)})",
        f"🎯 2+ VIP History ({len([h for h in history if h['vip_section'] == '2+'])})",
        f"💎 5+ VIP History ({len([h for h in history if h['vip_section'] == '5+'])})"
    ])

    with overall_tab:
        st.subheader("All Predictions - Last 30 Days")

        # Summary metrics
        total_predictions = len(history)
        correct_predictions = len([h for h in history if h['was_correct']])
        accuracy_rate = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Predictions", total_predictions)
        with col2:
            st.metric("Correct Predictions", correct_predictions)
        with col3:
            st.metric("Accuracy Rate", f"{accuracy_rate:.1f}%")

        # Display history table
        history_data = []
        for record in history:
            # Parse the date
            try:
                pred_date = datetime.fromisoformat(record['predicted_at'].replace('Z', '+00:00'))
                formatted_date = pred_date.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = "Unknown"

            history_data.append({
                "Date": formatted_date,
                "Match": record['match_id'] if 'match_id' in record else record.get('match', 'Unknown'),
                "Predicted": record['predicted_outcome'],
                "Actual": record['actual_outcome'],
                "Confidence": f"{record['confidence']}%",
                "VIP Section": record['vip_section'],
                "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
            })

        if history_data:
            import pandas as pd
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)

    with two_plus_tab:
        st.subheader("2+ VIP Section - Best Performers")
        two_plus_history = [h for h in history if h['vip_section'] == '2+']

        if two_plus_history:
            # Summary for 2+ section
            total_2plus = len(two_plus_history)
            correct_2plus = len([h for h in two_plus_history if h['was_correct']])
            accuracy_2plus = (correct_2plus / total_2plus * 100) if total_2plus > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Predictions", total_2plus)
            with col2:
                st.metric("Correct Predictions", correct_2plus)
            with col3:
                st.metric("Accuracy Rate", f"{accuracy_2plus:.1f}%")

            # Show 2+ VIP history
            two_plus_data = []
            for record in two_plus_history:
                try:
                    pred_date = datetime.fromisoformat(record['predicted_at'].replace('Z', '+00:00'))
                    formatted_date = pred_date.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = "Unknown"

                two_plus_data.append({
                    "Date": formatted_date,
                    "Match": record['match_id'] if 'match_id' in record else record.get('match', 'Unknown'),
                    "Predicted": record['predicted_outcome'],
                    "Actual": record['actual_outcome'],
                    "Confidence": f"{record['confidence']}%",
                    "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
                })

            if two_plus_data:
                import pandas as pd
                df_2plus = pd.DataFrame(two_plus_data)
                st.dataframe(df_2plus, use_container_width=True)
        else:
            st.info("No 2+ VIP predictions in history yet.")

    with five_plus_tab:
        st.subheader("5+ VIP Section - Premium Picks")
        five_plus_history = [h for h in history if h['vip_section'] == '5+']

        if five_plus_history:
            # Summary for 5+ section
            total_5plus = len(five_plus_history)
            correct_5plus = len([h for h in five_plus_history if h['was_correct']])
            accuracy_5plus = (correct_5plus / total_5plus * 100) if total_5plus > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Predictions", total_5plus)
            with col2:
                st.metric("Correct Predictions", correct_5plus)
            with col3:
                st.metric("Accuracy Rate", f"{accuracy_5plus:.1f}%")

            # Show 5+ VIP history
            five_plus_data = []
            for record in five_plus_history:
                try:
                    pred_date = datetime.fromisoformat(record['predicted_at'].replace('Z', '+00:00'))
                    formatted_date = pred_date.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = "Unknown"

                five_plus_data.append({
                    "Date": formatted_date,
                    "Match": record['match_id'] if 'match_id' in record else record.get('match', 'Unknown'),
                    "Predicted": record['predicted_outcome'],
                    "Actual": record['actual_outcome'],
                    "Confidence": f"{record['confidence']}%",
                    "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
                })

            if five_plus_data:
                import pandas as pd
                df_5plus = pd.DataFrame(five_plus_data)
                st.dataframe(df_5plus, use_container_width=True)
        else:
            st.info("No 5+ VIP predictions in history yet.")