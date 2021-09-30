import re
from collections import OrderedDict
import csv

import pathlib  # noqa
from typing import Sequence, Tuple, List
from typing import Mapping, Dict
from typing import NamedTuple, Set
from typing import TextIO, BinaryIO
from typing import Union, Optional, Any

import numpy as np
from numpy.linalg import norm

from catas.matrix import Matrix
from catas import parsers


def groupby_numpy(noms: np.ndarray, m: Matrix, order: Sequence[str]) -> Matrix:
    """ This is a helper funtion to do groupby like things without pandas.

    Keyword arguments:
    noms -- An array containing the classes for each row in the matrix.
    m -- A matrix containing PCs for each sample. Samples as rows.
    order -- A list of nomenclatures in the order that they should
        appear in the output. Note, these must be unique.

    Assertions:
    Each element in `order` must be unique.

    Returns:
    Matrix -- A matrix of centroids for each nomenclature (rows)
        and PC (columns).
    """

    seen: Set[str] = set()
    for o in order:
        assert o not in seen
        seen.add(o)

    centroids = {
        nom: np.mean(m.arr[noms == nom], axis=0)
        for nom
        in np.unique(noms)
    }

    out_arr = np.array([centroids[nom] for nom in order])
    return Matrix(rows=order, columns=m.columns, arr=out_arr)


class CentroidsModel(Matrix):

    @classmethod
    def fit(
        cls,
        m: Matrix,
        classes: Mapping[str, str],
        order: Sequence[str],
    ) -> "CentroidsModel":
        """ Find the centroids given a some labels and a matrix.
        Matrix rownames should match, the keys for the classes typing.

        Keyword arguments:
        m -- A matrix containing PCs (columns) for each label (rows).
        classes -- A dictionary mapping labels to nomenclature classes.
        order -- A list of nomenclatures in the order that they should appear
            in the output.

        Assertions:
        Each element in `order` must be unique.
        """

        noms = np.array([classes[r] for r in m.rows])

        centroids = groupby_numpy(noms, m, order)
        return cls(
            rows=centroids.rows,
            columns=centroids.columns,
            arr=centroids.arr
        )

    def distances(self, points: Matrix) -> Matrix:
        """ Given a point in PCA space, find the distance to each centroid.

        Keyword arguments:
        points -- A Matrix representing the location of sample(s) in PC space.

        Returns:
        Matrix -- A Matrix object giving the euclidean distance to each
            class centroid indexed by the class names.
        """

        # This computes the distance matrix, with samples in rows and
        # centroids as columns.
        diffs = np.apply_along_axis(lambda x: x - self.arr, 1, points.arr)
        normed = np.apply_along_axis(norm, 2, diffs)

        # Grab the class names from the centroids
        new_columns = self.rows

        # return a new series with the class names as index
        return Matrix(rows=points.rows, columns=new_columns, arr=normed)

    @staticmethod
    def _rcd(dists: Matrix) -> Matrix:
        """ Private method to compute rcd.

        This is separate for testing purposes.
        """

        min_ = dists.arr.min(axis=1).reshape(-1, 1)
        max_ = dists.arr.max(axis=1).reshape(-1, 1)
        ratio = (dists.arr - min_) / (max_ - min_)
        rcd_ = 1 - ratio

        # Return the RCDs as a series object with original names/index
        return Matrix(rows=dists.rows, columns=dists.columns, arr=rcd_)

    def rcd(self, points: Matrix) -> Matrix:
        """ Given some points in PCA space, finds the RCD.

        Keyword arguments:
        points -- A Matrix representing the location of sample(s) in PC space.

        Returns:
        Matrix -- A Matrix object with the RCD values for each class.
        """

        dists = self.distances(points)
        return self._rcd(dists)


class NomenclatureClass(NamedTuple):
    """ Contain simple info about training genomes. """

    label: str
    genome: str  # Which species/organism/genome version it is from.
    nomenclature1: str
    nomenclature2: str
    nomenclature3: str

    @classmethod
    def from_tsv(cls, handle: TextIO) -> List["NomenclatureClass"]:
        """ Read from a tsv file.

        The handle must be opened with the newline='' parameter.
        """

        reader = csv.DictReader(handle, delimiter='\t')
        output = list()

        for i, row in enumerate(reader):
            label = row.get("label", None)
            genome = row.get("genome", None)
            n1 = row.get("nomenclature1", None)
            n2 = row.get("nomenclature2", None)
            n3 = row.get("nomenclature3", None)

            if None in (label, genome, n1, n2, n3):
                raise parsers.ParseError(
                    handle.name,
                    i,
                    (
                        "Missing one of the required columns ('label', "
                        "'genome', 'nomenclature1', 'nomenclature2', "
                        "'nomenclature3')."
                    )
                )

            # this is to keep static analysis happy
            assert label is not None
            assert genome is not None
            assert n1 is not None
            assert n2 is not None
            assert n3 is not None

            output.append(cls(label, genome, n1, n2, n3))

        return output

    @classmethod
    def as_numpy_array(
        cls,
        results: Sequence["NomenclatureClass"]
    ) -> np.ndarray:
        """ Convert list of RCD results to a structured array. """

        return np.array(results, dtype=[
            ("label", "<U100"),
            ("genome", "<U100"),
            ("nomenclature1", "<U100"),
            ("nomenclature2", "<U100"),
            ("nomenclature3", "<U100"),
        ])

    @classmethod
    def from_numpy_array(cls, a: np.ndarray) -> List["NomenclatureClass"]:
        return [
            NomenclatureClass(
                str(r["label"]),
                str(r["genome"]),
                str(r["nomenclature1"]),
                str(r["nomenclature2"]),
                str(r["nomenclature3"])
            )
            for r
            in a
        ]


class RCDResult(NamedTuple):
    """ Contain info about RCD values. """

    label: str
    nomenclature: str
    nomenclature_class: str
    value: float

    @classmethod
    def from_matrix(cls, m: Matrix, nomenclature: str) -> List["RCDResult"]:
        """ Convert a wide matrix to a long format list of RCDResults.

        Keyword arguments:
        m -- A matrix to transform from wide to long format.
        nomenclature -- A string containing the nomenclature to repeat in
            output.

        Returns
        A list of RCDResult objects.
        """

        import itertools

        mapped = [
            cls(l, n, c, v)
            for ((l, c), n, v)
            in zip(
                itertools.product(m.rows, m.columns),
                itertools.repeat(nomenclature),
                m.arr.flatten()
            )
        ]
        return mapped

    @classmethod
    def as_numpy_array(cls, results: Sequence["RCDResult"]) -> np.ndarray:
        """ Convert list of RCD results to a structured array. """

        return np.array(results, dtype=[
            ("label", "<U100"),
            ("nomenclature", "<U100"),
            ("nomenclature_class", "<U100"),
            ("value", "float")
        ])

    @classmethod
    def from_numpy_array(cls, a: np.ndarray) -> List["RCDResult"]:
        return [
            RCDResult(
                str(r["label"]),
                str(r["nomenclature"]),
                str(r["nomenclature_class"]),
                float(r["value"])
            )
            for r
            in a
        ]

    @classmethod
    def write_tsv(cls, h: TextIO, a: Sequence["RCDResult"]):
        """ Write a bunch of results to a tsv file.

        Keyword argument:
        h -- A file like object to write to.
        a -- A list of RCDResults as output from `to_predictions_array`.
        """

        sorted_results = sorted(
            a,
            key=lambda r: (r.nomenclature, r.label,
                           -1 * r.value, r.nomenclature_class)
        )

        np.savetxt(
            h,
            RCDResult.as_numpy_array(sorted_results),
            delimiter='\t',
            fmt=["%s", "%s", "%s", "%f"],
            header="label\tnomenclature\tclass\tvalue"
        )
        return


class PCAModel(object):

    def __init__(self, means: np.ndarray, components: np.ndarray):
        """ Stores the necessary data and methods to do PCA transformations.
        """
        self.means = means
        self.components = components
        return

    @classmethod
    def fit(cls, counts: Matrix, n_components: int = 16) -> "PCAModel":
        """ Fit the PC model to find the loadings etc.

        Keyword arguments:
            counts -- A matrix of CAZyme counts.
            n_components -- The number of components to retain in the model.
            """
        # This is not a package dependency because we don't
        # expect regular users to train their own models.
        from sklearn.decomposition import PCA

        pipeline = PCA(n_components=n_components, svd_solver="full")
        pipeline.fit(counts.arr)

        return cls(pipeline.mean_, pipeline.components_)

    def transform(self, counts: Matrix) -> Matrix:
        """ Takes a matrix of CAZyme counts and gets PCA transformed values.

        NB this is based on the sklearn implementation.
        Used to avoid compatibility issues between skl versions.

        Keyword arguments:
        counts -- A Matrix containing CAZyme counts.

        Returns:
        Matrix -- A matrix object with the PCA transformed values.
        """

        values = counts.arr.astype(float)
        X = values - self.means
        X_transformed = np.dot(X, self.components.T)

        columns = [
            "pc{:0>2}".format(i + 1)
            for i
            in range(X_transformed.shape[1])
        ]

        return Matrix(rows=counts.rows, columns=columns, arr=X_transformed)

    def as_dict_of_arrays(self, prefix: str = "") -> Dict[str, np.ndarray]:
        return {
            f"{prefix}means": self.means,
            f"{prefix}components": self.components,
        }

    @classmethod
    def from_dict_of_arrays(
        cls,
        doa: Mapping[str, np.ndarray],
        prefix: str = ""
    ) -> "PCAModel":
        return cls(doa[f"{prefix}means"], doa[f"{prefix}components"])


class HMMLengths(OrderedDict):

    """ A subclass of an ordered dictionary. """

    @classmethod
    def read_hmm(cls, handle: TextIO) -> "HMMLengths":
        """ Find the lengths of the HMMs.

        Keyword arguments:
        handle -- A file-like object to a HMMER formatted text database.
        """

        regex = re.compile(r"\s+")
        output = list()

        current_name = None

        for line in handle:
            if line.startswith("NAME"):
                line = regex.split(line.strip(), maxsplit=1)[1]
                current_name = parsers.split_hmm(line)

            elif line.startswith("LENG"):
                line = regex.split(line.strip(), maxsplit=1)[1]

                assert current_name is not None, line
                output.append((current_name, int(line)))
                current_name = None

        # Sort by the hmm name
        output.sort(key=lambda t: t[0])
        return cls(output)

    def to_array(self) -> np.ndarray:
        """ Convert to a numpy structured array. """
        return np.array(
            list(self.items()),
            dtype=[("hmm", 'U60'), ("count", 'uint64')]
         )

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "HMMLengths":
        """ Create from a numpy structured array. """
        return cls(arr)


class PCAWithLabels(object):

    def __init__(
        self,
        pca: Matrix,
        rcd: Sequence[RCDResult],
        classes: Optional[Sequence[NomenclatureClass]] = None,
    ):
        """ Keep the rcd and PCA results together.

        Return type for the models.
        """

        self.pca = pca
        self.rcd = rcd
        self.classes = classes
        return

    def as_dict_of_arrays(self, prefix: str = "") -> Dict[str, np.ndarray]:
        out = {
            f"{prefix}rcd": RCDResult.as_numpy_array(self.rcd),
        }

        out.update(self.pca.as_dict_of_arrays(f"{prefix}pca_"))

        if self.classes is not None:
            out[f"{prefix}classes"] = NomenclatureClass.as_numpy_array(
                self.classes
            )
        return out

    @classmethod
    def from_dict_of_arrays(
        cls,
        doa: Mapping[str, np.ndarray],
        prefix: str = ""
    ) -> "PCAWithLabels":
        rcd = RCDResult.from_numpy_array(doa[f"{prefix}rcd"])
        pca = Matrix.from_dict_of_arrays(doa, f"{prefix}pca_")

        if f"{prefix}classes" in doa:
            classes: Optional[List[NomenclatureClass]] = (
                NomenclatureClass
                .from_numpy_array(doa[f"{prefix}classes"])
            )
        else:
            classes = None
        return cls(pca, rcd, classes)

    @classmethod
    def concat(cls, pwls: Sequence["PCAWithLabels"]) -> "PCAWithLabels":
        pca = Matrix.concat([p.pca for p in pwls])

        rcd: List[RCDResult] = []
        classes: Optional[List[NomenclatureClass]] = None
        for p in pwls:
            rcd.extend(p.rcd)

            if p.classes is not None:
                if classes is None:
                    classes = []

                classes.extend(p.classes)

        return cls(pca, rcd, classes)

    def write_tsv(self, h: TextIO, threshold: float = 0.8):
        "Write a copy if the results to a tsv file."

        if self.classes is not None:
            classes: Optional[Dict[str, NomenclatureClass]] = {
                r.label: r for r in self.classes
            }
        else:
            classes = None

        best_rcds: Dict[Tuple[str, str], RCDResult] = dict()
        sig_rcds: Dict[Tuple[str, str], List[str]] = dict()

        for rcd in self.rcd:
            id_ = (rcd.nomenclature, rcd.label)
            if rcd.value >= threshold:
                if id_ not in sig_rcds:
                    sig_rcds[id_] = [rcd.nomenclature_class]
                else:
                    sig_rcds[id_].append(rcd.nomenclature_class)

            if id_ not in best_rcds:
                best_rcds[id_] = rcd
            elif rcd.value > best_rcds[id_].value:
                best_rcds[id_] = rcd

        # First we setup the columns.
        columns = [("label", "<U100")]
        if self.classes is not None:
            columns.extend([
                ("genome", "<U100"),
                ("nomenclature1", "<U100"),
                ("nomenclature2", "<U100"),
                ("nomenclature3", "<U100"),
            ])

        columns.extend([
            ("nomenclature1_pred", "<U100"),
            ("nomenclature2_pred", "<U100"),
            ("nomenclature3_pred", "<U100"),
            ("nomenclature1_ancillary", "<U300"),
            ("nomenclature2_ancillary", "<U300"),
            ("nomenclature3_ancillary", "<U300"),
        ])

        columns.extend([(p, "<U10") for p in self.pca.columns])

        # Using any here so we can have length of tuple depend on matrix size.
        rows: List[Any] = list()
        for label, matrix_row in zip(self.pca.rows, self.pca.arr):
            row: List[str] = [label]

            if classes is not None:
                clss = classes.get(label, None)
                if clss is None:
                    row.extend(list("...."))
                else:
                    row.extend([
                        classes[label].genome,
                        classes[label].nomenclature1,
                        classes[label].nomenclature2,
                        classes[label].nomenclature3,
                    ])

            row.extend([
                best_rcds[("nomenclature1", label)].nomenclature_class,
                best_rcds[("nomenclature2", label)].nomenclature_class,
                best_rcds[("nomenclature3", label)].nomenclature_class,
                ",".join(sig_rcds[("nomenclature1", label)]),
                ",".join(sig_rcds[("nomenclature2", label)]),
                ",".join(sig_rcds[("nomenclature3", label)]),
            ])

            row.extend(map(str, list(matrix_row)))

            assert len(row) == len(columns)
            rows.append(tuple(row))

        np.savetxt(
            h,
            np.array(rows, dtype=columns),
            delimiter="\t",
            fmt=["%s" for _ in columns],
            header="\t".join(c[0] for c in columns)
        )
        return


class Model(object):

    def __init__(
        self,
        n1_centroids: CentroidsModel,
        n2_centroids: CentroidsModel,
        n3_centroids: CentroidsModel,
        pca_model: PCAModel,
        hmm_lengths: HMMLengths,
        training_data: PCAWithLabels,
    ):
        """ A Model contains all of the bits and methods to predict RCDS.

        Keyword arguments:
        n1_centroids -- A centroids model containing the centroids for each PC
            for each nomenclature one class.
        n2_centroids -- As for n1_centroids but for nomenclature two.
        n3_centroids -- As for n1_centroids but for nomenclature three.
        """

        self.n1_centroids = n1_centroids
        self.n2_centroids = n2_centroids
        self.n3_centroids = n3_centroids
        self.pca_model = pca_model
        self.hmm_lengths = hmm_lengths
        self.training_data = training_data
        return

    @classmethod
    def fit(
        cls,
        counts: Matrix,
        classes: Sequence[NomenclatureClass],
        nomenclatures: Mapping[str, Sequence[str]],
        hmm_lengths: HMMLengths,
        n_components: int = 16,
    ) -> "Model":
        """ Train the models given some counts.

        Keyword arguments:
        counts -- A matrix of counts for each hmm (columns), and label (rows).
        classes -- A list of nomenclature class objects.
        nomenclatures -- A dict mapping nomenclature versions to a list
            of the nomenclature names in the order that they should
            appear in the output.
        hmm_lengths -- A hmm lengths object mapping hmm names to the length
            of the model.
        n_components -- The number of components to include in the model.
        """

        # Fit the PC models.
        pca = PCAModel.fit(counts, n_components)

        # Get the actual pca transformed values.
        trans = pca.transform(counts)

        # Get a dict mapping labels to nomenclature1 classes.
        n1_dict = {c.label: c.nomenclature1 for c in classes}
        n2_dict = {c.label: c.nomenclature2 for c in classes}
        n3_dict = {c.label: c.nomenclature3 for c in classes}

        # Get a non-redundant list of classes in sorted order.
        n1_classes = sorted(set(n1_dict.values()))

        # Find the centroids
        n1_centroids = CentroidsModel.fit(
            trans,
            n1_dict,
            n1_classes
        )

        n2_centroids = CentroidsModel.fit(
            trans,
            n2_dict,
            sorted(set(n2_dict.values())),
        )

        n3_centroids = CentroidsModel.fit(
            trans,
            n3_dict,
            sorted(set(n3_dict.values())),
        )

        # Get the RCD predictions for the training data.
        n1_rcd = n1_centroids.rcd(trans)
        n2_rcd = n2_centroids.rcd(trans)
        n3_rcd = n3_centroids.rcd(trans)

        rcd = RCDResult.from_matrix(n1_rcd, "nomenclature1")
        rcd.extend(RCDResult.from_matrix(n2_rcd, "nomenclature2"))
        rcd.extend(RCDResult.from_matrix(n3_rcd, "nomenclature3"))

        return cls(
            n1_centroids,
            n2_centroids,
            n3_centroids,
            pca,
            hmm_lengths,
            PCAWithLabels(trans, rcd, classes)
        )

    def predict(self, counts: Matrix) -> PCAWithLabels:
        """ Given a matrix of counts, find the PC transformation and the RCDs.

        Keyword arguments:
        counts -- A `Matrix` containing the cazyme counts (required).

        Returns:
        Array -- A structured array containing RCD values.
        Matrix -- A matrix containing the PC transformed counts.
        """

        pca_transformed = self.pca_model.transform(counts)
        n1_rcd = self.n1_centroids.rcd(pca_transformed)
        n2_rcd = self.n2_centroids.rcd(pca_transformed)
        n3_rcd = self.n3_centroids.rcd(pca_transformed)

        rcd = RCDResult.from_matrix(n1_rcd, "nomenclature1")
        rcd.extend(RCDResult.from_matrix(n2_rcd, "nomenclature2"))
        rcd.extend(RCDResult.from_matrix(n3_rcd, "nomenclature3"))

        return PCAWithLabels(pca_transformed, rcd)

    def as_dict_of_arrays(self, prefix="") -> Dict[str, np.ndarray]:
        """ Convert the object to something that we can save easily. """

        output = {f"{prefix}hmm_lengths": self.hmm_lengths.to_array()}

        output.update(
            self.pca_model.as_dict_of_arrays(prefix=f"{prefix}pca_model_")
        )

        output.update(
            self.n1_centroids.as_dict_of_arrays(
                prefix=f"{prefix}n1_centroids_"
            )
        )
        output.update(
            self.n2_centroids.as_dict_of_arrays(
                prefix=f"{prefix}n2_centroids_"
            )
        )
        output.update(
            self.n3_centroids.as_dict_of_arrays(
                prefix=f"{prefix}n3_centroids_"
            )
        )

        output.update(
            self.training_data.as_dict_of_arrays(
                prefix=f"{prefix}training_data_"
            )
        )

        return output

    @classmethod
    def from_dict_of_arrays(
        cls,
        doa: Mapping[str, np.ndarray],
        prefix: str = ""
    ) -> "Model":
        """ Create new model from saved version.

        Intended to be used on np.load output.
        """

        hmm_lengths = HMMLengths.from_array(doa[f"{prefix}hmm_lengths"])

        pca_model = PCAModel.from_dict_of_arrays(
            doa,
            prefix=f"{prefix}pca_model_"
        )

        n1_centroids = CentroidsModel.from_dict_of_arrays(
            doa,
            prefix=f"{prefix}n1_centroids_"
        )

        n2_centroids = CentroidsModel.from_dict_of_arrays(
            doa,
            prefix=f"{prefix}n2_centroids_"
        )

        n3_centroids = CentroidsModel.from_dict_of_arrays(
            doa,
            prefix=f"{prefix}n3_centroids_"
        )

        training_data = PCAWithLabels.from_dict_of_arrays(
            doa,
            prefix=f"{prefix}training_data_"
        )

        # This is to appease the typechecker.
        assert isinstance(n1_centroids, CentroidsModel)
        assert isinstance(n2_centroids, CentroidsModel)
        assert isinstance(n3_centroids, CentroidsModel)

        assert isinstance(training_data, PCAWithLabels)

        return cls(n1_centroids, n2_centroids, n3_centroids,
                   pca_model, hmm_lengths, training_data)

    def write(
        self,
        handle: Union[str, BinaryIO, "pathlib.Path"],
        prefix: str = ""
    ):
        """ Write a model to a numpy binary file. """

        np.savez(
            handle,
            **self.as_dict_of_arrays(prefix=prefix)
        )
        return

    @classmethod
    def read(
        cls,
        handle: Union[str, BinaryIO, "pathlib.Path"],
        prefix: str = "",
    ) -> "Model":
        """ Read a model from a numpy binary file. """

        f = np.load(handle, allow_pickle=False)
        return cls.from_dict_of_arrays(f, prefix=prefix)
