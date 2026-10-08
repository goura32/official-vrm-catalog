#!/usr/bin/env python3
"""Validate all catalog JSON files locally, without network or third-party modules."""
import json
from pathlib import Path
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
            assert urlparse(item["download_url"]).path.lower().endswith(".vrm")
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

print(f"OK: {count} models, {len(seen)} unique IDs, {len(paths)} catalog files")
