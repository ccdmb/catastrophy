"""
"""

from catas.parsers import parse_dbcan_output
from catas.counts import cazy_counts
from catas.pipeline import predict
from catas.data import test_dbcan


import pytest
import pandas as pd

from numpy.testing import assert_almost_equal


@pytest.mark.parametrize("version,clss,exp_val", [
    ("v5", "biotroph 3", 0.9230486190150349),
    ("v5", "saprotroph", 0.8919083654247382),
    ("v5", "wilt", 0.0),
    ("v5", "mesotroph - internal", 0.22047031254890714),
    ("v4", "biotroph 3", 0.9233213567655258),
    ("v4", "saprotroph", 0.8913578386735521),
    ("v4", "wilt", 0.0),
    ("v4", "mesotroph - internal", 0.2201692033555083),
])
def test_predict(version, clss, exp_val):
    """ Pretty much a repeat of test_rcds. """

    with open(test_dbcan(version=version), "r") as handle:
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    rcds = predict(counts, version=version, nomenclature="nomenclature3")

    assert isinstance(rcds, pd.Series)
    assert rcds.name == "test"

    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(exp_val, rcds[clss], decimal=5)
    return
