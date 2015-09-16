#!/usr/bin/env python3
# -- coding: utf-8 --

import logging
from colorama import Fore, Back, Style
import datetime
import requests
from tornado.httpclient import AsyncHTTPClient
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev


#from threading import Thread, Event
from multiprocessing import Process, Value, Array, Pool, Queue, Event
import time

from lbc_item import LeboncoinItem

#class DocPage(Thread):
class DocPage(Process):

    def __init__(self, q_doc_urls, q_documents, q_stats_doc ):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self.docPage_url = ""
        self.q_doc_urls = q_doc_urls
        self.q_documents = q_documents
        self._event = Event()

        #google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        self._http_headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer' : 'http://www.leboncoin.fr/',
        'Connection' : 'keep-alive' }
        self._logger.debug("_session created" )


    def worker(self ):
        self.get_url_from_q()
        #page = self.fetch()
        page = self.async_fetch()
        self._logger.info( "page {}".format( page))
        while 1:
            if ( page is not None ) :
                self._logger.info( "page {}".format( page))
                self.scrap( page )
                return 0
            else:
                self._logger.debug( "Worker page empty or None" )


    def get_url_from_q(self):
        try:
            self.docPage_url = self.q_doc_urls.get( block=True, timeout=None )
            self._logger.info( Fore.CYAN + "Document URL to Fetch : {}".format( self.docPage_url ) + Fore.RESET )
            #self.q_doc_urls.task_done()
        except multiprocessing.Empty:
            self._logger.debug("Fetch self.docPage_url queue Empty:" )



    def async_fetch(self):
        try:
            http_client = AsyncHTTPClient()
            def handle_response(response):
                return str(response.body)
            http_client.fetch( self.docPage_url, callback=handle_response)
        except httpclient.HTTPError as e:
            self._logger.error("HTTP request {}".format(e) )
            self._logger.debug("HTTP request {}".format(e), exc_info=1)
            return self.async_fetch()


    def fetch(self):
        try:
            self._logger.debug("Handling request {}".format( self.docPage_url ) )
            response = requests.get( self.docPage_url , timeout=3, headers=self._http_headers)
            if response.status_code != requests.codes.ok:
                response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._logger.error("HTTP request {}".format(e) )
            self._logger.debug("HTTP request {}".format(e), exc_info=1)
            time.sleep(0.3)
            self._logger.info("HTTP request Relauching fetch")
            return self.fetch()
        self._logger.debug(  "Fetch headers sent to server : {}".format( response.request.headers )  )
        self._logger.debug(  "Fetch headers sent from server : {}".format( response.headers)  )
        return response.text

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
