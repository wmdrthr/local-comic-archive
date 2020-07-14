from urllib.parse import urlparse

import scrapy

import lcafetch.spiders

class Boulet(lcafetch.spiders.ComicSpider):

    name = 'boulet'
    comic_name = 'Boulet'
    start_url = 'http://english.bouletcorp.com/2004/01/09/reno/'

    def parse_next(self, response):

        next_link = response.xpath('//a[contains(text(), "Next")]/@href').get()
        if next_link != response.url:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        path = [p for p in path.split('/') if p != '']
        year, month, day = [int(x) for x in path[:3]]
        tag = year * 10000 + month * 100 + day

        images = []
        captions = []
        for img in response.xpath('//div[@class="storycontent non-classe "]//img'):
            images.append(img.attrib['src'])
            if 'title' in img.attrib and len(img.attrib['title'].strip()) > 0:
                captions.append(img.attrib['title'].strip())
            else:
                captions.append(None)

        title_text = response.xpath('//head/title/text()').get()
        _, title_text = title_text.split('»')
        title = title_text.strip()

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
