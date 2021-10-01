from typing import Optional


def call_hmmscan(
    infile: str,
    db: str,
    domtab: str,
    hmmer: str,
    cmd: str = "hmmscan"
) -> None:
    from subprocess import Popen
    from subprocess import PIPE

    command = [
        cmd,
        "--domtblout", domtab,
        db,
        infile
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open(hmmer, "wb") as handle:
        handle.write(stdout)
    return


def call_hmmpress(
    db: str,
    cmd: str = "hmmpress"
) -> None:
    import os
    from subprocess import Popen

    extensions = [".h3f", ".h3i", ".h3m", ".h3p"]
    all_present = True
    any_present = False

    for ext in extensions:
        fname = f"{db}{ext}"
        if os.path.isfile(fname):
            any_present = True
        else:
            all_present = False

    if all_present:
        return

    if any_present:
        for ext in extensions:
            fname = f"{db}{ext}"
            if os.path.isfile(fname):
                os.remove(fname)

    command = [
        cmd,
        db,
    ]

    call = Popen(command)
    stdout, stderr = call.communicate()
    return


def call_hmmscan_parser(
    infile: str,
    outfile: str,
    cmd: Optional[str] = None
) -> None:
    from subprocess import Popen
    from subprocess import PIPE

    if cmd is None:
        from catas.data import hmmscan_parser
        cmd = hmmscan_parser()

    command = [
        "bash",
        cmd,
        infile
    ]
    call = Popen(command, stdout=PIPE)
    stdout, stderr = call.communicate()

    with open(outfile, "wb") as handle:
        handle.write(stdout)
    return
