#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import logging
from colorama import Fore, Back, Style


import requests
from urllib.parse import urlparse
from lxml import html     #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple, deque
import threading
import itertools
import timeit
import time
import datetime
#from multiprocessing import Process, Value, Array, Pool

from lbc_frontpage import *
from lbc_docpage import *
from lbc_bdd import *
from lbc_item import *
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop





def bench_LBC():
    s= """
import requests
from lxml import html
from lbc_items import LeboncoinItem
url = 'http://www.leboncoin.fr/ventes_immobilieres/702810503.htm'
response = requests.get(url)
page = response.text
def one_iter_lbc():
    tree = html.fromstring( page )
    LeboncoinItem(url,tree)
"""
    n = 1000
    t = timeit.timeit('one_iter_lbc()',setup=s, number=n)
    print("bench_LBC", n, t)





def bench_tornado_async():
    #http://tornado.readthedocs.org/en/latest/guide/async.html
    number = 20000

    start = datetime.datetime.now()

    def handle_request(response):
        if response.error:
            print("Error:", response.error)
        else:
            l.append(1)
            print(len(l))
            #print(len(response.body))
            if len(l) == number:
                tornado.ioloop.IOLoop.instance().stop()
            if datetime.datetime.now() - start == 60:
                tornado.ioloop.IOLoop.instance().stop()

    http_client = AsyncHTTPClient()
    http_client.configure( None,
                            defaults=dict(user_agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"),
                            max_clients=20localocl)

    l = []
    for elem in range(number):

        http_client.fetch("http://www.leboncoin.fr/", method='GET', callback=handle_request)
    tornado.ioloop.IOLoop.instance().start()
    print('Done')




if __name__ == '__main__':

    logging.basicConfig( level=logging.INFO)
    logger = logging.getLogger(__name__)
    #bench_LBC()
    bench_tornado_async()
