"""
This module contains code for different prediction models.
"""

import warnings


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
        returns the names of the winning team or None
        if neither has a higher probability"""
        try:
            self.matchups_df = self._matchups(home_team,
                                              guest_team)  # instantiate df
            if len(self.matchups_df.index) == 0:
                return None
            home_team_win_prob = self._wins(home_team) / len(
                self.matchups_df.index)
            guest_team_win_prob = self._wins(guest_team) / len(
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
