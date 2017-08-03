from __future__ import absolute_import, division, print_function

import sys


def fatal(msg):
  print("error: {}".format(msg), file=sys.stderr)
  sys.exit(1)
