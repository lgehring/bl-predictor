"""
This module contains code to fetch required data from the internet and convert
it to a pd.DataFrame.
"""

import pandas as pd
import scrapy
import json

from scrapy.crawler import CrawlerProcess

# TODO: add possibility to choose what data should be scraped given by gui.py
# TODO: adjust scraped data to required format defined above
def fetch_data():
    """
    Query data from "the internet" and return as pd.DataFrame.
    """
    process = CrawlerProcess()
    process.crawl(OpenLigaSpider)
    process.start()
    gamedataframe = pd.DataFrame(data=process)
    return gameframedata


class OpenLigaSpider(scrapy.Spider):
    """
        Query sample match and print full json-string
    """
    name = "OpenLigaSpider"

    def start_requests(self):
        # Example: Spiele des 1. Spieltages der ersten Bundesliga 2020/2021
        urls = ['https://api.openligadb.de/getmatchdata/bl1/2020/1']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # suppresses false warning: can be ignored
    # noinspection PyMethodOverriding
    def parse(self, response):
        jsonresponse = json.loads(response.body)
        for game in range(9):
            yield {
                'Datum': jsonresponse[game]['matchDateTime'],
                'Heimverein': jsonresponse[game]['team1']['teamName'],
                'Gastverein': jsonresponse[game]['team2']['teamName'],
                'Tore Heim': jsonresponse[game]['matchResults'][0]['pointsTeam1'],
                'Tore Gast': jsonresponse[game]['matchResults'][0]['pointsTeam2'],
            }

# To scrape data call uncomment fetch_data_new()
# fetch_data_new()
