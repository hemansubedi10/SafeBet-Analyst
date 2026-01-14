from utils.live_score_updater import live_updater
import time

print('Testing live score updater...')
live_updater.start_auto_update()
time.sleep(2)  # Allow time for initial update
print('Live matches:', len(live_updater.live_matches))
for match_id, match_data in list(live_updater.live_matches.items())[:2]:  # Show first 2 matches
    print(f"  {match_data['home_team']} vs {match_data['away_team']}: {match_data['home_score']}-{match_data['away_score']} ({match_data['minute']}')")
live_updater.stop_auto_update()
print('Live score updater test completed.')