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

    def __init__(self, q_doc_urls, q_documents ):
        self.logger = logging.getLogger(__name__)

        super().__init__()

        self.docUrl_to_fetch = ""
        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents

        user_agent = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        self._session = requests.session()
        self._session.headers.update( user_agent )
        #print( self._session.headers.items()  )
        self._event = threading.Event()


    def worker(self ):
        self.fetch()
        #self.logger.debug( "self.page {}".format( self.page))
        if (self.page is not None ) or  (not self.page) :
            self.scrap()
        else:
            self.logger.error( "self.page empty or None" )

    def fetch(self):
        try:
            self.docUrl_to_fetch = self.q_doc_urls.get(block=True, timeout=None)
            self.logger.debug("self.docUrl_to_fetch :{}".format( self.docUrl_to_fetch  ) )
            self.logger.info( Fore.CYAN + "Document URL to Fetch :{}".format( self.docUrl_to_fetch ) + Fore.RESET )

        except queue.Empty:
            self.logger.debug(" self.docUrl_to_fetch queue Empty:" )
        reponse = self._session.get( self.docUrl_to_fetch , timeout=1)
        self.logger.debug("Handling request {}".format( self.docUrl_to_fetch ) )
        if reponse .status_code != requests.codes.ok:
            reponse .raise_for_status()
        self.page = reponse.text


    def scrap(self):

        tree = html.fromstring( self.page )
        LeboncoinItem(self.docUrl_to_fetch, tree)

    def add_Queue_Documents(self):
        #add doc url to doc queue
        try:
            self.logger.debug( "Try Add to q_front_urls {}".format( next_url) )
            self.q_documents.put( self.lbc_item, block=True, timeout=None)
        except queue.Full:
            self.logger.debug(" self.q_doc_url queue Full" )

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
                self.logger.debug("calling worker")
                self.worker()
                #time.sleep(1)   #FIXME
            except Exception as e:
                self.logger.info( "exception {} DocPage loop".format(e) )

        self.logger.info("Finished or stopped DocPage loop")
