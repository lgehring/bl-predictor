"""
This module contains code for a prediction models.
"""

from collections import Counter


class ExperienceAlwaysWins:
    """
    An example model that predicts the winner predicts the winner
    solely based on number of games played.
    """

    def __init__(self, matches):
        # We just count the number of games played by all teams and ignore
        # the winner:
        self.num_games = (
                Counter(matches.home_team)
                + Counter(matches.guest_team))

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        if self.num_games[home_team] >= self.num_games[guest_team]:
            return home_team
        else:
            return guest_team
