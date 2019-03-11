"""
Stored data for use during runtime or testing.

Because dbCAN is an evolving database, we'll have to maintain several models
for each database release. The latest version will always we the default one.
"""

from __future__ import unicode_literals

from pkg_resources import resource_filename

from collections import defaultdict
import logging
import json

import pandas as pd
import numpy as np

# from catas import utils

logger = logging.getLogger(__name__)

# Always make this newest to oldest
AVAILABLE_VERSIONS = ["v6", "v5", "v4"]
LATEST_VERSION = AVAILABLE_VERSIONS[0]

AVAILABLE_NOMENCLATURES = ["nomenclature1", "nomenclature2", "nomenclature3"]
DEFAULT_NOMENCLATURE = AVAILABLE_NOMENCLATURES[-1]


# @utils.log(logger, logging.DEBUG)
def models(version=LATEST_VERSION):
    """ Loads pickled sklearn pipeline. """

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-model.npz"),
            ("v5-20180324", "v5-20180324-model.npz"),
            ("v6-20180324", "v6-20180324-model.npz"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    return np.load(version_files[version])


# @utils.log(logger, logging.DEBUG)
def principle_components(version=LATEST_VERSION):
    """ Loads files containing PCs for training data. """

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-principle_components.json"),
            ("v5-20180324", "v5-20180324-principle_components.json"),
            ("v6-20180324", "v6-20180324-principle_components.json"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    return pd.read_json(version_files[version])


# @utils.log(logger, logging.DEBUG)
def cazy_list(version=LATEST_VERSION):
    """ Loads CAZY list of class names the in order that model was trained. """

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-cazy_list.json"),
            ("v5-20180324", "v5-20180324-cazy_list.json"),
            ("v6-20180324", "v6-20180324-cazy_list.json"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    with open(version_files[version], "r") as handle:
        return json.load(handle)


# @utils.log(logger, logging.DEBUG)
def centroids(version=LATEST_VERSION, nomenclature=DEFAULT_NOMENCLATURE):
    """ Loads pandas dataframe containing centroids. """

    files = defaultdict(dict)
    filelist = [
            (
                "v4-20180324",
                "nomenclature1", "v4-20180324-nomenclature1-centroids.json"
            ),
            (
                "v4-20180324",
                "nomenclature2", "v4-20180324-nomenclature2-centroids.json"
            ),
            (
                "v4-20180324",
                "nomenclature3", "v4-20180324-nomenclature3-centroids.json"
            ),
            (
                "v5-20180324",
                "nomenclature1",
                "v5-20180324-nomenclature1-centroids.json"
            ),
            (
                "v5-20180324",
                "nomenclature2", "v5-20180324-nomenclature2-centroids.json"
            ),
            (
                "v5-20180324",
                "nomenclature3",
                "v5-20180324-nomenclature3-centroids.json"
            ),
            (
                "v6-20180324",
                "nomenclature1",
                "v6-20180324-nomenclature1-centroids.json"
            ),
            (
                "v6-20180324",
                "nomenclature2",
                "v6-20180324-nomenclature2-centroids.json"
            ),
            (
                "v6-20180324",
                "nomenclature3",
                "v6-20180324-nomenclature3-centroids.json"
            ),
            ]

    for vname, nname, vfile in filelist:
        files[vname][nname] = resource_filename(__name__, vfile)

    files["v4"] = files["v4-20180324"]
    files["v5"] = files["v5-20180324"]
    files["v6"] = files["v6-20180324"]

    return pd.read_json(files[version][nomenclature])


# @utils.log(logger, logging.DEBUG)
def hmm_lengths(version=LATEST_VERSION):
    """ Loads dict object containing lengths of HMMs.

    The raw HMMER output doesn't contain the length of the HMM, which we
    need to compute coverage.
    """

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-hmm_lengths.json"),
            ("v5-20180324", "v5-20180324-hmm_lengths.json"),
            ("v6-20180324", "v6-20180324-hmm_lengths.json"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    with open(version_files[version], "r") as handle:
        return json.load(handle)


# @utils.log(logger, logging.DEBUG)
def trophic_classes(nomenclature=DEFAULT_NOMENCLATURE):
    """ Loads list containing names and correct order to display classes. """

    files = dict()
    filelist = [
        ("nomenclature1", "nomenclature1-trophic_classes.json"),
        ("nomenclature2", "nomenclature2-trophic_classes.json"),
        ("nomenclature3", "nomenclature3-trophic_classes.json"),
        ]

    for nname, nfile in filelist:
        files[nname] = resource_filename(__name__, nfile)

    with open(files[nomenclature], "r") as handle:
        return json.load(handle)


def sample_fasta():

    # There's no actual version for this.
    return resource_filename(__name__, "test_data.fasta")


# @utils.log(logger, logging.DEBUG)
def test_dbcan(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-test_dbcan.csv"),
            ("v5-20180324", "v5-20180324-test_dbcan.csv"),
            ("v6-20180324", "v6-20180324-test_dbcan.csv"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_hmmer(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-test_hmmer.txt"),
            ("v5-20180324", "v5-20180324-test_hmmer.txt"),
            ("v6-20180324", "v6-20180324-test_hmmer.txt"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_domtblout(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-test_hmmer.csv"),
            ("v5-20180324", "v5-20180324-test_hmmer.csv"),
            ("v6-20180324", "v6-20180324-test_hmmer.csv"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_counts(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
            ("v4-20180324", "v4-20180324-test_counts.csv"),
            ("v5-20180324", "v5-20180324-test_counts.csv"),
            ("v6-20180324", "v6-20180324-test_counts.csv"),
            ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    version_files["v4"] = version_files["v4-20180324"]
    version_files["v5"] = version_files["v5-20180324"]
    version_files["v6"] = version_files["v6-20180324"]

    df = pd.read_csv(
        version_files[version],
        sep='\t',
        header=None,
        names=["hmm", "sample_counts"]
        )
    df.set_index("hmm", inplace=True, drop=True)
    return df["sample_counts"]
