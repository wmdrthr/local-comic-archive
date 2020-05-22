import os
import json
import mimetypes
import string
from urllib.parse import urlparse
from datetime import datetime

import scrapy

class ComicValidator():

    def process_item(self, item, spider):

        try:
            for key in ('tag', 'url'):
                assert (key in item and item[key] is not None), f'item does not have {key}'

            assert len(item['file_urls']) > 0, 'item does not have any image URLs'
            for url in item['file_urls']:
                assert len(url) > 0, 'empty image URL'
                parsed_url = urlparse(url)
                assert parsed_url.scheme in ('http', 'https') and parsed_url.netloc != '', f'invalid image url: {url}'

            return item
        except AssertionError as ae:
            for key,val in item.items():
                item[key] = str(val)
            spider.logger.error(f'Dropping item: {json.dumps(item)}')
            raise scrapy.exceptions.DropItem(f'Validation Failure: {ae.args[0]}')

class ComicPipeline():


    def __init__(self, files_store):
        self.files_store = files_store

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            files_store  = crawler.settings.get('FILES_STORE'),
        )

    def validate(self, item):

        # ensure images were downloaded correctly
        assert len(item['files']) > 0, 'item does not have any images'
        assert len(item['files']) == len(item['file_urls']), 'all images not downloaded'
        for image in item['files']:
            assert len(image['path']) > 0, 'missing image path in item'

    def upload_images(self, item, spider):
        tag = item['tag']

        if tag > 190000:
            subdir = str(tag)[:4]
        else:
            subdir = '{:04d}'.format(100 * (tag // 100))

        images = []
        for image in item['files']:
            image_file_path = os.path.join(self.files_store, image['path'])

            filename = os.path.basename(urlparse(image['url']).path)
            mimetype = mimetypes.guess_type(filename)[0]
            image_object_path = os.path.join(spider.name, subdir, filename)

            images.append(image_object_path)

            # TODO: save image

        item['images'] = images
        return item

    def persist(self, item, spider):
        tag = item['tag']

        keys = ['tag', 'url', 'title', 'annotation', 'images']
        document = {'parsed_at': datetime.utcnow(), 'tag': tag}
        for key in keys:
            if key in item and item[key]:
                document[key] = item[key]

        # TODO: save comic data

        return document

    def process_item(self, item, spider):
        try:
            self.validate(item, spider)
            item = self.upload_images(item, spider)
            document = self.persist(item, spider)

            return document
        except AssertionError as ae:
            for key,val in item.items():
                item[key] = str(val)
            spider.logger.error(f'Dropping item: {json.dumps(item)}')
            raise scrapy.exceptions.DropItem(f'Validation Failure: {ae.args[0]}')
        except:
            for key,val in item.items():
                item[key] = str(val)
            spider.logger.error(f'Error while processing item: {json.dumps(item)}', exc_info=True)
