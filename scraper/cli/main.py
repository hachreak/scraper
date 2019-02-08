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
import json

from collections import defaultdict
from functools import partial
from copy import deepcopy
from datetime import datetime

from .validators import get_hashtag, get_tag
from .. import stats as s
from ..twitter import scraper as tscraper, tweet
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
@click.option('--language', '-l', default=None, help="Filter by language")
def scrape(hashtag, per_driver, times, from_id, language):
    """Scrape Twitter."""
    my_scraper = partial(
        tscraper.scraper, baseurl=tscraper.baseurl, per_driver=per_driver
    )

    # build query
    query = deepcopy(tscraper.query)
    if language:
        query['l'] = language

    for t in tscraper.scrape_more(
                query=query,
                q=hashtag,
                scraper=my_scraper,
                times=times,
                max_id=from_id
            ):
        print(json.dumps(t._info))


@twitter.command()
@click.argument('input_', type=click.File('r'))
@click.option('--language', '-l', default=None, help="Filter by language")
@click.option('--percentage', '-p', default=0.5,
              help="Percentage of X words to be considered X")
def stats(input_, language, percentage):
    """Show some statistics about the tweets."""
    if language:
        is_lang = s.is_of_lang(
            lang=language,
            filter_text=lambda w: not w.startswith('#'),
            percentage=percentage
        )
    count_all_posts = 0
    count_all_comments = 0
    count_posts = 0
    count_comments = 0
    count_comments_with_video = 0
    count_posts_with_video = 0
    count_retweets = 0
    count_likes = 0
    count_retweets_posts = 0
    count_likes_posts = 0
    count_without_comments = 0
    count_post_with_imgs = 0
    count_comments_with_imgs = 0
    count_without_comments = 0
    count_videos = 0
    count_imgs = 0
    users = defaultdict(lambda: 0)
    users_posting = defaultdict(lambda: 0)
    hashtags = defaultdict(lambda: 0)
    date_from = datetime.now()
    date_to = datetime.now()
    ids = []
    for line in input_:
        line = json.loads(line)
        count_all_posts += 1
        gen = tweet.Tweet.iterate(line)
        post = next(gen)
        if post['id'] not in ids:
            ids.append(post['id'])
            for t in gen:
                count_all_comments += 1
                if not language or is_lang(t['text']):
                    count_comments += 1
                    if t['video']:
                        count_comments_with_video += 1
                        count_videos += len(t['video'])
                    users[t['username']] += 1
                    for ht in t['hashtags']:
                        hashtags[ht.lower()] += 1
                    if t['retweets']:
                        count_retweets += s.parse_humanized_int(t['retweets'])
                    if t['likes']:
                        count_likes += s.parse_humanized_int(t['likes'])
                    if t.get('image', []) != []:
                        count_comments_with_imgs += 1
                    count_imgs += len(t.get('image', []))
            if not language or is_lang(post['text']):
                count_posts += 1
                users_posting[line['username']] += 1
                users[post['username']] += 1
                for ht in post['hashtags']:
                    hashtags[ht.lower()] += 1
                if post['video']:
                    count_posts_with_video += 1
                    count_videos += len(post['video'])
                if post['retweets']:
                    count_retweets_posts += s.parse_humanized_int(post['retweets'])
                    count_retweets += s.parse_humanized_int(post['retweets'])
                if post['likes']:
                    count_likes_posts += s.parse_humanized_int(post['likes'])
                    count_likes += s.parse_humanized_int(post['likes'])
                if post['comments']['total'] == 0:
                    count_without_comments += 1
                if post.get('image', []) != []:
                    count_post_with_imgs += 1
                count_imgs += len(post.get('image', []))
                timestamp = datetime.fromtimestamp(int(post['time']))
                if date_from > timestamp:
                    date_from = timestamp
                if date_to < timestamp:
                    date_to = timestamp

    if language:
        print('language: {0}'.format(language))
    print('period of time: from {0} to {1}'.format(date_from, date_to))
    print('# users: {0}'.format(len(users.keys())))
    print('# posts: {0} of {1}'.format(count_posts, count_all_posts))
    print('# comments: {0} of {1}'.format(count_comments, count_all_comments))
    print('# comments / # post: {0:0.2f}'.format(count_comments / count_posts))
    print('# videos: {0}'.format(count_videos))
    print('# post with video: {0}'.format(count_posts_with_video))
    print('# comments with video: {0}'.format(count_comments_with_video))
    print('# images: {0}'.format(count_imgs))
    print('# tweets with images: {0}'.format(count_post_with_imgs))
    print('# comments with images: {0}'.format(count_comments_with_imgs))
    print('# users posting: {0}'.format(len(users_posting.keys())))
    print('# all likes: {0}'.format(count_likes))
    print('# post likes: {0}'.format(count_likes_posts))
    print('# all retweets: {0}'.format(count_retweets_posts))
    print('# post retweets: {0}'.format(count_retweets_posts))
    print('# posts without comments: {0}'.format(count_without_comments))
    print('# users with less than 5 posts/comments: {0}'.format(
        len(list(filter(lambda x: x < 5, users.values())))
    ))
    print('most used hashtags:')
    for ht in sorted(hashtags, key=hashtags.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(ht, hashtags[ht]))
    print('most posting users (# post):')
    for username in sorted(
            users_posting, key=users_posting.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(username, users_posting[username]))
    print('\t...')
    print('most prolific users (# post + # comments):')
    for username in sorted(users, key=users.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(username, users[username]))
    print('\t...')


@cli.group()
def instagram():
    pass


@instagram.command('scrape')
@click.argument('hashtag', callback=get_tag)
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times call the API")
@click.option('--from-id', '-f', default=None, help="Start from this id")
def instagram_scrape(hashtag, times, from_id):
    """Scrape Instagram."""
    scraper = iscraper.scrape(
        iscraper.url_search.format(hashtag), times=times, end_cursor=from_id
    )
    for post in scraper:
        print(json.dumps(post))
