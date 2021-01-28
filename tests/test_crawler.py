# Use this file to test your crawler.

import pandas as pd
import pandas.api.types as ptypes
import pytest

import os
from pathlib import Path
from bl_predictor import crawler


@pytest.mark.parametrize(
    "start, end, exp_start, exp_end, remove",
    [

        ([32, 2019], [2, 2020], [32, 2019], [2, 2020], "no"),
        ([22, 2020], [1, 2021], [1, 2020], [34, 2020], "no"),
        ([18, 2020], [1, 2021], [18, 2020], [18, 2020], "no"),
        ([32, 2019], [2, 2020], [32, 2019], [2, 2020], "yes"),
        ([22, 2020], [1, 2021], [1, 2020], [34, 2020], "yes"),
        ([18, 2020], [1, 2021], [18, 2020], [18, 2020], "yes"),
    ])
def test_fetch_data(start, end, exp_start, exp_end, remove):
    dir_path = Path(__file__).parents[1]
    csv_file = os.path.join(dir_path, "bl_predictor/crawled_data.csv")
    if remove == "yes":
        os.remove(csv_file)

    data = crawler.fetch_data(start, end)

    assert isinstance(data, pd.DataFrame)
    assert all(ptypes.is_numeric_dtype(data[col])
               for col in ['home_score', 'guest_score'])
    assert all(ptypes.is_string_dtype(data[col])
               for col in ['home_team', 'guest_team'])
    assert ptypes.is_datetime64_any_dtype(data['date_time'])
    assert (data.home_score >= 0).all()
    assert (data.guest_score >= 0).all()
    assert (data.season >= exp_start[1]).all()
    assert (data.season <= exp_end[1]).all()
    assert (0 < data.matchday).all()
    assert (35 > data.matchday).all()
    assert (len(data.columns) == 7)
    assert data['season'].is_monotonic_increasing
    assert (len(data) != 0)


@pytest.mark.parametrize(
    "start, end",
    [
        ([0, 0], [0, 0])
    ])
def test_fetch_data_next_day(start, end):
    test_next_day = crawler.fetch_data(start, end)
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
         "https://api.openligadb.de/getmatchdata/bl1/2015"),

    ])
def test_test_curate_urls(start_date, end_date, index_of_url, expected):
    urls = crawler.curate_urls(start_date, end_date)
    if index_of_url is not None:
        assert urls[index_of_url] == expected
    else:
        assert urls == expected


def test_curate_urls_exc():
    pytest.raises(ValueError, crawler.curate_urls, [0, 2014], [8, 2014])


@pytest.mark.parametrize(
    "start, end, expected",
    [
        (crawler.get_current_date(), crawler.get_current_date(), False),
        ([12, 2012], [12, 2012], False),
    ])
def test_data_exists(start, end, expected):
    url = crawler.curate_urls(start, end)
    result = crawler.data_not_exist(url)
    assert result == expected


@pytest.mark.parametrize(
    "start, end, expected",
    [
        (crawler.get_current_date(), crawler.get_current_date(), True),
        ([12, 2012], [12, 2012], True),
        ([crawler.get_current_date()[0] + 1, crawler.get_current_date()[1]],
         [crawler.get_current_date()[0] + 1, crawler.get_current_date()[1]],
         False)
    ])
def matches_exists(start, end, expected):
    url = crawler.curate_urls(start, end)
    result = crawler.data_not_exist(url)
    assert result == expected
