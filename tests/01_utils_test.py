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
