"""
SafeBet Analyst - Utility Functions
Helper functions for data processing and API interactions
"""

import json
import requests
from datetime import datetime, timedelta
import random


def load_mock_match_data():
    """
    Load mock match data for demonstration purposes with accurate upcoming fixtures (2 days only)
    """
    # Generate realistic upcoming match dates (today + 1-2 days only)
    today = datetime.now()
    return [
        {
            "match_id": "match_001",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league": "Premier League",
            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 1, "away_wins": 3, "draws": 1},
            "recent_form": {"home": [1, 0, 3, 1, 3], "away": [3, 3, 3, 1, 3]},  # W=3, D=1, L=0
            "key_players_home": ["Bruno Fernandes", "Rashford", "Casemiro"],
            "key_players_away": ["Salah", "van Dijk", "Alisson"],
            "venue": "Old Trafford"
        },
        {
            "match_id": "match_002",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "league": "La Liga",
            "date": (today + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 2, "away_wins": 2, "draws": 1},
            "recent_form": {"home": [3, 1, 3, 3, 0], "away": [3, 3, 1, 3, 3]},
            "key_players_home": ["Bellingham", "Vinicius Jr.", "Courtois"],
            "key_players_away": ["Lewandowski", "Pedri", "Ter Stegen"],
            "venue": "Santiago Bernabeu"
        },
        {
            "match_id": "match_003",
            "home_team": "Bayern Munich",
            "away_team": "Borussia Dortmund",
            "league": "Bundesliga",
            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 3, "away_wins": 1, "draws": 1},
            "recent_form": {"home": [3, 3, 3, 1, 3], "away": [1, 3, 0, 3, 1]},
            "key_players_home": ["Kane", "Musiala", "Kimmich"],
            "key_players_away": ["Haaland", "Reus", "Hummels"],
            "venue": "Allianz Arena"
        },
        {
            "match_id": "match_004",
            "home_team": "PSG",
            "away_team": "Marseille",
            "league": "Ligue 1",
            "date": (today + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 4, "away_wins": 0, "draws": 1},
            "recent_form": {"home": [3, 3, 3, 3, 3], "away": [1, 0, 3, 1, 1]},
            "key_players_home": ["Mbappe", "Neymar", "Verratti"],
            "key_players_away": ["Payet", "Mitrovic", "Lopez"],
            "venue": "Parc des Princes"
        },
        {
            "match_id": "match_005",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league": "Premier League",
            "date": (today + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 3, "away_wins": 1, "draws": 1},
            "recent_form": {"home": [3, 3, 3, 1, 3], "away": [1, 0, 3, 1, 0]},
            "key_players_home": ["Saka", "Martinelli", "Ramsdale"],
            "key_players_away": ["Sterling", "Enzo", "Cucurella"],
            "venue": "Emirates Stadium"
        },
        {
            "match_id": "match_006",
            "home_team": "Juventus",
            "away_team": "AC Milan",
            "league": "Serie A",
            "date": (today + timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "h2h_last_5": {"home_wins": 2, "away_wins": 2, "draws": 1},
            "recent_form": {"home": [3, 1, 1, 3, 0], "away": [3, 3, 1, 3, 1]},
            "key_players_home": ["Vlahovic", "Chiesa", "Szczesny"],
            "key_players_away": ["Leao", "Giroud", "Maignan"],
            "venue": "Allianz Stadium"
        }
    ]


def load_prediction_history():
    """
    Load prediction history for tracking accuracy
    """
    # This would normally load from a database or file
    # For demo, returning mock history data
    today = datetime.now()
    return [
        {
            "prediction_id": "pred_001",
            "match": "Manchester City vs Tottenham",
            "predicted_outcome": "Win",
            "actual_outcome": "Win",  # This means prediction was correct
            "confidence": 85,
            "vip_section": "2+",  # 2+ or 5+
            "predicted_at": (today - timedelta(days=1)).isoformat(),
            "actual_score": "3-1",
            "was_correct": True
        },
        {
            "prediction_id": "pred_002",
            "match": "Real Madrid vs Atletico",
            "predicted_outcome": "Draw",
            "actual_outcome": "Win",  # This means prediction was incorrect
            "confidence": 70,
            "vip_section": "5+",
            "predicted_at": (today - timedelta(days=2)).isoformat(),
            "actual_score": "2-1",
            "was_correct": False
        },
        {
            "prediction_id": "pred_003",
            "match": "Bayern Munich vs Dortmund",
            "predicted_outcome": "Win",
            "actual_outcome": "Win",  # This means prediction was correct
            "confidence": 92,
            "vip_section": "2+",
            "predicted_at": (today - timedelta(days=3)).isoformat(),
            "actual_score": "4-0",
            "was_correct": True
        },
        {
            "prediction_id": "pred_004",
            "match": "PSG vs Lyon",
            "predicted_outcome": "Win",
            "actual_outcome": "Loss",  # This means prediction was incorrect
            "confidence": 78,
            "vip_section": "5+",
            "predicted_at": (today - timedelta(days=4)).isoformat(),
            "actual_score": "1-2",
            "was_correct": False
        }
    ]


def simulate_live_match_data(match_id):
    """
    Simulate live match data for a given match
    """
    # Generate random live stats for demo purposes
    return {
        "match_id": match_id,
        "minute": random.randint(45, 90),
        "score": f"{random.randint(0, 3)}-{random.randint(0, 3)}",
        "possession": {
            "home": random.randint(40, 65),
            "away": 100 - random.randint(40, 65)
        },
        "shots": {
            "home": random.randint(5, 15),
            "away": random.randint(5, 15)
        },
        "dangerous_attacks": {
            "home": random.randint(5, 20),
            "away": random.randint(5, 20)
        },
        "corners": {
            "home": random.randint(2, 8),
            "away": random.randint(2, 8)
        },
        "yellow_cards": {
            "home": random.randint(0, 3),
            "away": random.randint(0, 3)
        },
        "red_cards": {
            "home": random.randint(0, 1),
            "away": random.randint(0, 1)
        },
        "lineups": {
            "home": ["Player1", "Player2", "Player3", "Player4", "Player5", 
                     "Player6", "Player7", "Player8", "Player9", "Player10", "Player11"],
            "away": ["PlayerA", "PlayerB", "PlayerC", "PlayerD", "PlayerE", 
                     "PlayerF", "PlayerG", "PlayerH", "PlayerI", "PlayerJ", "PlayerK"]
        }
    }


def calculate_momentum_factor(live_data):
    """
    Calculate momentum based on live match statistics
    """
    home_dangerous_attacks = live_data.get('dangerous_attacks', {}).get('home', 0)
    away_dangerous_attacks = live_data.get('dangerous_attacks', {}).get('away', 0)
    
    total_dangerous_attacks = home_dangerous_attacks + away_dangerous_attacks
    
    if total_dangerous_attacks == 0:
        return {"home": 50, "away": 50}
    
    home_momentum = (home_dangerous_attacks / total_dangerous_attacks) * 100
    away_momentum = (away_dangerous_attacks / total_dangerous_attacks) * 100
    
    return {
        "home": round(home_momentum, 1),
        "away": round(away_momentum, 1)
    }


def check_player_availability(team_lineup, key_players):
    """
    Check if key players are in the starting lineup
    """
    available_players = []
    missing_players = []
    
    for player in key_players:
        if player in team_lineup:
            available_players.append(player)
        else:
            missing_players.append(player)
    
    return {
        "available": available_players,
        "missing": missing_players,
        "availability_rate": len(available_players) / len(key_players) if key_players else 0
    }


def format_odds(probability):
    """
    Convert probability to decimal odds
    """
    if probability <= 0 or probability >= 1:
        return 0.0
    return round(1 / probability, 2)


def calculate_expected_value(odds, probability):
    """
    Calculate expected value of a bet
    """
    if not odds or not probability:
        return 0.0
    
    probability_decimal = probability / 100
    ev = (odds * probability_decimal) - (1 - probability_decimal)
    return round(ev, 3)