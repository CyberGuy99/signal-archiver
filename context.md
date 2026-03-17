# Project Context

## Purpose
Prototype local Signal chat archiving with chunking, compression, encryption, and viewing.

## Implemented Modules
- parser.py: Parse Signal JSON/TXT export into normalized message schema.
- chunker.py: Group normalized messages into YYYY-MM chunk IDs.
- compressor.py: JSON serialization + zstd compression (gzip fallback).
- encryptor.py: Password-derived key (SHA256) + AES-GCM encrypt/decrypt.
- archive_manager.py: Archive file read/write and index/stats helpers.
- viewer.py: Render decrypted messages as readable lines.
- main.py: CLI (`compress`, `list`, `view`, `stats`).

## Data Layout
- data/raw: Optional source exports for size tracking.
- data/archives: Encrypted archive files (`chat_<chunk_id>.arc`).
- data/temp: Reserved temporary path (currently unused).

## Archive Format
- Binary file:
  1. Magic header: `SIGARCH1\n`
  2. Chunk ID line: `<chunk_id>\n`
  3. Encrypted blob bytes (`nonce + ciphertext + tag`)

## Operational Notes
- Plaintext chunks are only handled in memory and never written to disk.
- `stats` uses files in `data/raw` to estimate original size; otherwise shows unknown original size.
- `data/archives/index.json` stores run metadata (input size, chunk IDs, timestamp).
- CLI supports optional `--password` for `compress` and `view` to support non-interactive usage; if omitted, it prompts securely.

## Local Environment
- Virtual environment path: `.venv`
- Dependencies installed from `requirements.txt`.

## Next Session Checklist
- Activate virtual environment.
- Install/update dependencies from requirements.txt.
- Run a real export through `compress`, then verify `view` and `stats`.
- Optionally add tests for parser/chunker and wrong-password handling.
- Use `docs/v2_ios_github_issues.md` to create milestone issues in GitHub.
- Use `docs/v2_ios_handoff_demo.md` for Xcode-owner demo execution.

## Validation Snapshot (2026-03-17)
- Smoke test completed using `data/raw/sample_signal.json`.
- Verified commands: `compress`, `list`, `view`, `stats`.
- Tiny samples may show negative compression ratio because encryption/header overhead can exceed compressed payload size.

## Testing
- Test suite path: `tests/test_signal_archiver.py`
- Run tests: `./.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`
- Coverage includes parser formats, chunk/compress/encrypt roundtrip, wrong-password failure, archive read/write, and CLI integration.

## Demo
- Demo script: `demo_run.py`
- Run demo: `./.venv/bin/python demo_run.py --password demo-pass`
- Demo generates `data/raw/demo_signal.json`, compresses it, lists archives, shows first chunk, and prints stats.

## V2 iOS Planning Outputs (Branch: v2_ios)
- `docs/v2_ios_github_issues.md`: milestone-organized issue set with acceptance criteria, dependencies, and labels.
- `docs/v2_ios_handoff_demo.md`: end-to-end handoff and demonstration runbook for iOS/Xcode execution.
