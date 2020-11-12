"""
This module contains code for different prediction models.
"""

import warnings
from collections import Counter


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

    def __matchups(self, home_team, guest_team):
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

    def __wins(self, team):
        """Builds a DataFrame of only rows where
        the given team won the match"""
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
        returns the names of the winning team or None
        if neither has a higher probability"""
        try:
            self.matchups_df = self.__matchups(home_team,
                                               guest_team)  # instantiate df
            if len(self.matchups_df.index) == 0:
                return None
            home_team_win_prob = self.__wins(home_team) / len(
                self.matchups_df.index)
            guest_team_win_prob = self.__wins(guest_team) / len(
                self.matchups_df.index)
            if home_team_win_prob > guest_team_win_prob:
                return home_team
            elif home_team_win_prob < guest_team_win_prob:
                return guest_team
            else:
                return None
        except KeyError:
            warnings.warn(
                """Column(s) missing in the given trainset. 
                No prediction calculated.""")
            # prevents other modules from failing by casting no prediction/draw
            return None
        
