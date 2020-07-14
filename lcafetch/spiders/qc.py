from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class QuestionableContent(lcafetch.spiders.ComicSpider):

    name = 'questionablecontent'
    comic_name = 'Questionable Content'
    start_url = 'https://www.questionablecontent.net/view.php?comic=1'

    def parse_next(self, response):

        next_link = response.xpath('//a[text()="Next"]/@href').get()
        if next_link != '#':
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['comic'][0])

        img_url = response.xpath('//img[@id="strip"]/@src').get()
        images = [urljoin(response.url, img_url)]

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
