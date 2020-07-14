from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class Sequential(lcafetch.spiders.ComicSpider):

    name = 'sequentialart'
    comic_name = 'Sequential Art'
    start_url = 'https://www.collectedcurios.com/sequentialart.php?s=1'

    def parse_next(self, response):

        next_link = response.xpath('//img[@title="Forward one"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['s'][0])

        img_url = response.xpath('//img[@id="strip"]/@src').get()
        images = [urljoin(response.url, img_url)]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
