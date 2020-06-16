import os
import json
import string
from urllib.parse import urlparse
from datetime import datetime

import scrapy
from sqlalchemy import create_engine, Table, MetaData, select
from PIL import Image

class ComicValidator():

    def process_item(self, item, spider):

        try:
            for key in ('tag', 'url'):
                assert (key in item and item[key] is not None), f'item does not have {key}'

            if 'captions' in item:
                assert len(item['captions']) > 0, 'missing captions'

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
            raise # we want to fail immediately when we find an invalid item

class ComicPipeline():

    imagetypes = {'comic': 1, 'alternate': 2, 'annotation': 3}

    def __init__(self, db_engine, basedir, files_store):
        self.basedir = basedir
        self.files_store = files_store

        self.engine = db_engine
        self._initialize_database(self.engine)

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            db_engine = create_engine(crawler.settings.get('DATABASE_URL')),
            basedir   = crawler.settings.get('BASEDIR'),
            files_store  = crawler.settings.get('FILES_STORE'),
        )

    def _initialize_database(self, engine):

        metadata = MetaData(bind=engine)

        self.comicids = {}
        with engine.connect() as connection:
            result = connection.execute('SELECT * FROM comics')
            for row in result:
                self.comicids[row['nickname']] = row['id']

        self.archive = Table('archive', metadata, autoload=True)
        self.images = Table('images', metadata, autoload=True)
        self.titles = Table('titles', metadata, autoload=True)
        self.annotations = Table('annotations', metadata, autoload=True)

    def validate(self, item):

        # ensure images were downloaded correctly
        assert len(item['files']) > 0, 'item does not have any images'
        assert len(item['files']) == len(item['file_urls']), 'all images not downloaded'
        for image in item['files']:
            assert len(image['path']) > 0, 'missing image path in item'

    def upload_images(self, item, spider):
        tag = item['tag']

        if 'no_subdirs' in spider.options:
            subdir = ''
        elif 'subdir' in item:
            subdir = item['subdir']
        else:
            if tag > 190000:
                subdir = str(tag)[:4]
            else:
                subdir = '{:04d}'.format(100 * (tag // 100))

        images = []
        for index, image in enumerate(item['files']):
            image_data = {}

            image_file_path = os.path.join(self.files_store, image['path'])
            filename = os.path.basename(urlparse(image['url']).path)

            with open(image_file_path, 'rb') as f:
                with Image.open(f) as img:
                    image_data['width'], image_data['height'] = img.size

            if 'captions' in item and index < len(item['captions']) and\
               item['captions'][index] is not None:
                image_data['caption'] = item['captions'][index]

            if 'annotation_images' in item and image['url'] in item['annotation_images']:
                image_data['image_path'] = os.path.join('annotations', str(tag), filename)
            else:
                if (str(tag) not in filename or 'rename_images' in spider.options) and\
                   'dont_rename_images' not in spider.options:

                    image_data['original_filename'] = filename
                    extension = os.path.splitext(filename)[1]
                    if len(item['files']) > 1:
                        filename = str(tag) + string.ascii_lowercase[index] + extension
                    else:
                        filename = str(tag) + extension

                image_data['image_path'] = os.path.join(subdir, filename)

            image_local_path = os.path.join(self.basedir, 'comics', spider.name, image_data['image_path'])
            if not os.path.exists(image_local_path):
                dirname = os.path.dirname(image_local_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                os.link(image_file_path, image_local_path)

            if 'alternate_image' in item and item['alternate_image'] == image['url']:
                image_data['imagetype'] = self.imagetypes['alternate']
            elif 'annotation_images' in item and image['url'] in item['annotation_images']:
                image_data['imagetype'] = self.imagetypes['annotation']

            images.append(image_data)

        item['images'] = images
        return item

    def persist(self, item, spider):

        document = {'tag': item['tag'], 'url': item['url'],
                    'comicid': self.comicids[spider.name],
                    'parsed_at': datetime.utcnow()}

        if spider.prevtag is not None:
            document['prevtag'] = spider.prevtag
        if 'slug' in item and item['slug']:
            document['slug'] = item['slug']

        with self.engine.begin() as connection:

            result = connection.execute(self.archive.insert().values(**document))

            archiveid = result.inserted_primary_key[0]

            if 'title' in item and item['title']:
                connection.execute(self.titles.insert().values(archiveid=archiveid, title=item['title']))
            if 'annotation' in item and item['annotation']:
                annotations = [{'archiveid':archiveid, 'annotation':annotation} for annotation in item['annotation']]
                connection.execute(self.annotations.insert(), annotations)
            if spider.prevtag is not None:
                connection.execute(self.archive.update()
                                   .where(self.archive.c.tag == spider.prevtag)
                                   .values(nexttag=item['tag']))
            for image in item['images']:
                image['archiveid'] = archiveid
                connection.execute(self.images.insert().values(**image))

        return document

    def process_item(self, item, spider):
        try:
            self.validate(item)
            item = self.upload_images(item, spider)
            document = self.persist(item, spider)

            spider.prevtag = item['tag']

            return document
        except AssertionError as ae:
            for key,val in item.items():
                item[key] = str(val)
            spider.logger.error(f'Dropping item: {json.dumps(item)}')
            raise # we want to fail immediately when we find an invalid item
        except:
            for key,val in item.items():
                item[key] = str(val)
            spider.logger.error(f'Error while processing item: {json.dumps(item)}', exc_info=True)
            raise
