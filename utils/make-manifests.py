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
from urllib.parse import quote

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
    manifest = {
        'sequences': [{
            'canvases': [{**manifest_defaults['canvas'], **{
                'images': [{**manifest_defaults['image'], **{
                    'url': kwargs['url']
                }}]
            }}]
        }]
    }
    # add optional properties
    if 'label' in kwargs:
        manifest['label'] = kwargs['label']
        manifest['sequences'][0]['canvases'][0]['label'] = kwargs['label']
    if 'description' in kwargs:
        manifest['description'] = kwargs['description']
    if 'attribution' in kwargs:
        manifest['attribution'] = kwargs['attribution']
    if 'annotations' in kwargs:
        manifest['sequences'][0]['canvases'][0]['otherContent'] = [{
                '@id': kwargs['annotations'],
                '@type': 'sc:AnnotationList'
            }]
    logger.info(json.dumps(manifest, indent=2))
    resp = requests.post(
        'https://tripleeyeeff-atjcn6za6q-uc.a.run.app/presentation/create',
        headers={'Content-type': 'application/json'},
        json=manifest
    )
    return resp.json()

def as_hyperlink(qid, label=None):
    return '=HYPERLINK("{}", "{}")'.format('https://kg.jstor.org/entity/{}'.format(qid), label if label else qid)

def usage():
    print(('%s [hl:w:s:]' % sys.argv[0]))
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -w --workbook        Workbook name (default="%s"' % default_workbook)
    print('   -s --worksheet       Worksheet name (default="%s"' % default_worksheet)

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:w:s:e:n:b:p:', ['help', 'loglevel', 'workbook', 'worksheet'])
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
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    worksheets = {}
    ws_data = {}
    wb = get_workbook(**kwargs)
    for ws in wb.worksheets():
        worksheets[ws.title] = ws
        rows = ws.get_all_values()
        fields = rows[0]
        recs = [dict([(fields[col], row[col]) for col in range(len(row))]) for row in rows[1:]]
        print(json.dumps(recs))
