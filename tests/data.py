import logging
import os
import shutil
import time
from io import BytesIO
from pathlib import Path

import requests
import tqdm
from dotenv import load_dotenv
from github import Github

root = Path(__file__).resolve().parent

load_dotenv(dotenv_path=(root.parent / ".env"), override=True)

dirstruct = ["cache", "cache/pdf"]

filestruct = ["cache/datefile.txt"]


def create_struct():
    dirstruct.sort(key=len)
    filestruct.sort(key=len)
    for x in dirstruct:
        (root / x).mkdir(parents=True, exist_ok=True)
    for x in filestruct:
        (root / x).touch()


def getfile(url, file):
    body = requests.get(url, timeout=5, stream=True)
    if not isinstance(file, BytesIO):
        file = open(file, "wb")

    shutil.copyfileobj(body.raw, file)
    file.close()


create_struct()

datefile = root / "cache/datefile.txt"
d = datefile.read_text().strip()
try:
    d = int(d)
except ValueError:
    d = int(time.time())

if (d + (7 * 86400)) > time.time():
    print("Using cached data")
else:
    print("Downloading additional test data")
    # shutil.rmtree(root / "cache")
    create_struct()

    token = os.getenv("GITHUB_TOKEN")
    if token is None:
        logging.warning(
            "No github token set, rate limit may cause issue, set environment variable GITHUB_TOKEN, or add a .env file to project root"
        )

    g = Github(token)
    user = g.get_user("py-pdf")
    repo = user.get_repo("sample-files")

    c = repo.get_contents("files.json")
    d = requests.get(c.download_url).json()
    print("- Sample PDF data")
    for x in tqdm.tqdm(d["data"][:3]):
        fpath = x["path"]
        getfile(
            repo.get_contents(fpath).download_url,
            root / "cache" / "pdf" / Path(fpath).name,
        )

    datefile.write_text(str(int(time.time())), "utf-8")


class TestData:
    def __init__(self, data_folder):
        self.data_folder = Path(data_folder)
        self.files = []

        assert self.data_folder.exists(), "Data folder doesn't exist"

        for r, d, f in Path(self.data_folder).walk():
            self.files.extend((Path(self.data_folder) / r / x) for x in f)

    def filter_extension(self, extensions):
        return filter(lambda x: x.suffix.strip(".") in extensions, self.files)


dataset = TestData(root)

print(list(dataset.filter_extension(["cbr"])))
