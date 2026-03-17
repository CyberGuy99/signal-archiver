from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def format_messages(messages: list[dict[str, Any]]) -> str:
    """Render normalized messages into a readable line format."""
    lines: list[str] = []
    for message in messages:
        timestamp = int(message.get("timestamp", 0))
        sender = str(message.get("sender", "Unknown"))
        text = str(message.get("text", ""))

        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        date_label = dt.strftime("%Y-%m-%d")
        lines.append(f"[{date_label}] {sender}: {text}")
    return "\n".join(lines)
