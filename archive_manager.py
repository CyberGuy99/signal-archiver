from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MAGIC_HEADER = b"SIGARCH1\n"
ARCHIVE_PREFIX = "chat_"
ARCHIVE_SUFFIX = ".arc"
INDEX_FILE = "index.json"


def _archives_dir(data_dir: str | Path = "data/archives") -> Path:
    path = Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _index_path(data_dir: str | Path = "data/archives") -> Path:
    return _archives_dir(data_dir) / INDEX_FILE


def archive_file_path(chunk_id: str, data_dir: str | Path = "data/archives") -> Path:
    return _archives_dir(data_dir) / f"{ARCHIVE_PREFIX}{chunk_id}{ARCHIVE_SUFFIX}"


def write_archive(chunk_id: str, encrypted_blob: bytes, data_dir: str | Path = "data/archives") -> Path:
    archive_path = archive_file_path(chunk_id, data_dir)
    with archive_path.open("wb") as f:
        f.write(MAGIC_HEADER)
        f.write(f"{chunk_id}\n".encode("utf-8"))
        f.write(encrypted_blob)
    return archive_path


def read_archive(chunk_id: str, data_dir: str | Path = "data/archives") -> bytes:
    archive_path = archive_file_path(chunk_id, data_dir)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive chunk not found: {chunk_id}")

    with archive_path.open("rb") as f:
        header = f.readline()
        if header != MAGIC_HEADER:
            raise ValueError("Invalid archive header")

        stored_chunk_id = f.readline().decode("utf-8").strip()
        if stored_chunk_id != chunk_id:
            raise ValueError(f"Archive chunk ID mismatch: expected {chunk_id}, got {stored_chunk_id}")

        return f.read()


def list_archives(data_dir: str | Path = "data/archives") -> list[str]:
    paths = sorted(_archives_dir(data_dir).glob(f"{ARCHIVE_PREFIX}*{ARCHIVE_SUFFIX}"))
    chunk_ids = []
    for path in paths:
        name = path.name
        chunk_ids.append(name[len(ARCHIVE_PREFIX) : -len(ARCHIVE_SUFFIX)])
    return chunk_ids


def load_index(data_dir: str | Path = "data/archives") -> dict[str, Any]:
    index_path = _index_path(data_dir)
    if not index_path.exists():
        return {"runs": []}

    with index_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def append_index_entry(entry: dict[str, Any], data_dir: str | Path = "data/archives") -> None:
    index = load_index(data_dir)
    runs = index.setdefault("runs", [])
    runs.append(entry)

    with _index_path(data_dir).open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def archive_total_size(data_dir: str | Path = "data/archives") -> int:
    total = 0
    for chunk_id in list_archives(data_dir):
        total += archive_file_path(chunk_id, data_dir).stat().st_size
    return total
