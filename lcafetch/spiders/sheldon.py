from datetime import datetime

import scrapy

import lcafetch.spiders

class Sheldon(lcafetch.spiders.ComicSpider):

    name = 'sheldon'
    comic_name = 'Sheldon'
    start_url = 'http://www.sheldoncomics.com/archive/011130.html'

    def parse_next(self, response):

        next_link = response.xpath('//a[@id="nav-next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback=self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//div[@id="comic-meta"]//br/following-sibling::text()').get()
        comic_date = datetime.strptime(comic_date.strip(), '%b %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        title = None
        img_title = response.xpath('//div[@id="comic"]//img/@title').get()
        img_title = img_title.split('-')
        if len(img_title) > 1:
            title = img_title[1].strip()

        yield {'tag': tag,
               'title': title,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
