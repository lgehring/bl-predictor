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
        self.home_team = matches.home_team.tolist()
        self.home_score = matches.home_score.tolist()
        self.guest_scores = matches.guest_score.tolist()
        self.guest_team = matches.guest_team.tolist()

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        if self.num_games[home_team] >= self.num_games[guest_team]:
            return home_team
        else:
            return guest_team

    def find_row_indizes(self, team):
        #puts indizes of accurence 'team' in matches in a list
        indizes = []
        numht = 0
        numgt = 0
        pos_beginning_ht= 0
        pos_beginning_gt = 0
        while (numht+numgt) < self.num_games[team]:
            if numht <= self.home_team.count(team):
                new_index = self.home_team.index(team, pos_beginning_ht)
                indizes += [new_index]
                pos_beginning_ht = new_index+1
                numht += 1

            if numgt < self.guest_team.count(team):
               new_index = self.guest_team.index(team, pos_beginning_gt)
               indizes += [new_index]
               pos_beginning_gt = new_index+1
               numgt += 1







