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
        "wdt": "http://www.wikidata.org/prop/direct/",
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
        "locationCollected": {
            "@id": "jwdt:P1665"
        },
        "label": {
            "@id": "rdfs:label",
            "@language": "en"
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
        },
        "wofId": {
            "@id": "wdt:P6766"
        }
    }
}

sparql_template = '''
    PREFIX jwd: <http://kg.jstor.org/entity/>
    PREFIX jwdt: <http://kg.jstor.org/prop/direct/>
    PREFIX jp: <http://kg.jstor.org/prop/>
    PREFIX jps: <http://kg.jstor.org/prop/statement/>
    PREFIX jpq: <http://kg.jstor.org/prop/qualifier/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    CONSTRUCT {
    
        ?specimen jwdt:P1660 ?specimenOf ;
                  schema:description ?description ;
                  rdf:type jwd:Q14316 ;
                  jwdt:P1663 ?collectionDate ;
                  jwdt:P1662 ?collector ;
                  jwdt:P1665 ?locationCollected ;
                  jwdt:P1106 ?jstorPlantsId ;
                  jwdt:P1661 ?specimenType ;
                  jwdt:P501 ?taxonName ;
                  jwdt:P1666 ?availableAt ;
                  jp:P1467 ?img .

        ?img jps:P1467 ?url ;
            jpq:P1669 ?imgSize .

        ?availableAt jps:P1666 ?wdID ;
                     rdfs:label ?herbariumName .

        ?locationCollected jps:P1665 ?locId ;
                     rdfs:label ?locationName ;
                     wdt:P6766 ?wofId .

    } WHERE {

        ?specimen jwdt:P17 jwd:Q14316 ;
                jwdt:P501 '<TAXON NAME>' ;
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
            ?specimen jwdt:P1665 ?locationCollected .
            SERVICE <https://query.wikidata.org/sparql> {
                ?locationCollected rdfs:label ?locationName .
                FILTER(LANG(?locationName) = 'en')
                OPTIONAL {
                    ?locationCollected wdt:P6766 ?wofId .
                }
            }
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

def sort_specimens(specimens, **kwargs):
    def sort_by_date(_specimens):
        _specimens.sort(key=lambda x: str(x.get('collectionDate', '')), reverse=kwargs.get('reverse') == 'true')
        return _specimens
    types = 'holotype', 'isotype', 'lectotype'
    by_type = {}
    for specimen in specimens:
        specimen_type = specimen.get('specimenType', '').lower()
        if specimen_type not in by_type:
            by_type[specimen_type] = []
        by_type[specimen_type].append(specimen)
    sorted_specimens = []
    for specimen_type in types:
        if specimen_type in by_type:
            sorted_specimens += sort_by_date(by_type[specimen_type])
    for specimen_type in by_type:
        if specimen_type not in types:
            sorted_specimens += sort_by_date(by_type[specimen_type])
    return sorted_specimens

def get_specimens(taxon_name, **kwargs):
    logger.info(f'get_specimens: taxon_name={taxon_name} max={kwargs.get("max")}')
    sparql = sparql_template.replace('<TAXON NAME>', taxon_name)
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
            if '@graph' in _framed:
                data['specimens'] = _framed['@graph']
            else:
                _framed.pop('@context')
                data['specimens'] = [_framed]
            for specimen in data['specimens']:
                for attr in ('taxonName', '@type'):
                    specimen.pop(attr)
                if 'specimenOf' in specimen:
                    data['id'] = specimen.pop('specimenOf')
                if 'collectionDate' in specimen:
                    specimen['collectionDate'] = specimen['collectionDate'].split('T')[0]
                if 'locationCollected' in specimen and 'wofId' in specimen['locationCollected']:
                    wof = specimen['locationCollected'].pop('wofId')
                    wof_parts = [wof[i:i+3] for i in range(0, len(wof), 3)]
                    specimen['locationCollected']['geojson'] = f'https://data.whosonfirst.org/{"/".join(wof_parts)}/{wof}.geojson'
                specimen['images'] = [{'url': img['id'], 'type': img['imgSize']} for img in specimen['images']]
            data['specimens'] = sort_specimens(data['specimens'], **kwargs)
            if 'max' in kwargs:
                data['specimens'] = data['specimens'][:int(kwargs['max'])]
            break
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