# -*- coding: utf-8 -*-
#import codecs
from configparser import RawConfigParser
import os
import sys

__author__ = 'Aron Culotta'
__email__ = 'aronwc@gmail.com'
__version__ = '0.1.0'

config = RawConfigParser()
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
