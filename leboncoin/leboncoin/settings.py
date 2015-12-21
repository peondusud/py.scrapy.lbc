# -*- coding: utf-8 -*-

# Scrapy settings for leboncoin project
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'lbc_bot'

SPIDER_MODULES = ['leboncoin.spiders']
NEWSPIDER_MODULE = 'leboncoin.spiders'

EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 500,
    'scrapy.extensions.logstats.LogStats': 500,
    'scrapy.extensions.telnet.TelnetConsole': 500,
    'scrapy.extensions.closespider.CloseSpider': 500
}

#Maximum number of concurrent items (per response) to process in parallel in the Item Processor
CONCURRENT_ITEMS = 100

#The maximum number of concurrent (ie. simultaneous) requests that will be performed by the Scrapy downloader.
CONCURRENT_REQUESTS = 16

CONCURRENT_REQUESTS_PER_DOMAIN = 8

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'leboncoin (+http://www.yourdomain.com)'


# http://doc.scrapy.org/en/latest/topics/feed-exports.html#storage-uri-parameters
#FEED_URI = '/home/peon/%(name)s/%(time)s.json%'
FEED_URI = '/home/peon/py.scrapy.lbc/leboncoin/test.json'
FEED_FORMAT = 'jsonlines'

#The maximum limit for Twisted Reactor thread pool size. This is common multi-purpose thread pool used by various Scrapy components.
REACTOR_THREADPOOL_MAXSIZE = 10

#DOWNLOADER_MIDDLEWARES
DOWNLOADER_STATS = True
#DOWNLOAD_DELAY = 0.25    # 250 ms of delay
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
"""
"""
