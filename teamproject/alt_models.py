"""
This module contains code for a prediction model.
"""


# TODO: cover edge case: missing data

class FrequencyModel:
    """
    A model that uses all results of the last seasons to predict a winner
    based on the relative frequency of the respective result.
    """

    def __init__(self, matches):
        """Expects a pd.DataFrame with four columns
        ['home_team', 'home_score', 'guest_score', 'guest_team']
        in this order"""
        self.all_matches_df = matches
        self.matchups_df = None

    def matchups(self, home_team, guest_team):
        """Builds a DataFrame of only rows where there are
        matches between guest_team and home_team"""
        matchups_frame = \
            self.all_matches_df[(self.all_matches_df['home_team'] == home_team)
                                & (self.all_matches_df['guest_team'] == guest_team)]
        matchups_frame = matchups_frame.append(
            self.all_matches_df[(self.all_matches_df['home_team'] == guest_team)
                                & (self.all_matches_df['guest_team'] == home_team)])
        self.matchups_df = matchups_frame
        return matchups_frame

    def wins(self, team):
        """Builds a DataFrame of only rows where
        the given team won the match"""
        wins_frame = \
            self.matchups_df[(self.matchups_df['home_team'] == team)
                             & (self.matchups_df['home_score'] > self.matchups_df['guest_score'])]
        wins_frame = wins_frame.append(
            self.matchups_df[(self.matchups_df['guest_team'] == team)
                             & (self.matchups_df['guest_score'] > self.matchups_df['home_score'])])
        return len(wins_frame.index)

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the calculated probabilities."""
        self.matchups_df = self.matchups(home_team, guest_team)  # instantiate the df
        home_team_win_prob = self.wins(home_team) / len(self.matchups_df.index)
        guest_team_win_prob = self.wins(guest_team) / len(self.matchups_df.index)
        if home_team_win_prob > guest_team_win_prob:
            return home_team + " won " + str(home_team_win_prob) + "/1 of all past matches and will most likely win"
        elif home_team_win_prob < guest_team_win_prob:
            return guest_team + " won " + str(guest_team_win_prob) + "/1 of all past matches and will most likely win"
        else:
            return "Both teams have equal probabilities of winning"
