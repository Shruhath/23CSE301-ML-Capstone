"""Download and verify the two Review 1 datasets from UCI.

This script intentionally uses only the Python standard library so data can be
prepared before the project's third-party dependencies are installed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent
RAW_DIR = DATA_DIR / "raw"


@dataclass(frozen=True)
class ExpectedFile:
    archive_name: str
    output_name: str
    sha256: str
    rows: int
    delimiter: str = ","


@dataclass(frozen=True)
class Dataset:
    key: str
    title: str
    url: str
    archive_sha256: str
    output_directory: str
    files: tuple[ExpectedFile, ...]


DATASETS = {
    "regression": Dataset(
        key="regression",
        title="UCI Gas Turbine CO and NOx Emission Data Set",
        url=(
            "https://archive.ics.uci.edu/static/public/551/"
            "gas+turbine+co+and+nox+emission+data+set.zip"
        ),
        archive_sha256=(
            "55fdb1acc25f05bd9c77aac285c424e9154ffb0dbf1bbadb56b69a1142231295"
        ),
        output_directory="gas_turbine",
        files=(
            ExpectedFile(
                "gt_2011.csv",
                "gt_2011.csv",
                "d87ceef9aa59533cc7d924d10de241b1b06ecd11f9b26bab59191ea0f8a76b9a",
                7411,
            ),
            ExpectedFile(
                "gt_2012.csv",
                "gt_2012.csv",
                "be54b9d0e1a7de40c55d32fa489e75de892b000c066b5a09f09a19124ee29100",
                7628,
            ),
            ExpectedFile(
                "gt_2013.csv",
                "gt_2013.csv",
                "13c437bb440ec2045bd12057e6654c41dd4107a661eac16ba2e878e897a08f9e",
                7152,
            ),
            ExpectedFile(
                "gt_2014.csv",
                "gt_2014.csv",
                "c2a03c92c9c3207aad0c6be7de8d9b5b4bfa4720ad0efb2c1f21b6cec4d3f3fa",
                7158,
            ),
            ExpectedFile(
                "gt_2015.csv",
                "gt_2015.csv",
                "9b08f35fde0d4b138232a605db4093c2b8bf9d6757e6f1fbd9534ad616c13591",
                7384,
            ),
        ),
    ),
    "classification": Dataset(
        key="classification",
        title="UCI Predict Students' Dropout and Academic Success",
        url=(
            "https://archive.ics.uci.edu/static/public/697/"
            "predict+students+dropout+and+academic+success.zip"
        ),
        archive_sha256=(
            "e90e55fd65ec462ae283ebeb2cca409319e3460ed898d8754f62fb35cc83a65d"
        ),
        output_directory="student_outcomes",
        files=(
            ExpectedFile(
                "data.csv",
                "data.csv",
                "3ef126de5cefff26eb11fbb4237f1a1401cb64b488e2f1d598c23cedeb4c45ae",
                4424,
                delimiter=";",
            ),
        ),
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_data_rows(path: Path, delimiter: str) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter=delimiter)
        next(reader)
        return sum(1 for row in reader if row)


def validate_file(path: Path, expected: ExpectedFile) -> None:
    actual_hash = sha256_file(path)
    if actual_hash != expected.sha256:
        raise ValueError(
            f"Hash mismatch for {path}: expected {expected.sha256}, got {actual_hash}"
        )

    actual_rows = count_data_rows(path, expected.delimiter)
    if actual_rows != expected.rows:
        raise ValueError(
            f"Row-count mismatch for {path}: expected {expected.rows}, got {actual_rows}"
        )


def existing_dataset_is_valid(dataset: Dataset) -> bool:
    destination = RAW_DIR / dataset.output_directory
    paths = [destination / item.output_name for item in dataset.files]
    if not all(path.is_file() for path in paths):
        return False

    for path, expected in zip(paths, dataset.files, strict=True):
        validate_file(path, expected)
    return True


def download_archive(dataset: Dataset, destination: Path) -> None:
    request = urllib.request.Request(
        dataset.url,
        headers={"User-Agent": "23CSE301-capstone-dataset-downloader/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        with destination.open("wb") as stream:
            shutil.copyfileobj(response, stream)

    actual_hash = sha256_file(destination)
    if actual_hash != dataset.archive_sha256:
        raise ValueError(
            f"Archive hash mismatch for {dataset.title}: "
            f"expected {dataset.archive_sha256}, got {actual_hash}"
        )


def extract_expected_files(dataset: Dataset, archive: Path) -> None:
    destination = RAW_DIR / dataset.output_directory
    destination.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive) as bundle:
        available = set(bundle.namelist())
        for expected in dataset.files:
            if expected.archive_name not in available:
                raise ValueError(
                    f"Expected {expected.archive_name} is absent from {dataset.title} archive"
                )

            output_path = destination / expected.output_name
            temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
            with bundle.open(expected.archive_name) as source:
                with temporary_path.open("wb") as target:
                    shutil.copyfileobj(source, target)
            temporary_path.replace(output_path)
            validate_file(output_path, expected)


def prepare_dataset(dataset: Dataset, force: bool) -> None:
    if not force and existing_dataset_is_valid(dataset):
        print(f"Verified existing dataset: {dataset.title}")
        return

    with tempfile.TemporaryDirectory(prefix=f"{dataset.key}-dataset-") as temp_dir:
        archive = Path(temp_dir) / "dataset.zip"
        print(f"Downloading: {dataset.title}")
        download_archive(dataset, archive)
        extract_expected_files(dataset, archive)

    print(f"Downloaded and verified: {dataset.title}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and verify the Review 1 UCI datasets."
    )
    parser.add_argument(
        "--dataset",
        choices=("all", *DATASETS.keys()),
        default="all",
        help="Select a single track or download both datasets (default: all).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download again and replace existing verified raw files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = DATASETS.values() if args.dataset == "all" else (DATASETS[args.dataset],)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for dataset in selected:
        prepare_dataset(dataset, force=args.force)

    print(f"Raw data directory: {RAW_DIR}")


if __name__ == "__main__":
    main()
