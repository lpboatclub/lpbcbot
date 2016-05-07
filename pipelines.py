import os
import json
import tweepy
from emoji import Emoji

class TwitterPipeline(object):
    message = u'Air: {air_temp} \u00B0F\nWater: {water_temp} \u00B0F\nWind: {wind_speed} MPH {wind_direction}\nCombined Air + Water: {combined_air_water} \u00B0F {safe_to_row}'

    def process_item(self, item, spider):
        twitter_session = self.get_twitter_session()
        twitter_session.update_status(status=self.compose_status(item))
        return item

    def get_twitter_session(self):
        CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
        CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
        ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return tweepy.API(auth)


    def compose_status(self, item):
        return self.message.format(
            air_temp=item['temp'],
            water_temp=item['chicago_shore'],
            wind_speed=item['wind'],
            wind_direction=self.get_direction_from_degrees(item['wind_degs']),
            combined_air_water=item['combined_air_water'],
            safe_to_row=self.is_safe_to_row(item['safe_to_row'])
        )

    def get_direction_from_degrees(self, degrees):
        if degrees == 'N/A':
            return ''
        offset = (degrees/22.5) + .5 # 260 / 16 = 22.5 and .5 breaks the tie
        directions = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        return 'from ' + directions[int(offset) % 16]

    def is_safe_to_row(self, safe_to_row):
        return Emoji.ROWING.value if safe_to_row else Emoji.NO_ROWING.value

class ReplyTwitterPipeline(TwitterPipeline):
    def process_item(self, item, spider):
        twitter_session = self.get_twitter_session()
        mentions = twitter_session.mentions_timeline()
        status = self.compose_status(item)
        for mention in mentions:
            tweet_id = mention.id
            print("Replying to @{user_name} with id {id}".format(
                user_name=mention.user.screen_name,
                id=mention.id
            ))
            reply = u"@{user_name} {status}".format(
                user_name=mention.user.screen_name,
                status=status
            )
            # twitter_session.update_status(reply, mention.id)

        return item
