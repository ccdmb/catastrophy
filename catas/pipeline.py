"""
Main wrapper function to tie together counting, PCA, and RCD.
"""

from __future__ import unicode_literals

import logging

# from catas import utils
from catas.pca import transform
from catas.centroids import distances
from catas.centroids import rcd

from catas import data

logger = logging.getLogger(__name__)


# @utils.log(logger, logging.DEBUG)
def predict(
    counts,
    format=None,
    version=data.LATEST_VERSION,
    nomenclature=data.DEFAULT_NOMENCLATURE
):
    """ Wrapper function that takes file handle and returns RCD predictions.

    Keyword arguments:
    counts -- A pandas dataframe containing the cazyme counts (required).
    version -- The model to run the predictions against (Default is latest
        available in data).
    nomenclature -- The nomenclature to use.
    """

    # load the sklearn pipeline that runs scaling and PCA
    model = data.models(version)
    # Load the DataFrame containing PCA centroids for each class.
    centroids = data.centroids(version=version, nomenclature=nomenclature)

    # Transform the counts into PCA space values.
    trans = transform(counts, model=model)

    # Find the distances between the point in PCA space and class centroids.
    dists = distances(trans, centroids=centroids)

    # Calculate the relative centroid distance for each distance.
    rcds = rcd(dists)

    return rcds
