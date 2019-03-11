"""
Functions to find distances to centroids in PCA space.
"""

from __future__ import unicode_literals
import logging

import pandas as pd
from numpy.linalg import norm

# from catas import utils
from catas.data import centroids

logger = logging.getLogger(__name__)

LATEST_CENTROIDS = centroids()


# @utils.log(logger, logging.DEBUG)
def distances(point, centroids=LATEST_CENTROIDS):
    """ Given a point in PCA space, find the distance to each centroid.

    Keyword arguments:
    point -- A pandas series or numpy array representing the location of a
        sample in PC space (Required).
    centroids -- A pandas DataFrame with rows representing classes and columns
        representing class centroids in principle component space (Default is
        latest centroids available in data).

    Returns:
    Series -- A pandas Series object giving the euclidean distance to each
        class centroid indexed by the class names.
    """

    results = list()
    for idx in centroids.index:
        # Norm from numpy.linalg, converts difference to squared dist.
        results.append(norm(point - centroids.loc[idx]))

    # Grab the class names from the centroids
    new_index = centroids.index
    new_index.name = None

    # return a new series with the class names as index
    return pd.Series(results, index=new_index, name=point.name)


# @utils.log(logger, logging.DEBUG)
def rcd(dists):
    """ Finds the relative centroid distance.

    Given an array of distances between two points,
    returns the RCD for each distance in the array.

    Keyword arguments:
    dists -- A pandas Series object representing distances between points and
        centroids (required).

    Returns:
    Series -- A pandas Series object with the RCD values for each class.
    """

    min_ = dists.min()
    max_ = dists.max()
    ratio = (dists - min_) / (max_ - min_)
    rcd_ = 1 - ratio

    new_index = dists.index
    new_index.name = None

    # Return the RCDs as a series object with original names/index
    return pd.Series(rcd_, index=new_index, name=dists.name)
