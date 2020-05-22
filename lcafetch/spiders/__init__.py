import scrapy

class ComicSpider(scrapy.Spider):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.options = set()

    def start_requests(self):

        return [scrapy.Request(self.start_url, callback = self.parse)]
