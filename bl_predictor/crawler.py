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
    columns = ['date_time', 'matchday', 'home_team', 'home_score',
               'guest_score', 'guest_team', 'season']
    matches_empty = pd.DataFrame([], columns=columns)  # empty df to fill
    unfinished_matches_empty = pd.DataFrame([], columns=columns)

    current_date = get_current_date()
    if start_date == [0, 0] == end_date:
        urls = curate_urls([current_date[0] + 1, current_date[1]],
                           [34, current_date[1]])
        unfinished_matches = crawl_openligadb(urls, unfinished_matches_empty,
                                              matches_empty)[0]
        unfinished_m = convertdf(unfinished_matches)
        return unfinished_m
    else:
        # letzte csv datum oder 2004
        csv_last_date = get_csv_last_date()
        # wenn heute später ist als unser enddatum
        if current_date[1] > end_date[1] or (
                current_date[1] == end_date[1]
                and current_date[0] > end_date[0]):
            # wenn unser enddatum später ist als csv geht
            if end_date[1] > csv_last_date[1] or (
                    end_date[1] == csv_last_date[1]
                    and end_date[0] > csv_last_date[0]):
                # hole daten von csv datum bis unser end datum
                urls = curate_urls(csv_last_date, current_date)
                crawl_openligadb(urls, unfinished_matches_empty, matches_empty)
                dataframe = take_data(start_date, end_date)
            else:
                # sonst haben wir alle Daten, Nimm daten von Start bis ende
                dataframe = take_data(start_date, end_date)
        # sonst, also wenn unser end datum später ist als unser heute
        else:
            # wenn heute später ist als csv letztes datum
            if current_date[1] > csv_last_date[1] \
                    or (
                    current_date[1] == csv_last_date[1]
                    and current_date[0] > csv_last_date[0]):
                # hole alle daten von csv (viel. 2004) bis heute
                crawl_openligadb(curate_urls(csv_last_date, current_date))
                if start_date <= current_date:
                    # hole dann daten von unserem start bis heute,
                    # wenn start vor heute ist
                    dataframe = take_data(start_date, current_date)
                else:
                    dataframe = take_data([1, current_date[1]], current_date)
            # sonst, also wenn heute in csv ist
            else:
                # Nimm Daten von start bis ende
                if start_date <= current_date:
                    dataframe = take_data(start_date, end_date)
        return dataframe


def get_current_date():
    """
    Checks if there is data for the current year. If not, the year before is
    the current season. Expample: any match in 2021 before may is in the season
    2020.
    :return: current date [day, season]
    """
    current_year = datetime.date.today().year
    current_year_has_no_data = data_exists(
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


def get_csv_last_date():
    """
    This function finds the season and matchday of the last match in the csv,
    if a file exists. If there is no file yet it returns [1, 2004].
    :return: [matchday, season]
    """
    if os.path.exists("crawled_data.csv"):
        this_df = pd.read_csv("crawled_data.csv")
        end_date_csv = [int(this_df['matchday'].iloc[-1]),
                        int(this_df['season'].iloc[-1])]
    else:
        end_date_csv = [1, 2004]
    return end_date_csv


def take_data(start, end):
    """
    Takes data from start to end out of the csv file.
    :param list[int] start: Starting Date
    :param list[int] end: Ending Date
    :return: Dataframe
    """
    if os.path.exists("crawled_data.csv"):
        df = pd.read_csv("crawled_data.csv")
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
        # if it does start on 1. matchday we take the whole season and add
        # seasons between dates
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


def data_exists(url):
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


def crawl_openligadb(urls, unfinished_matches, matches):
    """
    Crawls through the given urls
    and safes the useful data in the dataframe 'matches'. The Data of an
    unfinished season is saved in 'unfinished_matches'.

    :param matches:
    :param unfinished_matches:
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
        crawler_path = os.path.abspath(__file__)
        directory_path = os.path.dirname(crawler_path)
        csv_file = os.path.join(directory_path, 'crawled_data.csv')
        if os.path.exists("crawled_data.csv"):
            matches.to_csv(csv_file, mode='a',
                           index=False, header=False)

        else:
            matches.to_csv(csv_file, mode='a',
                           index=False)
    return [unfinished_matches, matches]
