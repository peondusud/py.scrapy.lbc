
import logging

import requests
import queue
import time
from collections import namedtuple
import threading
from colorama import Fore, Back, Style

from lbc_FrontPage import *
from lbc_items import *


class BDD_file(threading.Thread):

    def __init__(self, q_documents):
        self._logger = logging.getLogger(__name__)
        super().__init__()
        self._q_documents = q_documents
        self._event = threading.Event()
        self._nb_object_saved = 0
        self._logger.debug("BDD_file initialized" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        self._event.clear()
        super().stop()


    def worker(self):
        nb_doc = 10

        self._logger.debug( Fore.RED + "BDD_file in worker" + Fore.RESET )
        with open("/home/peon/py.scrapy.lbc/py/lbc.json", 'w+') as f:
            bulk = []
            while 1:

                self._logger.debug(  Fore.RED + "Worker while1 loop q_documents.qsize : {}".format( self._q_documents.qsize() ) + Fore.RESET )
                self._logger.debug(  Fore.RED + "Worker while1 loop bulk size : {}".format( self._q_documents.qsize() ) + Fore.RESET )
                #if self._q_documents.qsize() > nb_doc:
                if len(bulk) > nb_doc:
                    self._logger.debug(  Fore.RED + "Worker enter if condition q_documents.qsize :{}".format( self._q_documents.qsize() ) + Fore.RESET )
                    self._logger.debug(  Fore.RED + "Worker enter if condition bulk size : {}".format( len(bulk) ) + Fore.RESET )
                    f.write( "\n".join(bulk) )
                    f.flush()
                    bulk = []
                    self._logger.info(  Fore.RED + "Worker write  {} documents".format( nb_doc ) + Fore.RESET )
                    self._nb_object_saved += nb_doc

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
        self._event.wait(timeout=None)
        self._logger.debug(Fore.RED + "lbc_BDD _event.wait passed"+ Fore.RESET)
        while self._event.is_set():
            self._logger.debug(Fore.RED + "lbc_BDD _event.wait passed"+ Fore.RESET)
            self.worker()
