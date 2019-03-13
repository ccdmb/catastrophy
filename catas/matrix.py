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
        return cls([row], columns, arr.reshape(1, -1))

    @classmethod
    def concat(cls, dfs):
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
