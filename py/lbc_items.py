

import logging
import json

Document_Identifier = namedtuple( "Document_Identifier", ["doc_url", "doc_id", "doc_category" ])
Document_Category = namedtuple( "Document_Category", [" doc_category ", "title ", "region ", "img_urls ", "desc" ])
Document_Uploader = namedtuple( "Document_Uploader", ["uploader_name", "uploader_url", "uploader_id", "uploader_ispro, uploader_pro_siren"])
Document_Price = namedtuple( "Document_Price", [" price_currency ", "price ", "urgent " ])
Document_Localisation = namedtuple( "Document_Localisation", [" addr_locality", "postal_code", "location " ])
Document_Criterias = namedtuple( "Document_Criterias", [" criterias_dict " ])

def document_identifier_factory(doc_url):
    logger = logging.getLogger(__name__)

    url_slash_split = doc_url.split("/")
    doc_category = url_slash_split.split("/")[3]
    logger.debug( "doc_category ", doc_category  )
    doc_id = int( url_slash_split[-1].split(".htm")[0] )
    logger.debug( "doc_id ", doc_id  )

    logger.debug( "doc_url", doc_url )
    return Document_Identifier(doc_url, doc_id, doc_category)

def  document_category_factory(tree):
    logger = logging.getLogger(__name__)
    doc_category = ""
    title = ""
    region = ""
    img_urls = ""
    desc = ""
    try:
        title = tree.xpath('/html/body/div/div[2]/div/div[3]/div/div[1]/div[1]/h1/text()')[0]
    except IndexError:
        logger.error( "IndexError", exc_info=True )

    header_path = tree.xpath('/html/body/div/div[2]/div/div[3]/div/span[@class="fine_print"]/a[@class="nohistory"]/text()')
    try:
        region = header_path[1]
        doc_category = header_path[2]
        logger.debug( "region", region  )
        logger.debug( "doc_category", doc_category )
    except IndexError:
        logger.debug( "header_path", header_path  )
        logger.error( "IndexError", exc_info=True )

    img_urls = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div/div[@class="lbcImages"]/meta/@content')
    logger.debug( "image urls", img_urls )

    description  = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="AdviewContent"]/div[@class="content"]/text()')
    desc  = u" ".join( map(lambda x: x.strip().replace("\n","").replace("  ","") ,description))

    return Document_Category( doc_category , title , region , img_urls, desc)


def document_uploader_factory(tree):
    logger = logging.getLogger(__name__)
    uploader_url = ""
    uploader_id = ""
    uploader_name = ""
    upload_date = ""
    #uploader_ispro = 0  #FIXME
    #uploader_pro_siren= #FIXME

    uploader_url = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/@href')[0]
    logger.debug( "user url", uploader_url )
    uploader_id = int( user_url.split("id=")[1] )
    logger.debug( "uploader_id", uploader_id )
    uploader_name = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/a/text()')[0]
    logger.debug( "uploader_name", uploader_name )

    upload_date = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="upload_by"]/text()')
    upload_date = "".join( upload_date ).strip()
    upload_date = upload_date.replace("- Mise en ligne le ","")
    upload_date = upload_date.replace(u"à ","")
    upload_date = upload_date.replace(".","")
    logger.debug( "uploader_name", upload_date )
    return Document_Uploader( uploader_name, uploader_url, uploader_id, uploader_ispro, uploader_pro_siren)

def document_price_factory(tree):
    logger = logging.getLogger(__name__)
    price_currency = ""
    price = ""

    try:
       price_currency = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/meta/@content')
       price = int(tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="price"]/@content').[0])
       urgent = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[1]/tbody/tr[@class="price"]/td/span[@class="urgent"]/text()')
       if urgent:
           urgent = 1
       else:
           urgent = 0

    except IndexError as e:
       logger.debug( "IndexError {}".format{ e }  )
       return Document_Price( price_currency , price , urgent )

def document_localisation_factory(tree):
    logger = logging.getLogger(__name__)
    addr_locality = ""
    postal_code = ""
    try:
       addr_locality = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="addressLocality"]/text()')[0]
       postal_code = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/tr/td[@itemprop="postalCode"]/text()').[0]
       postal_code =  int(postal_code)
   except IndexError as e:
       logger.debug( "IndexError {}".format{ e }  )

    try:
        latitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="latitude"]/@content')[0]
        longitude = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]/tbody[@itemtype="http://schema.org/PostalAddress"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams withborder"]/div[@class="floatLeft"]/table[@itemtype="http://schema.org/Place"]//meta[@itemprop="longitude"]/@content')[0]
        location = [longitude, latitude]
        location = map( float, location)
    except IndexError as e:
       logger.debug( "IndexError {}".format{ e }  )

   return Document_Localisation( addr_locality, postal_code ,location )

def document_criterias_factory(tree):
    logger = logging.getLogger(__name__)
    criterias_dict = dict()
    """ #FIXME
    criterias = tree.xpath('/html/body/div/div[2]/div/div[3]/div[@class="content-color"]/div[@class="lbcContainer"]/div[@class="colRight"]/div[@class="lbcParamsContainer floatLeft"]/div[@class="lbcParams criterias"]/table//tr')
           for row in criterias:
               header = u"".join( map(lambda x: x.strip().replace(" :","") ,row.xpath('th/text()').extract()))
               value =  u"".join( map(lambda x: x.strip(), row.xpath('td/text()').extract()))
               if not value:
                   value = u"".join(row.xpath('td//a/text()').extract())
               criterias_dict[header] = value
    """
    return Document_Criterias( criterias_dict )



class LeboncoinItem():

    def __init__(self, url, tree):

        self._document_Identifier = document_identifier_factory( url )
        self._document_Category = document_category_factory( url )
        self._document_Uploader = document_uploader_factory(tree)
        self._document_Localisation = document_localisation_factory(tree)

        self._document_Category_Criterias = document_Category_Criterias_factory(tree)
        self._document_Announcement = document_Announcement_factory(tree)

        def json_it(self):
            return None



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
