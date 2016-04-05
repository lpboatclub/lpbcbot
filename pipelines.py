import json
from twython import Twython
import boto3
from base64 import b64decode
from keys import Key
from emoji import Emoji


class TwitterPipeline(object):
    tweet_sent = False

    def process_item(self, item, spider):
        twitter_session = self.get_twitter_session()
        twitter_session.update_status(status=self.compose_status(item))
        return item

    def get_twitter_session(self):
        kms = boto3.client('kms')
        consumer_key = kms.decrypt(CiphertextBlob = b64decode(Key.ENCRYPTED_TWITTER_CONSUMER_KEY.value))['Plaintext']
        consumer_secret = kms.decrypt(CiphertextBlob = b64decode(Key.ENCRYPTRD_TWITTER_COMSUMER_SECRET.value))['Plaintext']
        access_token = kms.decrypt(CiphertextBlob = b64decode(Key.ENCRYPTED_TWITTER_ACCESS_TOKEN.value))['Plaintext']
        access_token_secret = kms.decrypt(CiphertextBlob = b64decode(Key.ENCRYPTED_TWITTER_ACCESS_TOKEN_SECRET.value))['Plaintext']
        return Twython(consumer_key, consumer_secret,
                       access_token, access_token_secret)

    
    def compose_status(self, item):
        return u'Air: {air_temp} \u00B0F Water: {water_temp} \u00B0F\nWind: {wind_speed} MPH from {wind_direction}\nSafe To Row: {safe_to_row}'.format(air_temp=item['temp'],
                                                                                                                                water_temp=item['chicago_shore'],
                                                                                                                                wind_speed=item['wind'],
                                                                                                                                wind_direction=self.get_direction_from_degrees(item['wind_degs']),
                                                                                                                                safe_to_row=self.is_safe_to_row(item['safe_to_row']))

    def get_direction_from_degrees(self, degrees):
        offset = (degrees/22.5) + .5 # 260 / 16 = 22.5 and .5 breaks the tie
        directions = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        return directions[int(offset) % 16]

    def is_safe_to_row(self, safe_to_row):
        return Emoji.ROWING.value if safe_to_row else Emoji.NO_ROWING.value