#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Collect Twitter data for brands.

usage:
    brandelion collect (--tweets | --followers) --input <file> --output <file> --max=<N>

Options
    -h, --help
    -i, --input <file>              File containing list of Twitter accounts, one per line.
    -o, --output <file>             File to store results
    -t, --tweets                    Fetch tweets.
    -f, --followers                 Fetch followers
    -m, --max=<N>                   Maximum number of followers or tweets to collect per account [default: 1e10].
"""

from docopt import docopt
import io
import json

import twutil


def iter_lines(filename):
    """ Iterate over screen names in a file, one per line."""
    with open(filename, 'rb') as idfile:
        for line in idfile:
            screen_name = line.strip()
            if len(screen_name) > 0:
                yield screen_name


def fetch_followers(account_file, outfile, limit):
    """ Fetch up to limit followers for each Twitter account in
    account_file. Write results to outfile file in format:

    screen_name user_id follower_id_1 follower_id_2 ...
    """
    print 'Fetching followers for accounts in', account_file
    outf = open(outfile, 'wb')
    for screen_name in iter_lines(account_file):
        ids = list(twutil.collect.lookup_ids([screen_name]))
        if len(ids) > 0:
            print 'collecting followers for', screen_name
            id_ = ids[0]
            followers = twutil.collect.followers_for_id(id_, limit)
            if len(followers) > 0:
                outf.write('%s %s %s\n' % (screen_name, id_, ' '.join(followers)))
                outf.flush()
        else:
            print 'unknown user', screen_name


def fetch_tweets(account_file, outfile, limit):
    """ Fetch up to limit tweets for each account in account_file and write to
    outfile. """
    print 'fetching tweets for accounts in', account_file
    outf = io.open(outfile, 'wt', encoding='utf8')
    for screen_name in iter_lines(account_file):
        print('\nFetching tweets for %s' % screen_name)
        for tweet in twutil.collect.tweets_for_user(screen_name, limit):
            outf.write('%s\n' % json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
            outf.flush()


def main():
    args = docopt(__doc__)
    action = fetch_followers if args['--followers'] else fetch_tweets
    action(args['--input'], args['--output'], int(args['--max']))


if __name__ == '__main__':
    main()
