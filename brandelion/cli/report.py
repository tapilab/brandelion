#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate reports to summarize the results.

usage:
    brandelion report --scores <file> --output <directory> [--validation <file>]

Options
    -h, --help
    -o, --output <directory>  Path to write results.
    -v, --validation <file>   File containing third-party scores for each brand by Twitter name, (e.g., surveys), for comparison.
    -s, --scores <file>       File containing the predicted scores for each brand by Twitter name.
"""

from docopt import docopt
import scipy.stats as scistat


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


def main():
    args = docopt(__doc__)
    scores = read_scores(args['--scores'])
    if args['--validation']:
        validate(scores, read_scores(args['--validation']))


if __name__ == '__main__':
    main()
