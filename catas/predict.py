"""
Functions to find the PCA-transformed values from cazyme counts.
Functions to find distances to centroids in PCA space.
"""

import numpy as np
from numpy.linalg import norm

from catas.matrix import Matrix
from catas.data import models
from catas.data import centroids
from catas.data import Version
from catas.data import Nomenclature


def predict(
    counts,
    version=Version.latest(),
    nomenclature=Nomenclature.default()
):
    """ Wrapper function that takes file handle and returns RCD predictions.

    Keyword arguments:
    counts -- A `Matrix` containing the cazyme counts (required).
    version -- The model to run the predictions against (Default is latest
        available in data).
    nomenclature -- The nomenclature to predict labels for.

    Returns:
    Matrix -- A matrix of RCDs, with samples in rows and nomenclature labels
        as columns.
    """

    version = Version.from_other(version)
    nomenclature = Nomenclature.from_other(nomenclature)

    # load the sklearn pipeline that runs scaling and PCA
    model = models(version)

    # Load the DataFrame containing PCA centroids for each class.
    ctds = centroids(version=version, nomenclature=nomenclature)

    # Transform the counts into PCA space values.
    trans = transform(counts, model=model)

    # Find the distances between the point in PCA space and class centroids.
    dists = distances(trans, centroids=ctds)

    # Calculate the relative centroid distance for each distance.
    rcds = rcd(dists)

    return rcds


def transform(counts, model=models()):
    """ Takes a series of CAZyme counts and gets PCA transformed values.

    Keyword arguments:
    counts -- A Matrix containing CAZyme counts.
    model -- A dictionary containing numpy arrays used to transform the counts.
        E.g. from `catas.data.models()`.

    Returns:
    Matrix -- A matrix object with the PCA transformed values.
    """

    values = counts.arr.astype(np.float)
    X = values - model["mean"]
    X_transformed = np.dot(X, model["components"].T)

    columns = ["pc{:0>2}".format(i + 1) for i in range(X_transformed.shape[1])]
    return Matrix(rows=counts.rows, columns=columns, arr=X_transformed)


def distances(points, centroids=centroids()):
    """ Given a point in PCA space, find the distance to each centroid.

    Keyword arguments:
    points -- A Matrix representing the location of sample(s) in PC space.
    centroids -- A matrix with rows representing classes and columns
        representing class centroids in principle component space (Default is
        latest centroids available in data).
        E.g. from `catas.data.centroids()`.

    Returns:
    Matrix -- A Matrix object giving the euclidean distance to each
        class centroid indexed by the class names.
    """

    # This computes the distance matrix, with samples in rows and centroids as
    # columns.
    diffs = np.apply_along_axis(lambda x: x - centroids.arr, 1, points.arr)
    normed = np.apply_along_axis(norm, 2, diffs)

    # Grab the class names from the centroids
    new_columns = centroids.rows

    # return a new series with the class names as index
    return Matrix(rows=points.rows, columns=new_columns, arr=normed)


def rcd(dists):
    """ Finds the relative centroid distance.

    Given an array of distances between two points,
    returns the RCD for each distance in the array.

    Keyword arguments:
    dists -- A Matrix object representing distances between points and
        centroids.

    Returns:
    Matrix -- A Matrix object with the RCD values for each class.
    """

    min_ = dists.arr.min(axis=1).reshape(-1, 1)
    max_ = dists.arr.max(axis=1).reshape(-1, 1)
    ratio = (dists.arr - min_) / (max_ - min_)
    rcd_ = 1 - ratio

    # Return the RCDs as a series object with original names/index
    return Matrix(rows=dists.rows, columns=dists.columns, arr=rcd_)
