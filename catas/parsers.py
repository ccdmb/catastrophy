import logging
import re
from io import StringIO
from functools import partial

import pandas as pd
from Bio import SearchIO

# from catas import utils
from catas.data import LATEST_VERSION # noqa
from catas.data import hmm_lengths # noqa

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """ Some aspect of parsing failed. """

    def __init__(self, filename, line, message):
        self.filename = filename
        self.line = line
        self.message = message


def parse(handle, format, version=None):
    if format == "dbcan":
        line_handler = parse_dbcan_output
    elif format == "hmmscan3-domtab":
        line_handler = partial(
            parse_hmmer,
            line_handler=parse_domtbl_line,
            version=version,
        )
    elif format == "hmmer3-text":
        line_handler = partial(
            parse_hmmer,
            line_handler=partial(parse_hmmer_output, format="hmmer3-text"),
            version=version,
        )
    else:
        raise ValueError((
            "Parse is only defined for 'dbcan', 'hmmscan3-domtab', "
            "'hmmer3-text'"
        ))
    return line_handler(handle)


# @utils.log(logger, logging.DEBUG)
def decode_object(handle, num_lines=None):
    """ Converts a binary file-like object into a String one.

    Files transferred over http arrive as binary objects.
    If I want to check the first few lines I need to decode it.
    """

    # If we don't specify a number of lines, just use infinity
    if num_lines is None:
        num_lines = float("inf")
    lines = [l.decode() for i, l
             in enumerate(handle)
             if i < num_lines]

    # Create an in memory file like object
    out = StringIO()
    # Write the lines to the file like object.
    out.writelines(lines)

    # Rewind the files to the start so that we can read them
    out.seek(0)
    handle.seek(0)
    return out


# @utils.log(logger, logging.DEBUG)
def split_hmm(string):
    return str(string).rstrip(".hmm")


# @utils.log(logger, logging.DEBUG)
def parse_dbcan_output(handle, sep="\t"):
    """ Parse the tabular output from dbCAN. """

    columns = [
        ("hmm", split_hmm),
        ("hmm_len", int),
        ("seqid", str),
        ("query_len", int),
        ("evalue", float),
        ("hmm_from", int),
        ("hmm_to", int),
        ("ali_from", int),
        ("ali_to", int),
        ("coverage", float)
    ]

    for line_number, line in enumerate(handle, 1):
        line = line.strip()
        # Skip comment lines
        if line.startswith("#"):
            continue
        # Skip empty lines
        elif line == "":
            continue

        line = line.split(sep)

        if len(line) != len(columns):
            raise ParseError(
                handle.name,
                line_number,
                ("Couldn't parse file as dbcan format.\n"
                 "Expected number of columns is {}, received {}."
                 ).format(len(columns), len(line))
            )

        output = dict()
        for i, (col, type_) in enumerate(columns):
            try:
                output[col] = type_(line[i])
            except IndexError:
                raise ParseError(
                    handle.name,
                    line_number,
                    "Couldn't parse file as dbcan format, missing column."
                )
            except ValueError:
                raise ParseError(
                    handle.name,
                    line_number,
                    ("Couldn't parse file as dbcan format.\n"
                     "Illegal value {} received in column {}.\n"
                     "This value should be interpretable as type {}."
                     ).format(line[i], i, type_.__name__)
                )

        yield output
    return


# @utils.log(logger, logging.DEBUG)
def parse_dbcan(handle):
    """ Simple wrapper to read dbcan into dataframe. """
    return pd.DataFrame(parse_dbcan_output(handle))


# @utils.log(logger, logging.DEBUG)
def parse_domtbl_line(handle, sep="\t"):
    """ Parse the tabular output from HMMER domtblout.

    ** Not properly implemented **
    Eventually it might be nice to support this but not super necessary.
    """

    columns = [
        ("hmm", split_hmm),  # target name
        ("hmm_acc", str),
        ("hmm_len", int),
        ("seqid", str),
        ("seqid_acc", str),
        ("seqid_len", int),
        ("fs_evalue", float),  # fs = full sequence
        ("fs_score", float),
        ("fs_bias", float),
        ("domain_idx", int),
        ("domain_num", int),
        ("domain_c_evalue", float),
        ("domain_i_evalue", float),
        ("domain_score", float),
        ("domain_bias", float),
        ("hmm_from", int),
        ("hmm_to", int),
        ("ali_from", int),
        ("ali_to", int),
        ("env_from", int),
        ("env_to", int),
        ("acc", float),  # No idea what this is
        ("description", str)
    ]

    sep = re.compile(r"\s+")

    for line_number, line in enumerate(handle, 1):
        line = line.strip()
        # Skip comment lines
        if line.startswith("#"):
            continue
        # Skip empty lines
        elif line == "":
            continue

        line = sep.split(line)

        if len(line) != len(columns):
            raise ParseError(
                handle.name,
                line_number,
                ("Couldn't parse file as hmmer domtab format.\n"
                 "Expected number of columns is {}, received {}."
                 ).format(len(columns), len(line))
            )

        output = dict()
        for i, (col, type_) in enumerate(columns):
            try:
                output[col] = type_(line[i])
            except IndexError:
                raise ParseError(
                    handle.name,
                    line_number,
                    ("Couldn't parse file as hmmer domtab format, "
                     "missing column.")
                )
            except ValueError:
                raise ParseError(
                    handle.name,
                    line_number,
                    ("Couldn't parse file as hmmer domtab format.\n"
                     "Illegal value {} received in column {}.\n"
                     "Should be interpretable as type {}."
                     ).format(line[i], i, type_.__name__)
                )

        yield output

    return


# @utils.log(logger, logging.DEBUG)
def parse_hmmer_output(handle, format="hmmer3-text"):
    """ Parse the HMMER files into easy to use rows.

    There are two main HMMER output types, the plaintext output and the domain
    table type output (provided by `--domtblout`). The plaintext format is not
    particularly friendly, so we're using the Biopython parser.
    This has the added benefit of handling both the domain table and plaintext
    format with minimal alteration.

    Keyword arguments:
    handle -- A python file handle of the HMMER output.
    format -- A string specifying an input format supported by the Biopython
        SearchIO API. Should be either 'hmmer3-text' or 'hmmscan3-domtab'.

    Returns:
    generator -- A generator yielding dictionaries corresponding to lines.
    """

    matches = SearchIO.parse(handle, format=format)

    # Loop through matches
    for query in matches:
        # For each HMM type that matches the sequence
        for hit in query.hits:
            # For each partial alignment of the HMM to the sequence.
            # Multiple HSPs can occur if there are genuinely two copies of
            # the domain or if a large domain is split into two alignments.
            for hsp in hit.hsps:
                # Format and yield the line elements that we actually want.
                d = {
                    "seqid": query.id,
                    "hmm": split_hmm(hit.id),
                    "domain_i_evalue": hsp.evalue,
                    "ali_from": hsp.query_start,
                    "ali_to": hsp.query_end,
                    "hmm_from": hsp.hit_start,
                    "hmm_to": hsp.hit_end
                }
                yield d
    return


# @utils.log(logger, logging.DEBUG)
def parse_hmmer(handle, line_handler, version=None):
    """ Processes HMMER output in a similar way to the dbCAN hmmscan-parser.sh.

    The dbCAN hmmscan-parser output changed without warning in 2016, and the
    web application doesn't output the same format as the command line version.
    We've implemented the same code in python so that we can use HMMER output
    directly, which should be more stable (and version controlled) over time.

    Keyword arguments:
    handle -- A file-like object (required).
    line_handler -- A callable function like `parse_hmmer_output` that yields
        dictionaries containing required columns (required).
    model_version -- The version of dbCAN that the model was trained with
        (Default: Latest available in data).

    Returns:
    DataFrame -- A pandas dataframe object.
    """

    # Grab the hmm lengths from the datafiles.
    if version is None:
        version = LATEST_VERSION
    hmm_lens = hmm_lengths(version)

    # Get the data in as a dataframe
    df = pd.DataFrame(line_handler(handle))

    if len(df) == 0:
        raise ParseError(
            handle.name,
            None,
            ("Couldn't parse file as HMMER file.\n"
             "Please check that your file is not empty, and that you "
             "specified the correct input format.\nE.G. trying to parsing "
             "a `domtab` file as a regular `hmmer` text file.")
        )

    # Sort columns by seqid, then by alignment coordinates, all ascending
    df.sort_values(["seqid", "ali_from", "ali_to"], axis=0, inplace=True)

    # Get the alignment lengths
    df["ali_length"] = df["ali_to"] - df["ali_from"]

    # Drop rows with alignment lengths of zero
    df = df.loc[df["ali_length"] > 0]

    # Loop through seqids and get the best matches for each
    winners = list()
    for seqid, subdf in df.groupby("seqid"):
        # Loop through each match for each seqid, replacing "winner" as we go.
        winner = None
        for i, row in subdf.iterrows():
            # If this is the first match winner will be None, so we just set it
            # to the first value and continue.
            if winner is None:
                winner = row
                # Continue moves to the next match in the list.
                continue

            # Get the distance between current match and winner
            dist = winner["ali_to"] - row["ali_from"]

            # Decide whether or not the matches are the same
            overlap_thres = 0.5
            winner_nooverlap = (dist / winner["ali_length"]) > overlap_thres
            row_nooverlap = (dist / row["ali_length"]) > overlap_thres

            # If the distance is positive (meaning that row start is before
            # current winner end) and the distance is a large proportion of the
            # alignment length, consider them to be the same.
            if dist > 0 and (winner_nooverlap or row_nooverlap):
                # If the new rows evalue is less than the current winners
                # evalue the new row becomes the new winner!
                if row["domain_i_evalue"] < winner["domain_i_evalue"]:
                    winner = row
            else:
                # We're onto a new alignment and the previous winner gets
                # to stay.
                winners.append(winner)
                winner = row

        # At the end we'll have a new winner to add.
        winners.append(winner)

    winners = pd.DataFrame(winners)

    # Select significant alignments based on evalues. dbCAN uses a threshold
    # of 1e-5 for alignments over 80 AA and 1e-3 for others.
    sig_mask = (
        ((winners["ali_length"] > 80) & (winners["domain_i_evalue"] < 1e-5)) |
        ((winners["ali_length"] <= 80) & (winners["domain_i_evalue"] < 1e-3))
    )

    winners = winners.loc[sig_mask]

    # Grab the HMM lengths and add to dataframe
    winners["hmm_len"] = [hmm_lens[h] for h in winners["hmm"]]

    # Calculate coverage of HMM and filter out hits that don't cover the HMM
    # at least 30%.
    cov = (winners["hmm_to"] - winners["hmm_from"]) / winners["hmm_len"]
    winners["coverage"] = cov
    winners = winners.loc[winners["coverage"] > 0.3]

    # If you need compatibility with dbCAN output change this.
    # winners.rename({"domain_i_evalue": "evalue"})

    # Convert the counts back to a list of dictionaries.
    winners = [r.to_dict() for _, r in winners.iterrows()]
    return winners
