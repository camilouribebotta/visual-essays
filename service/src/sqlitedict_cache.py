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

import zlib, sqlite3
from sqlitedict import SqliteDict
logging.getLogger('sqlitedict').setLevel(logging.WARNING)

def cache_encode(obj):
    return sqlite3.Binary(zlib.compress(json.dumps(obj).encode('utf-8')))
def cache_decode(obj):
    return json.loads(zlib.decompress(bytes(obj)))

DEFAULT_DATABASE_NAME     = 'db'
DEFAULT_KEYFIELD          = 'id'

class Cache(object):

    def __init__(self, **kwargs):
        self.name      = kwargs.get('name', DEFAULT_DATABASE_NAME)
        self._db       = SqliteDict('./%s.sqlite' % self.name, encode=cache_encode, decode=cache_decode, autocommit=True)
        logger.info('name=%s size=%s', self.name, len(self._db))

    def close(self):
        self._db.close()

    def __del__(self):
        pass # self.close()

    def __iter__(self):
        return self._db.__iter__()

    def iteritems(self):
        return self._db.iteritems()

    def iterkeys(self):
        return self._db.iterkeys()
    
    def itervalues(self):
        return self._db.itervalues()

    def items(self):
        return self.iteritems()

    def __getitem__(self, key):
        return self._db.__getitem__(key)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __setitem__(self, key, value):
        return self._db.__setitem__(key, value)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def __len__(self):
        return len(self._db)

    def __contains__(self, key):
        return key in self._db

    def __delitem__(self, key):
        if key in self._db:
            del self._db[key]

    def list(self, limit=None):
        logger.info('list')
        keys = []
        for key in self:
            keys.append(key)
            if limit is not None and len(keys) == limit: break
        return keys

def usage():
    print('%s [hl:n:f:k:siex] [keys]' % sys.argv[0])
    print('   -h --help            Print help message')
    print('   -l --loglevel        Logging level (default=warning)')
    print('   -n --name            Database name (%s)' % DEFAULT_DATABASE_NAME)
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
                        cache[doc[key]] = doc
                    except KeyboardInterrupt:
                        break
                    except:
                        logger.error(traceback.format_exc())
                        # cache.logger.error(line)
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
        for key in cache:
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
        #usage()
        #sys.exit(2)
        
    cache.close()