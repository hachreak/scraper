
"""Instagram post."""

import json

from copy import deepcopy


class DeletedPost(Exception):

    pass


class Post(object):

    def __init__(self, raw):
        """Init."""
        self._raw = deepcopy(raw)

        self._info = {
            "comments": {
                "count": len(self.comments),
                "conversations": self.comments,
            },
            "text": self.text,
            "id": self.id,
            "image": self.imgs,
            "likes": self.likes,
            "time": self.time,
            "username": self.owner['username'],
            "owner": self.owner,
            "video": self.video,
            "hashtags": self.hashtags,
            "location": self.location,
        }

    @property
    def comments(self):
        try:
            return [c['node'] for c in self._raw['_post']['graphql'][
                'shortcode_media']['edge_media_to_comment']['edges']]
        except KeyError:
            return []

    @property
    def text(self):
        # TODO check if can be more than one caption
        try:
            return self._raw['_post']['graphql']['shortcode_media'][
                    'edge_media_to_caption']['edges'][0]['node']['text']
        except KeyError:
            return ''
        except IndexError:
            return ''

    @property
    def id(self):
        try:
            return self._raw['_post']['graphql']['shortcode_media'][
                    'shortcode']
        except KeyError:
            raise DeletedPost()

    @property
    def imgs(self):
        list_imgs = self._raw['node']['thumbnail_resources'] + \
                self._raw['_post']['graphql']['shortcode_media'][
                        'display_resources']

        imgs = {}
        for i in list_imgs:
            imgs['{0}x{1}'.format(i['config_width'], i['config_height'])] = \
                    i['src']
        return imgs

    @property
    def likes(self):
        return self._raw['_post']['graphql']['shortcode_media'][
            'edge_media_preview_like']['count']

    @property
    def time(self):
        return self._raw['_post']['graphql']['shortcode_media'][
            'taken_at_timestamp']

    @property
    def owner(self):
        return self._raw['_post']['graphql']['shortcode_media']['owner']

    @property
    def video(self):
        sh = self._raw['_post']['graphql']['shortcode_media']
        if sh['is_video']:
            return {
                'views': sh['video_view_count'],
                'duration': sh['video_duration'],
                'preview': sh['thumbnail_src'],
            }

    @property
    def hashtags(self):
        return set([
            t.strip().lower()
            for t in self.text.split(' ') if t.startswith('#')
        ])

    @property
    def location(self):
        sh = self._raw['_post']['graphql']['shortcode_media']
        if sh['location']:
            sh['location']['address_json'] = json.loads(
                    sh['location'].get('address_json') or '{}'
            )
        return sh['location']
