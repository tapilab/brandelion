#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run diagnostics on a dataset.

usage:
    brandelion diagnose --network --brand-followers <file> --exemplar-followers <file> --validation <file> [--network-method <string>]

Options
    -h, --help
    --brand-followers <file>      File containing follower data for brand accounts.
    --exemplar-followers <file>   File containing follower data for exemplar accounts.
    --network-method <string>     Method to do text analysis [default: jaccard]
    -n, --network                 Analyze followers.
    -t, --text                    Analyze text.
    -v, --validation <file>       File containing third-party scores for each brand by Twitter name, (e.g., surveys), for comparison.
"""

from docopt import docopt
import scipy.stats as scistat
import random

from . import analyze, report


random.seed(123)


def read_scores(fname):
    scores = {}
    for line in open(fname):
        parts = line.strip().lower().split()
        if len(parts) > 1:
            scores[parts[0]] = float(parts[1])
    return scores


def validate(scores, validation):
    keys = sorted(validation.keys())
    predicted = [scores[k] for k in keys]
    truth = [validation[k] for k in keys]
    print 'Pearson:', scistat.pearsonr(predicted, truth)


def diagnose_text(brand_tweets_file, exemplar_tweets_file, sample_tweets_file, validation_file):
    pass


def correlation_by_exemplar(brands, exemplars, validation_scores):
    """ Report the overall correlation with the validation scores using each exemplar in isolation. """
    keys = sorted(k for k in validation_scores.keys() if k in set(x[0] for x in brands))
    truth = [validation_scores[k] for k in keys]
    sample = random.sample(keys, 10)
    print 'exemplar\tcorr\tn_followers\texamples\n'
    for exemplar in exemplars:
        single_exemplar = {exemplar: exemplars[exemplar]}
        social_scores = analyze.jaccard(brands, single_exemplar)
        predicted = [social_scores[k] for k in keys]
        print '%10s\t%.3f\t%d\t%s' % (exemplar, scistat.pearsonr(predicted, truth)[0],
                                      len(exemplars[exemplar]),
                                      ' '.join('%.2g' % social_scores[k] for k in sample))


def diagnose_followers(brand_follower_file, exemplar_follower_file, validation_file, analyze_fn):
    brands = analyze.read_follower_file(brand_follower_file).items()
    exemplars = analyze.read_follower_file(exemplar_follower_file)
    print 'read follower data for %d exemplars' % (len(exemplars))
    scores = report.read_scores(validation_file)
    correlation_by_exemplar(brands, exemplars, scores)


def main():
    args = docopt(__doc__)
    print args
    if args['--network']:
        diagnose_followers(args['--brand-followers'], args['--exemplar-followers'], args['--validation'], args['--network-method'])
    if args['--text']:
        diagnose_text(args['--brand-tweets'], args['--exemplar-tweets'], args['--sample-tweets'], args['--validation'], args['--text-method'])


if __name__ == '__main__':
    main()
