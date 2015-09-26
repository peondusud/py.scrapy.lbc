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

from requests_futures.sessions import FuturesSession





def bench_LBC(nb_req):
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
    t = timeit.timeit('one_iter_lbc()',setup=s, number=nb_req)
    print("bench_LBC",nb_req, t)


def bench_requests_futures_async(number_reqs, nb_worker):
    # https://pypi.python.org/pypi/requests-futures
    l=[]

    start = datetime.datetime.now()
    print('Start : ', start)

    def bg_cb(sess, resp):
        # resp.text
        if resp.status_code != requests.codes.ok:
            print(resp.status_code)
            resp.raise_for_status()
        #print(dir(resp))
        l.append(1)
        l_size = len(l)
        print(l_size)
        #print(len(response.body))
        if l_size == number_reqs:
            tornado.ioloop.IOLoop.instance().stop()
        if datetime.datetime.now() - start == 60:
            tornado.ioloop.IOLoop.instance().stop()

    session = FuturesSession( max_workers=10 )
    for elem in range(int(number_reqs/nb_worker)):
        for e in range(nb_worker):
            session.get(
                        "http://www.leboncoin.fr/",
                        background_callback = bg_cb
                        )
        time.sleep(1)
    print('[Rq TURFU] Done :', datetime.datetime.now() - start)



def bench_tornado_async( number_reqs, nb_worker):
    #http://tornado.readthedocs.org/en/latest/guide/async.html

    start = datetime.datetime.now()
    print('Start : ', start)
    l = []
    def handle_request(response):
        if response.error:
            print("Error:", response.error)
        else:
            l.append(1)
            l_size = len(l)
            print(l_size)
            #print(len(response.body))
            if l_size == number_reqs:
                tornado.ioloop.IOLoop.instance().stop()
            if datetime.datetime.now() - start == 60:
                tornado.ioloop.IOLoop.instance().stop()

    http_client = AsyncHTTPClient(max_clients = nb_worker)
    http_client.configure( None,
                        method = "GET",
                        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                        # max_clients determines the maximum number of simultaneous fetch() operations that can execute in parallel on each IOLoop
                        max_clients = nb_worker
                        )


    def url_generator():
        for elem in range(int(number_reqs/nb_worker)):
            for e in range(nb_worker):
                http_client.fetch("http://www.leboncoin.fr/",
                                    method='GET',
                                    callback=handle_request)
            time.sleep(1)

    threading.Thread(target=url_generator).start()
    tornado.ioloop.IOLoop.instance().start()
    print('[Tornado] Done :', datetime.datetime.now() - start)




if __name__ == '__main__':

    logging.basicConfig( level=logging.INFO)
    logger = logging.getLogger(__name__)
    #bench_LBC()
    #bench_tornado_async( 50, 10)
    bench_requests_futures_async(50, 10)
