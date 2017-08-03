from __future__ import absolute_import, division, print_function

from contextlib import contextmanager
import errno
import os
import os.path


def parse_timesteps(timesteps):
  """
  Possible configurations:

  * => all availabile => None
  100-200 => range(100, 201)
  100-200-10 => range(100, 201, 10)
  """
  timesteps = timesteps.split("-")
  timesteps = list(map(lambda s: s.strip(), timesteps))
  if len(timesteps) == 1:
    if timesteps[0] == "*":
      return []

    if timesteps[0].isdecimal():
      return [timesteps[0]]

    raise ValueError("{} is invalid".format(timesteps))
  else:
    if not all(map(lambda s: s.isdecimal(), timesteps)):
      raise ValueError("timesteps must only include integers")

    timesteps = list(map(int, timesteps))
    if not all(map(lambda t: t >= 0, timesteps)):
      raise ValueError("timesteps must be positive")

    if len(timesteps) == 2:
      return list(range(timesteps[0], timesteps[1] + 1))
    elif len(timesteps) == 3:
      return list(range(timesteps[0], timesteps[1] + 1, timesteps[2]))
    else:
      raise ValueError("timesteps must be presented with a maximum of 3 arguments")


@contextmanager
def chdir(path):
  old_cwd = os.getcwd()
  try:
    os.chdir(path)
    yield
  finally:
    os.chdir(old_cwd)


def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise
