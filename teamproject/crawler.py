"""
This module contains code to fetch required data from the internet and
convert it to a pd.DataFrame.
"""

import pandas as pd
import scrapy
import json
from scrapy.crawler import CrawlerProcess


def fetch_data():
    """
    Query data from "the internet" and return as pd.DataFrame.
    """

    process = CrawlerProcess()
    process.crawl(OpenLigaSpider)
    process.start()
    # gamedataframe = pd.DataFrame(data=process)
    # return gamedataframe


def incorrect_dates(starting_day, starting_season, ending_day,
                    ending_season):
    """Were there a matches on those days?"""
    days = [starting_day, ending_day]
    seasons = [starting_season, ending_season]
    Statement_d = False
    Statement_s = False

    for date in days:
        Statement_d = 0 == date or date > 35 or Statement_d
    for season in seasons:
        Statement_s = 1963 > season or season > 2020 or Statement_s
    return (Statement_d or Statement_s)


def get_all_urls(starting_day, starting_season, ending_day,
                 ending_season):
    """
    Expects a timeperiod. Gameday and season given seperately.

    :param starting_day: int
    :param starting_season: int
    :param ending_day: int
    :param ending_season: int
    :return: List of urls of matches from each gameday in the given
            time period
    """
    urls = []
    seasons_timerange = ending_season - starting_season

    # Dictionary with season as key combined with number of gamedays as
    # list
    if incorrect_dates(starting_day, starting_season, ending_day,
                       ending_season):
        raise ValueError("there has been no match on this day."
                         "Matches are 34 days per season from 1963 to 2020")

    if seasons_timerange == 0:
        days = {
            starting_season: list(range(starting_day, ending_day + 1))}
    else:
        days = {starting_season: list(range(starting_day, 35))}
        # adding seasons between the dates
        for x in range(starting_season + 1, ending_season):
            days[x] = list(range(1, 35))
        # adding last season we want to look at
        days[ending_season] = list(range(1, ending_day + 1))
    for season in days:
        for day in days[season]:
            url = 'https://api.openligadb.de/getmatchdata/bl1/' + \
                  str(season) + '/' + str(day)
            urls = urls + [url]
    return urls


def NextURL(list_of_dates):
    """gets a list of the dates (first day, first season, last day, last season)
    :return: list of urls from all gamedays(in the timerange) as generator"""
    urls = get_all_urls(list_of_dates[0], list_of_dates[1],
                        list_of_dates[2], list_of_dates[3])
    for next_url in urls:
        yield next_url


def get_dates_from_gui():
    day1 = 0
    season1 = 0
    day2 = 0
    season2 = 0
    return [day1, season1, day2, season2]


class OpenLigaSpider(scrapy.Spider):
    """
        Query sample match and print full json-string
    """
    name = "OpenLigaSpider"
    allowed_domains = []
    url = NextURL(get_dates_from_gui)   # generator of all urls
    start_url = []

    def start_requests(self):
        try:
            start_url = next(self.url)
            request = scrapy.Request(start_url, dont_filter=True)
            yield request
        except StopIteration:
            pass

    # suppresses false warning: can be ignored
    # noinspection PyMethodOverriding
    def parse(self, response):

        jsonresponse = json.loads(response.body)
        for game in range(9):
            yield {
                'Datum': jsonresponse[game]['matchDateTime'],
                'Heimverein': jsonresponse[game]['team1']['teamName'],
                'Gastverein': jsonresponse[game]['team2']['teamName'],
                'Tore Heim': jsonresponse[game]['matchResults'][0][
                    'pointsTeam1'],
                'Tore Gast': jsonresponse[game]['matchResults'][0][
                    'pointsTeam2'],
            }
            try:
                next_url = next(self.url)
                yield scrapy.Request(next_url)
            except StopIteration:
                pass

# To scrape data call uncomment fetch_data_new()
# fetch_data()

