"""
Visual DOM diff for WUP.

After a file change is detected, waits `delay_seconds`, then fetches the
configured pages with Playwright, records a DOM structure snapshot up to
`max_depth` levels, and compares with the previous snapshot.

Snapshots are stored in `.wup/visual-snapshots/<service>/<page_slug>.json`.
Diffs are appended to `.wup/visual-diffs/<service>/<page_slug>.jsonl`.

Playwright is an optional dependency — if not installed the module degrades
gracefully and logs a warning.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .models.config import VisualDiffConfig


console = Console()

# ---------------------------------------------------------------------------
# DOM snapshotting (Playwright)
# ---------------------------------------------------------------------------

_PW_AVAILABLE: Optional[bool] = None
_PW_WARNED: bool = False


def _playwright_available() -> bool:
    global _PW_AVAILABLE
    if _PW_AVAILABLE is None:
        try:
            import playwright  # noqa: F401
            _PW_AVAILABLE = True
        except ImportError:
            _PW_AVAILABLE = False
    return _PW_AVAILABLE


def _warn_playwright_missing() -> None:
    global _PW_WARNED
    if _PW_WARNED:
        return
    _PW_WARNED = True
    console.print(
        "[yellow]visual_diff: playwright not installed — DOM scan skipped "
        "(pip install playwright && playwright install chromium)[/yellow]"
    )


_DOM_SNAPSHOT_JS = """
(maxDepth) => {
    function snapshot(node, depth) {
        if (!node || depth > maxDepth) return null;
        const info = {tag: node.tagName || '#text'};
        if (node.id) info.id = node.id;
        if (node.className && typeof node.className === 'string' && node.className.trim())
            info.cls = node.className.trim().split(/\\s+/).sort().join(' ');
        const attrs = {};
        if (node.attributes) {
            for (const a of node.attributes) {
                if (!['class','id','style'].includes(a.name))
                    attrs[a.name] = a.value;
            }
        }
        if (Object.keys(attrs).length) info.attrs = attrs;
        const kids = [];
        for (const child of (node.children || [])) {
            const s = snapshot(child, depth + 1);
            if (s) kids.push(s);
        }
        if (kids.length) info.children = kids;
        return info;
    }
    return snapshot(document.documentElement, 0);
}
"""


async def _fetch_dom_snapshot(
    url: str,
    max_depth: int,
    headless: bool,
    error_selectors: List[str],
) -> Tuple[Optional[Dict], Optional[str]]:
    """Return a DOM structure dict for *url* using Playwright."""
    if not _playwright_available():
        _warn_playwright_missing()
        return None, "Playwright not installed"
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=headless)
            page = await browser.new_page()
            try:
                await page.goto(url, wait_until="networkidle", timeout=15_000)
                snapshot = await page.evaluate(_DOM_SNAPSHOT_JS, max_depth)
                text_length = await page.evaluate("() => (document.body?.innerText || '').trim().length")
                dom_nodes = await page.evaluate("() => document.querySelectorAll('*').length")
                matched_error_selectors = []
                for selector in error_selectors:
                    try:
                        count = await page.locator(selector).count()
                        if count > 0:
                            matched_error_selectors.append(selector)
                    except Exception:
                        continue

                if isinstance(snapshot, dict):
                    snapshot["meta"] = {
                        "text_length": int(text_length or 0),
                        "dom_nodes": int(dom_nodes or 0),
                        "matched_error_selectors": matched_error_selectors,
                    }
            finally:
                await browser.close()
        return snapshot, None
    except Exception as exc:
        return None, str(exc)


def _detect_content_issues(snapshot: Dict, cfg: VisualDiffConfig) -> List[str]:
    """Detect known runtime page issues from snapshot metadata."""
    meta = snapshot.get("meta", {}) if isinstance(snapshot, dict) else {}
    text_length = int(meta.get("text_length", 0))
    dom_nodes = int(meta.get("dom_nodes", 0))
    matched_error_selectors = meta.get("matched_error_selectors", []) or []

    issues: List[str] = []
    if matched_error_selectors:
        issues.append(f"error_container_detected:{','.join(matched_error_selectors)}")
    if text_length < cfg.min_text_length:
        issues.append(f"too_little_content:text_length={text_length}<min={cfg.min_text_length}")
    if dom_nodes < cfg.min_dom_nodes:
        issues.append(f"too_small_dom:nodes={dom_nodes}<min={cfg.min_dom_nodes}")
    return issues


# ---------------------------------------------------------------------------
# Snapshot persistence
# ---------------------------------------------------------------------------

def _page_slug(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_") or "root"
    return path[:80]


def _short_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return f"{path}?{parsed.query}" if parsed.query else path


def _compact_error_message(message: str, max_len: int = 180) -> str:
    compact = " ".join((message or "").split())
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3] + "..."


def _sample_list(items: List[str], limit: int = 3) -> str:
    if not items:
        return ""
    sample = ", ".join(items[:limit])
    remaining = len(items) - limit
    if remaining > 0:
        sample += f" (+{remaining} more)"
    return sample


def _looks_like_visual_page(url: str) -> bool:
    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    if not path or path in {"/", "/index.html"}:
        return True
    if path.startswith("/api/"):
        return False
    if any(
        token in path
        for token in (
            "/health",
            "/healthz",
            "/ready",
            "/live",
            "/status",
            "/openapi",
            "/execution/logs",
            "/execution/status",
        )
    ):
        return False
    return True


def _snapshot_path(snapshot_dir: Path, service: str, url: str) -> Path:
    slug = _page_slug(url)
    svc_safe = service.replace("/", "_")
    return snapshot_dir / svc_safe / f"{slug}.json"


def _load_snapshot(path: Path) -> Optional[Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_snapshot(path: Path, snapshot: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Diff algorithm (structural)
# ---------------------------------------------------------------------------

def _node_signature(node: Dict, depth: int = 0) -> str:
    """Produce a stable string identifier for a DOM node."""
    parts = [node.get("tag", "?")]
    if "id" in node:
        parts.append(f"#{node['id']}")
    if "cls" in node:
        parts.append(f".{node['cls']}")
    return "/".join(parts)


def _flatten(node: Optional[Dict], depth: int = 0, max_depth: int = 10) -> List[Tuple[int, str, Dict]]:
    """Return flat list of (depth, signature, attrs) for all nodes."""
    if node is None or depth > max_depth:
        return []
    result = [(depth, _node_signature(node, depth), node.get("attrs", {}))]
    for child in node.get("children", []):
        result.extend(_flatten(child, depth + 1, max_depth))
    return result


def _diff_snapshots(
    old: Optional[Dict],
    new: Optional[Dict],
    max_depth: int,
    threshold_added: int,
    threshold_removed: int,
    threshold_changed: int,
) -> Dict:
    """Compare two DOM snapshots. Returns a diff summary dict."""
    if old is None:
        return {"status": "new", "message": "No previous snapshot — baseline created"}

    old_nodes = _flatten(old, max_depth=max_depth)
    new_nodes = _flatten(new, max_depth=max_depth)

    old_sigs = {sig for _, sig, _ in old_nodes}
    new_sigs = {sig for _, sig, _ in new_nodes}

    added = new_sigs - old_sigs
    removed = old_sigs - new_sigs

    # check attribute changes for nodes present in both
    old_by_sig = {sig: attrs for _, sig, attrs in old_nodes}
    new_by_sig = {sig: attrs for _, sig, attrs in new_nodes}
    changed_attrs: List[str] = []
    for sig in old_sigs & new_sigs:
        if old_by_sig.get(sig) != new_by_sig.get(sig):
            changed_attrs.append(sig)

    significant = (
        len(added) >= threshold_added
        or len(removed) >= threshold_removed
        or len(changed_attrs) >= threshold_changed
    )

    return {
        "status": "changed" if significant else "ok",
        "added": sorted(added)[:20],
        "removed": sorted(removed)[:20],
        "changed_attrs": changed_attrs[:20],
        "counts": {
            "added": len(added),
            "removed": len(removed),
            "changed_attrs": len(changed_attrs),
            "total_old": len(old_nodes),
            "total_new": len(new_nodes),
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _resolve_base_url(cfg: VisualDiffConfig) -> str:
    if cfg.base_url:
        return cfg.base_url.rstrip("/")
    env_var = cfg.base_url_env or "WUP_BASE_URL"
    return os.environ.get(env_var, "").rstrip("/")


class VisualDiffer:
    """
    Triggered by TestQLWatcher after a file change.

    Usage::

        differ = VisualDiffer(project_root, config.visual_diff)
        results = await differ.run_for_service(service, changed_endpoints)
    """

    def __init__(self, project_root: str, cfg: VisualDiffConfig) -> None:
        self.project_root = Path(project_root)
        self.cfg = cfg
        self.snapshot_dir = self.project_root / cfg.snapshot_dir
        self.diff_dir = self.project_root / cfg.diff_dir
        self.base_url = _resolve_base_url(cfg)

    def _pages_for_service(self, service: str, endpoints: List[str]) -> List[str]:
        """Build list of full URLs to scan for this service."""
        pages: List[str] = list(self.cfg.pages)

        if self.cfg.pages_from_endpoints and endpoints:
            for endpoint in endpoints:
                pages.append(endpoint)

        if not pages:
            pages = [f"/{service}"]

        base = self.base_url or "http://localhost"
        result = []
        for p in pages:
            if p.startswith("http://") or p.startswith("https://"):
                if _looks_like_visual_page(p):
                    result.append(p)
            else:
                url = f"{base}{p}"
                if _looks_like_visual_page(url):
                    result.append(url)
        return result

    def _categorize_page_result(
        self,
        service: str,
        url: str,
        result: Dict[str, Any],
        ok_urls: List[str],
        new_urls: List[str],
        error_results: List[Tuple[str, str]],
    ) -> None:
        """Classify a single page result and append to the appropriate bucket."""
        status = result["diff"]["status"]
        if status in {"changed", "issue"}:
            self._write_diff_event(service, url, result)
            if status == "issue":
                console.print(
                    f"[bold red]🚨 Page issue: {service} {url}[/bold red]  "
                    f"{'; '.join(result['diff'].get('issues', []))}"
                )
            else:
                console.print(
                    f"[bold yellow]🔍 Visual diff: {service} {url}[/bold yellow]  "
                    f"+{result['diff']['counts']['added']} "
                    f"-{result['diff']['counts']['removed']} "
                    f"~{result['diff']['counts']['changed_attrs']}"
                )
        elif status == "new":
            new_urls.append(_short_url(url))
        elif status == "error":
            message = result["diff"].get("message", "scan failed")
            error_results.append((_short_url(url), message))
        elif status == "ok":
            ok_urls.append(_short_url(url))

    def _print_scan_summary(
        self,
        service: str,
        ok_urls: List[str],
        new_urls: List[str],
        error_results: List[Tuple[str, str]],
    ) -> None:
        """Print summary after scanning all pages for a service."""
        if new_urls:
            console.print(
                f"[dim]📷 Baseline snapshots for {service}: {len(new_urls)} page(s)"
                f" — {_sample_list(new_urls)}[/dim]"
            )
        if ok_urls:
            console.print(
                f"[dim green]✓ No DOM change for {service}: {len(ok_urls)} page(s)"
                f" — {_sample_list(ok_urls)}[/dim green]"
            )
        if error_results:
            grouped_messages = Counter(
                _compact_error_message(message or "scan failed")
                for _, message in error_results
            )
            top_messages = [
                f"{count}x {message}" for message, count in grouped_messages.most_common(2)
            ]
            message_summary = "; ".join(top_messages)
            failed_urls = [url for url, _ in error_results]
            console.print(
                f"[yellow]⚠ Visual diff skipped for {service}: {len(error_results)} page(s)"
                f" failed to fetch — {message_summary}; sample: {_sample_list(failed_urls)}[/yellow]"
            )

    async def run_for_service(
        self, service: str, endpoints: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Scan pages for *service*, diff against stored snapshots.
        Returns list of diff results (one per page).
        """
        if not self.cfg.enabled:
            return []

        if not _playwright_available():
            _warn_playwright_missing()
            return []

        if self.cfg.delay_seconds > 0:
            await asyncio.sleep(self.cfg.delay_seconds)

        pages = self._pages_for_service(service, endpoints)
        max_pages = max(1, int(self.cfg.max_pages or 5))
        if len(pages) > max_pages:
            pages = pages[:max_pages]

        results: List[Dict[str, Any]] = []
        ok_urls: List[str] = []
        new_urls: List[str] = []
        error_results: List[Tuple[str, str]] = []

        progress = self._build_progress(service, len(pages))
        if progress is None:
            for url in pages:
                result = await self._check_page(service, url)
                results.append(result)
                self._categorize_page_result(service, url, result, ok_urls, new_urls, error_results)
        else:
            with progress:
                task_id = progress.add_task(
                    f"[cyan]🔍 Visual diff {service}", total=len(pages), url=""
                )
                for url in pages:
                    progress.update(task_id, url=_short_url(url))
                    result = await self._check_page(service, url)
                    results.append(result)
                    self._categorize_page_result(service, url, result, ok_urls, new_urls, error_results)
                    progress.advance(task_id)

        self._print_scan_summary(service, ok_urls, new_urls, error_results)
        return results

    def _build_progress(self, service: str, total: int) -> Optional[Progress]:
        """Return a rich Progress for big scans; None for tiny ones (avoid noise)."""
        if total < 5 or os.environ.get("WUP_VISUAL_DIFF_PROGRESS", "1") == "0":
            return None
        return Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TextColumn("[dim]{task.fields[url]}"),
            TimeElapsedColumn(),
            TextColumn("eta"),
            TimeRemainingColumn(),
            console=console,
            transient=True,
            refresh_per_second=4,
        )

    async def _check_page(self, service: str, url: str) -> Dict[str, Any]:
        snap_path = _snapshot_path(self.snapshot_dir, service, url)
        old_snapshot = _load_snapshot(snap_path)

        new_snapshot, fetch_error = await _fetch_dom_snapshot(
            url,
            self.cfg.max_depth,
            self.cfg.headless,
            self.cfg.error_selectors,
        )

        if new_snapshot is None:
            return {
                "url": url,
                "diff": {
                    "status": "error",
                    "message": _compact_error_message(fetch_error or "Failed to fetch page"),
                },
            }

        diff = _diff_snapshots(
            old_snapshot,
            new_snapshot,
            self.cfg.max_depth,
            self.cfg.threshold_added,
            self.cfg.threshold_removed,
            self.cfg.threshold_changed,
        )

        issues = _detect_content_issues(new_snapshot, self.cfg)
        if issues:
            diff["status"] = "issue"
            diff["issues"] = issues

        # always update snapshot (new baseline)
        _save_snapshot(snap_path, new_snapshot)

        return {"url": url, "diff": diff, "timestamp": int(time.time())}

    def _write_diff_event(self, service: str, url: str, result: Dict) -> None:
        slug = _page_slug(url)
        svc_safe = service.replace("/", "_")
        diff_file = self.diff_dir / svc_safe / f"{slug}.jsonl"
        diff_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {"service": service, "url": url, **result}
        with diff_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_recent_diffs(self, seconds: int = 300) -> List[Dict]:
        """Return all diff events newer than *seconds* ago."""
        cutoff = int(time.time()) - seconds
        results = []
        if not self.diff_dir.exists():
            return results
        for jsonl_file in self.diff_dir.rglob("*.jsonl"):
            try:
                for line in jsonl_file.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if entry.get("timestamp", 0) >= cutoff:
                        results.append(entry)
            except Exception:
                pass
        results.sort(key=lambda e: e.get("timestamp", 0), reverse=True)
        return results
