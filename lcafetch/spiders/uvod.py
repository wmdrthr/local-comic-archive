from urllib.parse import urljoin

import scrapy

import lcafetch.spiders

class UVOD(lcafetch.spiders.ComicSpider):

    name = 'uvod'
    start_url = 'http://www.goominet.com/unspeakable-vault/vault/1/'
    baseurl = 'http://www.goominet.com/'

    def parse_next(self, response):

        next_link = response.xpath('//img[@src="uploads/tx_cenostripviewer/next_en.gif"]/parent::a/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(self.baseurl, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        tag = int(response.url.split('/')[-2])

        title = response.xpath('//head/meta[@property="og:title"]/@content').get()
        title = title.split(':', 1)[-1]
        title = f'Vault {tag}: {title}'

        images = []
        for img_url in response.xpath('//div[@class="tx-cenostripviewer-pi1"]//img/@src').getall():
            for filterword in ('home', 'next', 'last', 'typo3temp', 'first', 'previous', 'rss'):
                if filterword in img_url:
                    break
            else:
                images.append(urljoin(self.baseurl, img_url))

        yield {'tag': tag,
               'url': response.url,
               'title': title,
               'file_urls': images}

        yield self.parse_next(response)
