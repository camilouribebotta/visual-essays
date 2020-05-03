#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()

import os
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'content')

import json
import getopt
import sys
import hashlib
from urllib.parse import quote
from time import time as now

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from slugify import slugify

from rdflib import ConjunctiveGraph as Graph
from pyld import jsonld

SPARQL_DIR = os.path.join(BASE_DIR, 'sparql')

DEFAULT_SITE = 'https://kg.jstor.org'

CUSTOM_MARKUP = {'config', 'component', 'image-viewer', 'image', 'essay', 'entity', 'map', 'geojson', 'map-layer', 'video', 'primary', 'specimens'}

def _is_empty(elem):
    child_images = [c for c in elem.children if c.name == 'img']
    if child_images:
        return False
    elem_contents = [t for t in elem.contents if t and (isinstance(t, str) and t.strip()) or t.name not in ('br',) and t.string and t.string.strip()]
    return len(elem_contents) == 0

class Essay(object):

    def __init__(self, html, **kwargs):
        st = now()
        self.cache = kwargs.get('cache', {})
        self.context = kwargs.pop('context', None)
        self.site = kwargs.get('site', DEFAULT_SITE)
        self._soup = BeautifulSoup(html, 'html5lib')
        for comment in self._soup(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        self.markup = self._find_ve_markup()
        logger.info(f'{round(now()-st,3)}: phase 1')
        st = now()
        self._update_entities_from_knowledgegraph(refresh=False)
        logger.info(f'{round(now()-st,3)}: phase 2')
        st = now()        
        self._find_and_tag_items()
        self.add_entity_classes()
        self. _update_image_links()
        self._remove_empty_paragraphs()
        self._add_heading_ids()
        self._add_data()
        logger.info(f'{round(now()-st,3)}: phase 3')

    def _remove_empty_paragraphs(self):
        for link in self._soup.findAll(lambda tag: tag.name in ('a',)):
            if 'plant-humanities.app' in link.attrs['href'] and 'gdid' in link.attrs['href']:
                link.extract()
        for para_elem in self._soup.findAll(lambda tag: tag.name in ('p',)):
            if _is_empty(para_elem):
                para_elem.extract()

    def _add_heading_ids(self):
        for lvl in range(1, 9):
            for heading in self._soup.findAll(lambda tag: tag.name in ('h%s' % lvl,)):
                if 'id' not in heading.attrs:
                    heading.attrs['id'] = slugify(heading.text)

    def _enclosing_section(self, elem):
        parent_section = None
        while elem.parent and parent_section is None:
            if elem.name == 'section' or elem.attrs.get('id') == 'essay':
                parent_section = elem
                break
            elem = elem.parent
        #logger.info(f'_enclosing_section: elem={elem} parent_section={parent_section}')
        return parent_section

    def _enclosing_sections(self, elem, id):
        sections = []
        while elem:
            # logger.info(f'{id} {elem.name}')
            if elem.attrs and elem.attrs.get('id'):
                sections.append(elem.attrs['id'])
            elem = elem.parent
        return sections

    def _enclosing_section_id(self, elem, default=None):
        _enclosing_section = self._enclosing_section(elem)
        return _enclosing_section.attrs['id'] if _enclosing_section and 'id' in _enclosing_section.attrs else default

    def _update_image_links(self):
        for thumb in self._soup.html.body.article.find_all('div', {'class': 'thumb'}):
            thumb.div.a.img.attrs["src"] = f'{self.site}{thumb.div.a.img.attrs["src"]}'
            '''
            logger.info(thumb)
            caption = thumb.div.div.text
            img_wrapper = self._soup.new_tag('div')
            img = self._soup.new_tag('img')
            img.attrs['src'] = f'{self.site}{thumb.div.a.img.attrs["src"]}'
            img.attrs['style'] = 'width: 300px; height: auto; border: 1px solid #ddd; box-shadow: 3px 3px 3px #eee;'
            caption_elem = self._soup.new_tag('p')
            caption_elem.attrs['style'] = 'text-align: center; margin-bottom: 18px; font-weight: 500;'
            caption_elem.string = caption
            img_wrapper.append(img)       
            img_wrapper.append(caption_elem)       
            thumb.replace_with(img_wrapper)
            '''
        #for img in self._soup.html.body.article.find_all('img'):
        #    img.attrs['src'] = f'{self.site}{img.attrs["src"]}'

    def _update_entities_from_knowledgegraph(self, refresh=False):
        qids = [item['qid'] for item in self.markup.values() if 'qid' in item]
        if qids:
            cache_key = hashlib.sha256(str(sorted(qids)).encode('utf-8')).hexdigest()
            kg_entities = self.cache.get(cache_key) if not refresh else None
            from_cache = kg_entities is not None
            if kg_entities is None:
                kg_entities = self._get_entity_data(qids)['@graph']
                self.cache[cache_key] = kg_entities
            # logger.info(json.dumps(kg_entities, indent=2))
            for entity in kg_entities:
                if 'whos_on_first_id' in entity:
                    wof = entity.pop('whos_on_first_id')
                    wof_parts = [wof[i:i+3] for i in range(0, len(wof), 3)]
                    entity['geojson'] = f'https://data.whosonfirst.org/{"/".join(wof_parts)}/{wof}.geojson'
            for kg_props in kg_entities:
                if kg_props['id'] in self.markup:
                    me = self.markup[kg_props['id']]
                    me['fromCache'] = from_cache
                    for k, v in kg_props.items():
                        if k in ('aliases',) and not isinstance(v, list):
                            v = [v]
                        elif k == 'qid' and ':' not in kg_props[k]:
                            v = f'wd:{kg_props[k]}'
                        elif k == 'coords':
                            coords = []
                            for coords_str in v:
                                coords.append([float(c.strip()) for c in coords_str.replace('Point(','').replace(')','').split()[::-1]])
                            v = coords
                        elif k == 'category':
                            if 'category' in me:
                                v = me['category']
                        if k in ('aliases',) and k in self.markup[kg_props['id']]:
                            # merge values
                            v = sorted(set(self.markup[kg_props['id']][k] + v))
                        me[k] = v
                    # logger.info(json.dumps(self.markup[kg_props['id']], indent=2))

    def add_entity_classes(self):
        for entity in [vem_elem for vem_tag in ('var', 'span') for vem_elem in self._soup.find_all(vem_tag, {'class': 'entity'})]:
            if 'category' in self.markup.get(entity.attrs.get('data-itemid'), {}):
                entity.attrs['class'] = sorted(set([cls for cls in entity.attrs['class'] if cls != 'entity'] + [self.markup[entity.attrs['data-itemid']]['category']]))

    def _find_ve_markup(self):
        ve_markup = {}

        # custom markup is defined in a var or span elements.  Custom properties are defined with element data-* attribute
        for vem_elem in [vem_elem for vem_tag in ('var', 'span', 'param') for vem_elem in self._soup.find_all(vem_tag)]:
            attrs = dict([k.replace('data-',''),v] for k,v in vem_elem.attrs.items() if k not in ['class']) if vem_elem.attrs else {}
            matches = CUSTOM_MARKUP.intersection(set(attrs.keys()))
            if len(matches) == 1:
                _type = matches.pop()
            elif ('id' in attrs and is_qid(attrs['id'])) or ('qid' in attrs and is_qid(attrs['qid'])):
                _type = 'entity'
                qid = attrs.pop('qid', attrs.pop('id', None))
                ns, qid = qid.split(':') if ':' in qid else ('wd', qid)
                attrs['id'] = f'{ns}:{qid}'
                attrs['qid'] = f'{ns}:{qid}'
            else:
                continue
            for k in sorted(attrs.keys()):
                if not attrs[k]:
                    del attrs[k]

            if 'id' not in attrs:
                attrs['id'] = f'{_type}-{sum([1 for item in ve_markup.values() if item["type"] == _type])+1}'

            if _type == 'entity':
                if 'scope' not in attrs:
                    attrs['scope'] = 'global'
                if 'aliases' in attrs:
                    attrs['aliases'] = [alias.strip() for alias in attrs['aliases'].split('|')]

            elif  _type == 'map':
                if 'center' in attrs:
                    if is_qid(attrs['center']):
                        attrs['center'] = self._qid_coords(attrs['center'])
                    else:
                        attrs['center'] = [float(c.strip()) for c in attrs['center'].replace(',', ' ').split()]
                if 'zoom' in attrs:
                    attrs['zoom'] = round(float(attrs['zoom']), 1)

            elif  _type == 'map-layer':
                if 'aliases' in attrs:
                    attrs['aliases'] = attrs['aliases'].split('|')
                for attr in [f'data-{attr_suffix}' for attr_suffix in ('active', 'geojson', 'url')]:
                    if attr in vem_elem.attrs:
                        del vem_elem.attrs[attr]

            elif  _type == 'image':
                if 'region' in attrs:
                    attrs['region'] = [int(c.strip()) for c in attrs['region'].split(',')]
            
            if attrs['id'] in ve_markup:
                attrs = ve_markup[attrs['id']]
            else:
                attrs['type'] = _type
                attrs['tagged_in'] = []

            # add id of enclosing element to entities 'tagged_in' attribute
            if vem_elem.parent.name == 'p': # enclosing element is a paragraph
                if 'id' in vem_elem.parent.attrs and not _is_empty(vem_elem.parent):
                    enclosing_element_id = vem_elem.parent.attrs['id']
                else:
                    enclosing_element_id = self._enclosing_section_id(vem_elem, self._soup.html.body.article.attrs['id'])
                if enclosing_element_id not in attrs['tagged_in'] and attrs.get('scope') != 'element':
                    attrs['tagged_in'].append(enclosing_element_id)
                if _type in ('entity', 'geojson') and vem_elem.text:
                    vem_elem.attrs['data-itemid'] = attrs['id']
                    vem_elem.attrs['class'] = [_type, 'tagged']
                    if _type == 'geojson':
                        attrs['scope'] = 'element'
                else:
                    vem_elem.decompose()
            # logger.info(f'{attrs["id"]} {attrs["tagged_in"]}')

            ve_markup[attrs['id']] = attrs
        # logger.info(json.dumps(ve_markup, indent=2))
        return ve_markup

    def add_stylesheet(self, **kwargs):
        if 'style' in kwargs:
            if not self._soup.html.head.style:
                self._soup.html.head.append(self._soup.new_tag('style'))
            self._soup.html.head.style.string = kwargs.pop('style')

    def _add_data(self):
        data = self._soup.new_tag('script')
        # logger.info(json.dumps([self.markup[_id] for _id in sorted(self.markup)], indent=2) + '\n')
        if self.context is not None:
            data.append(f'\nwindow.context = "{self.context}"')
        data.attrs['type'] = 'application/ld+json'
        data.append('\nwindow.data = ' + json.dumps([self.markup[_id] for _id in sorted(self.markup)], indent=2) + '\n')
        self._soup.html.body.article.append(data)

    def _ids_for_elem(self, elem):
        section_ids = []
        while elem:
            if elem.name in('p', 'section', 'article') and 'id' in elem.attrs:
                section_ids.append(elem.attrs['id'])
            elem = elem.parent
        return section_ids

    def _find_and_tag_items(self):
        def tm_regex(s):
            return r'(^|\W)(%s)($|\W|[,:;])' % re.escape(s.lower())

        def tag_visible(element):
            '''Returns true if text element is visible and not a comment.'''
            if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                return False
            if isinstance(element, Comment):
                return False
            return True

        to_match = {}
        for item in [item for item in self.markup.values() if item['type'] in ('entity', 'map-layer')]:
            if 'label' in item:
                to_match[tm_regex(item['label'])] = {'str': item['label'], 'item': item}
            if item.get('aliases'):
                for alias in item['aliases']:
                    to_match[tm_regex(alias)] = {'str': alias, 'item': item}

        for e in [e for e in filter(tag_visible, self._soup.findAll(text=True)) if e.strip() != '']:
            context = self._ids_for_elem(e)
            context_set = set(context)
            snorm = e.string.lower()
            matches = []
            tagged = set()
            for tm in sorted(to_match.keys(), key=len, reverse=True):
                item = to_match[tm]['item']
                try:
                    for m in re.finditer(tm, snorm):
                        matched = m[2]
                        start = m.start(2)
                        end = start + len(matched)
                        logger.debug(f'{item.get("label")} "{tm}" "{e[start:end]}" {start}')
                        overlaps = False
                        for match in matches:
                            mstart = match['idx']
                            mend = mstart + len(match['matched'])
                            if (start >= mstart and start <= mend) or (end >= mstart and end <= mend):
                                logger.debug(f'{tm} overlaps with {match["matched"]} {match["idx"]}')
                                overlaps = True
                                break
                        if not overlaps:
                            _m = {'idx': start, 'matched': e.string[start:end], 'item': to_match[tm]['item']}
                            matches.append(_m)

                except:
                    raise
            matches.sort(key=lambda x: x['idx'], reverse=False)
            logger.debug(json.dumps([{'idx': m['idx'], 'matched': m['matched']} for m in matches], indent=2))
            if matches:
                p = e.parent
                s = e.string
                for idx, child in enumerate(p.children):
                    if child == e:
                        break

                cursor = None
                replaced = []
                for rec in matches:
                    m = rec['idx']
                    item = rec['item']
                    if not cursor or m > cursor:
                        seg = s[cursor:m]
                        if replaced:
                            p.insert(idx+len(replaced), seg)
                        else:
                            e.replace_with(seg)
                        replaced.append(seg)
                        cursor = m

                    logger.debug(f'{rec["matched"]} tagged_in={item["tagged_in"]} scope={item.get("scope")} context={context} in_scope={len(set(item["tagged_in"]).intersection(context_set)) > 0}')

                    if item['id'] not in tagged and (item.get('scope') == 'global' or (item.get('scope') not in ('element',) and set(item['tagged_in']).intersection(context_set))):
                        # make tag for matched item
                        seg = self._soup.new_tag('span')
                        seg.string = rec['matched']
                        seg.attrs['title'] = item.get('title', item.get('label'))
                        seg.attrs['class'] = ['entity', 'inferred']
                        if 'category' in item:
                            seg.attrs['class'].append(item['category'])
                        seg.attrs['data-itemid'] = item['id']
                        if 'found_in' not in item:
                            item['found_in'] = []
                        if context[0] not in item['found_in']:
                            item['found_in'].append(context[0])
                        tagged.add(item['id'])
                    else:
                        seg = s[cursor:cursor+len(rec['matched'])]

                    if replaced:
                        p.insert(idx+len(replaced), seg if p.name in ('p', 'em', 'strong') else rec['matched'])
                    else:
                        e.parent.attrs['title'] = item.get('title', item.get('label'))
                    replaced.append(rec['matched'])
                    cursor += len(rec['matched'])

                if cursor < len(s):
                    seg = s[cursor:]
                    p.insert(idx+len(replaced), seg)
                    replaced.append(seg)
    
    def _qid_coords(self, qid):
        cache_key = '%s-coords' % (qid)
        coords = self.cache.get(cache_key)
        if not coords:
            sparql = f'SELECT ?coords WHERE {{ wd:{qid.split(":")[-1]} wdt:P625 ?coords . }}'
            for _ in range(3):
                resp = requests.post(
                    'https://query.wikidata.org/sparql',
                    headers={
                        'Accept': 'application/sparql-results+json',
                        'Content-type': 'application/x-www-form-urlencoded',
                        'User-agent': 'JSTOR Labs python client'},
                    data='query=%s' % quote(sparql)
                )
                if resp.status_code == 200:
                    bindings = resp.json()['results']['bindings']
                    if len(bindings) > 0:
                        coords_str = bindings[0]['coords']['value']
                        coords = [float(c.strip()) for c in coords_str.replace('Point(','').replace(')','').split()[::-1]]
                        self.cache[cache_key] = coords
        return coords

    def _get_entity_data(self, qids):
        sparql = open(os.path.join(SPARQL_DIR, 'entities.rq'), 'r').read()
        sparql = sparql.replace('VALUES (?item) {}', f'VALUES (?item) {{ ({") (".join(qids)}) }}')
        context = json.loads(open(os.path.join(SPARQL_DIR, 'entities_context.json'), 'r').read())
        for _ in range(3):
            resp = requests.post(
                'https://query.wikidata.org/sparql',
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
                return _jsonld
            logger.info(f'_get_entity_data: resp_code={resp.status_code} msg=${resp.text}')

    def _get_geojson(self, url):
        logger.info(f'_get_geojson url={url}')
        cache_key = hashlib.sha256(url.encode('utf-8')).hexdigest()
        geojson = self.cache.get(cache_key)
        if not geojson:
            geojson = json.loads(requests.get(url).text)
            if geojson:
                self.cache[cache_key] = geojson
        return geojson

    @property
    def json(self):
        return {
            'html': str(self._soup),
            'markup': [self.markup[k] for k in sorted(self.markup)]
        }

    def __repr__(self):
        return json.dumps(self.json, sort_keys=True)

    @property
    def html(self):
        #return self._soup.prettify()
        return str(self._soup)

    @property
    def soup(self):
        return self._soup

    def __str__(self):
        return self.html

def is_qid(s, ns_required=True):
    if not s or not isinstance(s, str): return False
    eid = s.split(':')
    return len(eid[-1]) > 1 and eid[-1][0] == 'Q' and eid[-1][1:].isdecimal()

def usage():
    print(f'{sys.argv[0]} [hl:s:e:f:] title')
    print(f'   -h --help          Print help message')
    print(f'   -l --loglevel      Logging level (default=warning)')
    print(f'   -s --site          Baseurl for source text (default="{DEFAULT_SITE}")')
    print(f'   -e --language      Language (default="en")')
    print(f'   -f --format        Format (json, html) (default=json)')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:s:e:f:w', ['help', 'loglevel', 'site', 'language', 'format'])
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
        elif o in ('-s', '--site'):
            kwargs['site'] = a
        elif o in ('-e', '--language'):
            kwargs['language'] = a
        elif o in ('-f', '--format'):
            kwargs['content_type'] = 'text/html' if a == 'html' else 'application/json'
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    client = Essay(**kwargs)

    if args:
        title = args[0]
        page_data = client.page(title, **kwargs)
        mw_html = page_data['text']['*']
        essay = Essay(mw_to_html5(mw_html))
        #print(json.dumps([entity.json() for entity in essay.entities.values()]))
        print(essay.html)