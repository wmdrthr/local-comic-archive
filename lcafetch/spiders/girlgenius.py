from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class GirlGenius(lcafetch.spiders.ComicSpider):

    name = 'girlgenius'
    start_url = 'http://www.girlgeniusonline.com/comic.php?date=20021104'

    def parse_next(self, response):

        next_link = response.xpath('//a[@id="topnext"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['date'][0])

        img_url = response.xpath('//img[@alt="Comic"]/@src').get()
        images = [img_url]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
