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
from collections import OrderedDict

import requests
logging.getLogger('requests').setLevel(logging.INFO)

import markdown as markdown_parser
from bs4 import BeautifulSoup

from fingerprints import get_fingerprints

GRAPHS = [
    {
        'ns': 'jstor',
        'prefix': 'http://kg.jstor.org/entity/',
        'baseurl': 'https://kg.jstor.org/entity',
        'sparql_endpoint': 'https://kg-query.jstor.org/proxy/wdqs/bigdata/namespace/wdq/sparql',
        'api_endpoint': 'https://kg.jstor.org/w/api.php',
        'types': {
            'entity': 'Q13'
        }
    },
    {
        'ns': 'wd',
        'prefix': 'http://www.wikidata.org/entity/',
        'baseurl': 'https://www.wikidata.org/entity',
        'sparql_endpoint': 'https://query.wikidata.org/sparql',
        'api_endpoint': 'https://www.wikidata.org/w/api.php',
        'types': {
            'entity': 'Q35120'
        }
    }
]
PREFIXES = dict([(g['ns'],g['prefix']) for g in GRAPHS])
NAMESPACES = set([g['ns'] for g in GRAPHS])
default_ns = 'wd'
default_entity_type = 'entity'

def as_uri(s, acct=None, repo=None):
    global default_ns
    uri = None
    if s.startswith('http'):
        uri = s
    else:
        prefix, entity_id = s.split(':') if ':' in s else (default_ns, s)
        if prefix in PREFIXES and _is_entity_id(entity_id):
            logger.info(f'{prefix}:{entity_id}')
            uri = f'{PREFIXES[prefix]}{entity_id}'
        else:
            uri = f'http://{acct}.github.io/{repo}/entity/{s}'
    logger.info(uri)
    return uri

class KnowledgeGraph(object):

    def __init__(self, **kwargs):
        self.acct = kwargs.get('acct')
        self.repo = kwargs.get('repo')
        self.cache = kwargs.get('cache', {})
        self.entity_type = kwargs.get('entity_type', default_entity_type)
        self.prop_mappings = {}
        self.formatter_urls = {}
        for g in GRAPHS:
            self.prop_mappings[g['ns']] = dict([(p['id'], p) for p in self._properties(g)])
            self.formatter_urls[g['ns']] = dict([(p['id'], p) for p in self._formatter_urls(g)])
        logger.info(f'KnowledgeGraph: acct={self.acct} repo={self.repo}')

    def entity(self, uri, project=None, raw=False, article=None, **kwargs):
        logger.info(f'entity={uri} project={project} raw={raw} article={article}')
        refresh = str(kwargs.pop('refresh', 'false')).lower() in ('', 'true')

        cache_key = f'{uri}-{project}'
        entity = self.cache.get(cache_key) if not refresh and not raw else None
        if entity:
            entity['fromCache'] = True
            return entity
 
        secondary = None
        if uri.startswith('http://kg.jstor.org/'):
            primary = self._entity_from_wikibase(uri)
            primary['id'] = f'jstor:{primary["id"]}'
            if primary and 'Wikidata entity ID' in primary.get('claims', {}):
                secondary = self._entity_from_wikibase(primary['claims'].pop('Wikidata entity ID')[0]['value']['url'])
        elif uri.startswith('http://www.wikidata.org/'):
            primary = self._entity_from_wikibase(uri)
            primary['id'] = f'wd:{primary["id"]}'
        else:
            uri = uri if uri.endswith('.json') else f'{uri}.json'
            primary = self._entity_from_url(uri)
            wd_id = None
            statements = []
            for stmt in primary.get('statements', []):
                if stmt['claim']['property'] == 'Wikidata entity ID':
                    wd_id = stmt['claim']['value']
                else:
                    statements.append(stmt)
            if wd_id:
                primary['statements'] = stmt
                secondary = self._entity_from_wikibase(f'http://www.wikidata.org/entity/{wd_id}')

        if secondary: # merge primary and secondary
            entity = {'id': primary['id']}
            for fld in ('labels', 'descriptions', 'aliases', 'claims'):
                entity[fld] = {**secondary.get(fld,{}), **primary.get(fld,{})}
        else:
            entity = primary

        if not raw:
            self._add_summary_text(entity, project, article, **kwargs)
        
            entity = self._add_id_labels(entity, get_fingerprints(self._find_ids(entity)))
        
            self.cache[cache_key] = entity

        entity['fromCache'] = False

        return entity

    def _entity_from_url(self, uri):
        for suffix in ('', '.json', 'jsonld'):
            try:
                entity = requests.get(f'{uri}{suffix}').json()
                if 'id' not in entity:
                    entity['id'] = uri.replace('https', 'http').replace('.json', '').replace('.jsonld', '')
                return entity
            except:
                pass
        return {}

    def _entity_from_wikibase(self, uri, language='en', entity_type='entity'):
        '''Gets entity data directly from wikibase API (rather than a SPARQL query) and
        returns a simplified representation of data with property IDs converted to labels enabling
        property merging with other graphs using a compatible data model'''
        g = [g for g in GRAPHS if uri.startswith(g['prefix'])][0]
        qid = uri.split('/')[-1]
        ns = g['ns']
        entity_url = f'{g["api_endpoint"]}?format=json&action=wbgetentities&ids={qid}'
        resp = requests.get(entity_url).json()
        raw_entity = resp.get('entities', {}).get(qid)
        entity = OrderedDict()
        for fld in ('id', 'labels', 'descriptions', 'aliases'):
            if fld in raw_entity:
                entity[fld] = raw_entity[fld]
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

    def _properties(self, g):
        '''Get property mappings for graph to map property entity IDs to labels'''
        cached_props_path = f'mappings/{g["ns"]}-props.json'
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
                g['sparql_endpoint'],
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

    def _formatter_urls(self, g):
        '''Get all formatter URLs for graph for converting external entity IDs to full URL'''
        cached_path = f'mappings/{g["ns"]}-formatter-urls.json'
        if os.path.exists(cached_path):
            with open (cached_path, 'r') as fp:
                formatter_urls = json.load(fp)
                return formatter_urls
        else:
            for prop, value in self.prop_mappings[g['ns']].items():
                if value['label'] == 'formatter URL':
                    break
            sparql = '''
                SELECT ?entity ?label ?formatterURL WHERE {
                    ?entity wdt:%s ?formatterURL ;
                    rdfs:label ?label .
                    FILTER(LANG(?label) = 'en')
                }''' % (prop)
            sparql_results = requests.post(
                g['sparql_endpoint'],
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

    def _add_summary_text(self, entity, project=None, article=None, **kwargs):
        '''Finds and adds summary data for entity.  For Wikidata entities the summary data is obtained
        from the Wikipedia article linked to the entity in the graph, if any.  For entities in the JSTOR
        graph the summary data (if any) is referenced by the "described at URL" property'''
        logger.info(f'_add_summary_text: id={entity.get("id")} project={project} article={article}')
        summary_url = None
        if article:
            summary_url = f'https://{self.acct}.github.io/{self.repo}/articles/{article}.md'
        elif entity.get('id'):
            if 'described at URL' in entity['claims']:
                for stmt in entity['claims']['described at URL']:
                    # Ignore summary data associated with a specific project unless the
                    #  property code is proided as a method argument
                    if not _is_entity_id(stmt['value'].split('/')[-1], False):
                        if project:
                            if project in stmt.get('qualifiers',{}).get('project code',[]):
                                summary_url = stmt['value']
                        else:
                            if 'project code' not in stmt.get('qualifiers', {}):
                                summary_url = stmt['value']
            elif entity['id'].startswith('wd:'):
                g = [g for g in GRAPHS if g['ns'] == 'wd'][0]
                sparql = '''
                    SELECT ?mwPage {
                        ?mwPage schema:about %s .
                        ?mwPage schema:isPartOf <https://en.wikipedia.org/> .
                    }''' % (entity['id'])
                resp = requests.post(
                    g['sparql_endpoint'],
                    headers={
                        'Accept': 'application/sparql-results+json;charset=UTF-8',
                        'Content-type': 'application/x-www-form-urlencoded',
                        'User-agent': 'JSTOR Labs python client'},
                    data='query=%s' % quote(sparql)
                )
                if resp.status_code == 200:
                    resp = resp.json()
                    if resp['results']['bindings']:
                        summary_url = resp['results']['bindings'][0]['mwPage']['value']
                else:
                    logger.info(f'_add_summary_text: resp_code={resp.status_code} msg={resp.text}')

        if summary_url:
            page = summary_url.replace('/w/', '/wiki/').split('/wiki/')[-1]
            if 'wikipedia.org/wiki/' in summary_url:
                # Summary data from Wikipedia comes back nicely formatted.  We just add it to the entity
                entity['summary info'] = requests.get(
                    f'https://en.wikipedia.org/api/rest_v1/page/summary/{page}',
                    headers={'User-agent': 'JSTOR Labs python client'},
                ).json()
            elif 'kg.jstor.org/wiki' in summary_url:
                # We need to create formatted summary data from the wikitext in the referenced mediawiki page
                #  Any data extracted is used to update the Wikidata/Wikipedia summary data, if found.  Currently
                #  this just includes the extract text in raw and HTML
                resp = requests.get(f'https://kg.jstor.org/w/api.php?action=parse&format=json&page={page}').json()
                html = BeautifulSoup(resp['parse']['text']['*'], 'html5lib')
                extract = html.find('p')
                if extract:
                    entity['summary info'] = {
                        'extract_html': str(extract).replace('\n',''),
                        'extract': extract.text.strip()
                    }
            else:
                logger.info(summary_url)
                md = requests.get(summary_url).content.decode('utf-8')
                html = markdown_parser.markdown(md, output_format='html5')
                soup = BeautifulSoup(html, 'html5lib')
                paragraphs = ['\n'.join(p.contents) for p in soup.find_all('p')]
                logger.info('\f'.join(paragraphs))
                entity['summary info'] = {'extract_html': '<br><br>'.join(paragraphs)}

    def _find_ids(self, entity):
        ids = set()
        self._find_ids_recursive(entity, ids)
        return ids

    def _find_ids_recursive(self, d, ids):
        if not isinstance(d, (dict, list, str)):
            return ids
        if isinstance(d, str):
            if _is_entity_id(d):
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
            if _is_entity_id(d):
                if d in fingerprints:
                    ns, qid = d.split(':')
                    label = fingerprints[d]['label']
                    g = [g for g in GRAPHS if g['ns'] == ns][0]
                    url = f'{g["baseurl"]}/{qid}'
                    d = {'id': d, 'value': label, 'url': url}
            return d
        elif isinstance(d, list):
            return [v for v in (self._add_id_labels(v, fingerprints) for v in d) if v]
        return {k: v for k, v in ((k, self._add_id_labels(v, fingerprints)) for k, v in d.items()) if v}


def _is_entity_id(s, ns_required=True):
    if not s or not isinstance(s, str): return False
    eid = s.split(':')
    if len(eid) == 1 and ns_required:
        return False
    if len(eid) == 2 and eid[0] not in NAMESPACES:
        return False
    if len(eid) > 2:
        return False
    return len(eid[-1]) > 1 and eid[-1][0] in ('Q', 'P') and eid[-1][1:].isdecimal()

def usage():
    print('%s [hl:jrp:] qid' % sys.argv[0])
    print('   -h --help       Print help message')
    print('   -l --loglevel   Logging level (default=warning)')
    print('   -j --raw        Return raw jsonld')
    print('   -r --refresh    Refresh cache')
    print('   -p --project    Entity context')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:jrp:', ['help', 'loglevel', 'raw', 'refresh', 'project'])
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
        elif o in ('-j', '--raw'):
            kwargs['raw'] = True
        elif o in ('-r', '--refresh'):
            kwargs['refresh'] = True
        elif o in ('-p', '--project'):
            kwargs['project'] = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    kg = KnowledgeGraph(**kwargs)

    if args:
        kwargs['uri'] = as_uri(args[0])
        print(json.dumps(kg.entity(**kwargs)))
    else:
        usage()
        sys.exit()
