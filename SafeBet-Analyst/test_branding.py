from utils.data_utils import load_mock_match_data
from datetime import datetime

matches = load_mock_match_data()
print('Loaded', len(matches), 'matches with accurate dates:')
for i, match in enumerate(matches[:3]):
    print(f'{i+1}. {match["home_team"]} vs {match["away_team"]} - {match["date"]} ({match["league"]})')