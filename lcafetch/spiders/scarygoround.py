from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class ScaryGoRound(lcafetch.spiders.ComicSpider):

    name = 'scarygoround'
    comic_name = 'Scary Go Round'
    start_url = 'http://www.scarygoround.com/sgr/ar.php?date=20020604'

    def parse_next(self, response):

        if response.url == 'http://www.scarygoround.com/sgr/ar.php?date=20090911':
            return None
        next_link = response.xpath('//a[contains(text(), "Next")]/@href').get()
        return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['date'][0])

        images = []
        for img_url in response.xpath('//div[@align="center"]//img/@src').getall():
            if 'strips/' in img_url:
                images.append(urljoin(response.url, img_url))

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
