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

"""CLI main."""

import click

from pprint import pprint
from functools import partial

from .validators import get_hashtag, get_tag
from ..twitter import scraper as tscraper
from ..instagram import scraper as iscraper


@click.group()
def cli():
    pass


@cli.group()
def twitter():
    pass


@twitter.command()
@click.argument('hashtag', callback=get_hashtag)
@click.option('--per_driver', '-p', default=0, type=int, show_default=True,
              help="How many times scroll for each driver")
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times open a new driver")
@click.option('--from-id', '-f', default=None, help="Start from this id")
def scrape(hashtag, per_driver, times, from_id):
    """Scrape Twitter."""
    my_scraper = partial(
        tscraper.scraper, baseurl=tscraper.baseurl, per_driver=per_driver
    )
    for t in tscraper.scrape_more(
                query=tscraper.query,
                q=hashtag,
                scraper=my_scraper,
                times=times,
                max_id=from_id
            ):
        pprint(t._info)


@cli.group()
def instagram():
    pass


@instagram.command('scrape')
@click.argument('hashtag', callback=get_tag)
@click.option('--times', '-t', default=10, type=int, show_default=True,
              help="How many times call the API")
@click.option('--from-id', '-f', default=None, help="Start from this id")
def instagram_scrape(hashtag, times, from_id):
    """Scrape Instagram."""
    driver = iscraper.scrape(
        iscraper.url.format(hashtag), times=times, end_cursor=from_id
    )
    for p in driver:
        pprint(p)
