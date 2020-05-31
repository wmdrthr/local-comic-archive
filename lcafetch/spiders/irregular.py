from urllib.parse import urljoin, urlparse
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
                image.set('src', f'irregular/annotations/{tag}/{filename}')

                if image.get('srcset') is not None:
                    srcset = image.get('srcset')
                    srcset_images = []
                    for img in srcset.split(','):
                        img_url, size = img.split(' ', 1)
                        annotation_images.append(urljoin(baseurl, img_url))
                        filename = os.path.basename(image.get('src'))
                        srcset_images.append(f'irregular{img_url} {size}')
                    image.set('srcset', ','.join(srcset_images))
            annotation = tostring(soup).decode('utf-8')
            return annotation, annotation_images
        else:
            return annotation, []
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip(), []
        else:
            raise e


class Irregular(lcafetch.spiders.ComicSpider):

    name = 'irregular'
    start_url = 'https://www.irregularwebcomic.net/1.html'

    def parse_next(self, response):

        next_link = response.xpath('//td[@class="smc"]/a[contains(text(), "Next (")]/@href').get()
        if next_link is not None:
                next_link = urljoin(response.url, next_link)
                return scrapy.Request(next_link, callback=self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        tag = path.split('/')[-1]
        tag = int(tag[:-5])

        img_url = response.xpath('//div[@class="center"]//img/@src').get()
        images = [urljoin(response.url, img_url)]

        title = None
        img_title = response.xpath('//div[@class="center"]//img/@alt').get()
        if img_title is not None and not img_title.startswith('Comic #'):
            title = img_title.strip()

        annotations = []
        annotation_images = set()
        annotation_div = response.xpath('//div[@id="annotation"]')
        if len(annotation_div) > 0:
            for annotation in response.xpath('//div[@id="annotation"]/node()').getall():
                if len(annotation.strip()) == 0:
                    continue
                annotation, _images = process_annotation(tag, response.url, annotation)
                annotations.append(annotation)
                annotation_images.update(_images)

        images.extend(annotation_images)

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'file_urls': images,
               'annotation_images': annotation_images}

        yield self.parse_next(response)
