# Scrapy settings for lcafetch project

import os

BOT_NAME = 'lcafetch'
SPIDER_MODULES = ['lcafetch.spiders']

USER_AGENT = 'shiny-armadillo/0.1.0'
ROBOTSTXT_OBEY = False
MEDIA_ALLOW_REDIRECTS = True

TELNETCONSOLE_ENABLED = False

EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider' : 1
}
CLOSESPIDER_ERRORCOUNT = 1
CLOSESPIDER_ITEMCOUNT = 3
CONCURRENT_REQUESTS = 1

ITEM_PIPELINES = {
    'lcafetch.pipelines.ComicValidator': 10,
    'scrapy.pipelines.images.FilesPipeline': 100,
    'lcafetch.pipelines.ComicPipeline': 200
}

BASEDIR = os.getenv('LCA_BASEDIR', '/tmp/lcafetch')

FILES_STORE  = os.path.join(BASEDIR, 'download/comics')

HTTPCACHE_ENABLED = True
HTTPCACHE_DIR = os.path.join(BASEDIR, 'httpcache')
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
