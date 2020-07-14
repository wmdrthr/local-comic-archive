from urllib.parse import urljoin, urlparse, parse_qs

import scrapy

import lcafetch.spiders

class Sinfest(lcafetch.spiders.ComicSpider):

    name = 'sinfest'
    comic_name = 'Sinfest'
    start_url = 'https://www.sinfest.net/view.php?date=2000-01-17'

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="../images/next.gif"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        params = parse_qs(urlparse(response.url).query)
        comic_date = params['date'][0]
        year, month, day = comic_date.split('-')
        tag = int(year + month + day)

        images = []
        for img_url in response.xpath('//table//img/@src').getall():
            if 'btphp/comics' in img_url:
                images.append(urljoin(response.url, img_url))

        title = response.xpath('//td/nobr/following-sibling::text()').get()
        title = title.strip()

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
