"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""

import datetime
import json

import pandas as pd
import requests

# Initialize matches dataframe that will be filled and returned
columns = ['date_time', 'matchday', 'home_team', 'home_score', 'guest_score',
           'guest_team']
matches = pd.DataFrame([], columns=columns)  # empty df to fill
unfinished_matches = pd.DataFrame([], columns=columns)


def fetch_data(start_date, end_date):
    """
    Query sample data from "the internet" and return as pd.DataFrame.
    """

    # initialize and start crawling

    wanted_urls = curate_urls(start_date, end_date)
    crawl_openligadb(wanted_urls)

    # covert DataFrame columns from object to int
    if start_date == end_date == (0, 0):
        convertdf(unfinished_matches)
        return unfinished_matches
    else:
        convertdf(matches)
        return matches


def convertdf(dataframe):
    dataframe['home_score'] = dataframe['home_score'].astype('int')
    dataframe['matchday'] = dataframe['matchday'].astype('int')
    dataframe['guest_score'] = dataframe['guest_score'].astype('int')
    dataframe['home_team'] = dataframe['home_team'].astype('str')
    dataframe['guest_team'] = dataframe['guest_team'].astype('str')
    dataframe['date_time'] = dataframe['date_time'].astype('datetime64')


def incorrect_dates(start_date, end_date):
    """Were any matches on those days?"""
    days = [start_date[0], end_date[0]]
    seasons = [start_date[1], end_date[1]]
    statement_day = False
    statement_season = False
    for date in days:
        # each season has 35 gamedays
        statement_day = 0 == date or date > 35 or statement_day
    for season in seasons:
        # first season was in 1963
        statement_season = (1963 > season
                            or season > datetime.datetime.now().year
                            or statement_season)
    return statement_day or statement_season


def dict_of_gamedays(game_days, start_season, start_day, end_season, end_day):
    """
    :param game_days: {}
    :param start_season: int
    :param start_day: int
    :param end_season: int
    :param end_day: int
    :return: dictionary of seasons and gamedays
    """
    seasons_between_dates = end_season - start_season
    if seasons_between_dates == 0:
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
    Expects a timeperiod. Gameday and season as an array, in that order.

    :param start_date: [int]
    :param end_date: [int]
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
    game_days = dict_of_gamedays({}, start_season, start_day, end_season,
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


def crawl_openligadb(url):
    """Crawls through the given urls
    and safes the useful data in the dataframe 'matches'.
    Parameters
    __________
    url : 'list' ['str']
        List with URLs to scrape.
    """
    to_crawl = url

    while to_crawl:
        current_url = to_crawl.pop(0)
        r = requests.get(current_url)
        jsonresponse = r.content
        jsonresponse = json.loads(jsonresponse)

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
                    jsonresponse[game]['team2']['teamName']  # guest_t]
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
