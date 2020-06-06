from urllib.parse import urljoin
from datetime import datetime

import scrapy

import lcafetch.spiders

class Foxhound(lcafetch.spiders.ComicSpider):

    name = 'foxhound'
    start_url = 'http://www.doctorshrugs.com/foxhound/comic.php?id=1'
    titles = {}

    def parse_next(self, response):

        next_link = response.xpath('//a[contains(text(), "Next >")]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        if len(self.titles) == 0:
            for link in response.xpath('//div[@style="float:right; width:450px;"]//td/a'):
                title = link.xpath('text()').get()
                comic_link = urljoin(response.url, link.attrib['href'])
                comic_date = link.xpath('../text()[last()]').get()
                self.titles[comic_link] = {'title': title.strip(),
                                           'date': datetime.strptime(comic_date.strip(), '(%m/%d/%y)')}

        comic_date = self.titles[response.url]['date']
        tag = int(comic_date.strftime('%Y%m%d'))

        title = self.titles[response.url]['title']

        images = [urljoin(response.url, response.xpath('//div/img/@src').get())]

        yield {'tag': tag,
               'title': title,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
