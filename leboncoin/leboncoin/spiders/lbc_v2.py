# -*- coding: utf-8 -*-


import scrapy

from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from leboncoin.items import LeboncoinItem
from urlparse import urlparse, parse_qs
from datetime import date, datetime
import time
import re


class LbcSpider(scrapy.Spider):
    name = "lbc_v2"
    allowed_domains = ["leboncoin.fr"]
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = u" ".join((DATE_FORMAT, TIME_FORMAT))


    start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/', #all ads
        #'http://www.leboncoin.fr/voitures/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/',
        #'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/informatique/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/image_son/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/ameublement/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/electromenager/offres/ile_de_france/occasions/',
    )

    def __init__(self, *args, **kwargs):
        self.thumb_pattern = re.compile(ur'^background-image: url\(\'(?P<url>[\w/:\.]+)\'\);$')
        self.date_pattern = re.compile(ur'Mise en ligne le (?P<day>\d\d?) (?P<month>[a-zéû]+) . (?P<hour>\d\d?):(?P<minute>\d\d?)')
        self.doc_id_pattern = re.compile(ur"^http://www.leboncoin.fr/.{0,100}(?P<id>\d{9})\.htm.{0,50}$")
        self.uploader_id_pattern = re.compile(ur"^http.{0,50}(?P<id>\d{9,12})$")
        self.criteria_pattern = re.compile(ur'^\s{2}(?P<key>\w+) : "(?P<val>\w+)",?', re.MULTILINE)
        self.nb_page = 0
        self.nb_doc = 0
        super(LbcSpider, self).__init__(*args, **kwargs)


    def parse(self, response):

       content = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]')
       urls = content.xpath('div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]/a/@href').extract()
       self.nb_doc = len(urls)
       for doc_url in urls:
           #print("doc_url", doc_url)
           #yield scrapy.Request(doc_url,callback=self.parse_page_loader)
           yield scrapy.Request(doc_url,callback=self.parse_page)

       page_urls = content.xpath('nav/ul[@id="paging"]//li[@class="page"]/a/@href').extract()
       next_url = page_urls[-1]
       nb_page = next_url.split("?o=")[-1]
       last_page = content.xpath('nav/ul[@id="paging"]//li/a/@href').extract()
       last_page = last_page[-1].split("?o=")[-1]
       if nb_page == last_page:
           while True:
               if self.nb_doc == 0:
                   raise CloseSpider('End - Done') #must close spider
               time.sleep(1)
       self.nb_page += 1
       yield scrapy.Request(next_url ,callback=self.parse)

    def proper_url(self, url):
        """
        remove = "?ca=12_s" frm url
        """
        #return url.split('?')[0]
        return url[:-8]


    def get_doc_id(self, url):
        print(url)
        parse_result = urlparse(url)
        tmp = parse_result.path
        tmp = tmp.split("/")[-1]
        id = tmp.split(".htm")[0]
        return int(id)

    def get_id_regex(self, url):
        #pattern = r"(\d{9})"
        m = re.search(self.doc_id_pattern, url)
        id = m.group('id')
        return int(id)

    def get_uploader_id(self, url):
        parse_result = urlparse(url)
        tmp = parse_result.query
        tmp = tmp.split("id=")[-1]
        return int(tmp)

    def get_uploader_id_regex(self, url):
        m = re.search(self.uploader_id_pattern, url)
        id = m.group('id')
        return int(id)


    def get_date(self, str):
        text = u''.join(str)
        t = re.search(self.date_pattern, text).groupdict()
        monthDict = {
                        u'janvier': 1,
                        u'février': 2,
                        u'mars': 3 ,
                        u'avril': 4,
                        u'mai': 5,
                        u'juin': 6,
                        u'juillet': 7,
                        u'août': 8,
                        u'septembre': 9,
                        u'octobre': 10,
                        u'novembre': 11,
                        u'décembre': 12
                    }
        if t is not None:
            for key, val in monthDict.items():
                if key == t['month']:
                    t['month'] = val
            now = date.today()
            year   = now.year
            month  = int(t['month'])
            day    = int(t['day'])
            hour   = int(t['hour'])
            minute = int(t['minute'])

            date_tmp = date(year, month, day)
            #Prevent to have ads in future date
            #Example if parsed in january with an ads date in december
            if date_tmp > now:
                #set previous year
                year -= 1
            d = datetime(year, month, day, hour, minute)

            date_str = d.strftime(self.DATETIME_FORMAT)
            return date_str
        return ""


    def proper_thumbs_url(self, urls):
        thumb_urls = list()
        for elem in urls:
            m = re.search(self.thumb_pattern, elem)
            if m is not None:
                thumb_urls.append(m.group('url'))
        return thumb_urls

    def jsVar_2_pyDic(self, criterias):
        return dict(re.findall(self.criteria_pattern,criterias))

    def proper_description(self, desc):
        str = u"\n".join(desc)
        str = str.strip()
        #str = str.replace("\n","")
        #str = str.replace("  ","")
        return str

    def parse_page(self, response):
       lbc_page = LeboncoinItem()

       lbc_page['doc_url'] = self.proper_url(response.url)

       content = response.xpath('/html/body/div/div[2]/div/div[3]')

       #titre
       lbc_page['title'] = content.xpath('div/div[1]/div[1]/h1/text()').extract()
       try:
           lbc_page['title'] = lbc_page['title'][0]
       except IndexError:
           print("BUG title doc_url", lbc_page['doc_url'])

       content2 = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]')

       imgs = content2.xpath('div/div[@class="lbcImages"]')
       thumbs = imgs.xpath('div[@class="thumbs_carousel_window"]/div[@id="thumbs_carousel"]//span[@class="thumbs"]/@style').extract()
       lbc_page['img_urls'] = imgs.xpath('meta/@content').extract()
       lbc_page['thumbs_urls'] = self.proper_thumbs_url(thumbs)

       upload = content2.xpath('div[@class="upload_by"]')
       try:
           lbc_page['user_name'] = upload.xpath('a/text()').extract()[0]
       except IndexError:
          pass

       text = u''.join(upload.xpath('text()').extract())
       lbc_page['upload_date'] = self.get_date(text)
       lbc_page['check_date'] = datetime.now().strftime(self.DATETIME_FORMAT)


       #lbc_page['urgent'] = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()').extract()
       lbc_page['urgent'] = content2.xpath('//span[@class="urgent"]/text()').extract()
       if lbc_page['urgent']:
           lbc_page['urgent'] = 1
       else:
           lbc_page['urgent'] = 0


       place = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]')
       try:
           lbc_page['addr_locality'] = place.xpath('tr/td[@itemprop="addressLocality"]/text()').extract()[0]
       except IndexError:
           pass

       try:
           geo_coords = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]')
           latitude = geo_coords.xpath('//meta[@itemprop="latitude"]/@content').extract()[0]
           longitude = geo_coords.xpath('//meta[@itemprop="longitude"]/@content').extract()[0]
           location = [longitude, latitude]
           lbc_page['location'] = map(float, location)
       except IndexError:
           pass

       criterias = response.xpath('/html/body/script[1]/text()').extract()[0]
       lbc_page['criterias'] = self.jsVar_2_pyDic(criterias)


       description  = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()').extract()
       lbc_page['desc'] = self.proper_description(description)

       self.nb_page -= 1 #decrement cnt usefull for stop spider
       return lbc_page
