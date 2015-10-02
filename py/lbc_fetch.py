#!/usr/bin/env python3
# -- coding: utf-8 --


import logging
from colorama import Fore, Back, Style
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado import gen
from multiprocessing import Process, Value, Array, Pool, Queue, Event
#from time import sleep
import time
from datetime import timedelta

#google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
"""
self._http_headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
'Referer' : 'http://www.leboncoin.fr/',
'Connection' : 'keep-alive' }
"""

class DocFetcher(Process):

    def __init__(self, q_lbc_urls, q_lbc_response_page , q_fetch_stats, req_sec=12 ):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.q_lbc_urls = q_lbc_urls
        self.q_lbc_response_page = q_lbc_response_page
        self.q_fetch_stats = q_fetch_stats
        self.req_sec = req_sec
        self.max_clients = 200
        self.concurrency = 1

        self.http_client = AsyncHTTPClient(max_clients = 200)
        self.http_client.configure( None,
                                method = "GET",
                                user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                                # max_clients determines the maximum number of simultaneous fetch() operations that can execute in parallel on each IOLoop
                                max_clients = self.max_clients
                                )

        self.fetching  = set()
        self.fetched = set()
        self.io_loop = IOLoop.current()
        #self.io_loop = IOLoop.instance()
        self._event = Event()
        self._logger.debug( "Fetcher created, initialized" )



    @gen.coroutine
    def get_page(self, url):
        """
            http://tornado.readthedocs.org/en/latest/guide/queues.html
        """
        try:
            #response = yield self.http_client.fetch( url, method='GET', callback=self.handle_response)  #FIXME
            response = yield self.http_client.fetch( url, method='GET' )
            #futur = self.http_client.fetch( url, method='GET' )    #FIXME
                                                                    #FIXME never goes on callback
                                                                    #FIXME
            #self.io_loop.add_future(futur, self.handle_response)   #FIXME
            #futur.add_done_callback(self.self.handle_response)     #FIXME
            #response =  futur.result()                             #FIXME


            self._logger.debug( Fore.CYAN + "#### fetched : {}".format( url) + Fore.RESET )
            self.handle_response( response )    #FIXME never goes on callback
            print(dir(response))
            print(type(response))


        except tornado.httpclient.HTTPError as e:
            self._logger.exception( Fore.CYAN + "GET PAGE {}".format(e) + Fore.RESET )
            raise gen.Return([])

        raise gen.Return(response)

    def handle_response(self, response):
        print("fetch callback", dir(response))
        print("fetch callback", type(response))
        if response.error:
            self._logger.error( response.error )
            self.io_loop.stop() #FIXME add current to q
        else:
            self._logger.debug( Fore.CYAN + "Request Time : {}".format( response.request_time)  + Fore.RESET)
            self.add_Response2Queue( response )

    def add_Response2Queue(self,  elem):
        #add doc url to doc queue
        try:
            self._logger.debug( Fore.CYAN + "add_Response2Queue : try add elem to q_lbc_response_page" + Fore.RESET )
            self.q_lbc_response_page.put( elem, block=True, timeout=None )
            self._logger.debug( Fore.CYAN + "add_Response2Queue : added elem to q_lbc_response_page" + Fore.RESET )
        except multiprocessing.Full:
            self._logger.exception( Fore.CYAN + "add_Queue_Documents : self.q_lbc_response_page queue Full" + Fore.RESET )


    #@gen.coroutine
    def get_url_from_q(self):
        try:
            lbc_url =  self.q_lbc_urls.get( block=True, timeout=None )
            self._logger.info( Fore.CYAN + "Document URL to Fetch : {}".format( lbc_url ) + Fore.RESET )
            #self.q_doc_urls.task_done()
            return lbc_url
        except multiprocessing.Empty:
            self._logger.debug( Fore.CYAN + "Fetch self.docPage_url queue Empty:" + Fore.RESET )

    #@gen.coroutine
    def fetch_url(self):
        try:
            self._logger.debug( Fore.CYAN + "inside fetch_url" + Fore.RESET )
            current_lbc_url = self.get_url_from_q()
            self._logger.debug( Fore.CYAN + "will fetch  : {}".format( current_lbc_url ) + Fore.RESET )
            self.fetching.add( current_lbc_url )
            self.get_page( current_lbc_url )


            self.fetched.add( current_lbc_url )
            self._logger.debug( Fore.CYAN + 'fetched {}'.format( current_lbc_url ) + Fore.RESET)
        except Exception as e:
            self._logger.exception( e )

    #@gen.coroutine
    def async_worker( self ):
        self._logger.info( Fore.CYAN + 'inside async_worker()' + Fore.RESET )
        while 1:
            for _ in range(self.req_sec):
                self._logger.debug( Fore.CYAN + "Launch fetch_url"  + Fore.RESET)
                self.fetch_url()

            time.sleep(1)
        self._logger.debug( Fore.CYAN + "fetcher done"  + Fore.RESET)


    @gen.coroutine
    def worker(self):
        for _ in range(self.concurrency):
            self.async_worker()
            self._logger.info( Fore.CYAN + 'FETCHER Launch async_worker()' + Fore.RESET )
        while self._event.is_set():
            time.sleep(1)
        self._logger.info( Fore.CYAN + 'FETCHER Done fetched {} URLs.'.format(self.fetched) + Fore.RESET )

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
                self._logger.debug( Fore.CYAN + "calling worker"+ Fore.RESET )
                self.io_loop.run_sync(self.worker)
            except Exception as e:
                self._logger.debug( Fore.CYAN + "exception {} ".format(e) + Fore.RESET )
                self._logger.exception(e)
        self._logger.info( Fore.CYAN + "Finished or stopped Fetcher loop"+ Fore.RESET )
