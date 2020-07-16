#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s')
logger = logging.getLogger()

import os
import re
import json
import getopt
import sys
from urllib.parse import quote

import requests
logging.getLogger('requests').setLevel(logging.INFO)

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
        'https://iiif.visual-essays.app/presentation/create',
        headers={'Content-type': 'application/json'},
        json=manifest
    )
    return resp.json()


def usage():
    print(f'{sys.argv[0]} [hl:t:d:a:r:] url')
    print(f'   -h --help          Print help message')
    print(f'   -l --loglevel      Logging level (default=warning)')
    print(f'   -t --label         Image label')
    print(f'   -d --description   Image description')
    print(f'   -a --annotations   URL to image annotations')
    print(f'   -r --attribution   Attribution')

if __name__ == '__main__':
    logger.setLevel(logging.WARNING)
    kwargs = {}
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hl:t:d:a:r:', ['help', 'loglevel', 'label', 'description', 'annotations', 'attribution'])
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
        elif o in ('-t', '--label'):
            kwargs['label'] = a
        elif o in ('-d', '--description'):
            kwargs['description'] = a
        elif o in ('-a', '--annotations'):
            kwargs['annotations'] = a
        elif o in ('-r', '--attribution'):
            kwargs['attribution'] = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        kwargs['url'] = args[0]
        print(json.dumps(create_manifest(**kwargs)))
    else:
        usage()