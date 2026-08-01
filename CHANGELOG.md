# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Continuous todo2code Intent-vs-Reality monitoring.** The opt-in
  `intent_monitoring` section runs deterministic or LLM-backed audits on
  startup, periodically and after debounced file changes. Findings enter the
  normal WUP health/event/Planfile stream as `<project>:intent`, and both the
  todo2code CLI and its Python SDK bridge are supported.
- **Pluggable endpoint-discovery adapters (`wup/discovery.py`).** `deps.json` is
  now built by per-ecosystem adapters — FastAPI, Flask, Django, NestJS, Express,
  Fastify, Hono, Go (gin/echo/net-http) and OpenAPI/Swagger — selected by repo
  markers instead of a hardcoded four-framework switch. Adding a framework means
  adding an adapter, not editing the mapper. Endpoints are de-duplicated across
  adapters and HTTP methods.
- **OQL — Observability Query Language (`wup/oql.py`, `wup oql`).** A small
  declarative language over observed state (service health + events):
  `wup oql "services where status = down"`, `wup oql "events since 10m limit 5"`.
  Supports `= != > < >= <= ~ !~`, `since <dur>`, `limit`, `--json` output, and a
  `RunOQL` query on the CQRS event bus so agents can read state programmatically.
- **AQL — Assertion Query Language (`wup/aql.py`, `wup aql`).** Declarative
  assertions about a file's data (JSON/YAML/text) that emit `AnomalyResult`
  violations: `wup aql wup.yaml "yaml .project.name exists" "json .services
  length > 0"`. Supports paths with `[index]`, predicates `exists/missing`,
  `= != > < >= <=`, `~ !~`, `matches <regex>`, `length <op> <n>`, `type <t>`,
  per-rule `severity`, `--json` output (non-zero exit on failure for CI), and a
  `CheckAQL` bus query. Together TestQL + OQL + AQL give AI agents one declarative
  surface to test behaviour, read state, and assert invariants.
- **Config-driven docker→service mapping.** `testql.docker_service_map`
  (`{substring: service}`) and `testql.service_map_profile` let a project map its
  compose services to WUP services without any names hardcoded in WUP. The old
  maskservice/c2004 "connect" fleet rules are now an opt-in built-in profile
  (`service_map_profile: connect`) instead of always-on logic.
- **Config-driven probe rejection.** `testql.monitoring_reject_prefixes` (and the
  `connect` profile) control which URL path prefixes are excluded from health
  probes. The default rejects nothing, so a generic project's `/api/*` health
  endpoints are no longer wrongly filtered out by hardcoded "connect" fleet paths.
- **Config-driven service-name prefixes.** `core.py`'s directory→service heuristic
  is now generic (`backend/frontend/api/app/worker/service`); the fleet-specific
  `connect-*` prefix is opt-in via `service_map_profile: connect`, and projects add
  their own via `testql.service_name_prefixes`.
- `docs/GENERICITY_AUDIT.md` — inventory of how `wup.yaml`/`deps.json` are
  generated, where the tool is hardwired to one project, and a TestQL+OQL+AQL
  roadmap toward a language-agnostic, AI-open design.

### Fixed
- **`deps.json` now works for JS/TS projects.** `_scan_js_endpoints` used
  `rglob("*.{js,ts,jsx,tsx}")`, which pathlib never brace-expands, so it matched
  zero files; it now iterates real extensions. Framework detection is
  language-scoped (Python indicators only in `.py`, Express only in JS/TS) to stop
  frontend files false-positiving as Flask, and `_infer_service` recognises
  `services/`, `packages/`, `lib/`, … not just `app/`/`src/`.
- `DependencyMapper.to_dict()` no longer positionally-zips three dicts (which
  corrupted the map when a service had files but no endpoints); it iterates the
  union of service keys.
- Auto-generated `wup.yaml` now watches source directories that actually exist
  (probing `app`, `src`, `routes`, `services`, `lib`, `packages`, …) instead of
  always writing `app/src/routes`. This fixes `No valid paths to watch` on
  projects whose code lives under a different top-level folder (e.g. a monorepo
  module using `services/`).
- `wup watch .` now detects source directories inside immediate project
  subfolders (for example `api/src` and `worker/services`) through
  `wup/config.py::detect_watch_paths`. Existing older auto-generated configs
  whose `app/src/routes` paths do not exist fall back through
  `wup/core.py::WupWatcher.build_watched_paths` instead of exiting with
  `No valid paths to watch`; regression coverage lives in
  `tests/test_multi_project.py`.

- **Simultaneous multi-project watching.** `wup watch` now accepts several
  project directories and watches them at once in a single process
  (`wup watch proj-a proj-b proj-c`). Each project keeps its own wup.yaml,
  dependency map, file observer and test queue.
- **`--discover` / `-D` flag.** Expands a monorepo root into every immediate
  sub-directory that already has a wup.yaml and watches each one
  (`wup watch --discover .`). Hidden and vendor folders (node_modules, .venv,
  dist, build, …) are skipped.

### Changed
- A relative `--deps` path is now resolved against each project's own root, so
  multiple watched projects no longer share one deps.json. For `wup watch .`
  this is the current directory as before.
- TestQL periodic live probes now also run in `--dashboard` mode.

### Refactored
- Split the high-cyclomatic-complexity methods flagged by `project/analysis.toon.yaml`
  into focused helpers (behaviour unchanged, all tests green):
  `_map_docker_to_wup_service` and `format_manifest_summary` (monitoring_manifest),
  `collect_status_snapshot` (status_data), `_create_ticket` (planfile_reporter),
  and `_select_scenarios_for_service` (testql_watcher). Also removed a dead
  web-service branch in scenario selection.

## [0.2.79] - 2026-07-29

### Docs
- Update README.md

### Other
- Update app.doql.events.pb
- Update tree.txt
- Update wup/aql.py

## [0.2.78] - 2026-07-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_assistant.py
- Update tests/test_auto_detection.py
- Update tests/test_bootstrap.py
- Update tests/test_cli_filtering.py
- Update tests/test_e2e.py
- Update tests/test_monitoring_manifest.py
- Update tests/test_multi_project.py
- Update tests/test_service_inference.py
- Update tests/test_testql_monitor.py
- Update tests/test_visual_diff_progress.py
- ... and 1 more files

### Other
- Update Makefile
- Update app.doql.events.pb
- Update app.doql.less
- Update packages/cli2wup/src/cli2wup/cli.py
- Update packages/dsl2wup/src/dsl2wup/cli.py
- Update packages/dsl2wup/src/dsl2wup/codegen.py
- Update packages/dsl2wup/src/dsl2wup/events.py
- Update packages/dsl2wup/src/dsl2wup/grammar.py
- Update packages/dsl2wup/src/dsl2wup/handlers/command.py
- Update packages/dsl2wup/src/dsl2wup/pb_codec.py
- ... and 41 more files

## [0.2.77] - 2026-07-17

### Docs
- Update README.md

### Test
- Update tests/test_multi_project.py

### Other
- Update app.doql.events.pb
- Update wup/config.py

## [0.2.76] - 2026-07-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/GENERICITY_AUDIT.md

### Test
- Update tests/test_genericity.py

### Other
- Update app.doql.events.pb
- Update wup/config.py
- Update wup/core.py
- Update wup/models/config.py

## [0.2.75] - 2026-07-17

### Docs
- Update README.md

### Other
- Update app.doql.events.pb

## [0.2.74] - 2026-07-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/GENERICITY_AUDIT.md

### Test
- Update tests/test_aql.py
- Update tests/test_discovery_adapters.py
- Update tests/test_genericity.py
- Update tests/test_oql.py
- Update tests/test_testql_monitor.py

### Other
- Update app.doql.events.pb
- Update wup/aql.py
- Update wup/cli.py
- Update wup/config.py
- Update wup/dependency_mapper.py
- Update wup/discovery.py
- Update wup/models/config.py
- Update wup/oql.py
- Update wup/testql_monitor.py

## [0.2.73] - 2026-07-17

### Docs
- Update README.md

### Other
- Update app.doql.events.pb
- Update wup/discovery.py

## [0.2.72] - 2026-07-17

### Docs
- Update README.md

### Other
- Update app.doql.events.pb
- Update uv.lock
- Update wup/discovery.py

## [0.2.71] - 2026-07-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/GENERICITY_AUDIT.md

### Test
- Update tests/test_genericity.py

### Other
- Update app.doql.events.pb
- Update wup/config.py
- Update wup/dependency_mapper.py
- Update wup/models/config.py
- Update wup/monitoring_manifest.py

## [0.2.70] - 2026-07-17

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_multi_project.py

### Other
- Update app.doql.events.pb
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- Update project/flow.mmd
- ... and 16 more files

## [0.2.69] - 2026-07-16

### Docs
- Update README.md

### Other
- Update .koru/event-store.jsonl
- Update .koru/events/observability.jsonl
- Update .nlp2dsl/environment.doql.less
- Update .nlp2dsl/registry/environment.doql.less
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- Update app.doql.events.pb
- ... and 4 more files

## [0.2.68] - 2026-07-03

### Docs
- Update README.md

### Other
- Update app.doql.events.pb
- Update uv.lock

## [0.2.67] - 2026-06-29

### Docs
- Update README.md

## [0.2.66] - 2026-06-08

### Docs
- Update README.md
- Update packages/README.md
- Update packages/cli2wup/README.md
- Update packages/dsl2wup/README.md
- Update packages/mcp2wup/README.md
- Update packages/nlp2wup/README.md
- Update packages/rest2wup/README.md
- Update packages/uri2wup/README.md

### Test
- Update tests/test_cli_bridge.py
- Update tests/test_control.py
- Update tests/test_endpoints_init_cli.py
- Update tests/test_status_data.py
- Update tests/test_sync.py
- Update tests/test_wup_generate.py

### Other
- Update .gillm/events/app.gillm.events.pb
- Update .gitignore
- Update app.doql.events.pb
- Update app.doql.less
- Update packages/cli2wup/pyproject.toml
- Update packages/cli2wup/src/cli2wup/__init__.py
- Update packages/cli2wup/src/cli2wup/cli.py
- Update packages/cli2wup/tests/test_cli2wup.py
- Update packages/dsl2wup/proto/dsl2wup/v1/command.proto
- Update packages/dsl2wup/proto/dsl2wup/v1/result.proto
- ... and 81 more files

## [0.2.65] - 2026-06-03

### Docs
- Update README.md

### Test
- Update tests/test_testql_monitor.py

### Other
- Update .idea/pyLspTools.xml
- Update Makefile
- Update wup/config.py
- Update wup/models/config.py
- Update wup/monitoring_manifest.py
- Update wup/testing/handlers/health_handlers.py
- Update wup/testql_monitor.py

## [0.2.64] - 2026-05-27

### Docs
- Update README.md

### Other
- Update VERSION
- Update poetry.lock
- Update uv.lock
- Update wup/__init__.py

## [0.2.62] - 2026-05-27

### Docs
- Update README.md

## [0.2.61] - 2026-05-27

### Docs
- Update README.md

### Other
- Update wup/config.py
- Update wup/models/config.py
- Update wup/monitoring_manifest.py

## [0.2.60] - 2026-05-26

### Docs
- Update README.md

### Other
- Update .planfile/sprints/current.yaml
- Update examples/visual_diff_demo.py
- Update examples/webhook_notifications.py
- Update wup/cli.py
- Update wup/config.py
- Update wup/monitoring_manifest.py
- Update wup/visual_diff.py

## [0.2.59] - 2026-05-26

### Docs
- Update README.md

### Test
- Update tests/test_assistant.py

### Other
- Update .koru/event-store.jsonl
- Update .koru/events/observability.jsonl
- Update .koru/keys/screencast.session
- Update .koru/project.json
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .planfile/config.yaml
- Update .planfile/sprints/current.yaml
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- ... and 10 more files

## [0.2.58] - 2026-05-26

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.57] - 2026-05-26

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.56] - 2026-05-25

### Docs
- Update README.md

### Other
- Update .koru/event-store.jsonl
- Update .koru/keys/screencast.session
- Update .koru/project.json
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .planfile/config.yaml
- Update .planfile/sprints/current.yaml
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- ... and 1 more files

## [0.2.55] - 2026-05-25

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .koru/event-store.jsonl
- Update .planfile/.store.lock
- Update .planfile/config.yaml
- Update .planfile/sprints/current.yaml
- Update app.doql.less
- Update duplication.json
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- ... and 15 more files

## [0.2.54] - 2026-05-24

### Docs
- Update README.md

### Other
- Update .koru/event-store.jsonl
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- Update uv.lock

## [0.2.53] - 2026-05-24

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/Taskfile_1779635779396134993_705.pkl
- Update .code2llm_cache/__init___1779638198782020523_1238.pkl
- Update .code2llm_cache/config_1779637229299258868_6752.pkl
- Update .code2llm_cache/config_1779638086299112913_18971.pkl
- Update .code2llm_cache/core_1779636922238636681_25124.pkl
- Update .code2llm_cache/goal_1779635891400000000_12301.pkl
- Update .code2llm_cache/pyproject_1779638198769513096_1830.pkl
- Update .code2llm_cache/testql_watcher_1779638080223048207_38618.pkl
- Update .code2llm_cache/visual_diff_1779636890209381411_20082.pkl
- Update .code2llm_cache/wup_1779638109658370579_3017.pkl
- ... and 28 more files

## [0.2.52] - 2026-05-24

### Docs
- Update README.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_health_summary_passed.py
- Update tests/test_probe_mutex.py
- Update tests/test_visual_diff_progress.py
- Update tests/test_watch_exclude.py

### Other
- Update .koru/event-store.jsonl
- Update .koru/project.json
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .planfile/config.yaml
- Update .planfile/sprints/current.yaml
- Update .planfile/sprints/current.yaml.lock
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- ... and 13 more files

## [0.2.51] - 2026-05-24

### Docs
- Update README.md

### Other
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- Update uv.lock
- Update wup.yaml

## [0.2.50] - 2026-05-24

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.49] - 2026-05-24

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .gitignore
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- Update Taskfile.yml
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- ... and 19 more files

## [0.2.48] - 2026-05-24

### Docs
- Update README.md

## [0.2.47] - 2026-05-24

### Docs
- Update README.md

### Test
- Update tests/test_testql_watcher.py

### Other
- Update .koru/event-store.jsonl
- Update .koru/project.json
- Update .planfile/.koru/autoloop-diag/wup-iter1-api.failed
- Update .planfile/.koru/autoloop-diag/wup-iter1-shell.failed
- Update .planfile/.koru/autoloop-diag/wup-iter7-auto.failed
- Update .planfile/.koru/autoloop-diag/wup-iter7-shell.failed
- Update .planfile/.koru/autonomous-state.json
- Update .planfile/.koru/autonomy-telemetry.json
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- ... and 4 more files

## [0.2.46] - 2026-05-23

### Docs
- Update README.md

### Test
- Update tests/test_wup.py

### Other
- Update uv.lock
- Update wup/config.py
- Update wup/testql_watcher.py

## [0.2.45] - 2026-05-23

### Docs
- Update README.md

### Other
- Update .gitignore
- Update .planfile/sprints/current.yaml
- Update regix.yaml
- Update uv.lock

## [0.2.44] - 2026-05-23

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/cli-smoke.testql.toon.yaml
- Update testql-scenarios/cli-wup.testql.toon.yaml
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update tests/test_testql_watcher.py

### Other
- Update .cursor/mcp.json
- Update .gitignore
- Update .koru/history.jsonl
- Update .koru/onboarding.json
- Update .koru/project.json
- Update .planfile/.koru/autoloop-diag/wup-iter1-api.failed
- Update .planfile/.koru/autoloop-diag/wup-iter1-shell.failed
- Update .planfile/.koru/autoloop-diag/wup-iter7-auto.failed
- Update .planfile/.koru/autoloop-diag/wup-iter7-shell.failed
- Update .planfile/.koru/autonomous-state.json
- ... and 121 more files

## [0.2.43] - 2026-05-23

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/TEST_PLAN.md
- Update tests/TEST_SUMMARY.md
- Update tests/test_auto_detection.py
- Update tests/test_cli_filtering.py
- Update tests/test_service_inference.py

### Other
- Update .gitignore
- Update .wup/browser-events/latest.json
- Update .wup/service-health.json
- Update .wup/tracks/1779487305_wup-shell_quick.json
- Update .wup/tracks/1779487406_wup-shell_quick.json
- Update .wup/tracks/1779487427_wup-shell_quick.json
- Update .wup/tracks/1779487429_wup-shell_detail.json
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- ... and 19 more files

## [0.2.42] - 2026-05-22

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/context.md

### Test
- Update tests/test_wup.py

### Other
- Update .code2llm_cache/__init___1779486150751966031_1238.pkl
- Update .code2llm_cache/pyproject_1779486150737995527_1830.pkl
- Update .code2llm_cache/testql_watcher_1779486123709000000_33681.pkl
- Update .code2llm_cache/wup_1779486342062745131_3017.pkl
- Update .wup/browser-events/latest.json
- Update .wup/service-health.json
- Update .wup/tracks/1779486174_iter1-api_quick.json
- Update .wup/tracks/1779486175_iter1-shell_quick.json
- Update .wup/tracks/1779486175_iter7-auto_quick.json
- Update .wup/tracks/1779486176_iter7-shell_quick.json
- ... and 48 more files

## [0.2.41] - 2026-05-22

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md

### Other
- Update .wup/browser-events/latest.json
- Update .wup/service-health.json
- Update .wup/tracks/1779486110_iter1-api_quick.json
- Update .wup/tracks/1779486111_iter1-shell_quick.json
- Update .wup/tracks/1779486112_iter7-auto_quick.json
- Update .wup/tracks/1779486112_iter7-shell_quick.json
- Update .wup/tracks/1779486113_wup-shell_quick.json
- Update .wup/tracks/1779486124___home_quick.json
- Update .wup/tracks/1779486127___home_detail.json
- Update app.doql.less
- ... and 6 more files

## [0.2.40] - 2026-05-22

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/config_1779485633797501415_6453.pkl
- Update .code2llm_cache/config_1779485903503139874_16729.pkl
- Update .code2llm_cache/testql_watcher_1779485964454000000_33378.pkl
- Update .code2llm_cache/tree_1779485611539296271_4265.pkl
- Update .code2llm_cache/wup_1779485971513156277_3016.pkl
- Update .gitignore
- Update .wup/browser-events/latest.json
- Update .wup/service-health-events.jsonl
- Update .wup/service-health.json
- Update .wup/tracks/1779485019___home_quick.json
- ... and 58 more files

## [0.2.39] - 2026-05-22

### Docs
- Update CHANGELOG.md
- Update README.md

### Other
- Update uv.lock
- Update wup.yaml
- Update wup/cli_config_generator.py

## [0.2.38] - 2026-05-22

### Added
- **CLI/Shell Automation**: New `wup init-cli` command for automatic detection and configuration of CLI tools and shell scripts
  - `cli_scanner.py` - Detects CLI commands from pyproject.toml, setup.py, setup.cfg, and __main__.py modules
  - `cli_config_generator.py` - Generates wup.yaml configuration for shell services
  - `testql_cli_generator.py` - Generates TestQL scenarios for CLI commands
  - Supports merging with existing wup.yaml configurations
  - Auto-infers command arguments by inspection (can be disabled)

### Changed
- **Refactoring**: Reduced cyclomatic complexity of `_assign_http_probe` method in testql_monitor.py from CC=19 to CC<15
  - Extracted helper methods: `_find_service_by_name`, `_find_service_by_token`, `_assign_by_port_8101`, `_assign_by_port_8202`, `_assign_by_port_8100`, `_assign_by_connect_backend`
- **Refactoring**: Broke 2 circular dependencies
  - Made `TestQLWatcher` import lazy in __init__.py via `__getattr__`
  - Made `TestQLMonitor` import lazy in testql_watcher.py

### Docs
- Update README.md with CLI/Shell automation documentation
- Update docs/TESTQL_INTEGRATION.md with init-cli command details
- Update docs/WUP_ASSISTANT.md to reference init-cli

### Test
- Update testql-scenarios/cli-smoke.testql.toon.yaml
- Update testql-scenarios/cli-wup.testql.toon.yaml

### Other
- Update uv.lock
- Update wup.yaml

## [0.2.37] - 2026-05-22

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/__init___1779396843079217862_994.pkl
- Update .code2llm_cache/cli_1779358589700069902_27494.pkl
- Update .code2llm_cache/config_1779393825903947745_6450.pkl
- Update .code2llm_cache/config_1779393839370074367_16726.pkl
- Update .code2llm_cache/core_1779393875903418379_24048.pkl
- Update .code2llm_cache/monitoring_manifest_1779358512685371221_12068.pkl
- Update .code2llm_cache/planfile_reporter_1779396522047955511_7461.pkl
- Update .code2llm_cache/pyproject_1779396822426008563_1830.pkl
- Update .code2llm_cache/testql_monitor_1779358638454517220_17951.pkl
- Update .code2llm_cache/testql_watcher_1779394052771092604_31192.pkl
- ... and 30 more files

## [0.2.36] - 2026-05-21

### Fixed
- **inotify watch limit fallback**: `wup watch` no longer crashes with `OSError: [Errno 28] inotify watch limit reached`. When the system's inotify limits are exceeded, WUP automatically falls back to `watchdog.observers.polling.PollingObserver` with a clear console warning.

### Refactored
- Split 8 high cyclomatic-complexity methods into smaller helpers:
  - `wup/testql_monitor.py`: `assign_probe_to_service` (CC 40→9) → `_assign_http_probe`, `_assign_by_longest_token`, `_assign_by_path_prefix`
  - `wup/testql_monitor.py`: `discover_probes_by_service` (CC 22→6) → `_ProbeAccumulator`, `_add_config_endpoints`, `_add_scenario_probes`, `_add_service_map_probes`
  - `wup/testql_monitor.py`: `parse_service_map_probes` (CC 15→5) → `_extract_base_url`, `_parse_endpoint_row`
  - `wup/testql_watcher.py`: `_summarize_health_scenario_failure` (CC 19→5) → `_try_parse_json_summary`, `_try_find_line_summary`
  - `wup/visual_diff.py`: `run_for_service` (CC 19→7) → `_categorize_page_result`, `_print_scan_summary`
  - `wup/monitoring_manifest.py`: `discover_docker_compose_services` (CC 20→7) → `_load_compose_yaml`, `_extract_service_from_spec`, `_extract_healthcheck_test`
  - `wup/monitoring_manifest.py`: `build_monitoring_manifest` (CC 19→6) → `_build_wup_service_dicts`, `_build_docker_rows`, `_build_scenario_rows`
  - `wup/cli.py`: `watch` (CC 15→4) → `_load_watch_config`, `_print_watch_header`, `_refresh_monitoring_manifest`, `_create_watcher`

### Added
- **New Examples**: Added comprehensive usage examples
  - `c2004_monorepo_demo.py`: Large monorepo analysis (21 connect-* modules)
  - `ci_cd_integration.py`: CI/CD pipeline integration patterns (GitHub Actions, GitLab CI)
  - `webhook_notifications.py`: Slack, Teams, Discord notifications
- **c2004 Integration**: Tested and verified with c2004 project at `/home/tom/github/maskservice/c2004`
- **Enhanced wup.yaml Generation**: `wup init` now generates config with:
  - Metadata header (version, generation date)
  - Documentation links (PyPI, GitHub, README)
  - Dependencies info (wup version, wupbro optional)
  - wupbro section comments with install/run instructions
  - Quick start guide in comments
- **Configuration Assistant** (`wup assistant`): Interactive shell assistant for wup.yaml
  - Auto-detects framework (FastAPI, Flask, Django, Express)
  - Auto-detects services from project structure
  - Guided setup for services, watch paths, TestQL, web dashboard
  - Validation and intelligent suggestions
  - Quick mode: `wup assistant --quick --template fastapi`
- **Fast Anomaly Detection**: Alternatives to Playwright for YAML/config monitoring
  - Hash-based detection (~1ms per file)
  - YAML structure analysis (keys, types, nesting)
  - Python AST diff for API changes
  - Configure via `anomaly_detection:` in wup.yaml
- **Browser Notifications** (wupbro): Real-time notifications for regression events
  - 7 notification types: REGRESSION_NEW, REGRESSION_DIFF, STATUS_TRANSITION, PASS_RECOVERY, ANOMALY_NEW, VISUAL_DIFF_NEW, HEALTH_CHANGE
  - Configurable per-type with cooldown and service filtering
  - Server-Sent Events (SSE) for instant delivery
  - Native Browser Notifications API integration
  - Dashboard UI for configuration
- **Notification System** (wupbro backend):
  - `POST /notifications/subscribe` - Create subscription
  - `GET /notifications/stream` - SSE endpoint for real-time notifications
  - `PUT /notifications/subscriptions/{id}` - Update config
  - `POST /notifications/test` - Send test notification
  - NotificationManager with event detection and cooldown
- **Documentation Suite**: Comprehensive docs in `docs/` directory
  - `docs/WUP_ASSISTANT.md` - Configuration assistant guide
  - `docs/ANOMALY_DETECTION.md` - Fast anomaly detection methods
  - `docs/NOTIFICATIONS.md` - Browser notifications setup
  - `docs/TESTQL_INTEGRATION.md` - TestQL integration guide
- **Package Rename**: wup-web → wupbro (dashboard package)
  - Renamed folder and all references
  - Updated CLI command from `wup-web` to `wupbro`
  - Updated documentation and environment variables

### Docs
- Updated README.md with new examples

## [0.2.35] - 2026-05-21

### Docs
- Update README.md

### Other
- Update uv.lock
- Update wup/planfile_reporter.py

## [0.2.34] - 2026-05-21

### Docs
- Update README.md

### Test
- Update tests/test_testql_watcher.py
- Update tests/test_wup.py

### Other
- Update uv.lock
- Update wup/config.py
- Update wup/core.py
- Update wup/models/config.py
- Update wup/planfile_reporter.py
- Update wup/testql_watcher.py

## [0.2.33] - 2026-05-21

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_wup.py

### Other
- Update .code2llm_cache/__init___1779357396277625568_994.pkl
- Update .code2llm_cache/core_1779357576743459926_23378.pkl
- Update .code2llm_cache/pyproject_1779357396260771960_1830.pkl
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- ... and 17 more files

## [0.2.32] - 2026-05-21

### Docs
- Update README.md

### Other
- Update poetry.lock

## [0.2.31] - 2026-05-21

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/context.md

### Test
- Update tests/test_testql_watcher.py

### Other
- Update .code2llm_cache/__init___1779357253934266966_994.pkl
- Update .code2llm_cache/pyproject_1779357253932233637_1854.pkl
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 8 more files

## [0.2.30] - 2026-05-21

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_testql_watcher.py
- Update tests/test_wup.py

### Other
- Update .code2llm_cache/__init___1779028001074951992_994.pkl
- Update .code2llm_cache/cli_1779093732279705766_25884.pkl
- Update .code2llm_cache/config_1779093732256705325_5948.pkl
- Update .code2llm_cache/config_1779308006117295178_15299.pkl
- Update .code2llm_cache/goal_1779357051910051242_12256.pkl
- Update .code2llm_cache/pyproject_1779357019376717092_1831.pkl
- Update .code2llm_cache/testql_monitor_1779349049504394378_16110.pkl
- Update .code2llm_cache/testql_watcher_1779349554857917715_30253.pkl
- Update .code2llm_cache/visual_diff_1779349214161559462_17193.pkl
- Update app.doql.less
- ... and 19 more files

## [0.2.29] - 2026-05-17

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.28] - 2026-05-17

### Docs
- Update README.md

### Test
- Update tests/test_testql_monitor.py
- Update tests/test_testql_watcher.py

### Other
- Update uv.lock
- Update wup/testql_monitor.py
- Update wup/testql_watcher.py

## [0.2.27] - 2026-05-16

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_testql_monitor.py
- Update tests/test_testql_watcher.py

### Other
- Update .gitignore
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 18 more files

## [0.2.26] - 2026-05-16

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update tests/test_monitoring_manifest.py
- Update tests/test_testql_monitor.py

### Other
- Update .code2llm_cache/__init___1778834867362150110_994.pkl
- Update .code2llm_cache/cli_1778918000187674386_25505.pkl
- Update .code2llm_cache/config_1778917061530209730_5560.pkl
- Update .code2llm_cache/config_1778917065742082116_14204.pkl
- Update .code2llm_cache/core_1778834388730285362_22557.pkl
- Update .code2llm_cache/monitoring_manifest_1778918028128141262_11166.pkl
- Update .code2llm_cache/pyproject_1778834867353321406_1757.pkl
- Update .code2llm_cache/testql_monitor_1778917195918986170_12093.pkl
- Update .code2llm_cache/testql_watcher_1778917117518359513_24716.pkl
- Update app.doql.less
- ... and 24 more files

## [0.2.25] - 2026-05-15

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/__init___1778575039167989094_994.pkl
- Update .code2llm_cache/c2004_monorepo_demo_1778684557319617197_8257.pkl
- Update .code2llm_cache/ci_cd_integration_1778684557320617207_9296.pkl
- Update .code2llm_cache/main_1778684557319617197_369.pkl
- Update .code2llm_cache/main_1778684557321617217_382.pkl
- Update .code2llm_cache/pyproject_1778690658063351150_1757.pkl
- Update .code2llm_cache/routes_1778684557320617207_301.pkl
- Update .code2llm_cache/routes_1778684557320617207_881.pkl
- Update .code2llm_cache/testql_demo_1778684557320617207_6201.pkl
- Update .code2llm_cache/testql_integration_1778684557324617246_9120.pkl
- ... and 23 more files

## [0.2.22] - 2026-05-12

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.21] - 2026-05-01

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update examples/c2004_monorepo_demo.py
- Update examples/testql_demo.py
- Update examples/testql_integration.py
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- ... and 20 more files

## [0.2.20] - 2026-04-29

### Docs
- Update README.md

### Other
- Update wup/testql_watcher.py

## [0.2.19] - 2026-04-29

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.18] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 14 more files

## [0.2.17] - 2026-04-29

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.16] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md
- Update wup-web/README.md

### Test
- Update tests/test_web_client.py

### Other
- Update .wup-web/events.jsonl
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 31 more files

## [0.2.15] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_testql_watcher.py
- Update tests/test_wup.py

### Other
- Update examples/testql_integration.py
- Update examples/visual_diff_demo.py
- Update uv.lock
- Update wup/config.py

## [0.2.14] - 2026-04-29

### Docs
- Update README.md

### Other
- Update uv.lock
- Update wup/cli.py
- Update wup/config.py
- Update wup/models/config.py
- Update wup/testql_watcher.py
- Update wup/visual_diff.py

## [0.2.13] - 2026-04-29

### Docs
- Update README.md

### Other
- Update uv.lock

## [0.2.12] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update docs/1.md
- Update docs/2.md
- Update docs/3.md
- Update project/README.md
- Update project/context.md

### Other
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- Update project/evolution.toon.yaml
- ... and 9 more files

## [0.2.11] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_testql_watcher.py

### Other
- Update uv.lock
- Update wup/core.py
- Update wup/testql_watcher.py

## [0.2.10] - 2026-04-29

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml
- Update tests/test_testql_watcher.py

### Other
- Update app.doql.less
- Update project.sh
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 12 more files

## [0.2.9] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_e2e.py
- Update tests/test_testql_watcher.py
- Update tests/test_wup.py

### Other
- Update wup/config.py
- Update wup/core.py
- Update wup/models/config.py
- Update wup/testql_watcher.py

## [0.2.8] - 2026-04-29

### Docs
- Update README.md
- Update examples/fastapi-app/README.md
- Update examples/flask-app/README.md

### Test
- Update tests/test_e2e.py

### Other
- Update examples/fastapi-app/Dockerfile
- Update examples/fastapi-app/app/__init__.py
- Update examples/fastapi-app/app/users/__init__.py
- Update examples/fastapi-app/app/users/routes.py
- Update examples/fastapi-app/main.py
- Update examples/fastapi-app/requirements.txt
- Update examples/fastapi-app/wup.yaml
- Update examples/flask-app/Dockerfile
- Update examples/flask-app/app/__init__.py
- Update examples/flask-app/app/auth/__init__.py
- ... and 21 more files

## [0.2.7] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_wup.py

### Other
- Update wup.yaml
- Update wup/core.py

## [0.2.6] - 2026-04-29

### Docs
- Update CHANGELOG.md
- Update README.md

### Test
- Update testql-deps.json

### Other
- Update VERSION
- Update wup.yaml
- Update wup.yaml.example
- Update wup/__init__.py
- Update wup/cli.py
- Update wup/config.py
- Update wup/core.py
- Update wup/dependency_mapper.py
- Update wup/models/config.py
- Update wup/testql_discovery.py

## [0.2.5] - 2026-04-29

### Added
- **Service Coincidence Detection**: Added automatic detection of related services (e.g., shell <-> web)
- **Auto-detection for Services**: Made service paths optional - WUP auto-detects files by service name
- **Service Type Classification**: Added `type` field to services (web/shell/auto) for coincidence detection
- **Coincidence Detection Methods**: Added `detect_service_coincidences()` and `_services_share_domain()` to WupWatcher

### Changed
- **ServiceConfig**: Made `root` and `paths` optional, added `type` field
- **Config Loader**: Updated to handle optional service fields and type classification
- **Infer Service**: Enhanced to auto-detect service files when paths are empty
- **Simplified Configuration**: Service config no longer requires manual path mapping

### Docs
- Updated wup.yaml.example with simplified service configuration examples
- Updated README with auto-detection and coincidence detection documentation

## [0.2.4] - 2026-04-29

### Added
- **TestQL Endpoint Discovery**: Added automatic endpoint discovery from TestQL scenario files
- **testql_discovery Module**: New module to extract API endpoints from .testql.toon.yaml files
- **CLI Command**: Added `wup testql-endpoints` command to discover and map endpoints from TestQL scenarios
- **DependencyMapper Integration**: Added `build_from_testql_scenarios()` method to build dependency maps from TestQL
- **Configuration**: Added `endpoint_discovery` field to TestQLConfig for controlling automatic discovery

### Changed
- **DependencyMapper**: Added import for TestQLEndpointDiscovery
- **TestQLConfig**: Added `endpoint_discovery` boolean field (default: true)
- **Config Loader**: Updated to load `endpoint_discovery` from wup.yaml

### Docs
- Updated wup.yaml.example with endpoint_discovery configuration
- Updated README with testql-endpoints command usage

## [0.2.2] - 2026-04-29

### Docs
- Update README.md

## [0.2.1] - 2026-04-29

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/2.md
- Update docs/3.md

### Test
- Update tests/test_testql_watcher.py
- Update tests/test_wup.py

### Other
- Update VERSION
- Update wup.yaml.example
- Update wup/__init__.py
- Update wup/cli.py
- Update wup/config.py
- Update wup/core.py
- Update wup/models/__init__.py
- Update wup/models/config.py
- Update wup/testql_watcher.py

## [0.2.0] - 2026-04-29

### Added
- **Configuration System**: Added `wup.yaml` configuration file support for declarative project setup
- **Config Models**: Added dataclasses for `WupConfig`, `ServiceConfig`, `WatchConfig`, `TestStrategyConfig`, `TestQLConfig`, and `NotifyConfig`
- **Config Loader**: Added `load_config()`, `save_config()`, and `get_default_config()` functions for configuration management
- **CLI Init Command**: Added `wup init` command to generate default `wup.yaml` configuration files
- **Service Configuration**: Support for per-service test strategies including scope and endpoint limits
- **Watch Configuration**: Configurable watch paths and exclude patterns with glob support
- **Test Strategy Configuration**: Global quick and detail test strategies with debounce, queue, and timeout settings
- **TestQL Integration**: TestQL-specific configuration including scenario directory and extra args
- **Notification Configuration**: Per-service notification settings for HTTP and file-based notifications

### Changed
- **Core Watcher**: Refactored `WupWatcher` to accept and use `WupConfig` instead of hardcoded paths
- **TestQL Watcher**: Updated `TestQLWatcher` to accept `WupConfig` and use configuration values
- **CLI Commands**: Updated all CLI commands to load and use `wup.yaml` configuration
- **Service Inference**: Enhanced service inference to use configured service paths
- **Path Building**: Added `build_watched_paths()` method to construct watch paths from configuration
- **Status Command**: Enhanced `wup status` to display configuration details alongside dependency map

### Dependencies
- Added `pyyaml>=6.0.0` for YAML configuration file support

## [0.1.10] - 2026-04-29

### Docs
- Update README.md

### Other
- Update wup/testql_watcher.py

## [0.1.9] - 2026-04-29

### Docs
- Update README.md

### Other
- Update wup/core.py

## [0.1.8] - 2026-04-29

### Docs
- Update README.md

## [0.1.7] - 2026-04-29

### Docs
- Update README.md
- Update docs/1.md
- Update docs/TESTQL_INTEGRATION.md

### Test
- Update tests/test_wup.py

### Other
- Update .gitignore
- Update deps.json
- Update examples/testql_demo.py
- Update examples/testql_integration.py
- Update wup/__init__.py
- Update wup/cli.py
- Update wup/core.py
- Update wup/dependency_mapper.py

## [0.1.6] - 2026-04-29

### Docs
- Update CHANGELOG.md
- Update README.md

### Test
- Update tests/test_wup.py

### Other
- Update .gitignore
- Update .idea/.gitignore
- Update VERSION
- Update wup/__init__.py
- Update wup/core.py

## [0.1.5] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_wup.py

### Other
- Update policy_blocked.csv
- Update progress.txt
- Update publish.py
- Update publish.txt
- Update pypi_pronounceable.csv
- Update waf/__init__.py
- Update wup/__init__.py
- Update wup/core.py

## [0.1.4] - 2026-04-29

### Docs
- Update README.md

### Other
- Update progress.txt
- Update pypi_pronounceable.csv

## [0.1.3] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_waf.py

### Other
- Update drug/__init__.py
- Update progress.txt
- Update publish.txt
- Update pypi_pronounceable.csv
- Update waf/__init__.py
- Update waf/core.py

## [0.1.2] - 2026-04-29

### Docs
- Update README.md

### Other
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/misc.xml
- Update .idea/modules.xml
- Update .idea/py.iml
- Update .idea/vcs.xml
- Update progress.txt
- Update publish.py
- Update publish.txt
- Update pypi.py
- ... and 1 more files

## [0.1.1] - 2026-04-29

### Docs
- Update README.md

### Test
- Update tests/test_drug.py

### Other
- Update .env.example
- Update .idea/.gitignore
- Update drug/__init__.py
- Update drug/core.py
