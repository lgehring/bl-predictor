# Use this file to test your crawler.

from teamproject import crawler
import pandas as pd
import pytest




def test_fetch_data():
    data = crawler.fetch_data([1, 2014], [1, 2014])
    assert isinstance(data, pd.DataFrame)
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.home_team != data.guest_team).all()


@pytest.mark.parametrize(
    "start_date, end_date, index, expected",
    [  # curate urls tests
        ([1, 2014], [2, 2014], None, [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1',
            'https://api.openligadb.de/getmatchdata/bl1/2014/2']),
        ([1, 2014], [1, 2014], None, [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1']),
        ([1, 2014], [8, 2016], -1,
         "https://api.openligadb.de/getmatchdata/bl1/2016/8"),
        ([1, 2014], [8, 2016], 0,
         "https://api.openligadb.de/getmatchdata/bl1/2014/1"),
        ([1, 2014], [8, 2016], 35,
         "https://api.openligadb.de/getmatchdata/bl1/2015/2")
    ])

def test_test_curate_urls(start_date, end_date, index, expected):
    crawler.curate_urls(start_date, end_date)
    if index != None:
        assert crawler.urls[index] == expected
    else:
        crawler.urls == expected
    crawler.urls = []
