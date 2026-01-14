print('Testing application components...')
from ai_analyzer.upcoming_predictor import UpcomingEventPredictor
from utils.data_utils import load_mock_match_data, load_prediction_history
from utils.live_score_updater import live_updater

predictor = UpcomingEventPredictor()
matches = predictor.get_upcoming_matches()
print(f'[OK] Loaded {len(matches)} matches for next 2 days')

history = load_prediction_history()
print(f'[OK] Loaded {len(history)} prediction history records')

print('[OK] All components loaded successfully!')
print('Application is ready for Streamlit Sharing deployment.')