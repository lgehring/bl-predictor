# Use this file to test your crawler.

import pandas as pd
import pandas.api.types as ptypes
import pytest

import teamproject.crawler as crawler


def test_fetch_data():

    data = crawler.fetch_data([1, 2010], [12, 2011])
    test_urls = crawler.curate_urls([1, 2010], [12, 2011])
    columns = ['date_time', 'matchday', 'home_team', 'home_score',
               'guest_score', 'guest_team', 'season']
    m_empty = pd.DataFrame([], columns=columns)  # empty df to fill
    un_m_empty = pd.DataFrame([], columns=columns)
    test_matches = crawler.crawl_openligadb(test_urls, m_empty, un_m_empty)[1]

    assert isinstance(data, pd.DataFrame)
    assert all(ptypes.is_numeric_dtype(data[col])
               for col in ['home_score', 'guest_score'])
    assert all(ptypes.is_string_dtype(data[col])
               for col in ['home_team', 'guest_team'])
    assert ptypes.is_datetime64_any_dtype(data['date_time'])
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.season >= 2010).all()
    #Todo change to 2015
    assert (data.season <= 2011).all()
    assert (0 < data.matchday).all()
    assert (35 > data.matchday).all()
    #Todo change to 130
    assert data['matchday'].head(30).is_monotonic_increasing
    assert (len(data.columns) == 7)
    assert data['season'].is_monotonic_increasing
    # matches might have indices that data does not have
    #pd.set_option('display.max_rows', None)
    #print("testmacthes \n", data)

    # Todo data changes depending wether or not the file exists befor
    pd.testing.assert_frame_equal(test_matches.reset_index(drop=True), data.reset_index(drop=True))
#Todo delete
test_fetch_data()


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
