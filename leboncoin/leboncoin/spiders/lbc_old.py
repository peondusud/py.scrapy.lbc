# -*- coding: utf-8 -*-


import scrapy

from scrapy.loader import ItemLoader
from leboncoin.items import LeboncoinItem
from urlparse import urlparse
import re


class LbcSpider(scrapy.Spider):
    name = "lbc_old"
    allowed_domains = ["leboncoin.fr"]
    start_urls = (
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/',
        'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
    )

    def __init__(self, *args, **kwargs):
        super(LbcSpider, self).__init__(*args, **kwargs)


    def parse(self, response):

       urls = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href').extract()
       for doc_url in urls:
           #yield scrapy.Request(doc_url,callback=self.parse_page_loader)
           yield scrapy.Request(doc_url,callback=self.parse_page)

       nex = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]')
       next_url = nex.xpath('a/@href').extract()[-1]
       nb_page = next_url.split("?o=")[-1]
       last_page = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li/a/@href').extract()[-1].split("?o=")[-1]
       if nb_page == last_page:
            raise CloseSpider('End - Done') #must close spider

       yield scrapy.Request(next_url ,callback=self.parse)


    def get_id(self, url):
        print(url)
        parse_result = urlparse(url)
        tmp = parse_result.path
        tmp = tmp.split("/")[-1]
        id = tmp.split(".htm")[0]
        return int(id)

    def get_id_v2(self, url):
        #pattern = r"(\d{9})"
        pattern = r"^http://www.leboncoin.fr/.{,100}(\d{9})\.htm.{,50}$"
        m = re.search(pattern, url)
        id = m.group(1)
        return int(id)


    def parse_page(self, response):
       lbc_page = LeboncoinItem()

       lbc_page['doc_category'] = response.url.split("/")[3]
       lbc_page['doc_id'] = self.get_id_v2(response.url)
       lbc_page['doc_url'] = response.url

       content = response.xpath('/html/body/div/div[2]/div/div[3]')

       #titre
       lbc_page['title'] = content.xpath('div/div[1]/div[1]/h1/text()').extract()[0]


       tmp = content.xpath('div/span[@class="fine_print"]/a[@class="nohistory"]/text()').extract()
       try:
           lbc_page['region'] = tmp[1]
           lbc_page['doc_category'] = tmp[2]
       except IndexError:
           pass


       content2 = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]')

       imgs = content2.xpath('div/div[@class="lbcImages"]')
       lbc_page['img_urls'] = imgs.xpath('meta/@content').extract()

       upload = content2.xpath('div[@class="upload_by"]')
       lbc_page['user_url'] = upload.xpath('a/@href').extract()[0]
       lbc_page['user_id'] =  int(lbc_page['user_url'].split("id=")[1])
       lbc_page['user_name'] = upload.xpath('a/text()').extract()[0]
       lbc_page['upload_date'] = "".join(upload.xpath('text()').extract()).strip().replace("- Mise en ligne le ","").replace(u"à ","").replace(".","")

       tmp =  content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td')
       try:
           lbc_page['price_currency'] = tmp.xpath('meta/@content').extract()[0]
           lbc_page['price'] = int(tmp.xpath('span[@class="price"]/@content').extract()[0])
           lbc_page['urgent'] = tmp.xpath('span[@class="urgent"]/text()').extract()
           if lbc_page['urgent']:
               lbc_page['urgent'] = 1
           else:
               lbc_page['urgent'] = 0

       except IndexError:
           pass


       place =  content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]')
       try:
           lbc_page['addr_locality'] = place.xpath('tr/td[@itemprop="addressLocality"]/text()').extract()[0]
           lbc_page['postal_code'] = place.xpath('tr/td[@itemprop="postalCode"]/text()').extract()[0]
       except IndexError:
           pass

       try:
           geo_coords = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]')
           latitude = geo_coords.xpath('//meta[@itemprop="latitude"]/@content').extract()[0]
           longitude = geo_coords.xpath('//meta[@itemprop="longitude"]/@content').extract()[0]
           location = [longitude, latitude]
           lbc_page['location'] = map( float, location)
       except IndexError:
           pass


       criterias = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table//tr')

       dic = dict()
       for row in criterias:
           header = u"".join( map(lambda x: x.strip().replace(" :","") ,row.xpath('th/text()').extract()))
           value =  u"".join( map(lambda x: x.strip(), row.xpath('td/text()').extract()))
           if not value:
               value = u"".join(row.xpath('td//a/text()').extract())
           dic[header] = value
       lbc_page['criterias'] = dic

       description  = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()').extract()
       lbc_page['desc'] = u" ".join( map(lambda x: x.strip().replace("\n","").replace("  ","") ,description))

       return lbc_page
