from urllib.parse import urljoin

import scrapy

import lcafetch.spiders

class WastedTalent(lcafetch.spiders.ComicSpider):

    name = 'wastedtalent'
    start_url = 'http://www.wastedtalent.ca/comic/anime-crack'

    def parse_next(self, response):

        next_link = response.xpath('//li[@class="next"]/a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        title = response.xpath('//h1[@class="comictitle"]/a/text()').get()
        tag, _ = title.split('-')
        tag = int(tag.strip()[1:])

        images = [response.xpath('//div[@class="comic_content"]/img/@src').get()]

        annotations = []
        for node in response.xpath('//div[@class="comic_info clear-block"]//p').getall():
            annotations.append(node)

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
