import os
import re
from urllib.parse import urlparse

import scrapy

import lcafetch.spiders

class Copper(lcafetch.spiders.ComicSpider):

    name = 'copper'
    comic_name = 'Copper'
    start_url = 'https://www.boltcityproductions.com/copper'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options.add('no_subdirs')

    def process_page(self, response):

        items = []
        for img in response.xpath('//img[@class="thumb-image"]'):
            img_url = img.attrib['data-src']
            images = [img_url]

            path = urlparse(img_url).path
            filename, _ = os.path.splitext(os.path.basename(path))
            _, tag, title = filename.split('_', 2)
            title = re.sub(r'_', r' ', title).title()
            if title[-1] == '1':
                title = title[:-1]

            items.append({'tag': int(tag),
                          'url': response.url,
                          'title': title,
                          'file_urls': images})
        return items

    def parse(self, response):

        if 'items' in response.meta:
            items = response.meta['items']
            yield items[0]
            yield scrapy.Request(self.start_url,
                                  callback = self.parse,
                                  meta = {'items': items[1:]})
        else:
            items = self.process_page(response)
            already_scraped = self.prevtag and self.prevtag or 0
            if items and len(items) > already_scraped:
                items = sorted([item for item in items if item['tag'] > already_scraped],
                               key=lambda item: item['tag'])
                yield items[0]
                yield scrapy.Request(self.start_url,
                                     callback = self.parse,
                                     meta = {'items': items[1:]})
            else:
                yield None

    parse_next = parse
