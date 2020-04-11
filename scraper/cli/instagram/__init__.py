
"""Instagram CLI."""

import click

from .stats import stats
from .scraper import scrape
from .label_studio.asc import asc


@click.group()
def instagram():
    pass


instagram.add_command(scrape)
instagram.add_command(stats)
instagram.add_command(asc)
