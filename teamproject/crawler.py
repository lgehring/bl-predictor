"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""

import datetime
import json

import pandas as pd
import requests

# Initialize matches dataframe that will be filled and returned
columns = ['date_time', 'home_team', 'home_score', 'guest_score',
           'guest_team']
matches = pd.DataFrame([], columns=columns)  # empty df to fill
unfinished_matches = pd.DataFrame([], columns=columns)
urls = []


def fetch_data(start_date, end_date):
    """
    Query sample data from "the internet" and return as pd.DataFrame.
    """
    global urls
    curate_urls(start_date, end_date)
    # initialize and start crawling

    crawl_openligadb(urls)

    urls = []

    # covert DataFrame columns from object to int
    if start_date[1] == end_date[1]:
        convertdf(unfinished_matches)
        return unfinished_matches
    else:
        convertdf(matches)
        return matches


def convertdf(dataframe):
    dataframe['home_score'] = dataframe['home_score'].astype('int')
    dataframe['guest_score'] = dataframe['guest_score'].astype('int')
    dataframe['home_team'] = dataframe['home_team'].astype('str')
    dataframe['guest_team'] = dataframe['guest_team'].astype('str')
    dataframe['date_time'] = dataframe['date_time'].astype('datetime64')


def incorrect_dates(start_date, end_date):
    """Were any matches on those days?"""
    days = [start_date[0], end_date[0]]
    seasons = [start_date[1], end_date[1]]
    statement_d = False
    statement_s = False
    for date in days:
        # each season has 35 gamedays
        statement_d = 0 == date or date > 35 or statement_d
    for season in seasons:
        # first season was in 1963
        statement_s = (1963 > season
                       or season > datetime.datetime.now().year
                       or statement_s)
    return statement_d or statement_s


def curate_urls(start_date, end_date):
    """
    Expects a timeperiod. Gameday and season as an array, in that order.

    :param start_date: [int]
    :param end_date: [int]
    :return: List of urls of matches from each gameday in the given
            time period
    """
    global urls
    seasons_time_range = end_date[1] - start_date[1]

    if incorrect_dates(start_date, end_date):
        raise ValueError("there has been no match on this day."
                         "Matches are 34 days per season from 1963 to "
                         "2020")
    # Dictionary with season as key combined with number of gamedays as
    # list
    if seasons_time_range == 0:
        days = {
            start_date[1]: list(range(start_date[0], end_date[0] + 1))}
    else:
        days = {start_date[1]: list(range(start_date[0], 35))}
        # adding seasons between the dates
        for x in range(start_date[1] + 1, end_date[1]):
            days[x] = list(range(1, 35))
        # adding last season we want to look at
        days[end_date[1]] = list(range(1, end_date[0] + 1))
    # make url for each day
    for season in days:
        for day in days[season]:
            url = 'https://api.openligadb.de/getmatchdata/bl1/' + \
                  str(season) + '/' + str(day)
            urls = urls + [url]


def crawl_openligadb(url):
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
                    jsonresponse[game]['team1']['teamName'],  # home_t
                    jsonresponse[game]['matchResults'][0]['pointsTeam1'],  # h
                    jsonresponse[game]['matchResults'][0]['pointsTeam2'],  # g
                    jsonresponse[game]['team2']['teamName']  # guest_t]
                ]
            else:
                unfinished_matches_length = len(unfinished_matches)
                unfinished_matches.loc[unfinished_matches_length] = [
                    jsonresponse[game]['matchDateTime'],  # match_date_time
                    jsonresponse[game]['team1']['teamName'],  # home_t
                    -1,  # h
                    -1,  # g
                    jsonresponse[game]['team2']['teamName']  # guest_t]
]