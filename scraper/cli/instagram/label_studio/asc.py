
"""Label-studio ASC format."""

import click
import os
import json

from ....label_studio import completitions_to_asc, alias_to_label
from ....instagram import post, label_studio as ls
from ....utils import count_lines, load_json


@click.group()
def asc():
    pass


@asc.group()
def convert():
    pass


@convert.command()
@click.argument('src', type=click.File('r'))
@click.argument('dst', type=click.Path(exists=True, readable=True))
@click.option('--start-from', '-s', type=int, default=0, show_default=True)
@click.option('--pattern', '-p', default='output-{index:08d}.json',
              show_default=True)
@click.option('--max-per-file', '-m', type=int, default=-1, show_default=True)
@click.option('--base-path', '-b', default='.', show_default=True)
def scraper_to_label_studio(src, dst, start_from, pattern, max_per_file,
                            base_path):
    """Convert scraper hydratated posts to label-studio import files."""
    def save(dst, pattern, start_from):
        filename = os.path.join(dst, pattern.format(index=start_from))
        with open(filename, 'w') as f:
            json.dump(out, f)

    out = []
    format_ = ls.format(base_path)
    with click.progressbar(src, length=count_lines(src.name)) as bar:
        for line in bar:
            out.extend(format_(post.Post(json.loads(line))))
            if max_per_file != -1 and len(out) >= max_per_file:
                save(dst, pattern, start_from)
                out = []
                start_from += 1
    if len(out) > 0:
        save(dst, pattern, start_from)


@convert.command()
@click.argument('src', type=click.Path(exists=True, readable=True))
def label_studio_to_asc(src):
    """Convert label-studio json completions to ASC dataset.

    SRC is the config.json file inside completions directory.
    """
    config = load_json(src)
    a2l = alias_to_label(config['label_config'])
    dataset = dict(completitions_to_asc(config['output_dir'], a2l))
    print(json.dumps(dataset))
