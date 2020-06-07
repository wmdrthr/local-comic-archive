from urllib.parse import urlparse, parse_qs

import scrapy

import lcafetch.spiders

class Nodwick(lcafetch.spiders.ComicSpider):

    name = 'nodwick'
    start_url = 'http://comic.nodwick.com/?comic=2001-01-01'

    def parse_next(self, response):

        next_link = response.xpath('//a[contains(@class, "comic-nav-next")]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        comic_date = params['comic'][0]
        tag = int(''.join(comic_date.split('-')))

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)


class Nerdity(Nodwick):

    name = 'nerdity'
    start_url = 'http://ffn.nodwick.com/?p=6'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//h2[@class="post-title"]/a/text()').get()
        month, day, year = comic_date.split('/')
        tag = int(year + month + day)

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
