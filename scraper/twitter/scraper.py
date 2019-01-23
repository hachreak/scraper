# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2018-2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
#
# pysenslog is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pysenslog is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pysenslog.  If not, see <http://www.gnu.org/licenses/>.

"""Twitter scraper."""

import time
import urllib

from selenium import webdriver
from bs4 import BeautifulSoup as bs
from copy import deepcopy

from .tweet import Tweet


query = {
    'f': 'tweets',
    'src': 'typd',
}
baseurl = "https://twitter.com/search?"


def get_tweets(html_source):
    soup = bs(html_source)
    return [Tweet(t)
            for t in soup.body.findAll('li', attrs={'class': 'stream-item'})]


def scroll(driver, times=10):
    for i in range(0, times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
    return driver


def load(url):
    driver = webdriver.Firefox()
    driver.base_url = url
    driver.get(driver.base_url)
    return driver


def get_url(baseurl, params):
    return ' '.join([baseurl + urllib.urlencode(params)])


def scraper(query, baseurl, per_driver=10):
    driver = scroll(load(get_url(baseurl, query)), per_driver)
    html_source = driver.page_source
    driver.close()
    return get_tweets(html_source)


def scrape_more(query, q, scraper, times=10):
    query = deepcopy(query)
    query['q'] = q
    for i in range(0, times):
        tweets = scraper(query=query)
        if len(tweets) == 0:
            raise StopIteration()
        for t in tweets:
            yield t
        query['q'] = ' '.join([q, 'max_id:{0}'.format(tweets[-1].id)])
