import pytest

import c_sar_denarius.markdown as csdmd


@pytest.mark.parametrize(
    "version, config_ver",
    [
        ("1.2.0", "1.2.0"),
        ("?", "1.2.0"),
    ],
)
def test_01_versions(version, config_ver):
    assert isinstance(csdmd.structure_yaml(version, config_ver), dict)
