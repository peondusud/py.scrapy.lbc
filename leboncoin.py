#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import re
import requests
from urllib.parse import urlparse
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
import threading
import queue


start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
    )


allow_domains = [ "leboncoin.fr" ]

fetchlist=[]


class FrontPage():
    q_front = queue.Queue()

    def __init__(self, q_doc_page_url):
        self.url2fetch = FrontPage.q_front.get()
        self.fetch()
        if (self.page is not None ) or  (not self.page) :
            self.scrap()

    def fetch(self):

        s = requests.session()
        r = s.get( self.url2fetch  , timeout=0.01)    
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        self.page = r.text


    def scrap(self):
            
        tree = html.fromstring( self.page )
       
        # retrieve 25 elems doc page url
        self.content_urls = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
        self.add_DocUrls_2_queue()

        prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
        self.next_url = prev_nxt_url[-1]
        self.nb_page = next_url.split("?o=")[-1]

        self.add_nextFrontPageUrl()


    def add_nextFrontPageUrl(self):
        #verify in allow_domain
        if url_isAllow(self.next_url):
             #add to queue new front page url
             FrontPage.q_front.put(next_url)

    def printz(self):

        print( self.content_urls )
        print( self.next_url, self.nb_page )

    def add_DocUrls_2_queue(self):
        #add doc url to doc queue
        for page_url in self.content_urls:
            if  url_isAllow( page_url ):
                q_doc_page_url.put( page_url ) #FIXME QUEUE doc_page_url



    def url_isAllow(url_to_check):
        o = urlparse(url_to_check)
        for allow_domain in allow_domains:
            if allow_domain in o.netloc:
                return True
        return False




class DocPage():
    q_docs = queue.Queue()

    def __init__(self):
        self.url2fetch = DocPage.q_docs.get()
        self.fetch()
        if (self.page is not None ) or  (not self.page) :
            self.scrap()

    def fetch(self):

        s = requests.session()
        r = s.get( self.url2fetch  , timeout=0.01)    
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        self.page = r.text


    def scrap(self):
            
        tree = html.fromstring( self.page )
       
        doc_category = url2fetch.split("/")[3]
        doc_id = int(url.split("/")[-1].split(".htm")[0])
        doc_url = url 


        title = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')[0]


        tmp = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')    
        
        try:
            region = tmp[1]
            doc_category = tmp[2]
        except IndexError:
             pass

        img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
        print( img_urls )

        user_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
        user_id = int( user_url.split("id=")[1] )
        user_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
        
        upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
        upload_date = "".join( upload_date ).strip()
        upload_date = upload_date.replace("- Mise en ligne le ","")
        upload_date = upload_date.replace(u"à ","")
        upload_date = upload_date.replace(".","")




    def printz(self):

        print( self.content_urls )
        print( self.next_url, self.nb_page )

    def add_Document_2_queue(self):
        #add doc url to doc queue
        for page_url in self.content_urls:
            if  url_isAllow( page_url ):
                q_documents.put( page_url ) #FIXME QUEUE doc_page_url


class LeboncoinItem():
    doc_id = int()
    doc_url = str()
    doc_category = str()
    title = str()
    img_urls = list()

    user_url = str()
    user_id = int()
    user_name = str()
    user_pro = bool()
    user_pro_siren = str()
    upload_date = str()

    price_currency = str()
    price = str()
    urgent = bool()

    region = str()
    addr_locality = str()
    postal_code = int()
    location = list()

    criterias = dict()

    desc = str()



def fetch():
    s = requests.session()
    r = s.get( start_urls  , timeout=0.01)
    
    if r.status_code != requests.codes.ok:
        r.raise_for_status()
        
    tree = html.fromstring( r.text )
   
    #test = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]')
    #print dir(test))

    content_urls = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
    #content_urls = test.xpath('div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
    print( content_urls )

    prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
    next_url = prev_nxt_url[-1]
    nb_page = next_url.split("?o=")[-1]

    print( next_url )
    print( nb_page )

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
        print( title )


        tmp = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')    
        
        try:
            region = tmp[1]
            doc_category = tmp[2]
        except IndexError:
             pass

        img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
        print( img_urls )

        user_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
        user_id = int( user_url.split("id=")[1] )
        user_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
        
        upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
        upload_date = "".join( upload_date ).strip()
        upload_date = upload_date.replace("- Mise en ligne le ","")
        upload_date = upload_date.replace(u"à ","")
        upload_date = upload_date.replace(".","")

        print( user_url, user_name , upload_date )



def update_DB():
    pass


def stats():
    pass

if __name__ == '__main__':
   for start_url in start_urls:
       FrontPage.q_front.put(start_url)

   q_doc_page_url = queue.Queue()
   front = FrontPage(q_doc_page_url)
   fetch() 


