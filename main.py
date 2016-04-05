import json
from scrapy.utils.project import get_project_settings

import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from spiders import NOAASpider

settings = get_project_settings()

settings.set('BOT_NAME', 'lpbcbot')
settings.set('LOG_LEVEL', 'ERROR')
settings.set('ITEM_PIPELINES', {
    'pipelines.TwitterPipeline': 100
})

def lambda_handler(event, context):
	self.start_crawl()
	return 'finished crawl at {now}'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def start_crawl(self):
	process = CrawlerProcess(settings)
	process.crawl(NOAASpider)
	process.start() # the script will block here until all crawling jobs are finished
