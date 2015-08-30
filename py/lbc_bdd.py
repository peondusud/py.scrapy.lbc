#!/usr/bin/env python3
# -- coding: utf-8 --

import os
import logging
import queue
import time
import threading
from colorama import Fore, Back, Style



class BDD_file(threading.Thread):

    def __init__(self, q_documents, q_stats_bdd, bdd_bulksize, bdd_filename ):
        self._logger = logging.getLogger(__name__)
        super().__init__()
        self._q_documents = q_documents
        self._event = threading.Event()
        self._q_stats_bdd = q_stats_bdd
        self._bulk_nb_doc = bdd_bulksize
        self._bdd_filename = bdd_filename
        self._logger.debug("BDD_file initialized" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        self._event.clear()
        super().stop()


    def worker(self):
        nb_objects_saved = 0
        self._logger.debug( Fore.RED + "BDD_file in worker" + Fore.RESET )
        path = os.path.join( os.getcwd(), self._bdd_filename )
        with open( path , 'w+') as f:
            bulk = []
            while 1:
                self._logger.debug(  Fore.RED + "Worker while1 loop q_documents.qsize : {}".format( self._q_documents.qsize() ) + Fore.RESET )
                self._logger.debug(  Fore.RED + "Worker while1 loop bulk size : {}".format( self._q_documents.qsize() ) + Fore.RESET )
                #if self._q_documents.qsize() > nb_doc:
                if len(bulk) > self._bulk_nb_doc :
                    self._logger.debug(  Fore.RED + "Worker enter if condition q_documents.qsize :{}".format( self._q_documents.qsize() ) + Fore.RESET )
                    self._logger.debug(  Fore.RED + "Worker enter if condition bulk size : {}".format( len(bulk) ) + Fore.RESET )
                    f.write( "\n".join(bulk) )
                    f.flush()
                    bulk = []
                    self._logger.info( Fore.RED + "Worker write  {} documents".format( self._bulk_nb_doc ) + Fore.RESET )

                    nb_objects_saved += self._bulk_nb_doc
                    try:
                        self._q_stats_bdd.put( nb_objects_saved )
                    except queue.Full:
                        self._logger.debug("self._q_stats_bdd queue Full" )
                try:
                    document = self._q_documents.get(block=True, timeout=None)
                    self._logger.debug( Fore.RED + "Worker loop document {}".format( document ) + Fore.RESET)
                    document_json = document.json_it()
                    self._logger.debug( Fore.RED + "Worker loop document_json {}".format( document_json ) + Fore.RESET)
                    bulk.append( document_json )
                except queue.Empty:
                    self._logger.debug( Fore.RED + "lbc_BDD self._q_documents queue Empty" + Fore.RESET )
                self._logger.debug(Fore.RED + "Worker sleep 1" + Fore.RESET)
                time.sleep(1) #FIXME
        self._logger.debug(Fore.RED + "Finished or stopped BDD_file loop"+ Fore.RESET)


    def run(self):
        self._event.wait( timeout=None )
        self._logger.debug(Fore.RED + "lbc_BDD _event.wait passed"+ Fore.RESET)
        while self._event.is_set():
            self._logger.debug(Fore.RED + "lbc_BDD _event.wait passed"+ Fore.RESET)
            self.worker()