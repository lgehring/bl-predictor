"""
Add your GUI code here.
"""

from teamproject.crawler import fetch_data
from teamproject.models import ExperienceAlwaysWins


def main():
    """
    Creates and shows the main window.
    """
    # Add code here to create and initialize window.

    # For demo purposes, this is how you could access methods from other
    # modules:
    data = fetch_data()
    model = ExperienceAlwaysWins(data)
    winner = model.predict_winner('Tübingen', 'Leverkusen')
    print(winner)
