"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""

import json

import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

# Initialize matches dataframe that will be filled and returned
columns = ['date_time', 'home_team', 'home_score', 'guest_score', 'guest_team']
matches = pd.DataFrame([], columns=columns)  # empty df to fill


def fetch_data():
    """
    Query sample data from "the internet" and return as pd.DataFrame.
    """
    # initialize and start crawling
    process = CrawlerProcess()
    process.crawl(OpenLigaSpider)
    process.start()

    return matches


class OpenLigaSpider(scrapy.Spider):
    """
        Query sample match and print full json-string
    """
    name = "OpenLigaSpider"

    def start_requests(self):
        urls = ['https://api.openligadb.de/getmatchdata/bl1/2020/1']
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
                jsonresponse[game]['matchResults'][0]['pointsTeam1'],  # h_s
                jsonresponse[game]['matchResults'][0]['pointsTeam2'],  # g_s
                jsonresponse[game]['team2']['teamName']  # guest_t]
            ]
