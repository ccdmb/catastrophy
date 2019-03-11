"""
Functions to count the number of specific classes of CAZymes.
"""

from __future__ import unicode_literals

import logging
from collections import defaultdict

import pandas as pd

from catas import utils # noqa
from catas.data import cazy_list # noqa
from catas.data import hmm_lengths # noqa
from catas.data import LATEST_VERSION # noqa

logger = logging.getLogger(__name__)


# @utils.log(logger, logging.DEBUG)
def cazy_counts(handle, label, version=None):
    """ Takes a file handle and counts unique occurrences of HMMs.

    Keyword arguments:
    handle -- A file-like object (required).
    label -- A string to identify the input by (required).
    format -- The format that the handle is in. Must be one of ["hmmer3-text",
        "hmmscan3-domtab", "dbcan"]. Default is "hmmer3-text".
    model_version -- The version of dbCAN that the model was trained with
        (Default: Latest available in data).

    Output:
    list -- A list of tuples specifying column names and values.
    """

    if version is None:
        version = LATEST_VERSION

    required_cols = cazy_list(version)

    # Loop through all lines and add seqids a set for each HMM that they match.
    these_hmms = defaultdict(set)
    for line in handle:
        these_hmms[line["hmm"]].add(line["seqid"])

    output = list()

    # If required columns isn't specified, just use all from this file.
    if required_cols is None:
        required_cols = sorted(these_hmms.keys())

    # Loop through columns and add the required hmm counts to output row.
    for col in required_cols:
        # Raises keyerror if we didn't see required column. Catch and set to 0.
        try:
            count = len(these_hmms[col])
        except KeyError:
            count = 0

        output.append((col, count))

    output = pd.Series(
        data=[t[1] for t in output],
        index=pd.Index([t[0] for t in output]),
        name=label
    )

    return output
