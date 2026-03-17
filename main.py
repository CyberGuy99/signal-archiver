from __future__ import annotations

import argparse
import getpass
import sys
from datetime import datetime, timezone
from pathlib import Path

from archive_manager import (
    append_index_entry,
    archive_file_path,
    archive_total_size,
    list_archives,
    read_archive,
    write_archive,
)
from chunker import chunk_messages
from compressor import compress_chunk, decompress_chunk
from encryptor import decrypt_data, derive_key, encrypt_data
from parser import parse_signal_export
from viewer import format_messages


def _archives_dir() -> Path:
    return Path("data/archives")


def _ratio_percent(original_size: int, compressed_size: int) -> float:
    if original_size <= 0:
        return 0.0
    return ((original_size - compressed_size) / original_size) * 100


def _resolve_password(cli_password: str | None) -> str:
    if cli_password:
        return cli_password
    return getpass.getpass("Password: ")


def cmd_compress(input_file: str, password: str | None = None) -> int:
    input_path = Path(input_file)
    messages = parse_signal_export(input_path)
    chunks = chunk_messages(messages)

    if not chunks:
        print("No messages found to compress.")
        return 0

    key = derive_key(_resolve_password(password))

    written_archives: list[Path] = []
    for chunk in chunks:
        compressed = compress_chunk(chunk)
        encrypted = encrypt_data(compressed, key)
        archive_path = write_archive(chunk["chunk_id"], encrypted)
        written_archives.append(archive_path)

    original_size = input_path.stat().st_size
    compressed_size = sum(path.stat().st_size for path in written_archives)
    ratio = _ratio_percent(original_size, compressed_size)

    append_index_entry(
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "input_file": str(input_path),
            "input_size": original_size,
            "chunk_ids": [chunk["chunk_id"] for chunk in chunks],
            "archive_size": compressed_size,
        }
    )

    print(f"Compressed {len(messages)} messages into {len(chunks)} archives.")
    print(f"Original size: {original_size / (1024 * 1024):.2f} MB")
    print(f"Compressed size: {compressed_size / (1024 * 1024):.2f} MB")
    print(f"Compression ratio: {ratio:.2f}%")
    return 0


def cmd_list() -> int:
    chunk_ids = list_archives()
    if not chunk_ids:
        print("No archives found.")
        return 0

    for chunk_id in chunk_ids:
        path = archive_file_path(chunk_id)
        print(f"{chunk_id} ({path.stat().st_size} bytes)")
    return 0


def cmd_view(chunk_id: str, password: str | None = None) -> int:
    key = derive_key(_resolve_password(password))

    encrypted_blob = read_archive(chunk_id)
    decrypted_blob = decrypt_data(encrypted_blob, key)
    chunk = decompress_chunk(decrypted_blob)

    messages = chunk.get("messages", [])
    print(format_messages(messages))
    return 0


def cmd_stats() -> int:
    archives_size = archive_total_size(_archives_dir())

    # Best effort: infer original size from latest input file if it exists.
    latest_original_size = 0
    for path in sorted(Path("data/raw").glob("*")):
        if path.is_file():
            latest_original_size += path.stat().st_size

    if latest_original_size == 0:
        print("Original size: unknown (place source exports under data/raw for tracked stats)")
    else:
        print(f"Original size: {latest_original_size / (1024 * 1024):.2f} MB")

    print(f"Compressed size: {archives_size / (1024 * 1024):.2f} MB")
    if latest_original_size > 0:
        print(f"Compression ratio: {_ratio_percent(latest_original_size, archives_size):.2f}%")
    else:
        print("Compression ratio: unknown")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Signal chat compression prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compress_parser = subparsers.add_parser("compress", help="Compress and archive Signal export")
    compress_parser.add_argument("input_file", help="Path to export file (.json or .txt)")
    compress_parser.add_argument("--password", help="Archive password (optional; prompts if omitted)")

    subparsers.add_parser("list", help="List available archive chunks")

    view_parser = subparsers.add_parser("view", help="Decrypt and view a chunk")
    view_parser.add_argument("chunk_id", help="Chunk ID (for example: 2024-01)")
    view_parser.add_argument("--password", help="Archive password (optional; prompts if omitted)")

    subparsers.add_parser("stats", help="Show storage/compression stats")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "compress":
            return cmd_compress(args.input_file, args.password)
        if args.command == "list":
            return cmd_list()
        if args.command == "view":
            return cmd_view(args.chunk_id, args.password)
        if args.command == "stats":
            return cmd_stats()
        parser.print_help()
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
