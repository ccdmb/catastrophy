import argparse
import sys

from typing import List

from catas import __version__

from catas.parsers import FileType
from catas.cli import MyArgumentParser


def cli(prog: str, args: List[str]) -> argparse.Namespace:

    parser = MyArgumentParser(description="Train models for catastrophy.")

    parser.add_argument(
        "classes",
        type=str,
        help=(
            "A tsv file containing the columns: 'label', 'nomenclature1', "
            "'nomenclature2', nomenclature3'"
        )
    )

    parser.add_argument(
        "hmms",
        type=argparse.FileType('r'),
        help=(
            "Path to the hmmer formatted database. "
            "We use this to get HMM lengths."
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
        "-n", "--nomenclatures",
        default=None,
        type=argparse.FileType('r'),
        help=(
            "A json formatted file containing the keys nomenclature{1,2,3} "
            "and with values as a list of the classes in the order to be "
            "presented. By default use file in catas/data folder."
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
        default=sys.stdout.buffer,
        type=argparse.FileType('wb'),
        help=(
            "File path to write the model to. Default is STDOUT."
        )
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help="Print the version of %(prog)s and exit"
    )

    return parser.parse_args()
