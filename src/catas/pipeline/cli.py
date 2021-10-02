import argparse

from typing import List

from catas.cli import MyArgumentParser
from catas.data import Version

from catas import __version__

from catas.exitcodes import (
    EXIT_VALID, EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_CLI, EXIT_INPUT_FORMAT,
    EXIT_INPUT_NOT_FOUND, EXIT_SYSERR, EXIT_CANT_OUTPUT
)


def cli(prog: str, args: List[str]) -> argparse.Namespace:

    import joblib

    parser = MyArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Examples:\n\n"
            "```bash\n"
            "$ %(prog)s -o outdir proteome_1.fasta proteome_2.fasta\n"
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
        "infiles",
        type=str,
        nargs="+",
        help=(
            "Proteome fasta-files to run."
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
        "--hmms",
        type=str,
        help=(
            "Path to the dbCAN hmmer-formatted database. "
            "Note that the specified model version must match the version of "
            "the database specified here."
        )
    )

    parser.add_argument(
        "-o", "--outdir",
        type=str,
        default="results",
        help="A directory to put the files in. default will be 'results'"
    )

    parser.add_argument(
        "--hmmscan_path",
        type=str,
        default="hmmscan",
        help=(
            "Where to look for hmmscan"
        )
    )

    parser.add_argument(
        "--hmmpress_path",
        type=str,
        default="hmmpress",
        help=(
            "Where to look for hmmpress"
        )
    )

    parser.add_argument(
        "--ncpu",
        type=int,
        default=joblib.cpu_count(),
        help="How many processes to run."
    )

    parser.add_argument(
        "-c", "--correct",
        action="store_true",
        default=False,
        help="Replace invalid characters in Fasta files."
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        default=False,
        help="Suppress running feedback."
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help="Print the version of %(prog)s and exit"
    )

    return parser.parse_args()
