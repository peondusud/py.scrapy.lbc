#!/usr/bin/env python

# -- coding: utf-8 --


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
   
    #test = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]')
    #print dir(test))

    content_urls = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
    #content_urls = test.xpath('div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
    print content_urls

    prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
    next_url = prev_nxt_url[-1]
    nb_page = next_url.split("?o=")[-1]

    print next_url
    print nb_page

    check_domain(next_url)
    
    parse(content_urls)


def parse(urls):
    for url in urls:
        doc_category = url.split("/")[3]
        doc_id = int(url.split("/")[-1].split(".htm")[0])
        doc_url = url 

        check_domain(url)
        page = requests.get( url )            
        tree = html.fromstring( page.text )
        title = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')[0]
        print title


        tmp = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')    
        
        try:
            region = tmp[1]
            doc_category = tmp[2]
        except IndexError:
             pass

        img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
        print img_urls

        user_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
        user_id = int( user_url.split("id=")[1] )
        user_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
        
        upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
        upload_date = "".join( upload_date ).strip()
        upload_date = upload_date.replace("- Mise en ligne le ","")
        upload_date = upload_date.replace("à ","")
        upload_date = upload_date.replace(".","")

        print user_url, user_name , upload_date



def update_DB():
    pass


def stats():
    pass

if __name__ == '__main__':
   fetch() 


