from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from archive_manager import read_archive
from compressor import decompress_chunk
from encryptor import decrypt_data, derive_key
from main import main as cli_main
from viewer import format_messages


def _build_demo_export(path: Path, count: int = 2000) -> None:
    """Create a synthetic Signal-like export with repetitive text for visible compression."""
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    messages = []
    for i in range(count):
        ts = int((start + timedelta(hours=i * 6)).timestamp())
        sender = "Alice" if i % 2 == 0 else "Bob"
        # Intentionally repetitive body to demonstrate compression savings.
        text = f"Demo message block {(i % 20)}: " + ("hello " * 30)
        messages.append({"timestamp": ts, "sender": sender, "text": text.strip()})

    payload = {"messages": messages}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def run_demo(password: str) -> int:
    demo_export = Path("data/raw/demo_signal.json")
    _build_demo_export(demo_export)

    print("=== Demo: Compress ===")
    code = cli_main(["compress", str(demo_export), "--password", password])
    if code != 0:
        return code

    print("\n=== Demo: List Archives ===")
    code = cli_main(["list"])
    if code != 0:
        return code

    print("\n=== Demo: View First Chunk Preview (2024-01) ===")
    key = derive_key(password)
    encrypted_blob = read_archive("2024-01")
    decrypted_blob = decrypt_data(encrypted_blob, key)
    chunk = decompress_chunk(decrypted_blob)
    preview_messages = chunk.get("messages", [])[:8]
    print(format_messages(preview_messages))
    print("... (truncated preview)")

    print("\n=== Demo: Stats ===")
    return cli_main(["stats"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local end-to-end demo for signal-archiver")
    parser.add_argument("--password", default="demo-pass", help="Password used for archive encryption")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return run_demo(args.password)


if __name__ == "__main__":
    raise SystemExit(main())
