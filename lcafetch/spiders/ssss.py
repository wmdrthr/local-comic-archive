from urllib.parse import urljoin, urlparse, parse_qs
import os

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(baseurl, annotation):

    annotation_images = []
    try:
        soup = fragment_fromstring(annotation)
        images = [elt for elt in soup.xpath('//img')]
        if len(images) > 0:
            for image in images:
                annotation_images.append(urljoin(baseurl, image.get('src')))
                filename = os.path.basename(image.get('src'))
                image.set('src', f'ssss/annotations/{filename}')
                image.attrib.pop('class', None)

            annotation = tostring(soup).decode('utf-8')
            return annotation, annotation_images
        else:
            return annotation, []
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip(), []
        else:
            raise e

class SSSS(lcafetch.spiders.ComicSpider):

    name = 'ssss'
    comic_name = 'Stand Still, Stay Silent'
    start_url = 'http://sssscomic.com/comic.php?page=1'

    def parse_next(self, response):

        img = response.xpath('//img[@src="adv2_comicimages/nav_next.png"]')
        if img.attrib['class'] == 'button':
            next_link = img.xpath('parent::a/@href').get()
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        _, _, path, _, query, _ = urlparse(response.url)
        params = parse_qs(query)
        if path == '/comic.php':
            tag = 1000 + int(params['page'][0])
        else:
            tag = 2000 + int(params['page'][0])

        images = [urljoin(response.url, response.xpath('//img[@class="comicnormal"]/@src').get())]

        annotations = []
        annotation_images = set()
        for node_text in response.xpath('//div[@id="comic_text"]/p').getall():
            annotation, _images = process_annotation(response.url, node_text)
            annotations.append(annotation)
            annotation_images.update(_images)

        images.extend(annotation_images)

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images,
               'annotation_images': annotation_images}

        yield self.parse_next(response)

class RedTail(lcafetch.spiders.ComicSpider):

    name = 'redtail'
    comic_name = "A Redtail's Dream"
    start_url = 'http://www.minnasundberg.fi/comic/page00.php'

    def parse_next(self, response):

        next_link = response.xpath('//div[@id="nav2"]/table/tr/td[3]/a/@href').get()
        if next_link != 'http://www.sssscomic.com':
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        tag = 9000 + int(response.xpath('//p[@class="num"]/text()').get())

        images = [urljoin(response.url, response.xpath('//div[@id="page"]/img/@src').get())]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
