#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()

import os
import sys
import json

import requests
logging.getLogger('requests').setLevel(logging.WARNING)

from rdflib import ConjunctiveGraph as Graph
import pyld

hostname = 'https://kg.jstor.org'
default_serialization = 'jsonld' # 'rdf', 'nt', 'ttl', 'jsonld'

_context = None
def get_context():
    global _context
    if _context is None:    
        _context = json.load(open('docs/jstor-context.json', 'r'))
    return _context

def get_entity(eid, serialization=default_serialization, entity_type=None):
    url = '%s/wiki/Special:EntityData/%s.%s' % (hostname, eid, 'nt' if serialization == 'jsonld' else serialization)
    triples = requests.get(url).content.decode('utf-8').strip()
    if serialization == 'jsonld':
        context = get_context()
        graph = Graph()
        graph.parse(data=triples, format='nt')
        jsonld = json.loads(str(graph.serialize(format='json-ld', context=context, indent=None), 'utf-8'))

        if entity_type is not None:
            jsonld = pyld.jsonld.frame(
                jsonld,
                frame = {
                    '@context': context,
                    '@explicit': True,
                    '@requireAll': False,
                    '@embed': '@last',
                    '@type': entity_type,
                    'label': {},
                    'description': {},
                    'aliases': {},
                    'available at': {},
                    'collector name string': {},
                    'instance of': {
                        '@type': 'wikibase:Item',
                        '@embed': '@never'
                    },
                    "JSTOR plants ID": {},
                    "location collected": {},
                    "specimen of": {},
                    "specimen type": {},
                    "taxon name": {},
                    "taxon rank": {},
                    'images': {
                        '@type': 'wikibase:Statement',
                        '@explicit': True,
                        '@omit': True,
                        'size': {},
                        'url': {}
                    }
                })
        jsonld['@graph'] = [{**clean(entity), **{'id': f'jstor:{eid}'}}for entity in jsonld['@graph'] if entity['@id'].split(':')[-1] == eid]
        return jsonld
    else:
        return triples

def clean(d):
    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (clean(v) for v in d) if v]
    return {k: v for k, v in ((k, clean(v)) for k, v in d.items()) if k[0] != '@' and v}

if __name__ == '__main__':

    eid = sys.argv[1]
    serialization = sys.argv[2] if len(sys.argv) > 2 else default_serialization
    entity_type = 'wikibase:Item' if serialization == 'jsonld' else None
    entity = get_entity(eid, serialization, entity_type)

    if serialization == 'jsonld':
        print(json.dumps(entity))
    else:
        print(entity)
