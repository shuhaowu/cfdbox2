from contextlib import contextmanager
import errno
import logging
import os

import paramiko

if os.environ.get("PARAMIKO_VERBOSE"):
  logging.getLogger("paramiko").setLevel(logging.DEBUG)

SSH_PROTOCOL_ERROR_RETRIES = 5


def available():
  return os.environ.get("SFTP_SERVER") and os.environ.get("SFTP_USER") and os.environ.get("SFTP_PASSWORD")


# TODO: therem ust be a better way to write this function
def path_exists(path, c=None):
  def exists(c):
    ex = True
    try:
      c.stat(path)
    except IOError as e:
      if e.errno == errno.ENOENT:
        ex = False
      else:
        raise e

    return ex

  if c is None:
    with client() as c:
      return exists(c)
  else:
    return exists(c)


@contextmanager
def client(logger=None):
  if logger is None:
    logger = logging.getLogger("sftp_client")
    logger.setLevel(logging.DEBUG)

  if not available():
    raise ValueError("environmental variable $SFTP_SERVER, $SFTP_USER, and $SFTP_PASSWORD is required")

  sftp_server, sftp_user, sftp_password = os.environ["SFTP_SERVER"], os.environ["SFTP_USER"], os.environ["SFTP_PASSWORD"]

  try:
    sftp_port = int(os.environ.get("SFTP_PORT", 22))
  except ValueError:
    raise ValueError("SFTP_PORT is not an integer: {0}".format(os.environ.get("SFTP_PORT")))

  try:
    connected = False
    e = None
    for i in range(0, SSH_PROTOCOL_ERROR_RETRIES):
      logger.info("trying to connect to {0}@{1} (port {2}) attempt {3}".format(sftp_user, sftp_server, sftp_port, i))
      transport = paramiko.Transport((sftp_server, sftp_port))
      try:
        transport.connect(username=sftp_user, password=sftp_password)
      except paramiko.SSHException as e:
        if str(e) == "Error reading SSH protocol banner":
          transport.close()
          logger.warning("failed to connect with {0}, retrying...".format(str(e)))
          continue
        raise e
      else:
        logger.info("connected to {0}@{1} (port {2})".format(sftp_user, sftp_server, sftp_port))
        connected = True
        break

    if not connected:
      raise paramiko.SSHException("cannot connect to SSH even after {0} retries: {1}".format(SSH_PROTOCOL_ERROR_RETRIES, str(e)))

    sftp = paramiko.SFTPClient.from_transport(transport)
    logger.debug("Can see the following directory listings: {0}".format(" ".join(sftp.listdir())))

    yield sftp
  finally:
    sftp.close()
    transport.close()

    logger.info("disconnected from {0}@{1} (port {2})".format(sftp_user, sftp_server, sftp_port))
