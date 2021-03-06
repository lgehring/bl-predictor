"""
This file is used for testing models in a variety of cases
"""
import pytest

from bl_predictor import crawler
from bl_predictor import models
from bl_predictor import prediction_evaluation

# import pandas as pd

test_crawler_data = crawler.fetch_data([1, 2010], [1, 2015])


# Models testsuite
@pytest.mark.parametrize(
    "model,trainset,home_team,guest_team,expected",
    [  # FrequencyModel tests
        ("FrequencyModel", test_crawler_data, 'Hamburger SV', 'Hannover 96',
         'Draw: 20.0%'),
        ("FrequencyModel", test_crawler_data, 'Hannover 96', 'Hamburger SV',
         'Draw: 20.0%'),
        ("FrequencyModel", test_crawler_data, 'VfB Stuttgart',
         'FC Bayern München', 'FC Bayern München: 100.0%'),
        ("FrequencyModel", test_crawler_data, 'FC Schalke 04', 'Werder Bremen',
         'FC Schalke 04: 72.7%'),
        # PoissonModel tests
        ("PoissonModel", test_crawler_data, 'Hamburger SV', 'Hannover 96',
         'Hamburger SV: 38.2%'),
        ("PoissonModel", test_crawler_data, 'Hannover 96', 'Hamburger SV',
         'Hannover 96: 53.3%'),
        ("PoissonModel", test_crawler_data, 'BV Borussia Dortmund 09',
         'Hertha BSC', 'BV Borussia Dortmund 09: 77.1%'),
        ("PoissonModel", test_crawler_data, 'FC Schalke 04', 'Werder Bremen',
         'FC Schalke 04: 64.0%'),
    ])
def test_predict_winner(model, trainset, home_team, guest_team, expected):
    trained_model = getattr(models, model)(trainset)
    winner = trained_model.predict_winner
    assert winner(home_team, guest_team) == expected


# WholeDataFrequencies testsuite
@pytest.mark.parametrize(
    "trainset,"
    "expected_home_team_wins,"
    "expected_guest_team_wins,"
    "expected_draws,"
    "expected_home_team_avg_goals,"
    "expected_guest_team_avg_goals",
    [  # WholeDataFrequencies tests
        (test_crawler_data, 704, 465, 370, 1.6426250812215724,
         1.2735542560103963)
    ])
def test_stats(trainset,
               expected_home_team_wins,
               expected_guest_team_wins,
               expected_draws,
               expected_home_team_avg_goals,
               expected_guest_team_avg_goals):
    trained_model = prediction_evaluation.WholeDataFrequencies(trainset)
    assert trained_model.home_team_wins == expected_home_team_wins
    assert trained_model.guest_team_wins == expected_guest_team_wins
    assert trained_model.draws == expected_draws
    assert trained_model.home_team_avg_goals == expected_home_team_avg_goals
    assert trained_model.guest_team_avg_goals == expected_guest_team_avg_goals
