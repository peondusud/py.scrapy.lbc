#!/usr/bin/env python3
# -- coding: utf-8 --


import logging
from colorama import Fore, Back, Style

        #google_user_agent = { 'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}

        self._http_headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer' : 'http://www.leboncoin.fr/',
        'Connection' : 'keep-alive' }



def bench_tornado_async( number_reqs, nb_worker):
    #http://tornado.readthedocs.org/en/latest/guide/async.html

    start = datetime.datetime.now()
    print('Start : ', start)
    l = []
    def handle_request(response):
        if response.error:
            print("Error:", response.error)
        else:
            l.append(1)
            l_size = len(l)
            print(l_size)
            #print(len(response.body))
            if l_size == number_reqs:
                tornado.ioloop.IOLoop.instance().stop()
            if datetime.datetime.now() - start == 60:
                tornado.ioloop.IOLoop.instance().stop()

    http_client = AsyncHTTPClient(max_clients = nb_worker)
    http_client.configure( None,
                        method = "GET",
                        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                        # max_clients determines the maximum number of simultaneous fetch() operations that can execute in parallel on each IOLoop
                        max_clients = nb_worker
                        )


    def url_generator():
        for elem in range(int(number_reqs/nb_worker)):
            for e in range(nb_worker):
                http_client.fetch("http://www.leboncoin.fr/",
                                    method='GET',
                                    callback=handle_request)
            time.sleep(1)

    threading.Thread(target=url_generator).start()
    tornado.ioloop.IOLoop.instance().start()
    print('[Tornado] Done :', datetime.datetime.now() - start)
