# WUP (What's Up)

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `wup`
- **version**: `0.2.42`
- **python_requires**: `>=3.9`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(4), app.doql.less, goal.yaml, .env.example, src(20 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.42;
}

dependencies {
  runtime: "watchdog>=4.0.0, psutil>=5.9.0, rich>=13.0.0, typer>=0.9.0, pyyaml>=6.0";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="wup"] {

}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.9;
}
```

### Source Modules

- `wup._ast_detector`
- `wup._hash_detector`
- `wup._yaml_detector`
- `wup.anomaly_detector`
- `wup.anomaly_models`
- `wup.assistant`
- `wup.cli`
- `wup.cli_config_generator`
- `wup.cli_scanner`
- `wup.config`
- `wup.core`
- `wup.dependency_mapper`
- `wup.monitoring_manifest`
- `wup.planfile_reporter`
- `wup.testql_cli_generator`
- `wup.testql_discovery`
- `wup.testql_monitor`
- `wup.testql_watcher`
- `wup.visual_diff`
- `wup.web_client`

## Dependencies

### Runtime

```text markpact:deps python
watchdog>=4.0.0
psutil>=5.9.0
rich>=13.0.0
typer>=0.9.0
pyyaml>=6.0
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
    def _normalize_fleet_health_entry()  # CC=6
    def _load_service_health()  # CC=4
    def _save_service_health()  # CC=1
    def _record_health_transition()  # CC=9
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
    def _select_scenarios_for_service(service)  # CC=9
    def _filter_scenarios_by_type(scenarios, svc_type)  # CC=8
    def _scenario_matches_type(scenario, svc_type)  # CC=4
    def _run_testql(args, timeout)  # CC=2
    def _write_track()  # CC=11 ⚠
    def _quick_timeout()  # CC=3
    def _merge_endpoints(service, endpoints)  # CC=3
    def _run_scenario_quick(service, scenario, merged_endpoints)  # CC=6
    def _quick_pass_actions(service, merged_endpoints)  # CC=11 ⚠
    def _quick_probe_limit(service)  # CC=3
    def _quick_probe_timeout()  # CC=3
    def _run_live_http_probes(service, merged_endpoints)  # CC=6
    def _try_parse_json_summary(blob)  # CC=8
    def _try_find_line_summary(blob)  # CC=7
    def _summarize_health_scenario_failure(result)  # CC=8
    def _run_fleet_health_scenario()  # CC=10 ⚠
    def run_quick_test(service, endpoints)  # CC=9
    def _publish_visual_events(service, visual_results)  # CC=6
    def run_detail_test(service, endpoints)  # CC=9
    def process_changed_file_once(file_path)  # CC=4
    def _run_periodic_probes_once()  # CC=5
    def _start_periodic_probe_thread()  # CC=3
    def start_watching(watch_paths)  # CC=1
```

### `wup.testql_monitor` (`wup/testql_monitor.py`)

```python
def _parse_api_lines(content, source)  # CC=3, fan=6
def parse_scenario_probes(scenario_path)  # CC=2, fan=3
def _extract_base_url(data)  # CC=4, fan=4
def _parse_endpoint_row(row, base_url, source)  # CC=8, fan=8
def parse_service_map_probes(map_path)  # CC=6, fan=8
def _connect_module_api_on_frontend_proxy(probe)  # CC=5, fan=4
def _firmware_plugin_probe_without_runtime(probe)  # CC=5, fan=4
def is_monitoring_probe(probe)  # CC=9, fan=7
def _service_path_patterns(services)  # CC=6, fan=7
def _find_service_by_name(services, name)  # CC=3, fan=1
def _find_service_by_token(services, token)  # CC=3, fan=1
def _assign_by_port_8101(services)  # CC=1, fan=1
def _assign_by_port_8202(services)  # CC=1, fan=1
def _assign_by_port_8100(services, path_lower)  # CC=2, fan=3
def _assign_by_connect_backend(services, path_lower)  # CC=4, fan=3
def _assign_http_probe(probe, services, path_lower)  # CC=4, fan=5
def _assign_by_longest_token(path_lower, services)  # CC=7, fan=3
def _assign_by_path_prefix(path_lower, services)  # CC=13, fan=2 ⚠
def assign_probe_to_service(probe, services)  # CC=5, fan=6
class ProbeTarget:  # Single HTTP probe derived from TestQL scenarios or service m
    def probe(timeout_s)  # CC=5
class _ProbeAccumulator:  # Deduplicated probe collector for discover_probes_by_service.
    def __init__(services)  # CC=2
    def add(service, probe)  # CC=3
class TestQLMonitor:  # Build and run live probes from TestQL scenarios + WUP config
    def __init__(project_root, config)  # CC=2
    def _service_map_paths()  # CC=3
    def _add_config_endpoints(accumulator)  # CC=11 ⚠
    def _add_scenario_probes(accumulator)  # CC=5
    def _add_service_map_probes(accumulator)  # CC=5
    def discover_probes_by_service()  # CC=2
    def _resolve_base_url_for_service(service)  # CC=8
    def _probeable_url(path, base)  # CC=4
    def probes_for_service(service, extra_paths)  # CC=9
    def _sort_probes_for_live(probes)  # CC=1
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
    def infer_service(file_path)  # CC=10 ⚠
    def _is_coincident_pair(type_a, type_b)  # CC=6
    def detect_service_coincidences(changed_service)  # CC=9
    def _services_share_domain(service1, service2)  # CC=1
    def get_service_config(service_name)  # CC=3
    def should_test(service)  # CC=1
    def schedule_quick_test(service)  # CC=3
    def schedule_detail_test(service)  # CC=1
    def process_test_queue_once()  # CC=7
    def cpu_ok()  # CC=2
    def run_quick_test(service, endpoints)  # CC=6
    def run_detail_test(service, endpoints)  # CC=10 ⚠
    def test_loop()  # CC=2
    def should_watch_file(file_path)  # CC=3
    def _is_file_ignored(rel_path)  # CC=11 ⚠
    def _notify_all_configured_services(rel_path)  # CC=4
    def on_file_change(file_path)  # CC=11 ⚠
    def build_watched_paths()  # CC=6
    def _create_and_start_observer(event_handler, watch_paths)  # CC=5
    def start_watching(watch_paths)  # CC=7
    def create_status_table()  # CC=3
    def run_with_dashboard()  # CC=5
class WupEventHandler:  # File system event handler for WUP watcher.
    def __init__(watcher)  # CC=1
    def on_modified(event)  # CC=2
    def on_created(event)  # CC=2
    def on_deleted(event)  # CC=2
```

### `wup.assistant` (`wup/assistant.py`)

```python
def main()  # CC=1, fan=5
class WupAssistant:  # Interactive configuration assistant.
    def __init__(project_root)  # CC=1
    def _dispatch_menu_choice(choice, template)  # CC=3
    def run(quick, template)  # CC=8
    def _init_project(template)  # CC=7
    def _detect_framework()  # CC=6
    def _auto_detect_services(framework)  # CC=7
    def _detect_service_type(name, path)  # CC=10 ⚠
    def _configure_services()  # CC=14 ⚠
    def _add_service_interactive()  # CC=11 ⚠
    def _edit_service(idx)  # CC=5
    def _setup_watch()  # CC=7
    def _configure_testql()  # CC=3
    def _setup_web_dashboard()  # CC=3
    def _setup_visual_diff()  # CC=6
    def _setup_anomaly_detection()  # CC=8
    def _review_and_validate()  # CC=11 ⚠
    def _validate_config()  # CC=9
    def _generate_suggestions()  # CC=6
    def _save_configuration()  # CC=3
    def _save_draft()  # CC=1
    def _load_draft()  # CC=2
    def _config_to_dict(config)  # CC=1
    def _quick_setup(template)  # CC=4
```

### `wup.visual_diff` (`wup/visual_diff.py`)

```python
def _playwright_available()  # CC=3, fan=0
def _warn_playwright_missing()  # CC=2, fan=1
def _fetch_dom_snapshot(url, max_depth, headless, error_selectors)  # CC=9, fan=14
def _detect_content_issues(snapshot, cfg)  # CC=6, fan=5
def _page_slug(url)  # CC=2, fan=3
def _short_url(url)  # CC=3, fan=1
def _compact_error_message(message, max_len)  # CC=3, fan=3
def _sample_list(items, limit)  # CC=3, fan=2
def _looks_like_visual_page(url)  # CC=7, fan=4
def _snapshot_path(snapshot_dir, service, url)  # CC=1, fan=2
def _load_snapshot(path)  # CC=3, fan=3
def _save_snapshot(path, snapshot)  # CC=1, fan=3
def _node_signature(node, depth)  # CC=3, fan=3
def _flatten(node, depth, max_depth)  # CC=4, fan=4
def _diff_snapshots(old, new, max_depth, threshold_added, threshold_removed, threshold_changed)  # CC=11, fan=5 ⚠
def _resolve_base_url(cfg)  # CC=3, fan=2
class VisualDiffer:  # Triggered by TestQLWatcher after a file change.
    def __init__(project_root, cfg)  # CC=1
    def _pages_for_service(service, endpoints)  # CC=11 ⚠
    def _categorize_page_result(service, url, result, ok_urls, new_urls, error_results)  # CC=6
    def _print_scan_summary(service, ok_urls, new_urls, error_results)  # CC=8
    def run_for_service(service, endpoints)  # CC=7
    def _check_page(service, url)  # CC=4
    def _write_diff_event(service, url, result)  # CC=1
    def get_recent_diffs(seconds)  # CC=7
```

## Call Graph

*104 nodes · 100 edges · 16 modules · CC̄=4.3*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `status` *(in wup.cli)* | 5 | 0 | 121 | **121** |
| `validate_config` *(in wup.config)* | 14 ⚠ | 1 | 118 | **119** |
| `show_ci_cd_demo` *(in examples.ci_cd_integration)* | 2 | 1 | 69 | **70** |
| `show_webhook_demo` *(in examples.webhook_notifications)* | 4 | 1 | 68 | **69** |
| `_run_with_mock_services` *(in examples.testql_demo)* | 6 | 2 | 60 | **62** |
| `sync_testql` *(in wup.cli)* | 13 ⚠ | 0 | 45 | **45** |
| `main` *(in scripts.run_probe_smoke)* | 14 ⚠ | 0 | 38 | **38** |
| `demo_snapshot_persistence` *(in examples.visual_diff_demo)* | 3 | 1 | 26 | **27** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# generated in 0.08s
# nodes: 104 | edges: 100 | modules: 16
# CC̄=4.3

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:121  total:121
  wup.config.validate_config
    CC=14  in:1  out:118  total:119
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  wup.cli.sync_testql
    CC=13  in:0  out:45  total:45
  scripts.run_probe_smoke.main
    CC=14  in:0  out:38  total:38
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=2  in:1  out:26  total:27
  wup.monitoring_manifest.build_monitoring_manifest
    CC=9  in:4  out:15  total:19
  wup.visual_diff._fetch_dom_snapshot
    CC=9  in:1  out:17  total:18
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:18  total:18
  examples.testql_demo.simulate_testql_analysis
    CC=2  in:0  out:18  total:18
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.config.load_config
    CC=5  in:9  out:8  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.monitoring_manifest.load_monitoring_manifest_from_yaml
    CC=9  in:2  out:14  total:16
  wup.config.save_config
    CC=2  in:3  out:12  total:15

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
  scripts.run_probe_smoke  [1 funcs]
    main  CC=14  out:38
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.cli  [6 funcs]
    _auto_generate_config  CC=3  out:13
    _load_watch_config  CC=4  out:3
    _refresh_monitoring_manifest  CC=3  out:4
    init  CC=3  out:16
    status  CC=5  out:121
    sync_testql  CC=13  out:45
  wup.cli_config_generator  [1 funcs]
    generate  CC=4  out:5
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:12
    validate_config  CC=14  out:118
  wup.core  [1 funcs]
    __init__  CC=7  out:18
  wup.monitoring_manifest  [13 funcs]
    _build_docker_rows  CC=5  out:3
    _build_scenario_rows  CC=5  out:8
    _build_wup_service_dicts  CC=3  out:2
    _extract_healthcheck_test  CC=6  out:7
    _extract_service_from_spec  CC=7  out:12
    _load_compose_yaml  CC=5  out:5
    _map_docker_to_wup_service  CC=11  out:7
    _parse_port_mapping  CC=5  out:4
    build_monitoring_manifest  CC=9  out:15
    discover_docker_compose_services  CC=7  out:10
  wup.testql_monitor  [24 funcs]
    _add_config_endpoints  CC=11  out:13
    _add_scenario_probes  CC=5  out:5
    _add_service_map_probes  CC=5  out:5
    _resolve_base_url  CC=4  out:6
    probes_for_service  CC=9  out:11
    _assign_by_connect_backend  CC=4  out:4
    _assign_by_longest_token  CC=7  out:5
    _assign_by_path_prefix  CC=13  out:7
    _assign_by_port_8100  CC=2  out:3
    _assign_by_port_8101  CC=1  out:1
  wup.testql_watcher  [2 funcs]
    __init__  CC=13  out:14
    _get_config_endpoints_for_service  CC=10  out:7
  wup.visual_diff  [22 funcs]
    __init__  CC=1  out:2
    _categorize_page_result  CC=6  out:12
    _check_page  CC=4  out:9
    _pages_for_service  CC=11  out:8
    _print_scan_summary  CC=8  out:13
    _write_diff_event  CC=1  out:6
    run_for_service  CC=7  out:11
    _compact_error_message  CC=3  out:3
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=5  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._parse_port_mapping
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._extract_healthcheck_test
  wup.monitoring_manifest.discover_docker_compose_services → wup.monitoring_manifest._load_compose_yaml
  wup.monitoring_manifest.discover_docker_compose_services → wup.monitoring_manifest._extract_service_from_spec
  wup.monitoring_manifest._build_docker_rows → wup.monitoring_manifest._map_docker_to_wup_service
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest.discover_docker_compose_services
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_wup_service_dicts
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_docker_rows
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_scenario_rows
  wup.monitoring_manifest.patch_wup_yaml_monitoring → wup.monitoring_manifest.manifest_to_yaml_block
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli._load_watch_config → wup.config.load_config
  wup.cli._refresh_monitoring_manifest → wup.monitoring_manifest.build_monitoring_manifest
  wup.cli._refresh_monitoring_manifest → wup.monitoring_manifest.patch_wup_yaml_monitoring
  wup.cli._auto_generate_config → wup.config.get_default_config
  wup.cli._auto_generate_config → wup.config.save_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.cli.sync_testql → wup.config.load_config
  wup.cli.sync_testql → wup.monitoring_manifest.build_monitoring_manifest
  wup.testql_monitor.parse_scenario_probes → wup.testql_monitor._parse_api_lines
  wup.testql_monitor.parse_service_map_probes → wup.testql_monitor._extract_base_url
  wup.testql_monitor.parse_service_map_probes → wup.testql_monitor._parse_endpoint_row
  wup.testql_monitor.is_monitoring_probe → wup.testql_monitor._connect_module_api_on_frontend_proxy
  wup.testql_monitor.is_monitoring_probe → wup.testql_monitor._firmware_plugin_probe_without_runtime
  wup.testql_monitor._assign_by_port_8101 → wup.testql_monitor._find_service_by_name
  wup.testql_monitor._assign_by_port_8202 → wup.testql_monitor._find_service_by_token
  wup.testql_monitor._assign_by_port_8100 → wup.testql_monitor._find_service_by_name
  wup.testql_monitor._assign_by_port_8100 → wup.testql_monitor._find_service_by_token
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_connect_backend
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8101
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8202
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8100
  wup.testql_monitor._assign_by_longest_token → wup.testql_monitor._service_path_patterns
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_by_longest_token
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_by_path_prefix
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_http_probe
  wup.testql_monitor.TestQLMonitor._add_config_endpoints → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_config_endpoints → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.parse_scenario_probes
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.parse_service_map_probes
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor.probes_for_service → wup.testql_monitor.is_monitoring_probe
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
# generated in 0.08s
# nodes: 104 | edges: 100 | modules: 16
# CC̄=4.3

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:121  total:121
  wup.config.validate_config
    CC=14  in:1  out:118  total:119
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  wup.cli.sync_testql
    CC=13  in:0  out:45  total:45
  scripts.run_probe_smoke.main
    CC=14  in:0  out:38  total:38
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=2  in:1  out:26  total:27
  wup.monitoring_manifest.build_monitoring_manifest
    CC=9  in:4  out:15  total:19
  wup.visual_diff._fetch_dom_snapshot
    CC=9  in:1  out:17  total:18
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:18  total:18
  examples.testql_demo.simulate_testql_analysis
    CC=2  in:0  out:18  total:18
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.config.load_config
    CC=5  in:9  out:8  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.monitoring_manifest.load_monitoring_manifest_from_yaml
    CC=9  in:2  out:14  total:16
  wup.config.save_config
    CC=2  in:3  out:12  total:15

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
  scripts.run_probe_smoke  [1 funcs]
    main  CC=14  out:38
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.cli  [6 funcs]
    _auto_generate_config  CC=3  out:13
    _load_watch_config  CC=4  out:3
    _refresh_monitoring_manifest  CC=3  out:4
    init  CC=3  out:16
    status  CC=5  out:121
    sync_testql  CC=13  out:45
  wup.cli_config_generator  [1 funcs]
    generate  CC=4  out:5
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:12
    validate_config  CC=14  out:118
  wup.core  [1 funcs]
    __init__  CC=7  out:18
  wup.monitoring_manifest  [13 funcs]
    _build_docker_rows  CC=5  out:3
    _build_scenario_rows  CC=5  out:8
    _build_wup_service_dicts  CC=3  out:2
    _extract_healthcheck_test  CC=6  out:7
    _extract_service_from_spec  CC=7  out:12
    _load_compose_yaml  CC=5  out:5
    _map_docker_to_wup_service  CC=11  out:7
    _parse_port_mapping  CC=5  out:4
    build_monitoring_manifest  CC=9  out:15
    discover_docker_compose_services  CC=7  out:10
  wup.testql_monitor  [24 funcs]
    _add_config_endpoints  CC=11  out:13
    _add_scenario_probes  CC=5  out:5
    _add_service_map_probes  CC=5  out:5
    _resolve_base_url  CC=4  out:6
    probes_for_service  CC=9  out:11
    _assign_by_connect_backend  CC=4  out:4
    _assign_by_longest_token  CC=7  out:5
    _assign_by_path_prefix  CC=13  out:7
    _assign_by_port_8100  CC=2  out:3
    _assign_by_port_8101  CC=1  out:1
  wup.testql_watcher  [2 funcs]
    __init__  CC=13  out:14
    _get_config_endpoints_for_service  CC=10  out:7
  wup.visual_diff  [22 funcs]
    __init__  CC=1  out:2
    _categorize_page_result  CC=6  out:12
    _check_page  CC=4  out:9
    _pages_for_service  CC=11  out:8
    _print_scan_summary  CC=8  out:13
    _write_diff_event  CC=1  out:6
    run_for_service  CC=7  out:11
    _compact_error_message  CC=3  out:3
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=5  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._parse_port_mapping
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._extract_healthcheck_test
  wup.monitoring_manifest.discover_docker_compose_services → wup.monitoring_manifest._load_compose_yaml
  wup.monitoring_manifest.discover_docker_compose_services → wup.monitoring_manifest._extract_service_from_spec
  wup.monitoring_manifest._build_docker_rows → wup.monitoring_manifest._map_docker_to_wup_service
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest.discover_docker_compose_services
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_wup_service_dicts
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_docker_rows
  wup.monitoring_manifest.build_monitoring_manifest → wup.monitoring_manifest._build_scenario_rows
  wup.monitoring_manifest.patch_wup_yaml_monitoring → wup.monitoring_manifest.manifest_to_yaml_block
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli._load_watch_config → wup.config.load_config
  wup.cli._refresh_monitoring_manifest → wup.monitoring_manifest.build_monitoring_manifest
  wup.cli._refresh_monitoring_manifest → wup.monitoring_manifest.patch_wup_yaml_monitoring
  wup.cli._auto_generate_config → wup.config.get_default_config
  wup.cli._auto_generate_config → wup.config.save_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.cli.sync_testql → wup.config.load_config
  wup.cli.sync_testql → wup.monitoring_manifest.build_monitoring_manifest
  wup.testql_monitor.parse_scenario_probes → wup.testql_monitor._parse_api_lines
  wup.testql_monitor.parse_service_map_probes → wup.testql_monitor._extract_base_url
  wup.testql_monitor.parse_service_map_probes → wup.testql_monitor._parse_endpoint_row
  wup.testql_monitor.is_monitoring_probe → wup.testql_monitor._connect_module_api_on_frontend_proxy
  wup.testql_monitor.is_monitoring_probe → wup.testql_monitor._firmware_plugin_probe_without_runtime
  wup.testql_monitor._assign_by_port_8101 → wup.testql_monitor._find_service_by_name
  wup.testql_monitor._assign_by_port_8202 → wup.testql_monitor._find_service_by_token
  wup.testql_monitor._assign_by_port_8100 → wup.testql_monitor._find_service_by_name
  wup.testql_monitor._assign_by_port_8100 → wup.testql_monitor._find_service_by_token
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_connect_backend
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8101
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8202
  wup.testql_monitor._assign_http_probe → wup.testql_monitor._assign_by_port_8100
  wup.testql_monitor._assign_by_longest_token → wup.testql_monitor._service_path_patterns
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_by_longest_token
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_by_path_prefix
  wup.testql_monitor.assign_probe_to_service → wup.testql_monitor._assign_http_probe
  wup.testql_monitor.TestQLMonitor._add_config_endpoints → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_config_endpoints → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.parse_scenario_probes
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_scenario_probes → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.parse_service_map_probes
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.assign_probe_to_service
  wup.testql_monitor.TestQLMonitor._add_service_map_probes → wup.testql_monitor.is_monitoring_probe
  wup.testql_monitor.TestQLMonitor.probes_for_service → wup.testql_monitor.is_monitoring_probe
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 62f 10727L | python:41,yaml:10,txt:4,json:2,toml:1,shell:1,yml:1 | 2026-05-22
# generated in 0.02s
# CC̄=4.3 | critical:0/359 | dups:0 | cycles:0

HEALTH[0]: ok

REFACTOR[0]: none needed

PIPELINES[257]:
  [1] Src [__init__]: __init__
      PURITY: 100% pure
  [2] Src [generate]: generate
      PURITY: 100% pure
  [3] Src [_generate_smoke_scenario]: _generate_smoke_scenario
      PURITY: 100% pure
  [4] Src [_generate_command_scenario]: _generate_command_scenario
      PURITY: 100% pure
  [5] Src [generate_custom_scenario]: generate_custom_scenario
      PURITY: 100% pure

LAYERS:
  scripts/                        CC̄=14.0   ←in:0  →out:3
  │ run_probe_smoke             64L  0C    1m  CC=14     ←0
  │
  wup/                            CC̄=4.7    ←in:9  →out:0
  │ !! testql_watcher             858L  2C   41m  CC=13     ←0
  │ !! cli                        799L  0C   14m  CC=13     ←0
  │ !! assistant                  694L  1C   24m  CC=14     ←0
  │ !! core                       663L  2C   28m  CC=11     ←0
  │ !! testql_monitor             521L  3C   36m  CC=13     ←2
  │ !! visual_diff                518L  1C   24m  CC=11     ←1
  │ config                     464L  0C    6m  CC=14     ←7
  │ monitoring_manifest        340L  1C   16m  CC=11     ←2
  │ cli_scanner                302L  3C   12m  CC=10     ←0
  │ dependency_mapper          284L  1C   16m  CC=10     ←0
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ cli_config_generator       223L  1C    6m  CC=6      ←0
  │ testql_cli_generator       215L  1C    6m  CC=6      ←0
  │ planfile_reporter          203L  1C   11m  CC=13     ←0
  │ web_client                 185L  1C   10m  CC=6      ←0
  │ anomaly_detector           175L  1C    8m  CC=7      ←0
  │ config                     165L  12C    0m  CC=0.0    ←0
  │ _yaml_detector             128L  1C    8m  CC=8      ←0
  │ _ast_detector              124L  1C    9m  CC=11     ←1
  │ _hash_detector              72L  1C    4m  CC=5      ←0
  │ __init__                    46L  0C    1m  CC=2      ←0
  │ anomaly_models              35L  2C    0m  CC=0.0    ←0
  │ __init__                    34L  0C    0m  CC=0.0    ←0
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
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ tree.txt                   123L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              75L  0C    0m  CC=0.0    ←0
  │ project.sh                  49L  0C    0m  CC=0.0    ←0
  │ deps.json                    4L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    82L  0C    0m  CC=0.0    ←0
  │ cli-wup.testql.toon.yaml    21L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ cli-smoke.testql.toon.yaml    17L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     examples/flask-app/app/__init__.py        0L

COUPLING:
                 wup  examples   scripts
       wup        ──        ←6        ←3  hub
  examples         6        ──          
   scripts         3                  ──
  CYCLES: none
  HUB: wup/ (fan-in=9)

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 4 groups | 38f 7003L | 2026-05-22

SUMMARY:
  files_scanned: 38
  total_lines:   7003
  dup_groups:    4
  dup_fragments: 10
  saved_lines:   20
  scan_ms:       2321

HOTSPOTS[6] (files with most duplication):
  examples/flask-app/app/auth/routes.py  dup=8L  groups=1  frags=2  (0.1%)
  wup/_ast_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  wup/_hash_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  wup/_yaml_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  examples/visual_diff_demo.py  dup=3L  groups=1  frags=1  (0.0%)
  wup/visual_diff.py  dup=3L  groups=1  frags=1  (0.0%)

DUPLICATES[4] (ranked by impact):
  [b5eae728fdce70c7]   STRU  __init__  L=3 N=3 saved=6 sim=1.00
      wup/_ast_detector.py:16-18  (__init__)
      wup/_hash_detector.py:15-17  (__init__)
      wup/_yaml_detector.py:19-21  (__init__)
  [8575900946923f44]   STRU  _snapshot_path  L=3 N=3 saved=6 sim=1.00
      wup/_ast_detector.py:59-61  (_snapshot_path)
      wup/_hash_detector.py:22-24  (_snapshot_path)
      wup/_yaml_detector.py:49-51  (_snapshot_path)
  [e86dae8501b38602]   STRU  login  L=5 N=2 saved=5 sim=1.00
      examples/flask-app/app/auth/routes.py:7-11  (login)
      examples/flask-app/app/auth/routes.py:20-22  (register)
  [94e52a5e17c9baae]   STRU  _save_snapshot  L=3 N=2 saved=3 sim=1.00
      examples/visual_diff_demo.py:62-64  (_save_snapshot)
      wup/visual_diff.py:222-224  (_save_snapshot)

REFACTOR[4] (ranked by priority):
  [1] ○ extract_function   → wup/utils/__init__.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: wup/_ast_detector.py, wup/_hash_detector.py, wup/_yaml_detector.py
  [2] ○ extract_function   → wup/utils/_snapshot_path.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: wup/_ast_detector.py, wup/_hash_detector.py, wup/_yaml_detector.py
  [3] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: examples/flask-app/app/auth/routes.py
  [4] ○ extract_function   → utils/_save_snapshot.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/visual_diff_demo.py, wup/visual_diff.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=6L  → wup/utils/__init__.py
      FILES: _ast_detector.py, _hash_detector.py, _yaml_detector.py
  [2] extract_function   saved=6L  → wup/utils/_snapshot_path.py
      FILES: _ast_detector.py, _hash_detector.py, _yaml_detector.py

DEPENDENCY_RISK[1] (duplicates spanning multiple packages):
  _save_snapshot  packages=2  files=2
      examples/visual_diff_demo.py
      wup/visual_diff.py

EFFORT_ESTIMATE (total ≈ 0.8h):
  easy   __init__                            saved=6L  ~12min
  easy   _snapshot_path                      saved=6L  ~12min
  easy   login                               saved=5L  ~10min
  easy   _save_snapshot                      saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  4 → 0
  saved_lines: 20 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 287 func | 20f | 2026-05-22
# generated in 0.00s

NEXT[3] (ranked by impact):
  [1] !! SPLIT           wup/testql_watcher.py
      WHY: 858L, 2 classes, max CC=13
      EFFORT: ~4h  IMPACT: 11154

  [2] !! SPLIT           wup/cli.py
      WHY: 799L, 0 classes, max CC=13
      EFFORT: ~4h  IMPACT: 10387

  [3] !! SPLIT           wup/assistant.py
      WHY: 694L, 1 classes, max CC=14
      EFFORT: ~4h  IMPACT: 9716


RISKS[3]:
  ⚠ Splitting wup/testql_watcher.py may break 41 import paths
  ⚠ Splitting wup/cli.py may break 14 import paths
  ⚠ Splitting wup/assistant.py may break 24 import paths

METRICS-TARGET:
  CC̄:          4.7 → ≤3.3
  max-CC:      14 → ≤7
  god-modules: 7 → 0
  high-CC(≥15): 0 → ≤0
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
  prev CC̄=4.8 → now CC̄=4.7
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
