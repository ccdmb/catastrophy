"""
A simpler alternative to a pandas dataframe for non-interactive work.
"""

import csv
import pathlib  # noqa
from typing import cast
from typing import List, Sequence
from typing import Dict, Mapping
from typing import Union
from typing import BinaryIO, TextIO

import numpy as np


class Matrix(object):
    """ A simple wrapper around a numpy array that tracks column and row names.

    Order is row major.
    Using this as an alternative to pandas to get rid of dependency.
    """

    def __init__(
        self,
        rows: Sequence[str],
        columns: Sequence[str],
        arr: np.ndarray,
    ):
        assert len(rows) == arr.shape[0]
        assert len(columns) == arr.shape[1]

        self.rows = list(rows)
        self.columns = list(columns)
        self.arr = arr
        return

    def __getitem__(self, key: Union[str, int]) -> np.ndarray:
        if isinstance(key, str):
            key = self.columns.index(key)

        return self.arr[:, key]

    @classmethod
    def from_row(
        cls,
        row: str,
        columns: Sequence[str],
        arr: np.ndarray
    ) -> "Matrix":
        """ Create a matrix from a single row """

        return cls([row], list(columns), arr.reshape(1, -1))

    @classmethod
    def concat(cls, dfs: Sequence["Matrix"]) -> "Matrix":
        """ Concatenate multiple matrices together by rows (ie. columns are
        matched)
        """

        if len(dfs) == 0:
            return cls([], [], np.zeros((0, 0)))

        columns = dfs[0].columns

        # Columns must all be same shape and names.
        for df in dfs:
            assert df.columns == columns

        # Concatenates and flattens all rows.
        rows = [r for df in dfs for r in df.rows]
        # NB concatenate requires all dfs to have correct dimensions.
        # IE they can't be a flat array.
        arr = np.concatenate([df.arr for df in dfs])
        return cls(rows, columns, arr)

    def as_df(self):
        # This isn't typed so that I don't need pandas as dependency
        import pandas as pd
        return pd.DataFrame(
            data=self.arr,
            index=self.rows,
            columns=self.columns
        )

    @classmethod
    def from_df(cls, df):
        """ Assumes heterogeneous df with rownames. """
        rows = df.index.tolist()
        columns = df.columns.tolist()
        return cls(rows, columns, df.values)

    def as_dict_of_arrays(
        self,
        prefix: str = ""
    ) -> Dict[str, np.ndarray]:
        return {
            f"{prefix}arr": self.arr,
            f"{prefix}rows": np.array(self.rows, dtype='U60'),
            f"{prefix}columns": np.array(self.columns, dtype='U60'),
        }

    @classmethod
    def from_dict_of_arrays(
        cls,
        doa: Mapping[str, np.ndarray],
        prefix: str = ""
    ) -> "Matrix":
        return cls(
            doa[f"{prefix}rows"].tolist(),
            doa[f"{prefix}columns"].tolist(),
            doa[f"{prefix}arr"],
        )

    def write(
        self,
        handle: Union[str, BinaryIO, "pathlib.Path"],
        prefix: str = ""
    ):
        """ Writes matrix out as a numpy file. """
        np.savez(
            handle,
            *self.as_dict_of_arrays(prefix=prefix)
        )
        return

    @classmethod
    def read(
        cls,
        handle: Union[str, BinaryIO, "pathlib.Path"],
        prefix: str = "",
    ) -> "Matrix":
        """ Reads matrix from an numpy file. """
        f = np.load(handle, allow_pickle=False)
        return cls.from_dict_of_arrays(f)

    def write_tsv(
        self,
        filename: Union[str, TextIO],
        rows_colname: str = "# label"
    ):
        """ Write a tsv formatted table from the matrix.

        Note that if you provide a file-object handle to filename, it must
        have been opened with the `newline=''` option (required by csv).
        """
        try:
            if isinstance(filename, str):
                handle: TextIO = open(filename, 'w', newline='')
            else:
                handle = filename

            tab_writer = csv.writer(handle, "excel-tab")

            # Write the header
            tab_writer.writerow([rows_colname] + self.columns)

            # Write the lines
            for rowname, row in zip(self.rows, self.arr):
                tab_writer.writerow([rowname] + list(row))

        finally:
            if isinstance(filename, str):
                handle.close()
        return

    def as_serializable(self) -> List[Dict[str, Union[str, float]]]:
        """ Output the matrix as a dict, which can be easily serialised into
        JSON etc.
        """

        output = list()
        for rowname, row in zip(self.rows, self.arr):
            drow: Dict[str, Union[str, float]] = {
                str(k): float(v)
                for k, v
                in zip(self.columns, row)
            }
            drow["label"] = rowname
            output.append(drow)
        return output

    @classmethod
    def from_serialized(
        cls,
        ser: Sequence[Mapping[str, Union[str, float]]]
    ) -> "Matrix":
        """ Parses a dictionary representation back into a matrix. """

        if len(ser) == 0:
            return cls([], [], np.zeros((0, 0)))

        rows: List[str] = list()
        arr = list()
        columns: List[str] = [k for k, v in ser if k != "label"]
        for row in ser:
            arr_row = list()

            # This helps the type checker.
            # It shouldn't occur at runtime if the spec is observed.
            assert isinstance(row["label"], str)
            rows.append(row["label"])

            for column in columns:
                arr_row.append(row[column])
            arr.append(arr_row)

        return cls(
            rows,
            columns,
            np.array(arr),
        )
