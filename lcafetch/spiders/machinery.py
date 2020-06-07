from urllib.parse import urlparse, urljoin, parse_qs
import re

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(annotation):

    try:
        soup = fragment_fromstring(annotation)
        for link in soup.xpath('//a'):
            url = link.get('href')
            if (match := re.search('\?date=(\d{8})$', url)) is not None:
                tag = int(match.group(1))
                link.set('href', f'/badmachinery/{tag}')
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e


class BadMachinery(lcafetch.spiders.ComicSpider):

    name = 'badmachinery'
    start_url = 'http://scarygoround.com/badmachinery/index.php?date=20090921'

    def parse_next(self, response):

        next_link = response.xpath('//a[contains(text(), "Next")]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['date'][0])

        img_url = response.xpath('//img[@class="comicimg"]/@src').get()
        images = [urljoin(response.url, img_url)]

        annotations = []
        annotation_nodes = response.xpath('.//span[@class="rss3"]/node()').getall()
        if len(annotation_nodes) > 0:
            for annotation in annotation_nodes:
                annotations.append(process_annotation(annotation))

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
