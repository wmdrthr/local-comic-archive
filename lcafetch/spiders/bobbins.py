from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime

import scrapy

import lcafetch.spiders

class Bobbins(lcafetch.spiders.ComicSpider):

    name = 'bobbins'
    comic_name = 'Bobbins'
    start_url = 'http://www.scarygoround.com/bobbins/index-archive.php?date=19980921'
    last_url = 'http://www.scarygoround.com/bobbins/index-archive.php?date=20020517'

    def parse_next(self, response):

        if response.url == self.last_url:
            return None
        next_link = response.xpath('//a[contains(text(), "Next")]/@href').get()
        return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['date'][0])

        images = []
        for img_url in response.xpath('//div[@id="bodybox"]//img/@src').getall():
            if 'strips' in img_url:
                images.append(urljoin(response.url, img_url))

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)


class NewBobbins(Bobbins):

    name = 'newbobbins'
    comic_name = 'New Bobbins'
    start_url = 'http://www.scarygoround.com/bobbins/index.php?date=20131101'
    last_url = 'http://www.scarygoround.com/bobbins/index.php?date=20171229'


class BobbinsHorse(lcafetch.spiders.ComicSpider):

    name = 'bobbins.horse'
    comic_name = 'Bobbins Horse'
    start_url = 'https://bobbins.horse/comic/2013-08-30/'

    def parse_next(self, response):

        if response.url == 'https://bobbins.horse/comic/just-my-type/':
            return None
        next_link = response.xpath('//a[contains(text(), "Next >")]/@href').get()
        return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)

    def parse(self, response):

        comic_date = response.xpath('//span[@class="post-date"]/text()').get()
        comic_date = datetime.strptime(comic_date.strip(), '%B %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        img = response.xpath('//div[@id="comic"]/a/img')
        images = [img.attrib['src']]
        title = img.attrib['title']

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
