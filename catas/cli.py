import argparse
import sys

from typing import List

from catas.parsers import FileType
from catas.data import Version
from catas.data import Nomenclature

from catas import __version__

from catas.exitcodes import (
    EXIT_VALID, EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_CLI, EXIT_INPUT_FORMAT,
    EXIT_INPUT_NOT_FOUND, EXIT_SYSERR, EXIT_CANT_OUTPUT
)


class MyArgumentParser(argparse.ArgumentParser):

    def error(self, message: str):
        """ Override default to have more informative exit codes. """
        self.print_usage(sys.stderr)
        raise MyArgumentError("{}: error: {}".format(self.prog, message))


class MyArgumentError(Exception):

    def __init__(self, message: str):
        self.message = message
        self.errno = EXIT_CLI

        # This is a bit hacky, but I can't figure out another way to do it.
        if "No such file or directory" in message:
            if "infile" in message:
                self.errno = EXIT_INPUT_NOT_FOUND
            elif "outfile" in message:
                self.errno = EXIT_CANT_OUTPUT
        return


def cli(prog: str, args: List[str]) -> argparse.Namespace:

    parser = MyArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Examples:\n\n"
            "```bash\n"
            "$ %(prog)s -o prediction.csv dbcan_results.csv\n"
            "$ %(prog)s -l result1 result2 -o prediction.csv "
            "dbcan_results_2.csv dbcan_results_1.csv\n"
            "```\n"
        ),
        epilog=(
            "Exit codes:\n\n"
            f"{EXIT_VALID} - Everything's fine\n"
            f"{EXIT_KEYBOARD} - Keyboard interrupt\n"
            f"{EXIT_CLI} - Invalid command line usage\n"
            f"{EXIT_INPUT_FORMAT} - Input format error\n"
            f"{EXIT_INPUT_NOT_FOUND} - Cannot open the input\n"
            f"{EXIT_SYSERR} - System error\n"
            f"{EXIT_CANT_OUTPUT} - Can't create output file\n"
            f"{EXIT_UNKNOWN} - Unhandled exception, please file a bug!\n"
        )
    )

    parser.add_argument(
        "infile",
        nargs="+",
        type=argparse.FileType('r'),
        help=(
            "Path to the input file output by HMMER or formatted by dbCAN "
            "`hmmscan-parser.sh`. You can specify more than one file by "
            "separating them with a space."
        )
    )

    parser.add_argument(
        "-f", "--format",
        dest="file_format",
        type=FileType.from_string,
        default=FileType.hmmer_text,
        choices=list(FileType),
        help=(
            "The format that the input is provided in. If multiple files are "
            "specified, all input must be in the same format. HMMER raw "
            "(hmmer_text, default) and domain table (hmmer_domtab) formatted "
            "files are accepted. Files processed by the dbCAN formatter "
            "`hmmscan-parser.sh` are also accepted using the `dbcan` option."
        )
    )

    parser.add_argument(
        "-l", "--label",
        dest="labels",
        default=None,
        nargs="+",
        help=(
            "Label to give the prediction for the input file. Specify more "
            "than one label by separating them with a space. The number of "
            "labels should be the same as the number of input files. "
            "By default, the filenames are used as labels."
        )
    )

    parser.add_argument(
        "-o", "--outfile",
        dest="outhandle",
        default=sys.stdout,
        type=argparse.FileType('w'),
        help=(
            "File path to write tab delimited output to. Default is STDOUT."
        )
    )

    parser.add_argument(
        "-m", "--model",
        dest="model_version",
        default=Version.latest(),
        type=Version.from_string,
        choices=list(Version),
        help=(
            "The version of the model to use. If you're using old dbCAN "
            "predictions you may have to specify this. The version numbers "
            "are just the versions of dbCAN used to train the models so just "
            "select the dbCAN version that you used. The latest version is "
            "used by default."
        )
    )

    parser.add_argument(
        "-n", "--nomenclature",
        dest="nomenclature",
        default=Nomenclature.default(),
        type=Nomenclature.from_string,
        choices=list(Nomenclature),
        help=(
            "The nomenclature type to use. "
            "Nomenclature1 is the classical symbiont, saprotroph, "
            "(hemi)biotroph, necrotroph system. Nomenclature2 separates "
            "wilts from necrotrophs, and considers symbionts as a class "
            "of biotroph. Nomenclature3 is the system proposed in the "
            "paper (default)."
        )
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help="Print the version of %(prog)s and exit"
    )

    return parser.parse_args()
