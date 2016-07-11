#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Collect Twitter data for brands.

usage:
    brandelion collect --tweets --input <file> --output <file> --max=<N>
    brandelion collect --followers --input <file> --output <file> --max=<N> [--loop]
    brandelion collect --exemplars --query <string>  --output <file>

Options
    -h, --help
    -i, --input <file>              File containing list of Twitter accounts, one per line.
    -l, --loop                      If true, keep looping to collect more data continuously.
    -o, --output <file>             File to store results
    -t, --tweets                    Fetch tweets.
    -f, --followers                 Fetch followers
    -e, --exemplars                 Fetch exemplars from Twitter lists
    -q, --query <string>            A single string used to search for Twitter lists.
    -m, --max=<N>                   Maximum number of followers or tweets to collect per account [default: 50000].
"""

from collections import Counter
import datetime
from docopt import docopt
import gzip
import io
import json
import re
import requests
import sys
import time
import traceback
import requests

import twutil


def iter_lines(filename):
    """ Iterate over screen names in a file, one per line."""
    with open(filename, 'rt') as idfile:
        for line in idfile:
            screen_name = line.strip()
            if len(screen_name) > 0:
                yield screen_name.split()[0]


def fetch_followers(account_file, outfile, limit, do_loop):
    """ Fetch up to limit followers for each Twitter account in
    account_file. Write results to outfile file in format:

    screen_name user_id follower_id_1 follower_id_2 ..."""
    print('Fetching followers for accounts in %s' % account_file)
    niters = 1
    while True:
        outf = gzip.open(outfile, 'wt')
        for screen_name in iter_lines(account_file):
            timestamp = datetime.datetime.now().isoformat()
            print('collecting followers for', screen_name)
            followers = twutil.collect.followers_for_screen_name(screen_name, limit)
            if len(followers) > 0:
                outf.write('%s %s %s\n' % (timestamp, screen_name, ' '.join(followers)))
                outf.flush()
            else:
                print('unknown user', screen_name)
        outf.close()
        if not do_loop:
            return
        else:
            if niters == 1:
                outfile = '%s.%d' % (outfile, niters)
            else:
                outfile = outfile[:outfile.rindex('.')] + '.%d' % niters
            niters += 1


def fetch_tweets(account_file, outfile, limit):
    """ Fetch up to limit tweets for each account in account_file and write to
    outfile. """
    print('fetching tweets for accounts in', account_file)
    outf = io.open(outfile, 'wt')
    for screen_name in iter_lines(account_file):
        print('\nFetching tweets for %s' % screen_name)
        for tweet in twutil.collect.tweets_for_user(screen_name, limit):
            outf.write('%s\n' % json.dumps(tweet, ensure_ascii=False))
            outf.flush()


def fetch_lists(keyword, max_results=20):
    """
    Fetch the urls of up to max_results Twitter lists that match the provided keyword.
    >>> len(fetch_lists('politics', max_results=4))
    4
    """
    res_per_page = 8
    start = 0
    results = []
    while len(results) < max_results:
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:twitter.com+inurl:lists+%s&rsz=%d&start=%d' % (keyword,
                                                                                                                               res_per_page,
                                                                                                                               start)
        js = json.loads(requests.get(url).text)
        if not js['responseData']:
            print('something went wrong in google search:\n', js)
            return results[:max_results]
        else:
            for r in js['responseData']['results']:
                results.append(r['url'])
        start += res_per_page
        time.sleep(.4)
    return results[:max_results]


def fetch_list_members(list_url):
    """ Get all members of the list specified by the given url. E.g., https://twitter.com/lore77/lists/libri-cultura-education """
    match = re.match(r'.+twitter\.com\/(.+)\/lists\/(.+)', list_url)
    if not match:
        print('cannot parse list url %s', list_url)
        return []
    screen_name, slug = match.groups()
    print('collecting list %s/%s' % (screen_name, slug))
    return twutil.collect.list_members(slug, screen_name)


def fetch_exemplars(keyword, outfile, n=50):
    """ Fetch top lists matching this keyword, then return Twitter screen
    names along with the number of different lists on which each appers.. """
    list_urls = fetch_lists(keyword, n)
    print('found %d lists for %s' % (len(list_urls), keyword))
    counts = Counter()
    for list_url in list_urls:
        counts.update(fetch_list_members(list_url))
    # Write to file.
    outf = io.open(outfile, 'wt')
    for handle in sorted(counts):
        outf.write('%s\t%d\n' % (handle, counts[handle]))
    outf.close()
    print('saved exemplars to', outfile)


def main():
    args = docopt(__doc__)
    if args['--followers']:
        fetch_followers(args['--input'], args['--output'], int(args['--max']), args['--loop'])
    elif args['--tweets']:
        fetch_tweets(args['--input'], args['--output'], int(args['--max']))
    else:
        fetch_exemplars(args['--query'], args['--output'])


if __name__ == '__main__':
    main()
