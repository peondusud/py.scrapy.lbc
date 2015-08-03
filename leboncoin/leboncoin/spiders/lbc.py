# -*- coding: utf-8 -*-
import scrapy


from leboncoin.items import LeboncoinItem

class LbcSpider(scrapy.Spider):
    name = "lbc"
    allowed_domains = ["leboncoin.fr"]
    start_urls = (
        #'http://www.leboncoin.fr/utilitaires/837117373.htm',
        #'http://www.leboncoin.fr/informatique/837420855.htm',
        #'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/?f=a&th=1',
        'http://www.leboncoin.fr/_immobilier_/offres/ile_de_france/occasions/?o=2',
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/?th=1',
    )

    def parse(self, response):

       urls = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/div[@class="content-border list"]/div[@class="content-color"]/div[@class="list-lbc"]//a/@href').extract()
       for doc_url in urls:
           #continue
           yield scrapy.Request(doc_url,callback=self.parse_page)
       nex = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li[@class="page"]')
       next_url = nex.xpath('a/@href').extract()[-1]
       nb_page = next_url.split("?o=")[-1]
       last_page = response.xpath('/html/body/div[@id="page_align"]/div[@id="page_width"]/div[@id="ContainerMain"]/nav/ul[@id="paging"]//li/a/@href').extract()[-1].split("?o=")[-1]
       if nb_page == last_page:
           exit 

       yield scrapy.Request(next_url ,callback=self.parse)        

    def parse_page(self, response):
       lbc_page = LeboncoinItem()

       category = response.url.split("/")[3]
       doc_id = response.url.split("/")[-1].split(".htm")[0]
       print category, doc_id
       
       content = response.xpath('/html/body/div/div[2]/div/div[3]')
       #content = response.xpath('/html/body/div[@class="page_align"]/div[@class="page_width"]/div[@id="ContainerMain"]/div[@class="content-border"]')
     
       #tire  
       #titre = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="header_adview"]/h1/text()').extract()
       titre = content.xpath('div/div[1]/div[1]/h1/text()').extract()
       print "titre", titre[0]


       tmp = content.xpath('div/span[@class="fine_print"]/a[@class="nohistory"]/text()').extract()
       try:
           region = tmp[1]
           print "region", region

           category = tmp[2]
           print "category", category
       except IndexError:
           pass


       content2 = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]')

       imgs = content2.xpath('div/div[@class="lbcImages"]')
       #imgs = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]')
       img_urls = imgs.xpath('meta/@content').extract()

       upload = content2.xpath('div[@class="upload_by"]')
       #upload = content.xpath('div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]')
       user_url = upload.xpath('a/@href').extract()[0] 
       user_id = user_url.split("id=")[1]
       user_name = upload.xpath('a/text()').extract()[0] 
       upload_date = "".join(upload.xpath('text()').extract()).strip().replace("- Mise en ligne le ","").replace(u"à ","").replace(".","")
       print "user_url", user_url
       print "user_id", user_id
       print "user_name", user_name
       print "upload_date", upload_date

       tmp =  content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td')
       try:
           price_currency = tmp.xpath('meta/@content').extract()[0]
           price = tmp.xpath('span[@class="price"]/@content').extract()[0]
           print "price_currency", price_currency
           print "price", price
       except IndexError:
           pass


       place =  content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]')
       try:
           addr_locality = place.xpath('tr/td[@itemprop="addressLocality"]/text()').extract()[0]
           postal_code = place.xpath('tr/td[@itemprop="postalCode"]/text()').extract()[0]
           print "addr_locality", addr_locality
           print "postal_code", postal_code
       except IndexError:
           pass

       
       geo_coords = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]')
       latitude = geo_coords.xpath('//meta[@itemprop="latitude"]/@content').extract()
       longitude = geo_coords.xpath('//meta[@itemprop="longitude"]/@content').extract()
       print "latitude", latitude
       print "longitude", longitude

       criterias = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table//tr')
       #FIXME FOR IMMO a/text
       for row in criterias:
           header = u"".join( map(lambda x: x.strip().replace(" :","") ,row.xpath('th/text()').extract()))
           value =  u"".join( map(lambda x: x.strip(), row.xpath('td/text()').extract()))
           if not value:
               value = u"".join(row.xpath('td//a/text()').extract())
           print header, value


       description  = content2.xpath('div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()').extract()
       desc = u" ".join( map(lambda x: x.strip().replace("\n","").replace("  ","") ,description))
       print desc
