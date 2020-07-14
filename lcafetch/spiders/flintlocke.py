from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class Flintlocke(lcafetch.spiders.ComicSpider):

    name = 'flintlocke'
    comic_name = "Flintlocke's Guide to Azeroth"
    start_url = 'http://flintlocke.thecomicseries.com/comics/1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def parse_next(self, response):

        if response.url == 'http://flintlocke.thecomicseries.com/comics/366':
            return scrapy.Request('http://flintlockevshorde.thecomicseries.com/comics/1', callback = self.parse)
        if response.url == 'http://flintlockevshorde.thecomicseries.com/comics/166/':
            return None

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)

    def parse(self, response):

        _, netloc, path, *_ = urlparse(response.url)
        path = [p for p in path.split('/') if p != '']
        tag = int(path[-1])
        if netloc == 'flintlocke.thecomicseries.com':
            tag = f'g{tag:03}'
            subdir = 'guidetoazeroth'
        else:
            tag = f'h{tag:03}'
            subdir='vsthehorde'

        img = response.xpath('//img[@id="comicimage"]')
        images = [urljoin(response.url, img.attrib['src'])]
        title = img.attrib['alt']

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'subdir': subdir,
               'file_urls': images}

        yield self.parse_next(response)
