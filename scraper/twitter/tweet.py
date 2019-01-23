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
        }

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
