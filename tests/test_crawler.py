# Use this file to test your crawler.

import pandas as pd
import pandas.api.types as ptypes
import pytest

import teamproject.crawler as crawler


def test_fetch_data():
    data = crawler.fetch_data([1, 2010], [12, 2015])
    assert isinstance(data, pd.DataFrame)
    assert all(ptypes.is_numeric_dtype(data[col])
               for col in ['home_score', 'guest_score'])
    assert all(ptypes.is_string_dtype(data[col])
               for col in ['home_team', 'guest_team'])
    assert ptypes.is_datetime64_any_dtype(data['date_time'])
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.season >= 2010).all()
    assert (data.season <= 2015).all()
    assert (0 < data.matchday < 35).all()




@pytest.mark.parametrize(
    "start_date, end_date, index_of_url, expected",
    [  # curate urls tests
        ([1, 2014], [2, 2014], None, [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1',
            'https://api.openligadb.de/getmatchdata/bl1/2014/2']),
        ([1, 2014], [1, 2014], None, [
            'https://api.openligadb.de/getmatchdata/bl1/2014/1']),
        ([1, 2014], [8, 2016], -1,
         "https://api.openligadb.de/getmatchdata/bl1/2016/8"),
        ([1, 2014], [8, 2016], 0,
         "https://api.openligadb.de/getmatchdata/bl1/2014"),
        ([1, 2014], [8, 2016], 1,
         "https://api.openligadb.de/getmatchdata/bl1/2015")
    ])
def test_test_curate_urls(start_date, end_date, index_of_url, expected):
    urls = crawler.curate_urls(start_date, end_date)
    if index_of_url is not None:
        assert urls[index_of_url] == expected
    else:
        assert urls == expected
