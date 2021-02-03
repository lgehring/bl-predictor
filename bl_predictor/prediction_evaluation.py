"""
This module contains code for evaluating prediction models.
"""
import warnings
import pandas as pd
from bl_predictor import models

import sklearn.metrics as skm


class ModelEvaluator:
    """
    A class that evaluates a given model with the given data.

    To print the report use: ModelEvaluator(args).print_results()
    """

    def __init__(self, modelname, data_df, testset_size):
        """
        Holds the basic evaluation parameters and initiates the evaluation.

        :param str modelname: name of the model to evaluate
        :param data_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :param int testset_size: number of last rows to assign to testset
        """
        self.modelname = modelname
        self.data_df = data_df
        self.testset_size = testset_size
        self.trainset_df, self.testset_df = self._build_train_testset()
        self.predicted_result_df, self.model = self._predict_testset()
        self.true_winner_df = self._determine_winner()
        self.prediction_accuracy, self.success_df = \
            self._calc_prediction_accuracy()
        self.overview_df = self.success_df.join(self.testset_df)

    def _build_train_testset(self):
        """
        Builds a trainset pd.DataFrame that contains all data except
        the last given number of rows and
        a testset pd.DataFrame that contains those last rows

        :return: tuple trainset_df, testset_df
        """
        trainset_df = self.data_df.iloc[:-self.testset_size]
        testset_df = self.data_df.iloc[-self.testset_size:].reset_index(
            drop=True)
        return trainset_df, testset_df

    def _determine_winner(self):
        """
        Uses the given data to determine the true winner (or draw)
        of each match in the testset using only the number of goals

        :return: true_winner_df:
         pd.DataFrame['true_winner']
        """
        true_winner_df = pd.DataFrame([],
                                      dtype="string",
                                      columns=['true_winner'])

        for index, row in self.testset_df.iterrows():
            if row['home_score'] > row['guest_score']:
                true_winner_df.loc[len(true_winner_df)] = row['home_team']
            elif row['home_score'] < row['guest_score']:
                true_winner_df.loc[len(true_winner_df)] = row['guest_team']
            else:
                true_winner_df.loc[len(true_winner_df)] = "Draw"
        return true_winner_df

    def _predict_testset(self):
        """
        Uses the given data and a given testset_size to train a model
        on all data except the testset and uses the model to
        predict the testset matches.

        :return: tuple prediction_df:
         pd.DataFrame['predicted_winner']
         trained_model: model trained on the trainset
        """
        predicted_result_df = pd.DataFrame([],
                                           dtype="string",
                                           columns=['predicted_result'])

        trainset_df = self._build_train_testset()[0]
        # Get actual model using modelname from models
        trained_model = getattr(models, self.modelname)(trainset_df)

        for index, row in self.testset_df.iterrows():
            predicted_winner = trained_model.predict_winner(row['home_team'],
                                                            row['guest_team'])
            predicted_result_df.loc[
                len(predicted_result_df)] = predicted_winner
        return predicted_result_df, trained_model

    def _calc_prediction_accuracy(self):
        """
        Uses the true_winner_df and predicted_result_df and calculates
        what percentage of matches in the testset was correctly predicted

        :return: tuple percentage of correctly predicted matches,
            pd.DataFrame['prediction_correct?']
        """
        success_df = self.true_winner_df.join(self.predicted_result_df)
        success_df['prediction_correct?'] = bool
        # rearrange DF to display correctness of prediction in first column
        success_df = success_df[['prediction_correct?',
                                 'predicted_result',
                                 'true_winner']]

        for index, row in success_df.iterrows():
            # some models return more data than just the teamname
            if row['true_winner'] in row['predicted_result']:
                success_df.loc[index, 'prediction_correct?'] = True
            else:
                success_df.loc[index, 'prediction_correct?'] = False
        try:
            good_pred = success_df['prediction_correct?'].value_counts(
            ).loc[True]
        except KeyError:
            # happens when no match is correctly predicted
            good_pred = 0

        percent_corr_pred = "{:.1%}".format(good_pred / len(success_df))
        return percent_corr_pred, success_df

    def metrics(self):
        """
        Generates metrics for the testset
        # TODO: describe metrics

        :return: TODO
        """
        df = self.success_df.drop(columns=['prediction_correct?'])
        for index, row in df.iterrows():
            # cut off percentages
            df.loc[index, 'predicted_result'] = \
                row['predicted_result'].split(':', 1)[0]
        true_winner = df['true_winner']
        predicted_winner = df['predicted_result']

        # metrics
        print(skm.classification_report(true_winner, predicted_winner))

    def print_results(self):
        """
        Pretty prints all evaluation results in the console
        """

        purple = '\033[95m'
        darkcyan = '\033[36m'
        green = '\033[92m'
        yellow = '\033[93m'
        bold = '\033[1m'
        underline = '\033[4m'
        end = '\033[0m'

        print(underline + bold + darkcyan
              + 'Evaluation Results' + end)
        print("Model: " + self.modelname)
        print("Accuracy (proportion of correct testset predictions): "
              + green + self.prediction_accuracy + end)
        print("Size of: Trainset: " + str(len(self.trainset_df.index))
              + " ({:.1%}".format(len(self.trainset_df.index)
                                  / len(self.data_df.index)) + ")")
        print("         Testset:  " + str(len(self.testset_df.index))
              + "   ({:.1%}".format(len(self.testset_df.index)
                                    / len(self.data_df.index)) + ")")
        print("")

        print(purple + 'Detailed prediction results' + end)
        self.overview_df.index += 1  # adjust index for printing
        print(self.overview_df.to_markdown())
        print("")

        if self.modelname == 'PoissonModel':
            # only the PoissonModel has this functionality
            print(yellow + 'Team Ranking' + end)
            print("The given coefficients are an unaltered result "
                  "of the PoissonModel training")
            print("and do NOT represent actual wins or true rankings")
            self.model.team_ranking_df.index += 1  # adjust index for printing
            print(self.model.team_ranking_df.to_markdown())

# Test
import crawler
test_crawler_data = crawler.fetch_data([1, 2019], [34, 2019])
ModelEvaluator("PoissonModel", test_crawler_data, 90).metrics()


class WholeDataFrequencies:
    """
    Not a model! But:
    a class that gives the frequencies for all data given for:
        - game outcomes (home_team wins, guest_team wins, None)
        - average goals per game (home_team, guest_team)
    """

    def __init__(self, trainset_df):
        """
        Builds the WholeDataFrequencies statistics parameters.

        :param trainset_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        """
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
            warnings.warn("Calculating stats failed. "
                          "Check training DataFrame for errors")

    def _count_outcome_frequencies(self):
        """Builds DataFrames of only rows where
            - home team wins
            - guest team wins
            - neither team wins
        and assigns their lengths"""
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
        and assigns their average value"""
        home_team_goals_df = self.all_matches_df[['home_score']]
        sum_of_home_team_goals = home_team_goals_df.sum()[0]  # just sum
        num_of_home_team_games = len(home_team_goals_df.index)

        if num_of_home_team_games == 0:  # prevent div by 0
            self.home_team_avg_goals = None
        else:
            self.home_team_avg_goals = (sum_of_home_team_goals
                                        / num_of_home_team_games)

        guest_team_goals_df = self.all_matches_df[['guest_score']]
        sum_of_guest_team_goals = guest_team_goals_df.sum()[0]  # just sum
        num_of_guest_team_games = len(guest_team_goals_df.index)

        if num_of_guest_team_games == 0:  # prevent div by 0
            self.guest_team_avg_goals = None
        else:
            self.guest_team_avg_goals = (sum_of_guest_team_goals
                                         / num_of_guest_team_games)
