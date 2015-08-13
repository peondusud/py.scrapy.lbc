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


allow_domains = [ "leboncoin.fr" ]

class FrontPage(threading.Thread):

    def __init__(self, q_front_urls , q_doc_urls):
        self._logger = logging.getLogger(__name__)

        #super().__init__(group=None) #FIXME
        super().__init__() #FIXME

        self._q_front_urls = q_front_urls
        self._logger.debug("_q_front_urls created" )

        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )

        self._session = requests.session()
        self._logger.debug("_session created" )

        self._event = threading.Event()

    def worker(self ):
        try:
            url2fetch = self._q_front_urls.get(block=True, timeout=1.0)
            self._logger.debug("_session created" )
        except queue.Empty:
            self._logger.debug(" self.url2fetch queue Empty:" )
            return

        page = self.fetch(url2fetch)
        self._logger.debug( "page ",  page)
        if (page is not None ) or  (not page) :
            self._logger.debug("page No empty" )
            self.scrap(page)
        else:
            self.logger.error( "page empty or None" )

    def fetch(self, url2fetch):

        r = self._session.get( url2fetch  , timeout=0.3)
        self._logger.debug("Handling request ", url2fetch)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        return r.text


    def scrap(self, page):

        self.tree = html.fromstring( page )

        self.get_docUrls_fromTree( self.tree )
        self.add_Queue_DocUrls()

        self.get_nextUrl_fromTree(self.tree )
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
        if self.url_isAllow( next_url):
            #add to queue new front page url
            try:
                self._logger.debug( "Try Add to q_front_urls", next_url )
                self._q_front_urls.put( next_url, block=True, timeout=None)
            except queue.Full:
                self._logger.debug(" self.q_doc_url queue Full:" )

    def add_Queue_DocUrls(self,content_urls):
        #add doc url to doc queue
        for page_url in content_urls:
            if  self.url_isAllow( page_url ):
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


    def start(self):
        self._event.set()
        super().start()

    def stop(self):
        self._event.clear()
        super().stop()

    def run(self):

        while self._event.is_set():
            try:
                self.worker()
            except Exception as e:
                self._logger.info( "exception {} FrontPage loop".format(e) )

        self._logger.info("Finished or stopped FrontPage loop")
