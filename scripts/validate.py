#!/usr/bin/env python3
"""Check the catalog's basic structure. No network access required."""
import json
from pathlib import Path
from urllib.parse import urlparse

catalog = json.loads((Path(__file__).resolve().parents[1] / "data" / "models.json").read_text(encoding="utf-8"))
assert catalog["schema_version"] == 1
items = catalog["models"]
ids = set()
methods = {"direct_vrm", "vroid_hub_vrm", "vroid_studio_export", "official_page_download", "booth_free_download"}
for item in items:
    for field in ("id", "name", "publisher", "source_url", "access_method", "license_name", "license_url", "verification", "checked_at"):
        assert item.get(field), f"{item.get('id', '?')}: missing {field}"
    assert item["id"] not in ids, f"duplicate id: {item['id']}"
    ids.add(item["id"])
    assert item["access_method"] in methods
    for field in ("source_url", "license_url"):
        assert urlparse(item[field]).scheme == "https", f"{item['id']}: invalid {field}"
    if item["download_url"] is not None:
        assert urlparse(item["download_url"]).scheme == "https"
        assert item["download_url"].endswith(".vrm")
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
print(f"OK: {len(items)} models, {len(ids)} unique IDs")
