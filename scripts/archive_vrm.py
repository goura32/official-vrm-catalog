#!/usr/bin/env python3
"""Archive one verified humanoid VRM and matching previews under a catalog ID.

No network access. Does not download models, classify shapes or override existing IDs.
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from inspect_vrm import inspect_file

REPO = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def catalog_record(model_id):
    paths = [REPO / "data/models.json", *sorted((REPO / "data/collections").glob("*.json"))]
    found = []
    for path in paths:
        for model in json.loads(path.read_text(encoding="utf-8"))["models"]:
            if model["id"] == model_id:
                found.append(model)
    if len(found) != 1:
        raise ValueError(f"Expected one catalog model for {model_id}, found {len(found)}")
    return found[0]


def check_webp(path):
    """Return WebP pixel dimensions using only the standard library.

    Verify RIFF size and the first image frame header. This does not replace
    decoding and rendering validation performed by the preview generator.
    """
    import struct

    with path.open("rb") as stream:
        header = stream.read(64)
    length = path.stat().st_size
    if (len(header) < 30 or header[:4] != b"RIFF" or header[8:12] != b"WEBP"
            or struct.unpack_from("<I", header, 4)[0] + 8 != length):
        raise ValueError(f"Invalid WebP RIFF header: {path}")
    kind = header[12:16]
    chunk_size = struct.unpack_from("<I", header, 16)[0]
    if chunk_size < 10 and kind in (b"VP8 ", b"VP8X"):
        raise ValueError(f"Truncated WebP image header: {path}")
    if kind == b"VP8X":
        width = 1 + int.from_bytes(header[24:27], "little")
        height = 1 + int.from_bytes(header[27:30], "little")
    elif kind == b"VP8 ":
        if header[23:26] != bytes((0x9d, 0x01, 0x2a)):
            raise ValueError(f"Invalid WebP VP8 frame: {path}")
        width = int.from_bytes(header[26:28], "little") & 0x3fff
        height = int.from_bytes(header[28:30], "little") & 0x3fff
    elif kind == b"VP8L":
        if chunk_size < 5 or header[20] != 0x2f:
            raise ValueError(f"Invalid WebP lossless frame: {path}")
        bits = int.from_bytes(header[21:25], "little")
        width = 1 + (bits & 0x3fff)
        height = 1 + ((bits >> 14) & 0x3fff)
    else:
        raise ValueError(f"Unsupported WebP image chunk {kind!r}: {path}")
    if not (0 < width <= 16384 and 0 < height <= 16384):
        raise ValueError(f"Invalid WebP dimensions: {path}")
    return width, height


def compress(vrm, archive_path, fmt, model_id):
    if fmt == "zip":
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.write(vrm, arcname="model.vrm")
    else:
        zstd = shutil.which("zstd")
        if zstd is None:
            raise RuntimeError("zstd executable is required for zstd format")
        subprocess.run([zstd, "-10", "-T0", "-q", "-f", str(vrm), "-o", str(archive_path)], check=True)


def decompressed_digest(archive_path, fmt, model_id):
    hasher = hashlib.sha256()
    if fmt == "zip":
        with zipfile.ZipFile(archive_path) as z:
            if z.namelist() != ["model.vrm"]:
                raise ValueError("Unexpected ZIP members")
            with z.open("model.vrm") as stream:
                for data in iter(lambda: stream.read(1024 * 1024), b""):
                    hasher.update(data)
    else:
        zstd = shutil.which("zstd")
        with subprocess.Popen([zstd, "-d", "-q", "-c", str(archive_path)],
                              stdout=subprocess.PIPE) as p:
            for data in iter(lambda: p.stdout.read(1024 * 1024), b""):
                hasher.update(data)
            if p.wait() != 0:
                raise ValueError("Unable to decompress zstd archive")
    return hasher.hexdigest()


def archive_locked(args):
    if not args.confirm_humanoid:
        raise ValueError("Explicit 3D humanoid confirmation is required")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.id):
        raise ValueError("Unsafe catalog ID")
    source = args.vrm.resolve(strict=True)
    if source.suffix.lower() != ".vrm" or not source.is_file():
        raise ValueError("Input must be a local .vrm")
    model = catalog_record(args.id)
    scope = json.loads((REPO / "data/download-scope.json").read_text(encoding="utf-8"))
    if args.id in scope.get("non_humanoid", []):
        raise ValueError("Catalog scope explicitly excludes this non-humanoid ID")
    checked = inspect_file(source)
    if len(checked) != 1:
        raise ValueError("Expected one valid VRM")
    info = checked[0]
    vrm_hash = info["sha256"]
    base = args.previews.resolve(strict=True)
    manifest_path = base / (args.id + "-previews.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("catalog_id") != args.id or manifest.get("vrm_sha256") != vrm_hash:
        raise ValueError("Preview provenance mismatch: ID or VRM SHA-256")
    manifest_previews = {item["view"]: item for item in manifest["previews"]}
    if set(manifest_previews) != {"tpose", "face"}:
        raise ValueError("Expected exactly two preview records")
    pictures = {kind: base / f"{args.id}-{kind}.webp" for kind in ("tpose", "face")}
    for kind, preview in pictures.items():
        if manifest_previews[kind].get("filename") != preview.name:
            raise ValueError("Preview filename mismatch")
        if tuple((manifest_previews[kind].get("width"), manifest_previews[kind].get("height"))) != (
            (768, 1024) if kind == "tpose" else (512, 512)
        ):
            raise ValueError("Preview dimension metadata mismatch")
        actual_dimensions = check_webp(preview)
        if actual_dimensions != ((768, 1024) if kind == "tpose" else (512, 512)):
            raise ValueError("Actual WebP dimensions do not match preview type: " + kind)
        if not re.fullmatch(r"[0-9a-f]{64}", str(manifest_previews[kind].get("sha256", ""))):
            raise ValueError("Preview SHA-256 missing or invalid")
        if digest(preview) != manifest_previews[kind]["sha256"]:
            raise ValueError("Preview image SHA-256 mismatch: " + kind)
    root = args.nas_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    index_path = root / "index.jsonl"
    entries = []
    if index_path.is_file():
        entries = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(item["catalog_id"] == args.id for item in entries):
        raise ValueError("Catalog ID already archived; investigate before replacing: " + args.id)
    fmt = args.format
    if any(item.get("compression") != fmt for item in entries):
        raise ValueError("NAS archive format differs from existing records; keep one format")
    extension = ".zip" if fmt == "zip" else ".vrm.zst"
    relative_model_path = "models/" + args.id + extension
    relative_previews = {kind: "previews/" + args.id + "-" + kind + ".webp" for kind in pictures}
    outputs = [root / relative_model_path, *(root / p for p in relative_previews.values())]
    for target in outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise FileExistsError(f"Unindexed existing output; refusing to overwrite: {target}")
    created = []
    pending = []
    try:
        # Use temporary files under the NAS mount so renames remain atomic.
        with tempfile.NamedTemporaryFile(dir=root / "models", prefix=".pending-", delete=False) as temp:
            temp_archive = Path(temp.name)
        pending.append(temp_archive)
        # Reuse byte-identical VRM content stored for a different catalog ID.
        # The ZIP member is always 'model.vrm', so a hard-linked archive is valid
        # regardless of the catalog ID used for the enclosing filename.
        reused = False
        for entry in entries:
            if entry.get("vrm_sha256") != vrm_hash or entry.get("compression") != fmt:
                continue
            candidate = (root / entry["stored_path"]).resolve()
            if candidate.parent != (root / "models").resolve() or not candidate.is_file():
                continue
            if decompressed_digest(candidate, fmt, args.id) != vrm_hash:
                continue
            temp_archive.unlink()
            try:
                os.link(candidate, temp_archive)
                reused = True
            except OSError:
                pass
            break
        if not reused:
            compress(source, temp_archive, fmt, args.id)
        if decompressed_digest(temp_archive, fmt, args.id) != vrm_hash:
            raise ValueError("VRM bytes changed during compression")
        archive_hash = digest(temp_archive)
        stored_size = temp_archive.stat().st_size
        os.replace(temp_archive, outputs[0])
        pending.remove(temp_archive)
        created.append(outputs[0])
        for kind in ("tpose", "face"):
            target = root / relative_previews[kind]
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".pending-", delete=False) as temp:
                temp_pic = Path(temp.name)
            pending.append(temp_pic)
            shutil.copyfile(pictures[kind], temp_pic)
            if digest(temp_pic) != digest(pictures[kind]):
                raise ValueError("WebP copy SHA-256 mismatch")
            os.replace(temp_pic, target)
            pending.remove(temp_pic)
            created.append(target)
        entry = {
            "catalog_id": args.id, "name": model["name"], "publisher": model["publisher"],
            "stored_path": relative_model_path, "compression": fmt,
            "vrm_sha256": vrm_hash, "archive_sha256": archive_hash,
            "vrm_size_bytes": source.stat().st_size, "stored_size_bytes": stored_size,
            "vrm_version": info["vrm_version"],
            "source_url": model["source_url"], "license_url": model["license_url"],
            "distribution_filename": model.get("distribution_filename"),
            "archive_member_path": args.archive_member,
            "retrieved_at": args.retrieved_at,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "previews": {
                kind: {"path": relative_previews[kind], "sha256": digest(root / relative_previews[kind])}
                for kind in pictures
            },
            "shape": "humanoid_confirmed_by_operator",
        }
        entries.append(entry)
        entries.sort(key=lambda obj: obj["catalog_id"])
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=root,
                                         prefix=".index-", delete=False) as temp:
            temp_index = Path(temp.name)
            pending.append(temp_index)
            for row in entries:
                temp.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temp_index, index_path)
        pending.remove(temp_index)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    except BaseException:
        for target in created:
            target.unlink(missing_ok=True)
        raise
    finally:
        for target in pending:
            target.unlink(missing_ok=True)

def archive(args):
    # Keep a stable lock inode: flock(index.jsonl) is unsafe when the index
    # is atomically replaced with os.replace by another process.
    root = args.nas_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".index.lock").open("a+b") as lockfile:
        fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX)
        try:
            return archive_locked(args)
        finally:
            fcntl.flock(lockfile.fileno(), fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="Existing catalog ID")
    parser.add_argument("--vrm", required=True, type=Path, help="Validated local humanoid VRM")
    parser.add_argument("--previews", required=True, type=Path, help="Generated WebP directory")
    parser.add_argument("--nas-root", type=Path, default=Path("/mnt/hdd/vrm"))
    parser.add_argument("--format", choices=["zip", "zstd"], default="zip")
    parser.add_argument("--archive-member", help="Original member path within downloaded ZIP")
    parser.add_argument("--retrieved-at", help="Actual original acquisition time, ISO-8601")
    parser.add_argument("--confirm-humanoid", action="store_true", required=True,
                        help="Explicit operator assertion after 3D visual check")
    args = parser.parse_args()
    archive(args)


if __name__ == "__main__":
    main()
