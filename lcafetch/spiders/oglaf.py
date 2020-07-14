from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class Oglaf(lcafetch.spiders.ComicSpider):

    name = 'oglaf'
    comic_name = 'Oglaf'
    start_url = 'https://www.oglaf.com/cumsprite/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.prevtag is None:
            self.prevtag = 0
        self.options.update(['no_subdirs', 'dont_rename_images'])

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link),
                                  callback = self.parse,
                                  cookies = {'AGE_CONFIRMED': 'yes'})
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        path = [p for p in path.split('/') if p != '']
        if len(path) > 1:
            slug = '/'.join(path)
        else:
            slug = path[0]

        tag = self.prevtag + 1

        img = response.xpath('//img[@id="strip"]')
        images = [img.attrib['src']]
        captions = [img.attrib['title']]
        annotations = [img.attrib['alt']]

        yield {'tag': tag,
               'slug': slug,
               'url': response.url,
               'annotation': annotations,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
