from __future__ import absolute_import, division, print_function

import logging
import pkg_resources
import os.path
import sys

from . import cmdline

ENTRYPOINT = "cfdbox2.apps"


def main(argv=sys.argv):
  if len(argv) < 2:
    help(argv)
    sys.exit(0)

  logging.basicConfig(format="[%(asctime)s][%(name)s][%(levelname).1s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG)

  app = argv[1]
  argv = argv[1:]
  apps = load_apps()

  if app not in apps:
    cmdline.fatal("unknown command {}".format(app))

  apps[app](argv)


def help(argv):
  cfdbox2name = os.path.basename(sys.argv[0])
  print("usage: {} COMMAND [options]".format(cfdbox2name))
  print("")
  print("tip: type `{} list` to see the list of possible commands".format(cfdbox2name))


def list(argv):
  apps = load_apps()
  apps = sorted(apps.keys())
  for app_name in apps:
    print("-", app_name)


def load_apps():
  apps = {}
  for entry_point in pkg_resources.iter_entry_points(ENTRYPOINT):
    apps[entry_point.name] = entry_point.load()

  return apps
