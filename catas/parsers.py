from io import StringIO
from enum import Enum
from typing import NamedTuple

from Bio import SearchIO

from catas.data import Version
from catas.data import hmm_lengths


class FileType(Enum):
    """ All possible input filetypes that we support. """

    dbcan = 1
    hmmer_text = 2
    hmmer_domtab = 3

    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s):
        try:
            return cls[s]
        except KeyError:
            raise ValueError


class ParseError(Exception):
    """ Some aspect of parsing failed. """

    def __init__(self, filename, line, message):
        self.filename = filename
        self.line = line
        self.message = message


class LineParseError(Exception):
    def __init__(self, message):
        self.message


def parse(handle, format, version=None):
    """ Wrapper that directs parsing bases on enum. """

    version = Version.from_other(version)

    if isinstance(format, str):
        format = FileType[format]

    if format == FileType.dbcan:
        return DBCAN.from_file(handle)
    elif format == FileType.hmmer_domtab:
        parsed = HMMER.from_file(
            handle,
            format="hmmscan3-domtab",
            version=version,
        )
        return parsed
    elif format == FileType.hmmer_text:
        return HMMER.from_file(
            handle,
            format="hmmer3-text",
            version=version,
        )
    else:
        raise ValueError((
            "Parse is only defined for 'dbcan', 'hmmscan3-domtab', "
            "'hmmer3-text'"
        ))


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


def split_hmm(string):
    return str(string).rstrip(".hmm")


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
    def from_string(cls, line):
        """ Parse a single tabular output row from dbCAN. """

        columns = [split_hmm, int, str, int, float, int, int, int, int, float]
        line = line.strip().split('\t')

        if len(columns) != len(line):
            msg = "Wrong number of columns. Found {}, expected {}."
            raise LineParseError(msg.format(len(line), len(columns)))

        output = []
        for i, type_fn in enumerate(columns):
            try:
                output.append(type_fn(line[i]))
            except IndexError:
                # This shouldn't happen because of previous check
                msg = "Couldn't parse file as dbcan format, missing column."
                raise LineParseError(msg)
            except ValueError:
                msg = "Illegal value '{}' received in column {}."
                raise LineParseError(msg.format(line[i], i + 1))
        return cls(*output)

    @classmethod
    def from_file(cls, handle):
        """ Parse a DBCAN file into generator of rows. """

        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            # Skip comment lines
            if line.startswith("#"):
                continue
            # Skip empty lines
            elif line == "":
                continue

            try:
                parsed = cls.from_string(line)
            except LineParseError as e:
                raise ParseError(handle.name, line_number, e.msg)

            yield parsed
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
    def from_file(cls, handle, format="hmmer3-text", version=Version.latest()):
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

        version = Version.from_other(version)

        # This is the threshold used by dbcan to determine if to matches are
        # the same.
        overlap_thres = 0.5

        # Needed to find the coverage of hmms, some formats are missing this.
        hmm_lens = hmm_lengths(version)

        # Parse the file using Biopython.
        matches = SearchIO.parse(handle, format=format)

        # Loop through matches
        try:
            for query in matches:
                # For each HMM type that matches the sequence

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
            msg = (
                "Couldn't parse file as {} format.\n"
                "Double check that the input file is in the right format "
                "(i.e. hmmer_text vs hmmer_domtab).\n"
                "If you believe this is an error, please contact us."
            ).format(format)
            raise ParseError(handle.name, None, msg)
        return

    @classmethod
    def _get_hsp(cls, query, hit, hsp, hmm_lens):
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
    def _distinct_matches(matches, overlap_thres):
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
    def _filter_significant(match):
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
