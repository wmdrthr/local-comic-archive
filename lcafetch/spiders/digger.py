from urllib.parse import urlparse

import scrapy

import lcafetch.spiders

class Digger(lcafetch.spiders.ComicSpider):

    name = 'digger'
    comic_name = 'Digger'
    start_url = 'https://diggercomic.com/blog/2007/02/01/wombat1-gnorf/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        _, _, year, month, day, _, _ = path.split('/')
        tag = int(year + month + day)

        images = [response.xpath('//div[@id="comic"]/img/@src').get()]

        annotations = response.xpath('//div[@class="entry"]/p').getall()

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
