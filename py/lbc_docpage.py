#!/usr/bin/env python3
# -- coding: utf-8 --

import logging
from colorama import Fore, Back, Style
import datetime
import requests
from tornado.httpclient import AsyncHTTPClient
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev


from multiprocessing import Process, Value, Array, Pool, Queue, Event
import time

from lbc_item import LeboncoinItem

class DocPage(Process):

    def __init__(self, q_doc_urls, q_documents, q_stats_doc ):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self.docPage_url = ""
        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents
        self._event = Event()
        self._logger.debug("_session created" )


    def worker(self ):
    	while 1:
            self.get_url_from_q()
            self._logger.info( "page {}".format( page))
            self.scrap( page )
            self._logger.debug( "scap page done" )


    def get_url_from_q(self):
        try:
            self.docPage_url = self.q_doc_urls.get( block=True, timeout=None )
            self._logger.info( Fore.CYAN + "Document URL to Fetch : {}".format( self.docPage_url ) + Fore.RESET )
            #self.q_doc_urls.task_done()
        except multiprocessing.Empty:
            self._logger.debug("Fetch self.docPage_url queue Empty:" )


    def scrap(self, page):
        tree = html.fromstring( page )
        lbc_item = LeboncoinItem( self.docPage_url, tree)
        self._logger.debug( "scrap lbc_item :".format( ( lbc_item) ) )
        self.add_Queue_Documents( lbc_item.json_it()  )

    def add_Queue_Documents(self,  lbc_item):
        #add doc url to doc queue
        try:
            self._logger.debug( "add_Queue_Documents : Try Add to q_documents lbc_item ".format( lbc_item ) )
            self.q_documents.put( lbc_item, block=True, timeout=None)
        except multiprocessing.Full:
            self._logger.debug("add_Queue_Documents : self.q_documents queue Full" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        self._event.clear()

    def run(self):
        self._event.wait( timeout=None )
        while self._event.is_set():
            try:
                self._logger.debug("calling worker")
                self.worker()
                #time.sleep(1)   #FIXME
            except Exception as e:
                self._logger.debug( "exception {} DocPage loop".format(e) )
                self._logger.exception(e)
        self._logger.info("Finished or stopped DocPage loop")
