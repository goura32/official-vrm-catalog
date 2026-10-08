#!/usr/bin/env python3
"""Validate all catalog JSON files locally, without network or third-party modules."""
import json
from pathlib import Path
from re import fullmatch
from urllib.parse import urlparse

data_dir = Path(__file__).resolve().parents[1] / "data"
paths = [data_dir / "models.json", *sorted((data_dir / "collections").glob("*.json"))]
seen = set()
count = 0
methods = {"direct_vrm", "vroid_hub_vrm", "vroid_studio_export", "official_page_download", "booth_free_download"}

for path in paths:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    assert catalog["schema_version"] == 1, f"{path}: unsupported schema"
    assert isinstance(catalog["models"], list)
    for item in catalog["models"]:
        model_id = item.get("id", "?")
        for field in ("id", "name", "publisher", "source_url", "access_method", "license_name", "license_url", "verification", "checked_at"):
            assert item.get(field), f"{path}: {model_id}: missing {field}"
        assert model_id not in seen, f"duplicate id across catalog: {model_id}"
        seen.add(model_id)
        assert item["access_method"] in methods
        for field in ("source_url", "license_url"):
            assert urlparse(item[field]).scheme == "https", f"{model_id}: invalid {field}"
        if item.get("download_url") is not None:
            assert urlparse(item["download_url"]).scheme == "https"
            parsed_download = urlparse(item["download_url"])
            # Creator-indexed Arweave VRM objects have immutable extensionless paths.
            arweave_vrm = (parsed_download.netloc == "arweave.net"
                           and fullmatch(r"/[A-Za-z0-9_-]{43}", parsed_download.path))
            assert parsed_download.path.lower().endswith(".vrm") or arweave_vrm
        assert item["vrm_version"] in ("0.x", "1.0", None)
        if "distribution_size_bytes" in item:
            assert type(item["distribution_size_bytes"]) is int and item["distribution_size_bytes"] > 0
        if "binary_evidence" in item:
            evidence = item["binary_evidence"]
            assert item["verification"] == "official_binary_metadata_confirmed"
            assert evidence["glb_version"] == 2
            assert evidence["vrm_spec_version"] == item["vrm_version"]
            assert len(evidence["github_blob_sha"]) == 40
        if "distribution_filename" in item:
            assert isinstance(item["distribution_filename"], str)
            assert "/" not in item["distribution_filename"]
            assert item["distribution_filename"].lower().endswith((".vrm", ".zip"))
        assert item["kind"] in ("avatar", "feature-test")
        assert isinstance(item["features"], list)
        count += 1

# Scope is separate from source catalogs, with default-deny for unlisted IDs.
scope = json.loads((data_dir / "download-scope.json").read_text(encoding="utf-8"))
assert scope["schema_version"] == 1 and scope["policy"] == "default_deny"
humanoid = scope["humanoid_candidates"]
non_humanoid = scope["non_humanoid"]
assert isinstance(humanoid, list) and isinstance(non_humanoid, list)
assert all(isinstance(i, str) and i for i in [*humanoid, *non_humanoid])
assert len(humanoid) == len(set(humanoid)), "duplicate humanoid ID"
assert len(non_humanoid) == len(set(non_humanoid)), "duplicate nonhumanoid ID"
assert not (set(humanoid) & set(non_humanoid)), "overlapping scope IDs"
assert set(humanoid).issubset(seen), "unknown humanoid ID"
assert set(non_humanoid).issubset(seen), "unknown nonhumanoid ID"
pending = count - len(humanoid) - len(non_humanoid)
print(f"OK: {count} models, {len(seen)} unique IDs, {len(paths)} catalog files; scope: {len(humanoid)} humanoid candidates, {len(non_humanoid)} nonhumanoid, {pending} pending")
