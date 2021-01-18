"""
This module contains code for evaluating prediction models.
"""

import pandas as pd

import models


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


# # Test: Hinrunde 2020 prediction, from 15.01.2021
# import crawler
# test_crawler_data = crawler.fetch_data([1, 2004], [34, 2020])
# ModelEvaluator("PoissonModel", test_crawler_data, 135).print_results()
