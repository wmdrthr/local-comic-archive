import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

import lcafetch.spiders

class PVP(lcafetch.spiders.ComicSpider):

    name = 'pvp'
    start_url = 'http://pvponline.com/comic/mon-may-04'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options.add('rename_images')

    def parse_next(self, response):

        next_link = response.xpath('//div[@class="comic-nav left"]/a[@class="left"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//div[@class="comic-date right"]/text()').get()
        comic_date = datetime.strptime(comic_date.strip(), '%m/%d/%Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [response.xpath('//section[@class="comic-art"]/img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
