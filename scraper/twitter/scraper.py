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

import urllib

from bs4 import BeautifulSoup as bs
from copy import deepcopy
from selenium.common.exceptions import NoSuchElementException
from time import sleep

from ..driver import goto_end_page, load, scroll
from ..exc import NoMoreItems
from .tweet import Tweet, TweetFlowFromPage, get_ancestor, TweetFromScroll


query = {
    'f': 'tweets',
    'src': 'typd',
}
baseurl = "https://twitter.com/search?"


def get_tweet_ids(html_source):
    """Get all tweets from the page."""
    soup = bs(html_source, "lxml")
    # and all comments for each one
    for tag in TweetFromScroll.get_html_tag(soup):
        yield TweetFromScroll.get_id(tag), TweetFromScroll.get_username(tag)


def get_tweets(url):
    """Get single comments of the tweet."""
    with load(url) as driver:
        # scroll page until the end
        goto_end_page(driver, IsLastComment(driver))
        soup = bs(driver.page_source, "lxml")
        # open ancestor first
        ancestor = get_ancestor(soup)
        if ancestor:
            driver.get(Tweet.get_url(ancestor.username(), ancestor.id()))
        # click on "more reply"
        more_reply(driver)
        soup = bs(driver.page_source, "lxml")
        # return tweet
        result = TweetFlowFromPage(soup)
    return result


class IsLastComment(object):

    def __init__(self, driver):
        self._driver = driver

    def __call__(self):
        try:
            self._driver.find_element_by_css_selector(
                '.timeline-end.has-more-items .stream-end'
            )
            return False
        except NoSuchElementException:
            return True


def more_reply(driver):
    """Get more comments clicking on more reply link."""
    try:
        for link in driver.find_elements_by_css_selector(
                '.stream ol#stream-items-id > li > ol.stream-items > li '
                '> a.ThreadedConversation-moreRepliesLink'):
            link.click()
            sleep(1)
    except NoSuchElementException:
        pass


def get_url(baseurl, params):
    """Build page url."""
    return ' '.join([baseurl + urllib.parse.urlencode(params)])


def _has_more_items(driver):
    try:
        return driver.requests[-1].response.body['has_more_items']
    except (AttributeError, IndexError, KeyError, TypeError):
        return True


def scraper(query, baseurl, per_driver=10):
    """Download tweets opening the twitter page, scrolling X times."""
    with load(get_url(baseurl, query)) as driver:
        driver = scroll(driver, per_driver)
        html_source = driver.page_source
        _more_items = _has_more_items(driver)
    for t in get_tweet_ids(html_source):
        yield t
    if not _more_items:
        raise NoMoreItems()


def scrape_more(query, q, scraper, times=10, max_id=None):
    """Get tweets opening Y times selenium."""
    query = deepcopy(query)
    query['q'] = q
    for i in range(0, times):
        if max_id:
            query['q'] = ' '.join([q, 'max_id:{0}'.format(max_id)])
        for id_username in scraper(query=query):
            yield id_username
            id_, _ = id_username
            max_id = id_
