from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class Lackadaisy(lcafetch.spiders.ComicSpider):

    name = 'lackadaisy'
    start_url = 'https://www.lackadaisycats.com/comic.php?comicid=1'
    tag_param = 'comicid'

    def parse_next(self, response):

        next_link = response.xpath('//div[@class="next"]/a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params[self.tag_param][0])

        img = response.xpath('//div[@id="content"]/img')
        images = [urljoin(response.url, img.attrib['src'])]

        title_text = response.xpath('//head/title/text()').get()
        title = title_text.split('::')[-1].strip()

        annotations = []
        for annotation in response.xpath('//div[@class="description"]/text()').getall():
            annotation = annotation.replace('            ', ' ').strip()
            if annotation != '' and annotation != '<br>':
                annotations.append(annotation)

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'annotation': annotations,
               'file_urls': images}

        yield self.parse_next(response)


class LackadaisyGallery(Lackadaisy):

    name = 'lackadaisy.gallery'
    start_url = 'https://www.lackadaisycats.com/exhibit.php?exhibitid=1'
    tag_param = 'exhibitid'
