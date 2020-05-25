from urllib.parse import urljoin, urlparse

import scrapy

import lcafetch.spiders

class FreeFall(lcafetch.spiders.ComicSpider):

    name = 'freefall'
    start_url = 'http://freefall.purrsia.com/ff100/fv00001.htm'
    color = False

    jumps = {'http://freefall.purrsia.com/ff1300/fv01252.htm':'http://freefall.purrsia.com/ff1300/fc01253.htm',
             'http://freefall.purrsia.com/ff1900/fc01822.htm':'http://freefall.purrsia.com/ff1900/fc01823.htm',
             'http://freefall.purrsia.com/ff200/fv00158.htm':'http://freefall.purrsia.com/ff200/fv00159.htm'}

    def parse_next(self, response):

        if response.url in self.jumps:
            next_link = self.jumps[response.url]
            return scrapy.Request(next_link, callback=self.parse)
        else:
            next_link = response.xpath('//a[contains(text(), "Next")]/@href').get()
            if next_link is not None:
                next_link = urljoin(response.url, next_link)
                return scrapy.Request(next_link, callback=self.parse)
            else:
                return None

    def parse(self, response):

        if 'comic_data' in response.meta:

            comic_data = response.meta['comic_data']

            # get just the monochrome image, and add it as alternate image
            alt_img_url = urljoin(response.url, response.xpath('//img/@src').get())
            comic_data['file_urls'].append(alt_img_url)
            comic_data['alternate_image'] = alt_img_url

            yield comic_data

            yield scrapy.Request(comic_data['next_url'], callback = self.parse)

        else:
            path = urlparse(response.url).path
            tag = path.split('/')[-1]
            tag = int(tag[3:-4])

            img_url = response.xpath('//img/@src').get()
            images = [urljoin(response.url, img_url)]
            if tag == 976:
                alt_img_url = 'http://freefall.purrsia.com/ff1000/fv00976b.gif'
                images.append(alt_img_url)

            comic_data = {'tag': tag,
                          'url': response.url,
                          'file_urls': images}
            if len(images) == 2:
                comic_data['alternate_image'] = alt_img_url

            if tag <= 1252:
                yield comic_data
                yield self.parse_next(response)
            else:
                bw_url =  response.url.replace('fc', 'fv')
                next_request = self.parse_next(response)
                comic_data['next_url'] = next_request.url
                yield scrapy.Request(bw_url, callback = self.parse, meta = {'comic_data': comic_data})
