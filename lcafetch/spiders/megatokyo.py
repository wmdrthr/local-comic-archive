from urllib.parse import urljoin
from datetime import datetime
import re

import scrapy

import lcafetch.spiders

class Megatokyo(lcafetch.spiders.ComicSpider):

    name = 'megatokyo'
    start_url = 'https://megatokyo.com/strip/1'
    baseurl = 'http://www.megatokyo.com'

    def parse_next(self, response):

        next_link = response.xpath('//li[@class="next"]/a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(self.baseurl, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        img = response.xpath('//span[@id="strip-bl"]//img')

        title_text = img.attrib['title']
        title, *_, date = title_text.split(',', 3)

        date = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date)
        comic_date = datetime.strptime(date.strip(), '%B %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [urljoin(self.baseurl, img.attrib['src'])]

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
