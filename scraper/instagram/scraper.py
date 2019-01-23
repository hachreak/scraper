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


url = 'https://www.instagram.com/explore/tags/{0}/'


def scrape(url, times=1, end_cursor=None):
    params = {'__a': 1}
    for i in range(times):
        if end_cursor:
            params['max_id'] = end_cursor
        res = requests.get(url, params=params).json()
        media = res['graphql']['hashtag']['edge_hashtag_to_media']
        for r in media['edges']:
            r['_end_cursor'] = media['page_info']['end_cursor']
            yield r
        end_cursor = media['page_info']['end_cursor']
