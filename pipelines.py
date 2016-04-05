import json
from scrapy.conf import settings

class TwitterPipeline(object):
	def process_item(self, item, spider):
		print(item)
		return item