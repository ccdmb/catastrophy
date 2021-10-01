import argparse

from typing import List

# import datetime

from catas.cli import MyArgumentParser
from catas.data import sample_fasta

# TODAY = datetime.datetime.utcnow().strftime("%Y%m%d")
FASTA_FILE = sample_fasta()


def cli(prog: str, args: List[str]) -> argparse.Namespace:

    parser = MyArgumentParser(description="Generate test data.")

    parser.add_argument(
        "version",
        type=str,
        help=(
            "The dbcan version name"
        )
    )

    parser.add_argument(
        "hmms",
        type=str,
        help=(
            "path to the hmmer formatted database. "
        )
    )

    parser.add_argument(
        "model",
        type=str,
        help=(
            "Path to the model to generate data for."
        )
    )

    # parser.add_argument(
    #     "-t", "--today",
    #     type=str,
    #     default=TODAY,
    #     help="The date to use for the filename."
    # )

    parser.add_argument(
        "-o", "--outdir",
        type=str,
        default=None,
        help="A directory to put the files in. default will be 'test_{version}'"
    )

    parser.add_argument(
        "-i", "--infile",
        type=str,
        default=FASTA_FILE,
        help=(
            "Sample fasta file"
        )
    )

    parser.add_argument(
        "--hmmscan_path",
        type=str,
        default="hmmscan",
        help=(
            "how to look for hmmscan"
        )
    )

    return parser.parse_args()
