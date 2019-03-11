"""
"""

from catas.pca import transform
from catas.parsers import parse_dbcan_output
from catas.counts import cazy_counts
from catas.centroids import distances
from catas.centroids import rcd

from catas.data import test_dbcan
from catas.data import models
from catas.data import centroids

import pytest
import pandas as pd

from numpy.testing import assert_almost_equal


@pytest.mark.parametrize("version,clss,exp_val", [
    ("v5", "biotroph 2", 51.57963882216139),
    ("v5", "mesotroph - external", 70.20617822839525),
    ("v5", "wilt", 141.11596086281014)
])
def test_distances(version, clss, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    model = models(version)
    trans = transform(counts, model=model)

    cent = centroids(version)
    dists = distances(trans, centroids=cent)

    assert isinstance(dists, pd.Series)

    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(exp_val, dists[clss], decimal=5)
    return


@pytest.mark.parametrize("version,clss,exp_val", [
    ("v5", "biotroph 3", 0.9230486190150349),
    ("v5", "saprotroph", 0.8919083654247382),
    ("v5", "wilt", 0.0),
    ("v5", "mesotroph - internal", 0.22047031254890714),
])
def test_rcd(version, clss, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    model = models(version)
    trans = transform(counts, model=model)

    cent = centroids(version)
    dists = distances(trans, centroids=cent)
    rcds = rcd(dists)

    assert isinstance(rcds, pd.Series)

    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(exp_val, rcds[clss], decimal=5)
    return
