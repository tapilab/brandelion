#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A social media brand analysis tool.

usage: brandelion [--help] <command> [<args>...]

The most commonly used brandelion commands are:
     analyze    Compute brand analytics scores.
     collect    Collect brand Twitter information.
     diagnose   Run diagnostics.
     report     Summarize the results of the analysis
See 'brandelion help <command>' for more information on a specific command.

"""
from subprocess import call
from docopt import docopt

from .. import __version__

CMDS = ['analyze', 'collect', 'diagnose', 'report']


def main():
    args = docopt(__doc__,
                  version='brandelion version ' + __version__,
                  options_first=True)

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in CMDS:
        exit(call(['brandelion-%s' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['brandelion', '--help']))
    else:
        exit("%r is not a brandelion command. See 'brandelion help'." % args['<command>'])


if __name__ == '__main__':
    main()
