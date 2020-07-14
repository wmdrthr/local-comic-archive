from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class UserFriendly(lcafetch.spiders.ComicSpider):

    name = 'userfriendly'
    comic_name = 'User Friendly'
    start_url = 'http://ars.userfriendly.org/cartoons/?id=19971117&mode=classic'

    def parse_next(self, response):

        next_link = response.xpath('//map[@name="ars"]/area[@alt=""]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        tag = int(params['id'][0])

        images = []
        for img_url in response.xpath('//table//img/@src').getall():
            if 'cartoons/archives' in img_url:
                images.append(img_url)

        yield {'tag': tag,
               'url': response.url,
               'file_urls': images}

        yield self.parse_next(response)
