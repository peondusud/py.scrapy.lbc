#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import sys
import logging

import requests
from urllib.parse import urlparse
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple
import threading
#from multiprocessing import Process, Value, Array, Pool

from lbc_FrontPage import *
from lbc_DocPage import *
from lbc_BDD import *


start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
    )


allow_domains = [ "leboncoin.fr" ]


class LBC_Orchestrator():
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._q_docPageUrls = queue.Queue()
        self._logger.debug(" _q_docPageUrls  created" )
        self._q_documents = queue.Queue()
        self._logger.debug("_q_documents  created" )

        self._logger.debug("BDD_orchestrator initialize" )
        self._bdd_center = BDD_orchestrator( self._q_documents)
        self._logger.debug("BDD_orchestrator initialized" )

        self._logger.debug("DocPage_orchestrator initialize" )
        self._docPage_center = DocPage_orchestrator(self._q_docPageUrls, self._q_documents)
        self._logger.debug("DocPage_orchestrator initialized" )

        self._logger.debug("FrontPage_orchestrator initialize" )
        self._frontPage_center = FrontPage_orchestrator( self._q_docPageUrls)
        self._logger.debug("FrontPage_orchestrator initialized" )


    def run(self):
        self._logger.debug("Launch _bdd_center.run()" )
        self._bdd_center.run()

        self._logger.debug("Launch _docPage_center.run()" )
        self._docPage_center.run()

        self._logger.debug("Launch _frontPage_center.run()" )
        self._frontPage_center.run()




class BDD_orchestrator():
    def __init__(self,   q_documents):
        self._logger = logging.getLogger(__name__)

        self._q_documents = q_documents
        self._logger.debug("self._q_documents  created" )

        self._logger.debug("BDD_file  initialize" )
        self._bdd_process = BDD_file( self._q_documents )

    def run(self):
        self._bdd_process.run()


class DocPage_orchestrator():
    def __init__(self,  q_doc_urls, q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )

        self._q_documents = q_documents
        self._logger.debug("_q_documents created" )
        nb_concurent_documentScraper = 16
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
                self._q_frontPageUrls.put(start_url)
            except queue.Full:
                self.logger.debug(" self.q_frontPageUrls queue Full:" )
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







def stats():
    pass

if __name__ == '__main__':

    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    lbc_center = LBC_Orchestrator()
    lbc_center.run()
