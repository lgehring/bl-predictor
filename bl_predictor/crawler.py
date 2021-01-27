"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""
import datetime
import json

import pandas as pd
import requests
import os


# Initialize matches dataframe that will be filled and returned


def fetch_data(start_date, end_date):
    """
    Query sample data from "the internet"
    and return as pd.DataFrame.
    You can get the unfinished matches of the current season by entering 0
    for both start_date and end_date.
    Data gets stored into csv file. After download data is taken from here.

    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :return: Dataframe that contains all the matches between
        start_date and end_date.
    """
    # get path of csv file
    crawler_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(crawler_path)
    csv_file = os.path.join(directory_path, 'crawled_data.csv')
    # empty df to fill
    columns = ['date_time', 'matchday', 'home_team', 'home_score',
               'guest_score', 'guest_team', 'season']
    matches_empty = pd.DataFrame([], columns=columns)
    unfin_m_empty = pd.DataFrame([], columns=columns)
    current_d = get_current_date()

    if start_date == [0, 0] == end_date:
        urls = curate_urls([current_d[0] + 1, current_d[1]],
                           [34, current_d[1]])
        unfinished_matches = crawl_openligadb(urls, unfin_m_empty,
                                              matches_empty, csv_file)[0]
        unfinished_m = convertdf(unfinished_matches)
        return unfinished_m
    else:
        dataframe = fetch_data_helper(start_date, end_date, csv_file,
                                      current_d, unfin_m_empty, matches_empty)
        return dataframe


def fetch_data_helper(start_date, end_date, csv_file, current_d, unfin_m_empty,
                      matches_empty):
    """
    Helps fetch data to get missing data and takes data from the csv
    file in the correct time range.
    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :param csv_file: path or going to be to path to the csv file
    :param list [int] current_d: current date [matchday, season]
    :param unfin_m_empty: empty dataframe
    :param matches_empty: empty dataframe
    :return: Dataframe with matches from start_date until end_date
    """
    # last csv date or [1, 2004]
    csv_last_d = get_csv_last_date(csv_file)
    # if our end date if before today
    if current_d[1] > end_date[1] or (
            current_d[1] == end_date[1]
            and current_d[0] > end_date[0]):
        # if our end date is later than the csv file goes
        if end_date[1] > csv_last_d[1] or (
                end_date[1] == csv_last_d[1]
                and end_date[0] > csv_last_d[0]):
            # get the missing or all data until today and take matches in
            # our time range
            urls = curate_urls(csv_last_d, current_d)
            crawl_openligadb(urls, unfin_m_empty, matches_empty, csv_file)
            dataframe = take_data(start_date, end_date, csv_file)
        else:
            # otherwise just take matches in our time range
            dataframe = take_data(start_date, end_date, csv_file)
    # otherwise our end_date is in the future. Exp. Slider can give
    # until [34, current year]
    else:
        # if today later than our csv file
        if current_d[1] > csv_last_d[1] \
                or (
                current_d[1] == csv_last_d[1]
                and current_d[0] > csv_last_d[0]):
            # get all missing data
            url = curate_urls(csv_last_d, current_d)
            crawl_openligadb(url, unfin_m_empty, matches_empty, csv_file)
            # and take needed matches after checking if start date isn´t in
            # the future
            if start_date <= current_d:
                dataframe = take_data(start_date, current_d, csv_file)
            else:
                dataframe = take_data([1, current_d[1]], current_d,
                                      csv_file)
        # otherwise we have all data
        else:
            if start_date <= current_d:
                dataframe = take_data(start_date, end_date, csv_file)
            else:
                dataframe = take_data([1, current_d[1]], current_d,
                                      csv_file)
    return dataframe


def get_current_date():
    """
    Checks if there is data for the current year. If not, the year before is
    the current season. Exp. any match in 2021 before may is in the season
    2020.
    :return: current date [day, season]
    """
    current_year = datetime.date.today().year
    current_year_has_no_data = data_not_exist(
        curate_urls([1, current_year], [1, current_year]))
    if current_year_has_no_data:
        current_year = datetime.date.today().year - 1
    day = 0
    for day in range(34, 1, -1):
        if matches_exists(
                curate_urls([day, current_year], [day, current_year])):
            day = day
            break
    return [day, current_year]


def get_csv_last_date(csv_file):
    """
    This function finds the season and matchday of the last match in the csv,
    if a file exists. If there is no file yet it returns [1, 2004].
    :return: [matchday, season]
    """
    if os.path.exists(csv_file):
        this_df = pd.read_csv(csv_file)
        end_date_csv = [int(this_df['matchday'].iloc[-1]),
                        int(this_df['season'].iloc[-1])]
    else:
        end_date_csv = [1, 2004]
    return end_date_csv


def take_data(start, end, csv_file):
    """
    Takes data from start to end out of the csv file.
    :param csv_file: path to csv file
    :param list[int] start: Starting Date
    :param list[int] end: Ending Date
    :return: Dataframe
    """
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df = convertdf(df)
        # take all data with in these seasons(each included)
        data = df[(df['season'] >= start[1]) & (df['season'] <= end[1])]
        # take all except days in the first season, that are
        # before our first matchday
        data_cor_start = data[
            (data['season'] != start[1]) | (data['matchday'] >= start[0])]
        # same thing with last season, this time all that are after our last
        # matchday
        data_cor_end = data_cor_start[
            (data_cor_start['season'] != end[1])
            | (data['matchday'] <= end[0])]
        return data_cor_end


def convertdf(dataframe):
    """
    Takes a dataframe and converts the elements into types
    that can be more useful.

    :param DataFrame dataframe: DataFrame
    :return: The dataframe with converted elements
    """
    dataframe['home_score'] = dataframe['home_score'].astype('int')
    dataframe['matchday'] = dataframe['matchday'].astype('int')
    dataframe['guest_score'] = dataframe['guest_score'].astype('int')
    dataframe['home_team'] = dataframe['home_team'].astype('str')
    dataframe['guest_team'] = dataframe['guest_team'].astype('str')
    dataframe['date_time'] = dataframe['date_time'].astype('datetime64')
    dataframe['season'] = dataframe['season'].astype('int')
    return dataframe


def incorrect_dates(start_date, end_date):
    """
    Checks if the submitted dates are correct.

    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :returns: Result whether or not the dates are incorrect as type boolean
    """
    days = [start_date[0], end_date[0]]
    seasons = [start_date[1], end_date[1]]
    statement_day = False
    statement_season = False
    for date in days:
        # each season has 35 game days
        statement_day = (0 == date) or (date > 35) or statement_day
    for season in seasons:
        first_recorded_bl_year = 2003  # 1964 openliga has only new matches
        statement_season = (first_recorded_bl_year > season
                            or season > datetime.datetime.now().year
                            or statement_season)
    return statement_day or statement_season


def curate_urls(start_date, end_date):
    """
    A function that curates the urls for the data in the given time range.

    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :return: List of urls of matches from each game day in the given
     time period
    """
    start_season = start_date[1]
    end_season = end_date[1]
    end_day = end_date[0]
    start_day = start_date[0]
    urls = []
    if incorrect_dates(start_date, end_date):
        raise ValueError("there has been no match on this day."
                         "Matches are 34 days per season from 1963 to "
                         "2020")
    # dates are in same year
    if end_season == start_season:
        for day in list(range(start_day, end_day + 1)):
            urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                     + str(start_season) + '/' + str(day)]
    else:
        # starting date doesn't begin with 1.matchday
        if start_day != 1:
            for day in list(range(start_day, 35)):
                urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                         + str(start_season) + '/' + str(day)]
            for season in range(start_season + 1, end_season):
                urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                         + str(season)]
        # if it does start on 1. matchday we take the whole season and add
        # seasons between dates
        else:
            for season in range(start_season, end_season):
                urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                         + str(season)]
        # adding last season we want to look at
        if end_day != 34:
            for day in list(range(1, end_day + 1)):
                urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                         + str(end_season) + '/' + str(day)]
        else:
            urls += ['https://api.openligadb.de/getmatchdata/bl1/'
                     + str(end_season)]
    return urls


def data_not_exist(url):
    """
    Checks if data exists for this url.

    :param url: url of a day or season
    :return: Result as type boolean
    """
    to_crawl = url

    while to_crawl:
        current_url = to_crawl.pop(0)
        response = requests.get(current_url)
        json_response = response.content
        json_response = json.loads(json_response)

        if not json_response:
            return True
        return False


def matches_exists(url):
    """
    Checks if there is information to this match. Exp. if the season began but
    the match is tomorrow.

    :param url: url of the match
    :return: Result as boolean
    """
    to_crawl = url
    while to_crawl:
        current_url = to_crawl.pop(0)
        r = requests.get(current_url)
        json_response = r.content
        json_response = json.loads(json_response)
        for game in range(len(json_response)):
            if json_response[game]['matchIsFinished']:
                return True
            else:
                return False


def crawl_openligadb(urls, unfinished_matches, matches, csv_file):
    """
    Crawls through the given urls
    and safes the useful data in the dataframe 'matches'. The Data of an
    unfinished season is saved in 'unfinished_matches'.

    :param csv_file: path to csv file
    :param matches: empty dataframe
    :param unfinished_matches: empty dataframe
    :param list[str] urls: List with urls from matches and seasons in our
     time range.
    """

    to_crawl = urls
    while to_crawl:
        current_url = to_crawl.pop(0)
        r = requests.get(current_url)
        json_response = r.content
        json_response = json.loads(json_response)

        for game in range(len(json_response)):  # all matches in scrape
            # appends response item-array to matches, !ORDER SENSITIVE!
            if json_response[game]['matchIsFinished']:
                matches_length = len(matches)
                matches.loc[matches_length] = [
                    json_response[game]['matchDateTime'],  # match_date_time
                    json_response[game]['group']["groupOrderID"],  # matchday
                    json_response[game]['team1']['teamName'],  # home_t
                    json_response[game]['matchResults'][0]['pointsTeam1'],  # h
                    json_response[game]['matchResults'][0]['pointsTeam2'],  # g
                    json_response[game]['team2']['teamName'],  # guest_t
                    current_url[43:47]  # season
                ]
            else:
                unfinished_matches_length = len(unfinished_matches)
                unfinished_matches.loc[unfinished_matches_length] = [
                    json_response[game]['matchDateTime'],  # match_date_time
                    json_response[game]['group']["groupOrderID"],  # matchday
                    json_response[game]['team1']['teamName'],  # home_t
                    -1,  # h
                    -1,  # g
                    json_response[game]['team2']['teamName'],  # guest_t
                    current_url[43:47]  # season
                ]
    # if matches has been filled in this function
    if not matches.empty:
        if os.path.exists(csv_file):
            matches.to_csv(csv_file, mode='a',
                           index=False, header=False)

        else:
            matches.to_csv(csv_file, index=False)
    return [unfinished_matches, matches]
