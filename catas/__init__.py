import sys
import argparse
import logging

# This has to come before the modules are loaded, so that it will apply.
logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# The # noqa is there to stop linters yelling at me about the `basicConfig`
# coming before these imports.
from catas import utils # noqa
from catas.pipeline import predict # noqa
from catas.counts import cazy_counts # noqa
from catas import parsers # noqa
from catas.parsers import ParseError # noqa

from catas.data import AVAILABLE_VERSIONS # noqa
from catas.data import LATEST_VERSION # noqa
from catas.data import DEFAULT_NOMENCLATURE # noqa
from catas.data import AVAILABLE_NOMENCLATURES # noqa

__program = "catastrophy"
__version = "0.1.0"
__authors = ", ".join(["Darcy Jones", "James Hane"])
__date = "30 March 2017"
__email = "darcy.a.jones@postgrad.curtin.edu.au"
__short_blurb = (
    "Script to predict lifestyle of filamentous plant pathogens using "
    "carbohydrate-active enzymes (CAZymes)."
)

__license = (
    '{__program}-{__version}\n'
    '{__short_blurb}\n\n'
    'Copyright (C) {__date},  {__authors}'
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
)


license = __license.format(**locals())

logger = logging.getLogger(__name__)


@utils.log(logger, logging.DEBUG)
def cli(prog, args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=license,
        epilog=(
            'Example usage:\n'
            '$ %(prog)s -i dbcan_results.csv -o prediction.csv\n'
            '$ %(prog)s -i dbcan_results_1.csv dbcan_results_2.csv '
            '-l result1 result2 -o prediction.csv\n'
        )
    )

    parser.add_argument(
        "-i", "--infile",
        dest="inhandles",
        default=[sys.stdin],
        nargs="+",
        type=argparse.FileType('r'),
        help=(
            "Path to the input file formatted by dbCAN `hmmscan-parser.sh`. "
            "You can specify more than one file by separating them with a "
            "space. Default is STDIN."
        )
    )

    parser.add_argument(
        "-f", "--format",
        dest="file_format",
        default="hmmer",
        choices=["hmmer", "domtab"],  # "dbcan" but i don't want to maintain
        help=(
            "The format that the input is provided in. If multiple files are "
            "specified, all input must be in the same format. HMMER raw "
            "(hmmer, default) and domain table (domtab) formatted files are "
            "accepted."
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
        default=LATEST_VERSION,
        choices=AVAILABLE_VERSIONS,
        help=(
            "The version of the model to use. If you're using old dbCAN "
            "predictions you may have to specify this. The version numbers "
            "are just the dates that the models were trained, so use the "
            "closest version after the date of the dbCAN version that you "
            "used. The latest version is used by default."
        )
    )

    parser.add_argument(
        "-n", "--nomenclature",
        dest="nomenclature",
        default=DEFAULT_NOMENCLATURE,
        choices=AVAILABLE_NOMENCLATURES,
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
        "-v", "--verbose",
        help=("Print progress updates to stdout. Use twice (i.e. -vv or -v -v)"
              "to show debug output."),
        action="count",
        default=0
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version),
        help="Print the version of %(prog)s and exit"
    )

    return parser.parse_args()


def line_writer(series, label=None):
    """ Utility to format output as tsv. """
    if label is None:
        label = str(series.name)

    try:
        values = "\t".join([str(v) for v in series])
    except UnicodeEncodeError:
        values = "\t".join(series)

    return "{}\t{}\n".format(label, values)


def runner(inhandles, outhandle, labels, file_format,
           model_version, nomenclature):
    """ Runs the pipeline. """

    first = True
    for label, handle in zip(labels, inhandles):
        parsed = parsers.parse(handle, format=file_format)
        counts = cazy_counts(parsed, label, version=model_version)

        preds = predict(
            counts,
            version=model_version,
            nomenclature=nomenclature
        )

        if first:
            line = line_writer(preds.index, label="label")
            outhandle.write(line)
            first = False

        line = line_writer(preds, label=label)
        outhandle.write(line)
    return


def main():
    """ The cli interface to CATAStrophy. """

    args = cli(prog=sys.argv[0], args=sys.argv[1:])

    if args.verbose > 1:
        log_level = logging.DEBUG
    elif args.verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logger.setLevel(log_level)

    infile_names = [f.name for f in args.inhandles]

    if args.labels is None:
        labels = infile_names
    elif len(args.labels) != len(args.inhandles):
        logger.error((
            "When specified, the number of labels must be the same as the "
            "number of input files. Exiting.\n"
        ))
        sys.exit(1)
    else:
        labels = args.labels

    # Substitute the short format names for the ones that biopython will accept
    format_map = {
        "hmmer": "hmmer3-text",
        "domtab": "hmmscan3-domtab",
        "dbcan": "dbcan"
    }

    # This is safe because argparse enforces that it must be one of these.
    file_format = format_map[args.file_format]

    logger.info("Running %s v%s", __program, __version)
    logger.info("Using parameters:")
    logger.info("- infile = %s", ", ".join(infile_names))
    logger.info("- format = %s", args.file_format)
    logger.info("- label = %s", ", ".join(labels))
    logger.info("- outfile = %s", args.outhandle.name)
    logger.info("- model = %s", args.model_version)

    try:
        runner(
            args.inhandles,
            args.outhandle,
            labels,
            file_format,
            args.model_version,
            args.nomenclature
        )

    except ParseError as e:
        if e.line is not None:
            header = "Failed to parse file <{}> at line {}.\n".format(
                e.filename, e.line)
        else:
            header = "Failed to parse file <{}>.\n".format(e.filename)

        logger.error("{}\n{}".format(header, e.message))
        sys.exit(1)

    except EnvironmentError as e:
        logger.error((
            "Encountered a system error.\n"
            "We can't control these, and they're usually related to your OS.\n"
            "Try running again."
        ))
        raise e

    except MemoryError:
        logger.error("Ran out of memory!")
        logger.error(("Catastrophy shouldn't use much RAM, so check other "
                      "processes and try running again."))
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Exiting.")
        sys.exit(1)

    except Exception as e:
        logger.error((
            "I'm so sorry, but we've encountered an unexpected error.\n"
            "This shouldn't happen, so please file a bug report with the "
            "authors.\nWe will be extremely grateful!\n\n"
            "You can email us at {}.\n"
            "Alternatively, you can file the issue directly on the repo "
            "<https://bitbucket.org/ccdm-curtin/catastrophy/issues>\n"
        ).format(__email))

        raise e

    return


if __name__ == '__main__':
    main()
