
import logging

import requests
import queue
from collections import namedtuple

from lbc_FrontPage import *



class BDD_file():

    def __init__(self, q_documents):
        self._logger = logging.getLogger(__name__)
        self._q_documents = q_documents

    def run(self):
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
