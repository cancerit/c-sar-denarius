#
# Copyright (c) 2021 Genome Research Ltd
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

import pytest

import c_sar_denarius.utils as csdutils

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data/version_chks",
)


@pytest.mark.parametrize(
    "v_set, exp_err, exp_result",
    [
        ("good", False, ("1.2.0", "1.2.0")),
        ("good-extended", False, ("1.2.0a2", "1.2.0")),
        ("bad", True, None),
        ("absent", False, ("?", "1.2.0")),
    ],
)
def test_01_versions(v_set, exp_err, exp_result):
    if exp_err:
        with pytest.raises(
            ValueError,
            match="^Version '.+' does not conform to PEP440$",
        ) as e_info:
            csdutils.c_sar_version(os.path.join(DATA_DIR, v_set))
    else:
        ver = csdutils.c_sar_version(os.path.join(DATA_DIR, v_set))
        assert ver == exp_result
