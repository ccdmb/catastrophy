"""
Functions to count the number of specific classes of CAZymes.
"""

from collections import defaultdict
import numpy as np
from catas.matrix import Matrix


def cazy_counts_multi(handles, labels, required_cols):
    """ Computes counts for many files. """
    counts = [cazy_counts(m, required_cols) for m in handles]
    return Matrix(
        rows=labels,
        columns=required_cols,
        arr=np.row_stack(counts)
    )


def cazy_counts(matches, required_cols):
    """ Takes a file handle and counts unique occurrences of HMMs.

    Keyword arguments:
    matches -- A list or generator of DBCAN or HMMER records (required).
    required_cols -- A list of HMMs that must have counts in the output.

    Output:
    np.array -- An array of the counts in the same order as the required_cols.
    """

    # Loop through all lines and add seqids a set for each HMM that they match.
    these_hmms = defaultdict(set)
    for match in matches:
        these_hmms[match.hmm].add(match.seqid)

    row = np.zeros(len(required_cols), dtype=np.int)
    # Loop through columns and add the required hmm counts to output row.
    for i, col in enumerate(required_cols):
        row[i] = len(these_hmms[col])

    return row
