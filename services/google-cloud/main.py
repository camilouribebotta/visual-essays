#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.append(SCRIPT_DIR)
logger.info(f'')
import json
import traceback

import markdown2
from bs4 import BeautifulSoup
from bs4.element import Tag

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from flask import Flask, request
app = Flask(__name__)

from essay import Essay
from entity import KnowledgeGraph
from fingerprints import get_fingerprints

from gc_cache import Cache
cache = Cache()

VE_JS_LIB = 'https://jstor-labs.github.io/visual-essays/lib/visual-essays-0.4.5.min.js'

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': True
}

def get_gh_markdown(user, repo, file=None):
    files = ['index.md', 'home.md', 'README.md'] if file is None else [file if file.endswith('.md') else f'{file}.md']
    for file in files:
        resp = requests.get(f'https://raw.githubusercontent.com/{user}/{repo}/master/{file}')
        if resp.status_code == 200:
            return {'fname': file.replace('.md', ''), 'text': resp.text}

def get_local_markdown(file=None):
    files = ['index.md', 'home.md', 'README.md'] if file is None else [file if file.endswith('.md') else f'{file}.md']
    for file in files:
        path = os.path.join(BASEDIR, file)
        if os.path.exists(path):
            with open(path, 'r') as fp:
                return {'fname': file.replace('.md', ''), 'text': fp.read()}

def convert_relative_links(soup, baseUrl):
    for tag in ('img', 'var', 'a', 'span'):
        for elem in soup.find_all(tag):
            for attr in ('data-banner', 'src', 'url', 'href'):
                if attr in elem.attrs and not elem.attrs[attr].startswith('http'):
                    elem.attrs[attr] = f'{baseUrl}{elem.attrs[attr]}'

def _is_empty(elem):
    child_images = [c for c in elem.children if c.name == 'img']
    if child_images:
        return False
    elem_contents = [t for t in elem.contents if t and (isinstance(t, str) and t.strip()) or t.name not in ('br',) and t.string and t.string.strip()]
    return len(elem_contents) == 0

def markdown_to_html5(markdown, baseUrl):
    '''Transforms markdown generated HTML to semantic HTML'''
    html = markdown2.markdown(markdown['text'], extras=['footnotes', 'fenced-code-blocks'])

    soup = BeautifulSoup(f'<div id="md-content">{html}</div>', 'html5lib')
    convert_relative_links(soup, baseUrl)

    base_html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title></title></head><body></body></html>'
    html5 = BeautifulSoup(base_html, 'html5lib')

    article = html5.new_tag('article', id='essay')
    article.attrs['data-app'] = 'true'
    article.attrs['data-name'] = markdown['fname']
    html5.html.body.append(article)

    snum = 0 # section number
    pnum = 0 # paragraph number within section

    root = soup.find('div', {'id': 'md-content'})

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

    # return html5.prettify()
    return str(html5)

def add_vue_app(html, js_lib):
    soup = html if isinstance(html, BeautifulSoup) else BeautifulSoup(html, 'html5lib')

    for url in [
            'https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900',
            'https://cdn.jsdelivr.net/npm/@mdi/font@4.x/css/materialdesignicons.min.css',
            'https://unpkg.com/leaflet@1.6.0/dist/leaflet.css',
        ]:
        style = soup.new_tag('link')
        style.attrs['rel'] = 'stylesheet'
        style.attrs['href'] = url
        soup.html.head.append(style)

    for url in [
            js_lib
        ]:
        lib = soup.new_tag('script')
        lib.attrs['src'] = url
        soup.html.body.append(lib)

    return str(soup)

def _set_logging_level(args):
    if 'log' in args:
        level = args.pop('log').lower()
        if level == 'debug':
            logger.setLevel(logging.DEBUG)
        elif level == 'info':
            logger.setLevel(logging.INFO)

@app.route('/entity/<qid>', methods=['GET'])
def entity(qid):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        args = dict([(k, request.args.get(k)) for k in request.args])
        _set_logging_level(args)
        logger.info(f'entity: qid={qid} args={args}')
        entity = KnowledgeGraph(cache=cache, **args).entity(qid, **args)
        return (entity, 200, cors_headers)

@app.route('/fingerprints', methods=['GET'])
def fingerprints(*args, **kwargs):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        args = dict([(k, request.args.get(k)) for k in request.args])
        _set_logging_level(args)
        logger.info(f'fingerprints: args={args}')
        if 'qids' in args:
            qids = set()
            for qid in args['qids'].split(','):
                # ensure qids are namespaced
                ns, qid = qid.split(':') if ':' in qid else ('wd', qid)
                qids.add(f'{ns.strip()}:{qid.strip()}')
        fingerprints = get_fingerprints(qids, args.get('language', 'en'))
        logger.info(fingerprints)
        return (fingerprints, 200, cors_headers)


@app.route('/<user>/<repo>', methods=['GET'])
@app.route('/<user>/<repo>/<file>', methods=['GET'])
def essay(user, repo, file=None):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        baseUrl = f'https://raw.githubusercontent.com/{user}/{repo}/master'
        markdown = get_gh_markdown(user, repo, file)
        if markdown:
            essay = Essay(html=markdown_to_html5(markdown, baseUrl), cache=cache, **request.args)
            return (add_vue_app(essay.soup, VE_JS_LIB), 200, cors_headers)
        else:
            return 'Not found', 404

@app.route('/<file>', methods=['GET'])
@app.route('/', methods=['GET'])
def local_essay(file=None):
    baseUrl = 'http://localhost:5000'
    markdown = get_local_markdown(file)
    if markdown:
        essay = Essay(html=markdown_to_html5(markdown, baseUrl), cache=cache, **request.args)
        return (add_vue_app(essay.soup, VE_JS_LIB), 200, cors_headers)
    else:
        return 'Not found', 404

if __name__ == '__main__':
    VE_JS_LIB = 'http://localhost:8080/lib/visual-essays.js'
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
