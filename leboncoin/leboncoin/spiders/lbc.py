# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from leboncoin.items import LeboncoinItem
from scrapy.loader.processors import TakeFirst
from urlparse import urlparse, parse_qs
from datetime import date, datetime
import logging
import time
import re


class LbcSpider(scrapy.Spider):
    name = "lbc"
    allowed_domains = ["leboncoin.fr"]
    DATE_FORMAT = "%Y.%m.%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = u" ".join((DATE_FORMAT, TIME_FORMAT))


    start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/', #all ads
        #'http://www.leboncoin.fr/voitures/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/',
        'http://www.leboncoin.fr/annonces/offres/ile_de_france/?f=a&q=boule+facette',
        #'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/informatique/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/image_son/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/ameublement/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/electromenager/offres/ile_de_france/occasions/',
    )

    def __init__(self, *args, **kwargs):
        self.thumb_pattern = re.compile(ur'^background-image: url\(\'(?P<url>[\w/:\.]+)\'\);$')
        self.date_pattern = re.compile(ur'Mise en ligne le (?P<day>\d\d?) (?P<month>[a-zéû]+) . (?P<hour>\d\d?):(?P<minute>\d\d?)')
        self.doc_id_pattern = re.compile(ur"^http://www\.leboncoin\.fr/.{0,100}(?P<id>\d{9})\.htm.{0,50}$")
        self.uploader_id_pattern = re.compile(ur"^http.{0,50}(?P<id>\d{9,12})$")
        self.uploader_id_regex = re.compile(ur"^http:\/\/\w+\.leboncoin\.fr\/.{0,100}id=(?P<id>\d+).*?$")
        self.criteria_pattern = re.compile(ur'^\s{2}(?P<key>\w+) : "(?P<val>\w+)",?', re.MULTILINE)
        self.page_offset_regex = re.compile(ur"^http:\/\/www\.leboncoin\.fr\/.{0,100}\/\?o=(?P<offset>\d+).+$")
        self.nb_page = 0
        self.nb_doc = 0
        self.takeFirst = TakeFirst()
        super(LbcSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
       self.logger.debug("response.url", response.url)
       content = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]')
       urls = content.xpath('div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]/a/@href').extract()

       page_urls = content.xpath('nav/ul[@id="paging"]//li[@class="page"]/a/@href').extract()
       last_page = content.xpath('nav/ul[@id="paging"]//li/a/@href').extract()

       next_url = page_urls[-1]

       nb_page = self.offset_url_page_regex(next_url) - 1

       last_page = self.offset_url_page_regex(last_page[-1])
       self.logger.debug("nb_page, last_page", nb_page, last_page )

       if nb_page == last_page:
           while True:
               if self.nb_doc == 0:
                   raise CloseSpider('End - Done') #must close spider
               self.logger.debug("Wait to close spider nb doc left", self.nb_doc)
               self.logger.debug("wait to close spider offset page", self.nb_page)
               time.sleep(1)
       else:
          for doc_url in urls:
              self.nb_doc += 1
              yield scrapy.Request(doc_url, callback=self.parse_page)
       self.nb_page += 1
       yield scrapy.Request(next_url, callback=self.parse)


    def proper_url(self, url):
        """
        remove = "?ca=12_s" frm url
        """
        #return url.split('?')[0]
        return url[:-8]

    def offset_url_page_regex(self, url):
        m = re.search(self.page_offset_regex, url)
        if m is not None:
            url_page_offset = m.group('offset')
        else:
            url_page_offset = 1
        return int(url_page_offset)

    def get_url_page_offset_urlparse(self, url):
        url_parsed = urlparse(url)
        query_string = url_parsed.query
        offset_str = parse_qs(query_string).get('o', '1')
        offset = int(offset_str[-1]) #string trick
        return offset

    def offset_url_page_split(self, url):
         offset_str = url.split("?o=")[-1].split('&')
         offset = int(offset_str[0])
         return offset_str

    def get_doc_id(self, url):
        self.logger.debug(url)
        parse_result = urlparse(url)
        tmp = parse_result.path
        tmp = tmp.split("/")[-1]
        id = tmp.split(".htm")[0]
        return int(id)

    def get_id_regex(self, url):
        #pattern = r"(\d{9})"
        m = re.search(self.doc_id_pattern, url)
        if m is not None:
            return int(m.group('id'))
        return url

    def get_uploader_id(self, url):
        parse_result = urlparse(url)
        tmp = parse_result.query
        tmp = tmp.split("id=")[-1]
        return int(tmp)

    def get_uploader_id_regex(self, url):
        #m = re.search(self.uploader_id_pattern, url)
        m = re.search(self.uploader_id_regex, url)
        if m is not None:
            uploader_id = m.group('id')
            return int(uploader_id)
        return url

    def get_date(self, str):
        text = u''.join(str)
        t = re.search(self.date_pattern, text).groupdict()
        monthDict = {   u'janvier': 1,
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
                        u'décembre': 12  }
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
        return ''

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
       self.logger.debug("page nb doc", self.nb_doc, response.url)
       lbc_page['doc_url'] = self.proper_url(response.url)

       content = response.xpath('/html/body/div/div[2]/div/div[3]')

       lbc_page['title'] = self.takeFirst(content.xpath('div/div[1]/div[1]/h1/text()').extract())


       content2 = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]')

       imgs = content2.xpath('div/div[@class="lbcImages"]')
       thumbs = imgs.xpath('div[@class="thumbs_carousel_window"]/div[@id="thumbs_carousel"]//span[@class="thumbs"]/@style').extract()
       lbc_page['img_urls'] = imgs.xpath('meta/@content').extract()
       lbc_page['thumb_urls'] = self.proper_thumbs_url(thumbs)

       upload = content2.xpath('div[@class="upload_by"]')

       lbc_page['user_name'] = self.takeFirst(upload.xpath('a/text()').extract())

       user_url = self.takeFirst( upload.xpath('a/@href').extract() )
       #lbc_page['user_url'] = self.proper_url(user_url)
       lbc_page['user_id'] = self.get_uploader_id_regex(user_url)

       text = u''.join(upload.xpath('text()').extract())
       lbc_page['upload_date'] = self.get_date(text)
       lbc_page['check_date'] = datetime.now().strftime(self.DATETIME_FORMAT)

       #urgent = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()').extract()
       urgent = content2.xpath('//span[@class="urgent"]/text()').extract()
       if urgent:
           lbc_page['urgent'] = 1
       else:
           lbc_page['urgent'] = 0

       place = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]')

       lbc_page['addr_locality'] = self.takeFirst(place.xpath('tr/td[@itemprop="addressLocality"]/text()').extract())

       geo_coords = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]')
       latitude = self.takeFirst(geo_coords.xpath('.//meta[@itemprop="latitude"]/@content').extract())
       longitude = self.takeFirst(geo_coords.xpath('.//meta[@itemprop="longitude"]/@content').extract())
       if longitude and latitude:
           lbc_page['location'] = [float(longitude), float(latitude)]

       criterias = self.takeFirst(response.xpath('/html/body/script[1]/text()').extract())
       lbc_page['criterias'] = self.jsVar_2_pyDic(criterias)

       description  = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()').extract()
       lbc_page['desc'] = self.proper_description(description)

       self.nb_doc -= 1 #decrement cnt usefull for stop spider
       return lbc_page
