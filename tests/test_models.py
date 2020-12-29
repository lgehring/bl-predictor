"""
This file is used for testing models in a variety of cases
"""
import pandas as pd
import pytest

from teamproject import models

norm_train = pd.DataFrame([
    ['A', 0, 3, 'B'],
    ['A', 1, 1, 'C'],
    ['C', 4, 0, 'A'],
    ['B', 0, 3, 'C'],
    ['B', 1, 1, 'C'],
    ['A', 4, 0, 'B'],
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

nonsense_matches = pd.DataFrame([
    ['C', 0, -1, 'B'],
    ['A', 0, 1000, 'A'],
    ['A', 4.0, 0, 'B'],
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

empty_data = pd.DataFrame([
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

no_matchups = pd.DataFrame([
    ['A', 0, 0, 'C'],
    ['C', 1, 4, 'A'],
    ['B', 0, 3, 'C'],
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

too_many_columns = pd.DataFrame([
    ['A', 0, 0, 3, 'B'],
    ['A', 1, 1, 3, 'C'],
    ['C', 4, 10, 3, 'A'],
    ['B', 0, -1, 3, 'C'],
    ['B', 1, 100, 3, 'C'],
    ['A', 4, (1 / 3), 3, 'B'],
], columns=[
    'home_team', 'home_score', 'random_score', 'guest_score', 'guest_team'])

missing_column = pd.DataFrame([
    [0, 'A'],
    [0, 'B'],
    [3, 'A'],
], columns=['home_score', 'guest_team'])


# Models testsuite
@pytest.mark.parametrize(
    "model,trainset,home_team,guest_team,expected",
    [  # FrequencyModel tests
        ("FrequencyModel", norm_train, 'A', 'B', 'Draw'),
        ("FrequencyModel", norm_train, 'B', 'A', 'Draw'),
        ("FrequencyModel", norm_train, 'C', 'A', 'C'),
        ("FrequencyModel", norm_train, 'C', 'B', 'C'),
        ("FrequencyModel", norm_train, 'A', 'D', 'Not enough data'),
        ("FrequencyModel", nonsense_matches, 'B', 'C', 'C'),
        ("FrequencyModel", nonsense_matches, 'C', 'B', 'C'),
        ("FrequencyModel", nonsense_matches, 'C', 'A', 'Not enough data'),
        ("FrequencyModel", empty_data, 'C', 'A', 'Not enough data'),
        ("FrequencyModel", empty_data, 'B', 'C', 'Not enough data'),
        ("FrequencyModel", no_matchups, 'A', 'B', 'Not enough data'),
        ("FrequencyModel", empty_data, 'C', 'A', 'Not enough data'),
        ("FrequencyModel", too_many_columns, 'A', 'B', 'Draw'),
        ("FrequencyModel", missing_column, 'C', 'B', 'Prediction failed. '
                                                     'Check training '
                                                     'DataFrame for errors'),
        # PoissonModel tests
        ("PoissonModel", norm_train, 'A', 'B', 'A: 57.6%'),
        ("PoissonModel", norm_train, 'B', 'A', 'B: 80.3%'),
        ("PoissonModel", norm_train, 'A', 'C', 'C: 66.4%'),
        ("PoissonModel", norm_train, 'C', 'A', 'C: 95.9%'),
        ("PoissonModel", norm_train, 'B', 'C', 'C: 64.0%'),
        ("PoissonModel", norm_train, 'C', 'B', 'C: 96.2%'),
        ("PoissonModel", no_matchups, 'A', 'B', 'A: 72.3%'),
        ("PoissonModel", too_many_columns, 'A', 'B', 'B: 51.7%'),
        ("PoissonModel", nonsense_matches, 'B', 'C', 'Prediction failed. '
                                                     'Check training '
                                                     'DataFrame for errors'),
        ("PoissonModel", empty_data, 'C', 'A', 'Prediction failed. Check '
                                               'training DataFrame for '
                                               'errors'),
        ("PoissonModel", empty_data, 'C', 'A', 'Prediction failed. Check '
                                               'training DataFrame for '
                                               'errors'),
        ("PoissonModel", missing_column, 'C', 'B', 'Prediction failed. Check '
                                                   'training DataFrame for '
                                                   'errors'),
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
        (norm_train, 2, 2, 2, 5 / 3, 4 / 3),
        (nonsense_matches, 2, 1, 0, 4 / 3, 333),
        (empty_data, 0, 0, 0, None, None),
        (no_matchups, 0, 2, 1, 1 / 3, 7 / 3),
        (too_many_columns, 2, 4, 0, 10 / 6, 18 / 6),
        (missing_column, 0, 0, 0, None, None),
    ])
def test_stats(trainset,
               expected_home_team_wins,
               expected_guest_team_wins,
               expected_draws,
               expected_home_team_avg_goals,
               expected_guest_team_avg_goals):
    trained_model = models.WholeDataFrequencies(trainset)
    assert trained_model.home_team_wins == expected_home_team_wins
    assert trained_model.guest_team_wins == expected_guest_team_wins
    assert trained_model.draws == expected_draws
    assert trained_model.home_team_avg_goals == expected_home_team_avg_goals
    assert trained_model.guest_team_avg_goals == expected_guest_team_avg_goals
