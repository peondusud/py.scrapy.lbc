#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TODO
    Finish class
    on factory modify the input dict

"""


import logging
import json
import time
import re
from collections import namedtuple
from lxml import etree, html
from binascii import hexlify
from io import StringIO, BytesIO
from urlparse import urlparse, parse_qs
from datetime import date, datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = u" ".join((DATE_FORMAT, TIME_FORMAT))

Document_Identifier = namedtuple( "Document_Identifier", [ "doc_url", "ad" ])
Document_Main = namedtuple( "Document_Main", ["titre", "desc" ])
Document_IMG = namedtuple( "Document_IMG", ["img_urls", "thumb_urls" ])
Document_Time = namedtuple( "Document_Time", ["upload_date", "check_date"])
Document_Uploader = namedtuple( "Document_Uploader", [ "uploader_name", "uploader_url", "uploader_id" ])
Document_Urgent = namedtuple( "Document_Urgent", ["urgent"])
Document_Location = namedtuple( "Document_Localisation", ["addr_locality", "location" ])
Document_Criterias_From_JS = namedtuple( "Document_Criterias_From_JS", [ "criterias_js_dict" ])

js_var_regex = re.compile('\s\s(\w+)\s:\s"(.+)",?')
criteria_pattern = re.compile(ur'^\s{2}(?P<key>\w+) : "(?P<val>\w+)",?', re.MULTILINE)
thumb_pattern = re.compile(ur'^background-image: url\(\'(?P<url>[\w/:\.]+)\'\);$')
date_pattern = re.compile(ur'Mise en ligne le (?P<day>\d\d?) (?P<month>[a-zéû]+) . (?P<hour>\d\d?):(?P<minute>\d\d?)')
doc_id_pattern = re.compile(ur"^http://www.leboncoin.fr/.{0,100}(?P<id>\d{9})\.htm.{0,50}$")
uploader_id_pattern = re.compile(ur"^http.{0,50}(?P<id>\d{9,12})$")

def get_ad_id(url):
    """
        get ad_id from ad_url
    """
    print(url)
    parse_result = urlparse(url)
    tmp = parse_result.path
    tmp = tmp.split("/")[-1]
    id = tmp.split(".htm")[0]
    return int(id)

def proper_ad_url(url):
    """
        remove = "?ca=12_s" frm url
    """
    #return url.split('?')[0]
    return url[:-8]

def proper_description(desc):
    str = u"\n".join(desc)
    str = str.strip()
    #str = str.replace("\n","")
    #str = str.replace("  ","")
    return str

def get_ad_id_regex(url):
    #pattern = r"(\d{9})"
    m = re.search(self.doc_id_pattern, url)
    id = m.group('id')
    return int(id)

def get_uploader_id(url):
    parse_result = urlparse(url)
    tmp = parse_result.query
    tmp = tmp.split("id=")[-1]
    return int(tmp)

def get_uploader_id_regex(url):
    m = re.search(uploader_id_pattern, url)
    id = m.group('id')
    return int(id)

def get_check_date():
    d = datetime.now()
    date_str = d.strftime(DATETIME_FORMAT)
    return date_str

def get_uploaded_date(str):
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

        date_str = d.strftime(DATETIME_FORMAT)
        return date_str
    return ""


def proper_thumb_urls(thumb_urls):
    proper_thumb_urls = list()
    for elem in thumb_urls:
        m = re.search(thumb_pattern, elem)
        if m is not None:
            proper_thumb_urls.append(m.group('url'))
    return proper_thumb_urls

def proper_urgent(urgent_str):
    urgent_flag
    if urgent_str:
       urgent_flag = 1
    else:
       urgent_flag = 0
    return urgent_flag


def jsVar_2_pyDic(self, criterias):
    return dict(re.findall(self.criteria_pattern,criterias))


def document_identifier_factory( doc_url ):
    logger = logging.getLogger(__name__)
    logger.debug( u"document_identifier_factory orig doc_url {}".format(doc_url) )

    ad_id = get_ad_id(doc_url)
    logger.debug( u"document_identifier_factory ad_id {}".format(ad_id) )

    proper_ad_url = proper_ad_url(doc_url)
    logger.debug( u"document_identifier_factory proper_ad_url {}".format(proper_ad_url) )
    return Document_Identifier(proper_ad_url, ad_id)


def document_main_factory( **kwargs ):
    logger = logging.getLogger(__name__)

    titre = 0 #TODO
    description = 0 #proper_description() #TODO

    logger.debug( u"document_main_factory desc  {}".format( desc ) )
    return Document_Main( titre, desc)


def document_img_factory( **kwargs ):
    logger = logging.getLogger(__name__)
    img_urls = 0 #TODO
    thumb_urls = 0 #proper_thumb_urls(thumb_urls)#TODO
    return Document_IMG(img_urls, thumb_urls)


def document_time_factory( **kwargs ):
    logger = logging.getLogger(__name__)
    upload_date = 0 #get_upladed_date() #TODO
    check_date = get_upladed_date()
    return Document_Time(upload_date, check_date)



def document_uploader_factory( **kwargs ):
    logger = logging.getLogger(__name__)
    uploader_name = ""
    uploader_url = ""
    uploader_id = ""

    uploader_url = 0
    logger.debug( u"document_uploader_factory uploader_url {}".format( uploader_url ) )

    uploader_id = 0 #get_uploader_id() #TODO
    logger.debug( u"document_uploader_factory uploader_id {}".format( uploader_id ) )

    uploader_name = 0 #TODO
    logger.debug( u"document_uploader_factory uploader_name {}".format( uploader_name ) )
    return Document_Uploader( uploader_name, uploader_url, uploader_id)

def document_urgent_factory(**kwargs):
    logger = logging.getLogger(__name__)

    urgent = 0 #proper_urgent()
    logger.debug( "document_price_factory urgent  {}".format( urgent ) )
    return Document_Urgent(urgent)

def document_location_factory(**kwargs):
    logger = logging.getLogger(__name__)
    addr_locality  = ""

    latitude = ""
    logger.debug( "document_localisation_factor latitude  {}".format( latitude ))
    longitude = ""
    logger.debug( "document_localisation_factor longitude  {}".format( longitude ))


    location = [ longitude, latitude]
    #location = [ float(longitude), float(latitude)]
    logger.debug( "document_localisation_factor location  {}".format( location ))
    return Document_Localisation( addr_locality, location )


def document_criterias_from_js( tree ):
    logger = logging.getLogger(__name__)
    criterias_js_dict = {}

    logger.debug("document_criterias_factory_from_js criterias_js_dict {}".format( criterias_js_dict) )
    return criterias_js_dict


class LeboncoinItem_noScrap():
    def __init__(self):
        self._logger = logging.getLogger(__name__)


    def proper(self, dic):
        document_Identifier = document_identifier_proper( url )
        document_Main = document_main_proper( tree )
        document_IMG = document_img_proper( tree )
        document_Time = document_time_proper( tree )
        document_Uploader = document_uploader_proper( tree )
        document_Location = document_localisation_proper( tree )
        document_Urgent = document_urgent_proper( tree )
        document_Criterias_from_js = document_criterias_from_js( tree )


        self.remove_empty_keys(dic)
        return dic


    @staticmethod
    def remove_empty_keys(dic):
        for key, val in dic.items():
            if val is '':
                try:
                    dic.pop(key)
                except KeyError:
                    pass
