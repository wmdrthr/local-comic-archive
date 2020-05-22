import scrapy
from sqlalchemy import create_engine, Table, MetaData, select

class ComicSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.options = set()
        self.prevtag = None

    def start_requests(self):

        engine = create_engine(self.crawler.settings.get('DATABASE_URL'))
        metadata = MetaData(bind=engine)
        comics = Table('comics', metadata, autoload=True)
        archive = Table('archive', metadata, autoload=True)

        with engine.connect() as connection:
            result = connection.execute(select([archive.c.tag, archive.c.url])
                                        .select_from(archive.join(comics))
                                        .where(comics.c.nickname == self.name)
                                        .order_by(archive.c.parsed_at.desc())
                                        .limit(1))
            row = result.first()
            if row is not None:
                self.prevtag = row['tag']
                self.logger.info(f'Resuming crawl from {row["url"]}')
                return [scrapy.Request(row['url'], callback = self.parse_next)]
            else:
                self.logger.info(f'Starting crawl from {self.start_url}')
                return [scrapy.Request(self.start_url, callback = self.parse)]
