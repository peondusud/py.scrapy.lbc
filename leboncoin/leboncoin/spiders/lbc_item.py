#!/usr/bin/env python

# -- coding: utf-8 --



import logging
import json
import re
from collections import namedtuple
from lxml import etree, html
from binascii import hexlify
from io import StringIO, BytesIO


Document_Identifier = namedtuple( "Document_Identifier", [ "doc_url", "ad", "subcat" ])
Document_Subcategory = namedtuple( "Document_subcategory", [ "subcat", "titre", "region", "img_urls", "desc" ])
Document_Uploader = namedtuple( "Document_Uploader", [ "uploader_name", "uploader_url", "uploader_id", "uploader_ispro", "uploader_pro_siren", "upload_date"])
Document_Price = namedtuple( "Document_Price", [ "price_currency", "price", "urgent" ])
Document_Localisation = namedtuple( "Document_Localisation", ["city", "cp", "location" ])
Document_Criterias = namedtuple( "Document_Criterias", [ "criterias_dict" ])
Document_Criterias_From_JS = namedtuple( "Document_Criterias_From_JS", [ "criterias_js_dict" ])

titre_x =         etree.XPath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')
header_path_x =   etree.XPath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
img_urls_x =      etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
description_x  =  etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()')
uploader_url_x =  etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')
uploader_name_x = etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')
upload_date_x =   etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
price_currency_x = etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/meta/@content')
prix_x =          etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="price"]/@content')
urgent_x =        etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()')
city_l_x =        etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="addressLocality"]/text()')
cp_x =            etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="postalCode"]/text()')
latitude_x =      etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="latitude"]/@content')
longitude_x =     etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="longitude"]/@content')
criterias_x =     etree.XPath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table/tr')
table_header_x =  etree.XPath('th/text()')
table_data_x =    etree.XPath('td/text()')

noscript_x = etree.XPath('td/noscript/a/text()')
js_var_x =  etree.XPath('/html/body/script[1]/text()')
js_var_regex = re.compile('\s\s(\w+)\s:\s"(.+)",?')

def document_identifier_factory( doc_url ):
    logger = logging.getLogger(__name__)
    logger.debug( u"document_identifier_factory doc_url {}".format(doc_url) )
    url_slash_split = doc_url.split("/")
    subcat = url_slash_split[3]
    logger.debug( u"document_identifier_factory subcat {}".format(subcat) )

    logger.debug( u"subcat {}".format( subcat ) )
    ad = int( url_slash_split[-1].split(".htm")[0] )
    logger.debug( u"document_identifier_factory ad  {}".format( ad ) )

    logger.debug( u"document_identifier_factory doc_url  {}".format( doc_url) )
    return Document_Identifier(doc_url, ad, subcat)

def  document_subcategory_factory( tree ):
    logger = logging.getLogger(__name__)
    subcat = ""
    titre = ""
    region = ""
    img_urls = ""
    desc = ""
    try:
        #titre = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')
        titre = titre_x(tree)
        if  titre != []:
            titre = titre[0]
        else:
            titre = ""
    except IndexError:
        logger.error( u"document_subcategory_factory IndexError", exc_info=True )
        logger.debug( u"document_subcategory_factory titre  {}".format( titre ) )

    #header_path = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
    header_path = header_path_x(tree)
    try:
        if  header_path != []:
            region = header_path[1]
            subcat = header_path[2]
    except IndexError:
        logger.debug( u"document_subcategory_factory header_path {}".format( header_path)  )
        logger.error( u"document_subcategory_factory IndexError", exc_info=True)
    logger.debug( u"document_subcategory_factory region  {}".format( region ) )
    logger.debug( u"document_subcategory_factory subcat  {}".format( subcat.title())  )

    #img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
    img_urls = img_urls_x(tree)
    logger.debug( "document_subcategory_factory img_urls  {}".format( img_urls ) )

    #description  = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()')
    description = description_x(tree)

    def sanitize_description(description):
        sanitize_desc = description.strip()
        sanitize_desc.replace("\n","")
        sanitize_desc.replace("  ","")
        #logger.debug(">>>>>>>>>>>>>>>><"+ sanitize_desc)
        return sanitize_desc

    desc  = u" ".join( map( sanitize_description  ,description))
    logger.debug( u"document_subcategory_factory desc  {}".format( desc ) )
    return Document_Subcategory( subcat , titre , region , img_urls, desc)


def document_uploader_factory( tree ):
    logger = logging.getLogger(__name__)
    uploader_url = ""
    uploader_id = ""
    uploader_name = ""
    upload_date = ""
    uploader_ispro = 0
    uploader_pro_siren = ""

    #uploader_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
    uploader_url = uploader_url_x(tree)
    uploader_url =  uploader_url[0]
    logger.debug( u"document_uploader_factory uploader_url {}".format( uploader_url ) )

    uploader_id = int( uploader_url.split( u"id=")[1] )
    logger.debug( u"document_uploader_factory uploader_id {}".format( uploader_id ) )

    #uploader_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
    uploader_name = uploader_name_x(tree)
    uploader_name = uploader_name[0]
    logger.debug( u"document_uploader_factory uploader_name {}".format( uploader_name ) )

    #upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
    upload_date = upload_date_x(tree)
    upload_date = u"".join( upload_date ).strip()

    matchObj = re.match( u"Num\wro Siren : (\d{9})\s+?-", upload_date )
    if matchObj is not None:
        uploader_pro_siren = matchObj.group(1)
        uploader_ispro = 1
    upload_date = upload_date.replace(u"- Mise en ligne le ", u"")
    upload_date = upload_date.replace(u"\u00e0 ", u"")
    upload_date = upload_date.replace(u".", u"")
    #print(type(upload_date))
    logger.debug( u"document_uploader_factory upload_date {}".format( upload_date ) )
    return Document_Uploader( uploader_name, uploader_url, uploader_id, uploader_ispro, uploader_pro_siren, upload_date)

def document_price_factory(tree):
    logger = logging.getLogger(__name__)
    price_currency = ""
    price = ""
    urgent = ""
    try:
        #price_currency = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/meta/@content')
        price_currency = price_currency_x(tree)
        if  price_currency != []:
            price_currency = price_currency[0]
        else:
            price_currency = ""

        #prix = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="price"]/@content')
        prix = prix_x(tree)
        if  prix != []:
            prix = prix[0]
            prix = int(prix)
        else:
            prix = ""
        #urgent = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()')
        urgent = urgent_x(tree)
        if urgent:
           urgent = 1
        else:
           urgent = 0

        logger.debug( "document_price_factory urgent  {}".format( urgent ) )

    except IndexError as e:
       logger.error( "document_price_factory IndexError ", exc_info=True  )
       logger.debug( "document_price_factory price_currency  {}".format( price_currency ) )
       logger.debug( "document_price_factory price  {}".format( price ) )
    return Document_Price( price_currency , price , urgent )

def document_localisation_factory(tree):
    logger = logging.getLogger(__name__)
    city = ""
    cp = ""

    latitude = ""
    longitude = ""
    location= []
    try:
        #city_l = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="addressLocality"]/text()')
        city_l = city_l_x(tree)
        logger.debug( "document_localisation_factor city  {}".format( city_l ))
        if  city_l != []:
            city = city_l[0]
        else:
            city = ""
    except IndexError as e:
       logger.error( "document_localisation_factory city IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor city  {}".format( city_l ))

    try:
        #cp = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="postalCode"]/text()')
        cp = cp_x(tree)
        if  cp != []:
            cp = cp[0]
            cp =  int(cp)
        else:
            cp = ""
    except IndexError as e:
       logger.error( "document_localisation_factory city IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor cp  {}".format( cp ))

    try:
        #latitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="latitude"]/@content')
        latitude = latitude_x(tree)
        if  latitude != []:
            latitude = latitude[0]
        else:
            latitude = ""
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))

    try:
        #longitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="longitude"]/@content')
        longitude = longitude_x(tree)
        if  longitude != []:
            longitude = longitude[0]
        else:
            longitude = ""
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))

    
    location = [ longitude, latitude]
    #print(location)
    #location = [ float(longitude), float(latitude)]
    logger.debug( "document_localisation_factor location  {}".format( location ))
    return Document_Localisation( city, cp ,location )

def document_criterias( tree ):
    logger = logging.getLogger(__name__)
    criterias_dict = dict()

    # /html/body/div/div[2]/div/div[3]
    # div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]
    # div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table//tr
    criterias = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table/tr')
    #criterias = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table/tr')

    criterias = criterias_x(tree)
    for tr in criterias:
        #header = tr.xpath('th/text()')
        header = table_header_x(tr)
        try:
            header = header[0]
            header = header.split(" : ")[0]
            header = header.split(" :")[0]
            header = header.lower()
        except IndexError as e:
            logger.debug( "document_criterias_factory header IndexError" )

        #table_data = tr.xpath('td/text()')
        table_data = table_data_x(tr)
        try:
            table_data = table_data[0]
            table_data = table_data.strip()
        except IndexError as e:
            logger.debug( "document_criterias_factory value IndexError" )

        if not table_data:
            #table_data = tr.xpath('td/noscript/a/text()')
            table_data = noscript_x(tr)
            logger.debug( "document_criterias_factory value links : ---{}----".format(table_data) )
            try:
                table_data = table_data[0]
            except IndexError as e:
                logger.debug( "document_criterias_factory value links IndexError" )

        criterias_dict[header] = table_data
        #criterias_dict.update({ header : table_data })
        logger.debug( "document_criterias_factory {} : _{}_".format( header , table_data ))

    logger.debug( "document_criterias_factory criterias_dict  {}".format( criterias_dict ))
    return criterias_dict

def document_criterias_from_js( tree ):
    logger = logging.getLogger(__name__)
    #js_var = tree.xpath('/html/body/script[1]/text()')
    js_var = js_var_x(tree)
    js_var = js_var[0]
    js_var = str( js_var.strip() )
    logger.debug("document_criterias_factory_from_js js_var  {}".format(js_var) )


    criterias_js_dict = {}
    for line in js_var.splitlines():
        result = js_var_regex.search(line )
        if result is not None:
            key = result.group(1)
            val = result.group(2)
            logger.debug("document_criterias_factory_from_js key {}".format(key) )
            logger.debug("document_criterias_factory_from_js val {}".format(val) )
            criterias_js_dict[key] = val
    logger.debug("document_criterias_factory_from_js criterias_js_dict {}".format( criterias_js_dict) )
    return criterias_js_dict



class LeboncoinItem():

    def __init__(self):
        self._logger = logging.getLogger(__name__)
      
       
    def get(self, url, page_body): 
        #print(type(page_body))
        tree =  html.parse( BytesIO(page_body.encode('utf-8')))  
        document_Identifier = document_identifier_factory( url )
        document_Subcategory = document_subcategory_factory( tree )
        document_Uploader = document_uploader_factory( tree )
        document_Localisation = document_localisation_factory( tree )
        document_Price = document_price_factory( tree )
        document_Criterias = document_criterias( tree )
        document_Criterias_from_js = document_criterias_from_js( tree )

        dic =  dict()
        dic.update( document_Identifier.__dict__ )
        dic.update( document_Subcategory.__dict__ )
        dic.update( document_Uploader.__dict__ )
        dic.update( document_Localisation.__dict__ )
        dic.update( document_Price.__dict__ )
        dic.update( document_Criterias )
        dic.update( document_Criterias_from_js )
   
        self.remove_blank(dic)

        return dic


    @staticmethod
    def remove_blank(dic):
        for key, val in dic.items():
            if val is '':
                try:
                    dic.pop(key)
                except KeyError:
                    pass
