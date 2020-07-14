import scrapy

import lcafetch.spiders

class GWS(lcafetch.spiders.ComicSpider):

    name = 'gws'
    comic_name = 'Girls with Slingshots'
    start_url = 'https://www.girlswithslingshots.com/comic/gws1/'

    def parse_next(self, response):

        next_link = response.xpath('//a[@class="cc-next"]/@href').get()
        if next_link is not None:
            return scrapy.Request(next_link, callback = self.parse)
        else:
            return None

    def parse(self, response):

        index = response.url.rfind('gws') + 3
        if response.url[index] == '-':
            index += 1
        end = index
        while end < len(response.url) and response.url[end] in '0123456789':
            end += 1
        tag = int(response.url[index:end])

        img = response.xpath('//img[@id="cc-comic"]')
        images = [img.attrib['src']]

        captions = []
        if img.attrib['title'][:3] != 'GWS':
            captions.append(img.attrib['title'].strip())

        yield {'tag': tag,
               'url': response.url,
               'captions': captions,
               'file_urls': images}

        yield self.parse_next(response)
