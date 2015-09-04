#!/usr/bin/env python3

# -- coding: utf-8 --


import os
import logging
import argparse
import signal
from colorama import Fore, Back, Style
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode, urljoin
from lbc_orchestrators_thread import LBC_Orchestrator



start_urls = [
        #'http://www.leboncoin.fr/annonces/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/' #debug criterias
        #'http://www.leboncoin.fr/_multimedia_/offres/ile_de_france/occasions/',
        #'http://www.leboncoin.fr/informatique/offres/ile_de_france/occasions/?f=c', #debug pro
    ]

    #/bonnes_affaires/ #regions voisines
    #/occasions/ # toute la france

regions = {
        'regions_voisines': 'ile_de_france/bonnes_affaires',
        'FRANCE': 'ile_de_france/occasions',
        'alsace': 'alsace',
        'aquitaine': 'aquitaine',
        'auvergne': 'auvergne',
        'basse_normandie': 'basse_normandie',
        'bourgogne': 'bourgogne',
        'bretagne': 'bretagne',
        'centre': 'centre',
        'champagne_ardenne': 'champagne_ardenne',
        'corse': 'corse',
        'franche_comte': 'franche_comte',
        'haute_normandie': 'haute_normandie',
        'ile_de_france': 'ile_de_france',
        'languedoc_roussillon': 'languedoc_roussillon',
        'limousin': 'limousin',
        'lorraine': 'lorraine',
        'midi_pyrenees': 'midi_pyrenees',
        'nord_pas_de_calais': 'nord_pas_de_calais',
        'pays_de_la_loire': 'pays_de_la_loire',
        'picardie': 'picardie',
        'poitou_charentes': 'poitou_charentes',
        'provence_alpes_cote_d_azur': 'provence_alpes_cote_d_azur',
        'rhone_alpes': 'rhone_alpes',
        'guadeloupe': 'guadeloupe',
        'martinique': 'martinique',
        'guyane': 'guyane',
        'reunion': 'reunion'
        }


allow_domains = [ "leboncoin.fr" ]




    #/annonces/offres/

category = {
            'ALL' : 'annonces',
            'EMPLOI' : '_emploi_',
            'offres_emploi' : 'offres_d_emploi',

            'VEHICULES' : '_vehicules_',
            'voitures' : 'voitures',
            'motos' : 'motos',
            'caravaning' : 'caravaning',
            'utilitaires' : 'utilitaires',
            'equipement_auto' : 'equipement_auto',
            'equipement_moto' : 'equipement_moto',
            'equipement_caravaning' : 'equipement_caravaning',
            'nautisme' : 'nautisme',
            'equipement_nautisme' : 'equipement_nautisme',

            'IMMO' : '_immobilier_',
            'ventes_immo' : 'ventes_immobilieres',
            'locations' : 'locations',
            'colocations' : 'colocations',
            'bureaux_commerces' : 'bureaux_commerces',

            'VACANCES' : '_vacances_',
            'locations_gites' : 'locations_gites',
            'chambres_hotes' : 'chambres_d_hotes',
            'campings' : 'campings',
            'hotels' : 'hotels',
            'hebergements_insolites' : 'hebergements_insolites',

            'MULTIMEDIA' : '_multimedia_',
            'informatique' : 'informatique',
            'consoles_jeux_video' : 'consoles_jeux_video',
            'image_son' : 'image_son',
            'telephonie' : 'telephonie',

            'MAISON' : '_maison_',
            'ameublement' : 'ameublement',
            'electromenager' : 'electromenager',
            'arts_de_la_table' : 'arts_de_la_table',
            'decoration' : 'decoration',
            'linge_de_maison' : 'linge_de_maison',
            'bricolage' : 'bricolage',
            'jardinage' : 'jardinage',
            'vetements' : 'vetements',
            'chaussures' : 'chaussures',
            'accessoires_bagagerie' : 'accessoires_bagagerie',
            'montres_bijoux' : 'montres_bijoux',
            'equipement_bebe' : 'equipement_bebe',
            'vetements_bebe' : 'vetements_bebe',

            'LOISIRS' : '_loisirs_',
            'dvd_films' : 'dvd_films',
            'cd_musique' : 'cd_musique',
            'livres' : 'livres',
            'animaux' : 'animaux',
            'velos' : 'velos',
            'sports_hobbies' : 'sports_hobbies',
            'instruments_de_musique' : 'instruments_de_musique',
            'collection' : 'collection',
            'jeux_jouets' : 'jeux_jouets',
            'vins_gastronomie' : 'vins_gastronomie',

            'MATPRO' : '_materiel_professionnel_',

            'SERVICES' : '_services_',
            'prestations_de_services' : 'prestations_de_services',
            'billetterie' : 'billetterie',
            'evenements' : 'evenements',
            'cours_particuliers' : 'cours_particuliers',
            'SERVICES' : 'covoiturage',

            'AUTRES' : '_',
            }

log_levels = {
                'CRITICAL': 50,
                'ERROR': 40,
                'WARNING': 30,
                'INFO': 20,
                'DEBUG': 10,
                'NOTSET': 0
            }

def update_url(url , param_asdict ):
    #scheme://netloc/path;parameters?query#fragment
    l = list(urlparse(url))
    query = l[4]
    dic_query = parse_qs( query )
    for key, val in dic_query.items():
        if type(val) is list:
            dic_query[key] = val[0]
    dic_query.update(param_asdict)
    l[4] = urlencode( dic_query )
    return urlunparse(l)


if __name__ == '__main__':


    parser = argparse.ArgumentParser( description='lbc center' )
    parser.add_argument( '-filename', default='lbc.json' , help='dump filename' )
    parser.add_argument( '-logname', default='lbc.log' , help='log filename' )
    parser.add_argument( '-level', default='INFO', choices=log_levels.keys() , help='log level' )

    parser.add_argument( '-bulksize', default=10 , type=int , help='bulk size' )
    parser.add_argument( '-concurrent_doc', default=1 , type=int , help='docpage thread' )
    parser.add_argument( '-start_urls', action='append', default=start_urls , help='start urls' )
    #parser.add_argument( '-allow_domains', action='append', default=allow_domains , help='allow domains' )
    parser.add_argument( '-lbc_category', default='ALL' , choices=category.keys() , help='lbc category to dump' )
    parser.add_argument( '-lbc_region', default='FRANCE' , choices=regions.keys() , help='lbc region' )
    parser.add_argument( '-lbc_type', default='all' , choices=['all', 'pro', 'no_pro'] , help='select all or only pro or only no_pro' )
    parser.add_argument( '-lbc_urgent', default=False , choices=[False, True] ,  help='only urgent' )

    args = parser.parse_args()
    path = os.path.join(os.getcwd(), args.logname )
    logging.basicConfig( filename=path , level=log_levels[args.level] )
    logger = logging.getLogger(__name__)

    logger.debug( "args : {}".format(args) )


    start_urls = args.start_urls

    lbc_category = category[args.lbc_category]
    lbc_region = regions[args.lbc_region]
    host = 'http://www.leboncoin.fr'
    path = os.path.join( lbc_category , "offres" )
    path  = os.path.join(path , lbc_region )
    new_url =  urljoin(host , path )
    #start_urls = [] #take only urls from args don't care start_urls var in python file
    start_urls.append(new_url)


    logger.debug( "args : {}".format(new_url) )


    http_query = {}
    if args.lbc_urgent:
        d = { "ur" : "1" }
        http_query.update(d)
    else:
        d = { "ur" : "0" }
        #http_query.update(d)
        if "ur" in http_query:
            del http_query["ur"]

    if args.lbc_type == 'pro':
        d = { "f" : "c" }
        http_query.update(d)
    elif args.lbc_type == 'no_pro':
        d = { "f" : "p" }
        http_query.update(d)
    elif args.lbc_type == 'all':
        d = { "f" : "a" }
        #http_query.update(d)
        if "f" in http_query:
            del http_query["f"]

    tmp = list()
    for url in start_urls:
        modified_url = update_url( url , http_query )
        tmp.append(modified_url)
    start_urls = tmp
    print(start_urls)

    bdd_filename = args.filename
    concurrent_doc = args.concurrent_doc
    bdd_bulksize = args.bulksize


    lbc_center = LBC_Orchestrator( start_urls, allow_domains, concurrent_doc, bdd_bulksize, bdd_filename)

    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        lbc_center.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    
    lbc_center.run()
    logger.debug( "All running" )
