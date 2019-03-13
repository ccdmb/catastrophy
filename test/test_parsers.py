import pytest

from catas.data import Version
from catas.data import test_dbcan
from catas.parsers import split_hmm
from catas.parsers import DBCAN


@pytest.mark.parametrize("hmm,exp", [
    ("GH80.hmm", "GH80"),
    ("AC1.hmm", "AC1")
])
def test_split_hmm(hmm, exp):
    result = split_hmm(hmm)
    assert result == exp
    return


@pytest.mark.parametrize("version,idx,col,exp_val", [
    (Version.v4, 0, "hmm", "CBM1"),
    (Version.v4, 1, "hmm_len", 303),
    (Version.v4, 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    (Version.v4, 3, "query_len", 637),
    (Version.v4, 6, "hmm", "GH10"),
    (Version.v4, 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
    (Version.v5, 0, "hmm", "CBM1"),
    (Version.v5, 1, "hmm_len", 303),
    (Version.v5, 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    (Version.v5, 3, "query_len", 637),
    (Version.v5, 6, "hmm", "GH10"),
    (Version.v5, 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
    (Version.v6, 0, "hmm", "GH10"),
    (Version.v6, 1, "hmm_len", 29),
    (Version.v6, 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    (Version.v6, 3, "query_len", 637),
    (Version.v6, 6, "hmm", "GH10"),
    (Version.v6, 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
])
def test_parse_dbcan_output(version, idx, col, exp_val):

    with open(test_dbcan(version=version), "r") as handle:
        sample = list(DBCAN.from_file(handle))

    assert getattr(sample[idx], col) == exp_val
    return
