import re
from datetime import datetime

import scrapy

import lcafetch.spiders

class Wondermark(lcafetch.spiders.ComicSpider):

    name = 'wondermark'
    comi_name = 'Wondermark'
    start_url = 'http://wondermark.com/001/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        date_text = response.xpath('//div[@id="comic-notes"]//em/text()').get()
        comic_date = datetime.strptime(re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_text),
                                       '%B %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        img = response.xpath('//div[@id="comic"]/img')
        images = [img.attrib['src']]
        captions = [img.attrib['alt']]

        title_text = response.xpath('//head/title/text()').get()
        title_text = title_text.split('»')[-1]
        title = title_text.strip()

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
