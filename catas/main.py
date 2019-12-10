import sys
import traceback

from typing import Sequence
from typing import TextIO

from catas.predict import predict
from catas.count import cazy_counts_multi
from catas import parsers
from catas.parsers import FileType
from catas.parsers import ParseError
from catas.data import Version
from catas.data import Nomenclature
from catas.data import cazy_list
from catas.cli import cli, MyArgumentError

from catas import __email__
from catas.exitcodes import (
    EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_CLI, EXIT_INPUT_FORMAT, EXIT_SYSERR
)


def runner(
    inhandles: Sequence[TextIO],
    outhandle: TextIO,
    labels: Sequence[str],
    file_format: FileType,
    model_version: Version,
    nomenclature: Nomenclature,
):
    """ Runs the pipeline. """

    parsed = [
        parsers.parse(h, format=file_format, version=model_version)
        for h
        in inhandles
    ]
    required_cols = cazy_list(model_version)
    counts = cazy_counts_multi(parsed, labels, required_cols)
    preds = predict(
        counts,
        version=model_version,
        nomenclature=nomenclature
    )
    preds.write_tsv(outhandle)
    return


def main():
    """ The cli interface to CATAStrophy. """

    try:
        args = cli(prog=sys.argv[0], args=sys.argv[1:])
    except MyArgumentError as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.errno)

    infile_names = [f.name for f in args.infile]

    if args.labels is None:
        labels = infile_names
    elif len(args.labels) != len(args.infile):
        msg = (
            "argument labels and inhandles: \n"
            "When specified, the number of labels must be the same as the "
            "number of input files. Exiting.\n"
        )

        print(msg, file=sys.stderr)
        sys.exit(EXIT_CLI)
    else:
        labels = args.labels

    try:
        runner(
            args.inhandles,
            args.outhandle,
            labels,
            args.file_format,
            args.model_version,
            args.nomenclature
        )

    except ParseError as e:
        if e.line is not None:
            header = "Failed to parse file <{}> at line {}.\n".format(
                e.filename, e.line)
        else:
            header = "Failed to parse file <{}>.\n".format(e.filename)

        print("{}\n{}".format(header, e.message), file=sys.stderr)
        sys.exit(EXIT_INPUT_FORMAT)

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


if __name__ == '__main__':
    main()
