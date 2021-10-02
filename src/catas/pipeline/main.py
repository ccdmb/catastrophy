#!/usr/bin/env python3

import sys
import traceback
from os import makedirs
from os.path import isfile, basename, splitext, getsize
from os.path import join as pjoin

from typing import List, Optional

from requests.exceptions import HTTPError

from catas.parsers import ParseError

from catas.external import call_hmmscan, call_hmmpress

from catas.cli import MyArgumentError
from catas.pipeline.cli import cli

from catas.count import HMMError
from catas.data import Version, model_filepath

from catas.model import Model

from catas.parsers import FileType
from catas.sanitise import sanitise_fasta, FastaError

from catas.main import runner as catas_runner

from catas import __email__
from catas import __version__
from catas.exitcodes import (
    EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_INPUT_FORMAT,
    EXIT_IOERR, EXIT_SYSERR
)


def download_dbcan(version: Version, outdir: str) -> str:
    from ..dbcan import DBCAN_URLS, download_file
    from urllib.parse import urlparse
    import os.path

    makedirs(pjoin(outdir, "downloads"), exist_ok=True)
    url = DBCAN_URLS[version]
    url_fname = basename(urlparse(url).path)
    url_fname = pjoin(outdir, "downloads", url_fname)

    if not os.path.exists(url_fname):
        try:
            download_file(url, url_fname)
        except Exception as e:
            if os.path.isfile(url_fname):
                os.remove(url_fname)
                raise e
    return url_fname


def check_fastas(infiles: List[str], correct: bool, outdir: str) -> List[str]:
    from Bio import SeqIO
    errors = []

    if correct:
        new_infiles = []
    else:
        new_infiles = infiles

    if correct:
        makedirs(pjoin(outdir, "fastas"), exist_ok=True)

    for f in infiles:
        with open(f, "r") as handle:
            try:
                seqs = sanitise_fasta(handle, correct)
            except FastaError as e:
                errors.extend(e.messages)
                continue

        if correct:
            new_filename = pjoin(outdir, "fastas", basename(f))
            SeqIO.write(seqs, new_filename, "fasta")
            new_infiles.append(new_filename)

    if len(errors) > 0:
        raise FastaError(errors)

    assert len(infiles) == len(new_infiles)
    return new_infiles


def runner(  # noqa
    infiles: List[str],
    version: Version,
    outdir: str,
    hmms: Optional[str],
    hmmscan_path: str,
    hmmpress_path: str,
    ncpu: int,
    correct: bool,
    quiet: bool,
):
    """ Runs the pipeline. """
    from joblib import Parallel, delayed

    if not quiet:
        print(f"# CATAStrophy v{__version__}\n")

    makedirs(outdir, exist_ok=True)

    if not quiet:
        print("checking Fasta files")
    infiles = check_fastas(infiles, correct, outdir)

    if hmms is None:
        if not quiet:
            print(f"downloading dbCAN {version}")
        hmms = download_dbcan(version, outdir)

    if not quiet:
        print("pressing dbCAN HMMER database")

    call_hmmpress(hmms, cmd=hmmpress_path)

    def parallel_runner(f):
        bname = pjoin(outdir, "search", splitext(basename(f))[0])
        domtab = f"{bname}_domtab.tsv"
        txt = f"{bname}_hmmer.txt"

        # Skip computation
        # The txt file is written after computation so
        # its a better indicator of whether the process succeeded or not
        if isfile(txt) and (getsize(txt) > 0):
            if not quiet:
                print(f"- CACHED: {f}")

            return domtab

        call_hmmscan(f, hmms, domtab, txt, hmmscan_path)

        if not quiet:
            print(f"- COMPLETED: {f}")
        return domtab

    if not quiet:
        print("running hmmscan on proteomes:")

    makedirs(pjoin(outdir, "search"), exist_ok=True)
    domtabs = Parallel(n_jobs=ncpu, prefer="threads")(
        delayed(parallel_runner)(f) for f in infiles
    )

    if not quiet:
        print("\nclassifying proteomes")

    with open(model_filepath(version), "rb") as handle:
        model = Model.read(handle)

    labels = [basename(f[:-len("_domtab.tsv")]) for f in domtabs]

    domtab_handles = [open(h, "r") for h in domtabs]
    rcd_handle = open(pjoin(outdir, "classifications.tsv"), 'w')
    pca_handle = open(pjoin(outdir, "pca.tsv"), 'w')

    try:
        catas_runner(
            domtab_handles,
            rcd_handle,
            pca_handle,
            pjoin(outdir, "counts.tsv"),
            labels,
            FileType.hmmer_domtab,
            model
        )
    except Exception as e:
        for f in domtab_handles:
            f.close()

        rcd_handle.close()
        pca_handle.close()
        raise e

    if not quiet:
        print("Finished!")

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
            args.infiles,
            args.model_version,
            outdir,
            args.hmms,
            args.hmmscan_path,
            args.hmmpress_path,
            args.ncpu,
            args.correct,
            args.quiet
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

    except FastaError as e:
        msg = [
            "Encountered an error while checking input fasta files."
        ]
        msg.extend(e.messages)
        print("\n".join(msg), file=sys.stderr)
        sys.exit(EXIT_INPUT_FORMAT)

    except HTTPError as e:

        msg = [
            "Encountered an exception while trying to download the dbCAN "
            "database."
        ]

        if e.response is not None:
            msg.append(f"URL: {e.response.url}")
            msg.append(f"Code: {e.status_code}")

        print("\n".join(msg), file=sys.stderr)
        sys.exit(EXIT_IOERR)

    # except HTTPConnectionPool:
    #     msg = (
    #         "Encountered an exception while trying to download the dbCAN "
    #         "database. It's likely that the URL is broken. \n"
    #         "Please try downloading the database yourself and providing the "
    #         "file."
    #     )
    #     print(msg, file=sys.stderr)
    #     sys.exit(EXIT_IOERR)

    except OSError as e:
        msg = (
            "Encountered a system error.\n"
            "We can't control these, and they're usually related to your OS.\n"
            "Try running again.\n"
        )
        print(msg, file=sys.stderr)
        print(e, file=sys.stderr)
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
