#!/usr/bin/env python3
"""Check the catalog's basic structure. No network access required."""
import json
from pathlib import Path
from urllib.parse import urlparse

catalog = json.loads((Path(__file__).resolve().parents[1] / "data" / "models.json").read_text(encoding="utf-8"))
assert catalog["schema_version"] == 1
items = catalog["models"]
ids = set()
methods = {"direct_vrm", "vroid_hub_vrm", "vroid_studio_export"}
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
print(f"OK: {len(items)} models, {len(ids)} unique IDs")
