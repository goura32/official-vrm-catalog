#!/usr/bin/env python3
"""Inspect locally obtained VRM files (or VRMs in ZIP files), without dependencies."""
import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path


def inspect(stream, source, size):
    header = stream.read(20)
    if len(header) != 20:
        raise ValueError("incomplete GLB header")
    magic, glb_version, declared_size, json_size, chunk_type = struct.unpack("<4sIIII", header)
    if magic != b"glTF" or glb_version != 2 or chunk_type != 0x4E4F534A:
        raise ValueError("not a GLB 2 file with a JSON chunk")
    if json_size > 32 * 1024 * 1024:
        raise ValueError("GLB JSON chunk is unreasonably large")
    if declared_size != size:
        raise ValueError(f"GLB length {declared_size} differs from file size {size}")
    payload = stream.read(json_size)
    if len(payload) != json_size:
        raise ValueError("truncated GLB JSON chunk")
    gltf = json.loads(payload.decode("utf-8"))
    extensions = gltf.get("extensions", {})
    if "VRMC_vrm" in extensions:
        vrm = extensions["VRMC_vrm"]
        vrm_version = vrm.get("specVersion")
    elif "VRM" in extensions:
        vrm = extensions["VRM"]
        vrm_version = "0.x"
    else:
        raise ValueError("GLB contains no VRM extension")
    digest = hashlib.sha256()
    digest.update(header)
    digest.update(payload)
    length = 20 + len(payload)
    while block := stream.read(1024 * 1024):
        digest.update(block)
        length += len(block)
    if length != size:
        raise ValueError("file length changed during inspection")
    return {
        "source": source,
        "bytes": size,
        "sha256": digest.hexdigest(),
        "glb_version": glb_version,
        "vrm_version": vrm_version,
        "meta": vrm.get("meta", {}),
        "extensions_used": gltf.get("extensionsUsed", []),
    }


def inspect_file(path):
    if path.suffix.lower() == ".vrm":
        with path.open("rb") as stream:
            return [inspect(stream, str(path), path.stat().st_size)]
    if path.suffix.lower() == ".zip":
        results = []
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir() or not member.filename.lower().endswith(".vrm"):
                    continue
                with archive.open(member) as stream:
                    results.append(inspect(stream, f"{path}:{member.filename}", member.file_size))
        if not results:
            raise ValueError("ZIP contains no .vrm files")
        return results
    raise ValueError("expected a .vrm or .zip file")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    results = []
    failed = False
    for path in args.files:
        try:
            results.extend(inspect_file(path))
        except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
            results.append({"source": str(path), "error": str(exc)})
            failed = True
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
