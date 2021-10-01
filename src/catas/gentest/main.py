#!/usr/bin/env python3

import sys
import traceback
from os import makedirs
from os.path import basename, splitext
from os.path import join as pjoin

from catas import parsers
from catas.parsers import FileType
from catas.parsers import ParseError

from catas.cli import MyArgumentError
from catas.gentest.cli import cli

from catas.count import cazy_counts_multi
from catas.count import HMMError

from catas.model import Model, RCDResult, PCAWithLabels

from catas.external import call_hmmscan, call_hmmscan_parser

from catas import __email__
from catas.exitcodes import (
    EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_INPUT_FORMAT, EXIT_SYSERR
)


def runner(
    infile: str,
    hmms: str,
    model_fname: str,
    version: str,
    outdir: str,
    hmmscan_cmd: str,
):
    """ Runs the pipeline. """

    makedirs(outdir, exist_ok=False)

    # Just touch it to make easier to integrate into package.
    with open(pjoin(outdir, "__init__.py"), "w") as handle:
        print('', file=handle)

    domtab_filename = pjoin(outdir, "hmmer_domtab.tsv")
    hmmer_filename = pjoin(outdir, "hmmer_text.txt")
    dbcan_filename = pjoin(outdir, "hmmer_dbcan.tsv")
    counts_filename = pjoin(outdir, "counts.tsv")
    pca_filename = pjoin(outdir, "pca.tsv")
    rcd_filename = pjoin(outdir, "rcd.tsv")

    with open(model_fname, "rb") as model_handle:
        model = Model.read(model_handle)

    call_hmmscan(infile, hmms, domtab_filename, hmmer_filename, hmmscan_cmd)
    call_hmmscan_parser(domtab_filename, dbcan_filename)

    required_cols = list(model.hmm_lengths.keys())
    with open(dbcan_filename, "r") as dbcan_handle:
        parsed = parsers.parse(
            dbcan_handle,
            format=FileType.dbcan,
            hmm_lens=model.hmm_lengths
        )

        label = splitext(basename(infile))[0]
        counts = cazy_counts_multi([parsed], [label], required_cols)
        counts.write_tsv(counts_filename)

    predictions = model.predict(counts)

    with open(pca_filename, "w") as pca_handle:
        (PCAWithLabels
         .concat([predictions])
         .write_tsv(pca_handle))

    with open(rcd_filename, "w") as rcd_handle:
        RCDResult.write_tsv(rcd_handle, predictions.rcd)

    return


def main():  # noqa
    try:
        args = cli(prog=sys.argv[0], args=sys.argv[1:])
    except MyArgumentError as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.errno)

    if args.outdir is None:
        outdir = f"test_{args.version}"
    else:
        outdir = args.outdir

    try:
        runner(
            args.infile,
            args.hmms,
            args.model,
            args.version,
            outdir,
            args.hmmscan_path
        )

    except ParseError as e:
        if e.line is not None:
            header = "Failed to parse file <{}> at line {}.\n".format(
                e.filename, e.line)
        else:
            header = "Failed to parse file <{}>.\n".format(e.filename)

        print("{}\n{}".format(header, e.message), file=sys.stderr)
        sys.exit(EXIT_INPUT_FORMAT)

    except HMMError as e:
        msg = (
            "Encountered an hmm that wasn't present in the training data.\n"
            f"Offending HMMs were: {', '.join(e.hmms)}"
        )
        print(msg, file=sys.stderr)
        sys.exit(EXIT_INPUT_FORMAT)
        pass

    except OSError as e:
        msg = (
            "Encountered a system error.\n"
            "We can't control these, and they're usually related to your OS.\n"
            "Try running again.\n"
        )
        print(msg, file=sys.stderr)
        print(e.strerror, file=sys.stderr)
        sys.exit(EXIT_SYSERR)

    except MemoryError:
        msg = (
            "Ran out of memory!\n"
            "Catastrophy shouldn't use much RAM, so check other "
            "processes and try running again."
        )
        print(msg, file=sys.stderr)
        sys.exit(EXIT_SYSERR)

    except KeyboardInterrupt:
        print("Received keyboard interrupt. Exiting.", file=sys.stderr)
        sys.exit(EXIT_KEYBOARD)

    except Exception as e:
        msg = (
            "I'm so sorry, but we've encountered an unexpected error.\n"
            "This shouldn't happen, so please file a bug report with the "
            "authors.\nWe will be extremely grateful!\n\n"
            "You can email us at {}.\n"
            "Alternatively, you can file the issue directly on the repo "
            "<https://github.com/ccdmb/catastrophy/issues>\n\n"
            "Please attach a copy of the following message:"
        ).format(__email__)
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(EXIT_UNKNOWN)
    return
