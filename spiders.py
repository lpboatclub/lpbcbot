import re
import json
import unicodedata
import scrapy
import boto3
from datetime import datetime
from base64 import b64decode

RAW_OPEN_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?id=4887398&units=Imperial&APPID=%s'
ENCRYPTED_OPEN_WEATHER_TOKEN = 'CiD4po0KRHJC5lcDVGrsm/Lks1Dbm6B7kZGLrkeSnt1rNhKnAQEBAgB4+KaNCkRyQuZXA1Rq7Jvy5LNQ25uge5GRi65Hkp7dazYAAAB+MHwGCSqGSIb3DQEHBqBvMG0CAQAwaAYJKoZIhvcNAQcBMB4GCWCGSAFlAwQBLjARBAy5EgRNIyBfvqfhoewCARCAO4R6cYpYrES5c6iQuSDbGs5M78Kg0pU5LIR1BE6ITlz0RrI6unhVU7ueFaLBa18lvNytt7NPgG+fyz7k'
kms = boto3.client('kms')

class NOAASpider(scrapy.Spider):
    name = 'noaaspider'
    start_urls = ['http://forecast.weather.gov/product.php?site=LOT&issuedby=LOT&product=OMR&format=txt&version=1&glossary=1']

    def open_weather_url(self):
		open_weather_token = kms.decrypt(CiphertextBlob = b64decode(ENCRYPTED_OPEN_WEATHER_TOKEN))['Plaintext']
		return RAW_OPEN_WEATHER_URL % open_weather_token

    def parse(self, response):
    	raw_text = response.css('.glossaryProduct').xpath('./text()')
    	conditions = {'units':'imperial'}
    	raw_chicago_shore = raw_text.re(re.compile('CHICAGO SHORE\.*\d+', re.IGNORECASE))[0]
    	conditions['chicago_shore'] = self.parse_temp(raw_chicago_shore)
    	raw_chicago_crib = raw_text.re(re.compile('CHICAGO CRIB\.*\d+', re.IGNORECASE))[0]
    	conditions['chicago_offshore'] = self.parse_temp(raw_chicago_crib)
    	openweather_request = scrapy.Request(self.open_weather_url(), callback=self.parse_open_weather_map)
    	openweather_request.meta['conditions'] = conditions
    	yield openweather_request

    def parse_open_weather_map(self, response):
    	conditions = response.meta['conditions']
    	json_response = json.loads(response.body_as_unicode())
    	conditions['temp'] = json_response['main']['temp']
    	conditions['temp_high'] = json_response['main']['temp_min']
    	conditions['temp_low'] = json_response['main']['temp_max']
    	conditions['wind'] = json_response['wind']['speed']
    	conditions['combined_air_water'] = float(conditions['temp']) + float(conditions['chicago_shore'])
    	conditions['safe_to_row'] = conditions['combined_air_water'] >= 100
    	conditions['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    	return conditions

    def parse_temp(self, temp_str):
    	return re.search('\d+', temp_str).group(0).encode('utf-8')
