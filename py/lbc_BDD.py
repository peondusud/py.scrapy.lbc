
import logging

import requests
import queue
import time
from collections import namedtuple
import threading


from lbc_FrontPage import *



class BDD_file(threading.Thread):

    def __init__(self, q_documents):
        self._logger = logging.getLogger(__name__)
        super().__init__()
        self._q_documents = q_documents
        self._event = threading.Event()


    def start(self):
        self._event.set()
        super().start()

    def stop(self):
        self._event.clear()
        super().stop()


    def run(self):

        while self._event.is_set():
            with open("lbc.json", 'w') as f:
                while 1:
                    nb_doc = 1000
                    if self._q_documents.qsize() > nb_doc:
                        bulk = []
                        for document in range(nb_doc):
                            try:
                                document_json = self._q_documents.get()
                                bulk.append( document_json )
                            except queue.Empty:
                                self._logger.debug(" self.url2fetch queue Empty:" )
                        f.write("".join(bulk))
                    time.sleep(0.3)
