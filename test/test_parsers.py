import pytest

from catas.data import test_dbcan
from catas.parsers import split_hmm
from catas.parsers import parse_dbcan_output


@pytest.mark.parametrize("hmm,exp", [
    ("GH80.hmm", "GH80"),
    ("AC1.hmm", "AC1")
])
def test_split_hmm(hmm, exp):
    result = split_hmm(hmm)
    assert result == exp
    return


@pytest.mark.parametrize("version,idx,col,exp_val", [
    ("v4", 0, "hmm", "CBM1"),
    ("v4", 1, "hmm_len", 303),
    ("v4", 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    ("v4", 3, "query_len", 637),
    ("v4", 6, "hmm", "GH10"),
    ("v4", 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
    ("v5", 0, "hmm", "CBM1"),
    ("v5", 1, "hmm_len", 303),
    ("v5", 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    ("v5", 3, "query_len", 637),
    ("v5", 6, "hmm", "GH10"),
    ("v5", 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
    ("v6", 0, "hmm", "GH10"),
    ("v6", 1, "hmm_len", 29),
    ("v6", 2, "seqid", "tr|B6DQK8|B6DQK8_PHAND"),
    ("v6", 3, "query_len", 637),
    ("v6", 6, "hmm", "GH10"),
    ("v6", 11, "seqid", "tr|Q9Y7H9|Q9Y7H9_PHAND"),
])
def test_parse_dbcan_output(version, idx, col, exp_val):

    with open(test_dbcan(version=version), "r") as handle:
        sample = handle.readlines()

    lines = [l for l in parse_dbcan_output(sample)]

    assert lines[idx][col] == exp_val
    return
