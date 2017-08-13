from __future__ import absolute_import, division, print_function

import csv
import math
import os


BLASIUS_DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "blasius-solution.csv")

RAW_BLASIUS_SOLUTION = []
with open(BLASIUS_DATA_PATH) as f:
  reader = csv.reader(f)
  for i, line in enumerate(reader):
    if i == 0:
      continue

    RAW_BLASIUS_SOLUTION.append(list(map(float, line)))


def velocity_profile_at(x, u0, nu):
  blasius_ys = []
  blasius_profile = []
  for eta, feta in RAW_BLASIUS_SOLUTION:
    blasius_ys.append(eta / math.sqrt(u0 / (2 * nu * x)))
    blasius_profile.append(feta * u0)

  return blasius_ys, blasius_profile
