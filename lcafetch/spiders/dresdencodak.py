from urllib.parse import urlparse

import scrapy

import lcafetch.spiders

class DresdenCodak(lcafetch.spiders.ComicSpider):

    name = 'dresdencodak'
    comic_name = 'Dresden Codak'
    start_url = 'http://dresdencodak.com/2005/06/08/the-tomorrow-man/'

    def parse_next(self, response):

        next_link = response.xpath('//img[@alt="Next Page"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback=self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        year, month, day = path.split('/')[1:4]
        tag = int(year + month + day)

        title = response.xpath('//header[@class="entry-header"]/h1/text()').get()
        title = title.strip()

        images = [response.xpath('//section[@class="entry-content "]//p/img/@src').get()]

        yield {'tag': tag,
               'title': title,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
