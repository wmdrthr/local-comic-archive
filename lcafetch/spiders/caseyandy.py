from urllib.parse import urljoin, urlparse, parse_qs
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
            if (match := re.search('\?strip=(\d+)$', url)) is not None:
                tag = int(match.group(1))
                link.set('href', f'/caseyandandy/{tag}')
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e


class CaseyAndAndy(lcafetch.spiders.ComicSpider):

    name = 'caseyandandy'
    start_url = 'http://www.galactanet.com/comic/view.php?strip=1'

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="next.gif"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback=self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['strip'][0])

        images = []
        for img_url in response.xpath('//img/@src').getall():
            if img_url.startswith('Strip'):
                images.append(urljoin(response.url, img_url))

        annotations = []
        for node in response.xpath('//td[@background="castback.gif"]/node()').getall():
            text = node.strip()
            if len(text) == 0 or text == '<p>\xa0</p>' or\
               text == 'There is no news post for this strip.':
                continue
            annotations.append(process_annotation(text))

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
