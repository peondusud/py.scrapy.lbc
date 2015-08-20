#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import logging
from colorama import Fore, Back, Style
import datetime

import requests
from urllib.parse import urlparse
from lxml import html     #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple
import threading
import itertools
#from multiprocessing import Process, Value, Array, Pool

from lbc_FrontPage import *
from lbc_DocPage import *
from lbc_BDD import *


start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/', #debug criterias
        #'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/informatique/offres/ile_de_france/occasions/?f=c', #debug pro
    )


allow_domains = [ "leboncoin.fr" ]


class LBC_Orchestrator():
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._q_docPageUrls = queue.Queue()
        self._logger.debug("LBC_Orchestrator _q_docPageUrls  created" )
        self._q_documents = queue.Queue()
        self._logger.debug("LBC_Orchestrator _q_documents  created" )

        self._logger.debug("LBC_Orchestrator BDD_orchestrator initialize" )
        self._bdd_center = BDD_orchestrator( self._q_documents)
        self._logger.debug("LBC_Orchestrator BDD_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator DocPage_orchestrator initialize" )
        self._docPage_center = DocPage_orchestrator(self._q_docPageUrls, self._q_documents)
        self._logger.debug("LBC_Orchestrator DocPage_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator FrontPage_orchestrator initialize" )
        self._frontPage_center = FrontPage_orchestrator( self._q_docPageUrls)
        self._logger.debug("LBC_Orchestrator FrontPage_orchestrator initialized" )

        self._logger.debug("LBC_Orchestrator initialized" )


    def run(self):
        self._logger.debug("LBC_Orchestrator Launch _bdd_center.run()" )
        self._bdd_center.run()

        self._logger.debug("LBC_Orchestrator Launch _docPage_center.run()" )
        self._docPage_center.run()

        self._logger.debug("LBC_Orchestrator Launch _frontPage_center.run()" )
        self._frontPage_center.run()

        #self.stats()
        self.updateStatistics()


    def stats(self):
        t = threading.Thread(target=self.updateStatistics, args=(self._q_documents , self._bdd_center ))
        t.daemon = True
        t.start()

    #def updateStatistics( self , queue_doc, bdd_center ):
    def updateStatistics( self ):
        start_time = time.time()
        interval = 2 # wait  in second
        last_value = 0

        next_call = time.time()
        while 1:
            nb_docs_saved =  self._bdd_center._bdd_thread._nb_object_saved
            now = time.time()
            time_passed = now - start_time
            print("nb_docs_saved", nb_docs_saved)
            print("time_passed", time_passed)
            req_by_min = nb_docs_saved * time_passed/60
            print("req_by_min", req_by_min )
            print( datetime.datetime.now() )
            next_call += interval
            time.sleep( next_call - time.time() )


class BDD_orchestrator():
    def __init__(self,   q_documents):
        self._logger = logging.getLogger(__name__)

        self._q_documents = q_documents
        self._logger.debug("BDD_orchestrator self._q_documents  created" )

        self._logger.debug("BDD_orchestrator BDD_file  initialize" )
        self._bdd_thread = BDD_file( self._q_documents )

    def run(self):
        self._logger.debug("BDD_orchestrator BDD_file  in run()" )
        self._bdd_thread.start()


class DocPage_orchestrator():
    def __init__(self,  q_doc_urls, q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )

        self._q_documents = q_documents
        self._logger.debug("_q_documents created" )
        nb_concurent_documentScraper = 1
        #equals Nmber of concuremnt connection
        # Same nb_Thread_DocPage = 4
        self.pool_DocPageWorkers = []

        self._logger.debug("initialize pool_DocPageWorkers" )
        for a in range(nb_concurent_documentScraper):
            doc_page_thread = DocPage( self._q_doc_urls, self._q_documents )
            self._logger.debug("Create a new doc_page_thread instance" )
            self.pool_DocPageWorkers.append( doc_page_thread )
        self._logger.debug("pool_DocPageWorkers Initialized" )

    def run(self):
        for doc_page_thread in self.pool_DocPageWorkers:
            doc_page_thread.start()


class FrontPage_orchestrator():

    def __init__(self,  q_doc_urls):
        self._logger = logging.getLogger(__name__)

        self._q_frontPageUrls = queue.Queue()
        self._logger.debug("_q_frontPageUrls created" )

        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )

        for start_url in start_urls:
            try:
                self._q_frontPageUrls.put(start_url, block=True, timeout=None)
            except queue.Full:
                self.logger.debug(" self.q_frontPageUrls queue Full" )
        nb_Thread_FrontPage = self._q_frontPageUrls.qsize()

        self._logger.debug("initialize pool_FrontWorkers" )
        self.pool_FrontWorkers = []
        for a in range( nb_Thread_FrontPage ):
            front_page_thread = FrontPage( self._q_frontPageUrls, self._q_doc_urls )
            self._logger.debug("Create a new front_page_thread instance" )
            self.pool_FrontWorkers.append( front_page_thread )
        self._logger.debug("pool_FrontWorkers Initialized" )

    def run(self):
        for doc_page_thread in self.pool_FrontWorkers:
            doc_page_thread.start()



if __name__ == '__main__':
    logger = logging.getLogger(__name__)


    #logging.basicConfig(level=logging.DEBUG)

    logging.basicConfig(filename="lbc.log", level=logging.INFO)

    lbc_center = LBC_Orchestrator()
    lbc_center.run()
    logger.debug(" all running" )
