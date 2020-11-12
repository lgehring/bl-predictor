"""
This module contains code to fetch required data from the internet and convert
it to our internal format.
"""

import pandas as pd


def fetch_data():
    """
    Query data from "the internet" and return in our internal format.
    """
    # For now just return some example data in some example format:
    columns = ['home_team', 'home_score', 'guest_score', 'guest_team']
    return pd.DataFrame([
        ['Bayern', 0, 7, 'Tübingen'],
        ['Tübingen', 3, 2, 'Borussia'],
        ['Tübingen', 1, 0, 'Leverkusen'],
        ['Bremen', 0, 1, 'Leverkusen'],
    ], columns=columns)
