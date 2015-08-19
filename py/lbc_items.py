

import logging
import json
import re
from collections import namedtuple

Document_Identifier = namedtuple( "Document_Identifier", [ "doc_url", "doc_id", "doc_category" ])
Document_Category = namedtuple( "Document_Category", [ "doc_category", "title", "region", "img_urls", "desc" ])
Document_Uploader = namedtuple( "Document_Uploader", [ "uploader_name", "uploader_url", "uploader_id", "uploader_ispro", "uploader_pro_siren"])
Document_Price = namedtuple( "Document_Price", [ "price_currency", "price", "urgent" ])
Document_Localisation = namedtuple( "Document_Localisation", ["addr_locality", "postal_code", "location" ])
Document_Criterias = namedtuple( "Document_Criterias", [ "criterias_dict" ])

def document_identifier_factory( doc_url ):
    logger = logging.getLogger(__name__)
    logger.debug( "document_identifier_factory doc_url {}".format(doc_url) )
    url_slash_split = doc_url.split("/")
    doc_category = url_slash_split[3]
    logger.debug( "document_identifier_factory doc_category {}".format(doc_category) )

    logger.debug( "doc_category {}".format( doc_category ) )
    doc_id = int( url_slash_split[-1].split(".htm")[0] )
    logger.debug( "document_identifier_factory doc_id  {}".format( doc_id ) )

    logger.debug( "document_identifier_factory doc_url  {}".format( doc_url) )
    return Document_Identifier(doc_url, doc_id, doc_category)

def  document_category_factory( tree ):
    logger = logging.getLogger(__name__)
    doc_category = ""
    title = ""
    region = ""
    img_urls = ""
    desc = ""
    try:
        title = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')[0]
    except IndexError:
        logger.error( "document_category_factory IndexError", exc_info=True )
        logger.debug( "document_category_factory title  {}".format( title ) )
    header_path = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
    try:
        region = header_path[1]
        doc_category = header_path[2]
    except IndexError:
        logger.debug( "document_category_factory header_path {}".format( header_path)  )
        logger.error( "document_category_factory IndexError", exc_info=True)
    logger.debug( "document_category_factory region  {}".format( region ) )
    logger.debug( "document_category_factory doc_category  {}".format( doc_category ) )

    img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
    logger.debug( "document_category_factory img_urls  {}".format( img_urls ) )

    description  = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()')
    desc  = u" ".join( map(lambda x: x.strip().replace("\n","").replace("  ","") ,description))
    logger.debug( "document_category_factory desc  {}".format( desc ) )
    return Document_Category( doc_category , title , region , img_urls, desc)


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

    try:
        price_currency = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/meta/@content')[0]
        price = int(tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="price"]/@content')[0] )
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
    addr_locality = ""
    postal_code = ""

    latitude = ""
    longitude = ""
    location= []
    try:
        addr_locality = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="addressLocality"]/text()')
        logger.debug( "document_localisation_factor addr_locality  {}".format( addr_locality ))
        addr_locality = addr_locality[0]
    except IndexError as e:
       logger.error( "document_localisation_factory addr_locality IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor addr_locality  {}".format( addr_locality ))

    try:
        postal_code = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="postalCode"]/text()')
        postal_code = postal_code[0]
        postal_code =  int(postal_code)
    except IndexError as e:
       logger.error( "document_localisation_factory addr_locality IndexError" , exc_info=True  )
       logger.debug( "document_localisation_factor postal_code  {}".format( postal_code ))

    try:
        latitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0]
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor latitude  {}".format( latitude ))

    try:
        longitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0]
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))
    except IndexError as e:
        logger.error( "document_localisation_factory latitude IndexError", exc_info=True  )
        logger.debug( "document_localisation_factor longitude  {}".format( longitude ))


    location = [ longitude, latitude]
    location = list(map( float, location))
    logger.debug( "document_localisation_factor location  {}".format( location ))
    return Document_Localisation( addr_locality, postal_code ,location )

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



class LeboncoinItem():

    def __init__(self, url, tree):
        self._logger = logging.getLogger(__name__)
        document_Identifier = document_identifier_factory( url )
        document_Category = document_category_factory( tree )
        document_Uploader = document_uploader_factory( tree )
        document_Localisation = document_localisation_factory( tree )
        document_Price = document_price_factory( tree )

        document_Criterias = document_criterias_factory( tree )

        #FIXME 'key' is not defined DocPage loop

        #return OrdereDict  _document_Identifier._asdict()
        #return OrdereDict  _document_Identifier.__dict__
        self._dict =  dict( document_Identifier.__dict__ )
        self._dict.update( dict( document_Category.__dict__) )
        self._dict.update( dict( document_Uploader.__dict__) )
        self._dict.update( dict( document_Localisation.__dict__) )
        self._dict.update( dict( document_Price.__dict__) )

        #return only the value (containing a dict)
        self._dict.update( dict( document_Criterias.__dict__["criterias_dict"]) )

        #remove empty key
        for remove_key in [k for k,v in self._dict.items() if v is '']:
            self._logger.debug("Remove key empty {}".format(remove_key) )
            self._dict.pop(key)

        #print ( self._dict)

    def json_it(self):
        return json.dumps( self._dict )



#################################################################################################################

"""
Document_Category = namedtuple("Document_Category", ["doc_category", "pro_flag", "announcement_type"])
Document_Localisation = namedtuple("Document_Localisation", ["region", "department", "zip_code", "town", "location"])
Document_Uploader = namedtuple("Document_Uploader", ["uploader_name", "uploader_url", "uploader_id", "uploader_pro_siren"])
Document_Category_Criterias = namedtuple("Document_Criterias", ["criterias_dict" ]) #FIXME give dict() <====
Document_Announcement = namedtuple("Document_Announcement", ["title", "description", "price", "price_currency", "img_urls", "upload_date", "urgent", "doc_url", "doc_id" ])


def  document_Category_factory(tree):
    doc_category = ""
    pro_flag = ""
    announcement_type = ""
    return Document_Category( doc_category, pro_flag, announcement_type)

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

def  document_Category_Criterias_factory(tree):
    pass
    criterias_dict = {}
    return Document_Criterias( criterias_dict )

def  document_Category_Criterias_factory(tree):
    pass
    title= ""
    description= ""
    price= ""
    price_currency= ""
    img_urls= ""
    upload_date= ""
    urgent= ""
    doc_url= ""
    doc_id
    return Document_Announcement( title, description, price, price_currency, img_urls, upload_date, urgent, doc_url, doc_id )

class LeboncoinItem2():

    def __init__(self, url, tree):

        self._document_Category = document_Category_factory(tree)
        self._document_Localisation = document_Localisation_factory(tree)
        self._document_Uploader = document_Uploader_factory(tree)
        self._document_Category_Criterias = document_Category_Criterias_factory(tree)
        self._document_Announcement = document_Announcement_factory(tree)

        def json_it(self):
            return None
"""
