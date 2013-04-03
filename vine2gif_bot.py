#!/usr/bin/env python
# Twitter Bot to cnvert Vine URL's into animated GIF's
# This will end up getting banned pretty quick.
# BE WARNED! This is only ment to be a toy.
# I've hard coded paths and shit in here, you may want to change them...
# @gerryeisenhaur
import os
import re
import json
import envoy
import urllib
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

import vine2gif

consumer_key = "XXXXXXXXXX"
consumer_secret = "XXXXXXXXXX"

access_token = "XXXXXXXXXX"
access_token_secret = "XXXXXXXXXX"


class Vine2GIFListener(StreamListener):

    def on_data(self, data):
        self.on_status(data)

    def convert_movie(self, vine_url):
        output_name = vine_url.split('/')[-1].split("?", 1)[0]
        if not vine_url.startswith("http"):
            vine_url = "https://" + vine_url
        movie_path = vine2gif.download_movie(vine_url)
        gif = vine2gif.make_gif(movie_path, output_name)
        imgur_url = envoy.run(str('/Users/gerry/bin/imgur %s' % gif))
        try:
            os.remove(os.path.join(os.path.curdir, gif))
        except:
            # yea ahh why this fails, dont know yet
            print "Couldnt remove %s" % gif
        return imgur_url.std_out.strip()

    def on_status(self, status):
        try:
            status = json.loads(status)
        except ValueError, e:
            return

        # ignore some messages
        username = status.get('user', {}).get('screen_name')
        if (status.get('event', False) or  # Favorite, etc
            status.get('retweet_count', 0) or  # A retweet
            status.get('in_reply_to_status_id', 0) or  # replies
            username == 'vine2gif'):  # Self-tweets
            return True

        entities = status.get('entities', {})
        for url in entities.get('urls', {}):
            if url.get('display_url', '').startswith('vine.co/v/'):
                #print username, url.get('expanded_url')
                gif_url = self.convert_movie(url.get('expanded_url'))
                if gif_url:
                    msg = "Before: %s After: %s" % (url.get('display_url'),
                                                    gif_url)
                    api.update_status(msg)
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    listener = Vine2GIFListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth)
    print "Vine2GIF started as: %s" % API(auth).me().name
    stream = Stream(auth=auth, listener=listener)
    stream.filter(track=('vine',))
