#
# Copyright (c) 2021
#
# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>
#
# This file is part of c-sar-denarius.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# 1. The usage of a range of years within a copyright statement contained within
# this distribution should be interpreted as being equivalent to a list of years
# including the first and last year specified and all consecutive years between
# them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
# 2009, 2011-2012’ should be interpreted as being identical to a statement that
# reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
# statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
# identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
# 2009, 2010, 2011, 2012’.
import os
from stat import *

import pytest

from c_sar_denarius import serve

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/serve_chks",
)

YAML_PERMS = {
    "good.yaml": S_IRUSR | S_IRGRP,
    "missing_pw.yaml": S_IRUSR | S_IRGRP,
    "missing_group.yaml": S_IRUSR | S_IRGRP,
    "bad_permissions.yaml": S_IRUSR | S_IRGRP | S_IROTH,
}

# irritating but set the permissions we expect outside the tests
for k, v in YAML_PERMS.items():
    os.chmod(os.path.join(DATA_DIR, k), v)


@pytest.mark.parametrize(
    "auth_file, exp_exit, exp_result",
    [
        ("good.yaml", False, ("un", "pw")),
        ("bad_permissions.yaml", True, None),
    ],
)
def test_01_check_permissions(auth_file, exp_exit, exp_result):
    auth_path = os.path.join(DATA_DIR, auth_file)
    if exp_exit:
        with pytest.raises(SystemExit) as e_info:
            serve.check_permissions(auth_path)
    else:
        serve.check_permissions(auth_path)
        assert True
    # put permissions back for user
    os.chmod(auth_path, S_IRUSR | S_IWUSR)


@pytest.mark.parametrize(
    "auth_file, exp_err, exp_result",
    [
        ("good.yaml", False, ("un", "pw")),
        ("missing_pw.yaml", True, None),
        ("missing_group.yaml", True, None),
    ],
)
def test_02_load_auth(auth_file, exp_err, exp_result):
    auth_path = os.path.join(DATA_DIR, auth_file)
    if exp_err:
        with pytest.raises(KeyError) as e_info:
            serve.load_auth(auth_path)
    else:
        result = serve.load_auth(auth_path)
        assert result == exp_result
    # put permissions back for user
    os.chmod(auth_path, S_IRUSR | S_IWUSR)
