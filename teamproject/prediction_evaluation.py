"""
This module contains code for evaluating prediction models.
"""

import pandas as pd

import models


class ModelEvaluator:
    """
    A class that evaluates a given model with given data.
    """

    def __init__(self, modelname, data_df, testset_size):
        """
        Holds the basic evaluation parameters and initiates the evaluation.

        :param string - modelname: name of the model to evaluate
        :param data_df:
         pd.DataFrame['home_team', 'home_score', 'guest_score', 'guest_team']
        :param int - testset_size: number of last rows to assign to testset
        """
        self.modelname = modelname
        self.data_df = data_df
        self.testset_size = testset_size
        self.trainset_df, self.testset_df = self._build_train_testset()
        self.predicted_winner_df = self.predict_testset()
        self.true_winner_df = self.determine_winner()
        self.overview = self.testset_df.join(
            self.true_winner_df).join(self.predicted_winner_df)

    def _build_train_testset(self):
        """
        Builds a trainset pd.DataFrame that contains all data except
        the last given number of rows and
        a testset pd.DataFrame that contains those last rows

        :return: tuple - trainset_df, testset_df
        """
        trainset_df = self.data_df.iloc[:-self.testset_size]
        testset_df = self.data_df.iloc[-self.testset_size:].reset_index(
            drop=True)
        return trainset_df, testset_df

    def determine_winner(self):
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

    def predict_testset(self):
        """
        Uses the given data and a given testset_size to train a model
        on all data except the testset and uses the model to
        predict the testset matches.

        :return: prediction_df:
         pd.DataFrame['predicted_winner']
        """
        predicted_winner_df = pd.DataFrame([],
                                           dtype="string",
                                           columns=['predicted_winner'])

        trainset_df, testset_df = self._build_train_testset()
        # Get actual model using modelname from models
        trained_model = getattr(models, self.modelname)(trainset_df)

        for index, row in self.testset_df.iterrows():
            predicted_winner = trained_model.predict_winner(row['home_team'],
                                                            row['guest_team'])
            predicted_winner_df.loc[
                len(predicted_winner_df)] = predicted_winner
        return predicted_winner_df
