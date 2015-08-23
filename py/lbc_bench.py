#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import logging
from colorama import Fore, Back, Style
import datetime

import requests
from urllib.parse import urlparse
from lxml import html     #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple, deque
import threading
import itertools
import timeit
#from multiprocessing import Process, Value, Array, Pool

from lbc_FrontPage import *
from lbc_DocPage import *
from lbc_BDD import *
from lbc_items import *





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







if __name__ == '__main__':

    logging.basicConfig( level=logging.INFO)
    logger = logging.getLogger(__name__)
    bench_LBC()
