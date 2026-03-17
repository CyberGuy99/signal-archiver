from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


NormalizedMessage = dict[str, Any]


def _normalize_message(message: dict[str, Any]) -> NormalizedMessage:
    """Normalize a single message into the common internal format."""
    timestamp = int(message.get("timestamp", int(time.time())))
    sender = str(message.get("sender", "Unknown"))
    text = str(message.get("text", ""))
    return {"timestamp": timestamp, "sender": sender, "text": text}


def parse_signal_export(input_path: str | Path) -> list[NormalizedMessage]:
    """Parse a Signal export in JSON or TXT format.

    JSON format is expected to contain a top-level "messages" list.
    TXT format is treated as one raw message block.
    """
    path = Path(input_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        raw_messages: list[dict[str, Any]]
        if isinstance(payload, dict) and isinstance(payload.get("messages"), list):
            raw_messages = [m for m in payload["messages"] if isinstance(m, dict)]
        elif isinstance(payload, list):
            raw_messages = [m for m in payload if isinstance(m, dict)]
        else:
            raise ValueError("JSON input must be an object with a 'messages' list or a list of messages")

        return [_normalize_message(message) for message in raw_messages]

    if suffix == ".txt":
        with path.open("r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            return []
        return [
            {
                "timestamp": int(time.time()),
                "sender": "RawExport",
                "text": text,
            }
        ]

    raise ValueError("Unsupported input format. Use .json or .txt")
