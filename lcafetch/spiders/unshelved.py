from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class Unshelved(lcafetch.spiders.ComicSpider):

    name = 'unshelved'
    start_url = 'http://www.unshelved.com/2002-2-16'

    def parse_next(self, response):

        if response.url == 'http://www.unshelved.com/2016-11-11':
            return None
        else:
            next_link = response.xpath('//a[@id="nav-next"]/@href').get()
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)

    def parse(self, response):

        path = urlparse(response.url).path
        comic_date = path.split('/')[-1]
        year, month, day = [int(x) for x in comic_date.split('-')]
        tag = year * 10000 + month * 100 + day

        images = [response.xpath('//div[@id="comic-content"]/div[3]//img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
