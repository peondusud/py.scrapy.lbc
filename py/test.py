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
import json
import re


def tto():
    url = 'http://www.leboncoin.fr/ventes_immobilieres/702810503.htm'

    response = requests.get( url )
    page = response.text
    tree = html.fromstring( page )

    t = tree.xpath('/html/body/script[1]/text()')[0]
    t = str(t.strip() )
    print( (t) )


    pattern = '\s\s(\w+)\s:\s"(.+)",?'
    prog = re.compile(pattern)
    dic = {}
    for line in t.splitlines():
        result = prog.search(line )
        if result is not None:
            #print( result.groups() )
            dic[result.group(1)] = result.group(2)

    print(dic)

def get_region():
    response = requests.get('http://www.leboncoin.fr/')
    if response.status_code != requests.codes.ok:
        response.raise_for_status()
    page = response.text
    tree = html.fromstring( page )
    test = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerIndex"]/div[@id="Page_sky"]/div[@id="Page"]/table[@id="TableContentBottom"]/tr/td[@class="CountyList"]//a/@href' )
    regions = []
    for elem in test:
        regions.append(elem.split('/')[-2])
    return regions


if __name__ == '__main__':
    
    print(get_region())
