import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import ObsrsItem
from itemloaders.processors import TakeFirst


class ObsrsSpider(scrapy.Spider):
	name = 'obsrs'
	start_urls = ['https://www.obs.rs/mediji/novosti/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news-content"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//article[@class="pagination full"]//a[text()="»"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()[normalize-space()]').get()
		description = response.xpath('//div[@class="contained-9 centered body-copy"]//text()[normalize-space() and not(ancestor::em)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//em/text()').get()

		item = ItemLoader(item=ObsrsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
