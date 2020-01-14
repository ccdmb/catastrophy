"""
"""

import pytest

from catas.parsers import HMMER
from catas.count import cazy_counts
from catas.model import Model
from catas.data import Version
from catas.data import model_filepath
from catas.data import test_files


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
    with open(model_filepath(version), "rb") as handle:
        model = Model.read(handle)

    required_cols = list(model.hmm_lengths.keys())

    files = test_files(version)
    with open(files["hmmer_text"], "r") as handle:
        parsed = HMMER.from_file(
            handle,
            model.hmm_lengths,
            "hmmer3-text",
        )
        counts = cazy_counts(parsed, required_cols)

    column_index = required_cols.index(hmm)
    assert counts[column_index] == exp_val
    return
