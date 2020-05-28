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
import traceback
from urllib.parse import quote
import concurrent.futures
from collections import OrderedDict

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from bs4 import BeautifulSoup

from fingerprints import get_fingerprints

GRAPHS = {
    'jstor': {
        'prefix': '<http://kg.jstor.org/entity/>',
        'baseurl': 'https://kg.jstor.org/entity',
        'sparql_endpoint': 'https://kg-query.jstor.org/proxy/wdqs/bigdata/namespace/wdq/sparql',
        'api_endpoint': 'https://kg.jstor.org/w/api.php',
        'types': {
            'entity': 'Q13'
        }
    },
    'wd': {
        'prefix': '<http://www.wikidata.org/entity/>',
        'baseurl': 'https://www.wikidata.org/entity',
        'sparql_endpoint': 'https://query.wikidata.org/sparql',
        'api_endpoint': 'https://www.wikidata.org/w/api.php',
        'types': {
            'entity': 'Q35120'
        }
    }
}
default_ns = 'wd'
default_language = 'en'
default_entity_type = 'entity'

class KnowledgeGraph(object):

    def __init__(self, **kwargs):
        self.cache = kwargs.get('cache', {})
        self.ns = kwargs.get('ns', default_ns)
        self.language = kwargs.get('language', default_language)
        self.entity_type = kwargs.get('entity_type', default_entity_type)
        self.prop_mappings = {}
        self.formatter_urls = {}
        for ns in GRAPHS:
            self.prop_mappings[ns] = dict([(p['id'], p) for p in self._properties(ns)])
            self.formatter_urls[ns] = dict([(p['id'], p) for p in self._formatter_urls(ns)])

    def entity(self, qid, language=None, context=None, raw=False, **kwargs):
        language = language if language else self.language
        ns, qid = qid.split(':') if ':' in qid else (self.ns, qid)
        refresh = kwargs.pop('refresh', 'false').lower() in ('', 'true')

        cache_key = f'{ns}:{qid}-{language}-{context}'
        entity = self.cache.get(cache_key) if not refresh and not raw else None
        if entity:
            entity['fromCache'] = True
            return entity
 
        if ns == 'jstor':
            primary = f'{ns}:{qid}'
            wd_qid = self._wd_qid(qid)
            secondary = f'wd:{wd_qid}' if wd_qid else None
        else: # ns = 'wd'
            jstor_qid = self._jstor_qid(qid)
            if jstor_qid:
                primary = f'jstor:{jstor_qid}'
                secondary = f'{ns}:{qid}'
            else:
                primary = f'{ns}:{qid}'
                secondary = None
        
        logger.info(f'entity: primary={primary} secondary={secondary} language={language} context={context}')

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            by_qid = {}
            futures = {}
            for qid in [_qid for _qid in (secondary, primary) if _qid]:
                futures[executor.submit(self._entity, qid, language)] = qid

            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    by_qid[futures[future]] = future.result()
        
        entity = self._merge(by_qid.get(primary), by_qid.get(secondary))

        if not raw:
            self._add_summary_text(entity, context, **kwargs)
        
            entity = self._add_id_labels(entity, get_fingerprints(self._find_ids(entity), language))
        
            self.cache[cache_key] = entity
        entity['fromCache'] = False

        return entity

    def _entity(self, qid, language='en', entity_type='entity'):
        '''Gets entity data directly from wikibase API (rather than a SPARQL query) and
        returns a simplified representation of data with property IDs converted to labels enabling
        property merging with other graphs using a compatible data model'''
        ns, qid = qid.split(':') if ':' in qid else (self.ns, qid)
        entity_url = f'{GRAPHS[ns]["api_endpoint"]}?format=json&action=wbgetentities&ids={qid}'
        resp = requests.get(entity_url).json()
        raw_entity = resp.get('entities', {}).get(qid)
        entity = OrderedDict()
        entity['label'] = raw_entity['labels'].get(language,{}).get('value','')
        entity['language'] = language
        entity['id'] = f'{ns}:{qid}'
        if 'descriptions' in raw_entity and language in raw_entity['descriptions']:
            entity['description'] = raw_entity['descriptions'][language]['value']
        if 'aliases' in raw_entity and language in raw_entity['aliases']:
            entity['aliases'] = [alias['value'] for alias in raw_entity['aliases'][language]]
        if 'claims' in raw_entity:
            entity['claims'] = self._claims(raw_entity['claims'], ns)
        return entity

    def _claims(self, claims, ns='wd'):
        '''Converts wikibase claims into a simplified version with property IDs (Pxxxx)
        converted to text using the property labels.'''
        _claims = {}
        for prop, stmts in claims.items():
            prop_label = self.prop_mappings[ns].get(prop, {}).get('label', prop)
            _claims[prop_label] = []
            for stmt in stmts:
                stmt_value = self._stmt_value(stmt['mainsnak'], ns)
                if not stmt_value:
                    continue
                value = {'value': stmt_value}
                _claims[prop_label].append(value)
                if 'qualifiers' in stmt:
                    value['qualifiers'] = {}
                    for qual_prop, qualifiers in stmt['qualifiers'].items():
                        qualifier_label = self.prop_mappings[ns][qual_prop]['label']
                        value['qualifiers'][qualifier_label] = []
                        for qualifier in qualifiers:
                            value['qualifiers'][qualifier_label].append(self._stmt_value(qualifier, ns))
                if 'references' in stmt:
                    value['references'] = []
                    for reference in stmt['references']:
                        value['references'].append({})
                        for ref_prop, ref_stmts in reference['snaks'].items():
                            ref_label = self.prop_mappings[ns][ref_prop]['label']
                            value['references'][-1][ref_label] = []
                            for ref_stmt in ref_stmts:
                                value['references'][-1][ref_label].append(self._stmt_value(ref_stmt, ns))
        return _claims
        
    def _stmt_value(self, stmt, ns='wd'):
        '''Performs any needed statement value conversions'''
        if 'datavalue' in stmt:
            datatype = stmt['datatype']
            value = stmt['datavalue']['value']
            if datatype in ('commonsMedia', 'string', 'url'):
                return value
            elif datatype == 'external-id':
                extid = {'id': value}
                if 'property' in stmt and stmt['property'] in self.formatter_urls[ns]:
                    extid['url'] = self.formatter_urls[ns][stmt["property"]]["url"].replace('$1', value)
                return extid
            elif datatype == 'wikibase-item':
                return f'{ns}:{value["id"]}'
            elif datatype == 'globe-coordinate':
                return [value['latitude'], value['longitude']]
            elif datatype == 'quantity':
                # https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#quantity
                value['unit'] = value['unit'].replace('http://www.wikidata.org/entity/', 'wd:')
                return value
            elif datatype == 'time':
                # More info on time precision can be found at https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#time
                return {'time': value['time'][1:], 'precision': value['precision']}
            elif datatype == 'monolingualtext':
                return value # TODO
            else:
                logger.warning(f'Unrecognized datatype {datatype} with value {value}')
                return value

    def _properties(self, ns='wd'):
        '''Get property mappings for graph to map property entity IDs to labels'''
        cached_props_path = f'mappings/{ns}-props.json'
        if os.path.exists(cached_props_path):
            with open (cached_props_path, 'r') as fp:
                props = json.load(fp)
                return props
        else:
            sparql = '''
                SELECT ?property ?propertyType ?propertyLabel ?propertyDescription ?propertyAltLabel WHERE {
                    ?property wikibase:propertyType ?propertyType .
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                }
                ORDER BY ASC(xsd:integer(STRAFTER(STR(?property), 'P')))'''
            sparql_results = requests.post(
                GRAPHS[ns]['sparql_endpoint'],
                headers={
                    'Accept': 'application/sparql-results+json',
                    'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': 'JSTOR Labs python client'},
                data='query=%s' % quote(sparql)
            ).json()['results']['bindings']
            props = [
                {
                    'id': p['property']['value'].split('/')[-1],
                    'type': p['propertyType']['value'].split('#')[-1],
                    'label': p['propertyLabel']['value'],
                    'description': p['propertyDescription']['value'] if 'propertyDescription' in p else None,
                    'aliases': p['propertyAltLabel']['value'].split(',') if 'propertyAltLabel' in p else []
                } for p in sparql_results
            ]
            with open (cached_props_path, 'w') as fp:
                json.dump(props, fp)
            return props

    def _formatter_urls(self, ns='wd'):
        '''Get all formatter URLs for graph for converting external entity IDs to full URL'''
        cached_path = f'mappings/{ns}-formatter-urls.json'
        if os.path.exists(cached_path):
            with open (cached_path, 'r') as fp:
                formatter_urls = json.load(fp)
                return formatter_urls
        else:
            for prop, value in self.prop_mappings[ns].items():
                if value['label'] == 'formatter URL':
                    break
            sparql = '''
                SELECT ?entity ?label ?formatterURL WHERE {
                    ?entity wdt:%s ?formatterURL ;
                    rdfs:label ?label .
                    FILTER(LANG(?label) = 'en')
                }''' % (prop)
            sparql_results = requests.post(
                GRAPHS[ns]['sparql_endpoint'],
                headers={
                    'Accept': 'application/sparql-results+json',
                    'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': 'JSTOR Labs python client'},
                data='query=%s' % quote(sparql)
            ).json()['results']['bindings']
            formatter_urls = [
                {
                    'id': p['entity']['value'].split('/')[-1],
                    'label': p['label']['value'],
                    'url': p['formatterURL']['value']
                } for p in sparql_results
            ]
            with open (cached_path, 'w') as fp:
                json.dump(formatter_urls, fp)
            return formatter_urls


    def _wd_qid(self, jstorqid):
        '''Gets Wikidata QID corresponding to provided QID from JSTOR graph'''
        sparql = '''
        PREFIX jp: <http://kg.jstor.org/prop/>
        PREFIX jpr: <http://kg.jstor.org/prop/reference/>
        SELECT ?item WHERE {
            {
                wd:%s wdt:P4 ?item .
            } UNION {
                wd:%s wdt:P3 ?wdEntity .
                BIND(URI(CONCAT('http://www.wikidata.org/entity/', ?wdEntity)) AS ?item)
            } UNION {
                wd:%s jp:P4 [ prov:wasDerivedFrom [ jpr:P3 ?item ] ] .
            }
        }''' % (jstorqid, jstorqid, jstorqid)
        resp = requests.post(
            GRAPHS['jstor']['sparql_endpoint'],
            headers={
                'Accept': 'application/sparql-results+json;charset=UTF-8',
                'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'JSTOR Labs python client'},
            data='query=%s' % quote(sparql)
        ).json()
        for b in resp['results']['bindings']:
            if b['item']['type'] == 'uri':
                last_path_elem = b['item']['value'].split('/')[-1]
                if last_path_elem[0] == 'Q' and last_path_elem[1:].isdigit():
                    return last_path_elem

    def _jstor_qid(self, wdqid):
        '''Gets JSTOR QID corresponding to provided Wikidata QID'''
        sparql = '''
            PREFIX jp: <http://kg.jstor.org/prop/>
            PREFIX jpr: <http://kg.jstor.org/prop/reference/>
            SELECT ?item WHERE {
                {
                    VALUES ?value {
                        <https://www.wikidata.org/wiki/%s>
                        <https://www.wikidata.org/entity/%s> 
                    } .
                    ?item wdt:P4 ?value .
                } UNION {
                    ?item wdt:P3 '%s' .
                } UNION {
                    ?item jp:P4 [ prov:wasDerivedFrom [ jpr:P3 '%s' ] ] .
                }
            }''' % (wdqid, wdqid, wdqid, wdqid)
        resp = requests.post(
            GRAPHS['jstor']['sparql_endpoint'],
            headers={
                'Accept': 'application/sparql-results+json;charset=UTF-8',
                'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'JSTOR Labs python client'},
            data='query=%s' % quote(sparql)
        ).json()
        for b in resp['results']['bindings']:
            if b['item']['type'] == 'uri':
                last_path_elem = b['item']['value'].split('/')[-1]
                if last_path_elem[0] == 'Q' and last_path_elem[1:].isdigit():
                    return last_path_elem

    def _merge(self, primary, secondary=None):
        '''Merges entity claims from 2 graphs'''
        logger.debug(f'_merge: primary={primary["id"] if primary else None} secondary={secondary["id"] if secondary else None}')
        def _norm(v):
            return set([json.dumps(d, sort_keys=True) for d in v]) if isinstance(v, list) else json.dumps(v, sort_keys=True)

        for entity in (primary, secondary):
            if entity and 'image URL' in entity['claims']:
                entity['claims']['image'] = entity['claims'].get('image', []) + entity['claims'].pop('image URL')

        merged = primary
        merged['id'] = [merged['id']]
        if secondary and 'claims' in secondary:
            merged['id'].append(secondary['id'])
            if not 'claims' in merged:
                merged['claims'] = secondary['claims']
            else:
                for k, v in secondary['claims'].items():
                    if k in merged['claims']:
                        mv = _norm(merged['claims'][k])
                        for sv in v:
                            if not _norm(sv) in mv:
                                merged['claims'][k].append(sv)
                    else:
                        merged['claims'][k] = v
        return merged

    def _add_summary_text(self, entity, context=None, **kwargs):
        '''Finds and adds summary data for entity.  For Wikidata entities the summary data is obtained
        from the Wikipedia article linked to the entity in the graph, if any.  For entities in the JSTOR
        graph the summary data (if any) is referenced by the "described at URL" property'''
        logger.info(f'_add_summary_text: entity={entity["id"]} context={context}')
        summary_urls = {}
        for _id in entity['id']:
            if _id.startswith('jstor:') and 'described at URL' in entity['claims']:
                for stmt in entity['claims']['described at URL']:
                    # Ignore summary data associated with a specific project unless the
                    #  property code is proided as a method argument
                    logger.info(stmt['value'])
                    if not self._is_entity_id(stmt['value'].split('/')[-1], False):
                        if context:
                            if context in stmt.get('qualifiers',{}).get('project code',[]):
                                summary_urls['jstor'] = stmt['value']
                        else:
                            if 'project code' not in stmt.get('qualifiers', {}):
                                summary_urls['jstor'] = stmt['value']
            elif _id.startswith('wd:'):
                sparql = '''
                    SELECT ?mwPage {
                        ?mwPage schema:about %s .
                        ?mwPage schema:isPartOf <https://en.wikipedia.org/> .
                    }''' % (_id)
                resp = requests.post(
                    GRAPHS['wd']['sparql_endpoint'],
                    headers={
                        'Accept': 'application/sparql-results+json;charset=UTF-8',
                        'Content-type': 'application/x-www-form-urlencoded',
                        'User-agent': 'JSTOR Labs python client'},
                    data='query=%s' % quote(sparql)
                )
                if resp.status_code == 200:
                    resp = resp.json()
                    if resp['results']['bindings']:
                        summary_urls['wd'] = resp['results']['bindings'][0]['mwPage']['value']
                else:
                    logger.info(f'_add_summary_text: resp_code={resp.status_code} msg={resp.text}')

        if summary_urls:
            entity['summary info'] = {}
            for ns in ('wd', 'jstor'):
                if ns not in summary_urls:
                    continue
                url = summary_urls[ns]
                page = url.replace('/w/', '/wiki/').split('/wiki/')[-1]
                if ns == 'wd':
                    # Summary data from Wikipedia comes back nicely formatted.  We just add it to the entity
                    entity['summary info'] = requests.get(
                        f'https://en.wikipedia.org/api/rest_v1/page/summary/{page}',
                        headers={'User-agent': 'JSTOR Labs python client'},
                    ).json()
                elif ns == 'jstor':
                    # We need to create formatted summary data from the wikitext in the referenced mediawiki page
                    #  Any data extracted is used to update the Wikidata/Wikipedia summary data, if found.  Currently
                    #  this just includes the extract text in raw and HTML
                    resp = requests.get(f'https://kg.jstor.org/w/api.php?action=parse&format=json&page={page}').json()
                    html = BeautifulSoup(resp['parse']['text']['*'], 'html5lib')
                    extract = html.find('p')
                    if extract:
                        entity['summary info'].update({
                            'extract_html': str(extract).replace('\n',''),
                            'extract': extract.text.strip()
                        })

    def _is_entity_id(self, s, ns_required=True):
        if not s or not isinstance(s, str): return False
        eid = s.split(':')
        if len(eid) == 1 and ns_required:
            return False
        if len(eid) == 2 and eid[0] not in GRAPHS:
            return False
        if len(eid) > 2:
            return False
        return len(eid[-1]) > 1 and eid[-1][0] in ('Q', 'P') and eid[-1][1:].isdecimal()

    def _find_ids(self, entity):
        ids = set()
        self._find_ids_recursive(entity, ids)
        return ids

    def _find_ids_recursive(self, d, ids):
        if not isinstance(d, (dict, list, str)):
            return ids
        if isinstance(d, str):
            if self._is_entity_id(d):
                ids.add(d)
        elif isinstance(d, list):
            for v in d:
                self._find_ids_recursive(v, ids)
        else: # a dict
            for v in d.values():
                self._find_ids_recursive(v, ids)

    def _add_id_labels(self, d, fingerprints):
        if not isinstance(d, (dict, list, str)):
            return d
        if isinstance(d, str):
            if self._is_entity_id(d):
                if d in fingerprints:
                    ns, qid = d.split(':')
                    label = fingerprints[d]['label']
                    url = f'{GRAPHS[ns]["baseurl"]}/{qid}'
                    d = {'id': d, 'value': label, 'url': url}
            return d
        elif isinstance(d, list):
            return [v for v in (self._add_id_labels(v, fingerprints) for v in d) if v]
        return {k: v for k, v in ((k, self._add_id_labels(v, fingerprints)) for k, v in d.items()) if v}


def usage():
    print('%s [hl:e:r] qid' % sys.argv[0])
    print('   -h --help       Print help message')
    print('   -l --loglevel   Logging level (default=warning)')
    print('   -e --language   Language (default="en")')
    print('   -r --raw        Return raw jsonld')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:e:r', ['help', 'loglevel', 'language', 'raw'])
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
        elif o in ('-r', '--raw'):
            kwargs['raw'] = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    kg = KnowledgeGraph(**kwargs)

    if args:
        print(json.dumps(kg.entity(args[0], **kwargs)))
    else:
        usage()
        sys.exit()
