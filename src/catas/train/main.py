import sys
import traceback
import json
from os.path import split, splitext

from typing import Sequence
from typing import TextIO, BinaryIO
from typing import Optional

from catas import parsers
from catas.parsers import FileType
from catas.parsers import ParseError

from catas.cli import MyArgumentError
from catas.train.cli import cli

from catas.count import cazy_counts_multi
from catas.count import HMMError

from catas.model import NomenclatureClass, HMMLengths, Model

from catas import data

from catas import __email__
from catas.exitcodes import (
    EXIT_KEYBOARD, EXIT_UNKNOWN, EXIT_CLI, EXIT_INPUT_FORMAT, EXIT_SYSERR
)


def runner(
    nomenclatures_handle: Optional[TextIO],
    classes: str,
    inhmms: TextIO,
    inhandles: Sequence[TextIO],
    outhandle: BinaryIO,
    labels: Sequence[str],
    file_format: FileType,
):
    """ Runs the pipeline. """

    if nomenclatures_handle is None:
        nomenclatures = data.nomenclatures()
    else:
        nomenclatures = json.load(nomenclatures_handle)

        required_nomenclatures = {"nomenclature1", "nomenclature2",
                                  "nomenclature3"}
        if set(nomenclatures.keys()) != required_nomenclatures:
            raise ValueError("The nomenclatures json file has invalid keys.")

    with open(classes, newline='') as handle:
        class_labels = NomenclatureClass.from_tsv(handle)

    # This checks if there are any labels in input filenames that aren't in
    # the classes tsv, and vice-versa. We want 1-1.
    if len(set(c.label for c in class_labels)
           .symmetric_difference(labels)) != 0:
        print(set(c.label for c in class_labels)
           .symmetric_difference(labels))
        raise ValueError("The file labels and the class labels are different.")

    class_labels_nomenclatures = {
        "nomenclature1": {t.nomenclature1 for t in class_labels},
        "nomenclature2": {t.nomenclature2 for t in class_labels},
        "nomenclature3": {t.nomenclature3 for t in class_labels},
    }

    for nom, nom_class_set in class_labels_nomenclatures.items():
        if len(nom_class_set.symmetric_difference(nomenclatures[nom])) != 0:
            raise ValueError(f"The nomenclatures and class files for {nom} "
                             "don't have the same classes.")

    hmm_lengths = HMMLengths.read_hmm(inhmms)

    parsed = [
        parsers.parse(h, format=file_format, hmm_lens=hmm_lengths)
        for h
        in inhandles
    ]

    required_cols = sorted(hmm_lengths.keys())

    # Columns
    counts = cazy_counts_multi(parsed, labels, required_cols)
    model = Model.fit(counts, class_labels, nomenclatures, hmm_lengths)

    # The model_mean and model_components together make up the model.
    model.write(outhandle)
    return


def main():  # noqa
    try:
        args = cli(prog=sys.argv[0], args=sys.argv[1:])
    except MyArgumentError as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.errno)

    infile_names = [splitext(split(f.name)[-1])[0] for f in args.infile]

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
            args.nomenclatures,
            args.classes,
            args.hmms,
            args.infile,
            args.outhandle,
            labels,
            args.file_format,
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
