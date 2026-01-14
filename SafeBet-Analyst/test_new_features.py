from ai_analyzer.upcoming_predictor import UpcomingEventPredictor
predictor = UpcomingEventPredictor()

print('Testing 2+ odds predictions:')
two_plus = predictor.get_2plus_odds_predictions()
print(f'Found {len(two_plus)} matches with 2+ odds')

print('\nTesting 5+ odds predictions:')
five_plus = predictor.get_5plus_odds_predictions()
print(f'Found {len(five_plus)} matches with 5+ odds')

print('\nTesting high accuracy predictions (90%+):')
high_acc = predictor.get_high_accuracy_predictions()
print(f'Found {len(high_acc)} high accuracy predictions')

print('\nTesting slip format for 2+ odds:')
slip_format = predictor.get_slip_format_predictions(odd_threshold=2.0)
for i, slip in enumerate(slip_format[:2]):
    print(f'Slip {i+1}: {slip["match"]} - Recommended: {slip["recommended_bet"]} at {slip["implied_odd"]} odds')