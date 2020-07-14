import scrapy
from sqlalchemy import create_engine, Table, MetaData, select

class ComicSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.options = set()
        self.prevtag = None

    def _initialize_database(self):

        self.engine = create_engine(self.crawler.settings.get('DATABASE_URL'))
        metadata = MetaData(bind=self.engine)

        self.comics = Table('comics', metadata, autoload=True)
        self.archive = Table('archive', metadata, autoload=True)
        self.images = Table('images', metadata, autoload=True)
        self.titles = Table('titles', metadata, autoload=True)
        self.annotations = Table('annotations', metadata, autoload=True)

        with self.engine.begin() as connection:
            result = connection.execute(select([self.comics.c.id])
                                        .where(self.comics.c.nickname == self.name))
            row = result.first()
            if row is not None:
                self.comicid = row['id']
            else:
                result = connection.execute(self.comics.insert().values(nickname=self.name,
                                                                        name=self.comic_name))
                self.comicid = result.inserted_primary_key[0]

    def start_requests(self):

        self._initialize_database()

        with self.engine.connect() as connection:
            result = connection.execute(select([self.archive.c.tag, self.archive.c.url])
                                        .where(self.archive.c.comicid == self.comicid)
                                        .order_by(self.archive.c.parsed_at.desc())
                                        .limit(1))
            row = result.first()
            if row is not None:
                self.prevtag = row['tag']
                self.logger.info(f'Resuming crawl from {row["url"]}')
                return [scrapy.Request(row['url'], callback = self.parse_next)]
            else:
                self.logger.info(f'Starting crawl from {self.start_url}')
                return [scrapy.Request(self.start_url, callback = self.parse)]
