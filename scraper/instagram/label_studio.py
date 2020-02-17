
"""Label Studio utils."""

import os


def format(base_dir):
    def f(page):
        for comment in page.comments:
            yield {
                'data': {
                    'image': os.path.join(base_dir, page.img_name),
                    'text': comment['text'],
                }
            }
    return f
