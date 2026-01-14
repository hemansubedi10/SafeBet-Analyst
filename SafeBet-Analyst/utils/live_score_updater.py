"""
Live Football Data Integration Module
Handles live scores and game states for SpeedoVIP
"""

import requests
import time
from datetime import datetime, timedelta
import json
from threading import Thread
import schedule
from utils.data_utils import load_mock_match_data


class LiveScoreUpdater:
    def __init__(self):
        self.live_matches = {}
        self.is_running = False
        self.update_interval = 30  # seconds
        self.mock_data = load_mock_match_data()
        
    def get_live_scores_from_api(self):
        """
        Get live scores from a football API
        NOTE: This is a mock implementation since we don't have a real API key
        In production, you would connect to a service like:
        - Football-API (https://www.football-data.org/)
        - SportMonks
        - API-Football
        """
        # This is a mock implementation
        # In a real implementation, you would make API calls to a live football data service
        live_data = {}

        # Only include matches that are happening in the next 2 days
        now = datetime.now()
        two_days_later = now + timedelta(days=2)

        for match in self.mock_data:
            # Parse the match date
            match_date = datetime.strptime(match['date'], "%Y-%m-%d %H:%M")

            # Only include matches within the next 2 days
            if now <= match_date <= two_days_later:
                # Determine if match is live, finished, or upcoming
                if match_date <= now:
                    # Match has started
                    time_since_start = now - match_date
                    minutes_elapsed = min(90, int(time_since_start.total_seconds() / 60))

                    # Simulate live score based on match time
                    home_goals = 0
                    away_goals = 0

                    # Simulate scoring based on team strengths
                    if minutes_elapsed > 0:
                        import random
                        for minute in range(1, minutes_elapsed + 1):
                            # Higher chance of scoring in certain minutes (e.g., 45th, 90th)
                            scoring_chance = random.random()
                            if scoring_chance < 0.025:  # 2.5% chance per minute
                                if random.choice([True, False]):
                                    home_goals += 1
                                else:
                                    away_goals += 1

                    status = "LIVE" if minutes_elapsed < 90 else "FINISHED"
                    minute_display = minutes_elapsed if minutes_elapsed <= 90 else "FT"
                else:
                    # Match is upcoming
                    status = "UPCOMING"
                    minute_display = "VS"
                    home_goals = 0
                    away_goals = 0

                live_data[match['match_id']] = {
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'home_score': home_goals,
                    'away_score': away_goals,
                    'minute': minute_display,
                    'status': status,
                    'league': match['league'],
                    'venue': match['venue'],
                    'match_datetime': match['date'],
                    'last_update': datetime.now().isoformat()
                }

        return live_data
    
    def update_live_data(self):
        """
        Update the live scores and game states
        """
        try:
            new_data = self.get_live_scores_from_api()
            self.live_matches = new_data
            print(f"[{datetime.now()}] Updated live scores for {len(new_data)} matches")
        except Exception as e:
            print(f"Error updating live data: {str(e)}")
    
    def start_auto_update(self):
        """
        Start the automatic update process
        """
        if not self.is_running:
            self.is_running = True
            self.update_live_data()  # Initial update
            
            # Schedule periodic updates
            schedule.every(self.update_interval).seconds.do(self.update_live_data)
            
            # Start scheduler in a separate thread
            def run_scheduler():
                while self.is_running:
                    schedule.run_pending()
                    time.sleep(1)
            
            self.scheduler_thread = Thread(target=run_scheduler, daemon=True)
            self.scheduler_thread.start()
            print(f"Started live score auto-update (every {self.update_interval}s)")
    
    def stop_auto_update(self):
        """
        Stop the automatic update process
        """
        self.is_running = False
        schedule.clear()
        print("Stopped live score auto-update")
    
    def get_match_details(self, match_id):
        """
        Get details for a specific match
        """
        return self.live_matches.get(match_id, {})
    
    def get_all_live_matches(self):
        """
        Get all currently live matches
        """
        return {k: v for k, v in self.live_matches.items() if v['status'] == 'LIVE'}
    
    def get_recent_finished_matches(self):
        """
        Get recently finished matches (finished in last hour)
        """
        one_hour_ago = datetime.now() - timedelta(hours=1)
        return {
            k: v for k, v in self.live_matches.items()
            if v['status'] == 'FINISHED' and
            datetime.fromisoformat(v['last_update']) > one_hour_ago
        }

    def track_prediction_result(self, prediction_id, match_id, predicted_outcome, actual_outcome, confidence, vip_section):
        """
        Track the result of a prediction to update history
        """
        # This would normally save to a database
        # For demo, we'll just store in memory
        if not hasattr(self, 'prediction_history'):
            self.prediction_history = []

        # Determine if prediction was correct
        was_correct = predicted_outcome.lower() == actual_outcome.lower()

        prediction_record = {
            "prediction_id": prediction_id,
            "match_id": match_id,
            "predicted_outcome": predicted_outcome,
            "actual_outcome": actual_outcome,
            "confidence": confidence,
            "vip_section": vip_section,
            "predicted_at": datetime.now().isoformat(),
            "was_correct": was_correct
        }

        self.prediction_history.append(prediction_record)
        return prediction_record

    def get_prediction_history(self, days_back=30):
        """
        Get prediction history for the last N days
        """
        if not hasattr(self, 'prediction_history'):
            self.prediction_history = []

        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_history = []

        for record in self.prediction_history:
            record_date = datetime.fromisoformat(record['predicted_at'])
            if record_date >= cutoff_date:
                recent_history.append(record)

        return recent_history

    def get_vip_prediction_history(self, vip_section, days_back=30):
        """
        Get prediction history for a specific VIP section
        """
        all_history = self.get_prediction_history(days_back)
        return [record for record in all_history if record['vip_section'] == vip_section]


# Global instance for the app
live_updater = LiveScoreUpdater()