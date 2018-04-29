import os
import re
import json
import unicodedata
import scrapy
from datetime import datetime

RAW_OPEN_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?lat=41.923618&lon=-87.631961&units=Imperial&APPID=%s'

class NOAASpider(scrapy.Spider):
    name = 'noaaspider'
    start_urls = ['http://forecast.weather.gov/product.php?site=LOT&issuedby=LOT&product=OMR&format=txt&version=1&glossary=1']

    def open_weather_url(self):
        return RAW_OPEN_WEATHER_URL % os.environ['OPEN_WEATHER_TOKEN']

    def parse(self, response):
        raw_text = response.css('.glossaryProduct').xpath('./text()')
        conditions = {'units':'imperial'}
        raw_chicago_shore = raw_text.re(re.compile('CHICAGO SHORE\.*\d+', re.IGNORECASE))[0]
        conditions['chicago_shore'] = self.truncate(float(self.parse_temp(raw_chicago_shore)))
        raw_chicago_crib = raw_text.re(re.compile('CHICAGO CRIB\.*\d+', re.IGNORECASE))[0]
        conditions['chicago_offshore'] = self.truncate(float(self.parse_temp(raw_chicago_crib)))
        openweather_request = scrapy.Request(self.open_weather_url(), callback=self.parse_open_weather_map)
        openweather_request.meta['conditions'] = conditions
        yield openweather_request

    def parse_open_weather_map(self, response):
        conditions = response.meta['conditions']
        json_response = json.loads(response.body_as_unicode())
        conditions['temp'] = self.truncate(json_response['main']['temp'])
        conditions['temp_high'] = json_response['main']['temp_min']
        conditions['temp_low'] = json_response['main']['temp_max']
        conditions['wind'] = self.truncate(json_response['wind']['speed'])
        try: conditions['wind_degs'] = json_response['wind']['deg']
        except KeyError: conditions['wind_degs'] = 'N/A'
        conditions['weather'] = json_response['weather'][0]
        conditions['combined_air_water'] = self.truncate(float(conditions['temp']) + float(conditions['chicago_shore']))
        conditions['safe_to_row'] = int(conditions['combined_air_water']) >= 100
        conditions['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return conditions

    def parse_temp(self, temp_str):
        return re.search('\d+', temp_str).group(0).encode('utf-8')

    def truncate(self, num):
        return '{number:.{prec}f}'.format(number=num, prec=0)
