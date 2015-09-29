#!/usr/bin/env python3
# -- coding: utf-8 --


import logging
from colorama import Fore, Back, Style
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from multiprocessing import Process, Value, Array, Pool, Queue, Event
from threading import Thread

#google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}




class DocFetcher(Process):

    def __init__(self, q_lbc_urls, q_lbc_response_page , q_fetch_stats, req_sec=12 ):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.q_lbc_urls = q_lbc_urls
        self.q_lbc_response_page = q_lbc_response_page
        self.q_fetch_stats = q_fetch_stats
        self.req_sec = req_sec
        self.max_clients = 200
        """
        self._http_headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer' : 'http://www.leboncoin.fr/',
        'Connection' : 'keep-alive' }"""
        self.http_client = AsyncHTTPClient(max_clients = 200)
        self.http_client.configure( None,
                                method = "GET",
                                user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                                # max_clients determines the maximum number of simultaneous fetch() operations that can execute in parallel on each IOLoop
                                max_clients = self.max_clients
                                )
        #self.t = Thread(target = self.worker(), args=(self, )) #FIXME BIG

        self._event = Event()
        self._logger.debug( "Fetcher created" )


    def worker( self ):
        def handle_request(response):
            if response.error:
                self._logger.error( response.error )
                IOLoop.instance().stop()
            else:
                try:
                    self._logger.debug( "Request Time : {}".format( response.request_time) )
                    self.q_lbc_response_page.put( response, block=True, timeout=None )
                except multiprocessing.Full:
                    self._logger.exception( "add_Queue_Documents : self.q_lbc_response_page queue Full" )

        #IOLoop.instance().start() #FIXME BIG
        #self.t = Thread(target = IOLoop.instance()) #FIXME BIG
        #self.t.start()
        while 1:
            for ev in range(self.req_sec):
                lbc_url = self.get_url_from_q()
                http_client.fetch( lbc_url, method='GET', callback=handle_request)
            time.sleep(1)
        self._logger.debug( "fetcher done" )


    def add_Elem_Queue(self,  elem):
        #add doc url to doc queue
        try:
            self._logger.debug( "add_elem_Queue : Try Add to q_documents lbc_item ".format( lbc_item ) )
            self.q_documents.put( lbc_item, block=True, timeout=None)
        except multiprocessing.Full:
            self._logger.exception("add_Queue_Documents : self.q_documents queue Full" )


    def get_url_from_q(self):
        try:
            lbc_url = self.q_lbc_urls.get( block=True, timeout=None )
            self._logger.info( Fore.CYAN + "Document URL to Fetch : {}".format( lbc_url ) + Fore.RESET )
            #self.q_doc_urls.task_done()
            return lbc_url
        except multiprocessing.Empty:
            self._logger.debug("Fetch self.docPage_url queue Empty:" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        IOLoop.instance().stop()
        self._event.clear()


    def run(self):
        self._event.wait( timeout=None )
        while self._event.is_set():
            try:
                self._logger.debug("calling worker")
                self.worker()
                #self.t.start() #FIXME
                #IOLoop.instance().start() #FIXME
            except Exception as e:
                self._logger.debug( "exception {} DocPage loop".format(e) )
                self._logger.exception(e)
        self._logger.info("Finished or stopped DocPage loop")
