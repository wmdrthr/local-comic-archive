from urllib.parse import urljoin
from datetime import datetime
from string import ascii_lowercase
import os

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(tag, baseurl, annotation):
    annotation_images = []
    try:
        soup = fragment_fromstring(annotation)
        images = [elt for elt in soup.xpath('//img')]
        if len(images) > 0:
            for image in images:
                annotation_images.append(urljoin(baseurl, image.get('src')))
                filename = os.path.basename(image.get('src'))
                image.set('src', f'narbonic/annotations/{tag}/{filename}')

            annotation = tostring(soup).decode('utf-8')
            return annotation, annotation_images
        else:
            return annotation, []
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip(), []
        else:
            raise e

class Narbonic(lcafetch.spiders.ComicSpider):

    name = 'narbonic'
    start_url = 'http://narbonic.com/comic/july-31-august-5-2000/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//header[@class="comic-meta entry-meta"]//a/text()').get()
        comic_date = datetime.strptime(comic_date, '%B %d, %Y')
        base_tag = int(comic_date.strftime('%Y%m%d'))

        title = response.xpath('//h1[@class="comic-title"]/a/text()').get()

        comic_containers = response.xpath('//div[@class="comic-strip-container"]')
        for index, container in enumerate(comic_containers):

            if len(comic_containers) > 1:
                tag = str(base_tag) + ascii_lowercase[index]
            else:
                tag = base_tag

            images = [container.xpath('div/img/@src').get()]

            annotations = []
            annotation_images = set()
            for node in container.xpath('div[2]/p').getall():
                annotation, _images = process_annotation(tag, response.url, node)
                annotations.append(annotation)
                annotation_images.update(_images)

            images.extend(annotation_images)

            data = {'tag': tag,
                    'url': response.url,
                    'title': title,
                    'annotation': annotations,
                    'subdir': str(comic_date.year),
                    'file_urls': images}
            if len(annotation_images) > 0:
                data['annotation_images'] = annotation_images

            yield data

        yield self.parse_next(response)
