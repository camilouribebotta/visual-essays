#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
import re
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
BASEDIR = os.path.dirname(SCRIPT_DIR)
DOCS_ROOT = os.path.dirname(BASEDIR)
logger.warning(DOCS_ROOT)
sys.path.append(SCRIPT_DIR)

import json
import traceback
import getopt
from urllib.parse import urlparse

import markdown as markdown_parser

from bs4 import BeautifulSoup
from bs4.element import Tag

import requests
logging.getLogger('requests').setLevel(logging.INFO)

from flask import Flask, request, send_from_directory, redirect

app = Flask(__name__)

from essay import Essay
from entity import KnowledgeGraph, as_uri
from fingerprints import get_fingerprints
from specimens import get_specimens

from gc_cache import Cache
cache = Cache()

VE_JS_LIB = 'https://jstor-labs.github.io/visual-essays/lib/visual-essays.min.js'
ENV = 'prod'
DEFAULT_ACCT = None
DEFAULT_REPO = None

KNOWN_SITES = {
    'localhost': {'acct': 'jstor-labs', 'repo': 'visual-essays'},
    'visual-essays.app': {'acct': 'jstor-labs', 'repo': 'visual-essays'},
    'plant-humanities.app': {'acct': 'jstor-labs', 'repo': 'plant-humanities'},
    'dickens.kent-maps.online': {'acct': 'kent-map', 'repo': 'dickens'},
    'kent-maps.online': {'acct': 'kent-map', 'repo': 'dickens'}
}

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': True
}

def content_baseurl(acct, repo):
    return f'https://{acct}.github.io/{repo}{"/content" if repo == "plant-humanities" else ""}'

def get_markdown(url):
    resp = requests.get(url)
    logger.debug(f'{url} {resp.status_code}')
    if resp.status_code == 200:
        return {'source': 'url', 'fname': url.split('/')[-1].replace('.md', ''), 'text': resp.content.decode('utf-8')}

def get_gh_markdown(acct, repo, file=None):
    baseurl = content_baseurl(acct, repo)
    logger.debug(f'get_gh_markdown: acct={acct} repo={repo} baseurl={baseurl}')
    files = ['index.md', 'home.md', 'README.md'] if file is None else [file if file.endswith('.md') else f'{file}.md']
    for file in files:
        url = f'{baseurl}/{file}'
        resp = requests.get(url)
        logger.debug(f'{url} {resp.status_code}')
        if resp.status_code == 200:
            return {'source': 'gh', 'fname': file.replace('.md', ''), 'text': resp.content.decode('utf-8')}

def get_gd_markdown(gdid):
    url = f'https://drive.google.com/uc?export=download&id={gdid}'
    resp = requests.get(url)
    logger.debug(f'{url} {resp.status_code}')
    if resp.status_code == 200:
        return {'source': 'gdid', 'fname': gdid, 'text': resp.content.decode('utf-8')}

def get_local_markdown(file=None):
    logger.debug(f'get_local_markdown: file={file}')
    files = ['index.md', 'home.md', 'README.md'] if file is None else [file if file.endswith('.md') else f'{file}.md']
    for file in files:
        path = f'{DOCS_ROOT}/docs/{file}'
        logger.debug(f'path={path}')
        if os.path.exists(path):
            with open(path, 'r') as fp:
                return {'source': 'local', 'fname': file.replace('.md', ''), 'text': fp.read()}

def convert_relative_links(soup, acct=None, repo=None, fname=None, source=None, site=None):
    logger.info(f'convert_relative_links: acct={acct} repo={repo} site={site}')
    if site == 'localhost':
        baseurl = 'http://localhost:5000/essay'
        if acct:
            baseurl += f'/{acct}/{repo}'
    else:
        baseurl = None
        for site, site_data in KNOWN_SITES.items():
            if site_data['acct'] == acct and site_data['repo'] == repo and site != 'localhost':
                baseurl = f'http{"" if site == "localhost" else "s"}://{site}/essay'
                break
        if baseurl is None:
            baseurl = f'https://visual-essays.app/essay/{acct}/{repo}' 

    for tag in ('a',):
        for elem in soup.find_all(tag):
            for attr in ('href',):
                if attr in elem.attrs and not elem.attrs[attr].startswith('http'):
                    if elem.attrs[attr].startswith('#'):
                        elem.attrs[attr] = f'{fname}{elem.attrs[attr]}'
                    elem.attrs[attr] = f'{baseurl}/{elem.attrs[attr][1:] if elem.attrs[attr][0] == "/" else elem.attrs[attr]}'
    
    if source == 'local':
        baseurl = 'http://localhost:5000'
    else:
        baseurl = content_baseurl(acct, repo)
    logger.info(f'convert_relative_image_links: source={source} baseurl={baseurl}')
    for tag in ('img', 'var', 'span', 'param'):
        for elem in soup.find_all(tag):
            for attr in ('banner', 'data-banner', 'src', 'url'):
                if attr in elem.attrs and elem.attrs[attr] and not elem.attrs[attr].startswith('http'):
                    elem.attrs[attr] = f'{baseurl}/{elem.attrs[attr][1:] if elem.attrs[attr][0] == "/" else elem.attrs[attr]}'
                    if repo == 'plant-humanities':
                        elem.attrs[attr] = elem.attrs[attr].replace('/content/geojson', '/geojson')

def _is_empty(elem):
    child_images = [c for c in elem.children if c.name == 'img']
    if child_images:
        return False
    elem_contents = [t for t in elem.contents if t and (isinstance(t, str) and t.strip()) or t.name not in ('br',) and t.string and t.string.strip()]
    return len(elem_contents) == 0

def markdown_to_html5(markdown, acct=None, repo=None, site=None):
    logger.debug(f'markdown_to_html5: acct={acct} repo={repo} site={site}')
    '''Transforms markdown generated HTML to semantic HTML'''
    # html = markdown2.markdown(markdown['text'], extras=['footnotes', 'fenced-code-blocks'])
    html = markdown_parser.markdown(
        markdown['text'],
        output_format='html5', 
        extensions=['footnotes', 'pymdownx.superfences', 'pymdownx.details', 'attr_list'],
        extension_configs = {
            'footnotes': {
                'SEPARATOR': '-'
            }
        })
    soup = BeautifulSoup(f'<div id="md-content">{html}</div>', 'html5lib')
    convert_relative_links(soup, acct, repo, markdown['fname'], markdown['source'], site)

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
                head.attrs = elem.attrs
                head.string = title if title else ''
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

    # print(html5.prettify())
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
            'https://unpkg.com/mirador@beta/dist/mirador.min.js',
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

@app.route('/entity/<path:eid>', methods=['GET'])  
@app.route('/entity', methods=['GET'])  
def entity(eid=None):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    site = urlparse(request.base_url).hostname
    logger.info(f'DEFAULT_ACCT={DEFAULT_ACCT} DEFAULT_REPO={DEFAULT_REPO}')
    kwargs['acct'] = DEFAULT_ACCT if DEFAULT_ACCT else KNOWN_SITES.get(site, {}).get('acct')
    kwargs['repo'] = DEFAULT_REPO if DEFAULT_REPO else KNOWN_SITES.get(site, {}).get('repo')
    # kwargs['refresh'] = kwargs['refresh'] == 'true' if 'refresh' in kwargs else kwargs.pop('mode', ENV) == 'dev'
    kwargs['refresh'] = True
    logger.info(f'entity: eid={eid} kwargs={kwargs}')
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        if eid:
            kwargs['uri'] = as_uri(eid, **kwargs)
        entity = KnowledgeGraph(cache=cache, **kwargs).entity(**kwargs)
        return (entity, 200, cors_headers)

@app.route('/specimens/<taxon_name>', methods=['GET'])  
def specimens(taxon_name):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    accept = request.headers.get('Accept', 'application/json').split(',')
    content_type = ([ct for ct in accept if ct in ('text/html', 'application/json', 'text/csv', 'text/tsv')] + ['application/json'])[0]
    _set_logging_level(kwargs)
    logger.info(f'specimens: taxon_name={taxon_name} kwargs={kwargs}')
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        taxon_name = taxon_name.replace('_', ' ')
        # refresh = kwargs.pop('refresh', 'false').lower() in ('true', '')
        refresh = True
        specimens = cache.get(taxon_name) if not refresh else None
        if specimens is None:
            specimens = get_specimens(taxon_name, **kwargs)
            if specimens['specimens']:
                cache[taxon_name] = specimens
        else:
            specimens['from_cache'] = True
        if content_type == 'text/html':
            return (open(os.path.join(BASEDIR, 'src', 'json-viewer.html'), 'r').read().replace("'{{DATA}}'", json.dumps(specimens)), 200, cors_headers)
        else:
            return (specimens, 200, cors_headers)

@app.route('/fingerprints', methods=['GET'])  
def fingerprints():
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        logger.info(f'fingerprints: kwargs={kwargs}')
        if 'qids' in kwargs:
            qids = set()
            for qid in kwargs['qids'].split(','):
                # ensure qids are namespaced
                ns, qid = qid.split(':') if ':' in qid else ('wd', qid)
                qids.add(f'{ns.strip()}:{qid.strip()}')
        fingerprints = get_fingerprints(qids, kwargs.get('language', 'en'))
        return (fingerprints, 200, cors_headers)

@app.route('/local/<file>', methods=['GET'])  
@app.route('/local', methods=['GET'])  
def essay_local(file=None):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    logger.info(f'essay_local: file={file} kwargs={kwargs}')
    _set_logging_level(kwargs)    

    # baseUrl = 'http://localhost:5000'
    markdown = get_local_markdown(file)
    if markdown:
        essay = Essay(html=markdown_to_html5(markdown), cache=cache, **kwargs)
        return (add_vue_app(essay.soup, VE_JS_LIB), 200, cors_headers)
    else:
        return 'Not found', 404

@app.route('/essay/<acct>/<repo>/<file>', methods=['GET'])  
@app.route('/essay/<acct>/<repo>', methods=['GET'])
@app.route('/essay/<file>', methods=['GET'])  
@app.route('/essay', methods=['GET'])  
def essay(acct=None, repo=None, file=None):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    logger.info('essay')
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        raw = kwargs.pop('raw', 'false') in ('', 'true')
        site = urlparse(request.base_url).hostname
        acct = acct if acct else DEFAULT_ACCT if DEFAULT_ACCT else KNOWN_SITES.get(site, {}).get('acct')
        repo = repo if repo else DEFAULT_REPO if DEFAULT_REPO else KNOWN_SITES.get(site, {}).get('repo')
        src = None
        gdid = None
        for arg in ('src', 'gd', 'gdid', 'gdrive'):
            if arg in kwargs:
                val = kwargs.pop(arg)
                if val.startswith('https://drive.google.com'):
                    gdid = val.split('/')[5]
                elif arg == 'src':
                    src = val
                else:
                    gdid = val
        baseurl = None
        if src:
            markdown = get_markdown(src)
        elif gdid:
            markdown = get_gd_markdown(gdid)
        else:
            use_local = kwargs.pop('mode', ENV) == 'dev'
            if use_local:
                markdown = get_local_markdown(file)
                baseurl = 'http://localhost:5000'
            else:
                markdown = get_gh_markdown(acct, repo, file)
                baseurl = content_baseurl(acct, repo)
        logger.info(f'essay: site={site} acct={acct} repo={repo} file={file} raw={raw} kwargs={kwargs}')
        if markdown:
            if raw:
                return (markdown['text'], 200, cors_headers)
            else:
                essay = Essay(html=markdown_to_html5(markdown, acct, repo, site), cache=cache, baseurl=baseurl, **kwargs)
                return (add_vue_app(essay.soup, VE_JS_LIB), 200, cors_headers)
        else:
            return 'Not found', 404

@app.route('/markdown-viewer/<acct>/<repo>/<file>', methods=['GET'])  
@app.route('/markdown-viewer/<acct>/<repo>', methods=['GET'])
@app.route('/markdown-viewer/<file>', methods=['GET'])  
@app.route('/markdown-viewer', methods=['GET'])  
def markdown_viewer(acct=None, repo=None, file=None):
    return (open(os.path.join(BASEDIR, 'src', 'markdown-viewer.html'), 'r').read(), 200, cors_headers)

@app.route('/config/<acct>/<repo>', methods=['GET'])
@app.route('/config', methods=['GET'])
def config(acct=None, repo=None):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    logger.info(f'config: acct={acct} repo={repo} kwargs={kwargs}')

    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        site = urlparse(request.base_url).hostname
        acct = acct if acct else DEFAULT_ACCT if DEFAULT_ACCT else KNOWN_SITES.get(site, {}).get('acct')
        repo = repo if repo else DEFAULT_REPO if DEFAULT_REPO else KNOWN_SITES.get(site, {}).get('repo')
        use_local = kwargs.pop('mode', ENV) == 'dev'
        logger.info(f'config: site={site} acct={acct} repo={repo} use_local={use_local}')
        _config = None
        if use_local:
            baseurl = 'http://localhost:5000'     
            config_path = f'{DOCS_ROOT}/docs/config.json'
            if os.path.exists(config_path):
                _config = json.load(open(config_path, 'r'))
        else:
            baseurl =f'https://{acct}.github.io/{repo}'
            resp = requests.get(f'{baseurl}/config.json')
            _config = resp.json() if resp.status_code == 200 else None
        if _config:
            for attr in ('banner', 'logo'):
                if attr in _config and not _config[attr].startswith('http'):
                    _config[attr] = f'{baseurl}/{_config[attr][1:] if _config[attr][0] == "/" else _config[attr]}'
            for comp in _config.get('components', []):
                if not comp['src'].startswith('http'):
                    comp['src'] = f'{baseurl}/{comp["src"][1:] if comp["src"][0] == "/" else comp["src"]}'
            return (_config, 200, cors_headers)
        else:
            return 'Not found', 404

@app.route('/<acct>/<repo>/<file>', methods=['GET'])  
@app.route('/<acct>/<repo>', methods=['GET'])  
@app.route('/<file>', methods=['GET'])  
@app.route('/', methods=['GET'])  
def site(acct=None, repo=None, file=None):    
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    site = urlparse(request.base_url).hostname
    if site == 'kent-maps.online':
        return redirect(f'https://dickens.kent-maps.online{request.path}', code=302)

    acct = acct if acct else KNOWN_SITES.get(site, {}).get('acct')
    repo = repo if repo else KNOWN_SITES.get(site, {}).get('repo')
    logger.info(f'site: site={site} acct={acct} repo={repo} kwargs={kwargs}')

    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        with open(os.path.join(BASEDIR, 'index.html'), 'r') as fp:
            html = fp.read()
            if site == 'localhost':
                html = re.sub(r'"https://jstor-labs.github.io/visual-essays.+"', '"http://localhost:8080/lib/visual-essays.js"', html)
            return html, 200

@app.route('/images/<fname>', methods=['GET'])  
def images(fname):
    return send_from_directory(os.path.join(DOCS_ROOT, 'docs', 'images'), fname, as_attachment=False)


@app.route('/geojson/<fname>', methods=['GET'])  
def geojson(fname):
    return send_from_directory(os.path.join(DOCS_ROOT, 'docs', 'geojson'), fname, as_attachment=False)

@app.route('/components/<fname>', methods=['GET'])
@app.route('/components/<subdir>/<fname>', methods=['GET'])  
def components(fname, subdir=None):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        for root in (DOCS_ROOT, os.path.dirname(BASEDIR)):
            components_path = f'{root}/docs/components' if subdir is None else f'{root}/docs/components/{subdir}'
            path = os.path.join(components_path, fname)
            logger.info(f'components: subdir={subdir} fname={fname} components_path={components_path} path={path} exists={os.path.exists(path)}')
            if os.path.exists(path):
                return (send_from_directory(components_path, fname, as_attachment=False), 200, cors_headers)

def usage():
    print('%s [hl:dr:a:p:]' % sys.argv[0])
    print('   -h --help         Print help message')
    print('   -l --loglevel     Logging level (default=warning)')
    print('   -d --dev          Use local Visual Essay JS Lib')
    print('   -r --docs-root    Documents root directory when running in dev mode')
    print('   -a --acct         Default acct')
    print('   -p --repo         Default repository')


if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:dr:a:p:', ['help', 'loglevel', 'dev', 'docs-root', 'acct', 'repo'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-l', '--loglevel'):
            loglevel = a.lower()
            if loglevel in ('error',): logger.setLevel(logging.ERROR)
            elif loglevel in ('warn','warning'): logger.setLevel(logging.INFO)
            elif loglevel in ('info',): logger.setLevel(logging.INFO)
            elif loglevel in ('debug',): logger.setLevel(logging.DEBUG)
        elif o in ('-d', '--dev'):
            VE_JS_LIB = 'http://localhost:8080/lib/visual-essays.js'
            ENV = 'dev'
        elif o in ('-r', '--docs-root'):
            DOCS_ROOT = a
        elif o in ('-a', '--acct'):
            DEFAULT_ACCT = a
        elif o in ('-p', '--repo'):
            DEFAULT_REPO = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    logger.info(f'ENV={ENV} VE_JS_LIB={VE_JS_LIB} DOCS_ROOT={DOCS_ROOT} DEFAULT_ACCT={DEFAULT_ACCT} DEFAULT_REPO={DEFAULT_REPO}')
    app.run(debug=True, host='0.0.0.0')