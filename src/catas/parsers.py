from io import StringIO
from enum import Enum
import sys
import re

from typing import NamedTuple
from typing import TextIO, BinaryIO
from typing import Union, Optional
from typing import Sequence, List
from typing import Dict
from typing import Iterator

from Bio import SearchIO

# These are only used for type checking
from Bio.SearchIO._model.query import QueryResult
from Bio.SearchIO._model.hit import Hit
from Bio.SearchIO._model.hsp import HSP


REGEX = re.compile(r"\.p?hmm$")
TEXT_FIRSTLINE = re.compile(r"^# hmmscan ::")  # noqa: E501
DOMTAB_FIRSTLINE = re.compile(r"^#\s+--- full sequence ---.*$")  # noqa: E501
DBCAN_FIRSTLINE = re.compile("\t".join([
    r"\S+", "[0-9]+", r"\S+", "[0-9]+",
    r"([0-9]*[.])?[0-9]+([eE][-+]?\d+)?",
    "[0-9]+", "[0-9]+", "[0-9]+", "[0-9]+",
    r"([0-9]*[.])?[0-9]+([eE][-+]?\d+)?",
]))


def predict_filetype(handle: TextIO):

    handle.seek(0)
    line = ""

    # Just in case there is a blank line at the top.
    for line in handle:
        line = line.strip()
        if line != "":
            break

    if line == "":
        msg = (
            "The input file does not contain any non-empty lines.\n"
            "Please check your inputs and if you believe that "
            "this is an error, please contact us."
        )

        if hasattr(handle, "name"):
            name: Optional[str] = handle.name
        else:
            name = None

        raise ParseError(name, None, msg)

    if TEXT_FIRSTLINE.match(line):
        return "hmmer_text"
    elif DOMTAB_FIRSTLINE.match(line):
        return "hmmer_domtab"
    elif DBCAN_FIRSTLINE.match(line):
        return "dbcan"
    else:
        msg = (
            "The input file does not appear to be in any "
            "of the supported formats.\n"
            "Please check your inputs and if you believe that "
            "this is an error, please contact us."
        )

        if hasattr(handle, "name"):
            name = handle.name
        else:
            name = None

        raise ParseError(name, None, msg)


class FileType(Enum):
    """ All possible input filetypes that we support. """

    dbcan = 1
    hmmer_text = 2
    hmmer_domtab = 3

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_string(cls, s: str) -> "FileType":
        try:
            return cls[s]
        except KeyError:
            raise ValueError


class ParseError(Exception):
    """ Some aspect of parsing failed. """

    def __init__(
        self,
        filename: Optional[str],
        line: Optional[int],
        message: str
    ):
        self.filename = filename
        self.line = line
        self.message = message
        return


class LineParseError(Exception):

    def __init__(self, message: str):
        self.message = message
        return


def parse(
    handle: TextIO,
    format: Union[str, FileType],
    hmm_lens: Optional[Dict[str, int]],
) -> Union[Iterator["HMMER"], Iterator["DBCAN"]]:
    """ Wrapper that directs parsing bases on enum.

    Keyword arguments:
    handle -- A file-like object to parse.
    format -- The file-format that the handle is in, should be a FileType
        object.
    hmm_lens -- Required only for the HMMer formats. A dictionary mapping the
        hmm names to the length of the HMM model.

    Returns:
    A generator over the parsed records.
    Records will be either HMMER or DBCAN objects.
    """

    if isinstance(format, str):
        format = FileType[format]

    if format == FileType.dbcan:
        return DBCAN.from_file(handle)

    elif format == FileType.hmmer_domtab:
        assert hmm_lens is not None
        parsed = HMMER.from_file(
            handle,
            format="hmmscan3-domtab",
            hmm_lens=hmm_lens,
        )
        return parsed

    elif format == FileType.hmmer_text:
        assert hmm_lens is not None
        return HMMER.from_file(
            handle,
            format="hmmer3-text",
            hmm_lens=hmm_lens,
        )
    else:
        raise ValueError((
            "Parse is only defined for 'dbcan', 'hmmscan3-domtab', "
            "'hmmer3-text'"
        ))


def decode_object(
    handle: BinaryIO,
    num_lines: Optional[float] = None,
) -> StringIO:
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


def split_hmm(string: str) -> str:
    return REGEX.sub("", str(string))


def parse_str_as_int(val: str, column: str) -> int:
    try:
        return int(val)
    except ValueError:
        msg = "Illegal value '{}' received in column {}. Expected an integer."
        raise LineParseError(msg.format(val, column))


def parse_str_as_float(val: str, column: str) -> float:
    try:
        return float(val)
    except ValueError:
        msg = "Illegal value '{}' received in column {}. Expected a float."
        raise LineParseError(msg.format(val, column))


class DBCAN(NamedTuple):
    """ Stores a single row of the DBCAN tab-delimited file. """

    hmm: str
    hmm_len: int
    seqid: str
    query_len: int
    evalue: float
    hmm_from: int
    hmm_to: int
    ali_from: int
    ali_to: int
    coverage: float

    @classmethod
    def from_string(cls, line: str) -> "DBCAN":
        """ Parse a single tabular output row from dbCAN. """

        columns = ["hmm", "hmm_len", "seqid", "query_len", "evalue",
                   "hmm_from", "hmm_to", "ali_from", "ali_to", "coverage"]

        sline = line.strip().split('\t')

        if len(columns) != len(sline):
            msg = "Wrong number of columns. Found {}, expected {}."
            raise LineParseError(msg.format(len(sline), len(columns)))

        output = dict(zip(columns, sline))
        hmm = split_hmm(output["hmm"])
        hmm_len = parse_str_as_int(output["hmm_len"], "hmm_len")
        seqid = output["seqid"]
        query_len = parse_str_as_int(output["query_len"], "query_len")
        evalue = parse_str_as_float(output["evalue"], "evalue")
        hmm_from = parse_str_as_int(output["hmm_from"], "hmm_from")
        hmm_to = parse_str_as_int(output["hmm_to"], "hmm_to")
        ali_from = parse_str_as_int(output["ali_from"], "ali_from")
        ali_to = parse_str_as_int(output["ali_to"], "ali_to")
        coverage = parse_str_as_float(output["coverage"], "coverage")

        return cls(hmm, hmm_len, seqid, query_len, evalue, hmm_from, hmm_to,
                   ali_from, ali_to, coverage)

    @classmethod
    def from_file(cls, handle: TextIO) -> Iterator["DBCAN"]:
        """ Parse a DBCAN file into generator of rows. """

        nmatches = 0
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            # Skip comment lines
            if line.startswith("#"):
                continue
            # Skip empty lines
            elif line == "":
                continue

            nmatches += 1
            try:
                parsed = cls.from_string(line)
            except LineParseError as e:
                predicted = predict_filetype(handle)
                if hasattr(handle, "name"):
                    name = handle.name
                else:
                    name = None

                if predicted != "dbcan":
                    msg = (
                        "Couldn't parse file as dbcan format.\n"
                        "Double check that the input file is in the right "
                        "format (i.e. dbcan vs hmmer_text vs hmmer_domtab).\n"
                        "Based on the file contents, we think this is in "
                        "'{}' format.\n"
                        "If you believe this is an error, please contact us."
                    ).format(predicted)
                    raise ParseError(name, None, msg)

                else:
                    raise ParseError(name, line_number, e.message)

            yield parsed

        if nmatches == 0:
            if hasattr(handle, "name"):
                name = handle.name
            else:
                name = None

            print(
                f"WARNING: input {name} has zero CAZymes detected.",
                file=sys.stderr
            )
            print(
                "WARNING: This will result in poor predictions.",
                file=sys.stderr
            )
            print(
                "WARNING: Please double check that you have "
                "specified the correct file format.",
                file=sys.stderr
            )
        return


class HMMER(NamedTuple):
    """ Stores a single HMMER match. """

    hmm: str
    hmm_len: int
    seqid: str
    evalue: float
    hmm_from: int
    hmm_to: int
    ali_from: int
    ali_to: int
    coverage: float

    @classmethod
    def from_file(  # noqa: C901
        cls,
        handle: TextIO,
        hmm_lens: Dict[str, int],
        format: str = "hmmer3-text",
    ) -> Iterator["HMMER"]:
        """ Processes HMMER output in a similar way to dbCAN hmmscan-parser.sh.

        There are two main HMMER output types, the plaintext output and the
        domain table type output (provided by `--domtblout`). The plaintext
        format is not particularly friendly, so we're using the Biopython
        parser.  This has the added benefit of handling both the domain table
        and plaintext format with minimal alteration.

        Keyword arguments:
        handle -- A python file handle of the HMMER output.
        format -- A string specifying an input format supported by the
            Biopython SearchIO API. Should be either 'hmmer3-text' or
            'hmmscan3-domtab'.

        Returns:
        generator -- A generator yielding named tuples corresponding to lines.
        """

        # This should never be raised at runtime, but avoids foot shooting
        # while writing code.
        assert format in ("hmmer3-text", "hmmscan3-domtab")

        # This is the threshold used by dbcan to determine if to matches are
        # the same.
        overlap_thres = 0.5

        qcounts = 0

        # Parse the file using Biopython.
        matches = SearchIO.parse(handle, format=format)

        # Loop through matches
        try:
            for query in matches:
                # For each HMM type that matches the sequence
                qcounts += 1

                query_matches = list()
                for hit in query.hits:
                    # For each partial alignment of the HMM to the sequence.
                    # Multiple HSPs can occur if there are genuinely two
                    # copies of the domain or if a large domain is split
                    # into two alignments.
                    for hsp in hit.hsps:
                        # Drop rows with alignment lengths of zero
                        if hsp.query_end - hsp.query_start <= 0:
                            continue

                        # Format and yield the line elements that we want.
                        row = cls._get_hsp(query, hit, hsp, hmm_lens)
                        query_matches.append(row)
                # Get the best match for overlapping matches.
                query_matches.sort(key=lambda x: (x.ali_from, x.ali_to))
                query_winners = cls._distinct_matches(
                    query_matches,
                    overlap_thres
                )
                # Yield the rows.
                for winner in query_winners:
                    # If this winner passes the coverage and evalue thresholds
                    # yield it.
                    if cls._filter_significant(winner):
                        yield winner

        except AssertionError:
            predicted = predict_filetype(handle)
            msg = (
                "Couldn't parse file as {} format.\n"
                "Double check that the input file is in the right format "
                "(i.e. dbcan vs hmmer_text vs hmmer_domtab).\n"
                "Based on the file contents, we think this is in "
                "'{}' format.\n"
                "If you believe this is an error, please contact us."
            ).format(format, predicted)

            if hasattr(handle, "name"):
                name = handle.name
            else:
                name = None

            raise ParseError(name, None, msg)

        except KeyError as e:
            msg = (
                "The file appears to be a searched against a different "
                "version of DBCAN than specified.\n"
                "The CAZyme group {} doesn't exist in this version.\n"
                "Please check the database version and contact us if you "
                "think this was a mistake."
            ).format(e.args)

            if hasattr(handle, "name"):
                name = handle.name
            else:
                name = None

            raise ParseError(name, None, msg)

        if qcounts == 0:
            if hasattr(handle, "name"):
                name = handle.name
            else:
                name = None

            predicted = predict_filetype(handle)
            if format != predicted:
                msg = (
                    "Couldn't parse file as {} format.\n"
                    "Double check that the input file is in the right format "
                    "(i.e. dbcan vs hmmer_text vs hmmer_domtab).\n"
                    "Based on the file contents, we think this is in "
                    "'{}' format.\n"
                    "If you believe this is an error, please contact us."
                ).format(format, predicted)
                raise ParseError(name, None, msg)
            else:
                print(
                    f"WARNING: input {name} has zero CAZymes detected.",
                    file=sys.stderr
                )
                print(
                    "WARNING: This will result in poor predictions.",
                    file=sys.stderr
                )
                print(
                    "WARNING: Please double check that you have "
                    "specified the correct file format.",
                    file=sys.stderr
                )
                print(
                    "WARNING: For HMMER output, try using the alternate "
                    "format e.g. 'hmmer_text' or 'hmmer_domtab'.",
                    file=sys.stderr
                )
        return

    @classmethod
    def _get_hsp(
        cls,
        query: QueryResult,
        hit: Hit,
        hsp: HSP,
        hmm_lens: Dict[str, int]
    ) -> "HMMER":
        """ Construct a record from a biopython SearchIO tree. """

        hmm = split_hmm(hit.id)
        hmm_len = hmm_lens[hmm]

        hmm_from = hsp.hit_start
        hmm_to = hsp.hit_end

        coverage = (hmm_to - hmm_from) / hmm_len
        return cls(
            hmm=hmm,
            hmm_len=hmm_len,
            seqid=query.id,
            evalue=hsp.evalue,
            hmm_from=hmm_from,
            hmm_to=hmm_to,
            ali_from=hsp.query_start,
            ali_to=hsp.query_end,
            coverage=coverage,
        )

    @staticmethod
    def _distinct_matches(
        matches: Sequence["HMMER"],
        overlap_thres: float
    ) -> List["HMMER"]:
        # Accumulate winners into a list.
        winners = list()

        # Keep track of the current best hits.
        winner = None
        winner_ali_length = 0

        # Loop through each match for each seqid, replacing "winner" as we go.
        for match in matches:
            # If this is the first match winner will be None, so we just set
            # it to the first value and continue.
            if winner is None:
                winner = match
                winner_ali_length = winner.ali_to - winner.ali_from
                # Continue moves to the next match in the list.
                continue

            # Get the distance between current match and winner
            dist = winner.ali_to - match.ali_from

            # Decide whether or not the matches are the same
            match_ali_length = match.ali_to - match.ali_from
            winner_nooverlap = (dist / winner_ali_length) > overlap_thres
            match_nooverlap = (dist / match_ali_length) > overlap_thres

            # If the distance is positive (meaning that row start is before
            # current winner end) and the distance is a large proportion of
            # the alignment length, consider them to be the same.
            if dist > 0 and (winner_nooverlap or match_nooverlap):
                # If the new rows evalue is less than the current winners
                # evalue the new row becomes the new winner!
                if match.evalue < winner.evalue:
                    winner = match
                    winner_ali_length = match_ali_length
            else:
                # We're onto a new alignment and the previous winner gets
                # to stay.
                winners.append(winner)
                winner = match
                winner_ali_length = match_ali_length

        # At the end we'll have a new winner to add.
        # But not if the list was empty.
        if winner is not None:
            winners.append(winner)
        return winners

    @staticmethod
    def _filter_significant(match: "HMMER") -> bool:
        """ Select significant alignments based on evalues and coverage.

        dbCAN uses a threshold of 1e-5 for alignments over 80 AA
        and 1e-3 for others. A coverage threshold of 0.3 is used.
        """

        if match.coverage < 0.3:
            return False

        is_long = (match.ali_to - match.ali_from) > 80

        if is_long:
            return match.evalue < 1e-5
        else:
            return match.evalue < 1e-3
