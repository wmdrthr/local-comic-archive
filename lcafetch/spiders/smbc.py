import re
from urllib.parse import urlparse

import scrapy

import lcafetch.spiders

class SMBC(lcafetch.spiders.ComicSpider):

    name = 'smbc'
    comic_name = 'Saturday Morning Breakfast Cereal'
    start_url = 'https://www.smbc-comics.com/comic/2002-09-05'
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        comic_date = path.split('/')[-1]
        tag = int(''.join(comic_date.split('-')))

        img = response.xpath('//img[@id="cc-comic"]')

        images = [img.attrib['src']]
        captions = [img.attrib['title'].strip()]

        extra_image = response.xpath('//div[@id="aftercomic"]/img/@src').get()
        images.append(extra_image)

        title_text = response.xpath('//head/title/text()').get()
        title = title_text.split(' - ')[-1]
        if self.date_pattern.match(title) is not None:
            title = None

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
