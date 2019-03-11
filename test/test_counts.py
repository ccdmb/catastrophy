"""
"""

import pytest

from catas.parsers import parse_dbcan_output
from catas.counts import cazy_counts
from catas.data import Version
from catas.data import test_dbcan


@pytest.mark.parametrize("version,hmm,exp_val", [
    (Version.v4, "CBM1", 2),
    (Version.v4, "GH10", 4),
    (Version.v4, "GH100", 0),
    (Version.v5, "CBM1", 2),
    (Version.v5, "GH3", 3),
    (Version.v5, "CE10", 0),
    (Version.v6, "CBM1", 2),
    (Version.v6, "GH11", 1),
    (Version.v6, "GH31", 0),
])
def test_cazy_counts(version, hmm, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    assert counts[hmm] == exp_val
    return
