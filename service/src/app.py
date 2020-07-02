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
import base64
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
GH_CREDS = 'Token 47189dabf0b91a356d9f02155fc234f51f07905c'

KNOWN_SITES = {
    # 'localhost': {'acct': 'jstor-labs', 'repo': 'visual-essays'},
    'visual-essays.app': {'acct': 'jstor-labs', 'repo': 'visual-essays'},
    'plant-humanities.app': {'acct': 'jstor-labs', 'repo': 'plant-humanities'},
    'dickens.kent-maps.online': {'acct': 'kent-map', 'repo': 'dickens'},
    'kent-maps.online': {'acct': 'kent-map', 'repo': 'kent'}
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

'''
def get_gh_markdown(acct, repo, path=None):
    # baseurl = content_baseurl(acct, repo)
    for baseurl in (f'https://raw.githubusercontent.com/{acct}/{repo}/master{"/docs/content" if repo == "plant-humanities" else ""}', f'https://{acct}.github.io/{repo}'):
        logger.info(f'get_gh_markdown: acct={acct} repo={repo} path={path} baseurl={baseurl}')
        path_root = f'/{path}' if path else ''
        files = [f'/{path_root}' if path_root.endswith('.md') else f'{path_root}.md']
        files += [f'{path_root}/{file}' for file in ('index.md', 'home.md', 'README.md')]
        for file in files:
            url = f'{baseurl}{file}'
            resp = requests.get(url)
            logger.info(f'{url} {resp.status_code}')
            if resp.status_code == 200:
                return {
                    'baseurl': baseurl,
                    'source': 'gh',
                    'fname': file.replace('.md', ''),
                    'match': file.split('/')[-1],
                    'text': resp.content.decode('utf-8')
            }
'''

def get_gh_baseurls(acct, repo):
    baseurl = f'https://raw.githubusercontent.com/{acct}/{repo}/master'
    api_baseurl = f'https://api.github.com/repos/{acct}/{repo}/contents'
    resp = requests.get(f'https://api.github.com/repos/{acct}/{repo}/pages', headers={
        'Authorization': GH_CREDS,
        'Accept': 'application/vnd.github.v3+json',
        'User-agent': 'JSTOR Labs visual essays client'
    })
    if resp.status_code == 200:
        if resp.json()['source']['path'] == '/docs':
            baseurl += '/docs'
            api_baseurl += '/docs'
        if repo == 'plant-humanities':
            baseurl += '/content'
            api_baseurl += '/content'

    return baseurl, api_baseurl

def get_gh_markdown(acct, repo, path=None):
    baseurl, api_baseurl = get_gh_baseurls(acct, repo)
    logger.info(f'get_gh_markdown: acct={acct} repo={repo} path={path} baseurl={baseurl} api_baseurl={api_baseurl}')
    path_root = f'/{path}' if path else ''
    files = [f'/{path_root}' if path_root.endswith('.md') else f'{path_root}.md']
    files += [f'{path_root}/{file}' for file in ('index.md', 'home.md', 'README.md')]

    for file in files:
        url = f'{api_baseurl}{file}'
        if url in cache:
            resp = requests.get(url, headers={
                'Authorization': GH_CREDS,
                'Accept': 'application/vnd.github.v3+json',
                'User-agent': 'JSTOR Labs visual essays client'
            })
            logger.info(f'{url} {resp.status_code}')
            if resp.status_code == 200:
                resp = resp.json()
                return {
                    'baseurl': baseurl,
                    'source': 'gh',
                    'fname': file.replace('.md', ''),
                    'match': file.split('/')[-1],
                    'text': base64.b64decode(resp['content']).decode('utf-8'),
                    'url': url,
                    'sha': resp['sha']
                }
            else:
                logger.info(resp.json())
    for file in files:
        url = f'{api_baseurl}{file}'
        resp = requests.get(url, headers={
            'Authorization': GH_CREDS,
            'Accept': 'application/vnd.github.v3+json',
            'User-agent': 'JSTOR Labs visual essays client'
        })
        logger.info(f'{url} {resp.status_code}')
        if resp.status_code == 200:
            resp = resp.json()
            return {
                'baseurl': baseurl,
                'source': 'gh',
                'fname': file.replace('.md', ''),
                'match': file.split('/')[-1],
                'text': base64.b64decode(resp['content']).decode('utf-8'),
                'url': url,
                'sha': resp['sha']
        }

def get_gd_markdown(gdid):
    url = f'https://drive.google.com/uc?export=download&id={gdid}'
    resp = requests.get(url)
    logger.debug(f'{url} {resp.status_code}')
    if resp.status_code == 200:
        return {'source': 'gdid', 'fname': gdid, 'text': resp.content.decode('utf-8')}

def get_local_markdown(path=None):
    path = path[:-1] if path[-1] == '/' else path
    path_elems = path.split('/')
    is_dir = os.path.isdir(path)
    fname = path_elems[-1]
    fdir = path if is_dir else '/'.join(path_elems[:-1])
    logger.info(f'get_local_markdown: fdir={fdir} fname={fname}')
    files = ['index.md', 'home.md', 'README.md'] if is_dir else [fname if fname.endswith('.md') else f'{fname}.md']
    for file in files:
        fpath = f'{fdir}/{file}'
        logger.info(f'fpath{fpath} exists={os.path.exists(fpath)}')
        if os.path.exists(fpath):
            with open(fpath, 'r') as fp:
                return {
                    'baseurl': 'http://localhost:5000',
                    'source': 'local', 
                    'fname': fname.replace('.md', ''),
                    'match': file,
                    'text': fp.read()
                }

def convert_relative_links(soup, site, acct, repo, path, markdown):
    path_elems = [pe for pe in path.split('/') if pe] if path else []
    baseurl = f'{markdown["baseurl"]}/essay'
    if site == 'localhost':
        baseurl = 'http://localhost:5000/essay'
        if acct:
            baseurl += f'/{acct}/{repo}'
    else:
        baseurl = None
        for site, site_data in KNOWN_SITES.items():
            if site_data['acct'] == acct and site_data['repo'] == repo and site != 'localhost':
                baseurl = f'https://{site}/essay/{acct}/{repo}'
                break
        if baseurl is None:
            baseurl = f'https://visual-essays.app/essay/{acct}/{repo}'

    logger.info(f'convert_relative_links: site={site} acct={acct} repo={repo} path={path} fname={markdown["fname"]} match={markdown["match"]} baseurl={baseurl}')
    for tag in ('a',):
        for elem in soup.find_all(tag):
            for attr in ('href',):
                if attr in elem.attrs:
                    if not elem.attrs[attr].startswith('http'):
                        logger.info(elem.attrs[attr])
                        if elem.attrs[attr].startswith('#'):
                            elem.attrs[attr] = f'{markdown["fname"]}{elem.attrs[attr]}'
                        if elem.attrs[attr][0] == '/':
                            elem.attrs[attr] = f'{baseurl}{elem.attrs[attr]}'
                        else:
                            if markdown['match'] == 'index.md':
                                rel_path = f'/{"/".join(path_elems)}' if len(path_elems) > 0 else ''
                            else:
                                rel_path = f'/{"/".join(path_elems[:-1])}' if len(path_elems) > 1 else ''
                            logger.info(f'path={path_elems} match={markdown["match"]} rel_path={rel_path}')
                            elem.attrs[attr] = f'{baseurl}{rel_path}/{elem.attrs[attr]}'
                    logger.info(elem.attrs[attr])
    
    if site == 'localhost' and ENV == 'dev':
        # baseurl = f'http://localhost:5000/assets'
        baseurl = f'{markdown["baseurl"]}/assets'
    else:
        # baseurl = content_baseurl(acct, repo)
        baseurl = f'{markdown["baseurl"]}'
    
    logger.info(f'convert_relative_image_links: source={markdown["source"]} baseurl={baseurl}')
    for tag in ('img', 'var', 'span', 'param'):
        for elem in soup.find_all(tag):
            for attr in ('banner', 'data-banner', 'src', 'url'):
                if attr in elem.attrs and elem.attrs[attr] and not elem.attrs[attr].startswith('http'):
                    if elem.attrs[attr][0] == '/':
                        elem.attrs[attr] = f'{baseurl}{elem.attrs[attr]}'
                    else:
                        if markdown["match"] == 'index.md':
                            rel_path = f'/{"/".join(path_elems)}' if len(path_elems) > 0 else ''
                        else:
                            rel_path = f'/{"/".join(path_elems[:-1])}' if len(path_elems) > 1 else ''
                        elem.attrs[attr] = f'{baseurl}{rel_path}/{elem.attrs[attr]}'
                    if repo == 'plant-humanities':
                        elem.attrs[attr] = elem.attrs[attr].replace('/content/geojson', '/geojson')
                    logger.info(elem.attrs[attr])

def _is_empty(elem):
    child_images = [c for c in elem.children if c.name == 'img']
    if child_images:
        return False
    elem_contents = [t for t in elem.contents if t and (isinstance(t, str) and t.strip()) or t.name not in ('br',) and t.string and t.string.strip()]
    return len(elem_contents) == 0

def markdown_to_html5(markdown, site=None, acct=None, repo=None, path=None):
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
    convert_relative_links(soup, site, acct, repo, path, markdown)

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

@app.route('/essay/<path:path>', methods=['GET'])
@app.route('/essay/', methods=['GET'])
def essay(path=None):
    logger.info(path)
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        raw = kwargs.pop('raw', 'false') in ('', 'true')
        site = urlparse(request.base_url).hostname
        refresh = kwargs.pop('refresh', 'false').lower() in ('true', '')
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
        acct = None
        repo = None
        if src:
            markdown = get_markdown(src)
        elif gdid:
            markdown = get_gd_markdown(gdid)
        else:
            acct = DEFAULT_ACCT if DEFAULT_ACCT else KNOWN_SITES.get(site, {}).get('acct')
            repo = DEFAULT_REPO if DEFAULT_REPO else KNOWN_SITES.get(site, {}).get('repo')
            path_elems = path.split('/') if path else []
            logger.info(f'essay: site={site} path={path} raw={raw} kwargs={kwargs}')
            if site == 'localhost' and ENV == 'dev':
                abs_path = f'{DOCS_ROOT}/docs{"/content/" if repo == "plant-humanities" else "/"}{"/".join(path_elems)}'
                is_dir = os.path.isdir(abs_path)
                logger.info(f'path={path} abs_path={abs_path} is_dir={is_dir}')
                markdown = get_local_markdown(abs_path)
                baseurl = 'http://localhost:5000'
            else:
                if site in ('localhost', 'visual-essays.app'):
                    if len(path_elems) > 2:
                        acct = path_elems[0]
                        repo = path_elems[1]
                        path = '/'.join(path_elems[2:])
                    elif len(path_elems) == 2:
                        acct = path_elems[0]
                        repo = path_elems[1]
                        path = None
                    elif len(path_elems) == 1:
                        path = path_elems[0]
                markdown = get_gh_markdown(acct, repo, path)
                baseurl = content_baseurl(acct, repo)
        logger.info(f'essay: site={site} acct={acct} repo={repo} path={path} raw={raw} kwargs={kwargs}')
        if markdown:
            if raw:
                return (markdown['text'], 200, cors_headers)
            else:
                cache_key = f'{site}|{acct}|{repo}|{path}'
                cached = cache.get(cache_key) if not refresh else False
                logger.info(f'essay: site={site} acct={acct} repo={repo} path={path} cached={cached and cached["sha"] == markdown["sha"]}')
                if cached and cached['sha'] == markdown['sha']:
                    html = cached['html']
                else:
                    essay = Essay(html=markdown_to_html5(markdown, site, acct, repo, path or '/'), cache=cache, baseurl=baseurl, **kwargs)
                    html = add_vue_app(essay.soup, VE_JS_LIB)
                    if 'url' in markdown and 'sha' in markdown:
                        cache[cache_key] = {'html': html, 'sha': markdown['sha']}
                return (html, 200, cors_headers)
        else:
            return 'Not found', 404

@app.route('/markdown-viewer/<path:path>', methods=['GET'])
@app.route('/markdown-viewer/', methods=['GET'])  
@app.route('/markdown-viewer', methods=['GET'])  
def markdown_viewer(path=None):
    logger.info(f'markdown-viewer: path={path}')
    return (open(os.path.join(BASEDIR, 'src', 'markdown-viewer.html'), 'r').read(), 200, cors_headers)

@app.route('/config/<path:path>', methods=['GET'])
@app.route('/config', methods=['GET'])
def config(path=None):
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        path_elems = path.split('/') if path else []
        site = urlparse(request.base_url).hostname
        acct = path_elems[0] if len(path_elems) == 2 else DEFAULT_ACCT if DEFAULT_ACCT else KNOWN_SITES.get(site, {}).get('acct', )
        repo = path_elems[1] if len(path_elems) == 2 else DEFAULT_REPO if DEFAULT_REPO else KNOWN_SITES.get(site, {}).get('repo')
        logger.info(f'config: site={site} acct={acct} repo={repo}')
        _config = None
        if site == 'localhost' and ENV == 'dev':
            baseurl = 'http://localhost:5000'     
            config_path = f'{DOCS_ROOT}/docs/config.json'
            logger.info(f'config_path={config_path} exists={os.path.exists(config_path)}')
            if os.path.exists(config_path):
                _config = json.load(open(config_path, 'r'))
        else:
            baseurl = f'https://{acct}.github.io/{repo}'
            logger.info(f'{baseurl}/config.json')
            resp = requests.get(f'{baseurl}/config.json')
            _config = resp.json() if resp.status_code == 200 else None
        if _config:
            baseurl = f'http://localhost:5000/assets' if site == 'localhost' and ENV == 'dev' else f'https://{acct}.github.io/{repo}'
            for attr in ('banner', 'logo'):
                if attr in _config and not _config[attr].startswith('http'):
                    logger.info(_config[attr])
                    if _config[attr][0] == '/':
                        _config[attr] = f'{baseurl}{_config[attr]}'
                    else:
                        _config[attr] = f'{baseurl}/{_config[attr]}'
                    logger.info(_config[attr])
            baseurl = f'http://localhost:5000' if site == 'localhost' and ENV == 'dev'  else f'https://{acct}.github.io/{repo}'
            for comp in _config.get('components', []):
                if not comp['src'].startswith('http'):
                    if comp['src'][0] == '/':
                        comp['src'] = f'{baseurl}{comp["src"]}'
                    else:
                        comp['src'] = f'{baseurl}/{comp["src"]}'
                    logger.info(f'component={comp["src"]}')
            return (_config, 200, cors_headers)
        else:
            return 'Not found', 404

@app.route('/<path:path>', methods=['GET'])
@app.route('/', methods=['GET'])
def site(path=None):    
    kwargs = dict([(k, request.args.get(k)) for k in request.args])
    _set_logging_level(kwargs)
    site = urlparse(request.base_url).hostname
    if site == 'dickens.kent-maps.online':
        return redirect(f'https://kent-maps.online/dickens{request.path}', code=302)

    logger.info(f'site: site={site} path={path} kwargs={kwargs}')

    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        with open(os.path.join(BASEDIR, 'index.html'), 'r') as fp:
            html = fp.read()
            if site == 'localhost':
                html = re.sub(r'"https://jstor-labs.github.io/visual-essays.+"', '"http://localhost:8080/lib/visual-essays.js"', html)
            return html, 200
'''
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
'''

@app.route('/assets/<path:path>', methods=['GET'])
def assets(path):
    logger.info(f'assets: {path}')
    path_elems = path.split('/')
    logger.info(path_elems)
    idir = f'{DOCS_ROOT}/docs/{"/".join(path_elems[:-1])}' if len(path_elems) > 1 else f'{DOCS_ROOT}/docs'
    fname = path_elems[-1]
    logger.info(f'assets: dir={idir} fname={fname}')
    return send_from_directory(idir, fname, as_attachment=False)

@app.route('/geojson/<fname>', methods=['GET'])  
def geojson(fname):
    return send_from_directory(os.path.join(DOCS_ROOT, 'geojson'), fname, as_attachment=False)

@app.route('/components/<path:path>', methods=['GET'])
def components(path):
    if request.method == 'OPTIONS':
        return ('', 204, cors_headers)
    else:
        logger.info(path)
        path_elems = path.split('/')
        fname = path_elems[-1]
        for root in [DOCS_ROOT, os.path.dirname(BASEDIR)]:
            logger.info(root)
            _dir = f'{root}/docs/components/{"/".join(path_elems[:-1])}'
            exists = os.path.exists(f'{_dir}/{fname}')
            logger.info(f'components: dir={_dir} fname={fname} exists={exists}')
            if exists:
                return (send_from_directory(_dir, fname, as_attachment=False), 200, cors_headers)

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