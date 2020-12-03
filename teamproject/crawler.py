"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""

import json

import pandas as pd
import datetime
import scrapy
from scrapy.crawler import CrawlerProcess

# Initialize matches dataframe that will be filled and returned
columns = ['date_time', 'home_team', 'home_score', 'guest_score',
           'guest_team']
matches = pd.DataFrame([], columns=columns)  # empty df to fill
urls = []


def fetch_data(start_date, end_date):
    """
    Query sample data from "the internet" and return as pd.DataFrame.
    """
    global urls
    curate_urls(start_date, end_date)
    # initialize and start crawling
    process = CrawlerProcess()
    process.crawl(OpenLigaSpider)
    process.start()
    urls = []
    return matches


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
        statement_s = 1963 > season or season > datetime.datetime.now().year or statement_s
    return statement_d or statement_s


def curate_urls(start_date, end_date):
    """
    Expects a timeperiod. Gameday and season a an array, in that order.

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


class OpenLigaSpider(scrapy.Spider):
    """
        Query sample match and print full json-string
    """
    name = "OpenLigaSpider"

    def start_requests(self):
        print(urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # suppresses false warning: can be ignored
    # noinspection PyMethodOverriding
    def parse(self, response):
        """
        Parses json-data into matches DataFrame.

        Internal item order is sensitive to rearrangement!
        """

        jsonresponse = json.loads(response.body)
        for game in range(len(jsonresponse)):  # all matches in scrape
            # appends response item-array to matches, !ORDER SENSITIVE!
            matches_length = len(matches)
            matches.loc[matches_length] = [
                jsonresponse[game]['matchDateTime'],  # match_date_time
                jsonresponse[game]['team1']['teamName'],  # home_t
                jsonresponse[game]['matchResults'][0]['pointsTeam1'],
                # h_s
                jsonresponse[game]['matchResults'][0]['pointsTeam2'],
                # g_s
                jsonresponse[game]['team2']['teamName']  # guest_t]
            ]
