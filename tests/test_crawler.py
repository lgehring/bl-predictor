# Use this file to test your crawler.

from teamproject import crawler
import unittest


class test_crawler(unittest.TestCase):
    # Example test:
    """
    def test_fetch_data():
        data = crawler.fetch_data()
        assert isinstance(data, pd.DataFrame)
        assert data.home_score.dtype == 'int64'
        assert data.guest_score.dtype == 'int64'
        assert (data.home_score >= 0).all()
        assert (data.guest_score >= 0).all()
        assert (data.home_team != data.guest_team).all()
    """
