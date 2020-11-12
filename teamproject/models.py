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


class AlternativeFrequencyModel:
    """
    An example model that predicts the winner predicts the winner
    solely based on number of games played.
    """

    def __init__(self, all_matches):
        self.num_games = (
                Counter(all_matches.home_team)
                + Counter(all_matches.guest_team))
        self.home_team = all_matches.home_team.tolist()
        self.home_score = all_matches.home_score.tolist()
        self.guest_score = all_matches.guest_score.tolist()
        self.guest_team = all_matches.guest_team.tolist()

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        prob_to_win_ht = self.analyse_scores(home_team)[0] / self.num_games[
            home_team]
        prob_to_win_gt = self.analyse_scores(guest_team)[0] / self.num_games[
            guest_team]
        if prob_to_win_ht >= prob_to_win_gt:
            return home_team
        else:
            return guest_team

    # noinspection SpellCheckingInspection
    def find_row_indices(self, team):
        # gives back indices of rows, where 'team' is.
        # returns tuple with two arrays. first array: team was home team,
        # second array: team as guest_team

        indices_as_ht = []
        indices_as_gt = []
        numht = 0
        numgt = 0
        pos_beginning_ht = 0
        pos_beginning_gt = 0
        while (numht + numgt) < self.num_games[team]:
            if numht < self.home_team.count(team):
                new_index = self.home_team.index(team, pos_beginning_ht)
                indices_as_ht += [new_index]
                pos_beginning_ht = new_index + 1
                numht += 1

            if numgt < self.guest_team.count(team):
                new_index = self.guest_team.index(team, pos_beginning_gt)
                indices_as_gt += [new_index]
                pos_beginning_gt = new_index + 1
                numgt += 1
        return indices_as_ht, indices_as_gt

    def analyse_scores(self, team):
        # returns list with number  of wins, defeat and draws in this order
        indices = self.find_row_indices(team)
        defeat = 0
        draw = 0
        win = 0
        # determine results of scores, 'team' as home team
        for y in indices[0]:
            score_team = self.home_score[y]
            score_opponent = self.guest_score[y]
            if score_team < score_opponent:
                defeat += 1
            elif score_team == score_opponent:
                draw += 1
            else:
                win += 1
        # determines result of scores, 'team' a guest team
        for y in indices[1]:
            score_opponent = self.home_score[y]
            score_team = self.guest_score[y]
            if score_team < score_opponent:
                defeat += 1
            elif score_team == score_opponent:
                draw += 1
            else:
                win += 1
        result = [win, defeat, draw]
        return result
