
"""Instagram CLI."""

import click
import json

from collections import defaultdict
from datetime import datetime

from .. import stats as s, exc, driver as drv
from ..instagram import scraper, post
from .validators import get_tag


@click.group()
def instagram():
    pass


@instagram.group()
def scrape():
    pass


@scrape.command()
@click.argument('hashtag', callback=get_tag)
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times call the API")
@click.option('--from-id', '-f', default=None, help="Start from this id")
def ids(hashtag, times, from_id):
    """Scrape Instagram."""
    ids_scraped = scraper.scrape_ids(
        scraper.url_search.format(hashtag), times=times, end_cursor=from_id
    )
    for shortcode in ids_scraped:
        print(shortcode)


@scrape.command()
@click.argument('input_', type=click.File('r'))
@click.option('--reload-every', '-r', default=20, type=int,
              help="Reload selenium browser every X times.")
def hydrate(input_, reload_every):
    with drv.load(reload_every=reload_every) as loader:
        for value in input_:
            try:
                result = scraper.get_comments(value.strip(), loader=loader)
                if result:
                    print(json.dumps(result))
            except exc.UnknowObject:
                # if something went wrong loading page, skip
                pass


@scrape.group()
def hydrated():
    """Operation on hydrated data."""
    pass


@hydrated.command()
@click.argument('input_', type=click.File('r'))
def get_ids(input_):
    """Get shortcode from hydrated data."""
    for line in input_:
        try:
            line = json.loads(line)
            print(line['graphql']['shortcode_media']['shortcode'])
        except json.decoder.JSONDecodeError:
            pass


@hydrated.command()
@click.argument('input_', type=click.File('r'))
def get_imgs(input_):
    """Get image links from hydrated data."""
    for line in input_:
        try:
            line = json.loads(line)
            print(line['graphql'][
                'shortcode_media']['display_resources'][-1]['src'])
        except json.decoder.JSONDecodeError:
            pass


@instagram.command()
@click.argument('input_', type=click.File('r'))
@click.option('--language', '-l', default=None, help="Filter by language")
@click.option('--percentage', '-p', default=0.5,
              help="Percentage of X words to be considered X")
def stats(input_, language, percentage):
    """Show some statistics about the posts."""
    if language:
        is_lang = s.is_of_lang(
            lang=language,
            filter_text=lambda w: not w.startswith('#'),
            percentage=percentage
        )

    ids = []
    count_all_posts = 0
    count_posts = 0
    count_posts_likes = 0
    count_comments = 0
    count_videos = 0
    date_from = datetime.now()
    date_to = datetime.now()
    users = defaultdict(lambda: 0)
    users_posting = defaultdict(lambda: 0)
    hashtags = defaultdict(lambda: 0)
    locations = defaultdict(lambda: 0)
    for line in input_:
        try:
            mypost = post.Post(json.loads(line))._info
            if mypost['id'] not in ids:
                count_all_posts += 1
                if not language or \
                        is_lang(
                            s.remove_punctuations(mypost['text']).strip()
                        ) or \
                        not mypost['text']:
                    count_posts += 1
                    count_posts_likes += mypost['likes']
                    count_comments += mypost['comments']['count']
                    users_posting[mypost['username']] += 1
                    users[mypost['username']] += 1
                    for c in mypost['comments']['conversations']:
                        users[c['owner']['username']] += 1
                    timestamp = datetime.fromtimestamp(int(mypost['time']))
                    if date_from > timestamp:
                        date_from = timestamp
                    if date_to < timestamp:
                        date_to = timestamp
                    if mypost['video']:
                        count_videos += 1
                    for ht in mypost['hashtags']:
                        hashtags[ht] += 1
                    if (mypost.get('location', {}) or {}).get('slug'):
                        locations[mypost['location']['slug']] += 1
            ids.append(mypost['id'])
        except mypost.DeletedPost:
            print("post error..")
            pass
        except json.decoder.JSONDecodeError:
            print("json error..")
            pass

    if language:
        print('language: {0}'.format(language))
    print('period of time: from {0} to {1}'.format(date_from, date_to))
    print('# users: {0}'.format(len(users.keys())))
    print('# users posting: {0}'.format(len(users_posting.keys())))
    print('# users with less than 5 posts/comments: {0}'.format(
        len(list(filter(lambda x: x < 5, users.values())))
    ))
    print("# posts: {0} of {1}".format(count_posts, count_all_posts))
    print("# post likes: {0}".format(count_posts_likes))
    print("# likes / # posts: {0:0.2f}".format(
        count_posts_likes / count_posts))
    print('# comments: {0}'.format(count_comments))
    print("# comments / # posts: {0:0.2f}".format(
        count_comments / count_posts))
    print("# videos: {0}".format(count_videos))
    print('most posting users (# post):')
    for username in sorted(
            users, key=users.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(username, users[username]))
    print('\t...')
    print('most used hashtags:')
    for ht in sorted(hashtags, key=hashtags.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(ht, hashtags[ht]))
    print('\t...')
    print('count locations: {0} for {1} posts'.format(
        len(locations.keys()), sum(locations.values())))
    print('most frequent locations:')
    for slug in sorted(
            locations, key=locations.__getitem__, reverse=True)[:20]:
        print('\t{0} = {1}'.format(slug, locations[slug]))
    print('\t...')
