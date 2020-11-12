"""
This file is used for testing models in a variety of cases
"""

import pandas as pd
from teamproject import models

norm_train = pd.DataFrame([
    ['A', 0, 3, 'B'],
    ['A', 0, 1, 'C'],
    ['B', 4, 0, 'A'],
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
    ['A', 1, 4, 'C'],
    ['A', 0, 3, 'C'],
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

too_many_columns = pd.DataFrame([
    ['A', 2, 7, 0, 'C'],
    ['B', 0, 7, 3, 'C'],
    ['A', 1, 7, 3, 'B'],
], columns=[
    'home_team', 'home_score', 'random_score', 'guest_score', 'guest_team'])

missing_column = pd.DataFrame([
    ['A', 0, 1],
    ['B', 0, 0],
    ['A', 3, 1],
], columns=['home_team', 'home_score', 'guest_score'])


def test_norm():
    model = models.FrequencyModel(norm_train)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') == 'B'
    assert winner('C', 'A') == winner('A', 'C') == 'C'
    assert winner('B', 'C') == winner('C', 'B') is None
    assert winner('A', 'D') == winner('D', 'A') is None
    assert winner('A', 'E') == winner('E', 'A') is None


def test_nonsense():
    model = models.FrequencyModel(nonsense_matches)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') == 'A'
    assert winner('C', 'A') == winner('A', 'C') is None
    assert winner('B', 'C') == winner('C', 'B') == 'C'


def test_empty():
    model = models.FrequencyModel(empty_data)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') is None
    assert winner('C', 'A') == winner('A', 'C') is None
    assert winner('B', 'C') == winner('C', 'B') is None


def test_no_matchups():
    model = models.FrequencyModel(no_matchups)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') is None


def test_too_many_columns():
    model = models.FrequencyModel(too_many_columns)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') == 'B'
    assert winner('C', 'A') == winner('A', 'C') == 'A'
    assert winner('B', 'C') == winner('C', 'B') == 'C'


def test_missing_column():
    model = models.FrequencyModel(missing_column)
    winner = model.predict_winner
    assert winner('A', 'B') == winner('B', 'A') is None
    assert winner('C', 'A') == winner('A', 'C') is None
    assert winner('B', 'C') == winner('C', 'B') is None
