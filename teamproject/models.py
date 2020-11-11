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
        self.guest_score = matches.guest_score.tolist()
        self.guest_team = matches.guest_team.tolist()

    def predict_winner(self, home_team, guest_team):
        """Cast prediction based on the "learned" parameters."""
        prob_to_win_ht = self.analyse_scores(home_team)[0]/self.num_games[home_team]
        prob_to_win_gt = self.analyse_scores(guest_team)[0]/self.num_games[guest_team]
        if prob_to_win_ht >= prob_to_win_gt:
            return home_team
        else:
            return guest_team

    def find_row_indizes(self, team):
        #gives back indizes of rows, where 'team' is.
        # returns tuple with two arrays. first array: team was home team,
        # second array: team as guest_team

        indizes_as_ht = []
        indizes_as_gt =[]
        numht = 0
        numgt = 0
        pos_beginning_ht= 0
        pos_beginning_gt = 0
        while (numht+numgt) < self.num_games[team]:
            if numht < self.home_team.count(team):
                new_index = self.home_team.index(team, pos_beginning_ht)
                indizes_as_ht += [new_index]
                pos_beginning_ht = new_index+1
                numht += 1

            if numgt < self.guest_team.count(team):
               new_index = self.guest_team.index(team, pos_beginning_gt)
               indizes_as_gt += [new_index]
               pos_beginning_gt = new_index+1
               numgt += 1
        return (indizes_as_ht, indizes_as_gt)



    def analyse_scores(self, team):
        #returns list with number  of wins, defeat and draws in this order
        indizes = self.find_row_indizes(team)
        defeat = 0
        draw = 0
        win = 0
        #determine results of scores, 'team' as home team
        for y in indizes[0]:
            score_team = self.home_score[y]
            score_oppenent = self.guest_score[y]
            if score_team<score_oppenent:
                defeat += 1
            elif score_team == score_oppenent:
                draw += 1
            else:
                win += 1
        #determines result of scores, 'team' a guest team
        for y in indizes[1]:
            score_oppenent = self.home_score[y]
            score_team= self.guest_score[y]
            if score_team<score_oppenent:
                defeat += 1
            elif score_team == score_oppenent:
                draw += 1
            else:
                win += 1
        result = [win, defeat, draw]
        return result
