# -*- coding: utf-8 -*-
#
# This file is part of tweet_scraper.
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

"""Scraper."""

from __future__ import unicode_literals

import sys

from pprint import pprint
from functools import partial

from scraper.twitter import scraper


if len(sys.argv) < 2:
    print("{0} hashtag".format(sys.argv[0]))
    sys.exit(1)

q = sys.argv[1]
per_driver = 5
times = 1

my_scraper = partial(
    scraper.scraper, baseurl=scraper.baseurl, per_driver=per_driver
)
tweets = []
index = 1
for t in scraper.scrape_more(
        query=scraper.query, q=q, scraper=my_scraper, times=times):
    pprint(t._info)
