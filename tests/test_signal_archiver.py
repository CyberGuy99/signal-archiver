from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from archive_manager import archive_file_path, list_archives, read_archive, write_archive
from chunker import chunk_messages
from compressor import compress_chunk, decompress_chunk
from encryptor import decrypt_data, derive_key, encrypt_data
from main import main as cli_main
from parser import parse_signal_export


class SignalArchiverTests(unittest.TestCase):
    def test_parser_json_and_txt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            json_path = tmp_path / "sample.json"
            json_payload = {
                "messages": [
                    {"timestamp": 1700000000, "sender": "Alice", "text": "Hello"},
                    {"timestamp": 1700000100, "sender": "Bob", "text": "Hi"},
                ]
            }
            json_path.write_text(json.dumps(json_payload), encoding="utf-8")

            txt_path = tmp_path / "sample.txt"
            txt_path.write_text("Raw conversation line", encoding="utf-8")

            parsed_json = parse_signal_export(json_path)
            parsed_txt = parse_signal_export(txt_path)

            self.assertEqual(len(parsed_json), 2)
            self.assertEqual(parsed_json[0]["sender"], "Alice")
            self.assertEqual(len(parsed_txt), 1)
            self.assertEqual(parsed_txt[0]["sender"], "RawExport")

    def test_chunk_compress_encrypt_roundtrip(self) -> None:
        messages = [
            {"timestamp": 1704067200, "sender": "Alice", "text": "A"},
            {"timestamp": 1704153600, "sender": "Bob", "text": "B"},
        ]
        chunks = chunk_messages(messages)
        self.assertEqual(len(chunks), 1)

        compressed = compress_chunk(chunks[0])
        key = derive_key("secret")
        encrypted = encrypt_data(compressed, key)
        decrypted = decrypt_data(encrypted, key)
        restored = decompress_chunk(decrypted)

        self.assertEqual(restored["chunk_id"], chunks[0]["chunk_id"])
        self.assertEqual(len(restored["messages"]), 2)

    def test_wrong_password_fails_decryption(self) -> None:
        blob = b"important-message"
        good_key = derive_key("good-pass")
        bad_key = derive_key("bad-pass")
        encrypted = encrypt_data(blob, good_key)

        with self.assertRaises(Exception):
            decrypt_data(encrypted, bad_key)

    def test_archive_read_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "archives"
            payload = b"abc123"
            path = write_archive("2024-01", payload, data_dir)

            self.assertTrue(path.exists())
            self.assertEqual(list_archives(data_dir), ["2024-01"])
            self.assertEqual(read_archive("2024-01", data_dir), payload)
            self.assertTrue(archive_file_path("2024-01", data_dir).exists())

    def test_cli_end_to_end_and_temp_stays_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            old_cwd = Path.cwd()
            os.chdir(project_root)

            try:
                (project_root / "data" / "raw").mkdir(parents=True, exist_ok=True)
                (project_root / "data" / "archives").mkdir(parents=True, exist_ok=True)
                (project_root / "data" / "temp").mkdir(parents=True, exist_ok=True)

                export_path = project_root / "data" / "raw" / "input.json"
                export_payload = {
                    "messages": [
                        {"timestamp": 1704412800, "sender": "Alice", "text": "Hello"},
                        {"timestamp": 1704499200, "sender": "Bob", "text": "Hi"},
                        {"timestamp": 1707177600, "sender": "Alice", "text": "How are you?"},
                    ]
                }
                export_path.write_text(json.dumps(export_payload), encoding="utf-8")

                self.assertEqual(cli_main(["compress", str(export_path), "--password", "pw"]), 0)
                self.assertEqual(cli_main(["list"]), 0)
                self.assertEqual(cli_main(["view", "2024-01", "--password", "pw"]), 0)
                self.assertEqual(cli_main(["stats"]), 0)

                temp_contents = list((project_root / "data" / "temp").iterdir())
                self.assertEqual(temp_contents, [])
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
