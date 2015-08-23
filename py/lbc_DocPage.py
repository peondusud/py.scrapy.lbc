import os
import sys
import re
import logging
from colorama import Fore, Back, Style

import requests
import http.cookiejar
from urllib.parse import urlparse
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple
import threading
import time

from lbc_FrontPage import *
from lbc_items import *

class DocPage(threading.Thread):

    def __init__(self, q_doc_urls, q_documents, q_stats_doc ):
        self._logger = logging.getLogger(__name__)

        super().__init__()

        self.docPage_url = ""
        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents

        google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'DNT': '1',
        'Referer' : 'http://www.leboncoin.fr/',
        'Connection' : 'keep-alive' }
        self._session = requests.session()
        self._session.headers.update( headers )
        self._logger.debug("Init Session Headers : {}".format( self._session.headers )  )
        self._logger.debug("_session created" )

        self._event = threading.Event()


    def worker(self ):
        self.fetch()
        #self._logger.debug( "self.page {}".format( self.page))
        if (self.page is not None ) or  (not self.page) :
            self.scrap()
        else:
            self._logger.error( "Worker self.page empty or None" )


    def fetch(self):
        try:
            self.docPage_url = self.q_doc_urls.get(block=True, timeout=None)
            self._logger.info( Fore.CYAN + "Document URL to Fetch : {}".format( self.docPage_url ) + Fore.RESET )
        except queue.Empty:
            self._logger.debug("Fetch self.docPage_url queue Empty:" )

        self._logger.debug( "Fetch session cookies Before web request : {}".format( self._session.cookies.items())  )
        self._logger.debug("Handling request {}".format( self.docPage_url ) )
        #response = self._session.get( self.docPage_url , timeout=3)
        response = requests.get( self.docPage_url , timeout=None) #FIXME connection reset
        self._logger.debug( "Fetch session cookies after web request : {}".format( self._session.cookies.items())  )

        if response .status_code != requests.codes.ok:
            response .raise_for_status()
        self.page = response.text
        #self._logger.info(  "Fetch headers sent to server : {}".format( response.request.headers )  )
        #self._logger.info(  "Fetch headers sent from server : {}".format( response.headers)  )

    def scrap(self):

        tree = html.fromstring( self.page )
        lbc_item = LeboncoinItem( self.docPage_url, tree)
        self._logger.debug( "scrap lbc_item :".format( ( lbc_item ) ) )
        self.add_Queue_Documents( lbc_item )


    def add_Queue_Documents(self,  lbc_item):
        #add doc url to doc queue
        try:
            self._logger.debug( "add_Queue_Documents : Try Add to q_documents lbc_item ".format( lbc_item ) )
            self.q_documents.put( lbc_item, block=True, timeout=None)
        except queue.Full:
            self._logger.debug("add_Queue_Documents : self.q_doc_url queue Full" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        self._event.clear()
        super().stop()

    def run(self):
        self._event.wait(timeout=None)
        while self._event.is_set():
            try:
                self._logger.debug("calling worker")
                self.worker()
                #time.sleep(1)   #FIXME
            except Exception as e:
                self._logger.debug( "exception {} DocPage loop".format(e) )
                self._logger.exception(e)
        self._logger.info("Finished or stopped DocPage loop")
