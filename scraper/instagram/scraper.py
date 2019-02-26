# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
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

"""Instagram scraper."""

import requests
import itertools

from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

from .. import driver as drv


url_search = 'https://www.instagram.com/explore/tags/{0}/'
url_post = 'https://www.instagram.com/p/{0}/'

query_hash = 'f0986789a5c5d17c2400faebf16efd0d'
query_comments = {
    'query_hash': 'f0986789a5c5d17c2400faebf16efd0d',
}
url_query = 'https://www.instagram.com/graphql/query/'


def scrape(url, times=1, end_cursor=None):
    params = {'__a': 1}
    for i in range(times):
        if end_cursor:
            params['max_id'] = end_cursor
        res = requests.get(url, params=params).json()
        media = res['graphql']['hashtag']['edge_hashtag_to_media']
        for r in media['edges']:
            r['_end_cursor'] = media['page_info']['end_cursor']
            yield _get_comments(r)
        end_cursor = media['page_info']['end_cursor']


def _get_comments(media):
    """Get more info about this specific media post."""
    params = {'__a': 1}
    if 'shortcode' in media.get('node', {}).keys():
        # get post page
        res = requests.get(
            url_post.format(media['node']['shortcode']),
            params=params
        )
        if res.status_code == requests.codes.ok:
            media['_post'] = res.json()
            comments = media['_post']['graphql']['shortcode_media'][
                'edge_media_to_comment']['edges']
            shmedia = media['_post']['graphql']['shortcode_media']
            info = shmedia['edge_media_to_comment']['page_info']
            # check if there are more comments
            if info['has_next_page']:
                shortcode = media['_post']['graphql'][
                    'shortcode_media']['shortcode']
                # get all other comments
                comments.extend(
                    _get_more_comments(url_post.format(shortcode))
                )
                # sort comments
                sorted(comments, key=lambda x: x['node']['created_at'])
                media['_post']['graphql']['shortcode_media'][
                    'edge_media_to_comment']['edges'] = comments
    return media


def try_again(fun, exc=StaleElementReferenceException, times=5):
    for _ in range(times):
        try:
            return fun()
        except exc:
            sleep(1)


def _get_more_comments(url):
    with drv.load(url) as loader:
        query = 'query_hash={0}'.format(query_hash)
        get_more = True
        while get_more:
            link = _get_link_more_comments(loader.driver)
            get_more = link is not None
            if link:
                try_again(lambda: link.send_keys(Keys.ENTER))
        list_of_list = [
            r.response.body['data']['shortcode_media'][
                'edge_media_to_comment']['edges']
            for r in loader.driver.requests if query in r.path and r.response]
        return list(itertools.chain(*list_of_list))


def _get_link_more_comments(driver):
    els = try_again(
        lambda: [el for el in driver.find_elements_by_tag_name('button')
                 if 'comments' in el.text]
    ) or []
    try:
        return els[0]
    except IndexError:
        return None
