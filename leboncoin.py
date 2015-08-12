#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import re
import logging

import requests
from urllib.parse import urlparse
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple
import threading
from multiprocessing import Process, Value, Array, Pool



start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
    )


allow_domains = [ "leboncoin.fr" ]


class LBC_Orchestrator():
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._q_docPageUrls = queue.Queue()
        self._q_documents = queue.Queue()

        self._bdd_center = BDD_orchestrator( self._q_documents)
        self._docPage_center = DocPage_orchestrator(self._q_docPageUrls, self._q_documents)
        self._frontPage_center = FrontPage_orchestrator( self._q_docPageUrls)

    def run(self):
        self._bdd_center.run()
        self._docPage_center.run()
        self._frontPage_center.run()



class BDD_orchestrator():
    def __init__(self,   q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_documents = q_documents
        self._bdd_process = BDD_file(self._q_documents)

    def run(self):
        self._bdd_process.run()




class DocPage_orchestrator():
    def __init__(self,  q_doc_urls, q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_doc_urls = q_doc_urls
        self._q_documents = q_documents
        nb_concurent_documentScraper = 16
        #equals Nmber of concuremnt connection
        # Same nb_Thread_DocPage = 4
        self.pool_DocPageWorkers = Pool( nb_concurent_documentScraper )

    def run(self):
        self.pool_FrontWorkers.map(DocPage.loop(), self._q_doc_urls)
        #DocPage(_q_doc_urls, q_documents)loop()


class FrontPage_orchestrator():

    def __init__(self,  q_doc_urls):
        self._logger = logging.getLogger(__name__)

        self._q_doc_urls = q_doc_urls
        self._q_frontPageUrls = queue.Queue()
        for start_url in start_urls:
            try:
                self._q_frontPageUrls.put(start_url)
            except queue.Full:
                self.logger.debug(" self.q_frontPageUrls queue Full:" )
        nb_Thread_FrontPage = self._q_frontPageUrls.qsize()

        self.pool_FrontWorkers = Pool( nb_Thread_FrontPage )

    def run(self):
        self.pool_FrontWorkers.map(FrontPage.loop(), self.q_doc_urls)


class FrontPage():

    def __init__(self, q_front_urls , q_doc_urls):

        self._logger = logging.getLogger(__name__)
        self._q_front_urls = q_front_urls
        self._q_doc_urls = q_doc_urls
        self._session = requests.session()
        self.run = false

    def worker(self ):
        try:
            url2fetch = self._q_front_urls.get(block=True, timeout=1.0)
        except queue.Empty:
            self._logger.debug(" self.url2fetch queue Empty:" )
            return

        page = self.fetch(url2fetch)
        self._logger.debug( "page ",  page)
        if (page is not None ) or  (not page) :
            self.scrap()
        else:
            self.logger.error( "self.page empty or None" )

    def fetch(self, url2fetch):

        s = requests.session()
        r = s.get( url2fetch  , timeout=0.01)
        self._logger.debug("Handling request ", url2fetch)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        return r.text


    def scrap(self, page):

        self.tree = html.fromstring( page )

        self.get_docUrls_fromTree(tree)
        self.add_Queue_DocUrls()

        self.get_nextUrl_fromTree(tree)
        self.add_nextFrontPageUrl()

    def get_docUrls_fromTree(self , tree):
        # retrieve 25 elems doc page url
        content_urls = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
        self.add_Queue_DocUrls( content_urls )
        self._logger.debug( "content_urls :", content_urls )

    def get_nextUrl_fromTree(self, tree):
        prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
        next_url = prev_nxt_url[-1]
        nb_page = next_url.split("?o=")[-1]
        self._logger.debug( "next_url :", next_url)
        self._logger.debug( "nb_page :", nb_page )
        self.add_Queue_nextFrontPageUrl(next_url)

    def add_Queue_nextFrontPageUrl(self, next_url):
        #verify in allow_domain
        if url_isAllow( next_url):
            #add to queue new front page url
            try:
                self._logger.debug( "Try Add to q_front_urls", next_url )
                self._q_front_urls.put( next_url, block=True, timeout=None)
            except queue.Full:
                self._logger.debug(" self.q_doc_url queue Full:" )

    def add_Queue_DocUrls(self,content_urls):
        #add doc url to doc queue
        for page_url in content_urls:
            if  url_isAllow( page_url ):
                self._logger.debug( page_url, "is an Allow URL" )

                try:
                    self._q_doc_url.put( page_url, block=True, timeout=None )
                    self._logger.debug( "Add ", page_url, "to queue" )
                except queue.Full:
                    self._logger.debug(" self.q_doc_url queue Full:" )

    def url_isAllow(self, url_to_check):
        o = urlparse(url_to_check)
        for allow_domain in allow_domains:
            if allow_domain in o.netloc:
                self._logger.debug( url_to_check, "is an Allow URL. Domain", allow_domain )
                return True
        self._logger.debug( url_to_check, "is not Allow URL" )
        return False

    def loop(self):
        pass
        self._run = true
        while self._run:
            try:
                self.worker()
            except Exception as e:
                self._logger.info( "exception {} FrontPage loop".format(e) )

        self._logger.info("Finished or stopped FrontPage loop")



class DocPage():

    def __init__(self, q_doc_urls, q_documents ):
        self.logger = logging.getLogger(__name__)
        self.docUrl_to_fetch = ""
        try:
            self.docUrl_to_fetch = q_doc_urls.get()
        except queue.Empty:
            self.logger.debug(" self.docUrl_to_fetch queue Empty:" )

        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents
        self.session = requests.session()


    def worker(self ):
        self.fetch()
        self.logger.debug( "self.page ",  self.page)
        if (self.page is not None ) or  (not self.page) :
            self.scrap()
        else:
            self.logger.error( "self.page empty or None" )

    def fetch(self):
        reponse = self.session.get( self.docUrl_to_fetch , timeout=0.01)
        self.logger.debug("Handling request ", self.url2fetch)
        if reponse .status_code != requests.codes.ok:
            reponse .raise_for_status()
        self.page = reponse.text


    def document_identifier_factory(url):
        logger = logging.getLogger(__name__)
        url_slash_split = self.docUrl_to_fetch.split("/")
        doc_category = url_slash_split.split("/")[3]
        logger.debug( "doc_category ", doc_category  )
        doc_id = int(url_slash_split[-1].split(".htm")[0] )
        logger.debug( "doc_id ", doc_id  )
        doc_url = self.docUrl_to_fetch
        logger.debug( "doc_url", self.docUrl_to_fetch )
        return document_identifier(doc_url, doc_id, doc_category)

    def scrap(self):

        tree = html.fromstring( self.page )

        document_identifier_factory(url)

        try:
            title = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')[0]
        except IndexError:
            self.logger.error( "IndexError", exc_info=True )

        header_path = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
        try:
            region = header_path[1]
            doc_category = header_path[2]
            self.logger.debug( "region", region  )
            self.logger.debug( "doc_category", doc_category )
        except IndexError:
            self.logger.debug( "header_path", header_path  )
            self.logger.error( "IndexError", exc_info=True )

        img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
        self.logger.debug( "image urls", img_urls )

        uploader_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
        self.logger.debug( "user url", uploader_url )
        uploader_id = int( user_url.split("id=")[1] )
        self.logger.debug( "uploader_id", uploader_id )
        uploader_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
        self.logger.debug( "uploader_name", uploader_name )

        upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
        upload_date = "".join( upload_date ).strip()
        upload_date = upload_date.replace("- Mise en ligne le ","")
        upload_date = upload_date.replace(u"à ","")
        upload_date = upload_date.replace(".","")
        self.logger.debug( "uploader_name", upload_date )

    def add_Queue_Documents(self):
        #add doc url to doc queue
        try:
            self.logger.debug( "Try Add to q_front_urls", next_url )
            self.q_documents.put( self.lbc_item, block=True, timeout=None)
        except queue.Full:
            self.logger.debug(" self.q_doc_url queue Full:" )

    def loop(self):
        self._run = true
        while self._run:
            try:
                self.worker()
            except Exception as e:
                self._logger.info( "exception {} DocPage loop".format(e) )

        self._logger.info("Finished or stopped DocPage loop")


class LeboncoinItem():

    def __init__(self, url):
        Document_Category = namedtuple("Document_Category", ["doc_category", "pro_flag", "announcement_type"])
        Document_Localisation = namedtuple("Document_Localisation", ["region", "department", "zip code", "town", "location"])
        Document_Uploader = namedtuple("Document_Category", ["uploader_name", "uploader_url", "uploader_id", "uploader_pro_siren"])
        Document_Category_Criterias = namedtuple("Document_Category", ["dict" ]) #FIXME give dict() <====
        Document_Announcement = namedtuple("Document_Category", ["title", "description", "price", "price_currency", "img_urls" "upload_date", "urgent", "doc_url", "doc_id" ])
        self._document_Category = document_Category_factory(tree)
        self._document_Localisation = document_Localisation_factory(tree)
        self._document_Uploader = document_Uploader_factory(tree)
        self._document_Category_Criterias = document_Category_Criterias_factory(tree)
        self._document_Announcement = document_Announcement_factory(tree)


        def  document_Category_factory(tree):
            pass
            return Document_Category("doc_category", "pro_flag", "announcement_type")


        def jsonit(self):
            return None



class BDD_file():

    def __init__(self, q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_documents = q_documents

    def run(self):
        with open("lbc.json", 'w') as f:
            while 1:
                nb_doc = 1000
                if self._q_documents.qsize() > nb_doc:
                    bulk = []
                    for document in range(nb_doc):
                        try:
                            document_json = self._q_documents.get()
                            bulk.append( document_json )
                        except queue.Empty:
                            self._logger.debug(" self.url2fetch queue Empty:" )
                    f.write("".join(bulk))


def stats():
    pass

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    lbc_center = LBC_Orchestrator()
    lbc_center.run()
