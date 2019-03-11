"""
"""

import pytest

from catas.parsers import parse_dbcan_output
from catas.counts import cazy_counts
from catas.data import test_dbcan


@pytest.mark.parametrize("version,hmm,exp_val", [
    ("v4", "CBM1", 2),
    ("v4", "GH10", 4),
    ("v4", "GH100", 0),
    ("v5", "CBM1", 2),
    ("v5", "GH3", 3),
    ("v5", "CE10", 0),
    ("v6", "CBM1", 2),
    ("v6", "GH11", 1),
    ("v6", "GH31", 0),
])
def test_cazy_counts(version, hmm, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    assert counts[hmm] == exp_val
    return
