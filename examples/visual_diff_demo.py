"""
Demo: WUP Visual DOM Diff

Shows how VisualDiffer works without requiring a live browser.
Uses synthetic DOM snapshots to demonstrate:
  - baseline creation
  - "ok" (no significant change)
  - "changed" (additions/removals above threshold)
  - get_recent_diffs() report
  - YAML configuration round-trip

Run:
  python3 examples/visual_diff_demo.py

Optional – scan a real page (requires playwright):
  python3 examples/visual_diff_demo.py http://localhost:8100/health
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wup.models.config import VisualDiffConfig, WupConfig, ProjectConfig, TestQLConfig
from wup.visual_diff import VisualDiffer, _diff_snapshots, _page_slug, _playwright_available


# ---------------------------------------------------------------------------
# Helpers for simulated snapshots
# ---------------------------------------------------------------------------

def _make_dom(n_divs: int) -> dict:
    """Return a minimal DOM tree with *n_divs* child DIVs under BODY."""
    return {
        "tag": "HTML",
        "children": [
            {
                "tag": "HEAD",
                "children": [{"tag": "TITLE"}],
            },
            {
                "tag": "BODY",
                "id": "app",
                "children": [
                    {"tag": "DIV", "id": f"block-{i}", "cls": "card"} for i in range(n_divs)
                ],
            },
        ],
    }


def _save_snapshot(path: Path, dom: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dom, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------

def demo_diff_algorithm():
    print("=" * 60)
    print("  1. Diff algorithm (no Playwright)")
    print("=" * 60)

    baseline = _make_dom(3)
    same = _make_dom(3)
    bigger = _make_dom(10)
    smaller = _make_dom(0)

    for label, old, new, cfg in [
        ("No previous snapshot (baseline)",
         None, baseline, (1, 1, 1)),
        ("Identical DOM",
         same, same, (1, 1, 1)),
        ("7 divs added (threshold=3 → changed)",
         baseline, bigger, (3, 3, 5)),
        ("3 divs removed (threshold=3 → changed)",
         baseline, smaller, (3, 3, 5)),
    ]:
        result = _diff_snapshots(old, new, max_depth=10, threshold_added=cfg[0],
                                 threshold_removed=cfg[1], threshold_changed=cfg[2])
        status = result["status"]
        emoji = {"new": "📷", "ok": "✅", "changed": "🔴", "error": "❌"}.get(status, "?")
        print(f"  {emoji}  {label}")
        if status not in ("new",):
            counts = result.get("counts", {})
            print(f"     added={counts.get('added', 0)}  removed={counts.get('removed', 0)}  "
                  f"changed_attrs={counts.get('changed_attrs', 0)}")
    print()


def demo_page_slug():
    print("=" * 60)
    print("  2. URL → slug mapping")
    print("=" * 60)
    urls = [
        "http://localhost:8100/",
        "http://localhost:8100/api/v1/users",
        "http://localhost:8100/api/v1/users/search",
        "https://example.com/dashboard/overview",
    ]
    for url in urls:
        print(f"  {url!r:50s}  →  {_page_slug(url)!r}")
    print()


def demo_snapshot_persistence():
    print("=" * 60)
    print("  3. Snapshot persistence & VisualDiffer helpers")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = VisualDiffConfig(
            enabled=True,
            base_url="http://localhost:8100",
            pages=["/health", "/dashboard"],
            pages_from_endpoints=True,
            threshold_added=3,
            threshold_removed=3,
            threshold_changed=5,
        )
        differ = VisualDiffer(str(root), cfg)

        service = "my-service"
        endpoints = ["/api/v1/users"]

        # Pages resolved
        pages = differ._pages_for_service(service, endpoints)
        print(f"  Pages for '{service}' with endpoints {endpoints}:")
        for p in pages:
            print(f"    {p}")
        print()

        # Simulate snapshot write for /health
        snap_path = differ.snapshot_dir / service / "health.json"
        _save_snapshot(snap_path, _make_dom(3))
        print(f"  Saved baseline snapshot: {snap_path.relative_to(root)}")

        # Simulate a diff event
        import time
        diff_file = differ.diff_dir / service / "health.jsonl"
        diff_file.parent.mkdir(parents=True, exist_ok=True)
        diff_file.write_text(
            json.dumps({
                "timestamp": int(time.time()),
                "service": service,
                "url": "http://localhost:8100/health",
                "diff": {"status": "changed",
                         "counts": {"added": 7, "removed": 0, "changed_attrs": 0,
                                    "total_old": 6, "total_new": 13}},
            }) + "\n",
            encoding="utf-8",
        )

        recent = differ.get_recent_diffs(seconds=60)
        print(f"  get_recent_diffs(60s) → {len(recent)} event(s)")
        for ev in recent:
            c = ev["diff"]["counts"]
            print(f"    {ev['url']}  +{c['added']} -{c['removed']} ~{c['changed_attrs']}")
    print()


def demo_config_yaml_round_trip():
    print("=" * 60)
    print("  4. wup.yaml round-trip with visual_diff section")
    print("=" * 60)
    from wup.config import save_config, load_config

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        cfg = WupConfig(
            project=ProjectConfig(name="demo-app"),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
            visual_diff=VisualDiffConfig(
                enabled=True,
                base_url="http://localhost:8100",
                pages=["/health", "/dashboard"],
                delay_seconds=3.0,
                max_depth=8,
                threshold_added=5,
            ),
        )
        config_path = root / "wup.yaml"
        save_config(cfg, config_path)
        print(f"  Saved wup.yaml ({config_path.stat().st_size} bytes)")

        reloaded = load_config(root)
        vd = reloaded.visual_diff
        print(f"  Reloaded: enabled={vd.enabled}  base_url={vd.base_url!r}  "
              f"pages={vd.pages}  max_depth={vd.max_depth}  threshold_added={vd.threshold_added}")
        assert vd.enabled is True
        assert vd.base_url == "http://localhost:8100"
        assert vd.pages == ["/health", "/dashboard"]
        assert vd.max_depth == 8
        assert vd.threshold_added == 5
        print("  ✅ Round-trip assertions passed")
    print()


def demo_disabled_is_noop():
    print("=" * 60)
    print("  5. Disabled differ is a no-op")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = VisualDiffConfig(enabled=False)
        differ = VisualDiffer(tmpdir, cfg)
        results = asyncio.run(differ.run_for_service("svc", ["/api/x"]))
        print(f"  run_for_service() returned: {results!r}")
        assert results == [], "Expected empty list when disabled"
        print("  ✅ No-op confirmed")
    print()


async def demo_live_page(url: str):
    print("=" * 60)
    print(f"  6. Live page scan: {url}")
    print("=" * 60)
    if not _playwright_available():
        print("  ⚠  playwright not installed — skipping live scan")
        print("     Install: pip install playwright && playwright install chromium")
        print()
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = VisualDiffConfig(
            enabled=True,
            base_url="",
            pages=[url],
            pages_from_endpoints=False,
            delay_seconds=0,
        )
        differ = VisualDiffer(tmpdir, cfg)
        results = await differ.run_for_service("live", [])
        for r in results:
            status = r["diff"]["status"]
            emoji = {"new": "📷", "ok": "✅", "changed": "🔴", "error": "❌"}.get(status, "?")
            print(f"  {emoji}  {r['url']}  status={status}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("  WUP Visual DOM Diff — Demo")
    print()

    demo_diff_algorithm()
    demo_page_slug()
    demo_snapshot_persistence()
    demo_config_yaml_round_trip()
    demo_disabled_is_noop()

    if len(sys.argv) > 1:
        asyncio.run(demo_live_page(sys.argv[1]))
    else:
        print("  (Pass a URL as argument to run a live Playwright scan)")
        print("  e.g.: python3 examples/visual_diff_demo.py http://localhost:8100/health")
        print()

    print("  All demos completed successfully.")


if __name__ == "__main__":
    main()
