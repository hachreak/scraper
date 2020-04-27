
"""Label-studio ASC format."""

import click
import os
import json

from ....label_studio import completitions_to_asc, alias_to_label
from ....instagram import post, label_studio as ls
from ....utils import count_lines, load_json, fill_buffer, save_json


@click.group()
def asc():
    """Aspect Sentiment Classification."""
    pass


@asc.group()
def convert():
    """Convert formats.

    Usually the workflow is the following:

    1) Convert scrape result into label-studio format.

    2) Convert labelled data into ASC dataset format.
    """
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
    format_ = ls.format(base_path)
    fb = fill_buffer(
            lambda line: {v['data']['comment_id']: v
                          for v in format_(post.Post(json.loads(line)))},
            max_per_file
    )
    with click.progressbar(src, length=count_lines(src.name)) as bar:
        for (index, data) in enumerate(fb(bar), start_from):
            filename = os.path.join(dst, pattern.format(index=index))
            save_json(filename, data)


@convert.command()
@click.argument('src', type=click.Path(exists=True, readable=True))
@click.argument('dst', type=click.File('w'))
def get_images_from_label_studio(src, dst):
    """Get list of images to use inside label-studio."""
    filenames = os.listdir(src)
    images = []
    with click.progressbar(filenames, length=len(filenames)) as bar:
        # load all images
        for name in bar:
            content = load_json(os.path.join(src, name))
            for element in content.values():
                images.append(element['data']['image'].split('/')[-1])
        # save them
        dst.write('\n'.join(set(images)))


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
