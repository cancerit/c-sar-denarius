import logging
import os
import sys
from stat import S_IROTH
from stat import S_IWOTH
from stat import S_IXOTH

import yaml
from sauth import serve_http
from sauth import SimpleHTTPAuthHandler

from c_sar_denarius.constants import DEFAULT_GRP
from c_sar_denarius.constants import DEFAULT_PW

PERMISSIONS_FLAG: int = S_IROTH | S_IWOTH | S_IXOTH


def check_permissions(filename):
    # Check Unix permissions
    if os.name == "posix" and os.stat(filename).st_mode & PERMISSIONS_FLAG:
        logging.critical(f"'{filename}' is unprotected (run 'chmod o-rwx {filename}')!")
        sys.exit(1)


def load_auth(filename):
    check_permissions(filename)
    (group, pw) = (None, None)
    with open(filename, "r") as fo:
        y = yaml.safe_load(fo)
        group = y["group"]
        pw = y["pw"]
    return (group, pw)


def site(target, authfile, port, https):
    start_dir = os.path.join(target, "site")
    if authfile:
        (group, pw) = load_auth(authfile)
    else:
        logging.warning("Site running with, default user/pw values for authentication")
        (group, pw) = (DEFAULT_GRP, DEFAULT_PW)
    SimpleHTTPAuthHandler.username = group  # as that's how we restrict
    SimpleHTTPAuthHandler.password = pw
    serve_http(
        ip="0.0.0.0",
        port=port,
        https=https,
        start_dir=start_dir,
        handler_class=SimpleHTTPAuthHandler,
    )
