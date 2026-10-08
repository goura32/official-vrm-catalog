#!/usr/bin/env python3
"""Compare ZIP (Deflate) and zstd on actual local VRM files; verify lossless round trips.

No network access, downloading or NAS writes. Use several representative VRMs.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def measure_vrm(source, temporary, zstd_binary):
    expected_hash = sha256(source)
    original_size = source.stat().st_size
    row = {"source": str(source), "vrm_size_bytes": original_size, "vrm_sha256": expected_hash}
    zipped = temporary / "sample.zip"
    started = time.perf_counter()
    with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(source, arcname=source.name)
    zip_seconds = time.perf_counter() - started
    with zipfile.ZipFile(zipped) as archive:
        names = archive.namelist()
        if names != [source.name]:
            raise ValueError("ZIP member mismatch")
        restored = temporary / "restored-zip.vrm"
        with archive.open(names[0]) as input_stream, restored.open("wb") as output:
            shutil.copyfileobj(input_stream, output, 1024 * 1024)
    if sha256(restored) != expected_hash:
        raise ValueError("ZIP roundtrip SHA-256 mismatch")
    row["zip"] = {"bytes": zipped.stat().st_size, "seconds": round(zip_seconds, 4), "verified": True}
    if zstd_binary:
        compressed = temporary / "sample.vrm.zst"
        started = time.perf_counter()
        subprocess.run([zstd_binary, "-10", "-T0", "-q", "-f", str(source), "-o", str(compressed)], check=True)
        zstd_seconds = time.perf_counter() - started
        restored = temporary / "restored-zstd.vrm"
        subprocess.run([zstd_binary, "-d", "-q", "-f", str(compressed), "-o", str(restored)], check=True)
        if sha256(restored) != expected_hash:
            raise ValueError("zstd roundtrip SHA-256 mismatch")
        row["zstd"] = {"bytes": compressed.stat().st_size, "seconds": round(zstd_seconds, 4), "verified": True}
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Downloaded, legally obtainable .vrm samples")
    parser.add_argument("--zip-gap-percent", type=float, default=3.0,
                        help="Choose ZIP if its extra bytes are at most this fraction of original bytes")
    args = parser.parse_args()
    if not 0 <= args.zip_gap_percent <= 100:
        parser.error("--zip-gap-percent must be between 0 and 100")
    zstd_binary = shutil.which("zstd")
    rows = []
    for source in args.files:
        if not source.is_file() or source.suffix.lower() != ".vrm":
            parser.error(f"Expected an existing .vrm file: {source}")
        with tempfile.TemporaryDirectory(prefix="vrm-benchmark-") as temp:
            rows.append(measure_vrm(source.resolve(), Path(temp), zstd_binary))
    total_raw = sum(row["vrm_size_bytes"] for row in rows)
    total_zip = sum(row["zip"]["bytes"] for row in rows)
    total_zstd = sum(row["zstd"]["bytes"] for row in rows) if zstd_binary else None
    if not zstd_binary:
        decision = "zstd_unavailable_not_compared"
    elif len(rows) < 3:
        decision = "insufficient_samples"
    else:
        extra_percent = 100 * (total_zip - total_zstd) / total_raw if total_raw else 0
        decision = "zip" if extra_percent <= args.zip_gap_percent else "zstd"
    print(json.dumps({
        "samples": rows,
        "summary": {
            "count": len(rows), "original_bytes": total_raw,
            "zip_bytes": total_zip, "zstd_bytes": total_zstd,
            "zip_extra_percent_of_original": (
                round(100 * (total_zip - total_zstd) / total_raw, 3)
                if total_zstd is not None and total_raw else None
            ),
            "decision": decision,
            "decision_rule": f"ZIP if its extra size <= {args.zip_gap_percent}% of original over >=3 samples",
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
