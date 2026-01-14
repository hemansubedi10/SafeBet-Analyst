# Test the enhanced football analysis features
from ai_analyzer.upcoming_predictor import UpcomingEventPredictor
import json

predictor = UpcomingEventPredictor()
matches = predictor.get_upcoming_matches()

if matches:
    result = predictor.get_full_analysis_json(matches[0])
    print('Sample Analysis:')
    print(json.dumps(result, indent=2))
else:
    print("No matches found")