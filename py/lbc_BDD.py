
import logging

import requests
import queue
import time
from collections import namedtuple
import threading
from colorama import Fore, Back, Style

from lbc_FrontPage import *



class BDD_file(threading.Thread):

    def __init__(self, q_documents):
        self._logger = logging.getLogger(__name__)
        super().__init__()
        self._q_documents = q_documents
        self._event = threading.Event()
        self._logger.debug("BDD_file initialized" )


    def start(self):
        super().start()
        self._event.set()

    def stop(self):
        self._event.clear()
        super().stop()


    def worker(self):
        nb_doc = 1
        bulk = []
        self._logger.debug( Fore.GREEN + "BDD_file in worker" + Fore.RESET )
        with open("/home/peon/py.scrapy.lbc/py/lbc.json", 'w') as f:
            while 1:
                self._logger.debug( Fore.GREEN + "BDD_file in worker while1" + Fore.RESET )

                self._logger.info(  Fore.GREEN + "BDD_file in worker aaaaaaaa{}".format( self._q_documents.qsize() ) + Fore.RESET )
                if self._q_documents.qsize() > nb_doc:
                    self._logger.info(  Fore.GREEN + "BDD_file in worker {}".format( self._q_documents.qsize() ) + Fore.RESET )

                    f.write( "\n".join(bulk) )
                    bulk = []
                try:
                    document = self._q_documents.get(block=True, timeout=None)
                    document_json = document.json_it()
                    bulk.append( document_json )
                except queue.Empty:
                    self._logger.debug(Fore.GREEN + "lbc_BDD self._q_documents queue Empty" + Fore.RESET )
                    self._logger.info(Fore.GREEN + "Finished or stopped DocPage loop" + Fore.RESET)
                self._logger.info(Fore.GREEN + "sleep 1" + Fore.RESET)
                time.sleep(1)#FIXME
        f.close()
        self.logger.info(Fore.GREEN + "Finished or stopped DocPage loop"+ Fore.RESET)


    def run(self):
        self._event.wait(timeout=None)
        self._logger.info(Fore.GREEN + "lbc_BDD _event.wait passed"+ Fore.RESET)
        while self._event.is_set():
            self._logger.info(Fore.GREEN + "lbc_BDD _event.wait passed"+ Fore.RESET)
            self.worker()
