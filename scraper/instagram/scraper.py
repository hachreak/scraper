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

from json.decoder import JSONDecodeError
from selenium.webdriver.common.keys import Keys
from requests.exceptions import RequestException

from .. import utils


url_search = 'https://www.instagram.com/explore/tags/{0}/'
url_post = 'https://www.instagram.com/p/{0}/'

query_hash = 'f0986789a5c5d17c2400faebf16efd0d'
query_comments = {
    'query_hash': 'f0986789a5c5d17c2400faebf16efd0d',
}
url_query = 'https://www.instagram.com/graphql/query/'


def scrape_ids(url, times=1, end_cursor=None):
    def _get_media(url, params):
        res = requests.get(url, params=params).json()
        return res['graphql']['hashtag']['edge_hashtag_to_media']

    params = {'__a': 1}
    has_next_page = True
    #  for i in range(times):
    while True:
        if end_cursor:
            params['max_id'] = end_cursor
        media = utils.try_again(
            lambda: _get_media(url, params),
            (KeyError, RequestException, JSONDecodeError)
        )
        if media:
            for r in media['edges']:
                yield r['node']['shortcode']
                #  r['_end_cursor'] = media['page_info']['end_cursor']
                #  yield _get_comments(r)
            has_next_page = media['page_info']['has_next_page']
            if not has_next_page:
                # no more posts available
                return
            end_cursor = media['page_info']['end_cursor']


def get_comments(shortcode, loader):
    """Get more info about this specific media post."""
    def _get_request_json(url, params):
        res = requests.get(url, params=params)
        if res.status_code != requests.codes.ok:
            raise RequestException()
        return res.json()

    params = {'__a': 1}
    # get post page
    _post = utils.try_again(
        lambda: _get_request_json(url_post.format(shortcode), params),
        (RequestException, JSONDecodeError)
    )
    comments = _post['graphql']['shortcode_media'].get(
        'edge_media_to_comment', {}).get('edges', [])
    if len(comments) > 0:
        shmedia = _post['graphql']['shortcode_media']
        info = shmedia['edge_media_to_comment']['page_info']
        # check if there are more comments
        if info['has_next_page']:
            shortcode = _post['graphql'][
                'shortcode_media']['shortcode']
            # get all other comments
            comments.extend(
                _get_more_comments(url_post.format(shortcode), loader=loader)
            )
            # sort comments
            sorted(comments, key=lambda x: x['node']['created_at'])
            _post['graphql']['shortcode_media'][
                'edge_media_to_comment']['edges'] = comments
    return _post


def _get_more_comments(url, loader):
    query = 'query_hash={0}'.format(query_hash)
    get_more = True
    while get_more:
        link = _get_link_more_comments(loader.driver)
        get_more = link is not None
        if link:
            utils.try_again(lambda: link.send_keys(Keys.ENTER))
    list_of_list = [
        r.response.body['data']['shortcode_media'][
            'edge_media_to_comment']['edges']
        for r in loader.driver.requests if query in r.path and r.response]
    return list(itertools.chain(*list_of_list))


def _get_link_more_comments(driver):
    els = utils.try_again(
        lambda: [el for el in driver.find_elements_by_tag_name('button')
                 if 'comments' in el.text]
    ) or []
    try:
        return els[0]
    except IndexError:
        return None
