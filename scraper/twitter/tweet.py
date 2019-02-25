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

import os


from ..exc import UnknowObject


video_url = 'https://twitter.com/i/videos/tweet/{0}'
tweet_url = 'https://twitter.com/{0}/status/{1}'
gif_url = 'https://video.twimg.com/tweet_video/{0}.mp4'


def iterate_tweets(tweet):
    yield tweet
    for conversation in tweet['comments']['conversations']:
        for comment in conversation:
            yield comment


class Tweet(object):

    @classmethod
    def get_url(cls, username, id_):
        return tweet_url.format(username[1:], id_)


class TweetFromScroll(Tweet):

    @classmethod
    def get_id(cls, soup):
        return soup.get('data-item-id')

    @classmethod
    def get_username(self, soup):
        try:
            return soup.find('span', attrs={'class': 'username'}).text
        except AttributeError:
            return ''

    @classmethod
    def get_html_tag(cls, soup):
        """Get tweets from html soup."""
        return [
            t for t in soup.body.findAll('li', attrs={'class': 'stream-item'})
        ]


class TweetFromPage(Tweet):

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
            'video': self.video,
            'gif': self.gif,
        }

    @property
    def conversations_count(self):
        try:
            return len(self.raw_conversations)
        except ValueError:
            return 0
        except AttributeError:
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
            return self._soup.find(
                'a', attrs={'class': 'account-group'}
            ).find('span', attrs={'class': 'username'}).text
        except AttributeError:
            return ''

    @property
    def fullname(self):
        try:
            return self._soup.find('strong', attrs={'class': 'fullname'}).text
        except AttributeError:
            return ''

    @property
    def hashtags(self):
        try:
            links = self._soup.find(
                'p', attrs={'class': 'tweet-text'}
            ).findAll('a', attrs={'data-query-source': 'hashtag_click'})
            return [a.text.strip().lower() for a in links]
        except AttributeError:
            return []

    @property
    def likes(self):
        try:
            return int(self._soup.find(
                'div', attrs={'class': 'ProfileTweet-action--favorite'}
            ).find(
                'span', attrs={
                    'class': 'ProfileTweet-actionCountForPresentation'
                }
            ).text)
        except AttributeError:
            return 0
        except ValueError:
            return 0

    @property
    def retweets(self):
        try:
            return int(self._soup.find(
                'div', attrs={'class': 'ProfileTweet-action--retweet'}
            ).find(
                'span', attrs={
                    'class': 'ProfileTweet-actionCountForPresentation'
                }
            ).text)
        except AttributeError:
            return 0
        except ValueError:
            return 0

    @property
    def permalink(self):
        try:
            return self._soup.find(
                'div', attrs={'class': 'tweet'}
            ).get('data-permalink-path', '')
        except AttributeError:
            return ""

    @property
    def id(self):
        try:
            return self._soup.find(
                'div', attrs={'class': 'tweet'}
            ).get('data-tweet-id')
        except AttributeError:
            raise UnknowObject()

    @property
    def time(self):
        try:
            return self._soup.find(
                'span', attrs={'class': '_timestamp'}
            ).get('data-time')
        except AttributeError:
            return None

    @property
    def url(self):
        return self.get_url(self._info['username'][1:], self._info['id'])

    @property
    def video(self):
        video = self._soup.find('video')
        if video:
            return {
                'poster': video.attrs['poster'],
                'src': video_url.format(self.id),
            }

    @property
    def gif(self):
        if not self.video:
            tag = self._soup.find(
                'div', attrs={'class': 'PlayableMedia-player'})
            if tag:
                img = tag.get('style').split(
                    'tweet_video_thumb/')[1].split("'")[0]
                filename = os.path.splitext(img)[0]
                return gif_url.format(filename)

    @classmethod
    def get_tweets(cls, soup):
        """Get tweets from html soup."""
        return [
            Tweet(t)
            for t in soup.body.findAll('li', attrs={'class': 'stream-item'})
        ]


class TweetFlowFromPage(TweetFromPage):

    def __init__(self, soup):
        super(TweetFlowFromPage, self).__init__(soup)
        self._info['comments'] = {
            'count': self.conversations_count,
            'total': 0,
            'conversations': [],
        }
        if self._info['comments']['count'] > 0:
            self.add_conversations()

    @property
    def comments(self):
        return self._info['comments'].get('conversations', [])

    @classmethod
    def iterate(cls, tweet_info):
        """Iterate throw tweet and its comments."""
        yield tweet_info
        if tweet_info['comments']['total'] > 0:
            for c in tweet_info['comments']['conversations']:
                for conv in c:
                    yield conv

    @property
    def raw_conversations(self):
        return self._soup.select(
            'div.stream-container > .stream > ol.stream-items > li')

    def add_conversations(self):
        for conv in self.raw_conversations:
            self.add_conversation([
                Comment(c)._info for c in Comment.raw_comments(conv)
            ])

    def add_conversation(self, conversation):
        self._info['comments']['conversations'].append(conversation)
        self._info['comments']['total'] += len(conversation)


class Comment(TweetFromPage):

    @classmethod
    def raw_comments(cls, soup):
        return soup.findAll('li', attrs={'class': 'stream-item'})

    @classmethod
    def count(cls, soup):
        return len(cls.raw_comments(soup))


def get_ancestor(soup):
    class Ancestor(object):
        def __init__(self, soup):
            self._soup = soup

        def username(self):
            return self._soup.find(
                'span', attrs={'class': 'username'}).text[1:]

        def id(self):
            return self._soup.find(
                'div', attrs={'class': 'tweet'}).get('data-tweet-id')

    anc = soup.find('div', attrs={'id': 'ancestors'})
    if anc:
        return Ancestor(anc)
