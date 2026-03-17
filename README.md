# signal-archiver

Local prototype for archiving Signal chat exports with monthly chunking, compression, and password-based encryption.

## What It Does

- Parses Signal export files (`.json` or `.txt`) into a normalized message format.
- Groups messages into month-based chunks (`YYYY-MM`).
- Compresses each chunk (zstd, with gzip fallback).
- Encrypts compressed data using AES-GCM with a key derived from a password.
- Stores encrypted archives on disk and supports listing, viewing, and stats.

## Project Layout

```
signal-archiver/
├── main.py
├── parser.py
├── chunker.py
├── compressor.py
├── encryptor.py
├── archive_manager.py
├── viewer.py
├── demo_run.py
├── requirements.txt
├── data/
│   ├── raw/
│   ├── archives/
│   └── temp/
└── tests/
```

## Requirements

- Python 3.11+

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## CLI Usage

Run commands from the `signal-archiver` directory:

```bash
python main.py compress data/raw/sample_signal.json --password "your-password"
python main.py list
python main.py view 2024-01 --password "your-password"
python main.py stats
```

If `--password` is omitted for `compress` or `view`, the CLI prompts securely.

## Archive Format

Each archive file (`data/archives/chat_<chunk_id>.arc`) stores:

1. Magic header: `SIGARCH1\n`
2. Chunk ID line: `<chunk_id>\n`
3. Encrypted payload bytes (`nonce + ciphertext + tag`)

## Security Notes

- All archive data on disk remains encrypted.
- Plaintext chunk data is processed in memory.
- This is a prototype and not a production-hardened backup system.

## Demo

```bash
python demo_run.py --password demo-pass
```

The demo creates sample raw data, archives it, lists chunks, views one chunk, and prints stats.

## Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
