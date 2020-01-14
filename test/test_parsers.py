import pytest

from catas.data import Version
from catas.data import model_filepath
from catas.data import test_files
from catas.model import Model
from catas.parsers import split_hmm
from catas.parsers import HMMER


@pytest.mark.parametrize("hmm,exp", [
    ("GH80.hmm", "GH80"),
    ("AC1.hmm", "AC1"),
    ("AC1.phmm", "AC1"),
    ("AC1h.hmm", "AC1h")
])
def test_split_hmm(hmm, exp):
    result = split_hmm(hmm)
    assert result == exp
    return


@pytest.mark.parametrize("version,idx,col,exp_val", [
    (Version.v4, 0, "hmm", "GH47"),
    (Version.v4, 1, "hmm_len", 29),
    (Version.v4, 2, "seqid", "tr|Q0UA13|Q0UA13_PHANO"),
    (Version.v4, 6, "hmm", "GH10"),
    (Version.v4, 11, "seqid", "tr|Q68KX9|Q68KX9_PHAND"),
    (Version.v5, 0, "hmm", "GH47"),
    (Version.v5, 2, "seqid", "tr|Q0UA13|Q0UA13_PHANO"),
    (Version.v5, 6, "hmm", "GH10"),
    (Version.v5, 11, "seqid", "tr|Q68KX9|Q68KX9_PHAND"),
    (Version.v6, 0, "hmm", "GH47"),
    (Version.v6, 1, "hmm_len", 29),
    (Version.v6, 2, "seqid", "tr|Q0UA13|Q0UA13_PHANO"),
    (Version.v6, 6, "hmm", "GH10"),
    (Version.v6, 11, "seqid", "tr|Q68KX9|Q68KX9_PHAND"),
    (Version.v7, 0, "hmm", "GH47"),
    (Version.v7, 1, "hmm_len", 29),
    (Version.v7, 2, "seqid", "tr|Q0UA13|Q0UA13_PHANO"),
    (Version.v7, 6, "hmm", "GH10"),
    (Version.v7, 11, "seqid", "tr|Q68KX6|Q68KX6_PHAND"),
    (Version.v8, 0, "hmm", "GH47"),
    (Version.v8, 1, "hmm_len", 29),
    (Version.v8, 2, "seqid", "tr|Q0UA13|Q0UA13_PHANO"),
    (Version.v8, 6, "hmm", "GH10"),
    (Version.v8, 11, "seqid", "tr|Q68KX6|Q68KX6_PHAND"),
])
def test_parse_hmmer_text_output(version, idx, col, exp_val):

    with open(model_filepath(version), "rb") as handle:
        model = Model.read(handle)

    files = test_files(version)
    with open(files["hmmer_text"], "r") as handle:
        sample = list(HMMER.from_file(
            handle,
            model.hmm_lengths,
            "hmmer3-text",
        ))

    assert getattr(sample[idx], col) == exp_val
    return
