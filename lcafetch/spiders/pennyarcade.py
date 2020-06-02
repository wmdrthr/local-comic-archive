from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class PennyArcade(lcafetch.spiders.ComicSpider):

    name = 'pennyarcade'
    start_url = 'https://www.penny-arcade.com/comic/1998/11/18'

    def parse_next(self, response):

        next_link = response.xpath('//a[@class="btn btnNext"]/@href').get()
        if next_link != '#':
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        year, month, day = path.split('/')[2:5]
        tag = int(year + month + day)

        title_text = response.xpath('//head/title/text()').get()
        title = title_text.split('-', 2)[-1].strip()

        images = [response.xpath('//div[@id="comicFrame"]//img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
