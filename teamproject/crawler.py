"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""
import datetime
import json
import os

import pandas as pd
import requests

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

    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :return: Dataframe that contains all the matches between
        start_date and end_date.
    """

    # finding current/last season, by checking if there is data for this year
    current_year = current_season()
    df = pd.DataFrame([], columns=columns)

    # get data from stored data, if not empty
    # read all already present data from csv
    # each are type Dataframe
    if os.path.exists("crawled_data.csv"):
        matches_ex_data = pd.read_csv("crawled_data.csv")
        matches_ex_data = convertdf(matches_ex_data)
        df_ending_date = get_last_date(matches_ex_data)
        have_all_data = end_date[1] <= df_ending_date[1]
        if have_all_data:
            df = matches_ex_data
        else:

            urls = curate_urls(df_ending_date, [34, current_year])
            crawl_openligadb(urls)
            convertdf(matches)
            # append new data to csv file
            matches.to_csv('crawled_data.csv', mode='a', header=False)
            df = pd.concat([matches_ex_data, matches], axis=0)
    else:
        # if there is no stored data, download all of it
        urls = curate_urls([1, 2004],
                           [34, current_year])  # Todo index error with 2003
        crawl_openligadb(urls)
        #save macthes in csv file
        convertdf(matches)
        matches.to_csv('crawled_data.csv', index=False)
        take_data(start_date, end_date, matches)
    # return wanted data
    if start_date == [0, 0] == end_date:
        convertdf(unfinished_matches)
        # data saved as csv file
        return unfinished_matches
    else:
        dataframe = take_data(start_date, end_date, df)
        return dataframe


def current_season():
    current_year = datetime.date.today().year
    current_year_has_no_data = False or crawl_openligadb(
        curate_urls([1, current_year], [1, current_year]))
    if current_year_has_no_data:
        current_year = datetime.date.today().year - 1
    return current_year


def get_last_date(df):
    """
    This function finds when the first und last match is of df

    :param df: Dataframe
    :return:ending date as list. [day,year]
    """
    # end date from existing data [matchday,year], -15 to only
    # have the year from 'date_time'
    print(type(df['date_time'].iloc[-1]))
    end_date_df = [df['matchday'].iloc[-1],
                   df['date_time'].iloc[-1].year]
    print("enddate", end_date_df)
    return end_date_df


def take_data(start_date, ending_date, df):
    data = df[start_date[1] <= df['date_time'].year <= ending_date[1]]
    print("data", data)
    return data


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
        # each season has 35 gamedays
        statement_day = 0 == date or date > 35 or statement_day
    for season in seasons:
        first_recorded_bl_year = 2003  # 1964 openliga has only new matches
        statement_season = (first_recorded_bl_year > season
                            or season > datetime.datetime.now().year
                            or statement_season)
    return statement_day or statement_season


def dict_of_game_days(game_days, start_season, start_day, end_season, end_day):
    """
    Constructs a dictionary with all seasons and their matchdays in the
    timerange we need.

    :param dict game_days: empty dictionary
    :param int start_season: starting season
    :param int start_day: starting matchday
    :param int end_season: ending season
    :param int end_day:  ending matchday
    :return: filled dictionary, with seasons and days in given timerange.
     The keys are the seasons. These are combined with their matchdays as list.
     An empty list is a full season.
    """
    if end_season == start_season:
        game_days = {
            start_season: list(range(start_day, end_day + 1))}
    else:
        if start_day != 1:
            game_days = {start_season: list(range(start_day, 35))}
        else:
            game_days[start_season] = []
        # adding seasons between the dates
        for seasons in range(start_season + 1, end_season):
            game_days[seasons] = []
        # adding last season we want to look at
        if end_day != 34:
            game_days[end_season] = list(range(1, end_day + 1))
        else:
            game_days[end_season] = []
    return game_days


def curate_urls(start_date, end_date):
    """
    A function that curates the urls for the data in the given timerange.

    :param list [int] start_date: [matchday, year]
    :param list [int] end_date: [matchday, year]
    :return: List of urls of matches from each gameday in the given
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
    # Dictionary with season as key combined with number of gamedays as
    # list
    game_days = dict_of_game_days({}, start_season, start_day, end_season,
                                  end_day)

    # make list of urls for seasons and days
    for season in game_days:
        if game_days[season]:
            for day in game_days[season]:
                url = 'https://api.openligadb.de/getmatchdata/bl1/' + \
                      str(season) + '/' + str(day)
                urls += [url]
        else:
            url = 'https://api.openligadb.de/getmatchdata/bl1/' + \
                  str(season)
            urls += [url]
    return urls


def crawl_openligadb(urls):
    """
    Crawls through the given urls
    and safes the useful data in the dataframe 'matches'. The Data of an
    unfinished season is saved in 'unfinished_matches'.

    :param list[str] urls: List with urls from matches and seasons in our
     timerange.
    """
    to_crawl = urls

    while to_crawl:
        current_url = to_crawl.pop(0)
        r = requests.get(current_url)
        jsonresponse = r.content
        jsonresponse = json.loads(jsonresponse)
        # checks if there is any data yet for this/these day/s
        # important for fetch_data
        if not jsonresponse:
            return True
        for game in range(len(jsonresponse)):  # all matches in scrape
            # appends response item-array to matches, !ORDER SENSITIVE!
            if jsonresponse[game]['matchIsFinished']:
                matches_length = len(matches)

                matches.loc[matches_length] = [
                    jsonresponse[game]['matchDateTime'],  # match_date_time
                    jsonresponse[game]['group']["groupOrderID"],  # matchday
                    jsonresponse[game]['team1']['teamName'],  # home_t
                    jsonresponse[game]['matchResults'][0]['pointsTeam1'],  # h
                    jsonresponse[game]['matchResults'][0]['pointsTeam2'],  # g
                    jsonresponse[game]['team2']['teamName']  # guest_t
                ]
            else:
                unfinished_matches_length = len(unfinished_matches)
                unfinished_matches.loc[unfinished_matches_length] = [
                    jsonresponse[game]['matchDateTime'],  # match_date_time
                    jsonresponse[game]['group']["groupOrderID"],  # matchday
                    jsonresponse[game]['team1']['teamName'],  # home_t
                    -1,  # h
                    -1,  # g
                    jsonresponse[game]['team2']['teamName']  # guest_t]
                ]
