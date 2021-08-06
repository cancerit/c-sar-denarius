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
    if exp_exit:
        with pytest.raises(SystemExit) as e_info:
            serve.check_permissions(os.path.join(DATA_DIR, auth_file))
    else:
        serve.check_permissions(os.path.join(DATA_DIR, auth_file))
        assert True


@pytest.mark.parametrize(
    "auth_file, exp_err, exp_result",
    [
        ("good.yaml", False, ("un", "pw")),
        ("missing_pw.yaml", True, None),
        ("missing_group.yaml", True, None),
    ],
)
def test_02_load_auth(auth_file, exp_err, exp_result):
    if exp_err:
        with pytest.raises(KeyError) as e_info:
            serve.load_auth(os.path.join(DATA_DIR, auth_file))
    else:
        result = serve.load_auth(os.path.join(DATA_DIR, auth_file))
        assert result == exp_result
