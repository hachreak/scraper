
"""Scraper CLI."""

import click
import requests
import json
import os

from ... import exc, driver as drv
from ...instagram import scraper
from ..validators import get_tag


@click.group()
def scrape():
    """Scraper CLI."""
    pass


@scrape.command()
@click.argument('hashtag', callback=get_tag)
@click.option('--times', '-t', default=1, type=int, show_default=True,
              help="How many times call the API")
@click.option('--from-id', '-f', default=None, help="Start from this id")
def ids(hashtag, times, from_id):
    """Scrape Instagram and return post ids."""
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
    """Hydrate post id to a full post in json format."""
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
    """Operations on hydrated data."""
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
    """Get image temporary url from hydrated data."""
    for line in input_:
        try:
            line = json.loads(line)
            print(line['graphql'][
                'shortcode_media']['display_resources'][-1]['src'])
        except json.decoder.JSONDecodeError:
            pass


@scrape.command()
@click.argument('input_', type=click.File('r'))
def get_imgs_from_shortcode(input_):
    """Get image path from shortcode."""
    from scraper.instagram.scraper import url_post
    from bs4 import BeautifulSoup
    import requests

    for shortcode in input_:
        url = url_post.format(shortcode.strip())
        res = requests.get(
            url, headers={'User-Agent': 'Mozilla'}
        )
        soup = BeautifulSoup(res.text)
        meta_img = [f for f in soup.findAll('meta')
                    if f.get('property') == 'og:image'][0].get('content')
        print(meta_img)

@scrape.command()
@click.argument('ids', type=click.File('r'))
@click.argument('urls', type=click.File('r'))
@click.argument('dest_path', type=click.Path(exists=True, file_okay=False, dir_okay=True, 
                writable=True))
def download_images (ids, urls, dest_path):
    """Download images using the list of ids and urls."""
    for file1_line, file2_line in zip(ids, urls):
        r = requests.get(file2_line)
        images_path = file1_line
        download_path = os.path.join(dest_path, images_path.strip()+'.jpg')
        with open(download_path, 'wb') as f:
            f.write(r.content)