"""
"""

import pytest
from numpy.testing import assert_almost_equal

from catas.parsers import DBCAN
from catas.count import cazy_counts_multi
from catas.predict import predict
from catas.predict import transform
from catas.predict import distances
from catas.predict import rcd

from catas.data import test_dbcan
from catas.data import models
from catas.data import centroids
from catas.data import Version
from catas.data import Nomenclature
from catas.data import cazy_list


@pytest.mark.parametrize("version,clss,exp_val", [
    (Version.v5, "biotroph 3", 0.9230486190150349),
    (Version.v5, "saprotroph", 0.8919083654247382),
    (Version.v5, "wilt", 0.0),
    (Version.v5, "mesotroph - internal", 0.22047031254890714),
    (Version.v4, "biotroph 3", 0.9233213567655258),
    (Version.v4, "saprotroph", 0.8913578386735521),
    (Version.v4, "wilt", 0.0),
    (Version.v4, "mesotroph - internal", 0.2201692033555083),
])
def test_predict(version, clss, exp_val):
    """ Pretty much a repeat of test_rcds. """

    with open(test_dbcan(version=version), "r") as handle:
        parsed = DBCAN.from_file(handle)
        required_cols = cazy_list(version)
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    rcds = predict(counts, version, Nomenclature["nomenclature3"])

    assert rcds.rows[0] == "test"

    column_index = rcds.columns.index(clss)
    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(exp_val, rcds.arr[0, column_index], decimal=5)
    return


@pytest.mark.parametrize("version,pc,exp_val", [
    (Version.v4, "pc01", -69.00896835173042),
    (Version.v4, "pc02", -14.168483882671623),
    (Version.v5, "pc01", -68.9655038492295),
    (Version.v5, "pc02", -14.158262281499532),
    (Version.v6, "pc01", -64.99073313231153),
    (Version.v6, "pc02", -13.146559438278567),
])
def test_pca(version, pc, exp_val):

    with open(test_dbcan(version=version), "r") as handle:
        parsed = DBCAN.from_file(handle)
        required_cols = cazy_list(version)
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    print(counts)
    model = models(version)
    trans = transform(counts, model=model)

    # Checks that results are accurate to 5 decimal places.
    column_index = trans.columns.index(pc)
    assert_almost_equal(exp_val, trans.arr[0, column_index], decimal=5)
    return


@pytest.mark.parametrize("version,clss,exp_val", [
    (Version.v5, "biotroph 2", 51.57963882216139),
    (Version.v5, "mesotroph - external", 70.20617822839525),
    (Version.v5, "wilt", 141.11596086281014)
])
def test_distances(version, clss, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = DBCAN.from_file(handle)
        required_cols = cazy_list(version)
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    model = models(version)
    trans = transform(counts, model=model)

    cent = centroids(version)
    dists = distances(trans, centroids=cent)

    # Checks that results are accurate to 5 decimal places.
    column_index = dists.columns.index(clss)
    assert_almost_equal(exp_val, dists.arr[0, column_index], decimal=5)
    return


@pytest.mark.parametrize("version,clss,exp_val", [
    (Version.v5, "biotroph 3", 0.9230486190150349),
    (Version.v5, "saprotroph", 0.8919083654247382),
    (Version.v5, "wilt", 0.0),
    (Version.v5, "mesotroph - internal", 0.22047031254890714),
])
def test_rcd(version, clss, exp_val):
    with open(test_dbcan(version=version), "r") as handle:
        parsed = DBCAN.from_file(handle)
        required_cols = cazy_list(version)
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    model = models(version)
    trans = transform(counts, model=model)

    cent = centroids(version)
    dists = distances(trans, centroids=cent)
    rcds = rcd(dists)

    # Checks that results are accurate to 5 decimal places.
    column_index = rcds.columns.index(clss)
    assert_almost_equal(exp_val, rcds.arr[0, column_index], decimal=5)
    return
