import sys
import argparse

from catas.predict import predict
from catas.count import cazy_counts_multi
from catas import parsers
from catas.parsers import FileType
from catas.parsers import ParseError
from catas.data import Version
from catas.data import Nomenclature
from catas.data import cazy_list

__program__ = "catastrophy"
__version__ = "0.1.0"
__authors__ = ", ".join(["Darcy Jones", "James Hane"])
__date__ = "30 March 2017"
__email__ = "darcy.a.jones@postgrad.curtin.edu.au"
__short_blurb__ = (
    "Script to predict lifestyle of filamentous plant pathogens using "
    "carbohydrate-active enzymes (CAZymes)."
)

__license__ = (
    '{__program__}-{__version__}\n'
    '{__short_blurb__}\n\n'
    'Copyright (C) {__date__},  {__authors__}'
    '\n\n'
    'This program is free software: you can redistribute it and/or modify '
    'it under the terms of the GNU General Public License as published by '
    'the Free Software Foundation, either version 3 of the License, or '
    '(at your option) any later version.'
    '\n\n'
    'This program is distributed in the hope that it will be useful, '
    'but WITHOUT ANY WARRANTY; without even the implied warranty of '
    'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the '
    'GNU General Public License for more details.'
    '\n\n'
    'You should have received a copy of the GNU General Public License '
    'along with this program. If not, see <http://www.gnu.org/licenses/>.'
).format(**locals())


def cli(prog, args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Examples:\n\n"
            "```bash\n"
            "$ %(prog)s -i dbcan_results.csv -o prediction.csv\n"
            "$ %(prog)s -i dbcan_results_1.csv dbcan_results_2.csv "
            "-l result1 result2 -o prediction.csv\n"
            "```\n"
        ),
        epilog=(
            "Exit codes:\n\n"
            "0 - Everything's fine\n"
            "64 - Invalid command line usage\n"
            "65 - Input format error\n"
            "66 - Cannot open the input\n"
            "71 - System error\n"
            "73 - Can't create output file\n"
            "74 - IO error\n"
            "\n"
            "Codes loosely based on <https://stackoverflow.com/questions/1101957/are-there-any-standard-exit-status-codes-in-linux>"
        )
    )

    parser.add_argument(
        "-i", "--infile",
        dest="inhandles",
        default=[sys.stdin],
        nargs="+",
        type=argparse.FileType('r'),
        help=(
            "Path to the input file output by HMMER or formatted by dbCAN "
            "`hmmscan-parser.sh`. You can specify more than one file by "
            "separating them with a space. Default is STDIN."
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


def runner(inhandles, outhandle, labels, file_format,
           model_version, nomenclature):
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

    args = cli(prog=sys.argv[0], args=sys.argv[1:])

    infile_names = [f.name for f in args.inhandles]

    if args.labels is None:
        labels = infile_names
    elif len(args.labels) != len(args.inhandles):
        msg = (
            "When specified, the number of labels must be the same as the "
            "number of input files. Exiting.\n"
        )
        print(msg, file=sys.stderr)
        sys.exit(1)
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
        sys.exit(1)

    except EnvironmentError as e:
        msg = (
            "Encountered a system error.\n"
            "We can't control these, and they're usually related to your OS.\n"
            "Try running again."
        )
        print(msg, file=sys.stderr)
        raise e

    except MemoryError:
        msg = (
            "Ran out of memory!\n"
            "Catastrophy shouldn't use much RAM, so check other "
            "processes and try running again."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("Received keyboard interrupt. Exiting.", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        msg = (
            "I'm so sorry, but we've encountered an unexpected error.\n"
            "This shouldn't happen, so please file a bug report with the "
            "authors.\nWe will be extremely grateful!\n\n"
            "You can email us at {}.\n"
            "Alternatively, you can file the issue directly on the repo "
            "<https://bitbucket.org/ccdm-curtin/catastrophy/issues>\n"
        ).format(__email__)
        raise e

    return


if __name__ == '__main__':
    main()
