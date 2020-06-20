from urllib.parse import urljoin
from datetime import datetime

import scrapy

import lcafetch.spiders

class Failures(lcafetch.spiders.ComicSpider):

    name = 'failures'
    start_url = 'https://betweenfailures.com/comics1/every-story-has-to-start-somewhere'

    def parse_next(self, response):

        next_link = response.xpath('//aside[@id="next"]/a/@href').get()
        next_link = urljoin(response.url, next_link)
        if next_link != response.url:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//div[@class="timestamp"]/a/time/text()').get()
        comic_date = datetime.strptime(comic_date, '%B %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [urljoin(response.url, response.xpath('//div[@class="webcomic-image"]/a/img/@src').get())]

        title_text = response.xpath('//head/title/text()').get()
        title_text, _ = title_text.split('–')
        title = title_text.strip()

        annotations = []
        for node_text in response.xpath('//article[@role="article"]/div/p').getall():
            if 'Comic Vote' in node_text:
                continue
            annotations.append(node_text)

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
