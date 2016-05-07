import json
from scrapy.utils.project import get_project_settings

import scrapy
from scrapy.crawler import CrawlerProcess
from spiders import NOAASpider

settings = get_project_settings()
settings.set('BOT_NAME', 'lpbcbot')
settings.set('LOG_LEVEL', 'ERROR')
settings.set('ITEM_PIPELINES', {
    'pipelines.ReplyTwitterPipeline': 100
})

process = CrawlerProcess(settings)
process.crawl(NOAASpider)
process.start()
