#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import time
import logging
from colorama import Fore, Back, Style
import datetime

from multiprocessing import Process, Value, Array, Pool, Queue

from lbc_frontpage import FrontPage
from lbc_fetch import DocFetcher
from lbc_docpage import DocPage
from lbc_bdd import BDD_file



class LBC_Orchestrator():
    def __init__(self, start_urls, allow_domains, concurrent_doc, bdd_bulksize, bdd_filename ):
        self._logger = logging.getLogger(__name__)
        self.bdd_bulksize = bdd_bulksize
        self.bdd_filename = bdd_filename
        self.concurrent_doc = concurrent_doc

        self._q_frontPageUrls = Queue()
        self._logger.debug("LBC_Orchestrator _q_frontPageUrls created" )

        self._logger.debug("LBC_Orchestrator set _q_frontPageUrls with start_urls" )
        for start_url in start_urls:
            try:
                self._q_frontPageUrls.put(start_url, block=True, timeout=None)
            except multiprocessing.Full:
                self.logger.debug(" self.q_frontPageUrls queue Full" )

        self._q_docPageUrls = Queue()
        self._logger.debug("LBC_Orchestrator _q_docPageUrls created" )

        self._q_doc_response_page = Queue()
        self._logger.debug("LBC_Orchestrator _q_doc_response_page  created" )

        self._q_documents = Queue()
        self._logger.debug("LBC_Orchestrator _q_documents  created" )

        self._logger.debug("LBC_Orchestrator q_stats_doc initialize" )
        self.q_stats_doc = Queue()
        self._logger.debug("LBC_Orchestrator q_stats_doc initialized" )

        self._logger.debug("LBC_Orchestrator q_stats_front initialize" )
        self.q_stats_front = Queue()
        self._logger.debug("LBC_Orchestrator q_stats_front initialized" )

        self._logger.debug("LBC_Orchestrator q_stats_bdd initialize" )
        self.q_stats_bdd = Queue()
        self._logger.debug("LBC_Orchestrator q_stats_bdd initialized" )

        self._logger.debug("LBC_Orchestrator BDD_orchestrator initialize" )
        self._bdd_center = BDD_orchestrator( self._q_documents, self.q_stats_bdd , self.bdd_bulksize, self.bdd_filename )
        self._logger.debug("LBC_Orchestrator BDD_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator DocPage_orchestrator initialize" )
        self._docPage_center = DocPage_orchestrator( self._q_doc_response_page, self._q_documents, self.q_stats_doc, 2 ) #FIXME
        self._logger.debug("LBC_Orchestrator DocPage_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator DocFetcher_orchestrator initialize" )
        self._docFetcher_center = DocFetcher_orchestrator( self._q_docPageUrls, self._q_doc_response_page, self.q_stats_doc, self.concurrent_doc)
        self._logger.debug("LBC_Orchestrator DocFetcher_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator FrontPage_orchestrator initialize" )
        self._frontPage_center = FrontPage_orchestrator( self._q_frontPageUrls,  self._q_docPageUrls, self.q_stats_front, allow_domains )
        self._logger.debug("LBC_Orchestrator FrontPage_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator initialized" )


    def run(self):
        self._logger.debug("LBC_Orchestrator Launch _bdd_center.run()" )
        self._bdd_center.run()

        self._logger.debug("LBC_Orchestrator Launch _docPage_center.run()" )
        self._docPage_center.run()

        self._logger.debug("LBC_Orchestrator Launch _docFetcher_center.run()" )
        self._docFetcher_center.run()

        self._logger.debug("LBC_Orchestrator Launch _frontPage_center.run()" )
        self._frontPage_center.run()

        #self.stats()
        self.updateStatistics()

        #self._q_docPageUrls.join() #FIXME
        #self._q_frontPageUrls.join()
        #self._q_documents.join()

    def stop(self):
        self._logger.debug("LBC_Orchestrator Launch _frontPage_center.stop()" )
        self._frontPage_center.stop()

        self._logger.debug("LBC_Orchestrator Launch _docFetcher_center.stop()" )
        self._docFetcher_center.stop()

        self._logger.debug("LBC_Orchestrator Launch _docPage_center.stop()" )
        self._docPage_center.stop()


        self._logger.debug("LBC_Orchestrator Launch _bdd_center.stop()" )
        self._bdd_center.stop()

        #self._logger.debug("LBC_Orchestrator Launch self.t_stat.stop()" )
        #self.t_stat.stop() #FIXME


    def stats(self):
        self.t_stat = Process( target = self.updateStatistics)
        self.t_stat.daemon = True
        self.t_stat.start()

    def updateStatistics( self ):
        start_time = time.time()
        interval = 1 # wait  in second
        last_value = 0
        nb_docs_saved = 0
        next_call = time.time()
        while 1:
            try:
                if self.q_stats_bdd.qsize() > 0:
                    nb_docs_saved =  self.q_stats_bdd.get()
            except IndexError:
                print("updateStatistics pop IndexError")
            now = time.time()
            time_passed = now - start_time
            req_by_min = nb_docs_saved * 60 / time_passed
            print(Fore.RED + "nb_docs_saved\t: {}".format(nb_docs_saved) + Fore.RESET )
            print(Fore.YELLOW + "time_passed\t: {:.2f}".format(time_passed) + Fore.RESET)
            print(Fore.CYAN + "req_by_min\t: {:.2f}\n".format( req_by_min ) + Fore.RESET)
            next_call += interval
            time.sleep( next_call - time.time() )


class BDD_orchestrator():
    def __init__(self,   q_documents, q_stats_bdd, bdd_bulksize, bdd_filename):
        self._logger = logging.getLogger(__name__)

        self._q_documents = q_documents
        self._logger.debug("BDD_orchestrator self._q_documents  created" )

        self._logger.debug("BDD_orchestrator BDD_file  initialize" )
        self._bdd_thread = BDD_file( self._q_documents, q_stats_bdd, bdd_bulksize, bdd_filename)
        #self._bdd_thread.daemon = True

    def run(self):
        self._logger.debug("BDD_orchestrator BDD_file  in run()" )
        self._bdd_thread.start()

    def stop(self):
        self._bdd_thread.stop()


class DocPage_orchestrator():
    def __init__(self, q_lbc_response_page, q_documents, q_stats_doc, nb_worker):
        self._logger = logging.getLogger(__name__)
        self._q_lbc_response_page = q_lbc_response_page
        self._logger.debug("_q_lbc_response_page created" )

        self._q_documents = q_documents
        self._logger.debug("_q_documents created" )

        self._q_stats_doc = q_stats_doc
        self._logger.debug("_q_stats_doc created" )

        self.nb_worker = nb_worker #FIXME

        self.pool_DocPageWorkers = []
        self._logger.debug("initialize pool_DocPageWorkers" )
        for a in range( self.nb_worker ):
            doc_page_process = DocPage( self._q_lbc_response_page, self._q_documents , q_stats_doc )
            self._logger.debug("Create a new doc_page_process instance" )
            self.pool_DocPageWorkers.append( doc_page_process )
        self._logger.debug("pool_DocPageWorkers Initialized" )

    def run(self):
        for doc_page_process in self.pool_DocPageWorkers:
            doc_page_process.start()

    def stop(self):
        for doc_page_process in self.pool_DocPageWorkers:
            doc_page_process.stop()


class DocFetcher_orchestrator():
    def __init__(self, q_doc_urls, q_doc_response_page, q_stats_doc, concurrent_doc):
        self._logger = logging.getLogger(__name__)
        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )

        self._q_doc_response_page = q_doc_response_page
        self._logger.debug("_q_doc_response_page created" )

        self._q_stats_doc = q_stats_doc
        self._logger.debug("_q_stats_doc created" )

        self.concurrent_doc = concurrent_doc
        #equals Nmber of concurent connection

        self._logger.debug("initialize DocFetcher" )

        self.doc_page_process = DocFetcher( self._q_doc_urls, self._q_doc_response_page, q_stats_doc )
        self._logger.debug("Create a DocFetcher process instance" )

    def run(self):
        self.doc_page_process.start()

    def stop(self):
        self.doc_page_process.stop()

class FrontPage_orchestrator():

    def __init__(self, q_front_urls,  q_doc_urls, q_stats_front, allow_domains):
        self._logger = logging.getLogger(__name__)

        self._q_front_urls = q_front_urls
        self._q_doc_urls = q_doc_urls
        self._q_stats_front = q_stats_front

        nb_Thread_FrontPage = self._q_front_urls.qsize()

        self._logger.debug("initialize pool_FrontWorkers" )
        self.pool_FrontWorkers = []
        for a in range( nb_Thread_FrontPage ):
            front_page_thread = FrontPage( self._q_front_urls, self._q_doc_urls , q_stats_front, allow_domains)
            self._logger.debug("Create a new front_page_thread instance" )
            #front_page_thread.daemon = True
            self.pool_FrontWorkers.append( front_page_thread )
        self._logger.debug("pool_FrontWorkers Initialized" )

    def run(self):
        for doc_page_thread in self.pool_FrontWorkers:
            doc_page_thread.start()

    def stop(self):
        for doc_page_thread in self.pool_FrontWorkers:
            doc_page_thread.stop()
