#!/usr/bin/env python3

import sys
import subprocess
from subprocess import Popen
from subprocess import PIPE

import catas.data

import datetime


def main(version, today, db, model_file, outdir):
    fasta_file = catas.data.sample_fasta()

    command = [
        "hmmscan",
        "--domtblout",
        "{}/{}-{}-test_hmmer.csv".format(outdir, version, TODAY),
        db,
        fasta_file
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open("{}/{}-{}-test_hmmer.txt".format(outdir, version, TODAY), "wb") as handle:
        handle.write(stdout)

    command = [
        "bash",
        "bin/hmmscan-parser.sh",
        "{}/{}-{}-test_hmmer.csv".format(outdir, version, TODAY)
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open("{}/{}-{}-test_dbcan.csv".format(outdir, version, TODAY), "wb") as handle:
        handle.write(stdout)

    from catas.parsers import parse
    from catas.parsers

    from catas.model import Model
    with open(model_file, "rb") as handle:
        model = Model.read(handle)

    with open("{}/{}-{}-test_dbcan.csv".format(outdir, version, TODAY)) as handle:
        parsed = list(parse(handle, format=FileType.dbcan))
required_cols = list(model.hmm_lengths.keys())
counts = cazy_counts_multi([parsed], [labels], required_cols)
cnts.write("../catas/data/{}-{}-test_counts.npz".format(version, TODAY))

        mat_pca = model.pca_model.transform(cnts)
        mat_pca.write("../catas/data/{}-{}-test_pcs.npz".format(version, TODAY))
    return

if __name__ == "__main__":
    args = sys.vargs
    print(args)
    main(args[0], args[1], args[2], args[3], args[4])
