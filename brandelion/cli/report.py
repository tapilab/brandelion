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
import errno
import os
import matplotlib.pyplot as plt
import scipy.stats as scistat


def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def read_scores(fname):
    scores = {}
    for line in open(fname):
        parts = line.strip().lower().split()
        if len(parts) > 1:
            scores[parts[0]] = float(parts[1])
    return scores


def validate(scores, validation, title, outdir, doplot=True):
    keys = sorted(validation.keys())
    keys = list(set(keys) & set(scores.keys()))
    predicted = [scores[k] for k in keys]
    truth = [validation[k] for k in keys]
    corr = scistat.pearsonr(predicted, truth)
    print('Pearson:', corr)
    if doplot:
        plt.figure()
        plt.scatter(predicted, truth)
        plt.xlabel('predicted')
        plt.ylabel('truth')
        plt.xlim(min(predicted), max(predicted))
        plt.ylim(min(truth), max(truth))
        for x, y, label in zip(predicted, truth, keys):
            plt.annotate(label, xy=(x, y), xytext=(0, 0),
                         textcoords='offset points', size='10',
                         bbox=dict(boxstyle='round,pad=0.0', edgecolor='white',
                                   fc='white', alpha=0.9))
            plt.title('%s\nr(%d)=%.3f (p=%g)' % (title, len(truth), corr[0], corr[1]))
        plt.savefig(outdir + '/scatter.pdf')
        plt.show()
    return corr[0]


def main():
    args = docopt(__doc__)
    scores = read_scores(args['--scores'])
    mkdirs(args['--output'])
    if args['--validation']:
        validate(scores, read_scores(args['--validation']), '', args['--output'])


if __name__ == '__main__':
    main()
