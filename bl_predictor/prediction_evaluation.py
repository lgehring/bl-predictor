"""
This module contains code for evaluating prediction models.
"""
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import sklearn.metrics as skm

from bl_predictor import models


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
        self.overview_df = self.true_winner_df.join(
            self.predicted_result_df).join(self.testset_df)
        self.accuracy, self.f1_score, self.conf_matrix = self.calc_metrics()

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

    def calc_metrics(self):
        """
        Generates metrics for the testset, including:
           - Accuracy
           - F1-Score
           - Confusion matrix

        :return: triple - accuracy, f1_score, confusion_matrix
        """
        true_and_pred_df = self.true_winner_df.join(self.predicted_result_df)
        for index, row in true_and_pred_df.iterrows():
            # cut off percentages
            true_and_pred_df.loc[index, 'predicted_result'] = \
                row['predicted_result'].split(':', 1)[0]

        true_winner = true_and_pred_df['true_winner']
        predicted_winner = true_and_pred_df['predicted_result']
        accuracy = skm.accuracy_score(true_winner, predicted_winner)
        f1_score = skm.f1_score(true_winner, predicted_winner,
                                average='weighted')
        conf_matrix = skm.confusion_matrix(true_winner, predicted_winner)
        return accuracy, f1_score, conf_matrix

    def print_results(self, print_plot=False):
        """
        Pretty prints all evaluation results in the console.

        :param print_plot: plots the confusion matrix, if TRUE
        """

        darkcyan = '\033[36m'
        green = '\033[92m'
        yellow = '\033[93m'
        bold = '\033[1m'
        underline = '\033[4m'
        end = '\033[0m'

        print(underline + bold + darkcyan + 'Evaluation Results' + end)
        print("Model: " + self.modelname)
        print("Accuracy (proportion of correct testset predictions): "
              + green + "{:.1%}".format(self.accuracy) + end)
        print("F1-score (weighted average of the precision and recall): "
              + green + "{:.1%}".format(self.f1_score) + end)
        print("Size of: Trainset: " + str(len(self.trainset_df.index))
              + " ({:.1%}".format(len(self.trainset_df.index)
                                  / len(self.data_df.index)) + ")")
        print("         Testset:  " + str(len(self.testset_df.index))
              + "   ({:.1%}".format(len(self.testset_df.index)
                                    / len(self.data_df.index)) + ")")
        print("")

        if self.modelname == 'PoissonModel' or \
                self.modelname == 'BettingPoissonModel':
            # only the PoissonModel has this functionality
            print(yellow + 'Team Ranking' + end)
            print("The given coefficients are an unaltered result "
                  "of the PoissonModel training")
            print("and do NOT represent actual wins or true rankings")
            self.model.team_ranking_df.index += 1  # adjust index for printing
            print(self.model.team_ranking_df.to_markdown())

        if print_plot:
            true_and_pred_df = \
                self.true_winner_df.join(self.predicted_result_df)
            for index, row in true_and_pred_df.iterrows():
                # cut off percentages
                true_and_pred_df.loc[index, 'predicted_result'] = \
                    row['predicted_result'].split(':', 1)[0]

            true_winner = true_and_pred_df['true_winner']
            labels = true_winner.drop_duplicates().sort_values()
            skm.ConfusionMatrixDisplay(self.conf_matrix, labels).plot()
            plt.title('Confusion matrix: ' + self.modelname)
            plt.xticks(rotation=90)
            plt.xlabel('Predicted winner')
            plt.ylabel('True winner')
            plt.tight_layout()
            plt.show()


class ModelCompare:
    """
    A class that compares two given models

    To print the report use: ModelCompare(args).print_results()
    """

    def __init__(self, model1, model2, data_df, testset_size):
        """
        Holds the basic comparison parameters and initiates the comparison.

        :param str model1: name of the first model
        :param str model2: name of the second model
        :param data_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :param int testset_size: number of last rows to assign to testset
        """
        self.model1 = ModelEvaluator(model1, data_df, testset_size)
        self.model2 = ModelEvaluator(model2, data_df, testset_size)
        self.kappa = self._cohen_kappa()
        self.acc_diff, self.better_acc_mod = self._accuracy_diff()
        self.f1_diff, self.better_f1_mod = self._f1_diff()

    def _cohen_kappa(self):
        """
        Calculates the kappa score for two models

        :return: int - kappa_score
        """
        for index, row in self.model1.predicted_result_df.iterrows():
            # cut off percentages
            self.model1.predicted_result_df.loc[index, 'predicted_result'] = \
                row['predicted_result'].split(':', 1)[0]
        for index, row in self.model2.predicted_result_df.iterrows():
            # cut off percentages
            self.model2.predicted_result_df.loc[index, 'predicted_result'] = \
                row['predicted_result'].split(':', 1)[0]

        model1_pred = self.model1.predicted_result_df
        model2_pred = self.model2.predicted_result_df
        kappa_score = skm.cohen_kappa_score(model1_pred, model2_pred)
        return kappa_score

    def _accuracy_diff(self):
        """
        Calculates the difference in accuracy for two models.

        :return: tuple - acc_diff, better_model
        """
        model1_acc = self.model1.accuracy
        model2_acc = self.model2.accuracy
        acc_diff = abs(model1_acc - model2_acc)
        if model1_acc >= model2_acc:
            better_model = self.model1.modelname
        else:
            better_model = self.model2.modelname
        return acc_diff, better_model

    def _f1_diff(self):
        """
        Calculates the difference in F1-score for two models.

        :return: tuple - f1_diff, better_model
        """
        model1_f1 = self.model1.f1_score
        model2_f1 = self.model2.f1_score
        f1_diff = abs(model1_f1 - model2_f1)
        if model1_f1 >= model2_f1:
            better_model = self.model1.modelname
        else:
            better_model = self.model2.modelname
        return f1_diff, better_model

    def print_results(self):
        """
        Pretty prints all comparison results in the console.
        """

        darkcyan = '\033[36m'
        green = '\033[92m'
        yellow = '\033[93m'
        bold = '\033[1m'
        underline = '\033[4m'
        end = '\033[0m'

        print(underline + bold + darkcyan + 'Comparison Results' + end)
        print("Model1: " + self.model1.modelname)
        print("Model2: " + self.model2.modelname)
        print("Size of testsets: " + str(self.model1.testset_size))
        print("")
        print(self.model1.modelname + " accuracy: " + yellow
              + "{:.1%}".format(self.model1.accuracy) + end)
        print(self.model2.modelname + " accuracy: " + yellow
              + "{:.1%}".format(self.model2.accuracy) + end)
        print("Better accuracy: " + bold + self.better_acc_mod + end
              + " by " + green + "{:.1%}".format(self.acc_diff) + end)
        print("")
        print(self.model1.modelname + "F1-score: " + yellow
              + "{:.1%}".format(self.model1.f1_score) + end)
        print(self.model2.modelname + "F1-score: " + yellow
              + "{:.1%}".format(self.model2.f1_score) + end)
        print("Better F1-score: " + bold + self.better_f1_mod + end
              + " by " + green + "{:.1%}".format(self.f1_diff) + end)
        print("")


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
