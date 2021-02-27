"""
This module contains code for different prediction models.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson


class PoissonModel:
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
        Builds the poisson model and calculates a team ranking based on
        the coefficients obtained from training.

        :param trainset_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        """
        self.poisson_model = None
        self.team_ranking_df = None

        # In case of corrupt trainset_df:
        # Catch internal errors occurring in the smf.glm function
        # The problem is passed here but will be handled by predict_winner
        try:
            self._train_model(trainset_df)
            self.team_ranking_df = self._calc_team_ranking()
        except (ValueError, KeyError):
            pass

    def _train_model(self, trainset):
        """
        Train a poisson regression model (generalized linear model)
        to predict "goals" from the parameters home, team and opponent

        :param trainset:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :return: None
        """
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

    def _simulate_match(self, home_team: str, guest_team: str):
        """
        Calculates a combined probability matrix
        for scoring an exact number of goals for both teams.

        :return: pd.DataFrame Goals probability matrix
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

        The calculated winning probability of one team must be at least by
        threshold-percent higher than the other teams, or else "Draw" will be
        returned.
        (Draw percentage may be below any teams personal winning probability)
        The threshold was determined empirically to yield the best result.

        :return: str Predicted winner and corresponding probability
        """
        try:
            sim_match = self._simulate_match(home_team, guest_team)

            # sum up lower triangle, upper triangle and diagonal probabilities
            home_team_win_prob = np.round(np.sum(np.tril(sim_match, -1)), 5)
            guest_team_win_prob = np.round(np.sum(np.triu(sim_match, 1)), 5)
            draw_prob = np.round(np.sum(np.diag(sim_match)), 5)

            if home_team_win_prob > guest_team_win_prob and \
                    home_team_win_prob > draw_prob:
                return home_team + ": " + "{:.1%}".format(home_team_win_prob)
            elif guest_team_win_prob > home_team_win_prob and \
                    guest_team_win_prob > draw_prob:
                return guest_team + ": " + "{:.1%}".format(guest_team_win_prob)
            else:
                return "Draw" + ": " + "{:.1%}".format(draw_prob)
        except AttributeError:
            return 'Prediction failed. Check training DataFrame for errors'

    def _calc_team_ranking(self):
        """
        Uses the the trained coefficients of the model to rank all teams
        when playing as hometeam and guestteam

        The coefficients of the guest team column are negative values
        because the model tries to determine the impact of the coefficient
        to the winning probabilities of the hometeam.
        They may be interpreted as positive values in this case.

        :return: pd.DataFrame['home_ranking', 'guest_ranking']
        """
        # extract model summary as DataFrame and sort by coef value
        summary_df = pd.read_html(self.poisson_model.summary().tables[1].
                                  as_html(), header=0, index_col=0)[0]
        summary_df = summary_df.sort_values('coef', ascending=False)

        # export hometeam and guestteam entries as DataFrames
        home_ranking_df = summary_df[
            ['team' in s for s in summary_df.index]].sort_values(
            'coef', ascending=False)['coef'].to_frame()
        guest_ranking_df = summary_df[
            ['opponent' in s for s in summary_df.index]].sort_values(
            'coef', ascending=True)['coef'].to_frame()
        home_ranking_df.reset_index(inplace=True)
        home_ranking_df = home_ranking_df.rename(
            columns={'index': 'hometeam_ranking', 'coef': 'home_coef'})
        # reorder columns for better readability
        home_ranking_df = home_ranking_df[['home_coef', 'hometeam_ranking']]
        guest_ranking_df.reset_index(inplace=True)
        guest_ranking_df = guest_ranking_df.rename(
            columns={'index': 'guestteam_ranking', 'coef': 'guest_coef'})

        # combine both DataFrames and remove prefix and suffix from entries
        team_ranking_df = home_ranking_df.join(guest_ranking_df)
        team_ranking_df['hometeam_ranking'] = \
            team_ranking_df['hometeam_ranking'].apply(
                lambda s: s.replace('team[T.', '').replace(']', ''))
        team_ranking_df['guestteam_ranking'] = \
            team_ranking_df['guestteam_ranking'].apply(
                lambda s: s.replace('opponent[T.', '').replace(']', ''))
        return team_ranking_df


class BettingPoissonModel:
    """
    A adaptation of the PoissonModel improved for betting.
    If no relevant (>10%) difference in the teams
    winning probabilities is present, "Draw" is returned.

    A model that predicts the winning team out of two given teams,
    based on a poisson regression model.

    Caution: The model is sensitive to the order of given teams,
    because the home_team scores better on average!

    `This model is heavily based on a guideline from David Sheehan.
    <https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling/>`_
    """

    def __init__(self, trainset_df):
        """
        Builds the poisson model and calculates a team ranking based on
        the coefficients obtained from training.

        :param trainset_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        """
        self.poisson_model = None
        self.team_ranking_df = None

        # In case of corrupt trainset_df:
        # Catch internal errors occurring in the smf.glm function
        # The problem is passed here but will be handled by predict_winner
        try:
            self._train_model(trainset_df)
            self.team_ranking_df = self._calc_team_ranking()
        except (ValueError, KeyError):
            pass

    def _train_model(self, trainset):
        """
        Train a poisson regression model (generalized linear model)
        to predict "goals" from the parameters home, team and opponent

        :param trainset:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :return: None
        """
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

    def _simulate_match(self, home_team: str, guest_team: str):
        """
        Calculates a combined probability matrix
        for scoring an exact number of goals for both teams.

        :return: pd.DataFrame Goals probability matrix
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

        The calculated winning probability of one team must be at least by
        threshold-percent higher than the other teams, or else "Draw" will be
        returned.
        (Draw percentage may be below any teams personal winning probability)
        The threshold was determined empirically to yield the best result.

        :return: str Predicted winner and corresponding probability
        """
        try:
            sim_match = self._simulate_match(home_team, guest_team)

            # sum up lower triangle, upper triangle and diagonal probabilities
            home_team_win_prob = np.round(np.sum(np.tril(sim_match, -1)), 5)
            guest_team_win_prob = np.round(np.sum(np.triu(sim_match, 1)), 5)
            draw_prob = np.round(np.sum(np.diag(sim_match)), 5)

            # Threshold is just a guess
            significance_threshold = 0.1  # chance (home win, guest win, draw)
            if home_team_win_prob > guest_team_win_prob and \
                    home_team_win_prob > draw_prob and \
                    (home_team_win_prob - guest_team_win_prob) \
                    > significance_threshold:
                return home_team + ": " + "{:.1%}".format(home_team_win_prob)
            elif guest_team_win_prob > home_team_win_prob and \
                    guest_team_win_prob > draw_prob and \
                    (guest_team_win_prob - home_team_win_prob) \
                    > significance_threshold:
                return guest_team + ": " + "{:.1%}".format(guest_team_win_prob)
            else:
                return "Draw" + ": " + "{:.1%}".format(draw_prob)
        except AttributeError:
            return 'Prediction failed. Check training DataFrame for errors'

    def _calc_team_ranking(self):
        """
        Uses the the trained coefficients of the model to rank all teams
        when playing as hometeam and guestteam

        The coefficients of the guest team column are negative values
        because the model tries to determine the impact of the coefficient
        to the winning probabilities of the hometeam.
        They may be interpreted as positive values in this case.

        :return: pd.DataFrame['home_ranking', 'guest_ranking']
        """
        # extract model summary as DataFrame and sort by coef value
        summary_df = pd.read_html(self.poisson_model.summary().tables[1].
                                  as_html(), header=0, index_col=0)[0]
        summary_df = summary_df.sort_values('coef', ascending=False)

        # export hometeam and guestteam entries as DataFrames
        home_ranking_df = summary_df[
            ['team' in s for s in summary_df.index]].sort_values(
            'coef', ascending=False)['coef'].to_frame()
        guest_ranking_df = summary_df[
            ['opponent' in s for s in summary_df.index]].sort_values(
            'coef', ascending=True)['coef'].to_frame()
        home_ranking_df.reset_index(inplace=True)
        home_ranking_df = home_ranking_df.rename(
            columns={'index': 'hometeam_ranking', 'coef': 'home_coef'})
        # reorder columns for better readability
        home_ranking_df = home_ranking_df[['home_coef', 'hometeam_ranking']]
        guest_ranking_df.reset_index(inplace=True)
        guest_ranking_df = guest_ranking_df.rename(
            columns={'index': 'guestteam_ranking', 'coef': 'guest_coef'})

        # combine both DataFrames and remove prefix and suffix from entries
        team_ranking_df = home_ranking_df.join(guest_ranking_df)
        team_ranking_df['hometeam_ranking'] = \
            team_ranking_df['hometeam_ranking'].apply(
                lambda s: s.replace('team[T.', '').replace(']', ''))
        team_ranking_df['guestteam_ranking'] = \
            team_ranking_df['guestteam_ranking'].apply(
                lambda s: s.replace('opponent[T.', '').replace(']', ''))
        return team_ranking_df


class FrequencyModel:
    """
    A model that uses all results of the last seasons to predict a winner
    based on the relative frequency of the respective result.
    """

    def __init__(self, trainset_df):
        """
        Builds the frequency model.

        :param trainset_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        """
        self.all_matches_df = trainset_df
        self.matchups_df = None

    def _matchups(self, home_team, guest_team):
        """
        Builds a DataFrame of only rows where there are
        matches between home_team and guest_team

        :return: pd.DataFrame All matches between given teams
        """
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
        """
        Builds a DataFrame of only rows where
        the given team won the match and returns it's length

        :return: int Number of matches the given team wins
        """
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
        """
        Casts a prediction based on the calculated probabilities and
        returns the names and probabilities of the winning team or "Draw"
        if neither has a higher probability

        :return: str One of: home_team, guest_team, "Draw"
        """
        try:
            self.matchups_df = self._matchups(home_team,
                                              guest_team)  # instantiate df
            if len(self.matchups_df.index) == 0:
                return "Not enough data"
            home_team_win_prob = self._wins(home_team) / len(
                self.matchups_df.index)
            guest_team_win_prob = self._wins(guest_team) / len(
                self.matchups_df.index)
            draw_prob = 1 - (guest_team_win_prob + home_team_win_prob)
            if home_team_win_prob > guest_team_win_prob and \
                    home_team_win_prob > draw_prob:
                return home_team + ": " + "{:.1%}".format(home_team_win_prob)
            elif home_team_win_prob < guest_team_win_prob and \
                    guest_team_win_prob > draw_prob:
                return guest_team + ": " + "{:.1%}".format(guest_team_win_prob)
            else:
                return "Draw" + ": " + "{:.1%}".format(draw_prob)
        except KeyError:
            # prevents other modules from failing by casting no prediction/draw
            return "Prediction failed. Check training DataFrame for errors"
