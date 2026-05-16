#!/usr/bin/env python3
"""One-shot live probe smoke test for WUP (no file watcher)."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from wup.config import load_config
from wup.monitoring_manifest import build_monitoring_manifest, load_monitoring_manifest_from_yaml
from wup.testql_watcher import TestQLWatcher


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cfg = load_config(root)
    manifest = build_monitoring_manifest(root, cfg)

    print("=== Probe plan (from current config) ===")
    for svc, info in sorted((manifest.get("wup_services") or {}).items()):
        probes = info.get("live_probes") or []
        print(f"  {svc}: {len(probes)} probe(s)")
        for p in probes[:5]:
            print(f"    - {p.get('method', 'GET')} {p.get('url')}")
        if len(probes) > 5:
            print(f"    … +{len(probes) - 5} more")

    watcher = TestQLWatcher(
        project_root=str(root),
        deps_file=str(root / "deps.json"),
        scenarios_dir=cfg.testql.scenario_dir,
        config=cfg,
    )

    print("\n=== Live HTTP probes only ===")
    rc = 0
    for svc in cfg.services:
        ok = asyncio.run(watcher._run_live_http_probes(svc.name, []))
        print(f"  {svc.name} (probe): {'PASS' if ok else 'FAIL'}")
        if not ok:
            rc = 1

    print("\n=== Quick TestQL dry-run (optional) ===")
    for svc in cfg.services:
        ok = asyncio.run(watcher.run_quick_test(svc.name, []))
        print(f"  {svc.name} (testql+dry-run): {'PASS' if ok else 'FAIL'}")

    health_path = root / ".wup" / "service-health.json"
    if health_path.exists():
        print("\n=== service-health.json ===")
        print(json.dumps(json.loads(health_path.read_text()), indent=2))

    manifest_path = root / "wup.yaml"
    loaded = load_monitoring_manifest_from_yaml(manifest_path)
    if loaded:
        bad = "8100/api/id/health" in json.dumps(loaded)
        print(f"\n=== Manifest check: stale 8100/api/id probes = {bad} ===")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
