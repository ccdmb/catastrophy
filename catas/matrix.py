"""
A simpler alternative to a pandas dataframe for non-interactive work.
"""

import csv
import numpy as np


class Matrix(object):
    """ A simple wrapper around a numpy array that tracks column and row names.

    Order is row major.
    Using this as an alternative to pandas to get rid of dependency.
    """

    def __init__(self, rows, columns, arr):
        assert len(rows) == arr.shape[0]
        assert len(columns) == arr.shape[1]

        self.rows = rows
        self.columns = columns
        self.arr = arr
        return

    def __getitem__(self, key):
        if isinstance(key, str):
            key = self.columns.index(key)

        return self.arr[:, key]

    @classmethod
    def from_row(cls, row, columns, arr):
        """ Create a matrix from a single row """

        return cls([row], columns, arr.reshape(1, -1))

    @classmethod
    def concat(cls, dfs):
        """ Concatenate multiple matrices together by rows (ie. columns are
        matched) """

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

    def write(self, handle):
        """ Writes matrix out as a numpy file. """
        np.savez(
            handle,
            arr=self.arr,
            rows=self.rows,
            columns=self.columns
        )
        return

    @classmethod
    def read(cls, handle):
        """ Reads matrix from an numpy file. """
        f = np.load(handle, allow_pickle=False)
        return cls(f["rows"].tolist(), f["columns"].tolist(), f["arr"])

    def write_tsv(self, filename, rows_colname="label"):
        """ Write a tsv formatted table from the matrix.

        Note that if you provide a file-object handle to filename, it must
        have been opened with the `newline=''` option (required by csv).
        """
        try:
            if isinstance(filename, str):
                handle = open(filename, 'w', newline='')
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

    def as_serializable(self):
        """ Output the matrix as a dict, which can be easily serialised into
        JSON etc.
        """

        output = list()
        for rowname, row in zip(self.rows, self.arr):
            drow = {str(k): float(v) for k, v in zip(self.columns, row)}
            drow["label"] = rowname
            output.append(drow)
        return output

    @classmethod
    def from_serialized(cls, ser):
        """ Parses a dictionary representation back into a matrix. """

        if len(ser) == 0:
            return cls([], [], np.zeros((0, 0)))

        rows = list()
        arr = list()
        columns = [k for k, v in ser if k != "label"]
        for row in ser:
            arr_row = list()
            rows.append(row["label"])
            for column in columns:
                arr_row.append(row[column])
            arr.append(arr_row)

        return cls(
            rows,
            columns,
            np.array(arr),
        )
