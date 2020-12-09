"""
This module contains code for different prediction models.
"""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson


class PoissonModel:
    # no line-break in the link is intentional and compliant to PEP8 guidelines
    """
    A model that predicts the winning team out of two given teams,
    based on a poisson regression model.

    Caution: The model is sensitive to the order of given teams,
    because the home_team scores better on average!

    `This model is heavily based on a guideline from David Sheehan.
    <https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling/>`_
    """

    def __init__(self, trainset_df):
        """
        Trains the poisson model.

        :param trainset_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        """
        self.poisson_model = None
        self._train_model(trainset_df)

    def _train_model(self, trainset):
        """
        Train a poisson regression model (generalized linear model)
        to predict "goals" from the parameters home, team and opponent

        :param trainset:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :return: None
        """
        try:
            # Builds two DataFrames with added column "home"
            # where one has "home"=1 for all rows, and one with "home"=0,
            # rename their columns according to this new configuration
            # and concatenate them.
            goal_model_data = pd.concat([
                trainset[['home_team',
                          'guest_team',
                          'home_score']].assign(home=1).rename(
                    columns={'home_team': 'team',
                             'guest_team': 'opponent',
                             'home_score': 'goals'}),
                trainset[['guest_team',
                          'home_team',
                          'guest_score']].assign(home=0).rename(
                    columns={'guest_team': 'team',
                             'home_team': 'opponent',
                             'guest_score': 'goals'})])

            # train glm poisson model on "goals"
            self.poisson_model = smf.glm(
                formula="goals ~ home + team + opponent",
                data=goal_model_data,
                family=sm.families.Poisson()).fit()
        except KeyError:
            raise KeyError("Column(s) missing in the given trainset."
                           "No model trained.")

    def simulate_match(self, home_team: str, guest_team: str):
        """
        Calculates a combined probability matrix
        for scoring an exact number of goals for both teams.

        :return: 'pd.DataFrame' Goals probability matrix
        """
        home_goals_avg = self.poisson_model.predict(pd.DataFrame(
            data={'team': home_team,
                  'opponent': guest_team,
                  'home': 1},
            index=[1])).values[0]
        away_goals_avg = self.poisson_model.predict(pd.DataFrame(
            data={'team': guest_team,
                  'opponent': home_team,
                  'home': 0},
            index=[1])).values[0]
        max_goals = 10  # this number is just a guess by eye so far
        team_pred = [[poisson.pmf(i, team_avg)
                      for i in range(0, max_goals + 1)]
                     for team_avg in [home_goals_avg, away_goals_avg]]
        return np.outer(np.array(team_pred[0]), np.array(team_pred[1]))

    def predict_winner(self, home_team: str, guest_team: str):
        """
        Determines the winning team based on a simulated match.

        :return: `str` Predicted winner and corresponding probability
        """
        sim_match = self.simulate_match(home_team, guest_team)

        # sum up lower triangle, upper triangle and diagonal probabilities
        home_team_win_prob = np.sum(np.tril(sim_match, -1))
        guest_team_win_prob = np.sum(np.triu(sim_match, 1))
        draw_prob = np.sum(np.diag(sim_match))

        if home_team_win_prob > guest_team_win_prob:
            return home_team + ": " + "{:.1%}".format(home_team_win_prob)
        elif home_team_win_prob < guest_team_win_prob:
            return guest_team + ": " + "{:.1%}".format(guest_team_win_prob)
        else:
            return "Draw" + ": " + "{:.1%}".format(draw_prob)


class FrequencyModel:
    """
    A model that uses all results of the last seasons to predict a winner
    based on the relative frequency of the respective result.
    """

    def __init__(self, trainset_df):
        """Expects a pd.DataFrame with at least four columns
        ['home_team', 'home_score', 'guest_score', 'guest_team']
        in this order"""
        self.all_matches_df = trainset_df
        self.matchups_df = None

    def _matchups(self, home_team, guest_team):
        """Builds a DataFrame of only rows where there are
        matches between guest_team and home_team"""
        matchups_frame = \
            self.all_matches_df[
                (self.all_matches_df['home_team'] == home_team)
                & (self.all_matches_df['guest_team'] == guest_team)]
        matchups_frame = matchups_frame.append(
            self.all_matches_df[
                (self.all_matches_df['home_team'] == guest_team)
                & (self.all_matches_df['guest_team'] == home_team)])
        self.matchups_df = matchups_frame
        return matchups_frame

    def _wins(self, team):
        """Builds a DataFrame of only rows where
        the given team won the match and returns it's length"""
        wins_frame = \
            self.matchups_df[(self.matchups_df['home_team'] == team)
                             & (self.matchups_df['home_score']
                                > self.matchups_df['guest_score'])]
        wins_frame = wins_frame.append(
            self.matchups_df[(self.matchups_df['guest_team'] == team)
                             & (self.matchups_df['guest_score']
                                > self.matchups_df['home_score'])])
        return len(wins_frame.index)

    def predict_winner(self, home_team, guest_team):
        """Casts a prediction based on the calculated probabilities and
        returns the names of the winning team or "Draw"
        if neither has a higher probability"""
        try:
            self.matchups_df = self._matchups(home_team,
                                              guest_team)  # instantiate df
            if len(self.matchups_df.index) == 0:
                return "Not enough data"
            home_team_win_prob = self._wins(home_team) / len(
                self.matchups_df.index)
            guest_team_win_prob = self._wins(guest_team) / len(
                self.matchups_df.index)
            if home_team_win_prob > guest_team_win_prob:
                return home_team
            elif home_team_win_prob < guest_team_win_prob:
                return guest_team
            else:
                return "Draw"
        except KeyError:
            # prevents other modules from failing by casting no prediction/draw
            return "Column(s) missing.No prediction calculated. "


# Gets ignored by GUI
class WholeDataFrequencies:
    """
    Not a model! But:
    a class that gives the frequencies for all data given for:
    - game outcomes (home_team wins, guest_team wins, None)
    - average goals per game (home_team, guest_team)
    """

    def __init__(self, trainset_df):
        """Expects a pd.DataFrame with at least four columns
        ['home_team', 'home_score', 'guest_score', 'guest_team']
        in this order"""
        self.all_matches_df = trainset_df

        self.home_team_wins = 0
        self.guest_team_wins = 0
        self.draws = 0
        self.home_team_avg_goals = None
        self.guest_team_avg_goals = None

        # initialize
        try:
            self._count_outcome_frequencies()
            self._count_average_goals_per_game()
        except KeyError:
            warnings.warn(
                """Column(s) missing in the given trainset.
                No statistics calculated.""")

    def _count_outcome_frequencies(self):
        """Builds DataFrames of only rows where
            - home team wins
            - guest team wins
            - neither team wins
        and returns their lengths"""
        home_team_wins_df = \
            self.all_matches_df[(self.all_matches_df['home_score']
                                 > self.all_matches_df['guest_score'])]
        self.home_team_wins = len(home_team_wins_df.index)

        guest_team_wins_df = \
            self.all_matches_df[(self.all_matches_df['guest_score']
                                 > self.all_matches_df['home_score'])]
        self.guest_team_wins = len(guest_team_wins_df.index)

        draws_df = \
            self.all_matches_df[(self.all_matches_df['home_score']
                                 == self.all_matches_df['guest_score'])]
        self.draws = len(draws_df.index)

    def _count_average_goals_per_game(self):
        """Builds DataFrames of only goal count columns for
            - home team goals
            - guest team goals
        and returns their average"""
        home_team_goals_df = self.all_matches_df[['home_score']]
        sum_of_home_team_goals = home_team_goals_df.sum()[0]  # just sum
        num_of_home_team_games = len(home_team_goals_df.index)

        if num_of_home_team_games == 0:  # prevent div by 0
            return 0
        else:
            self.home_team_avg_goals = (sum_of_home_team_goals
                                        / num_of_home_team_games)

        guest_team_goals_df = self.all_matches_df[['guest_score']]
        sum_of_guest_team_goals = guest_team_goals_df.sum()[0]  # just sum
        num_of_guest_team_games = len(guest_team_goals_df.index)

        if num_of_guest_team_games == 0:  # prevent div by 0
            return 0
        else:
            self.guest_team_avg_goals = (sum_of_guest_team_goals
                                         / num_of_guest_team_games)
