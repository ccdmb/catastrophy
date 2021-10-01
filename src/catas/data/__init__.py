"""
Stored data for use during runtime or testing.

Because dbCAN is an evolving database, we'll have to maintain several models
for each database release. The latest version will always we the default one.
"""

import json
from enum import Enum

from typing import Dict
from typing import List
from typing import Union
from typing import TypeVar, Type

T = TypeVar('T', bound="MyEnum")


def resource_filename(module, resource):
    """ Emulates the behaviour of the old setuptools resource_filename command.

    Basically it just gets rid of the context manager thing, because it's not
    needed. None of the files are zip files or create any temporary files
    that need to be cleaned up.

    This function would be unsafe to use with anything that will be extracted.
    """

    from importlib.resources import path
    with path(module, resource) as handler:
        filename = str(handler)

    return filename


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

    v4 = 4
    v5 = 5
    v6 = 6
    v7 = 7
    v8 = 8
    v9 = 9
    v10 = 10

    @classmethod
    def latest(cls) -> "Version":
        return cls.v10


def hmmscan_parser() -> str:
    return resource_filename(__name__, "hmmscan-parser.sh")


def model_filepath(
    version: Union[str, int, Version] = Version.latest()
) -> str:
    """ Loads PCA parameters. """

    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    version_files = {
        Version.v4: resource_filename(__name__, "model_v4_20211001.npz"),
        Version.v5: resource_filename(__name__, "model_v5_20211001.npz"),
        Version.v6: resource_filename(__name__, "model_v6_20211001.npz"),
        Version.v7: resource_filename(__name__, "model_v7_20211001.npz"),
        Version.v8: resource_filename(__name__, "model_v8_20211001.npz"),
        Version.v9: resource_filename(__name__, "model_v9_20211001.npz"),
        Version.v10: resource_filename(__name__, "model_v10_20211001.npz"),
    }

    return version_files[versionp]


def nomenclatures_filepath() -> str:
    """ Loads list containing names and correct order to display classes. """

    return resource_filename(__name__, "nomenclatures.json")


def nomenclatures() -> Dict[str, List[str]]:
    """ Loads list containing names and correct order to display classes. """

    filename = nomenclatures_filepath()

    with open(filename, "r") as handle:
        d = json.load(handle)

    assert isinstance(d, dict)

    for k, v in d.items():
        assert isinstance(v, list)
        assert all(isinstance(vi, str) for vi in v)

    return d


def sample_fasta() -> str:
    # There's no actual version for this.
    return resource_filename(__name__, "test_data.fasta")


def test_files(
    version: Union[str, int, Version] = Version.latest()
) -> Dict[str, str]:
    # Handle strings as input instead of just enums.
    versionp = Version.from_other(version)

    dirs = {
        Version.v4: "test_v4",
        Version.v5: "test_v5",
        Version.v6: "test_v6",
        Version.v7: "test_v7",
        Version.v8: "test_v8",
        Version.v9: "test_v9",
        Version.v10: "test_v10",
    }

    want_files = {
        "hmmer_text": "hmmer_text.txt",
        "hmmer_domtab": "hmmer_domtab.tsv",
        "hmmer_dbcan": "hmmer_dbcan.tsv",
        "pca": "pca.tsv",
        "rcd": "rcd.tsv",
        "counts": "counts.tsv",
    }

    files = dict()

    for key, val in want_files.items():
        files[key] = resource_filename(__name__ + "." + dirs[versionp], val)

    return files
