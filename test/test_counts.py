"""
"""

import pytest

from catas.parsers import DBCAN
from catas.count import cazy_counts
from catas.data import Version
from catas.data import test_dbcan
from catas.data import cazy_list


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
    required_cols = cazy_list(version)
    with open(test_dbcan(version=version), "r") as handle:
        parsed = DBCAN.from_file(handle)
        counts = cazy_counts(parsed, required_cols)

    column_index = required_cols.index(hmm)
    assert counts[column_index] == exp_val
    return
