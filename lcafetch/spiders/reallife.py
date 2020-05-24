from datetime import datetime

import scrapy

import lcafetch.spiders

class RealLife(lcafetch.spiders.ComicSpider):

    name = 'reallife'
    start_url = 'https://reallifecomics.com/comic.php/?comic=title-1'

    def parse_next(self, response):

        next_link = response.xpath('//div[@class="next"]/a/@onclick').get()
        if next_link is not None:
            next_link = next_link.split('=', 1)[1]
            next_link = next_link.strip("';")
            return scrapy.Request(next_link, callback=self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//div[@id="date"]/h4/text()').get()
        comic_date = datetime.strptime(comic_date.strip(), '%A, %b %d, %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
