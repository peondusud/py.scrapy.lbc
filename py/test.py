import os
import sys
import logging
from colorama import Fore, Back, Style
import datetime

import requests
from urllib.parse import urlparse
from lxml import html     #apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
import json
import re

url = 'http://www.leboncoin.fr/ventes_immobilieres/702810503.htm'

response = requests.get( url )
page = response.text
tree = html.fromstring( page )

t = tree.xpath('/html/body/script[1]/text()')[0]
t = str(t.strip() )
print( (t) )


pattern = '\s\s(\w+)\s:\s"(.+)",?'
prog = re.compile(pattern)
dic = {}
for line in t.splitlines():
    result = prog.search(line )
    if result is not None:
        #print( result.groups() )
        dic[result.group(1)] = result.group(2)

print(dic)
