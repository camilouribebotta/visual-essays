#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()

import os
import re
import json
import getopt
import sys
from urllib.parse import quote

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from rdflib import ConjunctiveGraph as Graph
from pyld import jsonld

context = {
    "@context": {
        "jwd": "http://kg.jstor.org/entity/",
        "jwdt": "http://kg.jstor.org/prop/direct/",
        "jp": "http://kg.jstor.org/prop/",
        "jps": "http://kg.jstor.org/prop/statement/",
        "jpq": "http://kg.jstor.org/prop/qualifier/",
        "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
        "schema": "http://schema.org/",
        "wd": "http://www.wikidata.org/entity/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",

        "Specimen": "jwd:Q14316",

        "id": "@id",

        "collectionDate": {
            "@id": "jwdt:P1663",
            "@type": "xsd:dateTime"
        },
        "collector": {
            "@id": "jwdt:P1662",
            "@container": "@set"
        },
        "description": {
            "@id": "schema:description",
            "@language": "en"
        },
        "herbarium": {
            "@id": "jwdt:P1666",
            "@type": "@id"
        },
        "herbariumName": {
            "@id": "rdfs:label",
            "@language": "en"
        },
        "images": {
            "@id": "jp:P1467",
            "@type": "@id",
            "@container": "@set"
        },
        "imgSize": {
            "@id": "jpq:P1669"
        },
        "instance of": {
            "@id": "jwdt:P17",
            "@type": "@id"
        },
        "jstorPlantsId": {
            "@id": "jwdt:P1106"
        },
        "specimenOf": {
            "@id": "jwdt:P1660",
            "@type": "@id"
        },
        "specimenType": {
            "@id": "jwdt:P1661"
        },
        "taxonName": {
            "@id": "jwdt:P501"
        }
    }
}

sparql_template = '''
    PREFIX jwd: <http://kg.jstor.org/entity/>
    PREFIX jwdt: <http://kg.jstor.org/prop/direct/>
    PREFIX jp: <http://kg.jstor.org/prop/>
    PREFIX jps: <http://kg.jstor.org/prop/statement/>
    PREFIX jpq: <http://kg.jstor.org/prop/qualifier/>

    CONSTRUCT {
    
        ?specimen jwdt:P1660 ?specimenOf ;
                  schema:description ?description ;
                  rdf:type jwd:Q14316 ;
                  jwdt:P1663 ?collectionDate ;
                  jwdt:P1662 ?collector ;
                  jwdt:P1106 ?jstorPlantsId ;
                  jwdt:P1661 ?specimenType ;
                  jwdt:P501 ?taxonName ;
                  jwdt:P1666 ?availableAt ;
                  jp:P1467 ?img .

        ?img jps:P1467 ?url ;
            jpq:P1669 ?imgSize .

        ?availableAt jps:P1666 ?wdID ;
                     rdfs:label ?herbariumName .

    } WHERE {

        ?specimen jwdt:P17 jwd:Q14316 ;
                jwdt:P501 '<TAXON NAME>' ;
                jwdt:P1660 ?wdItem ;
                schema:description ?description ;
                jwdt:P1106 ?jstorPlantsId ;
                jwdt:P1661 ?specimenType ;
                jwdt:P501 ?taxonName ;
                jp:P1467 [ jps:P1467 ?img ;
                            jpq:P1669 ?imgSize ] .
        OPTIONAL {
            ?specimen jwdt:P1660 ?specimenOf .
        }
        OPTIONAL {
            ?specimen jwdt:P1663 ?collectionDate .
        }
        OPTIONAL {
            ?specimen jwdt:P1662 ?collector .
        }
        OPTIONAL {
            ?specimen jwdt:P1666 ?availableAt .
            SERVICE <https://query.wikidata.org/sparql> {
                ?availableAt rdfs:label ?herbariumName .
                FILTER(LANG(?herbariumName) = 'en')
            }
        }

    }
'''

def get_specimens(taxon_name):
    logger.info(f'get_specimens: taxon_name={taxon_name}')
    sparql = sparql_template.replace('<TAXON NAME>', taxon_name)
    logger.debug(sparql)
    data = {'taxonName': taxon_name, 'specimens': []}
    for _ in range(2):
        resp = requests.post(
            'https://kg-query.jstor.org/proxy/wdqs/bigdata/namespace/wdq/sparql',
            headers={
                'Accept': 'text/plain',
                'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'JSTOR Labs python client'},
            data='query=%s' % quote(sparql)
        )
        if resp.status_code == 200:
            # Convert N-Triples to json-ld using json-ld context
            graph = Graph()
            graph.parse(data=resp.text, format='nt')
            _jsonld = json.loads(str(graph.serialize(format='json-ld', context=context, indent=None), 'utf-8'))
            if '@graph' not in _jsonld:
                _context = _jsonld.pop('@context')
                _jsonld = {'@context': _context, '@graph': [_jsonld]}
            logger.debug(_jsonld)
            _framed = jsonld.frame(
                _jsonld,
                frame = {
                    "@context": context,
                    "@type": "Specimen"
                }
            )
            data['specimens'] = _framed['@graph']
            for specimen in data['specimens']:
                for attr in ('taxonName', '@type'):
                    specimen.pop(attr)
                if 'specimenOf' in specimen:
                    data['id'] = specimen.pop('specimenOf')
                if 'collectionDate' in specimen:
                    specimen['collectionDate'] = specimen['collectionDate'].split('T')[0]
                specimen['images'] = [{'url': img['id'], 'type': img['imgSize']} for img in specimen['images']]
    return data

def usage():
    print(f'{sys.argv[0]} [hl:] taxon name')
    print(f'   -h --help          Print help message')
    print(f'   -l --loglevel      Logging level (default=warning)')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:', ['help', 'loglevel'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-l', '--loglevel'):
            loglevel = a.lower()
            if loglevel in ('error',): logger.setLevel(logging.ERROR)
            elif loglevel in ('warn','warning'): logger.setLevel(logging.INFO)
            elif loglevel in ('info',): logger.setLevel(logging.INFO)
            elif loglevel in ('debug',): logger.setLevel(logging.DEBUG)
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    taxon_name = ' '.join(args)
    print(json.dumps(get_specimens(taxon_name)))