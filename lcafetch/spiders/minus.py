from urllib.parse import urljoin
from datetime import datetime

import scrapy

import lcafetch.spiders

class Minus(lcafetch.spiders.ComicSpider):

    name = 'minus'
    start_url = 'https://kiwisbybeat.netlify.app/minus1.html'

    def start_requests(self):

        return [scrapy.Request('https://kiwisbybeat.netlify.app/minusarchive.html', self.parse_archive)]

    def parse_next(self, response):

        next_link = response.xpath('//a[contains(text(), "next")]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse_archive(self, response):

        self.archive = {}
        for link in response.xpath('//table//td/center/a'):
            comic_url = urljoin(response.url, link.attrib['href'])
            comic_date = link.xpath('preceding-sibling::text()[1]')
            comic_date = datetime.strptime(comic_date.get().strip(), '%d/%m/%y:')

            self.archive[comic_url] = comic_date

        return super().start_requests()

    def parse(self, response):

        comic_date = self.archive[response.url]
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [response.xpath('//td/center/img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
