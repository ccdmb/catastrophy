"""
Stored data for use during runtime or testing.

Because dbCAN is an evolving database, we'll have to maintain several models
for each database release. The latest version will always we the default one.
"""

from __future__ import unicode_literals

from pkg_resources import resource_filename

from collections import defaultdict
import json
from enum import Enum

import numpy as np

from catas.matrix import Matrix


class MyEnum(Enum):
    """ Base class for enums. """

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s):
        try:
            return cls[s]
        except KeyError:
            raise ValueError

    @classmethod
    def from_other(cls, f):
        if isinstance(f, cls):
            return f
        elif isinstance(f, str):
            return cls.from_string(f)
        elif isinstance(f, int):
            return cls(f)
        else:
            raise ValueError("Expected an enum, string or integer.")


class Version(MyEnum):
    """ Supported DBCAN database versions. """

    v4 = 1
    v5 = 2
    v6 = 3
    v7 = 4

    @classmethod
    def latest(cls):
        return cls.v6


class Nomenclature(MyEnum):
    """ All CATAStrophy nomenclatures. """

    nomenclature1 = 1
    nomenclature2 = 2
    nomenclature3 = 3

    @classmethod
    def default(cls):
        return cls.nomenclature3


def models(version=Version.latest()):
    """ Loads PCA parameters. """

    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-model.npz"),
        (Version.v5, "v5-20190311-model.npz"),
        (Version.v6, "v6-20190311-model.npz"),
        (Version.v7, "v7-20190311-model.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return np.load(version_files[version])


def principle_components(version=Version.latest()):
    """ Loads files containing PCs for training data. """

    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-principle_components.npz"),
        (Version.v5, "v5-20190311-principle_components.npz"),
        (Version.v6, "v6-20190311-principle_components.npz"),
        (Version.v7, "v7-20190311-principle_components.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    mat_raw = np.load(version_files[version])
    mat = Matrix.read(version_files[version])

    mat.nomenclature1 = mat_raw["nomenclature1"]
    mat.nomenclature2 = mat_raw["nomenclature2"]
    mat.nomenclature3 = mat_raw["nomenclature3"]
    return mat


def cazy_list(version=Version.latest()):
    """ Loads CAZY list of class names the in order that model was trained. """

    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-cazy_list.json"),
        (Version.v5, "v5-20190311-cazy_list.json"),
        (Version.v6, "v6-20190311-cazy_list.json"),
        (Version.v7, "v7-20190311-cazy_list.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[version], "r") as handle:
        d = json.load(handle)

    return d


def centroids(version=Version.latest(), nomenclature=Nomenclature.default()):
    """ Loads pandas dataframe containing centroids. """

    # Handle strings as input instead of just enums.
    version = Version.from_other(version)
    nomenclature = Nomenclature.from_other(nomenclature)

    files = defaultdict(dict)
    filelist = [
        (
            Version.v4,
            Nomenclature.nomenclature1,
            "v4-20190311-nomenclature1-centroids.npz"
        ),
        (
            Version.v4,
            Nomenclature.nomenclature2,
            "v4-20190311-nomenclature2-centroids.npz"
        ),
        (
            Version.v4,
            Nomenclature.nomenclature3,
            "v4-20190311-nomenclature3-centroids.npz"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature1,
            "v5-20190311-nomenclature1-centroids.npz"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature2,
            "v5-20190311-nomenclature2-centroids.npz"
        ),
        (
            Version.v5,
            Nomenclature.nomenclature3,
            "v5-20190311-nomenclature3-centroids.npz"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature1,
            "v6-20190311-nomenclature1-centroids.npz"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature2,
            "v6-20190311-nomenclature2-centroids.npz"
        ),
        (
            Version.v6,
            Nomenclature.nomenclature3,
            "v6-20190311-nomenclature3-centroids.npz"
        ),
        (
            Version.v7,
            Nomenclature.nomenclature1,
            "v7-20190311-nomenclature1-centroids.npz"
        ),
        (
            Version.v7,
            Nomenclature.nomenclature2,
            "v7-20190311-nomenclature2-centroids.npz"
        ),
        (
            Version.v7,
            Nomenclature.nomenclature3,
            "v7-20190311-nomenclature3-centroids.npz"
        ),
    ]

    for vname, nname, vfile in filelist:
        files[vname][nname] = resource_filename(__name__, vfile)

    return Matrix.read(files[version][nomenclature])


def hmm_lengths(version=Version.latest()):
    """ Loads dict object containing lengths of HMMs.

    The raw HMMER output doesn't contain the length of the HMM, which we
    need to compute coverage.
    """

    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-hmm_lengths.json"),
        (Version.v5, "v5-20190311-hmm_lengths.json"),
        (Version.v6, "v6-20190311-hmm_lengths.json"),
        (Version.v7, "v7-20190311-hmm_lengths.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[version], "r") as handle:
        d = json.load(handle)

    return d


def trophic_classes(nomenclature=Nomenclature.default()):
    """ Loads list containing names and correct order to display classes. """

    nomenclature = Nomenclature.from_other(nomenclature)

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


def test_dbcan(version=Version.latest()):
    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_dbcan.csv"),
        (Version.v5, "v5-20190311-test_dbcan.csv"),
        (Version.v6, "v6-20190311-test_dbcan.csv"),
        (Version.v7, "v7-20190311-test_dbcan.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


def test_hmmer(version=Version.latest()):
    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_hmmer.txt"),
        (Version.v5, "v5-20190311-test_hmmer.txt"),
        (Version.v6, "v6-20190311-test_hmmer.txt"),
        (Version.v7, "v7-20190311-test_hmmer.txt"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


def test_domtblout(version=Version.latest()):
    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_hmmer.csv"),
        (Version.v5, "v5-20190311-test_hmmer.csv"),
        (Version.v6, "v6-20190311-test_hmmer.csv"),
        (Version.v7, "v7-20190311-test_hmmer.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[version]


def test_counts(version=Version.latest()):
    # Handle strings as input instead of just enums.
    version = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_counts.npz"),
        (Version.v5, "v5-20190311-test_counts.npz"),
        (Version.v6, "v6-20190311-test_counts.npz"),
        (Version.v7, "v7-20190311-test_counts.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return Matrix.read(version_files[version])
