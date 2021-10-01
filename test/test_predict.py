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
    (Version.v10, "monomertroph3", 1.0),
    (Version.v10, "saprotroph", 0.8773836040317411),
    (Version.v10, "vasculartroph", 0.0),
    (Version.v10, "mesotroph_intracellular", 0.08630181053724584),
    (Version.v5, "monomertroph3", 0.9676738995420295),
    (Version.v5, "saprotroph", 0.8796622614136591),
    (Version.v5, "vasculartroph", 0.0),
    (Version.v5, "mesotroph_intracellular", 0.21770575123709068),
    (Version.v4, "monomertroph3", 0.9674518271503275),
    (Version.v4, "saprotroph", 0.879052715572339),
    (Version.v4, "vasculartroph", 0.0),
    (Version.v4, "mesotroph_intracellular", 0.21759385711517643),
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
    (Version.v4, "pc01", -69.59756347101215),
    (Version.v4, "pc02", -13.422481929003107),
    (Version.v5, "pc01", -69.56184489008383),
    (Version.v5, "pc02", -13.395714644864263),
    (Version.v6, "pc01", -65.58320320620606),
    (Version.v6, "pc02", -11.363653203632293),
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
