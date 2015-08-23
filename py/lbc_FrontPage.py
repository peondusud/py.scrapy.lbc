import os
import sys
import re
import logging
from colorama import Fore, Back, Style

import requests
import http.cookiejar
from urllib.parse import urlparse
from lxml import html	 #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev

import queue
from collections import namedtuple
import threading


allow_domains = [ "leboncoin.fr" ]

class FrontPage(threading.Thread):

    def __init__(self, q_front_urls , q_doc_urls, q_stats_front ):
        self._logger = logging.getLogger(__name__)

        super().__init__()

        self._q_front_urls = q_front_urls
        self._logger.debug("_q_front_urls created" )

        self._q_doc_urls = q_doc_urls
        self._logger.debug("_q_doc_urls created" )


        google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'DNT': '1',
        'Referer' : 'http://www.leboncoin.fr/',
        'Connection' : 'keep-alive' }
        self._session = requests.session()
        self._session.headers.update( headers )
        self._logger.debug("Init Session Headers : {}".format( self._session.headers )  )
        self._logger.debug("_session created" )

        self._event = threading.Event()

    def worker(self ):
        try:
            frontPage_url = self._q_front_urls.get(block=True, timeout=None)
            self._logger.info( Fore.BLUE + "FRONT URL to Fetch : {}".format( frontPage_url ) + Fore.RESET )

        except queue.Empty:
            self._logger.debug(" self.frontPage_url queue Empty" )
            return

        page = self.fetch( frontPage_url )
        #self._logger.debug( "page {}".format( page ))
        if (page is not None ) or  (not page) :
            self._logger.debug("page No empty" )
            self.scrap(page)
        else:
            self._logger.error( "page empty or None" )

    def fetch(self, frontPage_url):

        self._logger.debug( "Fetch session cookies Before web request : {}".format( self._session.cookies.items() )  )
        self._logger.debug("Handling request : {}".format( frontPage_url) )
        response = self._session.get( frontPage_url , timeout=3)
        #response = requests.get( self.docPage_url , timeout=None) #FIXME
        self._logger.debug( "Fetch session cookies After web request : {}".format( self._session.cookies.items() )  )
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        #self._logger.debug( "Fetch headers sent to server : {}".format( response.request.headers)  )
        #self._logger.debug( "Fetch headers sent from server : {}".format( response.headers)  )
        return response.text


    def scrap(self, page):

        self.tree = html.fromstring( page )
        self.get_docUrls_fromTree( self.tree )
        self.get_nextUrl_fromTree(self.tree )

    def get_docUrls_fromTree(self , tree):
        # retrieve 25 elems doc page url
        content_urls = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href')
        #remove shity parameter in content_urls
        wipe_url = lambda x : x.split("?")[0]
        content_urls_wipe = list(map(wipe_url, content_urls))
        self.add_Queue_DocUrls( content_urls_wipe )
        self._logger.debug( "content_urls : {}".format( content_urls ))
        self._logger.debug( "content_urls_wipe : {}".format( content_urls_wipe ))

    def get_nextUrl_fromTree(self, tree):
        prev_nxt_url = tree.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]/a/@href')
        next_url = prev_nxt_url[-1]
        nb_page = next_url.split("?o=")[-1]
        self._logger.debug( "next_url : {}".format( next_url ))
        self._logger.debug( "nb_page : {}".format( nb_page ))
        self.add_Queue_nextFrontPageUrl(next_url)

    def add_Queue_nextFrontPageUrl(self, next_url):
        #verify in allow_domain
        if self.url_isAllow( next_url):
            #add to queue new front page url
            try:
                self._logger.debug( "Try Add to q_front_urls {}".format(next_url) )
                self._q_front_urls.put( next_url, block=True, timeout=None)
                self._logger.debug( Fore.GREEN + "{} Added to q_front_urls".format(next_url) + Fore.RESET )
            except queue.Full:
                self._logger.debug(" self.q_doc_url queue Full" )

    def add_Queue_DocUrls(self,content_urls):
        #add doc url to doc queue
        for page_url in content_urls:
            if  self.url_isAllow( page_url ):
                self._logger.debug( Fore.GREEN + "{} is an Allow URL".format( page_url) + Fore.RESET )

                try:

                    self._q_doc_urls.put( page_url, block=True, timeout=None )
                    self._logger.debug( Fore.GREEN + "Added {} to queue".format(page_url) + Fore.RESET )
                except queue.Full:
                    self._logger.debug(" self.q_doc_url queue Full" )

    def url_isAllow(self, url_to_check):
        o = urlparse(url_to_check)
        for allow_domain in allow_domains:
            if allow_domain in o.netloc:
                self._logger.debug( Fore.GREEN + "{} is an Allow URL. Domain {}".format(url_to_check, allow_domain) + Fore.RESET )
                return True
        self._logger.debug(  Fore.RED + "{} is not Allow URL".format( url_to_check ) + Fore.RESET )
        return False


    def start(self):
        super().start()
        self._event.set()


    def stop(self):
        self._event.clear()
        super().stop()

    def run(self):
        self._event.wait(timeout=None)
        while self._event.is_set():
            try:
                self.worker()
                #ime.sleep(1)   #FIXME
            except Exception as e:
                self._logger.debug( "exception {} FrontPage loop".format(e) )

        self._logger.info("Finished or stopped FrontPage loop")
