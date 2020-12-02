# Use this file to test your crawler.

from teamproject import crawler
import unittest

class test_crawler(unittest.TestCase):
    # Example test:
    '''
    def test_fetch_data():
        data = crawler.fetch_data()
        assert isinstance(data, pd.DataFrame)
        assert data.home_score.dtype == 'int64'
        assert data.guest_score.dtype == 'int64'
        assert (data.home_score >= 0).all()
        assert (data.guest_score >= 0).all()
        assert (data.home_team != data.guest_team).all()
    '''


    def test_get_all_urls(self):
        assert (crawler.get_all_urls(1, 2014, 2, 2014)) == [ \
            'https://api.openligadb.de/getmatchdata/bl1/2014/1', \
            'https://api.openligadb.de/getmatchdata/bl1/2014/2']
        assert (crawler.get_all_urls(1, 2014, 1, 2014)) == \
        ['https://api.openligadb.de/getmatchdata/bl1/2014/1']
        assert (crawler.get_all_urls(1, 2014, 8, 2016))[-1] == \
            "https://api.openligadb.de/getmatchdata/bl1/2016/8"
        assert (crawler.get_all_urls(1, 2014, 8, 2016))[0] == \
            "https://api.openligadb.de/getmatchdata/bl1/2014/1"
        self.assertRaises(ValueError, lambda: crawler.get_all_urls(0, 2014, 8, 2016))
