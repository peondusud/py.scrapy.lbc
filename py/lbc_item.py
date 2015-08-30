#!/usr/bin/env python3

# -- coding: utf-8 --



import logging
import json
import re
from collections import namedtuple

Document_Identifier = namedtuple( "Document_Identifier", [ "doc_url", "ad", "subcat" ])
Document_subcategory = namedtuple( "Document_subcategory", [ "subcat", "titre", "region", "img_urls", "desc" ])
Document_Uploader = namedtuple( "Document_Uploader", [ "uploader_name", "uploader_url", "uploader_id", "uploader_ispro", "uploader_pro_siren"])
Document_Price = namedtuple( "Document_Price", [ "price_currency", "price", "urgent" ])
Document_Localisation = namedtuple( "Document_Localisation", ["city", "cp", "location" ])
Document_Criterias = namedtuple( "Document_Criterias", [ "criterias_dict" ])
Document_Criterias_From_JS = namedtuple( "Document_Criterias_From_JS", [ "criterias_js_dict" ])

def document_identifier_factory( doc_url ):
    logger = logging.getLogger(__name__)
    logger.debug( "document_identifier_factory doc_url {}".format(doc_url) )
    url_slash_split = doc_url.split("/")
    subcat = url_slash_split[3]
    logger.debug( "document_identifier_factory subcat {}".format(subcat) )

    logger.debug( "subcat {}".format( subcat ) )
    ad = int( url_slash_split[-1].split(".htm")[0] )
    logger.debug( "document_identifier_factory ad  {}".format( ad ) )

    logger.debug( "document_identifier_factory doc_url  {}".format( doc_url) )
    return Document_Identifier(doc_url, ad, subcat)

def  document_subcategory_factory( tree ):
    logger = logging.getLogger(__name__)
    subcat = ""
    titre = ""
    region = ""
    img_urls = ""
    desc = ""
    try:
        titre = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')
        if  titre != []:
            titre = titre[0]
        else:
            titre = ""
    except IndexError:
        logger.error( "document_subcategory_factory IndexError", exc_info=True )
        logger.debug( "document_subcategory_factory titre  {}".format( titre ) )
    header_path = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
    try:
        if  header_path != []:
            region = header_path[1]
            subcat = header_path[2]
    except IndexError:
        logger.debug( "document_subcategory_factory header_path {}".format( header_path)  )
        logger.error( "document_subcategory_factory IndexError", exc_info=True)
    logger.debug( "document_subcategory_factory region  {}".format( region ) )
    logger.debug( "document_subcategory_factory subcat  {}".format( subcat ) )

    img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
    logger.debug( "document_subcategory_factory img_urls  {}".format( img_urls ) )

    description  = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()')
    def sanitize_description(description):
        sanitize_desc = description.strip()
        sanitize_desc.replace("\n","")
        sanitize_desc.replace("  ","")
        #logger.debug(">>>>>>>>>>>>>>>><"+ sanitize_desc)
        return sanitize_desc

    desc  = u" ".join( map( sanitize_description  ,description))
    logger.debug( "document_subcategory_factory desc  {}".format( desc ) )
    return Document_subcategory( subcat , titre , region , img_urls, desc)


def document_uploader_factory( tree ):
    logger = logging.getLogger(__name__)
    uploader_url = ""
    uploader_id = ""
    uploader_name = ""
    upload_date = ""
    uploader_ispro = 0
    uploader_pro_siren = ""

    uploader_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
    logger.debug( "document_uploader_factory uploader_url {}".format( uploader_url ) )

    uploader_id = int( uploader_url.split("id=")[1] )
    logger.debug( "document_uploader_factory uploader_id {}".format( uploader_id ) )

    uploader_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
    logger.debug( "document_uploader_factory uploader_name {}".format( uploader_name ) )

    upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
    upload_date = "".join( upload_date ).strip()

    matchObj = re.match( "Numéro Siren : (\d{9})\s+?-", upload_date )
    if matchObj is not None:
        uploader_pro_siren = matchObj.group(1)
        uploader_ispro = 1
    upload_date = upload_date.replace("- Mise en ligne le ","")
    upload_date = upload_date.replace(u"à ","")
    upload_date = upload_date.replace(".","")
    logger.debug( "document_uploader_factory upload_date {}".format( upload_date ) )
    return Document_Uploader( uploader_name, uploader_url, uploader_id, uploader_ispro, uploader_pro_siren)

def document_price_factory(tree):
    logger = logging.getLogger(__name__)
    price_currency = ""
    price = ""
    urgent = ""
    try:
        price_currency = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/meta/@content')
        if  price_currency != []:
            price_currency = price_currency[0]
        else:
            price_currency = ""

        prix = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="price"]/@content')
        if  prix != []:
            prix = prix[0]
            prix = int(prix )
        else:
            prix = ""
        urgent = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()')
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
        city_l = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="addressLocality"]/text()')
        logger.debug( "document_localisation_factor city  {}".format( city_l ))
        if  city_l != []:
            city = city_l[0]
        else:
            city = ""
    except IndexError as e:
       logger.error( "document_localisation_factory city IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor city  {}".format( city_l ))

    try:
        cp = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="postalCode"]/text()')
        if  cp != []:
            cp = cp[0]
            cp =  int(cp)
        else:
            cp = ""
    except IndexError as e:
       logger.error( "document_localisation_factory city IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor cp  {}".format( cp ))

    try:
        latitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="latitude"]/@content')
        if  latitude != []:
            latitude = latitude[0]
        else:
            latitude = ""
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))

    try:
        longitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="longitude"]/@content')
        if  longitude != []:
            longitude = longitude[0]
        else:
            latitude = ""
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))


    location = [ longitude, latitude]
    location = list(map( float, location))
    logger.debug( "document_localisation_factor location  {}".format( location ))
    return Document_Localisation( city, cp ,location )

def document_criterias_factory( tree ):
    logger = logging.getLogger(__name__)
    criterias_dict = dict()

    # /html/body/div/div[2]/div/div[3]
    # div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]
    # div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table//tr
    criterias = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table/tr')
    #criterias = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table/tr')

    for tr in criterias:
        header = tr.xpath('th/text()')
        try:
            header = header[0]
            header = header.split(" : ")[0]
            header = header.split(" :")[0]
            header = header.lower()
        except IndexError as e:
            logger.debug( "document_criterias_factory header IndexError" )

        value = tr.xpath('td/text()')
        try:
            value = value[0]
            value = value.strip()
        except IndexError as e:
            logger.debug( "document_criterias_factory value IndexError" )

        if not value:
            value = tr.xpath('td/noscript/a/text()')
            logger.debug( "document_criterias_factory value links : ---{}----".format(value) )
            try:
                value = value[0]
            except IndexError as e:
                logger.debug( "document_criterias_factory value links IndexError" )

        criterias_dict[header] = value
        #criterias_dict.update({ header : value })
        logger.debug( "document_criterias_factory {} : _{}_".format( header , value ))

    logger.debug( "document_criterias_factory criterias_dict  {}".format( criterias_dict ))
    return Document_Criterias( criterias_dict )

def document_criterias_factory_from_js( tree ):
    logger = logging.getLogger(__name__)
    js_var = tree.xpath('/html/body/script[1]/text()')
    js_var = js_var[0]
    js_var = str( js_var.strip() )
    logger.debug("document_criterias_factory_from_js js_var  {}".format(js_var) )

    pattern = '\s\s(\w+)\s:\s"(.+)",?'
    prog = re.compile(pattern)
    criterias_js_dict = {}
    for line in js_var.splitlines():
        result = prog.search(line )
        if result is not None:
            #print( result.groups() )
            key = result.group(1)
            val = result.group(2)
            logger.debug("document_criterias_factory_from_js key {}".format(key) )
            logger.debug("document_criterias_factory_from_js val {}".format(val) )
            criterias_js_dict[key] = val
    logger.debug("document_criterias_factory_from_js criterias_js_dict {}".format( criterias_js_dict) )
    return Document_Criterias_From_JS( criterias_js_dict )



class LeboncoinItem():

    def __init__(self, url, tree):
        self._logger = logging.getLogger(__name__)
        document_Identifier = document_identifier_factory( url )
        document_subcategory = document_subcategory_factory( tree )
        document_Uploader = document_uploader_factory( tree )
        document_Localisation = document_localisation_factory( tree )
        document_Price = document_price_factory( tree )
        document_Criterias = document_criterias_factory( tree )
        document_Criterias_from_js = document_criterias_factory_from_js( tree )

        #return OrdereDict  _document_Identifier._asdict()
        #return OrdereDict  _document_Identifier.__dict__
        self._dict =  dict( document_Identifier.__dict__ )
        self._dict.update( dict( document_subcategory.__dict__) )
        self._dict.update( dict( document_Uploader.__dict__) )
        self._dict.update( dict( document_Localisation.__dict__) )
        self._dict.update( dict( document_Price.__dict__) )

        #return only the values (containing a dict)
        self._dict.update( dict( document_Criterias.__dict__["criterias_dict"]) )
        self._dict.update( dict( document_Criterias_from_js.__dict__["criterias_js_dict"]) )

        #remove empty key
        keys2remove = [k for k,v in self._dict.items() if v is '']
        self._logger.debug( "LeboncoinItem  keys2remove : {}".format( keys2remove ))
        self._logger.debug( "LeboncoinItem  dict : {}".format( self._dict ))
        for remove_key in keys2remove:
            self._logger.debug("Remove empty key  {}".format(remove_key) )
            try:
                self._dict.pop(remove_key)
            except KeyError:
                self._logger.debug("Remove empty key  {}".format(remove_key) )
        self._logger.debug( "LeboncoinItem  dict : {}".format( self._dict ))

    def json_it(self):
        return json.dumps( self._dict )

#################################################################################################################

"""
Document_subcategory = namedtuple("Document_subcategory", ["subcat", "pro_flag", "announcement_type"])
Document_Localisation = namedtuple("Document_Localisation", ["region", "department", "zip_code", "town", "location"])
Document_Uploader = namedtuple("Document_Uploader", ["uploader_name", "uploader_url", "uploader_id", "uploader_pro_siren"])
Document_subcategory_Criterias = namedtuple("Document_Criterias", ["criterias_dict" ]) #FIXME give dict() <====
Document_Announcement = namedtuple("Document_Announcement", ["titre", "description", "price", "price_currency", "img_urls", "upload_date", "urgent", "doc_url", "ad" ])


def  document_subcategory_factory(tree):
    subcat = ""
    pro_flag = ""
    announcement_type = ""
    return Document_subcategory( subcat, pro_flag, announcement_type)

def  document_Localisation_factory(tree):
    region = ""
    department = ""
    zip_code = ""
    return Document_Localisation( region, department, zip_code, town,location)


def  document_Uploader_factory(tree):
    uploader_name = ""
    uploader_url = ""
    announcement_type = ""
    return Document_Uploader( uploader_name, uploader_url, uploader_id, uploader_pro_siren )

def  document_subcategory_Criterias_factory(tree):
    pass
    criterias_dict = {}
    return Document_Criterias( criterias_dict )

def  document_subcategory_Criterias_factory(tree):
    pass
    titre= ""
    description= ""
    price= ""
    price_currency= ""
    img_urls= ""
    upload_date= ""
    urgent= ""
    doc_url= ""
    ad
    return Document_Announcement( titre, description, price, price_currency, img_urls, upload_date, urgent, doc_url, ad )

class LeboncoinItem2():

    def __init__(self, url, tree):

        self._document_subcategory = document_subcategory_factory(tree)
        self._document_Localisation = document_Localisation_factory(tree)
        self._document_Uploader = document_Uploader_factory(tree)
        self._document_subcategory_Criterias = document_subcategory_Criterias_factory(tree)
        self._document_Announcement = document_Announcement_factory(tree)

        def json_it(self):
            return None
"""
