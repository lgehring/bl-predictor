# Use this file to test your crawler.

import pandas as pd
import pandas.api.types as ptypes
import pytest

from bl_predictor import crawler
import os


def test_fetch_data():

    # path of csv file
    test_path = os.path.abspath(os.path.join(os.getcwd(),"../.."))
    print(test_path)
    csv_file = os.path.join(test_path, 'bl_predictor/bl_predictor/crawled_data.csv')
    print(csv_file)
    # test_matches
    '''
    test_urls = crawler.curate_urls([1, 2010], [34, 2012])
    columns = ['date_time', 'matchday', 'home_team', 'home_score',
               'guest_score', 'guest_team', 'season']
    m_empty = pd.DataFrame([], columns=columns)  # empty df to fill
    un_m_empty = pd.DataFrame([], columns=columns)
    test_matches = crawler.crawl_openligadb(test_urls, m_empty, un_m_empty, csv_file)[
        1]
    test_matches = crawler.convertdf(test_matches)
    os.remove(csv_file)
    '''

    data = crawler.fetch_data([1, 2010], [34, 2012])
    test_next_day = crawler.fetch_data([0, 0], [0, 0])

    assert isinstance(data, pd.DataFrame)
    assert all(ptypes.is_numeric_dtype(data[col])
               for col in ['home_score', 'guest_score'])
    assert all(ptypes.is_string_dtype(data[col])
               for col in ['home_team', 'guest_team'])
    assert ptypes.is_datetime64_any_dtype(data['date_time'])
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.season >= 2010).all()
    assert (data.season <= 2012).all()
    assert (0 < data.matchday).all()
    assert (35 > data.matchday).all()
    assert data['matchday'].head(130).is_monotonic_increasing
    assert (len(data.columns) == 7)
    assert data['season'].is_monotonic_increasing
    #pd.testing.assert_frame_equal(test_matches.reset_index(drop=True),
     #                             data.reset_index(drop=True))
    assert (len(data) != 0)
    # testing test_next_day
    assert isinstance(test_next_day, pd.DataFrame)
    assert all(ptypes.is_numeric_dtype(test_next_day[col])
               for col in ['home_score', 'guest_score'])
    assert all(ptypes.is_string_dtype(test_next_day[col])
               for col in ['home_team', 'guest_team'])
    assert ptypes.is_datetime64_any_dtype(test_next_day['date_time'])
    assert (test_next_day.home_score >= -1).all()
    assert (test_next_day.guest_score >= -1).all()
    assert (0 < test_next_day.matchday).all()
    assert (35 > test_next_day.matchday).all()
    assert test_next_day['matchday'].head(60).is_monotonic_increasing
    assert (len(test_next_day.columns) == 7)
    assert test_next_day['season'].is_monotonic_increasing
    assert (len(test_next_day) != 0)


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
