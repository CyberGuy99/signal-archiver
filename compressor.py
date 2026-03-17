from __future__ import annotations

import gzip
import json
from typing import Any

try:
    import zstandard as zstd
except ImportError:  # pragma: no cover - exercised only when zstandard is unavailable
    zstd = None


ZSTD_MAGIC = b"ZST1"
GZIP_MAGIC = b"GZP1"


def compress_chunk(chunk: dict[str, Any]) -> bytes:
    """Serialize a chunk to JSON and compress it with zstd or gzip fallback."""
    payload = json.dumps(chunk, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    if zstd is not None:
        compressor = zstd.ZstdCompressor(level=10)
        return ZSTD_MAGIC + compressor.compress(payload)

    return GZIP_MAGIC + gzip.compress(payload, compresslevel=9)


def decompress_chunk(blob: bytes) -> dict[str, Any]:
    """Decompress bytes produced by compress_chunk back into a chunk dict."""
    if blob.startswith(ZSTD_MAGIC):
        if zstd is None:
            raise RuntimeError("zstandard support is required to read this archive")
        decompressor = zstd.ZstdDecompressor()
        payload = decompressor.decompress(blob[len(ZSTD_MAGIC) :])
    elif blob.startswith(GZIP_MAGIC):
        payload = gzip.decompress(blob[len(GZIP_MAGIC) :])
    else:
        raise ValueError("Unknown compression format header")

    return json.loads(payload.decode("utf-8"))
