from urllib.parse import urlparse
import re

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(annotation):

    try:
        soup = fragment_fromstring(annotation)
        for link in soup.xpath('//a'):
            path = urlparse(link.get('href')).path
            if (match := re.match('^/(\d+)-(\d+)-(\d+)', path)) is not None:
                tag = ''.join(match.groups())
                link.set('href', f'/exterminatus/{tag}')
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e

class Exterminatus(lcafetch.spiders.ComicSpider):

    name = 'exterminatus'
    start_url = 'http://exterminatusnow.co.uk/2003-09-29/comic/meet-the-crew/dirty-harry/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@class="navi navi-next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        path = [p for p in path.split('/') if p != '']
        year, month, day = [int(x) for x in path[0].split('-')]
        tag = year * 10000 + month * 100 + day

        storyline = path[2].replace('-', ' ').title()
        title_text = response.xpath('//h4[@class="post-title"]/a/text()').get()
        index, title_text = title_text.split(' – ', 1)
        if storyline == 'Non Storyline':
            title = f'{index} - {title_text}'
        else:
            title = f'{index} - {storyline}: {title_text}'

        images = [response.xpath('//div[@id="comic"]//img/@src').get()]

        annotations = []
        for node_text in response.xpath('//div[@class="entry"]/p').getall():
            annotations.append(process_annotation(node_text))

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
