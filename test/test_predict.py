"""
"""

import pytest
from numpy.testing import assert_almost_equal

from catas.parsers import HMMER
from catas.count import cazy_counts_multi
from catas.model import Model

from catas.data import test_files
from catas.data import model_filepath
from catas.data import Version


@pytest.mark.parametrize("version,clss,exp_val", [
    (Version.v5, "monomertroph3", 0.9812805406636743),
    (Version.v5, "saprotroph", 0.8921320075070078),
    (Version.v5, "vasculartroph", 0.0),
    (Version.v5, "mesotroph_intracellular", 0.2208436010079824),
    (Version.v4, "monomertroph3", 0.9809859570141375),
    (Version.v4, "saprotroph", 0.8914947140157209),
    (Version.v4, "vasculartroph", 0.0),
    (Version.v4, "mesotroph_intracellular", 0.22065943949266786),
])
def test_predict(version, clss, exp_val):
    """ Pretty much a repeat of test_rcds. """

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
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    pred = model.predict(counts)
    rcds = pred.rcd

    rcds_dict = dict()
    for res in rcds:
        assert res.label == "test"
        rcds_dict[(res.label, res.nomenclature,
                   res.nomenclature_class)] = res.value

    # Checks that results are accurate to 5 decimal places.
    assert_almost_equal(
        exp_val,
        rcds_dict[("test", "nomenclature3", clss)],
        decimal=5
    )
    return


@pytest.mark.parametrize("version,pc,exp_val", [
    (Version.v4, "pc01", -69.03231189317792),
    (Version.v4, "pc02", -14.24698322300769),
    (Version.v5, "pc01", -68.99783199880511),
    (Version.v5, "pc02", -14.222770776283497),
    (Version.v6, "pc01", -64.99171993939578),
    (Version.v6, "pc02", -13.167624276929748),
])
def test_pca(version, pc, exp_val):

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
        counts = cazy_counts_multi([parsed], ["test"], required_cols)

    pred = model.predict(counts)
    trans = pred.pca

    # Checks that results are accurate to 5 decimal places.
    column_index = trans.columns.index(pc)
    assert_almost_equal(exp_val, trans.arr[0, column_index], decimal=5)
    return
