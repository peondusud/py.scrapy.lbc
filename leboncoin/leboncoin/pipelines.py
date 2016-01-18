# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
from scrapy.conf import settings
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem

import json
import codecs
from collections import OrderedDict
rom datetime import datetime


"""
urifmt = settings['FEED_URI']
uri = urifmt % _get_uri_params(spider)

    def _get_uri_params(self, spider):
        params = {}
        for k in dir(spider):
            params[k] = getattr(spider, k)
        ts = datetime.utcnow().replace(microsecond=0).isoformat().replace(':', '-')
        params['time'] = ts
        self._uripar(params, spider)
        return params
"""



class JsonLinesWithEncodingPipeline(object):
    def __init__(self):
        #settings = get_project_settings()
        path = settings['FEED_URI_PREFIX'] + "_utf8.json"
        print("PATH ########", path)
        self.file = codecs.open(path, 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
