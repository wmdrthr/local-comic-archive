from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class Bruno(lcafetch.spiders.ComicSpider):

    name = 'bruno'
    start_url = 'http://brunothebandit.com/d/19980720.html'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)
        else:
            return None

    def parse(self, response):

        img = response.xpath('//img[@class="ksc"]')[0]

        title = img.xpath('following-sibling::center/text()').get()
        title = title.strip()

        path = urlparse(response.url).path
        tag = int(path[3:-5])

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': [urljoin(response.url, img.attrib['src'])]}

        yield self.parse_next(response)
