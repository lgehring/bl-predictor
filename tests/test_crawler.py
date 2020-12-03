# Use this file to test your crawler.

from teamproject import crawler
import pandas as pd
import unittest


class test_crawler(unittest.TestCase):


    def test_fetch_data(self):
        data = crawler.fetch_data([1, 2014], [1, 2014])
        assert isinstance(data, pd.DataFrame)
        assert (data.home_score >= 0).all()
        assert (data.guest_score >= 0).all()
        assert (data.home_team != data.guest_team).all()

    def test_curate_urls_two_days(self):
        crawler.curate_urls([1, 2014], [2, 2014])
        assert crawler.urls == [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1',
            'https://api.openligadb.de/getmatchdata/bl1/2014/2']
        crawler.urls = []

    def test_curate_urls_one_day(self):
        crawler.curate_urls([1, 2014], [1, 2014])
        assert crawler.urls == [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1']
        crawler.urls = []

    def test_curate_urls_multiple_seasons(self):
        crawler.curate_urls([1, 2014], [8, 2016])
        assert crawler.urls[-1] == \
               "https://api.openligadb.de/getmatchdata/bl1/2016/8"
        assert crawler.urls[0] == \
               "https://api.openligadb.de/getmatchdata/bl1/2014/1"
        assert crawler.urls[35] == \
               "https://api.openligadb.de/getmatchdata/bl1/2015/2"
        crawler.urls = []

    def test_curate_urls_raise_error(self):
        self.assertRaises(ValueError,
                          lambda: crawler.curate_urls([0, 2014],
                                                      [8, 2016]))
