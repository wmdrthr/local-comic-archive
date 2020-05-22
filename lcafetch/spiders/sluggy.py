from urllib.parse import urljoin
from datetime import datetime
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
            if (match := re.search('daily.php\?date=(\d+)$', url)) is not None:
                tag_text = match.group(1)
                if len(tag_text) == 6:
                    tag = int('20' + tag_text)
                else:
                    tag = int(tag_text)
                link.set('href', f'/sluggy/{tag}')
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e

class Sluggy(lcafetch.spiders.ComicSpider):

    name = 'sluggy'
    start_url = 'http://archives.sluggy.com/book.php?chapter=1'

    def parse_next(self, response):

        next_link = response.xpath('//div[@class="chapter_nav comic_spacer"]/div[@class="next"]/a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        for comic in response.xpath('//div[@class="comic_list"]//div[@class="comic_spacer"]'):
            images = []
            for img in comic.xpath('.//div[@class="comic_content"]/img/@src').getall():
                images.append(img)

            comic_date = datetime.strptime(comic.attrib['id'], '%Y-%m-%d')
            tag = int(comic_date.strftime('%Y%m%d'))

            url = urljoin(response.url, comic.xpath('.//a[@class="tinylink"]/@href').get())

            annotations = []
            annotation_div = comic.xpath('.//div[@class="comic_popup"]')
            if len(annotation_div) > 0:
                for node_text in comic.xpath('.//div[@class="comic_popup"]/node()').getall():
                    if len(node_text.strip()) > 0:
                        annotations.append(process_annotation(node_text.strip()))

            yield { 'tag': tag,
                    'url': url,
                    'annotation': annotations,
                    'file_urls': images}

        yield self.parse_next(response)
