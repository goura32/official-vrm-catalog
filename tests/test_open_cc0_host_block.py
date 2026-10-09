"""A host that returned HTTP 429 remains blocked after worker restart."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

STATE = Path(__file__).resolve().parents[2]
RUNNER_PATH = STATE / "run_open_cc0_batch.py"
RUNNER_AVAILABLE = RUNNER_PATH.is_file()
worker: Any
if RUNNER_AVAILABLE:
    SPEC = importlib.util.spec_from_file_location("cc0_batch_under_test", RUNNER_PATH)
    if SPEC is None or SPEC.loader is None:
        raise RuntimeError(f"cannot load batch runner from {RUNNER_PATH}")
    worker = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(worker)
else:
    worker = None


@unittest.skipUnless(RUNNER_AVAILABLE, "local batch runner is stored outside the catalog repository")
class Host429BlockTests(unittest.TestCase):
    def test_persisted_429_blocks_all_later_requests_to_that_host(self):
        with tempfile.TemporaryDirectory(prefix="vrm-host429-test-") as tmp:
            root = Path(tmp)
            journal = root / "checkpoint.jsonl"
            journal.write_text(json.dumps({
                "at": "2026-10-09T02:28:25.603909+00:00",
                "catalog_id": "polygonalmind-halloween-rising-007",
                "status": "http_429_rate_limited",
                "source_host": "dweb.link",
                "source_url": "https://dweb.link/ipfs/example/model.vrm",
                "retry_after_until": "2026-10-09T02:43:25.603909+00:00",
            }) + "\n", encoding="utf-8")
            sources = root / "sources"
            sources.mkdir()
            opener = type("NoNetwork", (), {
                "open": lambda *_args, **_kwargs: self.fail("blocked host made a request"),
            })()
            model = {
                "id": "polygonalmind-halloween-rising-008",
                "download_url": "https://dweb.link/ipfs/example/next.vrm",
                "license_name": "CC0 1.0",
            }
            with patch.object(worker, "JOURNAL", journal), \
                 patch.object(worker, "SOURCES", sources), \
                 patch.object(worker, "OPENER", opener):
                blocked = worker.load_hosts_blocked_after_429()
                self.assertIn("dweb.link", blocked)
                self.assertEqual(worker.MAX_HTTP_429_REQUESTS, 1)
                with patch.object(worker, "HOST_BLOCKED_AFTER_429", blocked):
                    _size, _digest, _origin, failure = worker.download(
                        model, "polygonalmind-halloween-rising.json", 0,
                    )
            self.assertTrue(failure["host_permanently_blocked"])
            self.assertFalse((sources / "polygonalmind-halloween-rising-008.vrm.part").exists())


if __name__ == "__main__":
    unittest.main()
