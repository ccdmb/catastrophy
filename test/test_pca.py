"""
"""

from catas.pca import transform
from catas.counts import cazy_counts
from catas.parsers import parse_dbcan_output

from catas.data import Version
from catas.data import test_dbcan
from catas.data import models

import pytest
import pandas as pd
from numpy.testing import assert_almost_equal


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
        parsed = parse_dbcan_output(handle)
        counts = cazy_counts(parsed, label="test", version=version)

    print(counts)
    model = models(version)
    trans = transform(counts, model=model)

    assert isinstance(trans, pd.Series)

    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(exp_val, trans[pc], decimal=5)
    return
