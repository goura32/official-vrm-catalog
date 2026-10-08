#!/usr/bin/env python3
"""Read-only integrity audit of an existing VRM NAS index and its artifacts.

Runs entirely offline. Does not modify or delete any files.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from archive_vrm import check_webp, decompressed_digest, digest


def resolve_inside(root, path_text):
    if not isinstance(path_text, str) or not path_text:
        raise ValueError("Missing artifact relative path")
    candidate = (root / path_text).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Artifact path escapes NAS root")
    if not candidate.is_file():
        raise ValueError("Artifact file is missing")
    return candidate


def verify(root):
    root = root.resolve()
    index = root / "index.jsonl"
    if not index.is_file():
        raise FileNotFoundError(f"NAS index missing: {index}")
    errors, seen, counts, formats = [], set(), {"entries": 0, "previews": 0, "bytes": 0}, set()
    for lineno, line in enumerate(index.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        model_id = None
        try:
            record = json.loads(line)
            model_id = record["catalog_id"]
            if not isinstance(model_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", model_id):
                raise ValueError("Invalid catalog ID")
            if model_id in seen:
                raise ValueError("Duplicate catalog ID")
            seen.add(model_id)
            counts["entries"] += 1
            fmt = record["compression"]
            if fmt not in ("zip", "zstd"):
                raise ValueError("Unknown compression method")
            formats.add(fmt)
            expected_path = f"models/{model_id}" + (".zip" if fmt == "zip" else ".vrm.zst")
            if record["stored_path"] != expected_path:
                raise ValueError("Stored filename does not match catalog ID")
            path = resolve_inside(root, record["stored_path"])
            counts["bytes"] += path.stat().st_size
            if path.stat().st_size != record["stored_size_bytes"]:
                raise ValueError("Compressed file size mismatch")
            if digest(path) != record["archive_sha256"]:
                raise ValueError("Compressed archive SHA-256 mismatch")
            if decompressed_digest(path, fmt, model_id) != record["vrm_sha256"]:
                raise ValueError("Decompressed VRM SHA-256 mismatch")
            previews = record["previews"]
            for kind, expected_dimensions in (("tpose", (768, 1024)), ("face", (512, 512))):
                item = previews[kind]
                expected_preview_path = f"previews/{model_id}-{kind}.webp"
                if item["path"] != expected_preview_path:
                    raise ValueError(f"{kind} preview filename mismatch")
                preview = resolve_inside(root, item["path"])
                if check_webp(preview) != expected_dimensions:
                    raise ValueError(f"{kind} WebP dimensions mismatch")
                if digest(preview) != item["sha256"]:
                    raise ValueError(f"{kind} WebP SHA-256 mismatch")
                counts["previews"] += 1
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            errors.append({"line": lineno, "catalog_id": model_id, "error": str(exc)})
    if len(formats) > 1:
        errors.append({"error": "Mixed ZIP and zstd archive formats"})
    return {"root": str(root), "counts": counts, "formats": sorted(formats),
            "errors": errors, "ok": not errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nas-root", type=Path, default=Path("/mnt/hdd/vrm"))
    args = parser.parse_args()
    try:
        result = verify(args.nas_root)
    except (OSError, ValueError) as exc:
        result = {"root": str(args.nas_root), "ok": False, "errors": [{"error": str(exc)}]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
