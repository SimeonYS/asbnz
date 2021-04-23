import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AsbnzItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.asb.co.nz/content/asb/blog/en/blog/blog-data.js.bh..{}.html?u=L2Jsb2c='


class AsbnzSpider(scrapy.Spider):
	name = 'asbnz'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['results'])):
			link = data['results'][index]['link']
			date = data['results'][index]['publishedDate']
			title = data['results'][index]['title']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		if len(data['results']) == 24:
			self.page += 24
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@data-text-image="text-image-bullet"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "", ' '.join(content))

		item = ItemLoader(item=AsbnzItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()





