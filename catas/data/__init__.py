"""
Stored data for use during runtime or testing.

Because dbCAN is an evolving database, we'll have to maintain several models
for each database release. The latest version will always we the default one.
"""

from pkg_resources import resource_filename

import json
from enum import Enum
from collections import defaultdict

from typing import Dict
from typing import List
from typing import Union
from typing import TypeVar, Type

import numpy as np

from catas.matrix import Matrix


T = TypeVar('T', bound="MyEnum")


class MyEnum(Enum):
    """ Base class for enums. """

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls: Type[T], s: str) -> T:
        try:
            return cls[s]
        except KeyError:
            raise ValueError

    @classmethod
    def from_other(cls: Type[T], f: Union[str, int, "MyEnum"]) -> T:
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
    def latest(cls) -> "Version":
        return cls.v6


class Nomenclature(MyEnum):
    """ All CATAStrophy nomenclatures. """

    nomenclature1 = 1
    nomenclature2 = 2
    nomenclature3 = 3

    @classmethod
    def default(cls) -> "Nomenclature":
        return cls.nomenclature3


def models(
    version: Union[str, int, Version] = Version.latest()
) -> Dict[str, np.array]:
    """ Loads PCA parameters. """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-model.npz"),
        (Version.v5, "v5-20190311-model.npz"),
        (Version.v6, "v6-20190311-model.npz"),
        (Version.v7, "v7-20190311-model.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return np.load(version_files[versionp])


def principle_components(
    version: Union[str, int, Version] = Version.latest()
) -> Matrix:
    """ Loads files containing PCs for training data. """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-principle_components.npz"),
        (Version.v5, "v5-20190311-principle_components.npz"),
        (Version.v6, "v6-20190311-principle_components.npz"),
        (Version.v7, "v7-20190311-principle_components.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    mat_raw = np.load(version_files[versionp])
    mat = Matrix.read(version_files[versionp])

    mat.nomenclature1 = mat_raw["nomenclature1"]
    mat.nomenclature2 = mat_raw["nomenclature2"]
    mat.nomenclature3 = mat_raw["nomenclature3"]
    return mat


def cazy_list(
    version: Union[str, int, Version] = Version.latest()
) -> List[str]:
    """ Loads CAZY list of class names the in order that model was trained. """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-cazy_list.json"),
        (Version.v5, "v5-20190311-cazy_list.json"),
        (Version.v6, "v6-20190311-cazy_list.json"),
        (Version.v7, "v7-20190311-cazy_list.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[versionp], "r") as handle:
        d = json.load(handle)

    assert isinstance(d, list)
    assert all(isinstance(di, str) for di in d)

    return d


def centroids(
    version: Union[str, int, Version] = Version.latest(),
    nomenclature: Union[str, int, Nomenclature] = Nomenclature.default()
) -> Matrix:
    """ Loads pandas dataframe containing centroids. """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)
    nomenclaturep = Nomenclature.from_other(nomenclature)

    files: Dict[Version, Dict[Nomenclature, str]] = defaultdict(dict)
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

    return Matrix.read(files[versionp][nomenclaturep])


def hmm_lengths(
    version: Union[str, int, Version] = Version.latest()
) -> Dict[str, int]:
    """ Loads dict object containing lengths of HMMs.

    The raw HMMER output doesn't contain the length of the HMM, which we
    need to compute coverage.
    """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-hmm_lengths.json"),
        (Version.v5, "v5-20190311-hmm_lengths.json"),
        (Version.v6, "v6-20190311-hmm_lengths.json"),
        (Version.v7, "v7-20190311-hmm_lengths.json"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    with open(version_files[versionp], "r") as handle:
        d = json.load(handle)

    assert isinstance(d, dict)
    assert all(isinstance(dk, str) for dk in d.keys())
    assert all(isinstance(dv, int) for dv in d.values())
    return d


def trophic_classes(
    nomenclature: Union[str, int, Nomenclature] = Nomenclature.default()
) -> List[str]:
    """ Loads list containing names and correct order to display classes. """

    nomenclaturep = Nomenclature.from_other(nomenclature)

    files = dict()
    filelist = [
        (Nomenclature.nomenclature1, "nomenclature1-trophic_classes.json"),
        (Nomenclature.nomenclature2, "nomenclature2-trophic_classes.json"),
        (Nomenclature.nomenclature3, "nomenclature3-trophic_classes.json"),
    ]

    for nname, nfile in filelist:
        files[nname] = resource_filename(__name__, nfile)

    with open(files[nomenclaturep], "r") as handle:
        d = json.load(handle)

    assert isinstance(d, list)
    assert all(isinstance(di, str) for di in d)
    return d


def sample_fasta() -> str:
    # There's no actual version for this.
    return resource_filename(__name__, "test_data.fasta")


def test_dbcan(version: Union[str, int, Version] = Version.latest()) -> str:
    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_dbcan.csv"),
        (Version.v5, "v5-20190311-test_dbcan.csv"),
        (Version.v6, "v6-20190311-test_dbcan.csv"),
        (Version.v7, "v7-20190311-test_dbcan.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[versionp]


def test_hmmer(version: Union[str, int, Version] = Version.latest()) -> str:
    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_hmmer.txt"),
        (Version.v5, "v5-20190311-test_hmmer.txt"),
        (Version.v6, "v6-20190311-test_hmmer.txt"),
        (Version.v7, "v7-20190311-test_hmmer.txt"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[versionp]


def test_domtblout(
    version: Union[str, int, Version] = Version.latest()
) -> str:
    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_hmmer.csv"),
        (Version.v5, "v5-20190311-test_hmmer.csv"),
        (Version.v6, "v6-20190311-test_hmmer.csv"),
        (Version.v7, "v7-20190311-test_hmmer.csv"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return version_files[versionp]


def test_counts(
    version: Union[str, int, Version] = Version.latest()
) -> Matrix:
    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = dict()
    filelist = [
        (Version.v4, "v4-20190311-test_counts.npz"),
        (Version.v5, "v5-20190311-test_counts.npz"),
        (Version.v6, "v6-20190311-test_counts.npz"),
        (Version.v7, "v7-20190311-test_counts.npz"),
    ]

    for vname, vfile in filelist:
        version_files[vname] = resource_filename(__name__, vfile)

    return Matrix.read(version_files[versionp])
