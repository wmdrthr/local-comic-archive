from urllib.parse import urljoin
from datetime import datetime

import scrapy

import lcafetch.spiders

class Gunnerkrigg(lcafetch.spiders.ComicSpider):

    name = 'gunnerkrigg'
    start_url = 'https://www.gunnerkrigg.com/?p=1'

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="/images/next_a.jpg"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        comic_date = response.xpath('//a[@class="important"]/following-sibling::text()').get()
        comic_date = comic_date.split('|')[0]
        comic_date = datetime.strptime(comic_date.strip(), '%d %b %Y')
        tag = int(comic_date.strftime('%Y%m%d'))

        img_url = response.xpath('//img[@class="comic_image"]/@src').get()
        images = [urljoin(response.url, img_url)]

        annotations = []
        container = response.xpath('//a[@class="important"]/following-sibling::h4')[0]
        if container.get() != '<h4></h4>':
            annotations.append(container.get())
        for node in container.xpath('following-sibling::node()').getall():
            node_text = node.strip()
            if node_text == '' or 'Comments' in node_text or\
               node_text == '<p></p>':
                continue
            annotations.append(node_text)

        yield {'tag': tag,
               'url': response.url,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)
