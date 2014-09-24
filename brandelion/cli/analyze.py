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
import numpy as np
import re
from scipy.sparse import vstack
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2
from sklearn import linear_model


### TEXT ANALYSIS ###

def parse_json(json_file):
    """ Yield screen_name, text tuples from a json file. """
    for line in io.open(json_file, mode='rt', encoding='utf8'):
        try:
            jj = json.loads(line)
            yield (jj['user']['screen_name'], jj['text'])
        except Exception as e:
            sys.stderr.write('skipping json error: %s\n' % e)


def extract_tweets(json_file):
    """ Yield screen_name, string tuples, where the string is the
    concatenation of all tweets of this user. """
    for screen_name, tweet_iter in groupby(parse_json(json_file), lambda x: x[0]):
        tweets = [t[1] for t in tweet_iter]
        yield screen_name, ' '.join(tweets)


def preprocess(s):
    """
    >>> preprocess('#hi there http://www.foo.com @you isn"t RT &lt;&gt;')
    'hashtaghi hashtaghi there isn"t'
    """
    # s = re.sub('@\S+', 'thisisamention', s)  # map all mentions to thisisamention
    s = re.sub(r'@\S+', ' ', s)  # map all mentions to thisisamention
    # s = re.sub('http\S+', 'http', s)  # keep only http from urls
    s = re.sub(r'http\S+', ' ', s)  # keep only http from urls
    s = re.sub(r'#(\S+)', r'hashtag\1 hashtag\1', s)  # #foo -> hashtagfoo hashtagfoo (for retaining hashtags even using bigrams)
    # s = re.sub(r'[0-9]+', '9', s)  # 1234 -> 9
    s = re.sub(r'\bRT\b', ' ', s, re.IGNORECASE)
    s = re.sub(r'&[a-z]+;', ' ', s, re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    return s.lower()


def vectorize(json_file, vec, dofit=True):
    """ Return a matrix where each row corresponds to a Twitter account, and
    each column corresponds to the number of times a term is used by that
    account. """
    ## CountVectorizer, efficiently.
    screen_names = [x[0] for x in extract_tweets(json_file)]
    if dofit:
        X = vec.fit_transform(x[1] for x in extract_tweets(json_file))
    else:
        X = vec.transform(x[1] for x in extract_tweets(json_file))
    return screen_names, X


def score_words_by_chi2(exemplars, samples, n=300):
    y = np.array(([1.] * exemplars.shape[0]) + ([.0] * samples.shape[0]))
    X = vstack((exemplars, samples)).tocsr()
    clf = linear_model.LogisticRegression(penalty='l2')
    clf.fit(X, y)
    coef = clf.coef_[0]
    chis, pvals = chi2(X, y)
    top_indices = chis.argsort()[::-1]
    top_indices = [i for i in top_indices if coef[i] > 0]
    for idx in range(len(coef)):
        coef[idx] = 0.
    for idx in top_indices[:n]:
        coef[idx] = chis[idx]
    return coef


def do_score(vec, coef):
    return np.sum(coef[vec.nonzero()[1]]) / np.sum(coef)


def analyze_text(brand_tweets_file, exemplar_tweets_file, sample_tweets_file, outfile):
    vec = CountVectorizer(min_df=3, preprocessor=preprocess, ngram_range=(2, 2), binary=True)
    _, exemplar_vectors = vectorize(exemplar_tweets_file, vec, dofit=True)
    brands, brand_vectors = vectorize(brand_tweets_file, vec, dofit=False)
    _, sample_vectors = vectorize(sample_tweets_file, vec, dofit=False)
    print 'read %d exemplars, %d brands, %d sample accounts' % (exemplar_vectors.shape[0],
                                                                brand_vectors.shape[0],
                                                                sample_vectors.shape[0])
    scores = score_words_by_chi2(exemplar_vectors, sample_vectors)
    vocab = vec.get_feature_names()
    print 'top 10 ngrams:\n', '\n'.join(['%s=%.4g' % (vocab[i], scores[i]) for i in np.argsort(scores)[::-1][:10]])
    outf = open(outfile, 'wt')
    for bi, brand_vec in enumerate(brand_vectors):
        outf.write('%s %f\n' % (brands[bi], do_score(brand_vec, scores)))
        outf.flush()


### FOLLOWER ANALYSIS ###


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
