from catas.data import Version

DBCAN_URLS = {
    Version.v4: "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-old@UGA/dbCAN-fam-HMMs.txt.v4",  # noqa
    Version.v5: "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-old@UGA/dbCAN-fam-HMMs.txt.v5",  # noqa
    Version.v6: "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-V6.txt",  # noqa
    Version.v7: "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-V7.txt",  # noqa
    Version.v8: "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-V8.txt",  # noqa
    Version.v9: "https://bcb.unl.edu/dbCAN2/download/dbCAN-HMMdb-V9.txt",
    Version.v10: "https://bcb.unl.edu/dbCAN2/download/dbCAN-HMMdb-V10.txt",
}


def download_file(url: str, destination: str) -> None:
    import requests
    response = requests.get(url)
    response.raise_for_status()

    with open(destination, "wb") as handle:
        for chunk in response.iter_content(chunk_size=256):
            handle.write(chunk)

    return
