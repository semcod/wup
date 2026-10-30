---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "probe-latency-recovery",
  "kind": "information",
  "version": 1,
  "title": "Recovery of latency incidents from exact probe evidence",
  "status": "proposed",
  "owner": "semcod/wup maintainers",
  "created": "2026-10-30",
  "updated": "2026-10-30",
  "review_after": "2026-11-30",
  "source_revision": "a413d469bee71e516809be54702872631a2ca015",
  "affected_repositories": ["semcod/wup"],
  "evidence": [
    "repo://semcod/wup#wup/testql_watcher.py",
    "repo://semcod/wup#wup/planfile_reporter.py",
    "repo://semcod/wup#tests/test_probe_stage_recovery.py"
  ]
}
---
# Recovery of probe latency incidents

<!-- docs:section purpose -->
## Purpose

A latency alarm uses stage `probe-latency`; a subsequent passing quick scenario
uses stage `quick`. Clearing only the latter stage leaves the original incident
open even when `complete_on_recovery` is enabled. PLF-204 addresses this gap.

<!-- docs:section scope -->
## Scope

Resolve only latency incidents backed by fresh successful HTTP observations.
Keep existing latency thresholds, confirmation counts, recurrence behavior and
the explicit `complete_on_recovery` switch. Other incident stages retain their
existing lifecycle.

<!-- docs:section evidence -->
## Evidence

The regression suite exercises the real probe monitor, latency tracker, watcher
and reporter against private ticket projections. It covers successful recovery,
failed and omitted probes, learning, continuing violations, compound incidents,
malformed evidence and a slower relearned baseline. Three cases failed against
the original source. The focused watcher/monitor/tracker/reporter run passes
74 tests; protected publication and deployment require their own receipts.

<!-- docs:section content -->
## Recovery contract

The monitor records which endpoints actually passed during the current probe
cycle, after applying its ordering and count limit. A successful cycle asks the
reporter to reconcile only the same service's `probe-latency` incidents.

For each incident the reporter reads its original failure summary through the
configured Planfile CLI. Every original URL must have been sampled successfully
now, have a learned latency baseline and no current violation, and pass the
unchanged latency policy against the incident's original baseline. This prevents
a restart that learns consistently slow responses from resolving an older alarm.

Missing or malformed ticket evidence stays unresolved. A compound alarm waits
for all original URLs. Failed completion preserves its deduplication entry for
retry. A passing quick scenario alone supplies no latency recovery evidence.

<!-- docs:section limitations -->
## Limitations

This change resolves incident lifecycle; it does not remove host contention or
prove that latency spikes cannot recur. The existing single service-health
projection and its treatment of other stages are outside this change. Source
publication does not update a separately pinned watcher runtime.

<!-- docs:section next_actions -->
## Validation and adoption

Run the focused regression suites and the pinned Docs checker, then require
exact-head OneDev verification and independent Validator publication. A runtime
owner must separately adopt the published artifact and verify original incidents
with the configured native Planfile CLI before recording deployment acceptance.
