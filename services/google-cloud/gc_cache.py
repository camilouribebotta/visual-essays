#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.WARN)
logger = logging.getLogger()

import os
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

import sys
import getopt
import traceback
import json

DEFAULT_PROJECT_NAME = 'visual-essays'
DEFAULT_BUCKET_NAME = 'visual-essays-cache'
DEFAULT_CREDS_PATH = './visual-essay-gcreds.json'
DEFAULT_KEYFIELD = 'id'

from google.oauth2 import service_account
from google.cloud import storage

from expiringdict import ExpiringDict
# cache = ExpiringDict(max_len=100, max_age_seconds=10)
expiration = 60 * 60 * 24 # one day

class Cache(object):

    def __init__(self, **kwargs):
        self.local = ExpiringDict(max_len=100, max_age_seconds=expiration)
        self.project_name = kwargs.get('project', DEFAULT_PROJECT_NAME)
        self.bucket_name = kwargs.get('name', DEFAULT_BUCKET_NAME)
        self.creds_path = kwargs.get('creds_path', DEFAULT_CREDS_PATH)
        credentials = service_account.Credentials.from_service_account_file(self.creds_path)
        self.client = storage.Client(self.project_name, credentials)
        self.bucket = self.client.get_bucket(self.bucket_name)

    def __contains__(self, key):
        logger.debug(f'{key} local={key in self.local} gc={self.bucket.blob(key).exists()}')
        return self.bucket.blob(key).exists()

    def __setitem__(self, key, value):
        self.local[key] = value
        blob = self.bucket.blob(key)
        blob.upload_from_string(json.dumps(value))

    def set(self, key, value):
        return self.__setitem__(key, value)

    def __getitem__(self, key):
        item = self.local.get(key)
        if item:
            logger.debug(f'get: key={key} local=True')
        else:
            blob = self.bucket.blob(key)
            try:
                item = json.loads(blob.download_as_string())
            except:
                pass
            logger.debug(f'get: key={key} local=False gc={item is not None}')
            if item:
                self.local[key] = item
        return item

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __iter__(self):
        return self.client.list_blobs(self.bucket)._items_iter()

    def iteritems(self):
        for blob in self.__iter__():
            yield blob.name, self[blob.name]

    def iterkeys(self):
        for blob in self.__iter__():
            yield blob.name
    
    def itervalues(self):
        for blob in self.__iter__():
            yield self[blob.name]

    def items(self):
        for blob in self.__iter__():
            yield blob.name, self[blob.name]

    def __len__(self):
        pass # TODO

    def __delitem__(self, key):
        pass # TODO

def usage():
    print('%s [hl:n:f:k:siex] [keys]' % sys.argv[0])
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -n --name            Database name (%s)' % DEFAULT_BUCKET_NAME)
    print('   -f --key             Field value to use for key when importing (default="%s")' % DEFAULT_KEYFIELD)
    print('   -k --list            Number of keys to list (-1 = all)')
    print('   -s --size            Database size')
    print('   -i --import          Import')
    print('   -e --export          Export')
    print('   -x --delete          Delete item from database')

if __name__ == '__main__':
    kwargs = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:n:f:k:siex', ['help', 'loglevel', 'name', 'key', 'list', 'size', 'import', 'export', 'delete'])
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
        elif o in ('-n', '--name'):
            kwargs['name'] = a
        elif o in ('-f', '--key'):
            kwargs['key'] = a
        elif o in ('-k', '--list'):
            kwargs['list'] = int(a)
        elif o in ('-s', '--size'):
            kwargs['size'] = True
        elif o in ('-i', '--import'):
            kwargs['import'] = True
        elif o in ('-e', '--export'):
            kwargs['export'] = True
        elif o in ('-x', '--delete'):
            kwargs['delete'] = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    cache = Cache(**kwargs)
        
    if kwargs.get('import', False):
        key = kwargs.get('key', DEFAULT_KEYFIELD)
        ctr = 0
        for path in args:
            with open(path,'r') as infile:
                for line in infile:
                    try:
                        doc = json.loads(line)
                        db[doc[key]] = doc
                    except KeyboardInterrupt:
                        break
                    except:
                        logger.error(traceback.format_exc())
                        # db.logger.error(line)
                    ctr += 1
                    if ctr % 10000 == 0: logger.info('%s %s'%(path,ctr))
        logger.info(ctr)
    elif kwargs.get('export', False):
        ctr = 0
        for item in cache.itervalues():
            try:
                print(json.dumps(item))
                ctr += 1
                if ctr % 10000 == 0: logger.info(ctr)
            except KeyboardInterrupt:
                break
            except:
                logger.error(traceback.format_exc())
        logger.info(ctr)
    elif kwargs.get('size', False):
        print(len(cache))
    elif 'list' in kwargs:
        limit = kwargs.get('list')
        ctr = 0
        for key in cache.iterkeys():
            try:
                print(key)
                ctr += 1
                if ctr == limit:
                    break
            except KeyboardInterrupt:
                break
            except:
                logger.error(traceback.format_exc())
    elif args:
        for key in args:
            if kwargs.get('delete', False):
                del cache[key]
            else:
                print(json.dumps(cache[key]))
    else:
        ctr = 0
        for line in sys.stdin:
            rec = json.loads(line)
            cache[rec['id']] = rec
            ctr += 1
            logger.info('%s %s', ctr, rec['id'])
