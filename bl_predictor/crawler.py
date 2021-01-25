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
    if start_date == [0, 0] == end_date:
        # getting data from last match, therefore possible unfinished matches.
        # fetch_data checks whether or not there is any data.
        # If not it takes the data from one year before. This can also
        # be unfinished matches (exp. 2020 matches are until may).
        current_year = datetime.date.today().year
        current_year_has_no_data = False or crawl_openligadb(
            curate_urls([1, current_year], [1, current_year]))
        if current_year_has_no_data:
            last_data_year = datetime.date.today().year - 1
            urls = curate_urls([1, last_data_year], [34, last_data_year])
        else:
            urls = curate_urls([1, current_year], [34, current_year])
    else:
        curate_urls(start_date, end_date)
        urls = curate_urls(start_date, end_date)
    # initialize and start crawling
    crawl_openligadb(urls)

    # covert DataFrame columns from object to int
    if start_date == [0, 0] == end_date:
        convertdf(unfinished_matches)
        return unfinished_matches
    else:
        convertdf(matches)
        return matches


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


def curate_urls(start_date, end_date):
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

            save_logos(jsonresponse[game]['team1']['teamName'],
                       jsonresponse[game]['team1']['teamIconUrl'])
            save_logos(jsonresponse[game]['team2']['teamName'],
                       jsonresponse[game]['team2']['teamIconUrl'])

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


def save_logos(teamname, teamicon):
    """
    checks if logos are missing in the folder "team_logos" and download,
    if necessary

    :param teamname: string with the name the file should be called
    :param teamname: Web URL where the image is saved
    """
    gui_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(gui_path)
    if not os.path.isfile(dir_path + "/team_logos/" + teamname + ".png"):
        save_logo = open(dir_path + "/team_logos/" + teamname + ".png", "wb")
        save_logo.write(requests.get(teamicon).content)
        save_logo.close()
