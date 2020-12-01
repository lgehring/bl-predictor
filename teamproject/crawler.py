"""
This module contains code to fetch required data from the internet and
convert it to a pd.DataFrame.
"""

import pandas as pd
import scrapy
import json
from scrapy.crawler import CrawlerProcess

urls = []


# TODO: add possibility to choose what data should be scraped given by gui.py
# TODO: adjust scraped data to required format defined above
def fetch_data(starting_day, starting_season, ending_day,
               ending_season):
    """
    Query data from "the internet" and return as pd.DataFrame.
    """
    urls = get_all_urls(starting_day, starting_season, ending_day,
                        ending_season)
    process = CrawlerProcess()
    process.crawl(OpenLigaSpider)
    process.start()

    # gamedataframe = pd.DataFrame(data=process)
    # return gamedataframe
    return urls


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
    global urls
    # Dictionary with season as key combined with number of gamedays
    days = {starting_season: list(range(starting_day, 35))}
    # adding seasons between the given seasons
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


def NextURL():
    global urls
    for next_url in urls:
        yield next_url


class OpenLigaSpider(scrapy.Spider):

    """
        Query sample match and print full json-string
    """
    name = "OpenLigaSpider"
    allowed_domains = []
    url = NextURL()
    start_url = []

    def start_requests(self):
        try:
            start_url = next(self.url)
        except StopIteration:
            pass
        request = scrapy.Request(start_url, dont_filter=True)
        yield request


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
fetch_data(1, 2014, 34, 2014)
