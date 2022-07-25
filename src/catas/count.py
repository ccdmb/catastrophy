"""
Functions to count the number of specific classes of CAZymes.
"""

from typing import List, Sequence
from typing import Iterable
from typing import Union
from typing import Dict, Set

from collections import defaultdict
import numpy as np

from catas.matrix import Matrix

# These are only used for type checking
from catas.parsers import HMMER, DBCAN


class HMMError(Exception):

    """ Requested an HMM that doesn't exist in this version of dbCAN. """

    def __init__(self, hmms: Sequence[str]):
        """

        Keyword arguments:
        hmms -- a list of hmms that were invalid.
        """

        self.hmms: List[str] = list(hmms)
        return


def cazy_counts_multi(
    handles: Iterable[Union[Iterable[HMMER], Iterable[DBCAN]]],
    labels: Sequence[str],
    required_cols: Sequence[str],
) -> Matrix:

    """ Computes counts for many files. """

    counts = [cazy_counts(m, required_cols) for m in handles]

    return Matrix(
        rows=list(labels),
        columns=list(required_cols),
        arr=np.row_stack(counts)
    )


def cazy_counts(
    matches: Union[Iterable[HMMER], Iterable[DBCAN]],
    required_cols: Sequence[str]
) -> np.ndarray:
    """ Takes a file handle and counts unique occurrences of HMMs.

    Keyword arguments:
    matches -- A list or generator of DBCAN or HMMER records (required).
    required_cols -- A list of HMMs that must have counts in the output.

    Output:
    np.ndarray -- An array of the counts in the same order as the
      required_cols.
    """

    # Loop through all lines and add seqids a set for each HMM that they match.
    these_hmms: Dict[str, Set[str]] = defaultdict(set)
    for match in matches:
        these_hmms[match.hmm].add(match.seqid)

    invalid_hmms = [k for k in these_hmms.keys() if k not in required_cols]
    if len(invalid_hmms) > 0:
        raise HMMError(invalid_hmms)

    row = np.zeros(len(required_cols), dtype=int)

    # Loop through columns and add the required hmm counts to output row.
    for i, col in enumerate(required_cols):
        row[i] = len(these_hmms[col])

    return row
