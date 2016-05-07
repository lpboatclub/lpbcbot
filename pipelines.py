import os
import json
import time
import sqlite3
import tweepy
import constants
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
        sql_session = self.get_sql_session()
        twitter_session = self.get_twitter_session()
        mentions = twitter_session.mentions_timeline()
        status = self.compose_status(item)
        for mention in mentions:
            # check if we've already replied to this @mention
            if not self.replied_to_mention(mention, sql_session):
                reply = u"@{user_name} {status}".format(
                    user_name=mention.user.screen_name,
                    status=status
                )
                print("replying to {user_name}".format(user_name=mention.user.screen_name))
                # twitter_session.update_status(reply, mention.id)
        self.mark_mentions_as_replied_to(mentions, sql_session)
        self.close_sql_session(sql_session)
        return item

    def get_sql_session(self):
        # creates a sqlite file if there isn;t one
        return sqlite3.connect(constants.sqlite_file)

    def close_sql_session(self, session):
        # commit and close
        session.commit()
        session.close()

    def replied_to_mention(self, mention, session):
        c = session.cursor()
        query = 'SELECT {col} FROM {tn} WHERE {col} = ?'\
                .format(tn=constants.table_replies, col=constants.field_mention_id);
        c.execute(query, (mention.id,))
        result = c.fetchone()
        return result is not None

    # keep track of all tweets replied to in the DB
    def mark_mentions_as_replied_to(self, mentions, session):
        c = session.cursor()
        for mention in mentions:
            c.execute('INSERT OR IGNORE INTO {tn} ({col}) VALUES ({val})'\
                    .format(tn=constants.table_replies, col=constants.field_mention_id, val=mention.id))
