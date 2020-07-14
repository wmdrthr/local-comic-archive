from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class OOTS(lcafetch.spiders.ComicSpider):

    name = 'orderofthestick'
    comic_name = 'Order of the Stick'
    start_url = 'https://www.giantitp.com/comics/oots0001.html'

    def parse_next(self, response):

        next_link = response.xpath('//img[@alt="Next Comic"]/parent::a/@href').get()
        if next_link is not None:
            next_url = urljoin(response.url, next_link)
            if next_url != response.url:
                return scrapy.Request(next_url, callback=self.parse)
            else:
                return None
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        tag = path.split('/')[-1]
        tag = int(tag[4:-5])

        title = response.xpath('//td[@align="center"]/b/text()').get()

        images = [response.xpath('//td[@align="center"]/img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
