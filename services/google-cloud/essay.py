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
from urllib.parse import quote

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from rdflib import ConjunctiveGraph as Graph
from pyld import jsonld

SPARQL_DIR = os.path.join(BASE_DIR, 'sparql')

DEFAULT_SITE = 'https://kg.jstor.org'

CUSTOM_MARKUP = {'entity', 'map', 'geojson', 'map-layer', 'video'}

def _is_empty(elem):
    child_images = [c for c in elem.children if c.name == 'img']
    if child_images:
        return False
    elem_contents = [t for t in elem.contents if t and (isinstance(t, str) and t.strip()) or t.name not in ('br',) and t.string and t.string.strip()]
    return len(elem_contents) == 0

def mw_to_html5(html):
    '''Transforms mediawiki generated HTML to semantic HTML'''
    _input = BeautifulSoup(html, 'html5lib')
    for elem in _input.find_all('span', {'class': 'mw-editsection'}):
        elem.decompose()
    for elem in _input.find_all(id='toc'):
        elem.decompose()
    base_html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title></title></head><body></body></html>'
    html5 = BeautifulSoup(base_html, 'html5lib')

    article = html5.new_tag('article', id='essay')
    article.attrs['data-app'] = 'true'
    html5.html.body.append(article)

    pnum = 0 # paragraph number within section
    root = _input.find('div', {'class': 'mw-parser-output'})
    sections = []
    for elem in root.find_all(recursive=False):
        if isinstance(elem, Tag):
            if elem.name[0] == 'h' and elem.name[1:].isdigit():
                headline = elem.find('span', {'class': 'mw-headline'})
                if not headline:
                    continue
                level = int(elem.name[1:])
                title = headline.string
                tag = html5.new_tag('section', id=headline.attrs['id'])
                head = html5.new_tag(f'h{level}')
                head.string = title
                tag.append(head)
                section = {
                    'id': headline.attrs['id'],
                    'level': level,
                    'parent': None,
                    'tag': tag
                }
                pnum = 0
                for s in sections[::-1]:
                    if s['level'] < section['level']:
                        section['parent'] = s['id']
                        break
                sections.append(section)
            else:
                parent = sections[-1]['tag'] if sections else article
                if elem.name == 'p' and not _is_empty(elem):
                    pnum += 1
                    # ensure non-empty paragraphs have an ID
                    if 'id' not in elem.attrs:
                        elem.attrs['id'] = f'{parent.attrs["id"]}-{pnum}'
                parent.append(elem)

    sections = dict([(s['id'], s) for s in sections])

    for section in sections.values():
        parent = sections[section['parent']]['tag'] if section['parent'] else article
        parent.append(section['tag'])

    return str(html5)

def md_to_html5(html):
    '''Transforms markdown generated HTML to semantic HTML'''
    # logger.info(html)
    _input = BeautifulSoup(f'<div id="md-content">{html}</div>', 'html5lib')

    base_html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title></title></head><body></body></html>'
    html5 = BeautifulSoup(base_html, 'html5lib')

    article = html5.new_tag('article', id='essay')
    article.attrs['data-app'] = 'true'
    html5.html.body.append(article)

    snum = 0 # section number
    pnum = 0 # paragraph number within section

    root = _input.find('div', {'id': 'md-content'})

    sections = []
    for elem in root.find_all(recursive=False):
        if isinstance(elem, Tag):
            if elem.name[0] == 'h' and elem.name[1:].isdigit():
                level = int(elem.name[1:])
                title = elem.string
                snum += 1
                section_id = f'section-{snum}'
                # logger.info(f'section: level={level} id={section_id} title="{title}')
                tag = html5.new_tag('section', id=section_id)
                head = html5.new_tag(f'h{level}')
                head.string = title
                tag.append(head)
                section = {
                    'id': section_id,
                    'level': level,
                    'parent': None,
                    'tag': tag
                }
                pnum = 0
                for s in sections[::-1]:
                    if s['level'] < section['level']:
                        section['parent'] = s['id']
                        break
                sections.append(section)
            else:
                parent = sections[-1]['tag'] if sections else article
                if elem.name == 'p' and not _is_empty(elem):
                    pnum += 1
                    # ensure non-empty paragraphs have an ID
                    if 'id' not in elem.attrs:
                        elem.attrs['id'] = f'{parent.attrs["id"]}-{pnum}'
                parent.append(elem)

    sections = dict([(s['id'], s) for s in sections])

    for section in sections.values():
        parent = sections[section['parent']]['tag'] if section['parent'] else article
        parent.append(section['tag'])

    return str(html5)


class Essay(object):

    def __init__(self, html, **kwargs):
        self.context = kwargs.pop('context', None)
        self._soup = BeautifulSoup(html, 'html5lib')
        for comment in self._soup(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        self.site = kwargs.get('site', DEFAULT_SITE)
        self.markup = self._find_ve_markup()
        self._update_entities_from_knowledgegraph()
        self._find_and_tag_items()
        self. _update_image_links()
        self._remove_empty_paragraphs()
        self._add_data()
        
    def _remove_empty_paragraphs(self):
        for para_elem in self._soup.findAll(lambda tag: tag.name in ('p',)):
            if _is_empty(para_elem):
                para_elem.extract()

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
            caption = thumb.div.div.text
            img_wrapper = self._soup.new_tag('div')
            img = self._soup.new_tag('img')
            img.attrs['src'] = f'{self.site}{thumb.div.a.img.attrs["src"]}'
            img.attrs['style'] = 'width: 100%; height: auto; border: 1px solid #ddd; box-shadow: 3px 3px 3px #eee;'
            caption_elem = self._soup.new_tag('p')
            caption_elem.attrs['style'] = 'text-align: center; margin-bottom: 18px; font-weight: 500;'
            caption_elem.string = caption
            img_wrapper.append(img)       
            img_wrapper.append(caption_elem)       
            thumb.replace_with(img_wrapper)
        #for img in self._soup.html.body.article.find_all('img'):
        #    img.attrs['src'] = f'{self.site}{img.attrs["src"]}'

    def _update_entities_from_knowledgegraph(self):
        qids = [item['qid'] for item in self.markup.values() if 'qid' in item]
        if qids:
            for kg_props in self._get_entity_data(qids)['@graph']:
                if kg_props['id'] in self.markup:
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
                        if k in ('aliases',) and k in self.markup[kg_props['id']]:
                            # merge values
                            v = sorted(set(self.markup[kg_props['id']][k] + v))
                        self.markup[kg_props['id']][k] = v
                    # logger.info(json.dumps(self.markup[kg_props['id']], indent=2))

    def _find_ve_markup(self):
        ve_markup = {}
        geojson_id_seq = 0

        # custom markup is defined in a var or span elements.  Custom properties are defined with element data-* attribute
        for vem_elem in [vem_elem for vem_tag in ('var', 'span') for vem_elem in self._soup.find_all(vem_tag)]:
            attrs = dict([k.replace('data-',''),v] for k,v in vem_elem.attrs.items() if k not in ['class'])
            matches = CUSTOM_MARKUP.intersection(set(attrs.keys()))
            if len(matches) == 1:
                _type = matches.pop()
            elif 'id' in attrs and is_qid(attrs['id']):
                if ':' not in attrs['id']:
                    attrs['id'] = f'wd:{attrs["id"]}'
                attrs['qid'] = attrs['id']
                _type = 'entity'
            else:
                continue

            if _type == 'entity':
                attrs['qid'] = attrs.pop('entity', attrs.pop('qid', None))
                if ':' not in attrs['qid']:
                    # ensure entity QIDs are namespaced. Use wikidata ('wd:') as default
                    attrs['qid'] = f'wd:{attrs["qid"]}'
                vem_elem.attrs['data-entity'] = attrs['qid']
                if 'scope' not in attrs:
                    attrs['scope'] = 'global'
                if 'aliases' in attrs:
                    attrs['aliases'] = [alias.strip() for alias in attrs['aliases'].split('|')]
            elif  _type == 'map':
                #logger.info(vem_elem)
                if 'center' in attrs:
                    if is_qid(attrs['center']):
                        attrs['center'] = self._qid_coords(attrs['center'])
                    else:
                        attrs['center'] = [float(c.strip()) for c in attrs['center'].replace(',', ' ').split()]
                if 'zoom' in attrs:
                    attrs['zoom'] = round(float(attrs['zoom']), 1)
                #logger.info(attrs)
            elif  _type == 'geojson':
                #if 'title' in attrs:
                #    attrs['label'] = attrs['title']
                if 'aliases' in attrs:
                    attrs['aliases'] = attrs['aliases'].split('|')
                geojson = self._get_geojson(attrs.pop('url'))
                attrs['geojson'] = geojson
                geojson_props = geojson['features'][0].get('properties', {}) if 'features' in geojson and len(geojson['features']) > 0 else geojson.get('properties', {})
                for attr, val in geojson_props.items():
                    if attr == 'aliases':
                        geojson_aliases = val.split('|') if isinstance(val, str) else val
                        attrs['aliases'] = sorted(set(geojson_aliases + attrs.get('aliases', [])))
                    else:
                        attrs[attr] = val
                if 'id' not in attrs:
                    geojson_id_seq += 1
                    attrs['id'] = f'geojson-{geojson_id_seq}'
                vem_elem['id'] = attrs['id']
                for attr in [f'data-{attr_suffix}' for attr_suffix in ('active', 'geojson', 'url')]:
                    if attr in vem_elem.attrs:
                        del vem_elem.attrs[attr]
            elif  _type == 'map-layer':
                if 'url' in attrs:
                    attrs['geojson'] = self._get_geojson(attrs.pop('url'))

            if 'id' not in attrs:
                attrs['id'] = attrs['qid'] if _type == 'entity' else f'{_type}-{sum([1 for item in ve_markup.values() if item["type"] == _type])+1}'
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
                if enclosing_element_id not in attrs['tagged_in']:
                    attrs['tagged_in'].append(enclosing_element_id)
                if _type in ('entity', 'geojson') and vem_elem.text:
                    vem_elem.attrs['class'] = [_type, 'tagged']
                    if _type == 'geojson':
                        attrs['scope' ] = 'element'
                else:
                    vem_elem.decompose()
            # logger.info(f'{attrs["id"]} {attrs["tagged_in"]}')

            ve_markup[attrs['id']] = attrs

        return ve_markup

    def add_stylesheet(self, **kwargs):
        if 'style' in kwargs:
            if not self._soup.html.head.style:
                self._soup.html.head.append(self._soup.new_tag('style'))
            self._soup.html.head.style.string = kwargs.pop('style')

    def _add_data(self):
        data = self._soup.new_tag('script')
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
        for item in [item for item in self.markup.values() if item['type'] in ('entity', 'geojson')]:
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

                    if item.get('scope') == 'global' or (item.get('scope') not in ('element',) and set(item['tagged_in']).intersection(context_set)):
                        # make tag for matched item
                        seg = self._soup.new_tag('span')
                        seg.string = rec['matched']
                        seg.attrs['id'] = item['id']
                        seg.attrs['title'] = item.get('title', item.get('label'))
                        seg.attrs['class'] = ['entity', 'inferred']
                        if 'qid' in item:
                            seg.attrs['data-entity'] = item['qid']
                        if 'found_in' not in item:
                            item['found_in'] = []
                        if context[0] not in item['found_in']:
                            item['found_in'].append(context[0])
                    else:
                        seg = s[cursor:cursor+len(rec['matched'])]

                    if replaced:
                        p.insert(idx+len(replaced), seg)
                    else:
                        e.parent.attrs['title'] = item.get('title', item.get('label'))
                    replaced.append(rec['matched'])
                    cursor += len(rec['matched'])

                if cursor < len(s):
                    seg = s[cursor:]
                    p.insert(idx+len(replaced), seg)
                    replaced.append(seg)
    
    def _qid_coords(self, qid):
        resp = requests.post(
            'https://query.wikidata.org/sparql',
            headers={
                'Accept': 'application/sparql-results+json',
                'Content-type': 'application/x-www-form-urlencoded'},
            data='query=%s' % quote(f'SELECT ?coords WHERE {{ wd:{qid.split(":")[-1]} wdt:P625 ?coords . }}')
        )
        if resp.status_code == 200:
            bindings = resp.json()['results']['bindings']
            if len(bindings) > 0:
                coords_str = bindings[0]['coords']['value']
                return [float(c.strip()) for c in coords_str.replace('Point(','').replace(')','').split()[::-1]]

    def _get_entity_data(self, qids):
        sparql = open(os.path.join(SPARQL_DIR, 'entities.rq'), 'r').read()
        sparql = sparql.replace('VALUES (?item) {}', f'VALUES (?item) {{ ({") (".join(qids)}) }}')
        context = json.loads(open(os.path.join(SPARQL_DIR, 'entities_context.json'), 'r').read())
        resp = requests.post(
            'https://query.wikidata.org/sparql',
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
            if '@graph' not in _jsonld:
                _context = _jsonld.pop('@context')
                _jsonld = {'@context': _context, '@graph': [_jsonld]}
            return _jsonld

    def _get_geojson(self, url):
        # logger.info(f'_get_geojson url={url}')
        return json.loads(requests.get(url).text)

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

    def __str__(self):
        return self.html

def is_qid(s, ns_required=True):
    if not s or not isinstance(s, str): return False
    eid = s.split(':')
    return len(eid[-1]) > 1 and eid[-1][0] == 'Q' and eid[-1][1:].isdecimal()

def add_vue_app(html, js_lib):
    soup = html if isinstance(html, BeautifulSoup) else BeautifulSoup(html, 'html5lib')

    for url in [
        'https://unpkg.com/leaflet@1.6.0/dist/leaflet.css',
        'https://cdnjs.cloudflare.com/ajax/libs/vuetify/2.1.12/vuetify.min.css'
        ]:
        style = soup.new_tag('link')
        style.attrs['rel'] = 'stylesheet'
        style.attrs['href'] = url
        soup.html.head.append(style)

    for url in [
            'https://unpkg.com/leaflet@1.6.0/dist/leaflet.js',
            js_lib
        ]:
        lib = soup.new_tag('script')
        lib.attrs['src'] = url
        soup.html.body.append(lib)

    return str(soup)

def usage():
    print(f'{sys.argv[0]} [hl:s:e:f:w] title')
    print(f'   -h --help          Print help message')
    print(f'   -l --loglevel      Logging level (default=warning)')
    print(f'   -s --site          Baseurl for source text (default="{DEFAULT_SITE}")')
    print(f'   -e --language      Language (default="en")')
    print(f'   -f --format        Format (json, html) (default=json)')
    print(f'   -w --wikitext      Return wikitext')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:s:e:f:w', ['help', 'loglevel', 'site', 'language', 'format', 'wikitext'])
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
        elif o in ('-w', '--wikitext'):
            kwargs['wikitext'] = True
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