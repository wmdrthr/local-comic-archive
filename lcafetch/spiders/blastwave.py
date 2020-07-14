from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class Blastwave(lcafetch.spiders.ComicSpider):

    name = 'blastwave'
    comic_name = 'Gone With The BlastWave'
    start_url = 'http://www.blastwave-comic.com/index.php?p=comic&nro=1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options.add('no_subdirs')

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="images/page/default/next.jpg"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['nro'][0])

        title = response.xpath('//div[@class="comic_title"]/text()').get()

        img_url = response.xpath('//center/img/@src').get()
        images = [urljoin(response.url, img_url)]

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
