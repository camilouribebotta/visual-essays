#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

import json
import getopt
import sys
from urllib.parse import quote
import concurrent.futures

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from rdflib import ConjunctiveGraph as Graph
from pyld import jsonld
 
from expiringdict import ExpiringDict
# cache = ExpiringDict(max_len=100, max_age_seconds=10)
expiration = 60 * 60 * 24 # one day
CACHE = {
    'fingerprints': ExpiringDict(max_len=1000, max_age_seconds=expiration)
}

GRAPHS = {
    'jstor': {
        'prefix': 'http://kg.jstor.org/entity/',
        'sparql_endpoint': 'https://kg-query.jstor.org/proxy/wdqs/bigdata/namespace/wdq/sparql',
    },
    'wd': {
        'prefix': 'http://www.wikidata.org/entity/',
        'sparql_endpoint': 'https://query.wikidata.org/sparql'
    }
}

default_ns = 'wd'
default_language = 'en'

query_tpl = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX jstor: <http://kg.jstor.org/entity/>
    CONSTRUCT {
    ?item rdfs:label ?label ;
            schema:description ?description ;
            skos:altLabel ?alias .
    } WHERE {
        VALUES ?item { %s } .
        ?item rdfs:label ?label .
        FILTER(LANG(?label) = '%s')
        OPTIONAL {
            ?item schema:description ?description .
            FILTER (lang(?description) = '%s') .
        }
        OPTIONAL {
            ?item skos:altLabel ?alias .
            FILTER (lang(?alias) = '%s') .
        }
    }'''

context_tpl = '''{
    "@context": {
        "wd": "http://www.wikidata.org/entity/",
        "jstor": "http://kg.jstor.org/entity/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "schema": "http://schema.org/",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "id": "@id",
        "aliases": {
            "@id": "skos:altLabel",
            "@language": "%s"
        },
        "description": {
            "@id": "schema:description",
            "@language": "%s"
        },
        "label": {
            "@id": "rdfs:label",
            "@language": "%s"
        }
    }
}'''

def _ns_fingerprints(ns, qids, language):
    sparql = query_tpl % (' '.join([f'{ns}:{qid}' for qid in qids]), language, language, language)
    context = json.loads(context_tpl % (language, language, language))
    resp = requests.post(
        GRAPHS[ns]['sparql_endpoint'],
        headers={
            'Accept': 'text/plain',
            'Content-type': 'application/x-www-form-urlencoded'},
        data='query=%s' % quote(sparql)
    )
    if resp.status_code == 200:
        # Convert N-Triples to json-ld using json-ld context
        graph = Graph()
        graph.parse(data=resp.text, format='nt')
        _jsonld = json.loads(str(graph.serialize(format='json-ld', context=context, indent=None), 'utf-8'))
        _jsonld.pop('@context')
        fingerprints = _jsonld['@graph'] if '@graph' in _jsonld else [_jsonld]
        for fingerprint in fingerprints:
            if 'aliases' in fingerprint and not isinstance(fingerprint['aliases'], list):
                fingerprint['aliases'] = [fingerprint['aliases']]
            fingerprint['language'] = language
        return fingerprints

def get_fingerprints(qids, language='en'):
    # logger.info(f'get_fingerprints: qids={qids} language={language}')
    fingerprints = {}
    if isinstance(qids, str):
        qids = [qids]
    by_ns = {}
    for qid in qids:
        ns, qid = qid.split(':') if ':' in qid else (default_ns, qid)
        fingerprint_from_cache = CACHE['fingerprints'].get(f'{language}:{ns}:{qid}')
        if fingerprint_from_cache:
            # fingerprint_from_cache['from_cache'] = True
            fingerprints[f'{ns}:{qid}'] = fingerprint_from_cache
        else:
            if ns not in by_ns:
                by_ns[ns] = set()
            by_ns[ns].add(qid)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = {}
        futures = {}
        for ns, qids in by_ns.items():
            futures[executor.submit(_ns_fingerprints, ns, qids, language)] = ns

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                results[futures[future]] = future.result()

    for fp_vals in results.values():
        for fingerprint in fp_vals:
            CACHE['fingerprints'][f'{language}:{fingerprint["id"]}'] = fingerprint
            # fingerprint['from_cache'] = False
            fingerprints[fingerprint['id']] = fingerprint

    return fingerprints

def usage():
    print('%s [hl:e:] qid qid ...' % sys.argv[0])
    print('   -h --help          Print help message')
    print('   -l --loglevel      Logging level (default=warning)')
    print('   -e --language      Language (default="en")')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, qids = getopt.getopt(
            sys.argv[1:], 'hl:e:', ['help', 'loglevel', 'language'])
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
        elif o in ('-e', '--language'):
            kwargs['language'] = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    if qids:
        print(json.dumps(get_fingerprints(qids, **kwargs)))
    else:
        usage()
        sys.exit()
