from urllib.parse import urljoin, urlparse
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
            if (match := re.search('/episodes/(\d+).html$', url)) is not None:
                tag = int(match.group(1))
                link.set('href', f'/droids/{tag}')
        annotation = tostring(soup).decode('utf-8')
        return annotation
    except ParserError as e:
        if 'leading text' in e.args[0]:
            return annotation.strip()
        else:
            raise e


class Droids(lcafetch.spiders.ComicSpider):

    name = 'droids'
    comic_name = 'Darths and Droids'
    start_url = 'https://www.darthsanddroids.net/episodes/0001.html'

    alternate_links = [ 'https://darthsanddroids.net/wandsandwarts/episodes/0050.html',
                        'https://darthsanddroids.net/notesandnazis/episodes/0050.html',
                        'https://darthsanddroids.net/mutantsandmiscreants/episodes/0050.html',
                        'https://darthsanddroids.net/emsandebes/episodes/0050.html',
                        'https://darthsanddroids.net/magiciansandmunchkins/episodes/0050.html',
                        'https://darthsanddroids.net/sandalsandspartans/0050.html',
                        'https://darthsanddroids.net/avatars/0050.html',
                        'https://darthsanddroids.net/terminators/0050.html']

    def parse_next(self, response):

        if response.url in self.alternate_links:
            index = self.alternate_links.index(response.url)
            index += 1
            if index < len(self.alternate_links):
                return scrapy.Request(self.alternate_links[index], callback = self.parse)
            else:
                return scrapy.Request('http://darthsanddroids.net/episodes/0051.html', calback = self.parse)
        elif response.url == 'https://www.darthsanddroids.net/episodes/0050.html':
            return scrapy.Request(self.alternate_links[0], callback = self.parse)
        else:
            next_link = response.xpath('//a[text()=">"]/@href').get()
            if next_link is not None:
                return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
            else:
                return None

    def parse(self, response):

        if response.url in self.alternate_links:
            index = self.alternate_links.index(response.url)
            tag = 50 + ((index + 1) * 0.1)
        else:
            path = urlparse(response.url).path
            tag = int(path[path.rfind('/')+1:path.rfind('.')])

        img = response.xpath('//div[@class="center"]//img')
        images = [urljoin(response.url, img.attrib['src'])]

        title = img.attrib['alt']

        annotations = []
        for node in response.xpath('//div[@class="text"]/node()'):
            node_text = node.get().strip()
            if node_text == '':
                continue
            if node_text == '<h3>Transcript</h3>' or node_text == '<h3>Vision-Impaired Transcript</h3>':
                break
            annotations.append(process_annotation(node_text))

        data =  {'tag': tag,
                 'url': response.url,
                 'title': title,
                 'annotation': annotations,
                 'file_urls': images}
        if response.url in self.alternate_links:
            data['subdir'] = '0000'
        yield data

        yield self.parse_next(response)
