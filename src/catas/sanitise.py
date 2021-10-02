import re

from typing import TextIO
from typing import List, Sequence
from typing import Optional

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio.Data.IUPACData import protein_letters

GAP_REGEX = re.compile(r"-\s")
DEGEN_REGEX = re.compile("BZJUO*", flags=re.IGNORECASE)
IUPAC_REGEX = re.compile(f"[^{protein_letters}X*]", flags=re.IGNORECASE)


class FastaError(Exception):

    def __init__(self, messages: Sequence[str]):
        self.messages = list(messages)
        return


class FastaBadCharError(Exception):

    def __init__(
        self,
        filename: Optional[str],
        id: str,
        invalid_chars: str,
    ):
        self.filename = filename
        self.id = id
        self.invalid_chars = invalid_chars

    def str(self) -> str:
        s = ["BAD CHARACTER:"]
        if self.filename is not None:
            s.append(self.filename)

        s.extend(["ID", self.id, "-", f"'{self.invalid_chars}'"])
        return " ".join(s)


def sanitise_fasta(handle: TextIO, correct: bool) -> List[SeqRecord]:
    out = []

    seqs = SeqIO.parse(handle, format="fasta")
    errors = []
    for seq in seqs:
        if correct:
            newseq = str(seq.seq.rstrip("*")).upper()
            newseq = GAP_REGEX.sub("", newseq)
            newseq = DEGEN_REGEX.sub("X", newseq)
            seq.seq = Seq(newseq)

        match = IUPAC_REGEX.search(str(seq.seq))
        if match is None:
            out.append(seq)
        else:
            all_matches = "".join(sorted(set(
                IUPAC_REGEX.findall(str(seq.seq))
            )))
            if hasattr(handle, "name"):
                n: Optional[str] = handle.name
            else:
                n = None

            errors.append(
                FastaBadCharError(
                    n,
                    seq.id,
                    all_matches
                )
            )

    if len(errors) > 0:
        messages = [e.str() for e in errors]
        raise FastaError(messages)
    elif len(out) == 0:
        if hasattr(handle, "name"):
            n = handle.name
        else:
            n = ""
        raise FastaError([
            f"File {n} appears to be empty or is not Fasta formatted."
        ])

    return out
