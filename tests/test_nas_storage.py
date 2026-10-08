"""Focused NAS storage smoke tests; standard library only, no network or NAS mount.

Run: python3 -m unittest discover -s tests -v
These fixtures contain a minimal synthetic VRM metadata block and real, tiny
lossless WebP images. They do not test 3D rendering or humanoid recognition.
"""
import base64
import contextlib
import hashlib
import io
import json
import os
import shutil
import struct
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import archive_vrm


TPOSE = base64.b64decode(
    "UklGRkQAAABXRUJQVlA4TDgAAAAv/8L/AAfQ5iJXuv8BgUCyP/kGRfQ/4z//+c9//vOf//znP//5z3/+85///Oc///nPf/7zn//83w=="
)
FACE = base64.b64decode(
    "UklGRi4AAABXRUJQVlA4TCIAAAAv/8F/AAfQ5iJXuv8BgUCyv/cMRfQ/4z//+c9//vOf//wf"
)


def sample_vrm():
    gltf = {
        "asset": {"version": "2.0"},
        "extensionsUsed": ["VRMC_vrm"],
        "extensions": {"VRMC_vrm": {"specVersion": "1.0", "meta": {}}},
    }
    content = json.dumps(gltf).encode("utf-8")
    content += b" " * (-len(content) % 4)
    return struct.pack("<4sIIII", b"glTF", 2, 20 + len(content),
                       len(content), 0x4E4F534A) + content


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix="vrm-catalog-test-")
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)
        self.repo = self.root / "repo"
        (self.repo / "data" / "collections").mkdir(parents=True)
        models = [{
            "id": name, "name": name, "publisher": "test publisher",
            "source_url": "https://example.org/creator",
            "license_url": "https://example.org/license",
        } for name in ("test-human-a", "test-human-b", "test-nonhuman")]
        (self.repo / "data" / "models.json").write_text(
            json.dumps({"models": models}), encoding="utf-8",
        )
        (self.repo / "data" / "download-scope.json").write_text(
            json.dumps({"non_humanoid": ["test-nonhuman"]}), encoding="utf-8",
        )
        self.saved_repo = archive_vrm.REPO
        archive_vrm.REPO = self.repo
        self.addCleanup(setattr, archive_vrm, "REPO", self.saved_repo)
        self.vrm = self.root / "source.vrm"
        self.vrm.write_bytes(sample_vrm())
        self.previews = self.root / "previews"
        self.previews.mkdir()
        self.nas = self.root / "fake-nas"

    def args(self, model_id, fmt="zip", confirmed=True):
        checksum = hashlib.sha256(self.vrm.read_bytes()).hexdigest()
        image_metadata = []
        for kind, payload, width, height in (
            ("tpose", TPOSE, 768, 1024), ("face", FACE, 512, 512)
        ):
            filename = f"{model_id}-{kind}.webp"
            (self.previews / filename).write_bytes(payload)
            image_metadata.append({
                "view": kind, "filename": filename, "width": width, "height": height,
                "sha256": hashlib.sha256(payload).hexdigest(),
            })
        (self.previews / f"{model_id}-previews.json").write_text(
            json.dumps({"catalog_id": model_id, "vrm_sha256": checksum,
                        "previews": image_metadata}), encoding="utf-8",
        )
        return Namespace(
            id=model_id, vrm=self.vrm, previews=self.previews,
            nas_root=self.nas, format=fmt, archive_member=None,
            retrieved_at=None, confirm_humanoid=confirmed,
        )

    def archive(self, args):
        with contextlib.redirect_stdout(io.StringIO()):
            archive_vrm.archive(args)

    def entries(self):
        return [
            json.loads(row) for row in (self.nas / "index.jsonl")
            .read_text(encoding="utf-8").splitlines()
        ]

    def test_webp_images_are_real_and_dimensions_match(self):
        p = self.previews / "pic.webp"
        for payload, expected in ((TPOSE, (768, 1024)), (FACE, (512, 512))):
            p.write_bytes(payload)
            self.assertEqual(archive_vrm.check_webp(p), expected)
        p.write_bytes(b"RIFF" + b"\0" * 26)
        with self.assertRaises(ValueError):
            archive_vrm.check_webp(p)

    def test_zip_roundtrip_and_byte_identical_deduplication(self):
        self.archive(self.args("test-human-a"))
        self.archive(self.args("test-human-b"))
        records = self.entries()
        self.assertEqual([r["catalog_id"] for r in records],
                         ["test-human-a", "test-human-b"])
        first, second = (self.nas / r["stored_path"] for r in records)
        self.assertEqual(os.stat(first).st_ino, os.stat(second).st_ino)
        self.assertEqual(os.stat(first).st_dev, os.stat(second).st_dev)
        with zipfile.ZipFile(first) as z:
            self.assertEqual(z.namelist(), ["model.vrm"])
            self.assertEqual(z.read("model.vrm"), self.vrm.read_bytes())
        self.assertEqual(records[0]["vrm_sha256"],
                         hashlib.sha256(self.vrm.read_bytes()).hexdigest())
        self.assertEqual(records[0]["previews"]["tpose"]["path"],
                         "previews/test-human-a-tpose.webp")
        self.assertIsNone(records[0]["retrieved_at"])
        self.assertIsNotNone(records[0]["archived_at"])
        with self.assertRaisesRegex(ValueError, "already archived"):
            self.archive(self.args("test-human-a"))

    def test_rejects_wrong_image_and_nonhumanoid_without_writing_index(self):
        args = self.args("test-human-a")
        image = self.previews / "test-human-a-face.webp"
        image.write_bytes(TPOSE)  # Valid WebP, wrong dimensions and SHA-256.
        with self.assertRaises(ValueError):
            self.archive(args)
        with self.assertRaisesRegex(ValueError, "non-humanoid"):
            self.archive(self.args("test-nonhuman"))
        with self.assertRaisesRegex(ValueError, "confirmation"):
            self.archive(self.args("test-human-b", confirmed=False))
        self.assertFalse((self.nas / "index.jsonl").exists())

    @unittest.skipUnless(shutil.which("zstd"), "zstd CLI not available")
    def test_zstd_roundtrip(self):
        self.archive(self.args("test-human-a", fmt="zstd"))
        row = self.entries()[0]
        packed = self.nas / row["stored_path"]
        self.assertTrue(str(packed).endswith(".vrm.zst"))
        self.assertEqual(
            archive_vrm.decompressed_digest(packed, "zstd", "test-human-a"),
            hashlib.sha256(self.vrm.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
