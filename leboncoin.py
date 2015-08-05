#!/usr/bin/env python



import os
import sys
import re
import requests
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
import threading

#import tornado.ioloop
#import tornado.web


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
    r = requests.get('http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/')
    #print  r.text          #Retourne le contenu en unicode
    #print  r.content       #Retourne le contenu en bytes
    #print  r.json          #Retourne le contenu sous forme json
    #print  r.headers       #Retourne le headers sous forme de dictionnaire
    #print  r.status_code   #Retourne le status code
    #print  r.request.headers # Headers you sent with the request 
    

    tree = html.fromstring( r.text )
    prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
    next_url = prev_nxt_url[-1]
    nb_page = next_url.split("?o=")[-1]

    print next_url
    print nb_page

    check_domain(next_url)

def parse():
    pass


def inject_to_DB():
    pass


def update_DB():
    pass


def stats():
    pass

if __name__ == '__main__':
   fetch() 


