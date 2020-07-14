from urllib.parse import urljoin
from datetime import datetime

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import strip_tags, ParserError

import lcafetch.spiders

def clean_footnote(footnote):
    try:
        soup = fragment_fromstring(footnote)
        strip_tags(soup, 'span')
        return tostring(soup).decode('utf-8')
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return footnote.strip()
        else:
            raise e

class Shlock(lcafetch.spiders.ComicSpider):

    name = 'schlock'
    comic_name = 'Schlock Mercenary'
    start_url = 'https://www.schlockmercenary.com/2000-06-12'

    def parse_next(self, response):

        next_link = response.xpath('//div[@class="strip-navigation"]//a[@class="next-strip"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        images = []
        for image in response.xpath('//div[@class="strip-image-wrapper"]/img'):
            images.append(urljoin(response.url, image.attrib['src']))

        footnotes = []
        footnote_div = response.xpath('//div[@class="strip-footnote"]')
        if len(footnote_div) > 0:
            footnotes = response.xpath('//div[@class="strip-footnote"]/node()').getall()
            footnotes = list([clean_footnote(f) for f in footnotes if len(f.strip()) > 0])

        comic_date = response.xpath('//div[@class="strip-date"]/text()').get()
        comic_date = datetime.strptime(comic_date.strip(), '%A %B %d, %Y')

        yield { 'tag': int(comic_date.strftime('%Y%m%d')),
                'url': response.url,
                'annotation': footnotes,
                'file_urls': images}

        yield self.parse_next(response)
