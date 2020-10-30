# Use this file to test your prediction algorithms.

from teamproject import models
import pandas as pd

# It is important to test your algorithms against handcrafted data to reliably
# cover edge cases! So feel free to make up several test datasets in the same
# format as would be returned by your crawler:
test_dataset = pd.DataFrame([
    ['A', 0, 1, 'B'],
    ['B', 1, 0, 'C'],
], columns=['home_team', 'home_score', 'guest_score', 'guest_team'])


# The following is an example of how useful tests could look like:

def test_experience_always_wins():
    model = models.ExperienceAlwaysWins(test_dataset)
    winner = model.predict_winner

    # B is the most experienced team with two matches:
    assert winner('A', 'B') == winner('B', 'A') == 'B'
    assert winner('C', 'B') == winner('B', 'C') == 'B'

    # A and C are tied with one match, so the home team wins:
    assert winner('A', 'C') == 'A'
    assert winner('C', 'A') == 'C'

    # We don't know 'D' or 'E' yet, so they should be counted as having zero
    # matches:
    assert winner('A', 'D') == winner('D', 'A') == 'A'
    assert winner('A', 'E') == winner('E', 'A') == 'A'
    assert winner('D', 'E') == 'D'
    assert winner('E', 'D') == 'E'
