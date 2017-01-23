# -*- coding: utf-8 -*-
#import codecs
import os
import sys

try:
    from configparser import RawConfigParser as ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

__author__ = 'Aron Culotta'
__email__ = 'aronwc@gmail.com'
__version__ = '0.1.7'

config = ConfigParser()
if 'BRANDELION_CFG' in os.environ:
    config.read(os.environ['BRANDELION_CFG'])
else:
    config.read('~/.brandelion')

#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

# make directories
path = config.get('data', 'path')
for subdir in ['collect', 'analyze', 'report']:
    try:
        os.makedirs(path + '/' + config.get('data', subdir))
    except:
        pass
