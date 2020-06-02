from urllib.parse import urljoin, urlparse
import html

import scrapy

import lcafetch.spiders

class XKCD(lcafetch.spiders.ComicSpider):

    name = 'xkcd'
    start_url = 'https://xkcd.com/1/'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options.add('dont_rename_images')

    def parse_next(self, response):

        next_link = response.xpath('//a[@rel="next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(urljoin(response.url, next_link), callback = self.parse)
        else:
            return None

    def parse(self, response):

        path = urlparse(response.url).path
        tag = int(path.split('/')[1])

        img = response.xpath('//div[@id="comic"]//img')
        img_url = urljoin(response.url, img.attrib['src'])
        images = [img_url]
        captions = [html.unescape(img.attrib['title'])]

        title = html.unescape(response.xpath('//div[@id="ctitle"]/text()').get())

        alt_img_div = response.xpath('//div[@id="comic"]//img/parent::a')
        if len(alt_img_div) > 0:
            alt_img_url = response.xpath('//div[@id="comic"]//img/parent::a/@href').get()
            alt_img_url = urljoin(response.url, alt_img_url)
            images.append(alt_img_url)

        comic_data = {'tag': tag,
                      'title':title,
                      'captions': captions,
                      'url': response.url,
                      'file_urls': images}

        if len(images) >= 2:
            comic_data['alternate_image'] = alt_img_url

        yield comic_data

        yield self.parse_next(response)
