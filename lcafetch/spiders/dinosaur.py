from urllib.parse import urljoin
from datetime import datetime
import re

import scrapy

import lcafetch.spiders

class Dinosaur(lcafetch.spiders.ComicSpider):

    name = 'dinosaur'
    start_url = 'http://www.qwantz.com/index.php?comic=1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive = {}


    def start_requests(self):

        return [scrapy.Request('http://www.qwantz.com/archive.php', self.parse_archive)]

    def parse_archive(self, response):

        for tag in response.xpath('//ul[@class="archive"]//li'):
            link = tag.xpath('a')

            date_text = link.xpath('text()').get()
            comic_date = datetime.strptime(re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_text),
                                           '%B %d, %Y')
            tag = int(comic_date.strftime('%Y%m%d'))

            annotations = []
            for node in link.xpath('following-sibling::node()').getall():
                if node == '!':
                    continue
                annotations.append(node)

            # add comic date to the first annotation
            annotations[0] = date_text + annotations[0]

            self.archive[link.attrib['href']] = {'tag': tag,
                                                 'annotations': annotations}

        return super().start_requests()

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        tag = self.archive[response.url]['tag']

        img = response.xpath('//img[@class="comic"]')[0]
        img_url = urljoin(response.url, img.attrib['src'])
        images = [img_url]
        captions = [img.attrib['title']]

        annotations = self.archive[response.url]['annotations']

        subject = response.xpath('//a[text()="contact"]/@href').get()
        subject_annotation = subject.split('=', 1)[1].strip()
        annotations.append(subject_annotation)

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
