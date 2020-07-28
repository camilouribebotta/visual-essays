#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s :  %(name)s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

import os, sys, getopt, traceback, time
from datetime import datetime

import json
import requests
logging.getLogger('requests').setLevel(logging.WARNING)

sys.path.append('/opt/lib')

import os
import sys
import getopt
from urllib.parse import quote, urlparse

default_workbook = 'Kent images'
default_worksheet = 'metadata'

import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
logging.getLogger('oauth2client.client').setLevel(logging.WARNING)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

def get_workbook(workbook=default_workbook, **kwargs):
    logger.info(f'get_workbook: {workbook}')
    creds = ServiceAccountCredentials.from_json_keyfile_name('labs-gs-creds.json', scope)
    client = gspread.authorize(creds)
    return client.open(workbook)

manifest_defaults = {
    'canvas': { 'height': 3000, 'width': 3000 },
    'image': { 'region': 'full', 'size': 'full', 'rotation': '0' }
}

def create_manifest(**kwargs):
    logger.info(f'create_manifest {kwargs}')
    url = None
    for fld in ('alt-source', 'source'):
        url = kwargs.get(fld)
        if url:
            logger.info(f'url={url}')
            parsed = urlparse(kwargs[fld])
            if '/blob/master' in parsed.path:
                path_elems = parsed.path[1:].replace('/blob/master', '').split('/')
                gh_acct = path_elems[0]
                gh_repo = path_elems[1]
                path = '/'.join(path_elems[2:])
                url = f'https://raw.githubusercontent.com/{gh_acct}/{gh_repo}/master/{path}'
            manifest = {
                '@context': 'http://iiif.io/api/presentation/2/context.json',
                'sequences': [{
                    'canvases': [{**manifest_defaults['canvas'], **{
                        'images': [{**manifest_defaults['image'], **{
                            'url': url
                        }}]
                    }}]
                }]
            }
            # add optional properties
            label = kwargs.get('label')
            if not label:
                label = kwargs.get('description')
            if label:
                manifest['label'] = label
                manifest['sequences'][0]['canvases'][0]['label'] = label
            metadata = dict([(k,v) for k,v in kwargs.items() if v and k in ('attribution', 'date', 'description', 'license', 'logo', 'rights')])
            metadata['source'] = url

            for fld in ('attribution', 'description', 'license', 'logo'):
                if fld in metadata:
                    manifest[fld] = metadata.get(fld)
            if metadata:
                manifest['metadata'] = [{'label': 'version', 'value': '2'}] + [{'label': k, 'value': v} for k,v in metadata.items()]

            logger.info(json.dumps(manifest, indent=2))
            resp = requests.post(
                'https://iiif.visual-essays.app/presentation/create',
                headers={'Content-type': 'application/json'},
                json=manifest
            )
            logger.info(resp.status_code)
            manifest = resp.json()
            if '@id' in manifest:
                logger.info(f'{url} {manifest["@id"]}')
                if '@type' in manifest:
                    return manifest
                else:
                    return requests.get(manifest['@id'], headers={'Content-type': 'application/json'}).json() 

def as_hyperlink(qid, label=None):
    return '=HYPERLINK("{}", "{}")'.format('https://kg.jstor.org/entity/{}'.format(qid), label if label else qid)

def as_image(url):
    return f'=IMAGE("{url}")'

def usage():
    print(('%s [hl:w:s:r]' % sys.argv[0]))
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -w --workbook        Workbook name (default="%s")' % default_workbook)
    print('   -s --worksheet       Worksheet name (default="%s")' % default_worksheet)
    print('   -r --refresh         Force refresh')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:w:s:r', ['help', 'loglevel', 'workbook', 'worksheet', 'refresh'])
    except getopt.GetoptError as err:
        # print help information and exit:
        logger.info(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-l', '--loglevel'):
            loglevel = a.lower()
            if loglevel in ('error',): logger.setLevel(logging.ERROR)
            elif loglevel in ('warn','warning'): logger.setLevel(logging.INFO)
            elif loglevel in ('info',): logger.setLevel(logging.INFO)
            elif loglevel in ('debug',): logger.setLevel(logging.DEBUG)
        elif o in ('-w', '--workbook'):
            kwargs['workbook'] = a
        elif o in ('-s', '--worksheet'):
            kwargs['worksheet'] = a
        elif o in ('-r', '--refresh'):
            kwargs['refresh'] = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"


    force_refresh = kwargs.pop('refresh', False)

    worksheets = {}
    ws_data = {}
    wb = get_workbook(**kwargs)
    logger.debug(kwargs.get('worksheet', default_worksheet))
    ws = wb.worksheet(kwargs.get('worksheet', default_worksheet))
    rows = ws.get_all_values()
    fields = rows[0]
    field_idx = dict([(fields[i], i) for i in range(len(fields))])
    recs = [dict([(fields[col], row[col]) for col in range(len(row))]) for row in rows[1:]]

    updates = []
    for i, rec in enumerate(recs):
        row = i + 2
        if not force_refresh and rec.get('manifest'):
            continue
        manifest = create_manifest(**rec)
        if manifest:
            logger.debug(json.dumps(manifest, indent=2))
            img = manifest['sequences'][0]['canvases'][0]['images'][0]['resource']
            row_updates = {
                'manifest': manifest['@id'],
                'thumbnail': as_image(manifest['thumbnail']),
                'image': img['service']['@id'],
                'height': img['height'],
                'width': img['width'],
                'format': img['format'].split('/')[-1]
            }
            row_updates = [Cell(row, field_idx[fld] + 1, val) for fld, val in row_updates.items() if fld in field_idx]
            row_updates.sort(key=lambda cell: cell.col, reverse=False)
            ws.update_cells(row_updates, value_input_option='USER_ENTERED')