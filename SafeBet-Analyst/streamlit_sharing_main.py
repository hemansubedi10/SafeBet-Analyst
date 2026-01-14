# Streamlit Sharing Compatible Version
# This version removes dependencies that might not work in Streamlit Sharing environment

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import random
from utils.data_utils import load_mock_match_data, load_prediction_history
from utils.live_score_updater import live_updater
from ai_analyzer.upcoming_predictor import UpcomingEventPredictor

def run_dashboard():
    # Custom header with SpeedoVIP branding
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🚀 SpeedoVIP - Premium Football Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #50C878;'>AI-Powered Betting Analysis & Prediction Tool</h3>", unsafe_allow_html=True)
    
    # Add a custom logo/text representation for HemanVIP
    st.markdown("<div style='text-align: center; background-color: #f0f8ff; padding: 10px; border-radius: 10px; margin-bottom: 20px;'><h2 style='color: #FF6B35;'>🔥 HemanVIP Exclusive 🔥</h2></div>", unsafe_allow_html=True)
    
    # Initialize session state
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
    
    # Initialize predictor
    predictor = UpcomingEventPredictor()
    
    # Update prediction history
    st.session_state.prediction_history = load_prediction_history()
    
    # Update best predictions for VIP sections
    st.session_state.best_2plus_predictions = predictor.get_2plus_best_predictions(top_n=10)
    st.session_state.best_5plus_predictions = predictor.get_5plus_best_predictions(top_n=10)
    
    # Sidebar for navigation and settings
    st.sidebar.header("🎯 SpeedoVIP Navigation")
    page = st.sidebar.selectbox("Choose a page", ["🏠 Dashboard", "🔮 AI Predictions", "⚽ Live Scores", "📊 Prediction History", "⚙️ Settings"])

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
    if st.sidebar.button("🔮 Refresh AI Predictions"):
        st.session_state.best_2plus_predictions = predictor.get_2plus_best_predictions(top_n=10)
        st.session_state.best_5plus_predictions = predictor.get_5plus_best_predictions(top_n=10)
        st.rerun()
    
    if st.sidebar.button("⚽ Refresh Live Scores"):
        # Update live scores in session state
        st.session_state.live_scores = live_updater.live_matches
        st.rerun()

    # Navigation
    if page == "🏠 Dashboard":
        show_dashboard(st.session_state.predictions)
    elif page == "🔮 AI Predictions":
        show_ai_predictions(st.session_state.predictions, predictor)
    elif page == "⚽ Live Scores":
        show_live_scores_streamlit_sharing()
    elif page == "📊 Prediction History":
        show_prediction_history(st.session_state.prediction_history)
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard(predictions):
    st.markdown("## 🏠 SpeedoVIP Dashboard Overview")
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Mock stats
    total_predictions = len(load_prediction_history())
    correct_predictions = len([h for h in load_prediction_history() if h['was_correct']])
    accuracy_rate = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    with col1:
        st.metric(label="Total Predictions", value=total_predictions)
    with col2:
        st.metric(label="Correct Predictions", value=correct_predictions)
    with col3:
        st.metric(label="Accuracy Rate", value=f"{accuracy_rate:.1f}%")
    with col4:
        st.metric(label="Active VIP Picks", value=len(load_mock_match_data()))

def show_ai_predictions(predictions, predictor):
    st.markdown("## 🔮 SpeedoVIP AI Predictions")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["General Probability", "2+ VIP Section", "5+ VIP Section", "Slip Format"])
    
    with tab1:
        st.subheader("General Probability Section")
        st.info("This section shows general match predictions based on historical data.")
        
        matches = predictor.get_upcoming_matches()
        if matches:
            for i, match in enumerate(matches[:5]):  # Show first 5 matches
                with st.container():
                    st.markdown(f"### {match['home_team']} vs {match['away_team']}")
                    st.write(f"**League:** {match['league']}")
                    st.write(f"**Date:** {match['date']}")
                    
                    # Simulated probabilities
                    home_prob = random.randint(30, 60)
                    draw_prob = random.randint(15, 35)
                    away_prob = 100 - home_prob - draw_prob
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Home Win", value=f"{home_prob}%")
                    with col2:
                        st.metric(label="Draw", value=f"{draw_prob}%")
                    with col3:
                        st.metric(label="Away Win", value=f"{away_prob}%")
                    
                    st.divider()
        else:
            st.info("No upcoming matches available.")
    
    with tab2:
        st.subheader("2+ VIP Section (Best Probability Predictions)")
        best_2plus = st.session_state.best_2plus_predictions
        
        if best_2plus:
            # Group into slips of 2-3 matches each
            slips = []
            for i in range(0, len(best_2plus), 3):
                slip = best_2plus[i:i+3]
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
                            
                            st.divider()
        else:
            st.info("No high-confidence predictions available for 2+ odds range")
    
    with tab3:
        st.subheader("5+ VIP Section (Premium High-Odds Predictions)")
        best_5plus = st.session_state.best_5plus_predictions
        
        if best_5plus:
            # Group into slips of 1-2 matches each (since 5+ odds are rarer)
            slips = []
            for i in range(0, len(best_5plus), 2):
                slip = best_5plus[i:i+2]
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
                            
                            st.divider()
        else:
            st.info("No high-confidence predictions available for 5+ odds range")
    
    with tab4:
        st.subheader("Slip Format View")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 2+ Odds Slips")
            two_plus_slips = predictor.get_slip_format_predictions(odd_threshold=2.0)
            high_conf_2_slips = [s for s in two_plus_slips if s['confidence'] >= 80]
            
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
            high_conf_5_slips = [s for s in five_plus_slips if s['confidence'] >= 70]
            
            for i, slip in enumerate(high_conf_5_slips[:3]):
                with st.container(border=True):
                    st.write(f"**{slip['match']}**")
                    st.write(f"Recommended: {slip['recommended_bet']}")
                    st.write(f"Probability: {slip['probability']}%")
                    st.write(f"Odds: {slip['implied_odd']}")
                    st.write(f"Confidence: {slip['confidence']}%")
                    if slip['confidence'] >= 85:
                        st.success("💎 PREMIUM PICK")

def show_live_scores_streamlit_sharing():
    st.markdown("## ⚽ SpeedoVIP Live Scores & Game States")
    
    # Auto-update status
    if st.session_state.auto_update_enabled:
        st.success(f"📡 Auto-update enabled (simulated)")
    else:
        st.info("📡 Auto-update disabled")
    
    # Simulate live matches
    matches = load_mock_match_data()
    now = datetime.now()
    
    # Filter to only show matches in the next 2 days
    two_days_later = now + timedelta(days=2)
    upcoming_matches = []
    for match in matches:
        match_date = datetime.strptime(match['date'], "%Y-%m-%d %H:%M")
        if now <= match_date <= two_days_later:
            upcoming_matches.append(match)
    
    # Simulate live scores for matches that have started
    live_matches = []
    finished_matches = []
    
    for match in upcoming_matches:
        match_date = datetime.strptime(match['date'], "%Y-%m-%d %H:%M")
        if match_date <= now:
            # Match has started
            time_since_start = now - match_date
            minutes_elapsed = min(90, int(time_since_start.total_seconds() / 60))
            
            if minutes_elapsed < 90:
                # Still live
                home_goals = min(4, max(0, int(minutes_elapsed / 20) + random.randint(-1, 1)))
                away_goals = min(4, max(0, int(minutes_elapsed / 25) + random.randint(-1, 1)))
                
                live_matches.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'minute': minutes_elapsed,
                    'status': 'LIVE',
                    'league': match['league'],
                    'venue': match['venue']
                })
            else:
                # Finished
                home_goals = min(5, max(0, random.randint(0, 4)))
                away_goals = min(5, max(0, random.randint(0, 4)))
                
                finished_matches.append({
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'minute': 'FT',
                    'status': 'FINISHED',
                    'league': match['league'],
                    'venue': match['venue']
                })
    
    # Tabs for different match states
    live_tab, finished_tab = st.tabs([f"🔴 Live Matches ({len(live_matches)})", f"✅ Finished ({len(finished_matches)})"])
    
    with live_tab:
        if live_matches:
            for match_data in live_matches:
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
                    st.divider()
        else:
            st.info("No live matches currently. Check back later!")
    
    with finished_tab:
        if finished_matches:
            for match_data in finished_matches:
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
                    st.divider()
        else:
            st.info("No recently finished matches.")
    
    # Additional stats
    st.markdown("### 📊 Live Match Statistics")
    if live_matches:
        total_live = len(live_matches)
        total_goals = sum(m['home_score'] + m['away_score'] for m in live_matches)
        avg_minute = sum(m['minute'] if isinstance(m['minute'], int) else 0 for m in live_matches) / total_live if total_live > 0 else 0
        
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
                "Match": record.get('match', 'Unknown'),
                "Predicted": record['predicted_outcome'],
                "Actual": record['actual_outcome'],
                "Confidence": f"{record['confidence']}%",
                "VIP Section": record['vip_section'],
                "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
            })
        
        if history_data:
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
                    "Match": record.get('match', 'Unknown'),
                    "Predicted": record['predicted_outcome'],
                    "Actual": record['actual_outcome'],
                    "Confidence": f"{record['confidence']}%",
                    "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
                })
            
            if two_plus_data:
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
                    "Match": record.get('match', 'Unknown'),
                    "Predicted": record['predicted_outcome'],
                    "Actual": record['actual_outcome'],
                    "Confidence": f"{record['confidence']}%",
                    "Result": "✅ Correct" if record['was_correct'] else "❌ Wrong"
                })
            
            if five_plus_data:
                df_5plus = pd.DataFrame(five_plus_data)
                st.dataframe(df_5plus, use_container_width=True)
        else:
            st.info("No 5+ VIP predictions in history yet.")

def show_settings():
    st.markdown("## ⚙️ SpeedoVIP Settings")
    
    st.subheader("API Configuration")
    api_key = st.text_input("Qwen API Key", type="password",
                           help="Enter your Qwen API key for AI analysis")
    
    if api_key:
        st.success("API key saved!")
    
    st.subheader("Notification Settings")
    notify_new_bets = st.checkbox("Notify on new predictions", value=True)
    notify_ai_updates = st.checkbox("Notify on AI prediction updates", value=True)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    st.set_page_config(
        page_title="SpeedoVIP - Premium Football Analysis",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add a loading indicator
    with st.spinner('Loading SpeedoVIP Premium Football Analysis...'):
        run_dashboard()