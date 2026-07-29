# WUP (What's Up)

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `wup`
- **version**: `0.2.77`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, testql(4), app.doql.less, goal.yaml, .env.example, src(38 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.77;
}

dependencies {
  runtime: "watchdog>=4.0.0, psutil>=5.9.0, rich>=13.0.0, typer>=0.9.0, pyyaml>=6.0";
  dev: "pytest>=7.0.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, uri2wup, dsl2wup, nlp2wup, cli2wup, mcp2wup, rest2wup, httpx>=0.27";
  visual: "playwright>=1.40,<2";
}

entity[name="AdoptCommand"] {
  verb: Literal[!;
  root: string!;
  out: string;
}

entity[name="EndpointsCommand"] {
  verb: Literal[!;
  scenarios_dir: string!;
  out: string!;
  testql_bin: string!;
}

entity[name="GenerateCommand"] {
  verb: Literal[!;
  text: string;
  out: string;
  project: string;
  template: Optional[Literal[;
}

entity[name="HealthCommand"] {
  verb: Literal[!;
  service: string;
  project: string;
}

entity[name="InitCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
}

entity[name="InitCliCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
  scenarios: string!;
  merge: bool!;
  infer_args: bool!;
}

entity[name="MapCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
  framework: string!;
}

entity[name="PatchCommand"] {
  verb: Literal[!;
  target: string!;
  with_path: string!;
  file: string;
  project: string;
}

entity[name="QueryCommand"] {
  verb: Literal[!;
  target: string!;
  file: string;
  format: Literal[!;
  project: string;
}

entity[name="ResolveCommand"] {
  verb: Literal[!;
  text: string!;
  file: string;
  project: string;
}

entity[name="StatusCommand"] {
  verb: Literal[!;
  project: string!;
  deps_file: string!;
  file: string;
  delta_seconds: int!;
  failed_only: bool!;
}

entity[name="SyncCommand"] {
  verb: Literal[!;
  project: string!;
  file: string;
  merge_endpoints: bool!;
}

entity[name="ValidateCommand"] {
  verb: Literal[!;
  path: string;
  project: string;
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="wup"] {
  entry: wup.cli:app;
}

interface[type="web"] {
  type: spa;
  framework: static;
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing sumd...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e .; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e .; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Installation completed!";
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing sumd with dev dependencies...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e ".[dev]"; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e ".[dev]"; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Dev installation completed!";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ -v --tb=short;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests with coverage...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ -v --cov=sumd --cov-report=term-missing --cov-report=json;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=echo "🔍 Running linting with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff check sumd/;
  step-3: run cmd=.venv/bin/python -m ruff check tests/;
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=echo "📝 Formatting code with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff format sumd/;
  step-3: run cmd=.venv/bin/python -m ruff format tests/;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "🧹 Cleaning temporary files...";
  step-2: run cmd=find . -type f -name "*.pyc" -delete;
  step-3: run cmd=find . -type d -name "__pycache__" -delete;
  step-4: run cmd=find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true;
  step-5: run cmd=rm -rf build/ dist/ .coverage htmlcov/ coverage.json;
  step-6: run cmd=echo "✅ Clean completed!";
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to PyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine check dist/*;
  step-6: run cmd=echo "⚡ Ready to upload.";
  step-7: run cmd=.venv/bin/twine upload dist/*;
}

workflow[name="publish-test"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to TestPyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine upload --repository testpypi dist/*;
}

workflow[name="version"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Version information...";
  step-2: run cmd=cat VERSION;
  step-3: run cmd=.venv/bin/python -c "from importlib.metadata import version; print(f'Installed version: {version(\"sumd\")}')";
}

workflow[name="wup:watch"] {
  trigger: manual;
  step-1: run cmd=poetry run wup watch;
}

workflow[name="wup:status"] {
  trigger: manual;
  step-1: run cmd=poetry run wup status;
}

workflow[name="wup:sync"] {
  trigger: manual;
  step-1: run cmd=poetry run wup sync-testql . --write;
}

workflow[name="wup:endpoints"] {
  trigger: manual;
  step-1: run cmd=poetry run wup testql-endpoints;
}

workflow[name="wup:map"] {
  trigger: manual;
  step-1: run cmd=poetry run wup map-deps;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_MODEL, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

### Source Modules

- `wup._ast_detector`
- `wup._base_detector`
- `wup._hash_detector`
- `wup._yaml_detector`
- `wup.anomaly_detector`
- `wup.anomaly_models`
- `wup.aql`
- `wup.assistant`
- `wup.assistant_discovery`
- `wup.assistant_validator`
- `wup.bus`
- `wup.cli`
- `wup.cli_bridge`
- `wup.cli_config_generator`
- `wup.cli_scanner`
- `wup.config`
- `wup.control`
- `wup.core`
- `wup.dependency_mapper`
- `wup.discovery`
- `wup.endpoints`
- `wup.event_store`
- `wup.generate`
- `wup.init_cli`
- `wup.monitoring_manifest`
- `wup.multi`
- `wup.oql`
- `wup.paths`
- `wup.planfile_reporter`
- `wup.status_data`
- `wup.sync`
- `wup.testql_cli_generator`
- `wup.testql_discovery`
- `wup.testql_monitor`
- `wup.testql_watcher`
- `wup.validate`
- `wup.visual_diff`
- `wup.web_client`

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: '3'

tasks:
  wup:watch:
    desc: "Watch project for file changes and run WUP regression tests"
    cmds:
      - poetry run wup watch

  wup:status:
    desc: "Show dependency map status and configuration"
    cmds:
      - poetry run wup status

  wup:sync:
    desc: "Discover monitoring targets and update wup.yaml manifest"
    cmds:
      - poetry run wup sync-testql . --write

  wup:endpoints:
    desc: "Verify TestQL scenarios and discover endpoints"
    cmds:
      - poetry run wup testql-endpoints

  wup:map:
    desc: "Build dependency map from codebase"
    cmds:
      - poetry run wup map-deps

  test:
    desc: "Run WUP pytest test suite"
    cmds:
      - poetry run pytest
```

## Dependencies

### Runtime

```text markpact:deps python
watchdog>=4.0.0
psutil>=5.9.0
rich>=13.0.0
typer>=0.9.0
pyyaml>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
uri2wup
dsl2wup
nlp2wup
cli2wup
mcp2wup
rest2wup
httpx>=0.27
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `wup.testql_watcher` (`wup/testql_watcher.py`)

```python
class BrowserNotifier:  # Send watcher events to browser-facing service and local file
    def __init__(service_url, events_file)  # CC=13 ⚠
    def notify(payload)  # CC=3
class TestQLWatcher:  # WUP watcher running selective TestQL scenarios for changed s
    def __init__(project_root, scenarios_dir, testql_bin, track_dir, browser_service_url, quick_limit, config)  # CC=13 ⚠
    def _normalize_fleet_health_entry()  # CC=7
    def _load_service_health()  # CC=1
    def _record_health_transition()  # CC=6
    def _tokenize_service(service)  # CC=3
    def _get_config_endpoints_for_service(service)  # CC=10 ⚠
    def _to_full_url_for_service(service, endpoint)  # CC=5
    def _resolve_base_url_for_service(service)  # CC=8
    def _resolve_base_url()  # CC=5
    def _to_full_url(endpoint)  # CC=5
    def _discover_scenarios()  # CC=2
    def get_service_config(service_name)  # CC=3
    def _score_scenario(scenario, tokens)  # CC=10 ⚠
    def _get_scored_scenarios(scenarios, tokens, limit)  # CC=4
    def _get_smoke_fallback(svc_type)  # CC=6
    def _resolve_scenario_path(scenario)  # CC=7
    def _testql_trailing_json_ok(result)  # CC=6
    def _health_summary_all_passed(summary)  # CC=5
    def _resolve_stage_config(service, stage)  # CC=6
    def _filter_connect_scenario(scenarios)  # CC=4
    def _select_scenarios_for_service(service)  # CC=9
    def _filter_scenarios_by_type(scenarios, svc_type)  # CC=8
    def _scenario_matches_type(scenario, svc_type)  # CC=4
    def _run_testql(args, timeout)  # CC=4
    def _is_interrupted_result(result)  # CC=4
    def _write_track()  # CC=13 ⚠
    def _quick_timeout()  # CC=3
    def _merge_endpoints(service, endpoints)  # CC=3
    def _run_scenario_quick(service, scenario, merged_endpoints)  # CC=3
    def _should_run_visual_diff()  # CC=4
    def _quick_pass_actions(service, merged_endpoints)  # CC=10 ⚠
    def _quick_probe_limit(service)  # CC=3
    def _quick_probe_timeout()  # CC=3
    def _run_live_http_probes(service, merged_endpoints)  # CC=6
    def _try_parse_json_summary(blob)  # CC=10 ⚠
    def _try_find_line_summary(blob)  # CC=7
    def _summarize_testql_failure(result)  # CC=3
    def _summarize_health_scenario_failure(result)  # CC=8
    def _run_fleet_health_scenario()  # CC=13 ⚠
    def _run_quick_test_no_scenarios(service, merged_endpoints)  # CC=11 ⚠
    def _get_quick_scenarios(service)  # CC=3
    def _run_quick_scenarios_loop(service, scenarios, merged_endpoints)  # CC=3
    def run_quick_test(service, endpoints)  # CC=4
    def _publish_visual_events(service, visual_results)  # CC=6
    def run_detail_test(service, endpoints)  # CC=11 ⚠
    def process_test_queue_once()  # CC=4
    def process_changed_file_once(file_path)  # CC=4
    def _run_periodic_probes_once()  # CC=6
    def _start_periodic_probe_thread()  # CC=3
    def start_background_tasks()  # CC=1
```

### `wup.testql_monitor` (`wup/testql_monitor.py`)

```python
def reject_prefixes_for_config(config)  # CC=3, fan=4
def _parse_api_lines(content, source)  # CC=3, fan=6
def _parse_shell_curl_lines(content, source)  # CC=2, fan=5
def parse_scenario_probes(scenario_path)  # CC=2, fan=4
def _extract_base_url(data)  # CC=4, fan=4
def _parse_endpoint_row(row, base_url, source)  # CC=8, fan=8
def parse_service_map_probes(map_path)  # CC=6, fan=8
def is_monitoring_probe(probe, reject_prefixes)  # CC=10, fan=5 ⚠
def _service_path_patterns(services)  # CC=6, fan=7
def _find_service_by_name(services, name)  # CC=3, fan=1
def _find_service_by_token(services, token)  # CC=3, fan=1
def _assign_by_port_8101(services)  # CC=1, fan=1
def _assign_by_port_8202(services)  # CC=1, fan=1
def _assign_by_port_8100(services, path_lower)  # CC=2, fan=3
def _assign_by_connect_backend(services, path_lower)  # CC=4, fan=3
def _assign_http_probe(probe, services, path_lower, port_map)  # CC=8, fan=6
def _assign_by_longest_token(path_lower, services)  # CC=7, fan=3
def _assign_by_path_prefix(path_lower, services)  # CC=13, fan=2 ⚠
def assign_probe_to_service(probe, services, port_map)  # CC=5, fan=6
class ProbeTarget:  # Single HTTP probe derived from TestQL scenarios or service m
    def probe(timeout_s)  # CC=5
class _ProbeAccumulator:  # Deduplicated probe collector for discover_probes_by_service.
    def __init__(services)  # CC=2
    def add(service, probe)  # CC=3
class TestQLMonitor:  # Build and run live probes from TestQL scenarios + WUP config
    def __init__(project_root, config)  # CC=2
    def _is_monitoring_probe(probe)  # CC=1
    def _load_dot_env()  # CC=7
    def _build_port_map()  # CC=6
    def _service_map_paths()  # CC=3
    def _add_hardware_usb_module_endpoints(accumulator)  # CC=13 ⚠
    def _add_config_endpoints(accumulator)  # CC=11 ⚠
    def _add_scenario_probes(accumulator, port_map)  # CC=5
    def _add_service_map_probes(accumulator, port_map)  # CC=5
    def discover_probes_by_service()  # CC=2
    def _resolve_base_url_for_service(service)  # CC=8
    def _probeable_url(path, base)  # CC=4
    def probes_for_service(service, extra_paths)  # CC=9
    def _sort_probes_for_live(probes, service)  # CC=1
    def run_probes(service, probes)  # CC=5
    def suggested_endpoints_by_service()  # CC=5
    def _resolve_base_url()  # CC=4
    def _join_base(base, path)  # CC=5
```

### `wup.core` (`wup/core.py`)

```python
class WupWatcher:  # Intelligent file watcher for regression testing.
    def __init__(project_root, deps_file, cpu_throttle, debounce_seconds, test_cooldown_seconds, config)  # CC=1
    def _to_relative_path(file_path)  # CC=2
    def _service_name_prefixes()  # CC=4
    def infer_service(file_path)  # CC=12 ⚠
    def _is_coincident_pair(type_a, type_b)  # CC=6
    def detect_service_coincidences(changed_service)  # CC=9
    def _services_share_domain(service1, service2)  # CC=1
    def get_service_config(service_name)  # CC=3
    def should_test(service)  # CC=1
    def schedule_quick_test(service)  # CC=3
    def schedule_detail_test(service)  # CC=1
    def process_test_queue_once()  # CC=7
    def cpu_ok()  # CC=2
    def run_quick_test(target)  # CC=6
    def run_detail_test(target)  # CC=10 ⚠
    def test_loop()  # CC=2
    def should_watch_file(file_path)  # CC=3
    def _path_matches_exclude_pattern(rel_path, pattern)  # CC=5
    def _is_file_ignored(rel_path)  # CC=11 ⚠
    def _notify_all_configured_services(rel_path)  # CC=4
    def on_file_change(file_path)  # CC=11 ⚠
    def build_watched_paths()  # CC=6
    def _create_and_start_observer(event_handler, watch_paths)  # CC=5
    def start_background_tasks()  # CC=1
    def prepare_observer(watch_paths)  # CC=5
    def start_watching(watch_paths)  # CC=4
    def create_status_table()  # CC=3
    def run_with_dashboard()  # CC=5
class WupEventHandler:  # File system event handler for WUP watcher.
    def __init__(watcher)  # CC=1
    def on_modified(event)  # CC=2
    def on_created(event)  # CC=2
    def on_deleted(event)  # CC=2
```

### `wup.visual_diff` (`wup/visual_diff.py`)

```python
def _playwright_available()  # CC=3, fan=0
def _warn_playwright_missing()  # CC=2, fan=1
def _chromium_launch_options(headless)  # CC=7, fan=4
def _fetch_dom_snapshot(url, max_depth, headless, error_selectors, page_settle_ms)  # CC=10, fan=16 ⚠
def _detect_content_issues(snapshot, cfg)  # CC=6, fan=5
def _page_slug(url)  # CC=2, fan=3
def _short_url(url)  # CC=3, fan=1
def _compact_error_message(message, max_len)  # CC=3, fan=3
def _sample_list(items, limit)  # CC=3, fan=2
def _looks_like_visual_page(url)  # CC=7, fan=4
def _snapshot_path(snapshot_dir, service, url)  # CC=1, fan=2
def _load_snapshot(file_path)  # CC=3, fan=3
def _save_snapshot(file_path, snapshot)  # CC=1, fan=3
def _node_signature(node, depth)  # CC=3, fan=3
def _flatten(node, depth, max_depth)  # CC=4, fan=4
def _diff_snapshots(old, new, max_depth, threshold_added, threshold_removed, threshold_changed)  # CC=11, fan=5 ⚠
def _resolve_base_url(cfg)  # CC=3, fan=2
class VisualDiffer:  # Triggered by TestQLWatcher after a file change.
    def __init__(project_root, cfg)  # CC=2
    def _pages_for_service(target)  # CC=11 ⚠
    def _categorize_page_result(service, url, result, ok_urls, new_urls, error_results, pending_notices)  # CC=7
    def _print_scan_summary(service, ok_urls, new_urls, error_results)  # CC=8
    def run_for_service(target)  # CC=10 ⚠
    def _build_progress(service, total)  # CC=3
    def _check_page(service, url)  # CC=10 ⚠
    def _write_diff_event(service, url, result)  # CC=1
    def get_recent_diffs(seconds)  # CC=7
```

### `wup.cli` (`wup/cli.py`)

```python
def _load_watch_config(project_path, config_path, probe_interval, mode)  # CC=4, fan=3
def _print_watch_header(wup_config, cpu_throttle, debounce, cooldown, config_path)  # CC=3, fan=1
def _refresh_monitoring_manifest(project_path, wup_config, cfg_path)  # CC=3, fan=3
def _create_watcher(mode, project_path, deps_file, cpu_throttle, debounce, cooldown, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, config)  # CC=2, fan=5
def _is_project_dir(path)  # CC=2, fan=2
def _discover_projects(root)  # CC=6, fan=5
def _resolve_project_paths(projects, discover)  # CC=8, fan=9
def _build_project_watcher(project_path, config_path)  # CC=9, fan=11
def watch(projects, deps_file, cpu_throttle, debounce, cooldown, dashboard, mode, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, probe_interval, discover, config)  # CC=13, fan=14 ⚠
def _auto_generate_config(project_path, mode)  # CC=3, fan=9
def map_deps(project, output, framework, config)  # CC=12, fan=16 ⚠
def _add_failing_services_lines(lines, health_state_path, failed_only, watch)  # CC=13, fan=10 ⚠
def _add_delta_events_lines(lines, health_events_path, delta_seconds, watch, ts)  # CC=14, fan=10 ⚠
def _add_monitoring_manifest_lines(lines, config_path, project_path)  # CC=11, fan=11 ⚠
def _add_visual_diff_lines(lines, wup_config, project_path, delta_seconds, watch)  # CC=9, fan=7
def _build_status_panel(ts, project_path, wup_config, config_path, health_state_path, health_events_path, delta_seconds, failed_only, watch)  # CC=1, fan=9
def status(deps_file, config, delta_seconds, failed_only, watch, interval, json_out)  # CC=8, fan=18
def oql(query, project, json_out)  # CC=11, fan=21 ⚠
def aql(file, rule, json_out)  # CC=9, fan=11
def init(project, output)  # CC=5, fan=11
def testql_endpoints(scenarios_dir, output, testql_bin)  # CC=6, fan=16
def sync_testql(project, write, merge_endpoints, config)  # CC=10, fan=19 ⚠
def assistant(quick, template, project)  # CC=8, fan=13
def version()  # CC=1, fan=2
def init_cli(project, output_config, output_scenarios, merge, infer_args)  # CC=9, fan=13
```

## Call Graph

*290 nodes · 307 edges · 57 modules · CC̄=4.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_set_body` *(in packages.dsl2wup.src.dsl2wup.pb_codec)* | 16 ⚠ | 1 | 88 | **89** |
| `show_ci_cd_demo` *(in examples.ci_cd_integration)* | 2 | 1 | 69 | **70** |
| `show_webhook_demo` *(in examples.webhook_notifications)* | 4 | 1 | 68 | **69** |
| `_run_with_mock_services` *(in examples.testql_demo)* | 6 | 2 | 60 | **62** |
| `query_uri` *(in packages.uri2wup.src.uri2wup.query)* | 23 ⚠ | 3 | 49 | **52** |
| `_parse_visual_diff_config` *(in wup.config)* | 6 | 1 | 48 | **49** |
| `map_deps` *(in wup.cli)* | 12 ⚠ | 0 | 45 | **45** |
| `parse_line` *(in packages.dsl2wup.src.dsl2wup.grammar)* | 59 ⚠ | 6 | 37 | **43** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# generated in 0.16s
# nodes: 290 | edges: 307 | modules: 57
# CC̄=4.7

HUBS[20]:
  packages.dsl2wup.src.dsl2wup.pb_codec._set_body
    CC=16  in:1  out:88  total:89
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  packages.uri2wup.src.uri2wup.query.query_uri
    CC=23  in:3  out:49  total:52
  wup.config._parse_visual_diff_config
    CC=6  in:1  out:48  total:49
  wup.cli.map_deps
    CC=12  in:0  out:45  total:45
  packages.dsl2wup.src.dsl2wup.grammar.parse_line
    CC=59  in:6  out:37  total:43
  wup.cli.testql_endpoints
    CC=6  in:0  out:43  total:43
  packages.dsl2wup.src.dsl2wup.codegen.generate_models
    CC=15  in:1  out:42  total:43
  packages.rest2wup.src.rest2wup.app.create_app
    CC=1  in:1  out:42  total:43
  wup.cli.sync_testql
    CC=10  in:0  out:38  total:38
  wup.aql.parse_rule
    CC=18  in:1  out:33  total:34
  packages.dsl2wup.src.dsl2wup.events.EventStore.append
    CC=3  in:0  out:33  total:33
  packages.dsl2wup.src.dsl2wup.grammar.to_text
    CC=11  in:14  out:19  total:33
  packages.dsl2wup.src.dsl2wup.bus.dispatch
    CC=6  in:16  out:15  total:31
  wup.cli.status
    CC=8  in:0  out:31  total:31
  wup.cli._add_delta_events_lines
    CC=14  in:1  out:29  total:30
  wup.config._parse_testql_config
    CC=2  in:1  out:28  total:29
  packages.dsl2wup.src.dsl2wup.grammar.pick_flag
    CC=3  in:27  out:2  total:29

MODULES:
  examples.c2004_monorepo_demo  [5 funcs]
    _analyze_module  CC=3  out:9
    _analyze_module_structure  CC=7  out:10
    _discover_modules  CC=5  out:8
    analyze_monorepo  CC=2  out:26
    main  CC=2  out:2
  examples.ci_cd_integration  [4 funcs]
    generate_github_actions  CC=1  out:9
    generate_gitlab_ci  CC=3  out:10
    main  CC=3  out:7
    show_ci_cd_demo  CC=2  out:69
  examples.testql_demo  [4 funcs]
    _build_mock_services  CC=5  out:4
    _run_with_mock_services  CC=6  out:60
    simulate_testql_analysis  CC=2  out:18
    simulate_with_mock_data  CC=1  out:12
  examples.visual_diff_demo  [8 funcs]
    _make_dom  CC=2  out:1
    demo_config_yaml_round_trip  CC=6  out:16
    demo_diff_algorithm  CC=3  out:16
    demo_disabled_is_noop  CC=2  out:11
    demo_live_page  CC=3  out:14
    demo_page_slug  CC=2  out:6
    demo_snapshot_persistence  CC=3  out:26
    main  CC=2  out:15
  examples.webhook_notifications  [2 funcs]
    main  CC=3  out:7
    show_webhook_demo  CC=4  out:68
  packages.cli2wup.src.cli2wup.cli  [1 funcs]
    run_shell  CC=9  out:12
  packages.dsl2wup.src.dsl2wup.bus  [5 funcs]
    _bytes_to_cmd  CC=3  out:5
    _dispatch_cmd  CC=5  out:12
    dispatch  CC=6  out:15
    execute_dsl  CC=4  out:6
    execute_dsl_line  CC=1  out:1
  packages.dsl2wup.src.dsl2wup.cli  [3 funcs]
    _main_legacy  CC=9  out:20
    _main_subcommand  CC=9  out:28
    main  CC=4  out:2
  packages.dsl2wup.src.dsl2wup.codec  [4 funcs]
    decode_protobuf  CC=1  out:1
    encode_protobuf  CC=1  out:1
    encode_text  CC=2  out:2
    roundtrip_text  CC=3  out:6
  packages.dsl2wup.src.dsl2wup.codegen  [2 funcs]
    generate_models  CC=15  out:42
    main  CC=1  out:4
  packages.dsl2wup.src.dsl2wup.events  [2 funcs]
    append  CC=3  out:33
    default_event_store  CC=2  out:6
  packages.dsl2wup.src.dsl2wup.grammar  [4 funcs]
    parse_line  CC=59  out:37
    pick_flag  CC=3  out:2
    split_command  CC=4  out:4
    to_text  CC=11  out:19
  packages.dsl2wup.src.dsl2wup.handlers.command  [9 funcs]
    _project_root  CC=2  out:4
    _read_content  CC=1  out:3
    handle_from_tokens  CC=16  out:21
    handle_generate  CC=4  out:11
    handle_init  CC=4  out:11
    handle_init_cli  CC=4  out:12
    handle_map  CC=7  out:20
    handle_patch  CC=3  out:13
    handle_sync  CC=4  out:12
  packages.dsl2wup.src.dsl2wup.handlers.query  [7 funcs]
    _project_root  CC=2  out:4
    handle_endpoints  CC=4  out:10
    handle_health  CC=5  out:12
    handle_query  CC=4  out:10
    handle_resolve  CC=4  out:9
    handle_status  CC=4  out:11
    handle_validate  CC=5  out:13
  packages.dsl2wup.src.dsl2wup.pb_codec  [8 funcs]
    _set_body  CC=16  out:88
    decode_protobuf  CC=1  out:3
    decode_protobuf_to_text  CC=1  out:2
    encode_protobuf  CC=1  out:6
    encode_result_protobuf  CC=1  out:2
    encode_text_to_protobuf  CC=2  out:3
    envelope_to_dict  CC=58  out:5
    result_to_pb  CC=4  out:4
  packages.dsl2wup.src.dsl2wup.schema_registry  [6 funcs]
    _load_schemas  CC=3  out:9
    _schema_verb_for  CC=1  out:3
    all_schemas  CC=1  out:2
    schema_for_verb  CC=1  out:3
    validate_command_dict  CC=3  out:7
    validate_schema_registry  CC=13  out:19
  packages.mcp2wup.src.mcp2wup.cli  [1 funcs]
    main  CC=4  out:6
  packages.mcp2wup.src.mcp2wup.server  [4 funcs]
    __post_init__  CC=1  out:3
    _require_fastmcp  CC=2  out:1
    create_server  CC=1  out:1
    run_server  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.apply  [3 funcs]
    _intent  CC=21  out:11
    apply_nl  CC=5  out:6
    to_dsl  CC=24  out:20
  packages.nlp2wup.src.nlp2wup.generate  [2 funcs]
    _extract_template  CC=3  out:1
    generate_from_nl  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.validate  [1 funcs]
    validate_wup_config  CC=1  out:1
  packages.rest2wup.src.rest2wup.app  [1 funcs]
    create_app  CC=1  out:42
  packages.rest2wup.src.rest2wup.cli  [1 funcs]
    main  CC=4  out:9
  packages.uri2wup.src.uri2wup.decode  [2 funcs]
    _dict_to_dsl  CC=7  out:7
    decode_uri  CC=20  out:23
  packages.uri2wup.src.uri2wup.nlp2uri  [2 funcs]
    best_uri  CC=2  out:1
    nlp2uri  CC=4  out:9
  packages.uri2wup.src.uri2wup.patch  [2 funcs]
    _resolve_config_path  CC=4  out:7
    patch_uri  CC=17  out:21
  packages.uri2wup.src.uri2wup.query  [3 funcs]
    _extract_block  CC=14  out:21
    _resolve_config_path  CC=4  out:7
    query_uri  CC=23  out:49
  packages.uri2wup.src.uri2wup.uri  [6 funcs]
    _decode  CC=2  out:1
    _encode  CC=1  out:1
    is_wup_uri  CC=1  out:2
    parse_wup_uri  CC=7  out:14
    uri_for_block  CC=7  out:9
    uri_for_cmd  CC=7  out:13
  scripts.run_probe_smoke  [6 funcs]
    check_manifest_stale_probes  CC=2  out:3
    main  CC=3  out:13
    print_probe_plan  CC=6  out:13
    print_service_health  CC=2  out:6
    run_live_http_probes  CC=4  out:4
    run_quick_testql_dryrun  CC=3  out:4
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.aql  [10 funcs]
    check_file  CC=11  out:21
    _coerce_number  CC=2  out:1
    _compare  CC=4  out:3
    _length_of  CC=2  out:2
    _passes  CC=11  out:9
    _resolve_path  CC=13  out:13
    _split_severity  CC=4  out:5
    _tokenize  CC=4  out:11
    _type_name  CC=7  out:5
    parse_rule  CC=18  out:33
  wup.assistant  [5 funcs]
    _auto_detect_services  CC=1  out:1
    _detect_framework  CC=1  out:1
    _detect_service_type  CC=1  out:1
    _generate_suggestions  CC=1  out:1
    _validate_config  CC=1  out:1
  wup.assistant_discovery  [3 funcs]
    auto_detect_services  CC=7  out:9
    detect_framework  CC=7  out:4
    detect_service_type  CC=11  out:9
  wup.assistant_validator  [2 funcs]
    generate_suggestions  CC=6  out:5
    validate_config  CC=9  out:9
  wup.cli  [20 funcs]
    _add_delta_events_lines  CC=14  out:29
    _add_failing_services_lines  CC=13  out:23
    _add_monitoring_manifest_lines  CC=11  out:24
    _add_visual_diff_lines  CC=9  out:18
    _auto_generate_config  CC=3  out:13
    _build_project_watcher  CC=9  out:15
    _build_status_panel  CC=1  out:9
    _create_watcher  CC=2  out:6
    _discover_projects  CC=6  out:7
    _is_project_dir  CC=2  out:2
  wup.cli_bridge  [8 funcs]
    run_endpoints  CC=1  out:1
    run_generate  CC=1  out:1
    run_init  CC=1  out:1
    run_init_cli  CC=1  out:1
    run_map_deps  CC=1  out:1
    run_status  CC=1  out:1
    run_sync  CC=1  out:1
    run_validate  CC=1  out:1
  wup.cli_config_generator  [1 funcs]
    generate  CC=4  out:5
  wup.config  [19 funcs]
    _load_dotenv  CC=10  out:10
    _normalize_testql_extra_args  CC=5  out:10
    _normalize_testql_timeout  CC=3  out:4
    _parse_planfile_config  CC=5  out:15
    _parse_project_config  CC=2  out:5
    _parse_semcod_tools_config  CC=9  out:23
    _parse_services_config  CC=3  out:23
    _parse_strategy_config  CC=1  out:4
    _parse_testql_config  CC=2  out:28
    _parse_testql_extra_args  CC=5  out:8
  wup.control  [12 funcs]
    _result_dict  CC=1  out:2
    dispatch_command  CC=1  out:1
    dispatch_endpoints  CC=1  out:1
    dispatch_generate  CC=3  out:1
    dispatch_health  CC=2  out:2
    dispatch_init  CC=1  out:1
    dispatch_init_cli  CC=3  out:1
    dispatch_map  CC=1  out:1
    dispatch_query  CC=3  out:5
    dispatch_status  CC=4  out:1
  wup.core  [1 funcs]
    __init__  CC=7  out:18
  wup.dependency_mapper  [2 funcs]
    _detect_framework  CC=2  out:2
    build_from_codebase  CC=6  out:7
  wup.discovery  [2 funcs]
    detect_frameworks  CC=3  out:1
    discover_endpoints  CC=7  out:6
  wup.endpoints  [1 funcs]
    discover_testql_endpoints  CC=5  out:26
  wup.generate  [2 funcs]
    _detect_template  CC=4  out:2
    generate_wup_config  CC=8  out:20
  wup.init_cli  [1 funcs]
    setup_cli_project  CC=9  out:26
  wup.monitoring_manifest  [18 funcs]
    _artifact_row  CC=4  out:5
    _build_docker_rows  CC=5  out:3
    _build_scenario_rows  CC=5  out:8
    _build_wup_service_dicts  CC=3  out:2
    _extract_healthcheck_test  CC=6  out:7
    _extract_service_from_spec  CC=7  out:12
    _load_compose_yaml  CC=5  out:5
    _map_docker_to_wup_service  CC=14  out:11
    _parse_port_mapping  CC=5  out:4
    _semcod_summary_lines  CC=5  out:9
  wup.oql  [9 funcs]
    matches  CC=1  out:2
    _event_rows  CC=5  out:7
    _service_rows  CC=6  out:9
    execute  CC=13  out:12
    _coerce_number  CC=2  out:1
    _compare  CC=14  out:8
    _parse_conditions  CC=7  out:10
    _tokenize  CC=2  out:7
    parse  CC=11  out:19
  wup.paths  [2 funcs]
    health_events_path  CC=1  out:1
    health_state_path  CC=1  out:1
  wup.status_data  [4 funcs]
    _load_json  CC=4  out:4
    _load_manifest  CC=4  out:2
    _summarize_deps  CC=4  out:8
    collect_status_snapshot  CC=12  out:23
  wup.sync  [2 funcs]
    _merge_endpoints  CC=6  out:14
    sync_testql_manifest  CC=9  out:16
  wup.testing.handlers.event_handlers  [1 funcs]
    register_testing_event_handlers  CC=1  out:3
  wup.testing.handlers.health_handlers  [1 funcs]
    register_health_handlers  CC=1  out:3
  wup.testql_monitor  [25 funcs]
    __init__  CC=2  out:3
    _add_config_endpoints  CC=11  out:14
    _add_scenario_probes  CC=5  out:5
    _add_service_map_probes  CC=5  out:5
    _build_port_map  CC=6  out:13
    _is_monitoring_probe  CC=1  out:1
    _assign_by_connect_backend  CC=4  out:4
    _assign_by_longest_token  CC=7  out:5
    _assign_by_path_prefix  CC=13  out:7
    _assign_by_port_8100  CC=2  out:3
  wup.testql_watcher  [2 funcs]
    __init__  CC=13  out:17
    _get_config_endpoints_for_service  CC=10  out:7
  wup.validate  [1 funcs]
    validate_wup_file  CC=8  out:15
  wup.visual_diff  [23 funcs]
    __init__  CC=2  out:3
    _categorize_page_result  CC=7  out:12
    _check_page  CC=10  out:19
    _pages_for_service  CC=11  out:8
    _print_scan_summary  CC=8  out:13
    _write_diff_event  CC=1  out:6
    run_for_service  CC=10  out:22
    _compact_error_message  CC=3  out:3
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=5  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  packages.cli2wup.src.cli2wup.cli.run_shell → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.rest2wup.src.rest2wup.cli.main → packages.rest2wup.src.rest2wup.app.create_app
  packages.rest2wup.src.rest2wup.app.create_app → packages.dsl2wup.src.dsl2wup.schema_registry.schema_for_verb
  packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri → packages.uri2wup.src.uri2wup.uri.uri_for_block
  packages.uri2wup.src.uri2wup.nlp2uri.best_uri → packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri
  packages.uri2wup.src.uri2wup.query._resolve_config_path → wup.config.find_config_file
  packages.uri2wup.src.uri2wup.query._extract_block → wup.paths.health_state_path
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.query._resolve_config_path
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.query._extract_block
  packages.uri2wup.src.uri2wup.decode.decode_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.decode.decode_uri → packages.uri2wup.src.uri2wup.decode._dict_to_dsl
  packages.uri2wup.src.uri2wup.uri.uri_for_cmd → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.uri_for_block → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri._decode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri.is_wup_uri
  packages.uri2wup.src.uri2wup.patch._resolve_config_path → wup.config.find_config_file
  packages.uri2wup.src.uri2wup.patch.patch_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.patch.patch_uri → packages.uri2wup.src.uri2wup.patch._resolve_config_path
  packages.nlp2wup.src.nlp2wup.validate.validate_wup_config → wup.validate.validate_wup_file
  packages.nlp2wup.src.nlp2wup.generate.generate_from_nl → wup.generate.generate_wup_config
  packages.nlp2wup.src.nlp2wup.generate.generate_from_nl → packages.nlp2wup.src.nlp2wup.generate._extract_template
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.nlp2wup.src.nlp2wup.apply._intent
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.uri2wup.src.uri2wup.nlp2uri.best_uri
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.nlp2wup.src.nlp2wup.apply.to_dsl
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.dsl2wup.src.dsl2wup.bus.dispatch
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.uri2wup.src.uri2wup.nlp2uri.best_uri
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.nlp2wup.src.nlp2wup.apply._intent
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.handlers.command.handle_from_tokens
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.events.default_event_store
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.pb_codec.decode_protobuf
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.parse_line
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line → packages.dsl2wup.src.dsl2wup.bus.dispatch
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.dsl2wup.src.dsl2wup.cli._main_legacy → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.dsl2wup.src.dsl2wup.cli._main_legacy → packages.dsl2wup.src.dsl2wup.bus.execute_dsl
  packages.dsl2wup.src.dsl2wup.cli._main_subcommand → packages.dsl2wup.src.dsl2wup.schema_registry.validate_schema_registry
  packages.dsl2wup.src.dsl2wup.cli.main → packages.dsl2wup.src.dsl2wup.cli._main_legacy
  packages.dsl2wup.src.dsl2wup.cli.main → packages.dsl2wup.src.dsl2wup.cli._main_subcommand
  packages.dsl2wup.src.dsl2wup.events.EventStore.append → packages.dsl2wup.src.dsl2wup.pb_codec.encode_protobuf
  packages.dsl2wup.src.dsl2wup.pb_codec.encode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec._set_body
  packages.dsl2wup.src.dsl2wup.pb_codec.decode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec.envelope_to_dict
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (3)

**`CLI Smoke Tests`**

**`wup Command Tests`**

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**
- assert `test_type == "quick"`
- assert `service_name == "users"`
- assert `inferred == "users"`

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# generated in 0.16s
# nodes: 290 | edges: 307 | modules: 57
# CC̄=4.7

HUBS[20]:
  packages.dsl2wup.src.dsl2wup.pb_codec._set_body
    CC=16  in:1  out:88  total:89
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  packages.uri2wup.src.uri2wup.query.query_uri
    CC=23  in:3  out:49  total:52
  wup.config._parse_visual_diff_config
    CC=6  in:1  out:48  total:49
  wup.cli.map_deps
    CC=12  in:0  out:45  total:45
  packages.dsl2wup.src.dsl2wup.grammar.parse_line
    CC=59  in:6  out:37  total:43
  wup.cli.testql_endpoints
    CC=6  in:0  out:43  total:43
  packages.dsl2wup.src.dsl2wup.codegen.generate_models
    CC=15  in:1  out:42  total:43
  packages.rest2wup.src.rest2wup.app.create_app
    CC=1  in:1  out:42  total:43
  wup.cli.sync_testql
    CC=10  in:0  out:38  total:38
  wup.aql.parse_rule
    CC=18  in:1  out:33  total:34
  packages.dsl2wup.src.dsl2wup.events.EventStore.append
    CC=3  in:0  out:33  total:33
  packages.dsl2wup.src.dsl2wup.grammar.to_text
    CC=11  in:14  out:19  total:33
  packages.dsl2wup.src.dsl2wup.bus.dispatch
    CC=6  in:16  out:15  total:31
  wup.cli.status
    CC=8  in:0  out:31  total:31
  wup.cli._add_delta_events_lines
    CC=14  in:1  out:29  total:30
  wup.config._parse_testql_config
    CC=2  in:1  out:28  total:29
  packages.dsl2wup.src.dsl2wup.grammar.pick_flag
    CC=3  in:27  out:2  total:29

MODULES:
  examples.c2004_monorepo_demo  [5 funcs]
    _analyze_module  CC=3  out:9
    _analyze_module_structure  CC=7  out:10
    _discover_modules  CC=5  out:8
    analyze_monorepo  CC=2  out:26
    main  CC=2  out:2
  examples.ci_cd_integration  [4 funcs]
    generate_github_actions  CC=1  out:9
    generate_gitlab_ci  CC=3  out:10
    main  CC=3  out:7
    show_ci_cd_demo  CC=2  out:69
  examples.testql_demo  [4 funcs]
    _build_mock_services  CC=5  out:4
    _run_with_mock_services  CC=6  out:60
    simulate_testql_analysis  CC=2  out:18
    simulate_with_mock_data  CC=1  out:12
  examples.visual_diff_demo  [8 funcs]
    _make_dom  CC=2  out:1
    demo_config_yaml_round_trip  CC=6  out:16
    demo_diff_algorithm  CC=3  out:16
    demo_disabled_is_noop  CC=2  out:11
    demo_live_page  CC=3  out:14
    demo_page_slug  CC=2  out:6
    demo_snapshot_persistence  CC=3  out:26
    main  CC=2  out:15
  examples.webhook_notifications  [2 funcs]
    main  CC=3  out:7
    show_webhook_demo  CC=4  out:68
  packages.cli2wup.src.cli2wup.cli  [1 funcs]
    run_shell  CC=9  out:12
  packages.dsl2wup.src.dsl2wup.bus  [5 funcs]
    _bytes_to_cmd  CC=3  out:5
    _dispatch_cmd  CC=5  out:12
    dispatch  CC=6  out:15
    execute_dsl  CC=4  out:6
    execute_dsl_line  CC=1  out:1
  packages.dsl2wup.src.dsl2wup.cli  [3 funcs]
    _main_legacy  CC=9  out:20
    _main_subcommand  CC=9  out:28
    main  CC=4  out:2
  packages.dsl2wup.src.dsl2wup.codec  [4 funcs]
    decode_protobuf  CC=1  out:1
    encode_protobuf  CC=1  out:1
    encode_text  CC=2  out:2
    roundtrip_text  CC=3  out:6
  packages.dsl2wup.src.dsl2wup.codegen  [2 funcs]
    generate_models  CC=15  out:42
    main  CC=1  out:4
  packages.dsl2wup.src.dsl2wup.events  [2 funcs]
    append  CC=3  out:33
    default_event_store  CC=2  out:6
  packages.dsl2wup.src.dsl2wup.grammar  [4 funcs]
    parse_line  CC=59  out:37
    pick_flag  CC=3  out:2
    split_command  CC=4  out:4
    to_text  CC=11  out:19
  packages.dsl2wup.src.dsl2wup.handlers.command  [9 funcs]
    _project_root  CC=2  out:4
    _read_content  CC=1  out:3
    handle_from_tokens  CC=16  out:21
    handle_generate  CC=4  out:11
    handle_init  CC=4  out:11
    handle_init_cli  CC=4  out:12
    handle_map  CC=7  out:20
    handle_patch  CC=3  out:13
    handle_sync  CC=4  out:12
  packages.dsl2wup.src.dsl2wup.handlers.query  [7 funcs]
    _project_root  CC=2  out:4
    handle_endpoints  CC=4  out:10
    handle_health  CC=5  out:12
    handle_query  CC=4  out:10
    handle_resolve  CC=4  out:9
    handle_status  CC=4  out:11
    handle_validate  CC=5  out:13
  packages.dsl2wup.src.dsl2wup.pb_codec  [8 funcs]
    _set_body  CC=16  out:88
    decode_protobuf  CC=1  out:3
    decode_protobuf_to_text  CC=1  out:2
    encode_protobuf  CC=1  out:6
    encode_result_protobuf  CC=1  out:2
    encode_text_to_protobuf  CC=2  out:3
    envelope_to_dict  CC=58  out:5
    result_to_pb  CC=4  out:4
  packages.dsl2wup.src.dsl2wup.schema_registry  [6 funcs]
    _load_schemas  CC=3  out:9
    _schema_verb_for  CC=1  out:3
    all_schemas  CC=1  out:2
    schema_for_verb  CC=1  out:3
    validate_command_dict  CC=3  out:7
    validate_schema_registry  CC=13  out:19
  packages.mcp2wup.src.mcp2wup.cli  [1 funcs]
    main  CC=4  out:6
  packages.mcp2wup.src.mcp2wup.server  [4 funcs]
    __post_init__  CC=1  out:3
    _require_fastmcp  CC=2  out:1
    create_server  CC=1  out:1
    run_server  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.apply  [3 funcs]
    _intent  CC=21  out:11
    apply_nl  CC=5  out:6
    to_dsl  CC=24  out:20
  packages.nlp2wup.src.nlp2wup.generate  [2 funcs]
    _extract_template  CC=3  out:1
    generate_from_nl  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.validate  [1 funcs]
    validate_wup_config  CC=1  out:1
  packages.rest2wup.src.rest2wup.app  [1 funcs]
    create_app  CC=1  out:42
  packages.rest2wup.src.rest2wup.cli  [1 funcs]
    main  CC=4  out:9
  packages.uri2wup.src.uri2wup.decode  [2 funcs]
    _dict_to_dsl  CC=7  out:7
    decode_uri  CC=20  out:23
  packages.uri2wup.src.uri2wup.nlp2uri  [2 funcs]
    best_uri  CC=2  out:1
    nlp2uri  CC=4  out:9
  packages.uri2wup.src.uri2wup.patch  [2 funcs]
    _resolve_config_path  CC=4  out:7
    patch_uri  CC=17  out:21
  packages.uri2wup.src.uri2wup.query  [3 funcs]
    _extract_block  CC=14  out:21
    _resolve_config_path  CC=4  out:7
    query_uri  CC=23  out:49
  packages.uri2wup.src.uri2wup.uri  [6 funcs]
    _decode  CC=2  out:1
    _encode  CC=1  out:1
    is_wup_uri  CC=1  out:2
    parse_wup_uri  CC=7  out:14
    uri_for_block  CC=7  out:9
    uri_for_cmd  CC=7  out:13
  scripts.run_probe_smoke  [6 funcs]
    check_manifest_stale_probes  CC=2  out:3
    main  CC=3  out:13
    print_probe_plan  CC=6  out:13
    print_service_health  CC=2  out:6
    run_live_http_probes  CC=4  out:4
    run_quick_testql_dryrun  CC=3  out:4
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.aql  [10 funcs]
    check_file  CC=11  out:21
    _coerce_number  CC=2  out:1
    _compare  CC=4  out:3
    _length_of  CC=2  out:2
    _passes  CC=11  out:9
    _resolve_path  CC=13  out:13
    _split_severity  CC=4  out:5
    _tokenize  CC=4  out:11
    _type_name  CC=7  out:5
    parse_rule  CC=18  out:33
  wup.assistant  [5 funcs]
    _auto_detect_services  CC=1  out:1
    _detect_framework  CC=1  out:1
    _detect_service_type  CC=1  out:1
    _generate_suggestions  CC=1  out:1
    _validate_config  CC=1  out:1
  wup.assistant_discovery  [3 funcs]
    auto_detect_services  CC=7  out:9
    detect_framework  CC=7  out:4
    detect_service_type  CC=11  out:9
  wup.assistant_validator  [2 funcs]
    generate_suggestions  CC=6  out:5
    validate_config  CC=9  out:9
  wup.cli  [20 funcs]
    _add_delta_events_lines  CC=14  out:29
    _add_failing_services_lines  CC=13  out:23
    _add_monitoring_manifest_lines  CC=11  out:24
    _add_visual_diff_lines  CC=9  out:18
    _auto_generate_config  CC=3  out:13
    _build_project_watcher  CC=9  out:15
    _build_status_panel  CC=1  out:9
    _create_watcher  CC=2  out:6
    _discover_projects  CC=6  out:7
    _is_project_dir  CC=2  out:2
  wup.cli_bridge  [8 funcs]
    run_endpoints  CC=1  out:1
    run_generate  CC=1  out:1
    run_init  CC=1  out:1
    run_init_cli  CC=1  out:1
    run_map_deps  CC=1  out:1
    run_status  CC=1  out:1
    run_sync  CC=1  out:1
    run_validate  CC=1  out:1
  wup.cli_config_generator  [1 funcs]
    generate  CC=4  out:5
  wup.config  [19 funcs]
    _load_dotenv  CC=10  out:10
    _normalize_testql_extra_args  CC=5  out:10
    _normalize_testql_timeout  CC=3  out:4
    _parse_planfile_config  CC=5  out:15
    _parse_project_config  CC=2  out:5
    _parse_semcod_tools_config  CC=9  out:23
    _parse_services_config  CC=3  out:23
    _parse_strategy_config  CC=1  out:4
    _parse_testql_config  CC=2  out:28
    _parse_testql_extra_args  CC=5  out:8
  wup.control  [12 funcs]
    _result_dict  CC=1  out:2
    dispatch_command  CC=1  out:1
    dispatch_endpoints  CC=1  out:1
    dispatch_generate  CC=3  out:1
    dispatch_health  CC=2  out:2
    dispatch_init  CC=1  out:1
    dispatch_init_cli  CC=3  out:1
    dispatch_map  CC=1  out:1
    dispatch_query  CC=3  out:5
    dispatch_status  CC=4  out:1
  wup.core  [1 funcs]
    __init__  CC=7  out:18
  wup.dependency_mapper  [2 funcs]
    _detect_framework  CC=2  out:2
    build_from_codebase  CC=6  out:7
  wup.discovery  [2 funcs]
    detect_frameworks  CC=3  out:1
    discover_endpoints  CC=7  out:6
  wup.endpoints  [1 funcs]
    discover_testql_endpoints  CC=5  out:26
  wup.generate  [2 funcs]
    _detect_template  CC=4  out:2
    generate_wup_config  CC=8  out:20
  wup.init_cli  [1 funcs]
    setup_cli_project  CC=9  out:26
  wup.monitoring_manifest  [18 funcs]
    _artifact_row  CC=4  out:5
    _build_docker_rows  CC=5  out:3
    _build_scenario_rows  CC=5  out:8
    _build_wup_service_dicts  CC=3  out:2
    _extract_healthcheck_test  CC=6  out:7
    _extract_service_from_spec  CC=7  out:12
    _load_compose_yaml  CC=5  out:5
    _map_docker_to_wup_service  CC=14  out:11
    _parse_port_mapping  CC=5  out:4
    _semcod_summary_lines  CC=5  out:9
  wup.oql  [9 funcs]
    matches  CC=1  out:2
    _event_rows  CC=5  out:7
    _service_rows  CC=6  out:9
    execute  CC=13  out:12
    _coerce_number  CC=2  out:1
    _compare  CC=14  out:8
    _parse_conditions  CC=7  out:10
    _tokenize  CC=2  out:7
    parse  CC=11  out:19
  wup.paths  [2 funcs]
    health_events_path  CC=1  out:1
    health_state_path  CC=1  out:1
  wup.status_data  [4 funcs]
    _load_json  CC=4  out:4
    _load_manifest  CC=4  out:2
    _summarize_deps  CC=4  out:8
    collect_status_snapshot  CC=12  out:23
  wup.sync  [2 funcs]
    _merge_endpoints  CC=6  out:14
    sync_testql_manifest  CC=9  out:16
  wup.testing.handlers.event_handlers  [1 funcs]
    register_testing_event_handlers  CC=1  out:3
  wup.testing.handlers.health_handlers  [1 funcs]
    register_health_handlers  CC=1  out:3
  wup.testql_monitor  [25 funcs]
    __init__  CC=2  out:3
    _add_config_endpoints  CC=11  out:14
    _add_scenario_probes  CC=5  out:5
    _add_service_map_probes  CC=5  out:5
    _build_port_map  CC=6  out:13
    _is_monitoring_probe  CC=1  out:1
    _assign_by_connect_backend  CC=4  out:4
    _assign_by_longest_token  CC=7  out:5
    _assign_by_path_prefix  CC=13  out:7
    _assign_by_port_8100  CC=2  out:3
  wup.testql_watcher  [2 funcs]
    __init__  CC=13  out:17
    _get_config_endpoints_for_service  CC=10  out:7
  wup.validate  [1 funcs]
    validate_wup_file  CC=8  out:15
  wup.visual_diff  [23 funcs]
    __init__  CC=2  out:3
    _categorize_page_result  CC=7  out:12
    _check_page  CC=10  out:19
    _pages_for_service  CC=11  out:8
    _print_scan_summary  CC=8  out:13
    _write_diff_event  CC=1  out:6
    run_for_service  CC=10  out:22
    _compact_error_message  CC=3  out:3
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=5  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  packages.cli2wup.src.cli2wup.cli.run_shell → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.rest2wup.src.rest2wup.cli.main → packages.rest2wup.src.rest2wup.app.create_app
  packages.rest2wup.src.rest2wup.app.create_app → packages.dsl2wup.src.dsl2wup.schema_registry.schema_for_verb
  packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri → packages.uri2wup.src.uri2wup.uri.uri_for_block
  packages.uri2wup.src.uri2wup.nlp2uri.best_uri → packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri
  packages.uri2wup.src.uri2wup.query._resolve_config_path → wup.config.find_config_file
  packages.uri2wup.src.uri2wup.query._extract_block → wup.paths.health_state_path
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.query._resolve_config_path
  packages.uri2wup.src.uri2wup.query.query_uri → packages.uri2wup.src.uri2wup.query._extract_block
  packages.uri2wup.src.uri2wup.decode.decode_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.decode.decode_uri → packages.uri2wup.src.uri2wup.decode._dict_to_dsl
  packages.uri2wup.src.uri2wup.uri.uri_for_cmd → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.uri_for_block → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri._decode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri.is_wup_uri
  packages.uri2wup.src.uri2wup.patch._resolve_config_path → wup.config.find_config_file
  packages.uri2wup.src.uri2wup.patch.patch_uri → packages.uri2wup.src.uri2wup.uri.parse_wup_uri
  packages.uri2wup.src.uri2wup.patch.patch_uri → packages.uri2wup.src.uri2wup.patch._resolve_config_path
  packages.nlp2wup.src.nlp2wup.validate.validate_wup_config → wup.validate.validate_wup_file
  packages.nlp2wup.src.nlp2wup.generate.generate_from_nl → wup.generate.generate_wup_config
  packages.nlp2wup.src.nlp2wup.generate.generate_from_nl → packages.nlp2wup.src.nlp2wup.generate._extract_template
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.nlp2wup.src.nlp2wup.apply._intent
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.uri2wup.src.uri2wup.nlp2uri.best_uri
  packages.nlp2wup.src.nlp2wup.apply.to_dsl → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.nlp2wup.src.nlp2wup.apply.to_dsl
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.dsl2wup.src.dsl2wup.bus.dispatch
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.uri2wup.src.uri2wup.nlp2uri.best_uri
  packages.nlp2wup.src.nlp2wup.apply.apply_nl → packages.nlp2wup.src.nlp2wup.apply._intent
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.handlers.command.handle_from_tokens
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.events.default_event_store
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.pb_codec.decode_protobuf
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.parse_line
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line → packages.dsl2wup.src.dsl2wup.bus.dispatch
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.dsl2wup.src.dsl2wup.cli._main_legacy → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.dsl2wup.src.dsl2wup.cli._main_legacy → packages.dsl2wup.src.dsl2wup.bus.execute_dsl
  packages.dsl2wup.src.dsl2wup.cli._main_subcommand → packages.dsl2wup.src.dsl2wup.schema_registry.validate_schema_registry
  packages.dsl2wup.src.dsl2wup.cli.main → packages.dsl2wup.src.dsl2wup.cli._main_legacy
  packages.dsl2wup.src.dsl2wup.cli.main → packages.dsl2wup.src.dsl2wup.cli._main_subcommand
  packages.dsl2wup.src.dsl2wup.events.EventStore.append → packages.dsl2wup.src.dsl2wup.pb_codec.encode_protobuf
  packages.dsl2wup.src.dsl2wup.pb_codec.encode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec._set_body
  packages.dsl2wup.src.dsl2wup.pb_codec.decode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec.envelope_to_dict
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 158f 21062L | python:101,json:16,yaml:12,txt:12,toml:7,shell:3,yml:2,proto:2 | 2026-07-29
# generated in 0.04s
# CC̅=4.7 | critical:13/608 | dups:0 | cycles:0

HEALTH[13]:
  🟡 CC    main CC=15 (limit:15)
  🟡 CC    main CC=15 (limit:15)
  🟡 CC    query_uri CC=23 (limit:15)
  🟡 CC    decode_uri CC=20 (limit:15)
  🟡 CC    patch_uri CC=17 (limit:15)
  🟡 CC    _intent CC=21 (limit:15)
  🟡 CC    to_dsl CC=24 (limit:15)
  🟡 CC    _set_body CC=16 (limit:15)
  🟡 CC    envelope_to_dict CC=58 (limit:15)
  🟡 CC    generate_models CC=15 (limit:15)
  🟡 CC    parse_line CC=59 (limit:15)
  🟡 CC    handle_from_tokens CC=16 (limit:15)
  🟡 CC    parse_rule CC=18 (limit:15)

REFACTOR[1]:
  1. split 13 high-CC methods  (CC>15)

PIPELINES[339]:
  [1] Src [main]: main → run_shell → execute_dsl_line → dispatch → ...(1 more)
      PURITY: 100% pure
  [2] Src [main]: main → create_app → schema_for_verb → _load_schemas
      PURITY: 100% pure
  [3] Src [main]: main → nlp2uri → uri_for_block → _encode
      PURITY: 100% pure
  [4] Src [uri_for_cmd]: uri_for_cmd → _encode
      PURITY: 100% pure
  [5] Src [main]: main → apply_nl → to_dsl → _intent
      PURITY: 100% pure
  [6] Src [validate_wup_config]: validate_wup_config → validate_wup_file → find_config_file
      PURITY: 100% pure
  [7] Src [generate_from_nl]: generate_from_nl → generate_wup_config → save_config
      PURITY: 100% pure
  [8] Src [main]: main → _main_legacy → execute_dsl_line → dispatch → ...(1 more)
      PURITY: 100% pure
  [9] Src [to_dict]: to_dict
      PURITY: 100% pure
  [10] Src [__init__]: __init__
      PURITY: 100% pure
  [11] Src [append]: append → encode_protobuf → _set_body
      PURITY: 100% pure
  [12] Src [replay]: replay → envelope_to_dict
      PURITY: 100% pure
  [13] Src [main]: main → generate_models
      PURITY: 100% pure
  [14] Src [encode_text]: encode_text → parse_line → split_command
      PURITY: 100% pure
  [15] Src [encode_protobuf]: encode_protobuf → encode_text_to_protobuf → parse_line → split_command
      PURITY: 100% pure
  [16] Src [decode_protobuf]: decode_protobuf → decode_protobuf_to_text → to_text
      PURITY: 100% pure
  [17] Src [main]: main → run_server → create_server
      PURITY: 100% pure
  [18] Src [__post_init__]: __post_init__ → _require_fastmcp
      PURITY: 100% pure
  [19] Src [_register_tools]: _register_tools → query_uri → parse_wup_uri → _decode
      PURITY: 100% pure
  [20] Src [run]: run
      PURITY: 100% pure
  [21] Src [__init__]: __init__
      PURITY: 100% pure
  [22] Src [generate]: generate
      PURITY: 100% pure
  [23] Src [_generate_smoke_scenario]: _generate_smoke_scenario
      PURITY: 100% pure
  [24] Src [_generate_command_scenario]: _generate_command_scenario
      PURITY: 100% pure
  [25] Src [generate_custom_scenario]: generate_custom_scenario
      PURITY: 100% pure
  [26] Src [print_summary]: print_summary
      PURITY: 100% pure
  [27] Src [__init__]: __init__
      PURITY: 100% pure
  [28] Src [subscribe]: subscribe
      PURITY: 100% pure
  [29] Src [publish]: publish
      PURITY: 100% pure
  [30] Src [execute]: execute
      PURITY: 100% pure
  [31] Src [query]: query
      PURITY: 100% pure
  [32] Src [__init__]: __init__
      PURITY: 100% pure
  [33] Src [_should_scan]: _should_scan
      PURITY: 100% pure
  [34] Src [scan_file]: scan_file
      PURITY: 100% pure
  [35] Src [scan_directory]: scan_directory
      PURITY: 100% pure
  [36] Src [get_summary]: get_summary
      PURITY: 100% pure
  [37] Src [print_report]: print_report
      PURITY: 100% pure
  [38] Src [quick_scan]: quick_scan
      PURITY: 100% pure
  [39] Src [scan_yaml_changes]: scan_yaml_changes
      PURITY: 100% pure
  [40] Src [_fail]: _fail
      PURITY: 100% pure
  [41] Src [run_validate]: run_validate → dispatch_validate → _result_dict → dispatch → ...(1 more)
      PURITY: 100% pure
  [42] Src [__init__]: __init__
      PURITY: 100% pure
  [43] Src [_dispatch_menu_choice]: _dispatch_menu_choice
      PURITY: 100% pure
  [44] Src [run]: run
      PURITY: 100% pure
  [45] Src [_init_project]: _init_project
      PURITY: 100% pure
  [46] Src [_detect_framework]: _detect_framework → detect_framework
      PURITY: 100% pure
  [47] Src [_auto_detect_services]: _auto_detect_services → auto_detect_services → detect_service_type
      PURITY: 100% pure
  [48] Src [_detect_service_type]: _detect_service_type → detect_service_type
      PURITY: 100% pure
  [49] Src [_configure_services]: _configure_services
      PURITY: 100% pure
  [50] Src [_add_service_interactive]: _add_service_interactive
      PURITY: 100% pure

LAYERS:
  packages/                       CC̄=6.3    ←in:0  →out:0
  │ !! pb_codec                   235L  0C    8m  CC=58     ←6
  │ !! command                    232L  0C   10m  CC=16     ←1
  │ !! query                      164L  1C    4m  CC=23     ←3
  │ !! grammar                    156L  0C    4m  CC=59     ←5
  │ server                     149L  1C    6m  CC=2      ←1
  │ query                      137L  0C    7m  CC=5      ←1
  │ models                     129L  13C    0m  CC=0.0    ←0
  │ !! apply                      126L  1C    4m  CC=24     ←2
  │ events                     116L  2C    5m  CC=7      ←3
  │ cli                        108L  0C    3m  CC=9      ←0
  │ command.proto              104L  0C    0m  CC=0.0    ←0
  │ !! cli                        100L  0C    2m  CC=15     ←0
  │ !! codegen                     98L  0C    2m  CC=15     ←0
  │ uri                         92L  0C    6m  CC=7      ←4
  │ schema_registry             84L  0C    6m  CC=13     ←4
  │ bus                         79L  0C    5m  CC=6      ←7
  │ !! decode                      72L  0C    2m  CC=20     ←1
  │ app                         68L  0C    1m  CC=1      ←1
  │ !! patch                       68L  1C    3m  CC=17     ←2
  │ !! cli                         62L  0C    1m  CC=15     ←0
  │ command_pb2                 62L  0C    0m  CC=0.0    ←0
  │ nlp2uri                     48L  1C    3m  CC=4      ←4
  │ cli                         43L  0C    1m  CC=9      ←0
  │ result_pb2                  39L  0C    0m  CC=0.0    ←0
  │ codec                       35L  0C    4m  CC=3      ←1
  │ pyproject.toml              34L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              29L  0C    0m  CC=0.0    ←0
  │ cli                         28L  0C    1m  CC=4      ←0
  │ result                      28L  1C    1m  CC=1      ←0
  │ pyproject.toml              28L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              27L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              27L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              26L  0C    0m  CC=0.0    ←0
  │ generate                    25L  0C    2m  CC=3      ←1
  │ cli                         24L  0C    1m  CC=4      ←0
  │ install-dev.sh              24L  0C    0m  CC=0.0    ←0
  │ result.proto                23L  0C    0m  CC=0.0    ←0
  │ init_cli.schema.json        14L  0C    0m  CC=0.0    ←0
  │ status.schema.json          14L  0C    0m  CC=0.0    ←0
  │ patch.schema.json           13L  0C    0m  CC=0.0    ←0
  │ generate.schema.json        13L  0C    0m  CC=0.0    ←0
  │ query.schema.json           13L  0C    0m  CC=0.0    ←0
  │ map.schema.json             12L  0C    0m  CC=0.0    ←0
  │ endpoints.schema.json       12L  0C    0m  CC=0.0    ←0
  │ resolve.schema.json         12L  0C    0m  CC=0.0    ←0
  │ sync.schema.json            12L  0C    0m  CC=0.0    ←0
  │ validate                    11L  0C    1m  CC=1      ←0
  │ health.schema.json          11L  0C    0m  CC=0.0    ←0
  │ adopt.schema.json           11L  0C    0m  CC=0.0    ←0
  │ init.schema.json            11L  0C    0m  CC=0.0    ←0
  │ validate.schema.json        11L  0C    0m  CC=0.0    ←0
  │ local.dev.txt               11L  0C    0m  CC=0.0    ←0
  │ local.dev.txt               10L  0C    0m  CC=0.0    ←0
  │ local.dev.txt               10L  0C    0m  CC=0.0    ←0
  │ local.dev.txt                9L  0C    0m  CC=0.0    ←0
  │ local.dev.txt                9L  0C    0m  CC=0.0    ←0
  │ local.dev.txt                9L  0C    0m  CC=0.0    ←0
  │ engine                       8L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ generate-proto.sh            7L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  wup/                            CC̄=4.7    ←in:27  →out:3
  │ !! cli                       1079L  0C   25m  CC=14     ←0
  │ !! testql_watcher            1013L  2C   52m  CC=13     ←0
  │ !! core                       740L  2C   32m  CC=12     ←0
  │ !! testql_monitor             693L  3C   40m  CC=13     ←1
  │ !! visual_diff                638L  1C   26m  CC=11     ←1
  │ !! config                     610L  0C   19m  CC=10     ←14
  │ !! assistant                  594L  1C   24m  CC=14     ←0
  │ monitoring_manifest        478L  1C   22m  CC=14     ←5
  │ !! aql                        306L  4C   13m  CC=18     ←0
  │ cli_scanner                302L  3C   12m  CC=10     ←0
  │ discovery                  279L  12C   12m  CC=8      ←1
  │ oql                        267L  5C   12m  CC=14     ←1
  │ planfile_reporter          267L  1C   16m  CC=14     ←0
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ cli_config_generator       223L  1C    6m  CC=6      ←0
  │ testql_cli_generator       215L  1C    6m  CC=6      ←0
  │ config                     206L  14C    0m  CC=0.0    ←0
  │ web_client                 185L  1C   10m  CC=6      ←0
  │ dependency_mapper          177L  1C   12m  CC=6      ←0
  │ anomaly_detector           175L  1C    8m  CC=7      ←0
  │ _yaml_detector             128L  1C    8m  CC=8      ←0
  │ _ast_detector              124L  1C    9m  CC=11     ←1
  │ health_handlers            123L  1C    6m  CC=8      ←1
  │ status_data                114L  0C    5m  CC=12     ←1
  │ control                    106L  0C   12m  CC=4      ←1
  │ assistant_discovery         99L  0C    3m  CC=11     ←1
  │ multi                       81L  1C    2m  CC=11     ←0
  │ cli_bridge                  80L  0C    9m  CC=3      ←1
  │ _hash_detector              72L  1C    4m  CC=5      ←0
  │ sync                        70L  0C    2m  CC=9      ←1
  │ bus                         65L  5C    5m  CC=4      ←0
  │ generate                    62L  0C    2m  CC=8      ←2
  │ init_cli                    60L  0C    1m  CC=9      ←1
  │ assistant_validator         57L  0C    2m  CC=9      ←2
  │ event_handlers              55L  1C    4m  CC=5      ←1
  │ __init__                    46L  0C    1m  CC=2      ←0
  │ endpoints                   44L  0C    1m  CC=5      ←1
  │ event_store                 41L  1C    3m  CC=4      ←0
  │ __init__                    36L  0C    0m  CC=0.0    ←0
  │ anomaly_models              35L  2C    0m  CC=0.0    ←0
  │ validate                    34L  0C    1m  CC=8      ←2
  │ target                      23L  1C    0m  CC=0.0    ←0
  │ _base_detector              18L  1C    2m  CC=1      ←0
  │ paths                       16L  0C    2m  CC=1      ←4
  │ health_events               11L  1C    0m  CC=0.0    ←0
  │ file_events                 10L  1C    0m  CC=0.0    ←0
  │ health_queries               7L  1C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=3.3    ←in:0  →out:3
  │ run_probe_smoke             88L  0C    6m  CC=6      ←0
  │
  examples/                       CC̄=2.4    ←in:0  →out:6
  │ webhook_notifications      375L  1C   10m  CC=6      ←0
  │ ci_cd_integration          339L  0C    4m  CC=3      ←0
  │ visual_diff_demo           305L  0C    9m  CC=6      ←0
  │ testql_integration         286L  1C    6m  CC=6      ←0
  │ c2004_monorepo_demo        258L  0C   10m  CC=7      ←0
  │ testql_demo                191L  0C    4m  CC=6      ←0
  │ routes                      38L  1C    5m  CC=1      ←0
  │ routes                      33L  0C    5m  CC=2      ←0
  │ docker-compose.yml          33L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    28L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    28L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  26L  0C    0m  CC=0.0    ←0
  │ Dockerfile                  26L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    21L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    21L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    21L  0C    0m  CC=0.0    ←0
  │ main                        20L  0C    2m  CC=1      ←0
  │ main                        20L  0C    2m  CC=1      ←0
  │ routes                      18L  0C    3m  CC=1      ←0
  │ routes                      18L  0C    3m  CC=1      ←0
  │ main                        16L  0C    2m  CC=1      ←0
  │ main                        16L  0C    2m  CC=1      ←0
  │ main                        16L  0C    2m  CC=1      ←0
  │ routes                      13L  0C    2m  CC=1      ←0
  │ requirements.txt             3L  0C    0m  CC=0.0    ←0
  │ requirements.txt             2L  0C    0m  CC=0.0    ←0
  │ requirements.txt             1L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! duplication.json          3481L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  528L  0C    0m  CC=0.0    ←0
  │ tree.txt                   330L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ koru.yaml                  133L  0C    0m  CC=0.0    ←0
  │ pyproject.toml             127L  0C    0m  CC=0.0    ←0
  │ Makefile                    96L  0C    0m  CC=0.0    ←0
  │ regix.yaml                  51L  0C    0m  CC=0.0    ←0
  │ project.sh                  49L  0C    0m  CC=0.0    ←0
  │ Taskfile.yml                32L  0C    0m  CC=0.0    ←0
  │ local.dev.txt               17L  0C    0m  CC=0.0    ←0
  │ todo.txt                    12L  0C    0m  CC=0.0    ←0
  │ deps.json                    4L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    82L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ cli-smoke.testql.toon.yaml    17L  0C    0m  CC=0.0    ←0
  │ cli-wup.testql.toon.yaml    16L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     examples/flask-app/app/__init__.py        0L

COUPLING:
                      packages.dsl2wup                wup   packages.mcp2wup   packages.nlp2wup   packages.uri2wup  packages.rest2wup           examples   packages.cli2wup            scripts        wup.testing
   packages.dsl2wup                 ──                 10                ←12                ←11                  3                 ←7                                    ←3                                        hub
                wup                  1                 ──                                    ←2                 ←6                                    ←6                                    ←3                  2  hub
   packages.mcp2wup                 12                                    ──                  2                  3                                                                                                 !! fan-out
   packages.nlp2wup                 11                  2                 ←2                 ──                  2                                                                                                 !! fan-out
   packages.uri2wup                  1                  6                 ←3                 ←2                 ──                                                                                                 hub
  packages.rest2wup                  7                                                                                             ──                                                                            
           examples                                     6                                                                                             ──                                                         
   packages.cli2wup                  3                                                                                                                                   ──                                      
            scripts                                     3                                                                                                                                   ──                   
        wup.testing                                    ←2                                                                                                                                                      ──
  CYCLES: none
  HUB: packages.uri2wup/ (fan-in=8)
  HUB: packages.dsl2wup/ (fan-in=35)
  HUB: wup/ (fan-in=27)
  SMELL: packages.dsl2wup/ fan-out=13 → split needed
  SMELL: packages.nlp2wup/ fan-out=15 → split needed
  SMELL: packages.mcp2wup/ fan-out=17 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 10 groups | 95f 12177L | 2026-07-29

SUMMARY:
  files_scanned: 95
  total_lines:   12177
  dup_groups:    10
  dup_fragments: 23
  saved_lines:   56
  scan_ms:       13459

HOTSPOTS[7] (files with most duplication):
  wup/core.py  dup=12L  groups=1  frags=3  (0.1%)
  wup/control.py  dup=12L  groups=2  frags=2  (0.1%)
  examples/webhook_notifications.py  dup=12L  groups=1  frags=3  (0.1%)
  packages/mcp2wup/src/mcp2wup/server.py  dup=11L  groups=2  frags=2  (0.1%)
  packages/uri2wup/src/uri2wup/patch.py  dup=9L  groups=1  frags=1  (0.1%)
  packages/uri2wup/src/uri2wup/query.py  dup=9L  groups=1  frags=1  (0.1%)
  examples/flask-app/app/auth/routes.py  dup=8L  groups=1  frags=2  (0.1%)

DUPLICATES[10] (ranked by impact):
  [a8a64d10d1166f5d]   EXAC  _resolve_config_path  L=9 N=2 saved=9 sim=1.00
      packages/uri2wup/src/uri2wup/patch.py:25-33  (_resolve_config_path)
      packages/uri2wup/src/uri2wup/query.py:41-49  (_resolve_config_path)
  [F0003]   FUZZ  on_modified  L=4 N=3 saved=8 sim=0.95
      wup/core.py:727-730  (on_modified)
      wup/core.py:732-735  (on_created)
      wup/core.py:737-740  (on_deleted)
  [8575900946923f44]   STRU  _snapshot_path  L=3 N=3 saved=6 sim=1.00
      wup/_ast_detector.py:59-61  (_snapshot_path)
      wup/_hash_detector.py:22-24  (_snapshot_path)
      wup/_yaml_detector.py:49-51  (_snapshot_path)
  [F0005]   FUZZ  wup_endpoints  L=6 N=2 saved=6 sim=0.90
      packages/mcp2wup/src/mcp2wup/server.py:88-93  (wup_endpoints)
      wup/control.py:80-86  (dispatch_endpoints)
  [F0001]   FUZZ  add_slack  L=3 N=3 saved=6 sim=0.89
      examples/webhook_notifications.py:193-195  (add_slack)
      examples/webhook_notifications.py:197-199  (add_teams)
      examples/webhook_notifications.py:201-206  (add_discord)
  [ada6007a0d4d4d23]   STRU  login  L=5 N=2 saved=5 sim=1.00
      examples/flask-app/app/auth/routes.py:7-11  (login)
      examples/flask-app/app/auth/routes.py:20-22  (register)
  [b5bb02e2622cb9c2]   STRU  _coerce_number  L=5 N=2 saved=5 sim=1.00
      wup/aql.py:182-186  (_coerce_number)
      wup/oql.py:70-74  (_coerce_number)
  [F0004]   FUZZ  wup_sync  L=5 N=2 saved=5 sim=0.90
      packages/mcp2wup/src/mcp2wup/server.py:69-73  (wup_sync)
      wup/control.py:41-45  (dispatch_sync)
  [dc68eab4ed2dec80]   STRU  _save_snapshot  L=3 N=2 saved=3 sim=1.00
      examples/visual_diff_demo.py:62-64  (_save_snapshot)
      wup/visual_diff.py:253-255  (_save_snapshot)
  [F0002]   FUZZ  get_endpoints_for_service  L=3 N=2 saved=3 sim=0.85
      wup/dependency_mapper.py:106-108  (get_endpoints_for_service)
      wup/dependency_mapper.py:110-112  (get_files_for_service)

REFACTOR[10] (ranked by priority):
  [1] ○ extract_function   → packages/uri2wup/src/uri2wup/utils/_resolve_config_path.py
      WHY: 2 occurrences of 9-line block across 2 files — saves 9 lines
      FILES: packages/uri2wup/src/uri2wup/patch.py, packages/uri2wup/src/uri2wup/query.py
  [2] ○ extract_class      → wup/utils/on_modified.py
      WHY: 3 occurrences of 4-line block across 1 files — saves 8 lines
      FILES: wup/core.py
  [3] ○ extract_function   → wup/utils/_snapshot_path.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: wup/_ast_detector.py, wup/_hash_detector.py, wup/_yaml_detector.py
  [4] ○ extract_function   → utils/wup_endpoints.py
      WHY: 2 occurrences of 6-line block across 2 files — saves 6 lines
      FILES: packages/mcp2wup/src/mcp2wup/server.py, wup/control.py
  [5] ○ extract_class      → examples/utils/add_slack.py
      WHY: 3 occurrences of 3-line block across 1 files — saves 6 lines
      FILES: examples/webhook_notifications.py
  [6] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: examples/flask-app/app/auth/routes.py
  [7] ○ extract_function   → wup/utils/_coerce_number.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: wup/aql.py, wup/oql.py
  [8] ○ extract_function   → utils/wup_sync.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/mcp2wup/src/mcp2wup/server.py, wup/control.py
  [9] ○ extract_function   → utils/_save_snapshot.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/visual_diff_demo.py, wup/visual_diff.py
  [10] ○ extract_class      → wup/utils/get_endpoints_for_service.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: wup/dependency_mapper.py

QUICK_WINS[5] (low risk, high savings — do first):
  [1] extract_function   saved=9L  → packages/uri2wup/src/uri2wup/utils/_resolve_config_path.py
      FILES: patch.py, query.py
  [2] extract_class      saved=8L  → wup/utils/on_modified.py
      FILES: core.py
  [3] extract_function   saved=6L  → wup/utils/_snapshot_path.py
      FILES: _ast_detector.py, _hash_detector.py, _yaml_detector.py
  [4] extract_function   saved=6L  → utils/wup_endpoints.py
      FILES: server.py, control.py
  [5] extract_class      saved=6L  → examples/utils/add_slack.py
      FILES: webhook_notifications.py

DEPENDENCY_RISK[3] (duplicates spanning multiple packages):
  wup_endpoints  packages=2  files=2
      packages/mcp2wup/src/mcp2wup/server.py
      wup/control.py
  wup_sync  packages=2  files=2
      packages/mcp2wup/src/mcp2wup/server.py
      wup/control.py
  _save_snapshot  packages=2  files=2
      examples/visual_diff_demo.py
      wup/visual_diff.py

EFFORT_ESTIMATE (total ≈ 2.3h):
  easy   _resolve_config_path                saved=9L  ~18min
  easy   on_modified                         saved=8L  ~16min
  easy   _snapshot_path                      saved=6L  ~12min
  easy   wup_endpoints                       saved=6L  ~24min
  easy   add_slack                           saved=6L  ~12min
  easy   login                               saved=5L  ~10min
  easy   _coerce_number                      saved=5L  ~10min
  easy   wup_sync                            saved=5L  ~20min
  easy   _save_snapshot                      saved=3L  ~12min
  easy   get_endpoints_for_service           saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  10 → 0
  saved_lines: 56 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 531 func | 66f | 2026-07-29
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT           wup/cli.py
      WHY: 1079L, 0 classes, max CC=14
      EFFORT: ~4h  IMPACT: 15106

  [2] !! SPLIT           wup/testql_watcher.py
      WHY: 1013L, 2 classes, max CC=13
      EFFORT: ~4h  IMPACT: 13169

  [3] !  SPLIT-FUNC      query_uri  CC=23  fan=26
      WHY: CC=23 exceeds 15
      EFFORT: ~1h  IMPACT: 598

  [4] !! SPLIT-FUNC      parse_line  CC=59  fan=7
      WHY: CC=59 exceeds 15
      EFFORT: ~1h  IMPACT: 413

  [5] !! SPLIT-FUNC      envelope_to_dict  CC=58  fan=5
      WHY: CC=58 exceeds 15
      EFFORT: ~1h  IMPACT: 290

  [6] !  SPLIT-FUNC      main  CC=15  fan=19
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 285

  [7] !  SPLIT-FUNC      generate_models  CC=15  fan=19
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 285

  [8] !  SPLIT-FUNC      handle_from_tokens  CC=16  fan=17
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 272

  [9] !  SPLIT-FUNC      main  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [10] !  SPLIT-FUNC      to_dsl  CC=24  fan=9
      WHY: CC=24 exceeds 15
      EFFORT: ~1h  IMPACT: 216


RISKS[3]:
  ⚠ Splitting duplication.json may break 0 import paths
  ⚠ Splitting wup/cli.py may break 25 import paths
  ⚠ Splitting wup/testql_watcher.py may break 52 import paths

METRICS-TARGET:
  CC̄:          5.0 → ≤3.5
  max-CC:      59 → ≤20
  god-modules: 9 → 0
  high-CC(≥15): 13 → ≤6
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=5.0 → now CC̄=5.0
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
