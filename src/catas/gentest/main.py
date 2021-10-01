#!/usr/bin/env python3

import sys
import traceback
from os.path import basename
from os.path import join as pjoin

from catas import parsers
from catas.parsers import FileType
from catas.parsers import ParseError

from catas.cli import MyArgumentError
from catas.train.cli import cli

from catas.count import cazy_counts_multi
from catas.count import HMMError

from catas.model import Model

from catas.data import hmmscan_parser

from catas import __email__
from catas.exitcodes import (
    EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_INPUT_FORMAT, EXIT_SYSERR
)


def call_hmmer(
    infile: str,
    db: str,
    domtab: str,
    hmmer: str,
    cmd: str = "hmmscan"
) -> None:
    from subprocess import Popen
    from subprocess import PIPE

    command = [
        cmd,
        "--domtblout", domtab,
        db,
        infile
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open(hmmer, "wb") as handle:
        handle.write(stdout)
    return


def call_hmmscan_parser(
    infile: str,
    outfile: str,
    cmd: str = "hmmscan-parser.sh"
) -> None:
    from subprocess import Popen
    from subprocess import PIPE

    command = [
        "bash",
        cmd,
        infile
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open(outfile, "wb") as handle:
        handle.write(stdout)
    return


def runner(
    infile: str,
    hmms: str,
    model_fname: str,
    version: str,
    today: str,
    outdir: str,
    hmmscan_cmd: str,
):
    """ Runs the pipeline. """

    fname_prefix = pjoin(outdir, f"{version}-{today}")
    domtab_filename = f"{fname_prefix}-test_hmmer.csv"
    hmmer_filename = f"{fname_prefix}-test_hmmer.txt"
    dbcan_filename = f"{fname_prefix}-test_dbcan.csv"
    counts_filename = f"{fname_prefix}-test_counts.npz"
    pcs_filename = f"{fname_prefix}-test_pcs.npz"

    with open(model_fname, "rb") as model_handle:
        model = Model.read(model_handle)

    call_hmmer(infile, hmms, domtab_filename, hmmer_filename, hmmscan_cmd)

    hmmscan_parser_cmd = hmmscan_parser()
    call_hmmscan_parser(domtab_filename, dbcan_filename, hmmscan_parser_cmd)

    with open(dbcan_filename, "r") as dbcan_handle:
        parsed = parsers.parse(
            dbcan_handle,
            format=FileType.dbcan,
            hmm_lens=model.hmm_lengths
        )

    required_cols = list(model.hmm_lengths.keys())
    counts = cazy_counts_multi([parsed], [basename(infile)], required_cols)
    counts.write(counts_filename)

    mat_pca = model.pca_model.transform(counts)
    mat_pca.write(pcs_filename)
    return


def main():  # noqa
    try:
        args = cli(prog=sys.argv[0], args=sys.argv[1:])
    except MyArgumentError as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.errno)

    try:
        runner(
            args.infile,
            args.hmms,
            args.model,
            args.version,
            args.today,
            args.outdir,
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
            "<https://bitbucket.org/ccdm-curtin/catastrophy/issues>\n\n"
            "Please attach a copy of the following message:"
        ).format(__email__)
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(EXIT_UNKNOWN)
    return
