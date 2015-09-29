#!/usr/bin/env python3
# -- coding: utf-8 --

import logging
import datetime
import time
import os
from colorama import Fore, Back, Style
from lxml import html
from multiprocessing import Process, Value, Array, Pool, Queue, Event
from lbc_item import LeboncoinItem

class DocPage(Process):

    def __init__(self, q_doc_response_page, q_documents, q_stats_doc):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self.q_doc_response_page = q_doc_response_page
        self.q_documents = q_documents
        self.q_stats_doc  = q_stats_doc
        self._event = Event()
        self._logger.debug("_session created" )


    def worker(self ):
    	while 1:
            doc_response_page = self.get_doc_response_page_from_q()
            self._logger.info( "doc_response_page {}".format( doc_response_page ))
            self.scrap( doc_response_page )
            self._logger.debug( "scap response_page done" )


    def get_doc_response_page_from_q(self):
        try:
            doc_response_page = self.q_doc_response_page.get( block=True, timeout=None)
            self._logger.info( Fore.BLUE + "DOC PAGE : {}".format( doc_response_page ) + Fore.RESET )
            #.self.q_doc_response_page.task_done()
            return doc_response_page
        except multiprocessing.Empty:
            self._logger.exception(" self.q_doc_response_page queue Empty" )
            #os._exit(1)

    def scrap(self, response_page):
        #tree = html.fromstring( response_page.body )
        tree = html.parse( response_page.buffer )
        lbc_item = LeboncoinItem( response_page.request.url, tree)
        self._logger.debug( "scrap lbc_item :".format( ( lbc_item) ) )
        self.add_Queue_Documents( lbc_item.json_it()  )

    def add_Queue_Documents( self, lbc_item):
        #add doc url to doc queue
        try:
            self._logger.debug( "add_Queue_Documents : Try Add to q_documents lbc_item ".format( lbc_item ) )
            self.q_documents.put( lbc_item, block=True, timeout=None)
        except multiprocessing.Full:
            self._logger.exception("add_Queue_Documents : self.q_documents queue Full" )


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
            except Exception as e:
                self._logger.debug( "exception {} DocPage loop".format(e) )
                self._logger.exception(e)
        self._logger.info("Finished or stopped DocPage loop")
