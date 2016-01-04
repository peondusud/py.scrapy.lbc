#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json import loads, dumps
from itertools import islice
from elasticsearch import Elasticsearch, helpers #pip3 install elasticsearch
from datetime import date, datetime
import logging


tmplt = """
{
  "template": "lbc-*",
  "settings": {
    "number_of_replicas": 0,
    "number_of_shards": 2,
    "refresh_interval": "30s"
  },
  "mappings": {
    "lbc": {
      "properties": {
        "user_name": {
          "type": "string",
          "index": "not_analyzed",
          "include_in_all": false
        },
        "title": {
          "type": "string",
          "index": "analyzed",
          "include_in_all": true
        },
        "thumbs_urls": {
          "type": "string",
          "index": "not_analyzed",
          "include_in_all": false
        },
        "desc": {
          "type": "string",
          "index": "analyzed",
          "include_in_all": true
        },
        "doc_url": {
          "type": "string",
          "index": "not_analyzed",
          "include_in_all": false
        },
        "location": {
          "type": "geo_point",
          "include_in_all": false
        },
        "urgent": {
          "type": "short",
          "include_in_all": false
        },
        "criterias": {
          "properties": {
            "region": {
              "type": "short",
              "include_in_all": false
            },
            "cat": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "subcat": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "prix": {
              "type": "integer",
              "include_in_all": false
            },
            "titre": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false,
              "fields": {
                "term": {
                  "type": "string",
                  "index": "analyzed",
                  "include_in_all": true
                }
              }
            },
            "departement": {
              "type": "short",
              "include_in_all": false
            },
            "city": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "siren": {
              "type": "integer",
              "include_in_all": false
            },
            "ca_type": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "offres": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "cp": {
              "type": "integer",
              "include_in_all": false
            },
            "nbphoto": {
              "type": "short",
              "include_in_all": false
            },
            "compte": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "prixmin": {
              "type": "integer",
              "include_in_all": false
            },
            "ad": {
              "type": "integer",
              "include_in_all": false
            },
            "pagetype": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "prixmax": {
              "type": "integer",
              "include_in_all": false
            },
            "environnement": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "boutique_id": {
              "type": "integer",
              "include_in_all": false
            },
            "nrj": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "surfacemin": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "pieces": {
              "type": "integer",
              "include_in_all": false
            },
            "surface": {
              "type": "integer",
              "include_in_all": false
            },
            "meuble": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "loyer": {
              "type": "integer",
              "include_in_all": false
            },
            "loyermin": {
              "type": "integer",
              "include_in_all": false
            },
            "loyermax": {
              "type": "integer",
              "include_in_all": false
            },
            "piecesmax": {
              "type": "integer",
              "include_in_all": false
            },
            "piecesmin": {
              "type": "integer",
              "include_in_all": false
            },
            "surfacemax": {
              "type": "integer",
              "include_in_all": false
            },
            "type": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "ges": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "activites": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "age": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "vitesse": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "experience": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "taille": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "race": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "marque": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "ccmax": {
              "type": "integer",
              "include_in_all": false
            },
            "ccmin": {
              "type": "integer",
              "include_in_all": false
            },
            "cc": {
              "type": "integer",
              "include_in_all": false
            },
            "modele": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "etudes": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "kmmax": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "kmmin": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "km": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "fonction": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            },
            "annee": {
              "type": "integer",
              "include_in_all": false
            },
            "anneemax": {
              "type": "integer",
              "include_in_all": false
            },
            "anneemin": {
              "type": "integer",
              "include_in_all": false
            },
            "temps": {
              "type": "string",
              "index": "not_analyzed",
              "include_in_all": false
            }
          }
        },
        "upload_date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss",
          "include_in_all": false
        },
        "check_date": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss",
          "include_in_all": false
        },
        "addr_locality": {
          "type": "string",
          "index": "not_analyzed",
          "include_in_all": false
        },
        "img_urls": {
          "type": "string",
          "index": "not_analyzed",
          "include_in_all": false
        }
      }
    }
  }
}
"""



def proper_encode(json_str):
    proper_encode = loads(json_str)
    return '{"index": {}}\n' + dumps(proper_encode)

def proper_encode_with_index(json_str):
    proper_encode = loads(json_str)
    #proper_encode["check_date"]
    index_date = proper_encode["upload_date"][:10]
    #"lbc-" + datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    return '{"index": {"_index": "lbc-' + index_date + '", "_type": "lbc"}}\n' + dumps(proper_encode)

if __name__ == '__main__':
    fmt = '%(asctime)-15s [%(levelname)s] [%(module)s>%(funcName)s] %(message)s'
    logging.basicConfig(format=fmt)
    logger = logging.getLogger(__name__)
    logger.setLevel( 'INFO' )

    logger.info("Start injection")
    es = Elasticsearch([
                        #{'host': 'localhost'},
                        {'host': '192.168.1.49'}
                        ])

    #es.put_template( id='lbc', body=dumps(loads(tmplt)) ) #, op_type='create'


    with open('dump_lbc.json', 'r') as fd:
        while True:
            chunk = list(islice(fd, 500))
            if not chunk:
                break

            l = list(map(proper_encode_with_index, chunk))
            #l = list(map(proper_encode, chunk))
            bulk_data =  '\n'.join(l)
            d = date.today()
            #es.bulk(index='lbc-{}'.format(d), doc_type='lbc', body=bulk_data) #chunk_size=500
            es.bulk( body=bulk_data) #chunk_size=500
            #print(bulk_data)
    logger.info("End injection")
