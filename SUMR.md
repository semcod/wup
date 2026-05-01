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
- **version**: `0.2.20`
- **python_requires**: `>=3.9`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(14 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.20;
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
- `wup.config`
- `wup.core`
- `wup.dependency_mapper`
- `wup.testql_discovery`
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

### `wup.core` (`wup/core.py`)

```python
class WupWatcher:  # Intelligent file watcher for regression testing.
    def __init__(project_root, deps_file, cpu_throttle, debounce_seconds, test_cooldown_seconds, config)  # CC=1
    def _to_relative_path(file_path)  # CC=2
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
    def run_quick_test(service, endpoints)  # CC=2
    def run_detail_test(service, endpoints)  # CC=3
    def test_loop()  # CC=2
    def should_watch_file(file_path)  # CC=3
    def on_file_change(file_path)  # CC=14 ⚠
    def build_watched_paths()  # CC=6
    def start_watching(watch_paths)  # CC=8
    def create_status_table()  # CC=3
    def run_with_dashboard()  # CC=6
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

### `wup.testql_watcher` (`wup/testql_watcher.py`)

```python
class BrowserNotifier:  # Send watcher events to browser-facing service and local file
    def __init__(service_url, events_file)  # CC=12 ⚠
    def notify(payload)  # CC=3
class TestQLWatcher:  # WUP watcher running selective TestQL scenarios for changed s
    def __init__(project_root, scenarios_dir, testql_bin, track_dir, browser_service_url, quick_limit, config)  # CC=12 ⚠
    def _load_service_health()  # CC=4
    def _save_service_health()  # CC=1
    def _record_health_transition()  # CC=6
    def _tokenize_service(service)  # CC=3
    def _get_config_endpoints_for_service(service)  # CC=5
    def _resolve_base_url()  # CC=5
    def _to_full_url(endpoint)  # CC=5
    def _discover_scenarios()  # CC=2
    def get_service_config(service_name)  # CC=3
    def _score_scenario(scenario, tokens)  # CC=7
    def _select_scenarios_for_service(service)  # CC=9
    def _run_testql(args, timeout)  # CC=2
    def _write_track()  # CC=11 ⚠
    def _quick_timeout()  # CC=3
    def _merge_endpoints(service, endpoints)  # CC=3
    def _run_scenario_quick(service, scenario, merged_endpoints)  # CC=6
    def _quick_pass_actions(service, merged_endpoints)  # CC=4
    def run_quick_test(service, endpoints)  # CC=8
    def _publish_visual_events(service, visual_results)  # CC=6
    def run_detail_test(service, endpoints)  # CC=9
    def process_changed_file_once(file_path)  # CC=4
```

### `wup.visual_diff` (`wup/visual_diff.py`)

```python
def _playwright_available()  # CC=3, fan=0
def _fetch_dom_snapshot(url, max_depth, headless, error_selectors)  # CC=9, fan=13
def _detect_content_issues(snapshot, cfg)  # CC=6, fan=5
def _page_slug(url)  # CC=2, fan=3
def _snapshot_path(snapshot_dir, service, url)  # CC=1, fan=2
def _load_snapshot(path)  # CC=3, fan=3
def _save_snapshot(path, snapshot)  # CC=1, fan=3
def _node_signature(node, depth)  # CC=3, fan=3
def _flatten(node, depth, max_depth)  # CC=4, fan=4
def _diff_snapshots(old, new, max_depth, threshold_added, threshold_removed, threshold_changed)  # CC=11, fan=5 ⚠
def _resolve_base_url(cfg)  # CC=3, fan=2
class VisualDiffer:  # Triggered by TestQLWatcher after a file change.
    def __init__(project_root, cfg)  # CC=1
    def _pages_for_service(service, endpoints)  # CC=8
    def run_for_service(service, endpoints)  # CC=7
    def _check_page(service, url)  # CC=3
    def _write_diff_event(service, url, result)  # CC=1
    def get_recent_diffs(seconds)  # CC=7
```

### `wup.dependency_mapper` (`wup/dependency_mapper.py`)

```python
class DependencyMapper:  # Maps project dependencies for intelligent testing.
    def __init__(project_root)  # CC=1
    def build_from_codebase(framework)  # CC=5
    def _detect_framework()  # CC=4
    def _search_codebase(pattern)  # CC=4
    def _scan_endpoints(framework)  # CC=3
    def _scan_python_endpoints(framework)  # CC=10 ⚠
    def _scan_js_endpoints()  # CC=4
    def _infer_service(file_path)  # CC=6
    def get_endpoints_for_file(file_path)  # CC=1
    def get_endpoints_for_service(service)  # CC=1
    def get_files_for_service(service)  # CC=1
    def get_service_for_file(file_path)  # CC=3
    def to_dict()  # CC=2
    def save(output_path)  # CC=1
    def load(input_path)  # CC=2
    def build_from_testql_scenarios(scenarios_dir, testql_bin)  # CC=3
```

## Call Graph

*49 nodes · 42 edges · 12 modules · CC̄=2.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `status` *(in wup.cli)* | 5 | 0 | 97 | **97** |
| `analyze_monorepo` *(in examples.c2004_monorepo_demo)* | 22 ⚠ | 1 | 94 | **95** |
| `validate_config` *(in wup.config)* | 7 | 1 | 87 | **88** |
| `show_ci_cd_demo` *(in examples.ci_cd_integration)* | 2 | 1 | 69 | **70** |
| `show_webhook_demo` *(in examples.webhook_notifications)* | 4 | 1 | 68 | **69** |
| `_run_with_mock_services` *(in examples.testql_demo)* | 6 | 2 | 60 | **62** |
| `demo_snapshot_persistence` *(in examples.visual_diff_demo)* | 3 | 1 | 26 | **27** |
| `simulate_testql_analysis` *(in examples.testql_demo)* | 2 | 0 | 18 | **18** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# nodes: 49 | edges: 42 | modules: 12
# CC̄=2.8

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=22  in:1  out:94  total:95
  wup.config.validate_config
    CC=7  in:1  out:87  total:88
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  examples.testql_demo.simulate_testql_analysis
    CC=2  in:0  out:18  total:18
  wup.visual_diff._fetch_dom_snapshot
    CC=9  in:1  out:17  total:18
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  wup.config.load_config
    CC=5  in:6  out:8  total:14
  wup.config.save_config
    CC=2  in:2  out:12  total:14
  examples.testql_demo.simulate_with_mock_data
    CC=1  in:1  out:12  total:13
  wup.testql_watcher.TestQLWatcher.__init__
    CC=12  in:0  out:12  total:12

MODULES:
  examples.c2004_monorepo_demo  [2 funcs]
    analyze_monorepo  CC=22  out:94
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
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:12
    validate_config  CC=7  out:87
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.testql_watcher  [2 funcs]
    __init__  CC=12  out:12
    _resolve_base_url  CC=5  out:6
  wup.visual_diff  [13 funcs]
    __init__  CC=1  out:2
    _check_page  CC=3  out:8
    _write_diff_event  CC=1  out:6
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
    _fetch_dom_snapshot  CC=9  out:17
    _flatten  CC=4  out:5
    _load_snapshot  CC=3  out:3
    _node_signature  CC=3  out:4
    _page_slug  CC=2  out:3
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.core.WupWatcher.__init__ → wup.config.load_config
  wup.web_client.WebClient.__init__ → wup.web_client.resolve_endpoint
  wup.web_client.WebClient.send_event → wup.web_client._normalize
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  wup.visual_diff._fetch_dom_snapshot → wup.visual_diff._playwright_available
  wup.visual_diff._snapshot_path → wup.visual_diff._page_slug
  wup.visual_diff._flatten → wup.visual_diff._node_signature
  wup.visual_diff._diff_snapshots → wup.visual_diff._flatten
  wup.visual_diff.VisualDiffer.__init__ → wup.testql_watcher.TestQLWatcher._resolve_base_url
  wup.visual_diff.VisualDiffer._check_page → wup._ast_detector.ASTDetector._snapshot_path
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._load_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._diff_snapshots
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._detect_content_issues
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._save_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._fetch_dom_snapshot
  wup.visual_diff.VisualDiffer._write_diff_event → wup.visual_diff._page_slug
  examples.c2004_monorepo_demo.main → examples.c2004_monorepo_demo.analyze_monorepo
  examples.visual_diff_demo.demo_diff_algorithm → examples.visual_diff_demo._make_dom
  examples.visual_diff_demo.demo_diff_algorithm → wup.visual_diff._diff_snapshots
  examples.visual_diff_demo.demo_page_slug → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_testql_analysis → examples.testql_demo._build_mock_services
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo._build_mock_services
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo._run_with_mock_services
  examples.ci_cd_integration.main → examples.ci_cd_integration.generate_github_actions
  examples.ci_cd_integration.main → examples.ci_cd_integration.generate_gitlab_ci
  examples.ci_cd_integration.main → examples.ci_cd_integration.show_ci_cd_demo
  examples.webhook_notifications.main → examples.webhook_notifications.show_webhook_demo
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

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
# nodes: 49 | edges: 42 | modules: 12
# CC̄=2.8

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=22  in:1  out:94  total:95
  wup.config.validate_config
    CC=7  in:1  out:87  total:88
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  examples.testql_demo.simulate_testql_analysis
    CC=2  in:0  out:18  total:18
  wup.visual_diff._fetch_dom_snapshot
    CC=9  in:1  out:17  total:18
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  wup.config.load_config
    CC=5  in:6  out:8  total:14
  wup.config.save_config
    CC=2  in:2  out:12  total:14
  examples.testql_demo.simulate_with_mock_data
    CC=1  in:1  out:12  total:13
  wup.testql_watcher.TestQLWatcher.__init__
    CC=12  in:0  out:12  total:12

MODULES:
  examples.c2004_monorepo_demo  [2 funcs]
    analyze_monorepo  CC=22  out:94
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
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:12
    validate_config  CC=7  out:87
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.testql_watcher  [2 funcs]
    __init__  CC=12  out:12
    _resolve_base_url  CC=5  out:6
  wup.visual_diff  [13 funcs]
    __init__  CC=1  out:2
    _check_page  CC=3  out:8
    _write_diff_event  CC=1  out:6
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
    _fetch_dom_snapshot  CC=9  out:17
    _flatten  CC=4  out:5
    _load_snapshot  CC=3  out:3
    _node_signature  CC=3  out:4
    _page_slug  CC=2  out:3
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.core.WupWatcher.__init__ → wup.config.load_config
  wup.web_client.WebClient.__init__ → wup.web_client.resolve_endpoint
  wup.web_client.WebClient.send_event → wup.web_client._normalize
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  wup.visual_diff._fetch_dom_snapshot → wup.visual_diff._playwright_available
  wup.visual_diff._snapshot_path → wup.visual_diff._page_slug
  wup.visual_diff._flatten → wup.visual_diff._node_signature
  wup.visual_diff._diff_snapshots → wup.visual_diff._flatten
  wup.visual_diff.VisualDiffer.__init__ → wup.testql_watcher.TestQLWatcher._resolve_base_url
  wup.visual_diff.VisualDiffer._check_page → wup._ast_detector.ASTDetector._snapshot_path
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._load_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._diff_snapshots
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._detect_content_issues
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._save_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._fetch_dom_snapshot
  wup.visual_diff.VisualDiffer._write_diff_event → wup.visual_diff._page_slug
  examples.c2004_monorepo_demo.main → examples.c2004_monorepo_demo.analyze_monorepo
  examples.visual_diff_demo.demo_diff_algorithm → examples.visual_diff_demo._make_dom
  examples.visual_diff_demo.demo_diff_algorithm → wup.visual_diff._diff_snapshots
  examples.visual_diff_demo.demo_page_slug → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_testql_analysis → examples.testql_demo._build_mock_services
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo._build_mock_services
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo._run_with_mock_services
  examples.ci_cd_integration.main → examples.ci_cd_integration.generate_github_actions
  examples.ci_cd_integration.main → examples.ci_cd_integration.generate_gitlab_ci
  examples.ci_cd_integration.main → examples.ci_cd_integration.show_ci_cd_demo
  examples.webhook_notifications.main → examples.webhook_notifications.show_webhook_demo
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 61f 9306L | python:34,yaml:15,txt:5,json:2,toml:1,shell:1,yml:1 | 2026-05-01
# CC̄=2.8 | critical:2/312 | dups:0 | cycles:2

HEALTH[2]:
  🟡 CC    _extract_ast_info CC=16 (limit:15)
  🟡 CC    analyze_monorepo CC=22 (limit:15)

REFACTOR[2]:
  1. split 2 high-CC methods  (CC>15)
  2. break 2 circular dependencies

PIPELINES[178]:
  [1] Src [__init__]: __init__
      PURITY: 100% pure
  [2] Src [_should_scan]: _should_scan
      PURITY: 100% pure
  [3] Src [scan_file]: scan_file
      PURITY: 100% pure
  [4] Src [scan_directory]: scan_directory
      PURITY: 100% pure
  [5] Src [get_summary]: get_summary
      PURITY: 100% pure

LAYERS:
  wup/                            CC̄=4.5    ←in:6  →out:0
  │ !! assistant                  694L  1C   24m  CC=14     ←0
  │ !! core                       590L  2C   25m  CC=14     ←0
  │ !! testql_watcher             512L  2C   24m  CC=12     ←1
  │ cli                        478L  0C    7m  CC=6      ←0
  │ config                     405L  0C    6m  CC=10     ←5
  │ visual_diff                388L  1C   17m  CC=11     ←1
  │ dependency_mapper          284L  1C   16m  CC=10     ←0
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ web_client                 178L  1C   10m  CC=6      ←0
  │ anomaly_detector           175L  1C    8m  CC=7      ←0
  │ config                     138L  11C    0m  CC=0.0    ←0
  │ _yaml_detector             128L  1C    8m  CC=8      ←0
  │ !! _ast_detector              116L  1C    5m  CC=16     ←1
  │ _hash_detector              72L  1C    4m  CC=5      ←0
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ anomaly_models              35L  2C    0m  CC=0.0    ←0
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.5    ←in:0  →out:6
  │ webhook_notifications      427L  1C   10m  CC=6      ←0
  │ ci_cd_integration          337L  0C    4m  CC=3      ←0
  │ visual_diff_demo           271L  0C    9m  CC=6      ←0
  │ testql_integration         267L  1C    6m  CC=6      ←0
  │ !! c2004_monorepo_demo        229L  0C    3m  CC=22     ←0
  │ testql_demo                192L  0C    4m  CC=6      ←0
  │ routes                      38L  1C    5m  CC=1      ←0
  │ docker-compose.yml          33L  0C    0m  CC=0.0    ←0
  │ routes                      31L  0C    5m  CC=2      ←0
  │ wup.yaml                    28L  0C    0m  CC=0.0    ←0
  │ wup.yaml                    28L  0C    0m  CC=0.0    ←0
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
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │ __init__                     0L  0C    0m  CC=0.0    ←0
  │ Dockerfile                   0L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                 802L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              280L  0C   87m  CC=0.0    ←0
  │ calls.toon.yaml            146L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         110L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       68L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         58L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           54L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ tree.txt                   110L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              71L  0C    0m  CC=0.0    ←0
  │ project.sh                  49L  0C    0m  CC=0.0    ←0
  │ deps.json                    4L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    82L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     examples/flask-app/Dockerfile             0L
     examples/flask-app/app/__init__.py        0L
     examples/multi-service/payments-service/Dockerfile  0L

COUPLING:
            examples       wup
  examples        ──         6
       wup        ←6        ──  hub
  CYCLES: 2
  HUB: wup/ (fan-in=6)

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 4 groups | 33f 5224L | 2026-05-01

SUMMARY:
  files_scanned: 33
  total_lines:   5224
  dup_groups:    4
  dup_fragments: 10
  saved_lines:   18
  scan_ms:       3795

HOTSPOTS[6] (files with most duplication):
  wup/_ast_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  wup/_hash_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  wup/_yaml_detector.py  dup=6L  groups=2  frags=2  (0.1%)
  examples/flask-app/app/auth/routes.py  dup=6L  groups=1  frags=2  (0.1%)
  examples/visual_diff_demo.py  dup=3L  groups=1  frags=1  (0.1%)
  wup/visual_diff.py  dup=3L  groups=1  frags=1  (0.1%)

DUPLICATES[4] (ranked by impact):
  [b5eae728fdce70c7]   STRU  __init__  L=3 N=3 saved=6 sim=1.00
      wup/_ast_detector.py:16-18  (__init__)
      wup/_hash_detector.py:15-17  (__init__)
      wup/_yaml_detector.py:19-21  (__init__)
  [8575900946923f44]   STRU  _snapshot_path  L=3 N=3 saved=6 sim=1.00
      wup/_ast_detector.py:51-53  (_snapshot_path)
      wup/_hash_detector.py:22-24  (_snapshot_path)
      wup/_yaml_detector.py:49-51  (_snapshot_path)
  [e86dae8501b38602]   STRU  login  L=3 N=2 saved=3 sim=1.00
      examples/flask-app/app/auth/routes.py:7-9  (login)
      examples/flask-app/app/auth/routes.py:18-20  (register)
  [94e52a5e17c9baae]   STRU  _save_snapshot  L=3 N=2 saved=3 sim=1.00
      examples/visual_diff_demo.py:55-57  (_save_snapshot)
      wup/visual_diff.py:164-166  (_save_snapshot)

REFACTOR[4] (ranked by priority):
  [1] ○ extract_function   → wup/utils/__init__.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: wup/_ast_detector.py, wup/_hash_detector.py, wup/_yaml_detector.py
  [2] ○ extract_function   → wup/utils/_snapshot_path.py
      WHY: 3 occurrences of 3-line block across 3 files — saves 6 lines
      FILES: wup/_ast_detector.py, wup/_hash_detector.py, wup/_yaml_detector.py
  [3] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
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

EFFORT_ESTIMATE (total ≈ 0.7h):
  easy   __init__                            saved=6L  ~12min
  easy   _snapshot_path                      saved=6L  ~12min
  easy   login                               saved=3L  ~6min
  easy   _save_snapshot                      saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  4 → 0
  saved_lines: 18 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 248 func | 14f | 2026-05-01

NEXT[4] (ranked by impact):
  [1] !! SPLIT           wup/assistant.py
      WHY: 694L, 1 classes, max CC=14
      EFFORT: ~4h  IMPACT: 9716

  [2] !! SPLIT           wup/core.py
      WHY: 590L, 2 classes, max CC=14
      EFFORT: ~4h  IMPACT: 8260

  [3] !! SPLIT           wup/testql_watcher.py
      WHY: 512L, 2 classes, max CC=12
      EFFORT: ~4h  IMPACT: 6144

  [4] !  SPLIT-FUNC      ASTDetector._extract_ast_info  CC=16  fan=7
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 112


RISKS[3]:
  ⚠ Splitting wup/assistant.py may break 24 import paths
  ⚠ Splitting wup/core.py may break 25 import paths
  ⚠ Splitting wup/testql_watcher.py may break 24 import paths

METRICS-TARGET:
  CC̄:          2.9 → ≤2.0
  max-CC:      16 → ≤8
  god-modules: 3 → 0
  high-CC(≥15): 1 → ≤0
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
  prev CC̄=2.9 → now CC̄=2.9
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
