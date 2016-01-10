import random
import logging

#http://www.freeproxylists.net/fr/?c=FR&pt=&pr=HTTP&a[]=0&a[]=1&a[]=2&u=0
PROXIES = [
        "94.23.247.76:3128",
        "94.23.200.49:3128",
        "194.214.185.37:80",
        "94.247.25.162:80",
        "91.121.181.168:80",
        "178.33.195.50:8080",
        "46.105.61.127:3128",
        "193.49.97.60:80",
        "178.33.214.8:8080",
        "94.247.25.163:80",
        "178.33.191.53:3128",
        "178.33.201.93:8080",
        "178.32.129.14:3128",
        "212.83.147.0:80",
        "80.14.12.161:80"
]

"""
Custom proxy provider.
http://doc.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.httpproxy
"""
class CustomHttpProxyMiddleware(object):
    
    def process_request(self, request, spider):
        if self.use_proxy(request):    
            ip_port = random.choice(PROXIES)
            try:
                request.meta['proxy'] = "http://%s" % ip_port
            except Exception, e:
                logging.error("Exception {}".format(e))

    def use_proxy(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 0.3
        """
        if "depth" in request.meta and int(request.meta['depth']) <= 2:
            return False
        i = random.randint(1, 10)
        return i <= 2


    def use_proxy_v2(self, request):
        """
        using direct download for depth <= 2
        using proxy with probability 1
        """
        if "depth" in request.meta and int(request.meta['depth']) <= 2:
            return False
        return True 

AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


]

"""
change request header nealy every time
"""
class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent

