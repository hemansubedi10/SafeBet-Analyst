from ai_analyzer.upcoming_predictor import UpcomingEventPredictor
from utils.data_utils import load_mock_match_data

predictor = UpcomingEventPredictor()

print('Testing 2-day match filtering...')
matches = predictor.get_upcoming_matches()
print(f'Found {len(matches)} matches in next 2 days:')
for match in matches:
    print(f'  {match["home_team"]} vs {match["away_team"]} - {match["date"]}')

print()
print('Testing best 2+ predictions...')
best_2plus = predictor.get_2plus_best_predictions(top_n=3)
print(f'Found {len(best_2plus)} best 2+ predictions:')
for i, pred in enumerate(best_2plus[:2]):
    match_result = pred['betting_markets']['MatchResult']
    max_result = max(match_result, key=match_result.get)
    print(f'  {i+1}. {pred["match"]}: {max_result} at {match_result[max_result]}%')

print()
print('Testing best 5+ predictions...')
best_5plus = predictor.get_5plus_best_predictions(top_n=3)
print(f'Found {len(best_5plus)} best 5+ predictions:')
for i, pred in enumerate(best_5plus[:2]):
    match_result = pred['betting_markets']['MatchResult']
    max_result = max(match_result, key=match_result.get)
    print(f'  {i+1}. {pred["match"]}: {max_result} at {match_result[max_result]}%')