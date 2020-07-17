from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders


class PerryBibleFelloship(lcafetch.spiders.ComicSpider):

    name = 'perrybible'
    comic_name = 'Perry Bible Fellowship'
    start_url = 'https://pbfcomics.com/comics/stiff-breeze/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.prevtag is None:
            self.prevtag = 0
        self.options.update(['no_subdirs', 'dont_rename_images'])

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        path = [p for p in path.split('/') if p != '']
        slug = path[-1]

        tag = self.prevtag + 1

        images = response.xpath('//div[@id="comic"]/img/@src').getall()

        title = response.xpath('//h1[@class="pbf-comic-title"]/text()').get()

        yield {'tag': tag,
               'slug': slug,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
