# -*- coding: utf-8 -*-

BOT_NAME = 'lbc_bot'

SPIDER_MODULES = ['leboncoin.spiders']
NEWSPIDER_MODULE = 'leboncoin.spiders'

EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 500,
    'scrapy.extensions.logstats.LogStats': 500,
    'scrapy.telnet.TelnetConsole': 500,
    #'scrapy.extensions.telnet.TelnetConsole': 500,
    'scrapy.extensions.closespider.CloseSpider': 500
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': None
    #'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #'leboncoin.middlewares.CustomHttpProxyMiddleware': 300,
    #'leboncoin.middlewares.RandomUserAgentMiddleware': 300
}

SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None
}

ITEM_PIPELINES = {
    #'leboncoin.pipelines.ElasticsearchBulkUpdatePipeline': 200,
    #'leboncoin.pipelines.ElasticsearchBulkIndexPipeline': 200,
    'leboncoin.pipelines.JsonLinesWithEncodingPipeline': 300,
}

ES_HOST = "192.168.1.49"
ES_PORT = 9200
ES_URL_PREFIX = ''
#ES_BULK_SIZE = 200

#Maximum number of concurrent items (per response) to process in parallel in the Item Processor
CONCURRENT_ITEMS = 100

#The maximum number of concurrent (ie. simultaneous) requests that will be performed by the Scrapy downloader.
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'

#FEED_URI = 'dump_lbc.json'
#FEED_FORMAT = 'jsonlines'

FEED_URI_PREFIX = 'dump_lbc'

#The maximum limit for Twisted Reactor thread pool size. This is common multi-purpose thread pool used by various Scrapy components.
REACTOR_THREADPOOL_MAXSIZE = 10

DOWNLOADER_STATS = True
#DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 180
AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_DEBUG = False

DOWNLOAD_MAXSIZE = 1073741824 #(1024MB)

COMPRESSION_ENABLED = True

LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = None #if None, standard error will be used.
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = 'INFO'
LOG_STDOUT = False #If True, all standard output (and error) of your process will be redirected to the log.


TELNETCONSOLE_ENABLED = True
#TELNETCONSOLE_HOST =
TELNETCONSOLE_PORT = [6023, 6073]


COOKIES_ENABLED = False
