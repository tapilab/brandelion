#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Analyze social and linguistic brand data.

usage:
    brandelion analyze --text --brand-tweets <file> --exemplar-tweets <file> --sample-tweets <file>  --output <file> [--text-method <string>]
    brandelion analyze --network --brand-followers <file> --exemplar-followers <file> --output <file> [--network-method <string>  --min-followers <n> --max-followers <n>  --sample-exemplars <p> --seed <s>]

Options
    -h, --help
    --brand-followers <file>      File containing follower data for brand accounts.
    --brand-tweets <file>         File containing tweets from brand accounts.
    --exemplar-followers <file>   File containing follower data for exemplar accounts.
    --exemplar-tweets <file>      File containing tweets from exemplar accounts.
    --sample-tweets <file>        File containing tweets from representative sample of Twitter.
    --text-method <string>        Method to do text analysis [default: chi2]
    --network-method <string>     Method to do text analysis [default: jaccard]
    -o, --output <file>           File to store results
    -t, --text                    Analyze text of tweets.
    -n, --network                 Analyze followers.
    --min-followers <n>           Ignore exemplars that don't have at least n followers [default: 0]
    --max-followers <n>           Ignore exemplars that have more than least n followers [default: 1e10]
    --sample-exemplars <p>        Sample p percent of the exemplars, uniformly at random. [default: 100]
    --seed <s>                    Seed for random sampling. [default: 12345]
"""

from collections import Counter, defaultdict
from docopt import docopt
import io
from itertools import groupby
import gzip
import json
import math
import numpy as np
import os
import re
import random
from scipy.sparse import vstack
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2 as skchi2
from sklearn import linear_model

from . import report

### TEXT ANALYSIS ###


def parse_json(json_file, include_date=False):
    """ Yield screen_name, text tuples from a json file. """
    if json_file[-2:] == 'gz':
        fh = gzip.open(json_file, 'rt')
    else:
        fh = io.open(json_file, mode='rt', encoding='utf8')
    for line in fh:
        try:
            jj = json.loads(line)
            if type(jj) is not list:
                jj = [jj]
            for j in jj:
                if include_date:
                    yield (j['user']['screen_name'].lower(), j['text'], j['created_at'])
                else:
                    yield (j['user']['screen_name'].lower(), j['text'])
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


def chi2(exemplars, samples, n=300):
    y = np.array(([1.] * exemplars.shape[0]) + ([.0] * samples.shape[0]))
    X = vstack((exemplars, samples)).tocsr()
    clf = linear_model.LogisticRegression(penalty='l2')
    clf.fit(X, y)
    coef = clf.coef_[0]
    chis, pvals = skchi2(X, y)
    top_indices = chis.argsort()[::-1]
    top_indices = [i for i in top_indices if coef[i] > 0]
    for idx in range(len(coef)):
        coef[idx] = 0.
    for idx in top_indices[:n]:
        coef[idx] = chis[idx]
    return coef


def do_score(vec, coef):
    return np.sum(coef[vec.nonzero()[1]]) / np.sum(coef)


def write_top_words(fname, vocab, scores):
    outf = io.open(fname, 'w', encoding='utf8')
    for i in np.argsort(scores)[::-1]:
        if scores[i] > 0:
            outf.write('%s %g\n' % (vocab[i], scores[i]))
    outf.close()


def analyze_text(brand_tweets_file, exemplar_tweets_file, sample_tweets_file, outfile, analyze_fn):
    analyze = getattr(sys.modules[__name__], analyze_fn)

    vec = CountVectorizer(min_df=3, preprocessor=preprocess, ngram_range=(2, 2), binary=True)
    _, exemplar_vectors = vectorize(exemplar_tweets_file, vec, dofit=True)
    print('read tweets for %d exemplar accounts' % exemplar_vectors.shape[0])
    brands, brand_vectors = vectorize(brand_tweets_file, vec, dofit=False)
    print('read tweets for %d brand accounts' % brand_vectors.shape[0])
    _, sample_vectors = vectorize(sample_tweets_file, vec, dofit=False)
    print('read tweets for %d sample accounts' % sample_vectors.shape[0])

    scores = analyze(exemplar_vectors, sample_vectors)
    vocab = vec.get_feature_names()
    write_top_words(outfile + '.topwords', vocab, scores)
    print('top 10 ngrams:\n', '\n'.join(['%s=%.4g' % (vocab[i], scores[i]) for i in np.argsort(scores)[::-1][:10]]))
    outf = open(outfile, 'wt')
    for bi, brand_vec in enumerate(brand_vectors):
        outf.write('%s %g\n' % (brands[bi], do_score(brand_vec, scores)))
        outf.flush()


### FOLLOWER ANALYSIS ###

def get_twitter_handles(fname):
    handles = set()
    with open(fname, 'rt') as f:
        for line in f:
            handles.add(line[:90].split()[0].lower())
    return handles


def read_follower_file(fname, min_followers=0, max_followers=1e10, blacklist=set()):
    """ Read a file of follower information and return a dictionary mapping screen_name to a set of follower ids. """
    result = {}
    with open(fname, 'rt') as f:
        for line in f:
            parts = line.split()
            if len(parts) > 3:
                if parts[1].lower() not in blacklist:
                    followers = set(int(x) for x in parts[2:])
                    if len(followers) > min_followers and len(followers) <= max_followers:
                        result[parts[1].lower()] = followers
                else:
                    print('skipping exemplar', parts[1].lower())
    return result


def iter_follower_file(fname):
    """ Iterator from a file of follower information and return a tuple of screen_name, follower ids.
    File format is:
    <iso timestamp> <screen_name> <follower_id1> <follower_ids2> ...
    """
    with open(fname, 'rt') as f:
        for line in f:
            parts = line.split()
            if len(parts) > 3:
                yield parts[1].lower(), set(int(x) for x in parts[2:])


# JACCARD


def _jaccard(a, b):
    """ Return the Jaccard similarity between two sets a and b. """
    return 1. * len(a & b) / len(a | b)


def jaccard(brands, exemplars, weighted_avg=False, sqrt=False):
    """ Return the average Jaccard similarity between a brand's followers and the
    followers of each exemplar. """
    scores = {}
    for brand, followers in brands:
        if weighted_avg:
            scores[brand] = np.average([_jaccard(followers, others) for others in exemplars.values()],
                                       weights=[1. / len(others) for others in exemplars.values()])
        else:
            scores[brand] = 1. * sum(_jaccard(followers, others) for others in exemplars.values()) / len(exemplars)
        # limit to exemplars with less than 40k followers:  scores[brand] = 1. * sum(_jaccard(brands[brand], others) for others in exemplars.itervalues() if len(others) < 40000) / len(exemplars)
    if sqrt:
        scores = dict([(b, math.sqrt(s)) for b, s in scores.items()])
    return scores


def jaccard_weighted_avg(brands, exemplars):
    return jaccard(brands, exemplars, True, False)


def jaccard_sqrt_no_weighted_avg(brands, exemplars):
    return jaccard(brands, exemplars, False, True)


def jaccard_sqrt(brands, exemplars):
    return jaccard(brands, exemplars, weighted_avg=True, sqrt=True)


def jaccard_merge(brands, exemplars):
    """ Return the average Jaccard similarity between a brand's followers and
    the followers of each exemplar. We merge all exemplar followers into one
    big pseudo-account."""
    scores = {}
    exemplar_followers = set()
    for followers in exemplars.values():
        exemplar_followers |= followers

    for brand, followers in brands:
        scores[brand] = _jaccard(followers, exemplar_followers)
    return scores


def compute_log_degrees(brands, exemplars):
    """ For each follower, let Z be the total number of brands they follow.
    Return a dictionary of 1. / log(Z), for each follower.
    """
    counts = Counter()
    for followers in brands.values():  # + exemplars.values():  # Include exemplars in these counts? No, don't want to penalize people who follow many exemplars.
        counts.update(followers)
    counts.update(counts.keys())  # Add 1 to each count.
    for k in counts:
        counts[k] = 1. / math.log(counts[k])
    return counts


# PROPORTION


def _proportion(a, b):
    """ Return the len(a & b) / len(a) """
    return 1. * len(a & b) / len(a)


def proportion(brands, exemplars, weighted_avg=False, sqrt=False):
    """
    Return the proportion of a brand's followers who also follow an exemplar.
    """
    scores = {}
    for brand, followers in brands:
        if weighted_avg:
            scores[brand] = np.average([_proportion(followers, others) for others in exemplars.values()],
                                       weights=[1. / len(others) for others in exemplars.values()])
        else:
            scores[brand] = 1. * sum(_proportion(followers, others) for others in exemplars.values()) / len(exemplars)
    if sqrt:
        scores = dict([(b, math.sqrt(s)) for b, s in scores.items()])
    return scores


def proportion_weighted_avg(brands, exemplars):
    return proportion(brands, exemplars, weighted_avg=True, sqrt=False)


def proportion_sqrt_no_weighted_avg(brands, exemplars):
    return proportion(brands, exemplars, weighted_avg=False, sqrt=True)


def proportion_sqrt(brands, exemplars):
    return proportion(brands, exemplars, weighted_avg=True, sqrt=True)


def proportion_merge(brands, exemplars):
    """ Return the proportion of a brand's followers who also follower an
    exemplar. We merge all exemplar followers into one big pseudo-account."""
    scores = {}
    exemplar_followers = set()
    for followers in exemplars.values():
        exemplar_followers |= followers

    for brand, followers in brands:
        scores[brand] = _proportion(followers, exemplar_followers)
    return scores


# COSINE SIMILARITY


def _cosine(a, b):
    """ Return the len(a & b) / len(a) """
    return 1. * len(a & b) / (math.sqrt(len(a)) * math.sqrt(len(b)))


def cosine(brands, exemplars, weighted_avg=False, sqrt=False):
    """
    Return the cosine similarity betwee a brand's followers and the exemplars.
    """
    scores = {}
    for brand, followers in brands:
        if weighted_avg:
            scores[brand] = np.average([_cosine(followers, others) for others in exemplars.values()],
                                       weights=[1. / len(others) for others in exemplars.values()])
        else:
            scores[brand] = 1. * sum(_cosine(followers, others) for others in exemplars.values()) / len(exemplars)
    if sqrt:
        scores = dict([(b, math.sqrt(s)) for b, s in scores.items()])
    return scores


def cosine_weighted_avg(brands, exemplars):
    return cosine(brands, exemplars, weighted_avg=True, sqrt=False)


def cosine_sqrt_no_weighted_avg(brands, exemplars):
    return cosine(brands, exemplars, weighted_avg=False, sqrt=True)


def cosine_sqrt(brands, exemplars):
    return cosine(brands, exemplars, weighted_avg=True, sqrt=True)


def cosine_merge(brands, exemplars):
    """ Return the proportion of a brand's followers who also follower an
    exemplar. We merge all exemplar followers into one big pseudo-account."""
    scores = {}
    exemplar_followers = set()
    for followers in exemplars.values():
        exemplar_followers |= followers

    for brand, followers in brands:
        scores[brand] = _cosine(followers, exemplar_followers)
    return scores


def adamic(brands, exemplars):
    """ Return the average Adamic/Adar similarity between a brand's followers
    and the followers of each exemplar. We approximate the number of followed
    accounts per user by only considering those in our brand set."""
    print('adamic deprecated...requires loading all brands in memory.')
    return
    degrees = compute_log_degrees(brands, exemplars)
    scores = {}
    exemplar_sums = dict([(exemplar, sum(degrees[z] for z in exemplars[exemplar])) for exemplar in exemplars])

    for brand in sorted(brands):
        brand_sum = sum(degrees[z] for z in brands[brand])
        total = 0.
        for exemplar in exemplars:
            total += sum(degrees[z] for z in brands[brand] & exemplars[exemplar]) / (brand_sum + exemplar_sums[exemplar])
        scores[brand] = total / len(exemplars)
    return scores


def compute_rarity_scores(exemplars):
    """ Compute a score for each follower that is sum_i (1/n_i), where n_i is
    the degree of the ith exemplar they follow.
    >>> compute_rarity_scores({'e1':{1,2,3,4}, 'e2':{4,5}}).items()
    [(1, 0.25), (2, 0.25), (3, 0.25), (4, 0.75), (5, 0.5)]
    """
    scores = defaultdict(lambda: 0.)
    for followers in exemplars.values():
        score = 1. / len(followers)
        for f in followers:
            scores[f] += score
    return scores


def rarity(brands, exemplars):
    """ Compute a score for each follower that is sum_i (1/n_i), where n_i is the degree of the ith exemplar they follow.
    The score for a brand is then the average of their follower scores."""
    rarity = compute_rarity_scores(exemplars)
    scores = {}
    for brand, followers in brands:
        scores[brand] = sum(rarity[f] for f in followers) / len(followers)
    return scores


def compute_rarity_scores_log(exemplars):
    """ Compute a score for each follower that is sum_i (1/n_i), where n_i is
    the degree of the ith exemplar they follow.
    >>> compute_rarity_scores({'e1':{1,2,3,4}, 'e2':{4,5}}).items()
    [(1, 0.25), (2, 0.25), (3, 0.25), (4, 0.75), (5, 0.5)]
    """
    scores = defaultdict(lambda: 0.)
    for followers in exemplars.values():
        score = 1. / math.log(len(followers))
        for f in followers:
            scores[f] += score
    return scores


def rarity_log(brands, exemplars):
    """ Compute a score for each follower that is sum_i (1/log(n_i)), where n_i is the degree of the ith exemplar they follow.
    The score for a brand is then the average of their follower scores."""
    rarity = compute_rarity_scores_log(exemplars)
    scores = {}
    for brand, followers in brands:
        scores[brand] = sum(rarity[f] for f in followers) / len(followers)
    return scores


def mkdirs(filename):
    report.mkdirs(os.path.dirname(filename))


def analyze_followers(brand_follower_file, exemplar_follower_file, outfile, analyze_fn,
                      min_followers, max_followers, sample_exemplars):
    brands = iter_follower_file(brand_follower_file)
    exemplars = read_follower_file(exemplar_follower_file, min_followers=min_followers, max_followers=max_followers, blacklist=get_twitter_handles(brand_follower_file))
    print('read follower data for %d exemplars' % (len(exemplars)))
    if sample_exemplars < 100:  # sample a subset of exemplars.
        exemplars = dict([(k, exemplars[k]) for k in random.sample(exemplars.keys(), int(len(exemplars) * sample_exemplars / 100.))])
        print('sampled %d exemplars' % (len(exemplars)))
    analyze = getattr(sys.modules[__name__], analyze_fn)
    scores = analyze(brands, exemplars)
    mkdirs(outfile)
    outf = open(outfile, 'wt')
    for brand in sorted(scores):
        outf.write('%s %g\n' % (brand, scores[brand]))
        outf.flush()
    outf.close()
    print('results written to', outfile)


def main():
    args = docopt(__doc__)
    print(args)
    if '--seed' in args:
        random.seed(args['--seed'])
    if args['--network']:
        analyze_followers(args['--brand-followers'], args['--exemplar-followers'], args['--output'], args['--network-method'],
                          int(args['--min-followers']), int(float(args['--max-followers'])), float(args['--sample-exemplars']))
    if args['--text']:
        analyze_text(args['--brand-tweets'], args['--exemplar-tweets'], args['--sample-tweets'], args['--output'], args['--text-method'])


if __name__ == '__main__':
    main()
