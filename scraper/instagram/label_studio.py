
"""Label Studio utils."""


def format_instagram_label_studio(page):
    for comment in page.comments:
        yield {
            'data': {
                'image': page.img_name,
                'text': comment['text'],
            }
        }
