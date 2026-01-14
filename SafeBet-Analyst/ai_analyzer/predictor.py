"""
SafeBet Analyst - AI Analysis Module
Handles sending data to Qwen AI and processing predictions
"""

import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIPredictor:
    def __init__(self):
        # Initialize OpenAI client for Qwen API
        # Note: This assumes Qwen API is compatible with OpenAI format
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("QWEN_API_KEY or OPENAI_API_KEY environment variable is required")

        openai.api_key = api_key

        # Base URL for Qwen API (adjust as needed)
        base_url = os.getenv("QWEN_BASE_URL", "https://api.openai.com/v1")
        openai.base_url = base_url

    def analyze_bet_slip(self, bet_data):
        """
        Analyze a single bet slip using Qwen AI
        """
        # Prepare prompt for Qwen
        prompt = f"""
        Analyze this betting slip for potential outcome:

        Match: {bet_data.get('match_name', 'Unknown')}
        Bet Type: {bet_data.get('bet_type', 'Unknown')}
        Odds: {bet_data.get('odds', 0)}
        Stake: {bet_data.get('stake', 0)}
        Status: {bet_data.get('status', 'Unknown')}
        Potential Win: {bet_data.get('potential_win', 'N/A')}
        Actual Win: {bet_data.get('actual_win', 'N/A')}

        Using your knowledge of sports analytics, evaluate:
        1. Momentum: Which team has more dangerous attacks in the last 10 minutes? (if available)
        2. Player Status: Are key players from the slip currently on the field or subbed out? (if available)
        3. Outcome Probability: Provide a percentage (%) of the slip winning
        4. AI Suggestion: Give a recommendation (e.g., "High Probability - Stay in" or "Risk Detected - Cashout if possible")

        Respond in JSON format with the following structure:
        {{
          "win_probability": float,
          "momentum_analysis": string,
          "player_status_analysis": string,
          "ai_suggestion": string,
          "risk_level": string,
          "confidence_level": string
        }}
        """

        try:
            response = openai.chat.completions.create(
                model=os.getenv("QWEN_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an expert sports analyst with deep knowledge of betting strategies and probability assessment. Focus on providing accurate, data-driven analysis without encouraging gambling. Your analysis should be objective and based on the information provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            # Parse the response
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in AI analysis: {str(e)}")
            # Return a default response in case of error
            return {
                "win_probability": 50.0,
                "momentum_analysis": "Unable to assess momentum due to insufficient live data",
                "player_status_analysis": "Unable to assess player status due to insufficient live data",
                "ai_suggestion": "Insufficient data for accurate prediction",
                "risk_level": "Medium",
                "confidence_level": "Low"
            }

    def analyze_active_bet_with_live_data(self, bet_data, live_match_data=None):
        """
        Analyze an active bet with live match data if available
        """
        # Prepare prompt for Qwen with live data
        live_info = ""
        if live_match_data:
            live_info = f"""
            Live Match Data:
            Current Score: {live_match_data.get('score', 'N/A')}
            Minute: {live_match_data.get('minute', 'N/A')}
            Possession (Home/Away): {live_match_data.get('possession', {}).get('home', 'N/A')}% / {live_match_data.get('possession', {}).get('away', 'N/A')}%
            Shots (Home/Away): {live_match_data.get('shots', {}).get('home', 'N/A')} / {live_match_data.get('shots', {}).get('away', 'N/A')}
            Dangerous Attacks (Home/Away): {live_match_data.get('dangerous_attacks', {}).get('home', 'N/A')} / {live_match_data.get('dangerous_attacks', {}).get('away', 'N/A')}
            Corners (Home/Away): {live_match_data.get('corners', {}).get('home', 'N/A')} / {live_match_data.get('corners', {}).get('away', 'N/A')}
            Yellow Cards (Home/Away): {live_match_data.get('yellow_cards', {}).get('home', 'N/A')} / {live_match_data.get('yellow_cards', {}).get('away', 'N/A')}
            Red Cards (Home/Away): {live_match_data.get('red_cards', {}).get('home', 'N/A')} / {live_match_data.get('red_cards', {}).get('away', 'N/A')}
            """

        prompt = f"""
        Analyze this ACTIVE betting slip with live match data:

        Match: {bet_data.get('match_name', 'Unknown')}
        Your Bet: {bet_data.get('bet_type', 'Unknown')} on {bet_data.get('match_name', 'Unknown')}
        Original Odds: {bet_data.get('odds', 0)}
        Stake: {bet_data.get('stake', 0)}
        Potential Win: {bet_data.get('potential_win', 'N/A')}
        Time Left: {bet_data.get('time_left', 'N/A')}

        {live_info}

        Based on the live data, evaluate:
        1. Current momentum: Which team is currently dominating based on live stats?
        2. Risk Assessment: Is your bet still favorable given the current score and match state?
        3. Cash-out Opportunity: Would you recommend cashing out now if available?
        4. Updated Win Probability: Adjust the win probability based on live data
        5. Recommendation: Should the user stay in the bet or consider cashing out?

        Respond in JSON format with the following structure:
        {{
          "updated_win_probability": float,
          "current_momentum": string,
          "risk_assessment": string,
          "cashout_recommendation": string,
          "stay_in_recommendation": string,
          "confidence_in_prediction": string
        }}
        """

        try:
            response = openai.chat.completions.create(
                model=os.getenv("QWEN_MODEL", "gpt-4o"),
                messages=[
                    {"role": "system", "content": "You are an expert sports analyst providing real-time analysis of active bets. Focus on objective assessment based on live data without encouraging gambling. Your recommendations should be data-driven and responsible."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600,
                response_format={"type": "json_object"}
            )

            # Parse the response
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in live AI analysis: {str(e)}")
            # Return a default response in case of error
            return {
                "updated_win_probability": 50.0,
                "current_momentum": "Unable to assess with current data",
                "risk_assessment": "Insufficient live data for accurate assessment",
                "cashout_recommendation": "Not enough information to recommend cashout",
                "stay_in_recommendation": "Continue monitoring the match",
                "confidence_in_prediction": "Low"
            }

    def batch_analyze_bets(self, bets_list):
        """
        Analyze multiple bets at once
        """
        results = []
        for bet in bets_list:
            analysis = self.analyze_bet_slip(bet)
            results.append({
                "bet_data": bet,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            })
        return results

    def generate_summary_report(self, analyzed_bets):
        """
        Generate a summary report of all analyzed bets
        """
        if not analyzed_bets:
            return {
                "total_bets": 0,
                "total_staked": 0,
                "total_potential_wins": 0,
                "average_win_probability": 0,
                "high_risk_count": 0,
                "recommendations_summary": []
            }

        total_staked = sum(bet['bet_data'].get('stake', 0) for bet in analyzed_bets)
        total_potential = sum(bet['bet_data'].get('potential_win', 0) for bet in analyzed_bets)
        avg_win_prob = sum(bet['analysis'].get('win_probability', 0) for bet in analyzed_bets) / len(analyzed_bets)
        high_risk_count = sum(1 for bet in analyzed_bets if bet['analysis'].get('risk_level') == 'High')

        recommendations = [bet['analysis'].get('ai_suggestion', '') for bet in analyzed_bets]

        return {
            "total_bets": len(analyzed_bets),
            "total_staked": round(total_staked, 2),
            "total_potential_wins": round(total_potential, 2),
            "average_win_probability": round(avg_win_prob, 2),
            "high_risk_count": high_risk_count,
            "recommendations_summary": recommendations
        }