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
columns = ['date_time', 'matchday', 'home_team', 'home_score', 'guest_score',
           'guest_team']
matches = pd.DataFrame([], columns=columns)  # empty df to fill
unfinished_matches = pd.DataFrame([], columns=columns)


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
    current_date = get_current_date()
    df = get_df(end_date, current_date)
    # return wanted data
    if start_date == [0, 0] == end_date:
        convertdf(unfinished_matches)
        return unfinished_matches
    else:
        dataframe = take_data(start_date, end_date, df)
        return dataframe


def get_df(end_date, current_date):
    """
    Takes data from csv file, concat the missing data and saves new data.
    If there is no csv file, the function will take all data from the
    "internet" and save it in a csv file.

    :param list[int] end_date: Until when the User wants the data
    :param list[int] current_date: the current season [34, season]
    :return: Dataframe with all documented matches
    """
    # read csv file, if not empty
    if os.path.exists("crawled_data.csv"):
        matches_ex_data = pd.read_csv("crawled_data.csv")
        # need to convert to get the right data types.
        matches_ex_data = convertdf(matches_ex_data)
        df_ending_date = get_last_date(matches_ex_data)
        get_data_from = [df_ending_date[0] + 1, df_ending_date[1]]
        have_all_data = 0 < end_date[1] <= df_ending_date[1]
        if have_all_data:
            df = matches_ex_data
        else:
            urls = curate_urls(get_data_from, current_date)
            crawl_openligadb(urls)
            convertdf(matches)
            # append new data to csv file
            matches.to_csv('crawled_data.csv', mode='a', header=False)
            df = pd.concat([matches_ex_data, matches], axis=0)
    else:
        # if there is no stored data, download all of it
        urls = curate_urls([1, 2004],
                           current_date)  # index error with 2003
        crawl_openligadb(urls)
        # save matches in csv file
        convertdf(matches)
        df = matches
        matches.to_csv('crawled_data.csv', mode='a', index=False)
    return df


def get_current_date():
    """
    Checks if there is data for the current year. If not, the year before is
    the currents season. Exp. any match in 2021 before may is in the season
    2020.

    :return: current season [34, season]
    """
    current_year = datetime.date.today().year
    current_year_has_no_data = data_exists(
        curate_urls([1, current_year], [1, current_year]))
    if current_year_has_no_data:
        current_year = datetime.date.today().year - 1
    return [34, current_year]


def get_last_date(df):
    # Todo with matchday?
    """
    Gives matchday and season of the last match in the df.

    :param df: Dataframe
    :return: Last date [matchday,season]
    """
    # assumption: 1. Bundesliga does not go longer than until may.
    # end date from existing data [matchday,season]
    month = df['date_time'].iloc[-1].month
    if month <= 5:
        end_date_df = [df['matchday'].iloc[-1],
                       df['date_time'].iloc[-1].year - 1]
    else:
        end_date_df = [df['matchday'].iloc[-1],
                       df['date_time'].iloc[-1].year]
    return end_date_df


def take_data(start_date, ending_date, df):
    """
      Takes data from start_date until ending_date from the dataframe.

      :param start_date: beginning of time range
      :param ending_date: ending of time range
      :param df: Dataframe with all matches.
      :return: Dataframe from first until last matchday in season(s)
       start_date/ending_date.
      """
    df_ending = get_last_date(df)
    start_day = start_date[0]
    end_day = ending_date[0]
    first_half_of_s = False

    start_year = str(start_date[1])
    if ending_date[1] < df_ending[1]:
        if end_day < 18:
            first_half_of_s = True
            end_year = str(ending_date[1])
        else:
            end_year = str(ending_date[1] + 1)
    else:
        if df_ending[1] < 18:
            end_year = str(df_ending[1])
            first_half_of_s = True
        else:
            end_year = str(df_ending[1])

    # selecting between years
    data = df[(df['date_time'].dt.strftime('%Y') > start_year)
              & (df['date_time'].dt.strftime('%Y') < end_year)]

    # selecting days in first year
    data_days1 = df[(df['date_time'].dt.strftime('%Y') == start_year)
                    & (df['matchday'] >= start_day)
                    & (df['date_time'].dt.strftime('%m') != "06")
                    & (df['date_time'].dt.strftime('%m') != "05")
                    & (df['date_time'].dt.strftime('%m') != "04")
                    & (df['date_time'].dt.strftime('%m') != "03")
                    & (df['date_time'].dt.strftime('%m') != "02")
                    & (df['date_time'].dt.strftime('%m') != "01")]
    print(data_days1)
    # select last days
    # in first year of the season?
    if not first_half_of_s:
        # select last days with out post seasonal matches
        data_days2 = df[
            (df['date_time'].dt.strftime('%Y') == end_year)
            & (df['matchday'] <= end_day)
            & (df['date_time'].dt.strftime('%Y') == end_year)
            & (df['date_time'].dt.strftime('%m') != "12")
            & (df['date_time'].dt.strftime('%m') != "11")
            & (df['date_time'].dt.strftime('%m') != "10")
            & (df['date_time'].dt.strftime('%m') != "09")
            & (df['date_time'].dt.strftime('%m') != "08")
            & (df['date_time'].dt.strftime('%m') != "07")]
    else:
        # same year? and not same year?
        if ending_date[1] == start_date[1]:
            data_days2 = \
                data_days1[
                    (data_days1['date_time'].dt.strftime('%Y') == end_year)
                    & (df['matchday'] <= end_day)]
        else:
            data_days2 = df[(df['date_time'].dt.strftime('%Y') == end_year)
                            & (df['matchday'] <= end_day)]
    return pd.concat[data_days1, data, data_days2]


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


def crawl_openligadb(urls):
    """
    Crawls through the given urls
    and safes the useful data in the dataframe 'matches'. The Data of an
    unfinished season is saved in 'unfinished_matches'.

    :param list[str] urls: List with urls from matches and seasons in our
     time range.
    """
    to_crawl = urls
    while to_crawl:
        current_url = to_crawl.pop(0)
        r = requests.get(current_url)
        json_response = r.content
        json_response = json.loads(json_response)
        # checks if there is any data yet for this/these day/s
        # important for fetch_data
        if not json_response:
            return True

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
                    json_response[game]['team2']['teamName']  # guest_t
                ]
            else:
                unfinished_matches_length = len(unfinished_matches)
                unfinished_matches.loc[unfinished_matches_length] = [
                    json_response[game]['matchDateTime'],  # match_date_time
                    json_response[game]['group']["groupOrderID"],  # matchday
                    json_response[game]['team1']['teamName'],  # home_t
                    -1,  # h
                    -1,  # g
                    json_response[game]['team2']['teamName']  # guest_t
                ]
