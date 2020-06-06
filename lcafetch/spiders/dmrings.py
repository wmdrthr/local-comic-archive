from urllib.parse import urljoin
from datetime import datetime
import html

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(baseurl, annotation):

    try:
        soup = fragment_fromstring(annotation)
        for link in soup.xpath('//a'):
            link.set('href', urljoin(baseurl, link.get('href')))
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e

class DMRings(lcafetch.spiders.ComicSpider):

    name = 'dmrings'
    start_url = 'https://www.shamusyoung.com/twentysidedtale/?p=612'

    def parse_next(self, response):

        if response.url == 'https://www.shamusyoung.com/twentysidedtale/?p=1331':
            return None
        next_link = response.xpath('//div[@class="prev-next-next"]/parent::a/@href').get()
        return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)

    def parse(self, response):

        for text in response.xpath('//article//span[@class="subhead-box"]/text()').getall():
            if text.startswith('Posted '):
                comic_date = datetime.strptime(text, 'Posted %A %b %d, %Y')
                tag = int(comic_date.strftime('%Y%m%d'))
                break

        title_nodes = response.xpath('//h2[@class="entry-title"]/descendant::text()').getall()
        title = ' '.join(title_nodes)

        annotations = []
        for node in response.xpath('//div[@class="entry-text"]/child::p'):
            if 'class' in node.attrib and node.attrib['class'] == 'byline':
                break
            if node.get() == '<p></p>' or node.xpath('text()').get().strip() == '':
                continue
            annotations.append(node.get())

        images = []
        captions = []
        for img in response.xpath('//img[@class="insetimage"]'):
            images.append(img.attrib['src'])
            if 'title' in img.attrib['title']:
                captions.append(img.attrib['title'])
            else:
                captions.append(None)

        annotations = [html.unescape(process_annotation(response.url, a)) for a in annotations]

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
