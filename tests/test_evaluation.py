"""
This file is used for testing model evaluators in a variety of cases
"""
import pandas as pd
import pytest

from bl_predictor import crawler
from bl_predictor import prediction_evaluation

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

draw_train = pd.DataFrame([
    ['B', 1, 1, 'A'],
    ['B', 1, 1, 'A'],
    ['A', 3, 3, 'B'],
    ['A', 2, 2, 'B'],
], columns=[
    'home_team', 'home_score', 'guest_score', 'guest_team'])

test_crawler_data = crawler.fetch_data([1, 2018], [34, 2019])

FMOutput = """\x1b[4m\x1b[1m\x1b[36mEvaluation Results\x1b[0m
Model: FrequencyModel
Accuracy (proportion of correct testset predictions): \x1b[92m0.0%\x1b[0m
F1-score (mean of the weighted average of precision and recall per class): \x1b[92m0.0%\x1b[0m
Size of: Trainset: 4 (66.7%)
         Testset:  2   (33.3%)

\x1b[93mPerformance per class\x1b[0m
              precision    recall  f1-score   support

        draw      0.000     0.000     0.000       1.0
  guest_team      0.000     0.000     0.000       0.0
   home_team      0.000     0.000     0.000       1.0

    accuracy                          0.000       2.0
   macro avg      0.000     0.000     0.000       2.0
weighted avg      0.000     0.000     0.000       2.0

"""

PMOutput = """\x1b[4m\x1b[1m\x1b[36mEvaluation Results\x1b[0m
Model: PoissonModel
Accuracy (proportion of correct testset predictions): \x1b[92m0.0%\x1b[0m
F1-score (mean of the weighted average of precision and recall per class): \x1b[92m0.0%\x1b[0m
Size of: Trainset: 4 (66.7%)
         Testset:  2   (33.3%)

\x1b[93mPerformance per class\x1b[0m
              precision    recall  f1-score   support

        draw      0.000     0.000     0.000       1.0
  guest_team      0.000     0.000     0.000       0.0
   home_team      0.000     0.000     0.000       1.0

    accuracy                          0.000       2.0
   macro avg      0.000     0.000     0.000       2.0
weighted avg      0.000     0.000     0.000       2.0

\x1b[93mTeam Ranking\x1b[0m
The given coefficients are an unaltered result of the PoissonModel training
and do NOT represent actual wins or true rankings

|    |   home_coef | hometeam_ranking   | guestteam_ranking   |   guest_coef |
|---:|------------:|:-------------------|:--------------------|-------------:|
|  1 |      1.5166 | C                  | C                   |      -1.5166 |
|  2 |      1.4904 | B                  | B                   |      -0.0262 |
"""

BPMOutput = """\x1b[4m\x1b[1m\x1b[36mEvaluation Results\x1b[0m
Model: BettingPoissonModel
Accuracy (proportion of correct testset predictions): \x1b[92m0.0%\x1b[0m
F1-score (mean of the weighted average of precision and recall per class): \x1b[92m0.0%\x1b[0m
Size of: Trainset: 4 (66.7%)
         Testset:  2   (33.3%)

\x1b[93mPerformance per class\x1b[0m
              precision    recall  f1-score   support

        draw      0.000     0.000     0.000       1.0
  guest_team      0.000     0.000     0.000       0.0
   home_team      0.000     0.000     0.000       1.0

    accuracy                          0.000       2.0
   macro avg      0.000     0.000     0.000       2.0
weighted avg      0.000     0.000     0.000       2.0

\x1b[93mTeam Ranking\x1b[0m
The given coefficients are an unaltered result of the PoissonModel training
and do NOT represent actual wins or true rankings

|    |   home_coef | hometeam_ranking   | guestteam_ranking   |   guest_coef |
|---:|------------:|:-------------------|:--------------------|-------------:|
|  1 |      1.5166 | C                  | C                   |      -1.5166 |
|  2 |      1.4904 | B                  | B                   |      -0.0262 |
"""


# ModelEvaluator testsuite
@pytest.mark.parametrize(
    "modelname,trainset,testset_size, result",
    [("FrequencyModel", norm_train, 2, FMOutput),
     ("PoissonModel", norm_train, 2, PMOutput),
     ("BettingPoissonModel", norm_train, 2, BPMOutput),
     ])
def test_evaluator(modelname, trainset, testset_size, result, capfd):
    prediction_evaluation.ModelEvaluator(modelname,
                                         trainset,
                                         testset_size).print_results()
    out, err = capfd.readouterr()
    assert out == result


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
        (too_many_columns, 2, 4, 0, 10 / 6, 18 / 6),
        (missing_column, 0, 0, 0, None, None)
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
