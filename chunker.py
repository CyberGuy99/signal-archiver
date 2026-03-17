from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def chunk_messages(messages: list[dict[str, Any]], chunk_days: int = 30) -> list[dict[str, Any]]:
    """Group messages into month-like 30-day chunks using YYYY-MM ids."""
    _ = chunk_days  # Reserved for future adjustable window support.

    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for message in messages:
        timestamp = int(message.get("timestamp", 0))
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        chunk_id = dt.strftime("%Y-%m")
        buckets[chunk_id].append(message)

    chunks: list[dict[str, Any]] = []
    for chunk_id in sorted(buckets.keys()):
        sorted_messages = sorted(buckets[chunk_id], key=lambda m: int(m.get("timestamp", 0)))
        chunks.append({"chunk_id": chunk_id, "messages": sorted_messages})
    return chunks
