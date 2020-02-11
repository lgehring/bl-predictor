"""
Add your GUI code here.
"""

from teamproject.crawler import fetch_data
from teamproject.models.nonsense import Model


def main():
    """
    Creates and shows the main window.
    """
    # Add code here to create and initialize window.

    # For demo purposes, this is how you could access methods from other
    # modules:
    data = fetch_data()
    model = Model.fit(data)
    results = model.predict(2)
    print(results)
