import logging
import os
from pathlib import Path

from packaging.version import InvalidVersion
from packaging.version import Version


def c_sar_version(root: str):
    """
    Get and parse c-sar version file from expected location
    """
    ver_file = Path(os.path.join(root, "c-sar.version"))
    version = None
    if ver_file.is_file():
        with open(ver_file, "r") as vfh:
            version = vfh.readline().strip()
        try:
            Version(version)
        except InvalidVersion:
            raise ValueError(f"Version '{version}' does not conform to PEP440")
    else:
        logging.warning(f"Unable to find 'c-sar.version' in result folder, using default structure")
        version = "current"
    return version
