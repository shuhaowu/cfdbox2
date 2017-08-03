#!/usr/bin/env python3

from setuptools import setup, find_packages


def install_requires():
  with open("requirements.txt") as f:
    for line in f:
      yield line.strip()


def entry_points():
  with open("entry_points.ini") as f:
    return f.read()


setup(
  name="cfdbox2",
  version="0.1",
  description="cfdbox2 general",
  author="Shuhao Wu",
  author_email="shuhao@shuhaowu.com",
  url="https://github.com/shuhaowu/cfdbox2",
  packages=list(find_packages()),
  include_package_data=True,
  entry_points=entry_points(),
)
