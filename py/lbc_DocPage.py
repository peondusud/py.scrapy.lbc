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

from lbc_FrontPage import *

class DocPage(threading.Thread):

    def __init__(self, q_doc_urls, q_documents ):
        self.logger = logging.getLogger(__name__)
        
        #super().__init__(group=None) #FIXME
        #super().__init__(self) #FIXME
        threading.Thread.__init__(self) #FIXME
        #threading.Thread.__init__(group=None, target=self.run() ) #FIXME

        self.docUrl_to_fetch = ""
        try:
            self.docUrl_to_fetch = q_doc_urls.get()
        except queue.Empty:
            self.logger.debug(" self.docUrl_to_fetch queue Empty:" )

        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents
        self.session = requests.session()
        self._run = False


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


    def scrap(self):

        tree = html.fromstring( self.page )
        LeboncoinItem(self.docUrl_to_fetch, tree)

    def add_Queue_Documents(self):
        #add doc url to doc queue
        try:
            self.logger.debug( "Try Add to q_front_urls", next_url )
            self.q_documents.put( self.lbc_item, block=True, timeout=None)
        except queue.Full:
            self.logger.debug(" self.q_doc_url queue Full:" )

    def start(self):
        self._run = True
        super().start()

    def stop(self):
        self._run = False
        super().stop()

    def run(self):

        while self._run:
            try:
                self.worker()
            except Exception as e:
                self._logger.info( "exception {} DocPage loop".format(e) )

        self._logger.info("Finished or stopped DocPage loop")
