"""
SafeBet Analyst - Upcoming Event Predictor
Module for predicting outcomes of upcoming events based on historical data
Enhanced with professional football analysis features
"""

from utils.data_utils import load_mock_match_data, simulate_live_match_data, calculate_momentum_factor, check_player_availability
import random
from datetime import datetime, timedelta


class UpcomingEventPredictor:
    def __init__(self):
        self.matches_data = load_mock_match_data()

    def get_upcoming_matches(self):
        """
        Get upcoming matches for prediction (limited to 2 days)
        """
        from datetime import datetime, timedelta
        from utils.data_utils import load_mock_match_data

        # Reload data to get fresh 2-day matches
        all_matches = load_mock_match_data()
        now = datetime.now()
        two_days_later = now + timedelta(days=2)

        # Filter matches to only include those in the next 2 days
        two_day_matches = []
        for match in all_matches:
            match_date = datetime.strptime(match['date'], "%Y-%m-%d %H:%M")
            if now <= match_date <= two_days_later:
                two_day_matches.append(match)

        # Update our internal matches data
        self.matches_data = two_day_matches
        return self.matches_data

    def predict_match_outcome(self, match_data):
        """
        Predict outcome of a single match based on various factors
        Enhanced to provide all possible betting outcomes with probabilities
        """
        # Calculate H2H advantage
        h2h_advantage = self._calculate_h2h_advantage(match_data['h2h_last_5'])

        # Calculate recent form advantage
        form_advantage = self._calculate_form_advantage(match_data['recent_form'])

        # Calculate venue advantage
        venue_advantage = self._calculate_venue_advantage(match_data['venue'])

        # Calculate key player availability impact
        player_impact = self._calculate_player_impact(match_data)

        # Calculate injury/news impact
        news_impact = self._calculate_news_impact(match_data)

        # Combine all factors to determine prediction
        total_advantage = {
            'home': h2h_advantage['home'] + form_advantage['home'] + venue_advantage['home'] + player_impact['home'] + news_impact['home'],
            'away': h2h_advantage['away'] + form_advantage['away'] + venue_advantage['away'] + player_impact['away'] + news_impact['away']
        }

        # Determine winner based on total advantage
        home_advantage = total_advantage['home'] - total_advantage['away']

        # Calculate probabilities with more realistic distribution
        # Base probability is 1/3 for each outcome, adjusted by advantage
        base_prob = 0.33
        max_advantage = 20  # Maximum possible advantage from all factors

        # Calculate adjusted probabilities
        home_prob = base_prob + (home_advantage / max_advantage) * 0.34  # Max adjustment of 34%
        away_prob = base_prob - (home_advantage / max_advantage) * 0.34
        draw_prob = 1 - home_prob - away_prob

        # Ensure probabilities are within bounds
        home_prob = max(0.05, min(0.95, home_prob))
        away_prob = max(0.05, min(0.95, away_prob))
        draw_prob = max(0.05, min(0.95, draw_prob))

        # Normalize to ensure they sum to 1
        total_prob = home_prob + away_prob + draw_prob
        home_prob /= total_prob
        away_prob /= total_prob
        draw_prob /= total_prob

        # Determine most likely outcome
        outcomes = ['home_win', 'draw', 'away_win']
        probs = [home_prob, draw_prob, away_prob]
        predicted_outcome_idx = probs.index(max(probs))
        predicted_outcome = outcomes[predicted_outcome_idx]

        # Calculate confidence based on the difference between the highest and second-highest probability
        sorted_probs = sorted(probs, reverse=True)
        confidence = round((sorted_probs[0] - sorted_probs[1]) * 100 + 50, 1)  # Scale to 50-100 range

        # Generate comprehensive betting market analysis
        betting_markets = self._generate_betting_markets(match_data, home_prob, away_prob, draw_prob)

        return {
            'match': f"{match_data['home_team']} vs {match_data['away_team']}",
            'predicted_outcome': self._format_outcome(predicted_outcome, match_data['home_team'], match_data['away_team']),
            'confidence': min(99.9, confidence),  # Cap at 99.9 to avoid 100% certainty
            'probabilities': {
                'home_win': round(home_prob * 100, 1),
                'draw': round(draw_prob * 100, 1),
                'away_win': round(away_prob * 100, 1)
            },
            'betting_markets': betting_markets,
            'key_factors': self._generate_key_factors(match_data, total_advantage),
            'h2h_stats': self._format_h2h_stats(match_data['h2h_last_5'], match_data['home_team'], match_data['away_team']),
            'match_date': match_data['date']
        }

    def _generate_betting_markets(self, match_data, home_prob, away_prob, draw_prob):
        """
        Generate comprehensive betting market analysis for the match
        """
        # Calculate expected goals based on team strengths
        home_strength = home_prob / (home_prob + away_prob + draw_prob)
        away_strength = away_prob / (home_prob + away_prob + draw_prob)

        # Expected total goals based on team strengths and historical averages
        expected_total_goals = 2.5 + (home_strength + away_strength - 1) * 0.5

        # Generate all betting markets
        markets = {
            "MatchResult": {
                "Win": round(home_prob * 100, 1),  # Home win
                "Draw": round(draw_prob * 100, 1),
                "Lose": round(away_prob * 100, 1)  # Away win
            },
            "OverUnder": self._calculate_over_under_markets(expected_total_goals),
            "BTTS": self._calculate_btts_market(home_strength, away_strength),
            "DoubleChance": self._calculate_double_chance_markets(home_prob, away_prob, draw_prob),
            "CorrectScores": self._calculate_correct_scores(home_prob, away_prob, draw_prob, expected_total_goals),
            "Confidence": round(min(95, max(60, (home_prob + away_prob + draw_prob) * 30 + 40)), 1),
            "RiskLevel": self._determine_risk_level(home_prob, away_prob, draw_prob),
            "KeyFactors": self._generate_comprehensive_key_factors(match_data, home_prob, away_prob, draw_prob)
        }

        return markets

    def _calculate_over_under_markets(self, expected_goals):
        """
        Calculate Over/Under probabilities for different goal thresholds
        """
        markets = {}

        # Define thresholds to calculate
        thresholds = [0.5, 1.5, 2.5, 3.5]

        for threshold in thresholds:
            # Calculate probability of total goals exceeding threshold
            # Using Poisson distribution approximation
            prob_over = self._poisson_cdf_greater_than(expected_goals, threshold)
            prob_under = 1 - prob_over

            markets[str(threshold)] = {
                "Over": round(prob_over * 100, 1),
                "Under": round(prob_under * 100, 1)
            }

        return markets

    def _poisson_cdf_greater_than(self, mu, k):
        """
        Approximate Poisson CDF for P(X > k)
        """
        # Simple approximation for demonstration
        # In a real implementation, this would use the actual Poisson CDF
        if k < mu:
            # Higher chance of going over if expected goals are higher than threshold
            return min(1.0, 0.3 + (mu - k) * 0.4)
        else:
            # Lower chance of going over if expected goals are lower than threshold
            return max(0.0, 0.7 - (k - mu) * 0.3)

    def _calculate_btts_market(self, home_strength, away_strength):
        """
        Calculate Both Teams to Score probabilities
        """
        # BTTS likelihood depends on both teams' attacking strength
        btts_yes_prob = (home_strength * 0.7 + away_strength * 0.7) * 0.8
        btts_no_prob = 1 - btts_yes_prob

        return {
            "Yes": round(btts_yes_prob * 100, 1),
            "No": round(btts_no_prob * 100, 1)
        }

    def _calculate_double_chance_markets(self, home_prob, away_prob, draw_prob):
        """
        Calculate double chance market probabilities
        """
        return {
            "TeamA/Draw": round((home_prob + draw_prob) * 100, 1),  # Home win or draw
            "TeamB/Draw": round((away_prob + draw_prob) * 100, 1),  # Away win or draw
            "TeamA/TeamB": round((home_prob + away_prob) * 100, 1)  # Home win or away win
        }

    def _calculate_correct_scores(self, home_prob, away_prob, draw_prob, expected_total_goals):
        """
        Calculate probabilities for top 5 most likely correct scores
        """
        # Simplified calculation - in reality, this would use more sophisticated models
        scores = {}

        # Most likely scores based on team strengths and expected goals
        home_goals_exp = expected_total_goals * (home_prob / (home_prob + away_prob + 0.1))
        away_goals_exp = expected_total_goals * (away_prob / (home_prob + away_prob + 0.1))

        # Generate top 5 most likely scores
        possible_scores = [
            (round(home_goals_exp), round(away_goals_exp)),
            (round(home_goals_exp)+1, round(away_goals_exp)),
            (round(home_goals_exp), round(away_goals_exp)+1),
            (round(home_goals_exp)-1, round(away_goals_exp)),
            (round(home_goals_exp), round(away_goals_exp)-1)
        ]

        # Ensure non-negative goals
        possible_scores = [(max(0, h), max(0, a)) for h, a in possible_scores]

        # Assign probabilities (simplified)
        total_score_prob = 0
        for i, (h, a) in enumerate(possible_scores):
            # Calculate probability based on Poisson-like distribution
            score_prob = max(5, 30 - i*5)  # Decreasing probability for less likely scores
            scores[f"{h}-{a}"] = round(score_prob, 1)
            total_score_prob += score_prob

        # Normalize to sum to ~100%
        normalized_scores = {}
        for score, prob in scores.items():
            normalized_scores[score] = round((prob / total_score_prob) * 100, 1)

        # Return top 5 scores
        sorted_scores = dict(sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:5])
        return sorted_scores

    def _determine_risk_level(self, home_prob, away_prob, draw_prob):
        """
        Determine risk level based on probability distribution
        """
        max_prob = max(home_prob, away_prob, draw_prob)

        if max_prob > 0.6:
            return "Low"
        elif max_prob > 0.4:
            return "Medium"
        else:
            return "High"

    def _generate_comprehensive_key_factors(self, match_data, home_prob, away_prob, draw_prob):
        """
        Generate comprehensive key factors for the match analysis
        """
        factors = []

        # H2H factor
        h2h_home = match_data['h2h_last_5']['home_wins']
        h2h_away = match_data['h2h_last_5']['away_wins']
        if h2h_home > h2h_away:
            factors.append(f"{match_data['home_team']} has superior head-to-head record ({h2h_home}-{h2h_away})")
        elif h2h_away > h2h_home:
            factors.append(f"{match_data['away_team']} has superior head-to-head record ({h2h_away}-{h2h_home})")
        else:
            factors.append(f"Teams evenly matched in head-to-head ({h2h_home}-{h2h_away}-{match_data['h2h_last_5']['draws']})")

        # Form factor
        home_form_points = sum([3 if x == 3 else 1 if x == 1 else 0 for x in match_data['recent_form']['home']])
        away_form_points = sum([3 if x == 3 else 1 if x == 1 else 0 for x in match_data['recent_form']['away']])

        if home_form_points > away_form_points:
            factors.append(f"{match_data['home_team']} in better recent form ({home_form_points} vs {away_form_points} points)")
        elif away_form_points > home_form_points:
            factors.append(f"{match_data['away_team']} in better recent form ({away_form_points} vs {home_form_points} points)")
        else:
            factors.append(f"Teams have similar recent form ({home_form_points} vs {away_form_points} points)")

        # Venue factor
        factors.append("Home advantage considered in calculations")

        # Key player availability
        factors.append("Key player availability factored into analysis")

        # Expected goals insight
        expected_home_goals = 1.5 + (home_prob - 0.33) * 2
        expected_away_goals = 1.5 + (away_prob - 0.33) * 2
        factors.append(f"Expected goals: {match_data['home_team']} {expected_home_goals:.1f} - {expected_away_goals:.1f} {match_data['away_team']}")

        # Market insights
        if max(home_prob, away_prob, draw_prob) > 0.5:
            factors.append("Clear favorite identified in match result market")
        else:
            factors.append("Competitive match expected with no clear favorite")

        return factors

    def _calculate_h2h_advantage(self, h2h_data):
        """
        Calculate advantage based on head-to-head record
        """
        home_wins = h2h_data['home_wins']
        away_wins = h2h_data['away_wins']
        draws = h2h_data['draws']

        total_games = home_wins + away_wins + draws

        if total_games == 0:
            return {'home': 0, 'away': 0}

        # Weight recent H2H more heavily if available
        home_ratio = home_wins / total_games
        away_ratio = away_wins / total_games

        # Scale to -10 to 10 range
        home_advantage = (home_ratio - away_ratio) * 10
        away_advantage = (away_ratio - home_ratio) * 10

        return {'home': home_advantage, 'away': away_advantage}

    def _calculate_form_advantage(self, form_data):
        """
        Calculate advantage based on recent form
        """
        home_form = form_data['home']
        away_form = form_data['away']

        # Convert form to points (W=3, D=1, L=0), with more weight to recent games
        weights = [0.15, 0.15, 0.2, 0.25, 0.25]  # More weight to last 3 games

        home_points = sum([points * weights[i] for i, points in enumerate([3 if x == 3 else 1 if x == 1 else 0 for x in home_form])])
        away_points = sum([points * weights[i] for i, points in enumerate([3 if x == 3 else 1 if x == 1 else 0 for x in away_form])])

        # Calculate advantage (scale to -10 to 10)
        max_possible_points = 3 * sum(weights)  # Max points if all wins
        form_diff = home_points - away_points
        scaled_diff = (form_diff / max_possible_points) * 10

        return {
            'home': max(-10, min(10, scaled_diff)),
            'away': max(-10, min(10, -scaled_diff))
        }

    def _calculate_venue_advantage(self, venue):
        """
        Calculate home advantage based on venue
        """
        # Standard home advantage
        return {
            'home': 1.2,  # Home advantage
            'away': -1.2
        }

    def _calculate_player_impact(self, match_data):
        """
        Calculate impact based on key player availability
        """
        # Simulate key player availability (in a real app, this would come from an API)
        home_available = random.randint(1, len(match_data['key_players_home']))
        away_available = random.randint(1, len(match_data['key_players_away']))

        home_rate = home_available / len(match_data['key_players_home'])
        away_rate = away_available / len(match_data['key_players_away'])

        # Scale to -5 to 5 range
        home_impact = (home_rate - away_rate) * 5
        away_impact = (away_rate - home_rate) * 5

        return {
            'home': home_impact,
            'away': away_impact
        }

    def _calculate_news_impact(self, match_data):
        """
        Calculate impact based on recent news (injuries, suspensions, etc.)
        """
        # Simulate news impact (in a real app, this would come from an API)
        # Randomly assign news impact for demo purposes
        home_news_impact = random.uniform(-1.5, 1.5)
        away_news_impact = random.uniform(-1.5, 1.5)

        return {
            'home': home_news_impact,
            'away': away_news_impact
        }

    def _format_outcome(self, outcome, home_team, away_team):
        """
        Format the predicted outcome for display
        """
        if outcome == 'home_win':
            return f"{home_team} to Win"
        elif outcome == 'away_win':
            return f"{away_team} to Win"
        else:
            return "Draw"

    def _generate_key_factors(self, match_data, advantages):
        """
        Generate key factors for the prediction
        """
        factors = []

        # H2H factor
        h2h_home = match_data['h2h_last_5']['home_wins']
        h2h_away = match_data['h2h_last_5']['away_wins']
        if h2h_home > h2h_away:
            factors.append(f"H2H: {match_data['home_team']} leads {h2h_home}-{h2h_away}")
        elif h2h_away > h2h_home:
            factors.append(f"H2H: {match_data['away_team']} leads {h2h_away}-{h2h_home}")
        else:
            factors.append(f"H2H: Even record ({h2h_home}-{h2h_away}-{match_data['h2h_last_5']['draws']})")

        # Form factor
        home_form_points = sum([3 if x == 3 else 1 if x == 1 else 0 for x in match_data['recent_form']['home']])
        away_form_points = sum([3 if x == 3 else 1 if x == 1 else 0 for x in match_data['recent_form']['away']])

        if home_form_points > away_form_points:
            factors.append(f"Form: {match_data['home_team']} in better form ({home_form_points}-{away_form_points})")
        elif away_form_points > home_form_points:
            factors.append(f"Form: {match_data['away_team']} in better form ({away_form_points}-{home_form_points})")
        else:
            factors.append(f"Form: Similar form ({home_form_points}-{away_form_points})")

        # Venue factor
        factors.append("Venue advantage for home team")

        # Player availability factor
        factors.append("Key player availability considered")

        # News/injury factor
        factors.append("Recent news and injuries considered")

        return factors

    def _format_h2h_stats(self, h2h_data, home_team, away_team):
        """
        Format H2H stats for display
        """
        return f"{home_team} won {h2h_data['home_wins']}, {away_team} won {h2h_data['away_wins']}, {h2h_data['draws']} draws in last 5 meetings"

    def predict_top_matches(self, count=3):
        """
        Predict outcomes for top N matches
        """
        matches = self.get_upcoming_matches()

        # Predict for all matches
        predictions = []
        for match in matches:
            pred = self.predict_match_outcome(match)
            predictions.append(pred)

        # Sort by confidence
        predictions.sort(key=lambda x: x['confidence'], reverse=True)

        # Return top N predictions
        return predictions[:count]

    def get_high_confidence_predictions(self, min_confidence=70):
        """
        Get predictions with confidence above a certain threshold
        """
        all_predictions = self.predict_top_matches(count=len(self.matches_data))
        high_confidence = [pred for pred in all_predictions if pred['confidence'] >= min_confidence]

        return high_confidence

    def get_full_analysis_json(self, match_data):
        """
        Return full analysis in the requested JSON format
        """
        prediction = self.predict_match_outcome(match_data)

        # Format as requested in the professional football analyst prompt
        result = {
            "match": prediction['match'],
            "allOutcomes": prediction['betting_markets']
        }

        return result

    def get_high_accuracy_predictions(self, min_confidence=90):
        """
        Get predictions with 90%+ confidence for high accuracy betting
        """
        all_predictions = self.predict_top_matches(count=len(self.matches_data))
        high_accuracy = [pred for pred in all_predictions if pred['confidence'] >= min_confidence]

        return high_accuracy

    def get_betting_slips_by_odd_range(self, min_odd=2.0, max_odd=None):
        """
        Generate betting slips for specific odd ranges (e.g., 2+ odds, 5+ odds)
        """
        all_predictions = self.predict_top_matches(count=len(self.matches_data))
        filtered_predictions = []

        for pred in all_predictions:
            # Calculate implied probability from odds
            # For match result, we'll use the highest probability outcome
            max_prob = max(
                pred['betting_markets']['MatchResult']['Win'],
                pred['betting_markets']['MatchResult']['Draw'],
                pred['betting_markets']['MatchResult']['Lose']
            )

            # Convert probability to decimal odds
            implied_odd = 1 / (max_prob / 100)

            if min_odd <= implied_odd:
                if max_odd is None or implied_odd <= max_odd:
                    # Add the calculated odd to the prediction
                    pred_copy = pred.copy()
                    pred_copy['calculated_odd'] = round(implied_odd, 2)
                    filtered_predictions.append(pred_copy)

        return filtered_predictions

    def get_2plus_odds_predictions(self):
        """
        Get predictions with 2.0+ odds for medium-high probability bets
        """
        return self.get_betting_slips_by_odd_range(min_odd=2.0)

    def get_5plus_odds_predictions(self):
        """
        Get predictions with 5.0+ odds for high-value bets
        """
        return self.get_betting_slips_by_odd_range(min_odd=5.0)

    def get_slip_format_predictions(self, odd_threshold=2.0):
        """
        Format predictions in betting slip format for specific odd thresholds
        """
        predictions = self.get_betting_slips_by_odd_range(min_odd=odd_threshold)

        slip_format = []
        for pred in predictions:
            # Determine the recommended bet based on highest probability
            match_result = pred['betting_markets']['MatchResult']
            max_result = max(match_result, key=match_result.get)

            # Format as betting slip
            slip_entry = {
                "match": pred['match'],
                "recommended_bet": max_result,
                "probability": match_result[max_result],
                "implied_odd": pred['calculated_odd'],
                "confidence": pred['confidence'],
                "risk_level": pred['betting_markets']['RiskLevel'],
                "key_factors": pred['betting_markets']['KeyFactors'][:3]  # Top 3 factors
            }
            slip_format.append(slip_entry)

        return slip_format

    def get_best_probability_predictions(self, odd_threshold=2.0, top_n=5):
        """
        Get predictions with the best winning probability for specific odd thresholds
        """
        predictions = self.get_betting_slips_by_odd_range(min_odd=odd_threshold)

        # Sort by probability of the recommended outcome
        sorted_predictions = []
        for pred in predictions:
            match_result = pred['betting_markets']['MatchResult']
            max_result = max(match_result, key=match_result.get)
            pred_with_prob = pred.copy()
            pred_with_prob['recommended_probability'] = match_result[max_result]
            sorted_predictions.append(pred_with_prob)

        # Sort by recommended probability descending
        sorted_predictions.sort(key=lambda x: x['recommended_probability'], reverse=True)

        # Return top N predictions
        return sorted_predictions[:top_n]

    def get_2plus_best_predictions(self, top_n=5):
        """
        Get best probability predictions for 2+ odds section
        """
        return self.get_best_probability_predictions(odd_threshold=2.0, top_n=top_n)

    def get_5plus_best_predictions(self, top_n=5):
        """
        Get best probability predictions for 5+ odds section
        """
        return self.get_best_probability_predictions(odd_threshold=5.0, top_n=top_n)