#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze social and linguistic brand data.

usage:
    brandelion analyze --text --brand-tweets <file> --exemplar-tweets <file> --sample-tweets <file> --output <file>
    brandelion analyze --network --brand-followers <file> --exemplar-followers <file> --output <file>

Options
    -h, --help
    --brand-followers <file>      File containing follower data for brand accounts.
    --brand-tweets <file>         File containing tweets from brand accounts.
    --exemplar-followers <file>   File containing follower data for exemplar accounts.
    --exemplar-tweets <file>      File containing tweets from exemplar accounts.
    --sample-tweets <file>        File containing tweets from representative sample of Twitter.
    -o, --output <file>           File to store results
    -t, --text                    Analyze text of tweets.
    -n, --network                 Analyze followers.
"""

from docopt import docopt
import io
from itertools import groupby
import json
import sys

from sklearn.feature_extraction.text import CountVectorizer


def parse_json(json_file):
    """ Yield screen_name, text tuples from a json file. """
    for line in io.open(json_file, mode='rt', encoding='utf8'):
        try:
            jj = json.loads(line)
            yield (jj['user']['screen_name'], jj['text'])
        except Exception as e:
            sys.stderr.write('skipping json error: %s\n' % e)


def vectorize(json_file):
    """ Return a matrix where each row corresponds to a Twitter account, and
    each column corresponds to the number of times a term is used by that
    account. """
    screen_names = []
    for screen_name, tweet_iter in groupby(parse_json(json_file), lambda x: x[0]):
        tweets = [t for t in tweet_iter]
        print screen_name, len(tweets)
    ## CountVectorizer, efficiently.

def analyze_text(brand_tweets_file, exemplar_tweets_file, sample_tweets_file, outfile):
    exemplar_vectors = vectorize(exemplar_tweets_file)


def read_follower_file(fname):
    """ Read a file of follower information and return a dictionary mapping screen_name to a set of follower ids. """
    result = {}
    with open(fname, 'rt') as f:
        for line in f:
            parts = line.split()
            result[parts[0]] = set(parts[2:])
    return result


def jaccard(a, b):
    """ Return the Jaccard similarity between two sets a and b. """
    return 1. * len(a & b) / len(a | b)


def compute_social_score(followers, exemplars, sim_fn=jaccard):
    """ Return the average similarity between a brand's followers and the
    followers of each exemplar. """
    return 1. * sum([sim_fn(followers, others) for others in exemplars.itervalues()]) / len(exemplars)


def analyze_followers(brand_follower_file, exemplar_follower_file, outfile):
    brands = read_follower_file(brand_follower_file)
    exemplars = read_follower_file(exemplar_follower_file)
    print 'read follower data for %d brands and %d exemplars' % (len(brands), len(exemplars))
    outf = open(outfile, 'wt')
    for brand, followers in brands.iteritems():
        outf.write('%s %f\n' % (brand, compute_social_score(followers, exemplars)))
        outf.flush()
    outf.close()
    print 'results written to', outfile


def main():
    args = docopt(__doc__)
    if args['--network']:
        analyze_followers(args['--brand-followers'], args['--exemplar-followers'], args['--output'])
    elif args['--text']:
        analyze_text(args['--brand-tweets'], args['--exemplar-tweets'], args['--sample-tweets'], args['--output'])


if __name__ == '__main__':
    main()
