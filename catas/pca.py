"""
Functions to find the PCA-transformed values from cazyme counts.
"""

from __future__ import unicode_literals
import logging

import pandas as pd
import numpy as np

# from catas import utils
from catas.data import models

logger = logging.getLogger(__name__)

LATEST_MODEL = models()


# @utils.log(logger, logging.DEBUG)
def transform(series, model=LATEST_MODEL):
    """ Takes a series of CAZyme counts and gets PCA transformed values.

    Keyword arguments:
    series -- A pandas series object containing CAZyme counts.
    model -- A scikit learn object to transform the series.

    Returns:
    Series -- A pandas Series object with the transformed values.
    """

    values = series.values.reshape(1, -1).astype(np.float)
    X = values - model["mean"]
    X_transformed = np.dot(X, model["components"].T)

    trans = pd.Series(X_transformed[0], name=series.name)
    trans.index = ["pc{:0>2}".format(i + 1) for i in trans.index]

    return trans
