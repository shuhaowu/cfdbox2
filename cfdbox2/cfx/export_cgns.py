from __future__ import absolute_import, division, print_function

import argparse
from datetime import datetime
import logging
import os
import subprocess

from .. import utils, cmdline
from ..utils import sftp

CFX5EXPORT = "cfx5export"
GZIP = "gzip"


class ExportCgns(object):
  """
  This exports CFX results into CGNS via the `cfx5export` command. This is
  more or less just a wrapper around cfx5export and gzip, to save space.

  Unfortunately, due to the lack of a mounted file system of sort to the
  storage NAS, I have to use SFTP here, although this functionality can be
  turned off.
  """

  @classmethod
  def main(cls, argv):
    parser = argparse.ArgumentParser(description="exports CFX results into CGNS")

    parser.add_argument("--sftp-trn", action="store_true",
                        help="hint for the exporter to use sftp to locate the trn files")
    parser.add_argument("--sftp-res", action="store_true",
                        help="hint for the exporter to use sftp to locate the res file")
    parser.add_argument("--sftp-export", action="store_true",
                        help="hint for the exporter to upload to sftp as soon")
    parser.add_argument("--gzip-export", action="store_true",
                        help="hint for the exporter to gzip after export")
    parser.add_argument("--local-tmp-dir", nargs="?", default="{}/tmp".format(os.environ.get("HOME", "")),
                        help="the temp dir for the export to start from, hard links will be made to that directory for local exports and downloads will be made to there")

    parser.add_argument("-t", "--timesteps", required=True,
                        help="the timesteps to export, in standard timesteps format (start[-end-step], does not include end)")
    parser.add_argument("-d", "--trn-directory", nargs="?", default=None,
                        help="the path to the trn directory")

    parser.add_argument("res_file",
                        help="the path to the .res file to export from")
    parser.add_argument("export_dir", nargs="?", default=None,
                        help="the path to the exported files. default: None, which will export into a subdir of local-tmp-dir, will display at the end")

    known_args, extra_args = parser.parse_known_args(args=argv[1:])

    if known_args.sftp_export:
      raise NotImplementedError

    if known_args.sftp_trn or known_args.sftp_res or known_args.sftp_export:
      if not sftp.available():
        cmdline.fatal("sftp support is not available, please fill out sftprc")

    if not known_args.sftp_res and not os.path.exists(known_args.res_file):
      cmdline.fatal("{} is not valid locally".format(known_args.res_file))
    elif known_args.sftp_res and not sftp.path_exists(known_args.res_file):
      cmdline.fatal("{} is not valid on sftp".format(known_args.res_file))

    if not known_args.sftp_trn and not os.path.exists(known_args.trn_directory):
      cmdline.fatal("{} is not valid locally".format(known_args.trn_directory))
    elif known_args.sftp_trn and not sftp.path_exists(known_args.trn_directory):
      cmdline.fatal("{} is not valid on sftp".format(known_args.trn_directory))

    try:
      known_args.timesteps = utils.parse_timesteps(known_args.timesteps)
    except ValueError:
      cmdline.fatal("timesteps must be in standard format")

    if not known_args.sftp_trn:
      for t in known_args.timesteps:
        p = os.path.join(known_args.trn_directory, "{}.trn".format(t))
        if not os.path.exists(p):
          cmdline.fatal("{} is not valid locally".format(p))
    else:
      with sftp.client() as c:
        for t in known_args.timesteps:
          p = os.path.join(known_args.trn_directory, "{}.trn".format(t))
          if not sftp.path_exists(p, c):
            cmdline.fatal("{} is not valid on sftp".format(p))

    app = cls(known_args, extra_args)
    app.run()

  def __init__(self, known_args, extra_args):
    self.logger = logging.getLogger("export_cgns")
    self.args = known_args
    self.extra_args = extra_args

  def run(self):
    self._setup_tmp_dir()
    for t in self.args.timesteps:
      if self.args.sftp_trn:
        self._download(t)

      self._export(t)
      self._delete_trn(t)

      if self.args.gzip_export:
        self._compress(t)

      if self.args.sftp_export:
        raise NotImplementedError
        self._upload(t)
        self._delete(t)

  def _setup_tmp_dir(self):
    jobname = os.path.splitext(os.path.basename(self.args.res_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    self.basedir = os.path.join(self.args.local_tmp_dir, "{}-{}".format(jobname, timestamp))
    self.logger.info("run basedir: {}".format(self.basedir))

    self.trn_path = os.path.join(self.basedir, jobname)
    utils.mkdir_p(self.trn_path)
    self.res_path = os.path.join(self.basedir, os.path.basename(self.args.res_file))

    if not self.args.sftp_trn:
      self.logger.warn("FIXME: should be hard linking trn files, but is symlinking the dir instead")
      src = os.path.abspath(self.args.trn_directory)
      os.symlink(src, self.trn_path)
      self.logger.info("{} -> {}".format(src, self.trn_path))

    if not self.args.sftp_res:
      src = os.path.abspath(self.args.res_file)
      os.link(src, self.res_path)
      self.logger.info("{} -> {}".format(src, self.res_path))
    else:
      self._download_res()

    if not self.args.export_dir:
      self.args.export_dir = os.path.join(self.basedir, "cgns-exports")

    utils.mkdir_p(self.args.export_dir)

    self.logger.info("export dir will be: {}".format(self.args.export_dir))

  def _download(self, t):
    filename = "{}.trn".format(t)
    sftp_path = os.path.join(self.args.trn_directory, filename)
    local_path = os.path.join(self.trn_path, filename)
    with sftp.client() as c:
      self.logger.info("downloading {} -> {}".format(sftp_path, local_path))
      c.get(sftp_path, local_path)

  def _download_res(self):
    sftp_path = self.args.res_file
    local_path = self.res_path

    with sftp.client() as c:
      self.logger.info("downloading {} -> {}".format(sftp_path, local_path))
      c.get(sftp_path, local_path)

  def _export(self, t):
    t = str(t)
    cmd = ["cfx5export", "-cgns", "-out", os.path.join(self.args.export_dir, t), "-t", t]
    cmd.extend(self.extra_args)
    cmd.append(self.res_path)
    self.logger.info(cmd)
    subprocess.check_call(cmd)

  def _delete_trn(self, t):
    filename = "{}.trn".format(t)
    local_path = os.path.join(self.trn_path, filename)
    os.remove(local_path)

  def _compress(self, t):
    t = str(t)
    cmd = ["gzip", "{}.cgns".format(os.path.join(self.args.export_dir, t))]
    self.logger.info(cmd)
    subprocess.check_call(cmd)

  def _upload(self, t):
    raise NotImplementedError

  def _delete(self, t):
    raise NotImplementedError
