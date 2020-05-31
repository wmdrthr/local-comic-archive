from urllib.parse import urljoin, urlparse, parse_qs
import os

import scrapy
from lxml.html import fragment_fromstring, tostring
from lxml.etree import ParserError

import lcafetch.spiders

def process_annotation(tag, baseurl, annotation):

    annotation_images = []
    try:
        soup = fragment_fromstring(annotation)
        image_links = [link for link in soup.xpath('//a') if link.get('href').startswith('images/')]
        if len(image_links) > 0:
            for link in image_links:
                annotation_images.append(urljoin(baseurl, link.get('href')))
                filename = os.path.basename(link.get('href'))
                link.set('href', f'concerned/annotations/{tag}/{filename}')

            annotation = tostring(soup).decode('utf-8')
            return annotation, annotation_images
        else:
            return annotation, []
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip(), []
        else:
            raise e


class Concerned(lcafetch.spiders.ComicSpider):

    name = 'concerned'
    start_url = 'http://www.screencuisine.net/hlcomic/index.php?date=2005-05-01'

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="templates/nextbutton.jpg"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        year, month, day = params['date'][0].split('-')
        tag = int(year + month + day)

        images = []
        for img_url in response.xpath('//center//img/@src').getall():
            if 'comics/' in img_url:
                images.append(urljoin(response.url, img_url))

        annotations = []
        annotation_images = set()
        annotation_tag = response.xpath('//div[@id="sc1"]//td')
        if len(annotation_tag) > 0:
            for annotation in annotation_tag[0].xpath('./node()').getall():
                annotation, _images = process_annotation(tag, response.url, annotation)
                annotations.append(annotation)
                annotation_images.update(_images)

        images.extend(annotation_images)

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images,
               'annotation_images': annotation_images}

        yield self.parse_next(response)
