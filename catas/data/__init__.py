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
from enum import Enum

import pandas as pd
import numpy as np

# from catas import utils

logger = logging.getLogger(__name__)


class MyEnum(Enum):

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s):
        try:
            return cls[s]
        except KeyError:
            raise ValueError


class Version(MyEnum):
    v4 = 1
    v5 = 2
    v6 = 3


LATEST_VERSION = max(list(Version), key=lambda v: v.value)


class Nomenclature(MyEnum):
    nomenclature1 = 1
    nomenclature2 = 2
    nomenclature3 = 3


DEFAULT_NOMENCLATURE = Nomenclature(3)


# @utils.log(logger, logging.DEBUG)
def models(version=LATEST_VERSION):
    """ Loads pickled sklearn pipeline. """

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-model.npz"),
        (Version.v5, "v5-20180324-model.npz"),
        (Version.v6, "v6-20180324-model.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return np.load(version_files[version])


# @utils.log(logger, logging.DEBUG)
def principle_components(version=LATEST_VERSION):
    """ Loads files containing PCs for training data. """

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-principle_components.json"),
        (Version.v5, "v5-20180324-principle_components.json"),
        (Version.v6, "v6-20180324-principle_components.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return pd.read_json(version_files[version])


def cazy_list(version=LATEST_VERSION):
    """ Loads CAZY list of class names the in order that model was trained. """

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-cazy_list.json"),
        (Version.v5, "v5-20180324-cazy_list.json"),
        (Version.v6, "v6-20180324-cazy_list.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[version], "r") as handle:
        d = json.load(handle)

    return d


def centroids(version=LATEST_VERSION, nomenclature=DEFAULT_NOMENCLATURE):
    """ Loads pandas dataframe containing centroids. """

    files = defaultdict(dict)
    filelist = [
        (
            Version.v4,
            Nomenclature.nomenclature1,
            "v4-20180324-nomenclature1-centroids.json"
        ),
        (
            Version.v4,
            Nomenclature.nomenclature2,
            "v4-20180324-nomenclature2-centroids.json"
        ),
        (
            Version.v4,
            Nomenclature.nomenclature3,
            "v4-20180324-nomenclature3-centroids.json"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature1,
            "v5-20180324-nomenclature1-centroids.json"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature2,
            "v5-20180324-nomenclature2-centroids.json"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature3,
            "v5-20180324-nomenclature3-centroids.json"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature1,
            "v6-20180324-nomenclature1-centroids.json"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature2,
            "v6-20180324-nomenclature2-centroids.json"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature3,
            "v6-20180324-nomenclature3-centroids.json"
        ),
    ]

    for vname, nname, vfile in filelist:
        files[vname][nname] = resource_filename(__name__, vfile)

    return pd.read_json(files[version][nomenclature])


def hmm_lengths(version=LATEST_VERSION):
    """ Loads dict object containing lengths of HMMs.

    The raw HMMER output doesn't contain the length of the HMM, which we
    need to compute coverage.
    """

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-hmm_lengths.json"),
        (Version.v5, "v5-20180324-hmm_lengths.json"),
        (Version.v6, "v6-20180324-hmm_lengths.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[version], "r") as handle:
        d = json.load(handle)

    return d


def trophic_classes(nomenclature=DEFAULT_NOMENCLATURE):
    """ Loads list containing names and correct order to display classes. """

    files = dict()
    filelist = [
        (Nomenclature.nomenclature1, "nomenclature1-trophic_classes.json"),
        (Nomenclature.nomenclature2, "nomenclature2-trophic_classes.json"),
        (Nomenclature.nomenclature3, "nomenclature3-trophic_classes.json"),
    ]

    for nname, nfile in filelist:
        files[nname] = resource_filename(__name__, nfile)

    with open(files[nomenclature], "r") as handle:
        d = json.load(handle)
    return d


def sample_fasta():
    # There's no actual version for this.
    return resource_filename(__name__, "test_data.fasta")


# @utils.log(logger, logging.DEBUG)
def test_dbcan(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-test_dbcan.csv"),
        (Version.v5, "v5-20180324-test_dbcan.csv"),
        (Version.v6, "v6-20180324-test_dbcan.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_hmmer(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-test_hmmer.txt"),
        (Version.v5, "v5-20180324-test_hmmer.txt"),
        (Version.v6, "v6-20180324-test_hmmer.txt"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_domtblout(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-test_hmmer.csv"),
        (Version.v5, "v5-20180324-test_hmmer.csv"),
        (Version.v6, "v6-20180324-test_hmmer.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


# @utils.log(logger, logging.DEBUG)
def test_counts(version=LATEST_VERSION):

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20180324-test_counts.csv"),
        (Version.v5, "v5-20180324-test_counts.csv"),
        (Version.v6, "v6-20180324-test_counts.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    df = pd.read_csv(
        version_files[version],
        sep='\t',
        header=None,
        names=["hmm", "sample_counts"]
        )
    df.set_index("hmm", inplace=True, drop=True)
    return df["sample_counts"]
