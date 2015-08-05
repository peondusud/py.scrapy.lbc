#!/usr/bin/env python



import os
import sys
import re
import requests
import lxml #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
import threading

import tornado.ioloop
import tornado.web


start_urls=[]

allow_domain=[]

fetchlist=[]


def inject():
    pass


def generate_fetchlist():
    pass

def check_domain(url_to_check):
    pass


def fetch():
    r = requests.get("http://leboncoin.fr/")
    print(r.text )
    print  r.text          #Retourne le contenu en unicode
    print  r.content       #Retourne le contenu en bytes
    print  r.json          #Retourne le contenu sous forme json
    print  r.headers       #Retourne le headers sous forme de dictionnaire
    print  r.status_code   #Retourne le status code
    print response.request.headers # Headers you sent with the request 

    check_domain()

def parse():
    pass


def inject_to_DB():
    pass


def update_DB():
    pass


def stats():
    pass

if __name__ == '__main__':
    pass


