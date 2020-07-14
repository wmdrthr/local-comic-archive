import scrapy

import lcafetch.spiders

class EightBit(lcafetch.spiders.ComicSpider):

    name = 'eightbit'
    comic_name = '8-Bit Theater'
    start_url = 'https://www.nuklearpower.com/2001/03/02/episode-001-were-going-where/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback=self.parse)
        else:
            return None

    def parse(self, response):

        year, month, day = response.url.split('/')[-5:-2]
        tag = int(year + month + day)

        title = response.xpath('//div[@class="navbar-title"]/text()').get()
        title = title.strip()

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        yield {'tag': tag,
               'title': title,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
