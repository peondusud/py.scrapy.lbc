# -*- coding: utf-8 -*-
#
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#https://www.elastic.co/guide/en/elasticsearch/plugins/2.1/lang-python.html
from elasticsearch import Elasticsearch, helpers #pip3 install elasticsearch

from scrapy import signals
from scrapy.conf import settings
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem

import json
import codecs
import logging
from collections import OrderedDict
from datetime import datetime


class JsonLinesWithEncodingPipeline(object):
    def __init__(self):
        #settings = get_project_settings()
        path = settings.get('FEED_URI_PREFIX', "dump" )  + "_utf8.json"
        self.logger = logging.getLogger(__name__)
        self.file = codecs.open(path, 'w', encoding='utf-8')


    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class ElasticsearchBulkIndexPipeline(object):
    def __init__(self):
        #settings = get_project_settings()
        #self.logger = logging.getLogger(__name__)
        self.tracer = logging.getLogger('elasticsearch.trace')
        self.tracer.setLevel(settings.get('LOG_LEVEL', 'INFO'))
        #self.tracer.addHandler(logging.StreamHandler())
        self.tracer.addHandler(logging.NullHandler())
        self.tracer.propagate = False
        es_params = {'host': settings.get('ES_HOST', 'localhost'),
                    'port': settings.get('ES_PORT', 9200),
                    'url_prefix': settings.get('ES_URL_PREFIX', '') }
        self.action_buffer = list()
        self.es_bulk_size = settings.get('ES_BULK_SIZE', 50)
        self.es = Elasticsearch([es_params])
        """
        if not self.es.ping():
            Exception('ES cluster not ready')
        """
        #self.es.cluster.health(index='lbc-*', level='cluster', wait_for_status='yellow', request_timeout=1)

    def add_index_action(self, dic):
        index_date = dic["upload_date"][:10]
        #"index_date = datetime.datetime.strptime(proper_encode["upload_date"], "%Y.%m.%d %H:%M:%S").strftime("%Y.%m.%d")
        action = { '_op_type': 'index',
                    '_index': "lbc-" + index_date,
                    '_type': 'lbc',
                    #'_id': dic.get('doc_id')
                    '_source': dic.__dict__
                }
        if 'doc_id' in dic:
            action['_id'] = dic.get('doc_id')
        self.action_buffer.append(action)

    def process_item(self, item, spider):
        if len(self.action_buffer) == self.es_bulk_size:
            success, _ = helpers.bulk( self.es, actions=self.action_buffer, stats_only=True, raise_on_error=True, chunk_size=self.es_bulk_size)
            print((success))
            self.action_buffer = list()
        self.add_index_action(item)
        return item

    def spider_closed(self, spider):
        success, _ = helpers.bulk( self.es, actions=self.action_buffer, stats_only=True,  raise_on_error=True)
