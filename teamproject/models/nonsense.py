"""
This module contains code for a completely nonsensical machine learning model
that learns to "predict results from given data".
"""


class Model:

    """A nonsensical model."""

    def __init__(self, params):
        self.params = params

    @classmethod
    def fit(cls, data):
        """
        Learn model parameters from the given data and return a
        corresponding Model.
        """
        params = sum([x**2 for x in data])
        return cls(params)

    def predict(self, where):
        """Cast prediction based on the learned parameters."""
        return self.params * where
