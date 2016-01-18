# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from leboncoin.items import LeboncoinItem
from urlparse import urlparse, parse_qs
from datetime import date, datetime
import time
import re

class LbcSpider(scrapy.Spider):
    name = "lbc_no_proper"
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
        self.first = TakeFirst()
        super(LbcSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
       content = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]')
       urls = content.xpath('div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]/a/@href').extract()
       self.nb_doc = len(urls)
       for doc_url in urls:
           yield scrapy.Request(doc_url,callback=self.parse_ad_page)
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


    def parse_ad_page(self, response):
       lbc_ad_item = LeboncoinItem()
       lbc_ad_item['doc_url'] = response.url
       #lbc_ad_item = {}

       content = response.xpath('/html/body/div/div[2]/div/div[3]')

       #titre
       lbc_ad_item['title'] = content.xpath('div/div[1]/div[1]/h1/text()').extract()

       content2 = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]')
       imgs = content2.xpath('div/div[@class="lbcImages"]')
       lbc_ad_item['img_urls'] = imgs.xpath('meta/@content').extract()
       lbc_ad_item['thumb_urls'] = imgs.xpath('div[@class="thumbs_carousel_window"]/div[@id="thumbs_carousel"]//span[@class="thumbs"]/@style').extract()

       upload = content2.xpath('div[@class="upload_by"]')
       lbc_ad_item['user_name'] = upload.xpath('a/text()').extract()
       lbc_ad_item['user_url'] = upload.xpath('a/@href').extract()
       lbc_ad_item['upload_date'] = u''.join(upload.xpath('text()').extract())
       lbc_ad_item['check_date'] = self.get_check_date()

       lbc_ad_item['urgent'] = content2.xpath('//span[@class="urgent"]/text()').extract()

       place = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]')
       lbc_ad_item['addr_locality'] = place.xpath('tr/td[@itemprop="addressLocality"]/text()').extract()

       geo_coords = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]')
       lbc_ad_item['latitude'] = geo_coords.xpath('//meta[@itemprop="latitude"]/@content').extract()
       lbc_ad_item['longitude'] = geo_coords.xpath('//meta[@itemprop="longitude"]/@content').extract()

       lbc_ad_item['criterias'] = response.xpath('/html/body/script[1]/text()').extract()

       lbc_ad_item['desc'] = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()').extract()

       self.nb_page -= 1 #decrement cnt usefull for stop spider

       return lbc_ad_item

    def get_check_date(self):
        d = datetime.now()
        date_str = d.strftime(self.DATETIME_FORMAT)
        return date_str
