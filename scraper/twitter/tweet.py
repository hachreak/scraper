# -*- coding: utf-8 -*-
#
# This file is part of scraper.
# Copyright 2018-2019 Leonardo Rossi <leonardo.rossi@studenti.unipr.it>.
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

"""Tweet."""


video_url = 'https://twitter.com/i/videos/tweet/{0}'


class Tweet(object):

    def __init__(self, soup):
        self._soup = soup
        self._info = {
            'image': self.image,
            'text': self.text,
            'username': self.username,
            'fullname': self.fullname,
            'hashtags': self.hashtags,
            'likes': self.likes,
            'retweets': self.retweets,
            'permalink': self.permalink,
            'id': self.id,
            'time': self.time,
            'comments': {
                'count': self.comments_count,
                'total': 0,
                'conversations': [],
            },
            'video': self.video,
        }

    @property
    def comments_count(self):
        try:
            return int(self._soup.find('span', attrs={
                'class': 'ProfileTweet-actionCountForPresentation'
            }).text)
        except ValueError:
            return 0

    @property
    def text(self):
        try:
            return self._soup.find('p', attrs={'class': 'tweet-text'}).text
        except AttributeError:
            pass

    @property
    def image(self):
        try:
            imgs = self._soup.findAll(
                'div', attrs={'class': 'AdaptiveMedia-photoContainer'}
            )
            return [i.get('data-image-url') for i in imgs]
        except AttributeError:
            pass

    @property
    def username(self):
        try:
            return self._soup.find('span', attrs={'class': 'username'}).text
        except AttributeError:
            pass

    @property
    def fullname(self):
        try:
            return self._soup.find('strong', attrs={'class': 'fullname'}).text
        except AttributeError:
            pass

    @property
    def hashtags(self):
        links = self._soup.find('p').findAll(
            'a', attrs={'data-query-source': 'hashtag_click'}
        )
        return [a.text for a in links]

    @property
    def likes(self):
        return self._soup.find(
            'div', attrs={'class': 'ProfileTweet-action--favorite'}
        ).find(
            'span', attrs={'class': 'ProfileTweet-actionCountForPresentation'}
        ).text

    @property
    def retweets(self):
        return self._soup.find(
            'div', attrs={'class': 'ProfileTweet-action--retweet'}
        ).find(
            'span', attrs={'class': 'ProfileTweet-actionCountForPresentation'}
        ).text

    @property
    def permalink(self):
        return self._soup.find(
            'div', attrs={'class': 'tweet'}
        )['data-permalink-path']

    @property
    def id(self):
        return self._soup['data-item-id']

    @property
    def time(self):
        return self._soup.find(
            'span', attrs={'class': '_timestamp'}
        )['data-time']

    @property
    def url(self):
        return 'https://twitter.com/{0}/status/{1}'.format(
            self._info['username'][1:], self._info['id']
        )

    @property
    def comments(self):
        return self._info['comments'].get('conversations', [])

    @property
    def video(self):
        video = self._soup.find('video')
        if video:
            return {
                'poster': video.attrs['poster'],
                'src': video_url.format(self.id),
            }

    def add_conversation(self, conversation):
        self._info['comments']['conversations'].append([
            c._info for c in conversation
        ])
        self._info['comments']['total'] += len(conversation)

    @classmethod
    def get_tweets(cls, soup):
        """Get tweets from html soup."""
        return [
            Tweet(t)
            for t in soup.body.findAll('li', attrs={'class': 'stream-item'})
        ]


class Comment(Tweet):

    @classmethod
    def conversations(cls, soup):
        """Get the all conversions."""
        return soup.findAll(
            'li', attrs={'class': 'ThreadedConversation--loneTweet'}
        ) + soup.findAll(
            'li', attrs={'class': 'ThreadedConversation'}
        )

    @classmethod
    def raw_comments(cls, soup):
        return soup.findAll('li', attrs={'class': 'stream-item'})

    @classmethod
    def count(cls, soup):
        return len(cls.raw_comments(soup))
