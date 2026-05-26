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


def print_probe_plan(manifest: dict) -> None:
    """Print the probe plan details from the manifest."""
    print("=== Probe plan (from current config) ===")
    for svc, info in sorted((manifest.get("wup_services") or {}).items()):
        probes = info.get("live_probes") or []
        print(f"  {svc}: {len(probes)} probe(s)")
        for p in probes[:5]:
            print(f"    - {p.get('method', 'GET')} {p.get('url')}")
        if len(probes) > 5:
            print(f"    … +{len(probes) - 5} more")


def run_live_http_probes(watcher: TestQLWatcher, services: list) -> bool:
    """Run live HTTP probes for each service. Returns True if all passed."""
    print("\n=== Live HTTP probes only ===")
    all_ok = True
    for svc in services:
        ok = asyncio.run(watcher._run_live_http_probes(svc.name, []))
        print(f"  {svc.name} (probe): {'PASS' if ok else 'FAIL'}")
        if not ok:
            all_ok = False
    return all_ok


def run_quick_testql_dryrun(watcher: TestQLWatcher, services: list) -> None:
    """Run quick TestQL dry-run for each service."""
    print("\n=== Quick TestQL dry-run (optional) ===")
    for svc in services:
        ok = asyncio.run(watcher.run_quick_test(svc.name, []))
        print(f"  {svc.name} (testql+dry-run): {'PASS' if ok else 'FAIL'}")


def print_service_health(health_path: Path) -> None:
    """Print service health from service-health.json if it exists."""
    if health_path.exists():
        print("\n=== service-health.json ===")
        print(json.dumps(json.loads(health_path.read_text()), indent=2))


def check_manifest_stale_probes(manifest_path: Path) -> None:
    """Load monitoring manifest and verify if there are stale 8100/api/id probes."""
    loaded = load_monitoring_manifest_from_yaml(manifest_path)
    if loaded:
        bad = "8100/api/id/health" in json.dumps(loaded)
        print(f"\n=== Manifest check: stale 8100/api/id probes = {bad} ===")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cfg = load_config(root)
    manifest = build_monitoring_manifest(root, cfg)

    print_probe_plan(manifest)

    watcher = TestQLWatcher(
        project_root=str(root),
        deps_file=str(root / "deps.json"),
        scenarios_dir=cfg.testql.scenario_dir,
        config=cfg,
    )

    all_probes_ok = run_live_http_probes(watcher, cfg.services)
    
    run_quick_testql_dryrun(watcher, cfg.services)

    print_service_health(root / ".wup" / "service-health.json")

    check_manifest_stale_probes(root / "wup.yaml")

    return 0 if all_probes_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
