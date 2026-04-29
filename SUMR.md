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
- **version**: `0.2.17`
- **python_requires**: `>=3.9`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(10 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.17;
}

dependencies {
  runtime: "watchdog>=4.0.0, psutil>=5.9.0, rich>=13.0.0, typer>=0.9.0, pyyaml>=6.0";
}

entity[name="Event"] {
  type: EventType!;
  service: string;
  file: string;
  endpoint: string;
  url: string;
  status: string;
  stage: string;
  reason: string;
  diff: Dict[str, Any];
  timestamp: int!;
}

entity[name="EventList"] {
  items: List[Event]!;
  total: int!;
}

entity[name="AnomalyReport"] {
  service: string!;
  metric: string!;
  value: float!;
  threshold: float!;
  timestamp: int!;
}

entity[name="NotificationConfig"] {
  enabled: bool!;
  regression_new: bool!;
  regression_diff: bool!;
  regression_diff_seconds: int!;
  status_transition: bool!;
  status_transition_type: StatusTransitionType!;
  anomaly_new: bool!;
  visual_diff_new: bool!;
  health_change: bool!;
  pass_recovery: bool!;
  cooldown_seconds: int!;
  services_include: List[str]!;
  services_exclude: List[str]!;
}

entity[name="NotificationSubscription"] {
  subscription_id: string!;
  config: NotificationConfig!;
  created_at: int!;
  last_notification_at: int;
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

- `wup.anomaly_detector`
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
    def detect_service_coincidences(changed_service)  # CC=19 ⚠
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

### `wup.anomaly_detector` (`wup/anomaly_detector.py`)

```python
def quick_scan(project_root, files)  # CC=2, fan=3
def scan_yaml_changes(project_root, yaml_dir)  # CC=1, fan=3
class AnomalyResult:  # Result of anomaly detection.
class YAMLAnomalyConfig:  # Configuration for YAML anomaly detection.
class HashDetector:  # Fast anomaly detection using file hashes.
    def __init__(snapshot_dir)  # CC=6
    def _compute_hash(content)  # CC=1
    def _snapshot_path(file_path)  # CC=1
    def detect(file_path)  # CC=16 ⚠
class YAMLStructureDetector:  # Detect structural changes in YAML files.
    def __init__(snapshot_dir)  # CC=6
    def _load_yaml(file_path)  # CC=2
    def _extract_structure(data, depth, max_depth)  # CC=6
    def _snapshot_path(file_path)  # CC=1
    def _compare_structures(old, new, path)  # CC=15 ⚠
    def detect(file_path)  # CC=16 ⚠
    def _generate_suggestions(diffs)  # CC=6
class ASTDetector:  # Detect changes in Python files using AST comparison.
    def __init__(snapshot_dir)  # CC=6
    def _extract_ast_info(tree)  # CC=16 ⚠
    def _snapshot_path(file_path)  # CC=1
    def detect(file_path)  # CC=16 ⚠
class AnomalyDetector:  # Main anomaly detector combining multiple detection methods.
    def __init__(project_root, config)  # CC=6
    def _should_scan(file_path)  # CC=7
    def scan_file(file_path)  # CC=6
    def scan_directory(directory, pattern, recursive)  # CC=6
    def get_summary(results)  # CC=2
    def print_report(results)  # CC=6
```

### `wup.assistant` (`wup/assistant.py`)

```python
def main()  # CC=1, fan=5
class WupAssistant:  # Interactive configuration assistant.
    def __init__(project_root)  # CC=1
    def run(quick, template)  # CC=16 ⚠
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
    def _select_scenarios_for_service(service)  # CC=15 ⚠
    def _run_testql(args, timeout)  # CC=2
    def _write_track()  # CC=11 ⚠
    def run_quick_test(service, endpoints)  # CC=15 ⚠
    def run_detail_test(service, endpoints)  # CC=9
    def process_changed_file_once(file_path)  # CC=4
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

*71 nodes · 61 edges · 21 modules · CC̄=2.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `status` *(in wup.cli)* | 5 | 0 | 97 | **97** |
| `analyze_monorepo` *(in examples.c2004_monorepo_demo)* | 22 ⚠ | 1 | 94 | **95** |
| `validate_config` *(in wup.config)* | 7 | 1 | 82 | **83** |
| `simulate_testql_analysis` *(in examples.testql_demo)* | 11 ⚠ | 1 | 80 | **81** |
| `show_ci_cd_demo` *(in examples.ci_cd_integration)* | 2 | 1 | 69 | **70** |
| `show_webhook_demo` *(in examples.webhook_notifications)* | 4 | 1 | 68 | **69** |
| `demo_snapshot_persistence` *(in examples.visual_diff_demo)* | 3 | 1 | 26 | **27** |
| `run_quick_test` *(in wup.testql_watcher.TestQLWatcher)* | 15 ⚠ | 0 | 23 | **23** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# nodes: 71 | edges: 61 | modules: 21
# CC̄=2.7

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=22  in:1  out:94  total:95
  wup.config.validate_config
    CC=7  in:1  out:82  total:83
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  wup.testql_watcher.TestQLWatcher.run_quick_test
    CC=15  in:0  out:23  total:23
  wupbro.wupbro.storage.EventStore.list
    CC=7  in:17  out:5  total:22
  wup.testql_watcher.TestQLWatcher.run_detail_test
    CC=9  in:0  out:20  total:20
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
    CC=11  in:0  out:16  total:16
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.anomaly_detector.AnomalyDetector.scan_directory
    CC=6  in:0  out:16  total:16
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  wupbro.wupbro.routers.notifications.notification_stream
    CC=2  in:0  out:14  total:14

MODULES:
  examples.c2004_monorepo_demo  [2 funcs]
    analyze_monorepo  CC=22  out:94
    main  CC=2  out:2
  examples.ci_cd_integration  [4 funcs]
    generate_github_actions  CC=1  out:9
    generate_gitlab_ci  CC=3  out:10
    main  CC=3  out:7
    show_ci_cd_demo  CC=2  out:69
  examples.testql_demo  [2 funcs]
    simulate_testql_analysis  CC=11  out:80
    simulate_with_mock_data  CC=1  out:3
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
  project.map.toon  [3 funcs]
    get_default_config  CC=0  out:0
    load_config  CC=0  out:0
    save_config  CC=0  out:0
  wup.anomaly_detector  [2 funcs]
    scan_directory  CC=6  out:16
    _extract_structure  CC=6  out:9
  wup.assistant  [2 funcs]
    _configure_testql  CC=3  out:12
    _detect_service_type  CC=10  out:9
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [5 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    validate_config  CC=7  out:82
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.dependency_mapper  [1 funcs]
    to_dict  CC=2  out:7
  wup.testql_discovery  [2 funcs]
    discover_all_endpoints  CC=6  out:9
    parse_scenario_endpoints  CC=11  out:16
  wup.testql_watcher  [3 funcs]
    __init__  CC=12  out:12
    run_detail_test  CC=9  out:20
    run_quick_test  CC=15  out:23
  wup.visual_diff  [14 funcs]
    __init__  CC=1  out:2
    _check_page  CC=2  out:7
    _pages_for_service  CC=8  out:6
    _write_diff_event  CC=1  out:6
    _diff_snapshots  CC=11  out:15
    _fetch_dom_snapshot  CC=3  out:9
    _flatten  CC=4  out:5
    _load_snapshot  CC=3  out:3
    _node_signature  CC=3  out:4
    _page_slug  CC=2  out:3
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3
  wupbro.wupbro.notifications  [2 funcs]
    list_subscriptions  CC=1  out:2
    get_notification_manager  CC=3  out:2
  wupbro.wupbro.routers.drivers  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.routers.events  [2 funcs]
    _store  CC=1  out:1
    post_event  CC=2  out:7
  wupbro.wupbro.routers.notifications  [7 funcs]
    get_subscription  CC=2  out:4
    list_subscriptions  CC=1  out:3
    notification_stream  CC=2  out:14
    send_test_notification  CC=2  out:6
    subscribe  CC=2  out:6
    unsubscribe  CC=2  out:4
    update_subscription  CC=2  out:4
  wupbro.wupbro.storage  [2 funcs]
    list  CC=7  out:5
    get_default_store  CC=2  out:2

EDGES:
  wup.dependency_mapper.DependencyMapper.to_dict → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.core.WupWatcher.__init__ → project.map.toon.load_config
  wup.visual_diff._fetch_dom_snapshot → wup.visual_diff._playwright_available
  wup.visual_diff._snapshot_path → wup.visual_diff._page_slug
  wup.visual_diff._flatten → wup.visual_diff._node_signature
  wup.visual_diff._diff_snapshots → wup.visual_diff._flatten
  wup.visual_diff.VisualDiffer.__init__ → wup.visual_diff._resolve_base_url
  wup.visual_diff.VisualDiffer._pages_for_service → wupbro.wupbro.storage.EventStore.list
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._snapshot_path
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._load_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._diff_snapshots
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._save_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._fetch_dom_snapshot
  wup.visual_diff.VisualDiffer._write_diff_event → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_diff_algorithm → examples.visual_diff_demo._make_dom
  examples.visual_diff_demo.demo_diff_algorithm → wup.visual_diff._diff_snapshots
  examples.visual_diff_demo.demo_page_slug → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_config_yaml_round_trip → project.map.toon.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → project.map.toon.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
  wup.web_client.WebClient.__init__ → wup.web_client.resolve_endpoint
  wup.web_client.WebClient.send_event → wup.web_client._normalize
  wupbro.wupbro.routers.events._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.events.post_event → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.drivers._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.notifications.NotificationManager.list_subscriptions → wupbro.wupbro.storage.EventStore.list
  wupbro.wupbro.notifications.get_notification_manager → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.notifications.subscribe → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.list_subscriptions → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.get_subscription → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.update_subscription → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.unsubscribe → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.notification_stream → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.send_test_notification → wupbro.wupbro.notifications.get_notification_manager
  examples.webhook_notifications.main → examples.webhook_notifications.show_webhook_demo
  examples.c2004_monorepo_demo.main → examples.c2004_monorepo_demo.analyze_monorepo
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.testql_watcher.TestQLWatcher.__init__ → project.map.toon.load_config
  wup.testql_watcher.TestQLWatcher.run_quick_test → wupbro.wupbro.storage.EventStore.list
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
# nodes: 71 | edges: 61 | modules: 21
# CC̄=2.7

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=22  in:1  out:94  total:95
  wup.config.validate_config
    CC=7  in:1  out:82  total:83
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  wup.testql_watcher.TestQLWatcher.run_quick_test
    CC=15  in:0  out:23  total:23
  wupbro.wupbro.storage.EventStore.list
    CC=7  in:17  out:5  total:22
  wup.testql_watcher.TestQLWatcher.run_detail_test
    CC=9  in:0  out:20  total:20
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
    CC=11  in:0  out:16  total:16
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.anomaly_detector.AnomalyDetector.scan_directory
    CC=6  in:0  out:16  total:16
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  wupbro.wupbro.routers.notifications.notification_stream
    CC=2  in:0  out:14  total:14

MODULES:
  examples.c2004_monorepo_demo  [2 funcs]
    analyze_monorepo  CC=22  out:94
    main  CC=2  out:2
  examples.ci_cd_integration  [4 funcs]
    generate_github_actions  CC=1  out:9
    generate_gitlab_ci  CC=3  out:10
    main  CC=3  out:7
    show_ci_cd_demo  CC=2  out:69
  examples.testql_demo  [2 funcs]
    simulate_testql_analysis  CC=11  out:80
    simulate_with_mock_data  CC=1  out:3
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
  project.map.toon  [3 funcs]
    get_default_config  CC=0  out:0
    load_config  CC=0  out:0
    save_config  CC=0  out:0
  wup.anomaly_detector  [2 funcs]
    scan_directory  CC=6  out:16
    _extract_structure  CC=6  out:9
  wup.assistant  [2 funcs]
    _configure_testql  CC=3  out:12
    _detect_service_type  CC=10  out:9
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [5 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    validate_config  CC=7  out:82
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.dependency_mapper  [1 funcs]
    to_dict  CC=2  out:7
  wup.testql_discovery  [2 funcs]
    discover_all_endpoints  CC=6  out:9
    parse_scenario_endpoints  CC=11  out:16
  wup.testql_watcher  [3 funcs]
    __init__  CC=12  out:12
    run_detail_test  CC=9  out:20
    run_quick_test  CC=15  out:23
  wup.visual_diff  [14 funcs]
    __init__  CC=1  out:2
    _check_page  CC=2  out:7
    _pages_for_service  CC=8  out:6
    _write_diff_event  CC=1  out:6
    _diff_snapshots  CC=11  out:15
    _fetch_dom_snapshot  CC=3  out:9
    _flatten  CC=4  out:5
    _load_snapshot  CC=3  out:3
    _node_signature  CC=3  out:4
    _page_slug  CC=2  out:3
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3
  wupbro.wupbro.notifications  [2 funcs]
    list_subscriptions  CC=1  out:2
    get_notification_manager  CC=3  out:2
  wupbro.wupbro.routers.drivers  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.routers.events  [2 funcs]
    _store  CC=1  out:1
    post_event  CC=2  out:7
  wupbro.wupbro.routers.notifications  [7 funcs]
    get_subscription  CC=2  out:4
    list_subscriptions  CC=1  out:3
    notification_stream  CC=2  out:14
    send_test_notification  CC=2  out:6
    subscribe  CC=2  out:6
    unsubscribe  CC=2  out:4
    update_subscription  CC=2  out:4
  wupbro.wupbro.storage  [2 funcs]
    list  CC=7  out:5
    get_default_store  CC=2  out:2

EDGES:
  wup.dependency_mapper.DependencyMapper.to_dict → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.core.WupWatcher.__init__ → project.map.toon.load_config
  wup.visual_diff._fetch_dom_snapshot → wup.visual_diff._playwright_available
  wup.visual_diff._snapshot_path → wup.visual_diff._page_slug
  wup.visual_diff._flatten → wup.visual_diff._node_signature
  wup.visual_diff._diff_snapshots → wup.visual_diff._flatten
  wup.visual_diff.VisualDiffer.__init__ → wup.visual_diff._resolve_base_url
  wup.visual_diff.VisualDiffer._pages_for_service → wupbro.wupbro.storage.EventStore.list
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._snapshot_path
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._load_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._diff_snapshots
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._save_snapshot
  wup.visual_diff.VisualDiffer._check_page → wup.visual_diff._fetch_dom_snapshot
  wup.visual_diff.VisualDiffer._write_diff_event → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_diff_algorithm → examples.visual_diff_demo._make_dom
  examples.visual_diff_demo.demo_diff_algorithm → wup.visual_diff._diff_snapshots
  examples.visual_diff_demo.demo_page_slug → wup.visual_diff._page_slug
  examples.visual_diff_demo.demo_config_yaml_round_trip → project.map.toon.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → project.map.toon.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
  wup.web_client.WebClient.__init__ → wup.web_client.resolve_endpoint
  wup.web_client.WebClient.send_event → wup.web_client._normalize
  wupbro.wupbro.routers.events._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.events.post_event → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.drivers._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.notifications.NotificationManager.list_subscriptions → wupbro.wupbro.storage.EventStore.list
  wupbro.wupbro.notifications.get_notification_manager → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.notifications.subscribe → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.list_subscriptions → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.get_subscription → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.update_subscription → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.unsubscribe → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.notification_stream → wupbro.wupbro.notifications.get_notification_manager
  wupbro.wupbro.routers.notifications.send_test_notification → wupbro.wupbro.notifications.get_notification_manager
  examples.webhook_notifications.main → examples.webhook_notifications.show_webhook_demo
  examples.c2004_monorepo_demo.main → examples.c2004_monorepo_demo.analyze_monorepo
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.testql_watcher.TestQLWatcher.__init__ → project.map.toon.load_config
  wup.testql_watcher.TestQLWatcher.run_quick_test → wupbro.wupbro.storage.EventStore.list
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 69f 10338L | python:41,yaml:15,txt:5,json:2,toml:2,shell:1,yml:1 | 2026-04-29
# CC̄=2.7 | critical:8/363 | dups:0 | cycles:4

HEALTH[10]:
  🔴 GOD   wup/anomaly_detector.py = 593L, 6 classes, 23m, max CC=16
  🔴 CYCLE Circular dependency detected: examples.testql_demo.simulate_testql_analysis -> examples.testql_demo.simulate_with_mock_data. This indicates high coupling and may lead to infinite recursion or initialization issues.
  🟡 CC    detect_service_coincidences CC=19 (limit:15)
  🟡 CC    analyze_monorepo CC=22 (limit:15)
  🟡 CC    _select_scenarios_for_service CC=15 (limit:15)
  🟡 CC    run_quick_test CC=15 (limit:15)
  🟡 CC    run CC=16 (limit:15)
  🟡 CC    _compare_structures CC=15 (limit:15)
  🟡 CC    _extract_ast_info CC=16 (limit:15)
  🟡 CC    detect CC=16 (limit:15)

REFACTOR[3]:
  1. split wup/anomaly_detector.py  (god module)
  2. split 8 high-CC methods  (CC>15)
  3. break 4 circular dependencies

PIPELINES[207]:
  [1] Src [__init__]: __init__
      PURITY: 100% pure
  [2] Src [build_from_codebase]: build_from_codebase
      PURITY: 100% pure
  [3] Src [_detect_framework]: _detect_framework
      PURITY: 100% pure
  [4] Src [_search_codebase]: _search_codebase
      PURITY: 100% pure
  [5] Src [_scan_endpoints]: _scan_endpoints
      PURITY: 100% pure

LAYERS:
  wup/                            CC̄=4.7    ←in:3  →out:19  !! split
  │ !! assistant                  692L  1C   23m  CC=16     ←0
  │ !! core                       604L  2C   24m  CC=19     ←0
  │ !! anomaly_detector           593L  6C   23m  CC=16     ←0
  │ cli                        478L  0C    7m  CC=6      ←0
  │ !! testql_watcher             477L  2C   18m  CC=15     ←0
  │ config                     394L  0C    6m  CC=10     ←0
  │ visual_diff                333L  1C   16m  CC=11     ←1
  │ dependency_mapper          284L  1C   16m  CC=10     ←0
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ web_client                 178L  1C   10m  CC=6      ←0
  │ config                     130L  11C    0m  CC=0.0    ←0
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ __init__                    34L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.6    ←in:0  →out:8  !! split
  │ webhook_notifications      427L  1C   10m  CC=6      ←0
  │ ci_cd_integration          337L  0C    4m  CC=3      ←0
  │ visual_diff_demo           271L  0C    9m  CC=6      ←0
  │ testql_integration         267L  1C    6m  CC=6      ←0
  │ !! c2004_monorepo_demo        229L  0C    3m  CC=22     ←0
  │ testql_demo                192L  0C    2m  CC=11     ←0
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
  wupbro/                         CC̄=2.6    ←in:0  →out:0
  │ notifications              283L  1C   15m  CC=14     ←2
  │ notifications              234L  0C   10m  CC=2      ←0
  │ drivers                    129L  0C    5m  CC=3      ←0
  │ models                     123L  8C    0m  CC=0.0    ←0
  │ storage                    110L  1C    8m  CC=7      ←10
  │ pyproject.toml              74L  0C    0m  CC=0.0    ←0
  │ events                      65L  0C    5m  CC=2      ←0
  │ main                        45L  0C    1m  CC=1      ←0
  │ dashboard                   24L  0C    2m  CC=1      ←0
  │ __main__                    21L  0C    1m  CC=1      ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                 724L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              305L  0C  104m  CC=0.0    ←5
  │ calls.toon.yaml            148L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         119L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           54L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         52L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       43L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ tree.txt                   129L  0C    0m  CC=0.0    ←0
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
                           wup  wupbro.wupbro    project.map       examples
            wup             ──             13              6             ←3  !! fan-out
  wupbro.wupbro            ←13             ──                            ←2  hub
    project.map             ←6                            ──             ←3  hub
       examples              3              2              3             ──  !! fan-out
  CYCLES: 4
  HUB: wupbro.wupbro/ (fan-in=15)
  HUB: project.map/ (fan-in=9)
  SMELL: examples/ fan-out=8 → split needed
  SMELL: wup/ fan-out=19 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 4 groups | 40f 6271L | 2026-04-29

SUMMARY:
  files_scanned: 40
  total_lines:   6271
  dup_groups:    4
  dup_fragments: 10
  saved_lines:   20
  scan_ms:       5405

HOTSPOTS[4] (files with most duplication):
  wup/anomaly_detector.py  dup=20L  groups=2  frags=6  (0.3%)
  examples/flask-app/app/auth/routes.py  dup=6L  groups=1  frags=2  (0.1%)
  examples/visual_diff_demo.py  dup=3L  groups=1  frags=1  (0.0%)
  wup/visual_diff.py  dup=3L  groups=1  frags=1  (0.0%)

DUPLICATES[4] (ranked by impact):
  [8575900946923f44]   STRU  _snapshot_path  L=4 N=3 saved=8 sim=1.00
      wup/anomaly_detector.py:78-81  (_snapshot_path)
      wup/anomaly_detector.py:175-178  (_snapshot_path)
      wup/anomaly_detector.py:344-346  (_snapshot_path)
  [b5eae728fdce70c7]   STRU  __init__  L=3 N=3 saved=6 sim=1.00
      wup/anomaly_detector.py:70-72  (__init__)
      wup/anomaly_detector.py:140-142  (__init__)
      wup/anomaly_detector.py:303-305  (__init__)
  [e86dae8501b38602]   STRU  login  L=3 N=2 saved=3 sim=1.00
      examples/flask-app/app/auth/routes.py:7-9  (login)
      examples/flask-app/app/auth/routes.py:18-20  (register)
  [94e52a5e17c9baae]   STRU  _save_snapshot  L=3 N=2 saved=3 sim=1.00
      examples/visual_diff_demo.py:55-57  (_save_snapshot)
      wup/visual_diff.py:125-127  (_save_snapshot)

REFACTOR[4] (ranked by priority):
  [1] ○ extract_function   → wup/utils/_snapshot_path.py
      WHY: 3 occurrences of 4-line block across 1 files — saves 8 lines
      FILES: wup/anomaly_detector.py
  [2] ○ extract_function   → wup/utils/__init__.py
      WHY: 3 occurrences of 3-line block across 1 files — saves 6 lines
      FILES: wup/anomaly_detector.py
  [3] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: examples/flask-app/app/auth/routes.py
  [4] ○ extract_function   → utils/_save_snapshot.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/visual_diff_demo.py, wup/visual_diff.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=8L  → wup/utils/_snapshot_path.py
      FILES: anomaly_detector.py
  [2] extract_function   saved=6L  → wup/utils/__init__.py
      FILES: anomaly_detector.py

DEPENDENCY_RISK[1] (duplicates spanning multiple packages):
  _save_snapshot  packages=2  files=2
      examples/visual_diff_demo.py
      wup/visual_diff.py

EFFORT_ESTIMATE (total ≈ 0.8h):
  easy   _snapshot_path                      saved=8L  ~16min
  easy   __init__                            saved=6L  ~12min
  easy   login                               saved=3L  ~6min
  easy   _save_snapshot                      saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  4 → 0
  saved_lines: 20 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 301 func | 19f | 2026-04-29

NEXT[9] (ranked by impact):
  [1] !! SPLIT           wup/core.py
      WHY: 604L, 2 classes, max CC=19
      EFFORT: ~4h  IMPACT: 11476

  [2] !! SPLIT           wup/assistant.py
      WHY: 692L, 1 classes, max CC=16
      EFFORT: ~4h  IMPACT: 11072

  [3] !! SPLIT           wup/anomaly_detector.py
      WHY: 593L, 6 classes, max CC=16
      EFFORT: ~4h  IMPACT: 9488

  [4] !  SPLIT-FUNC      ASTDetector.detect  CC=16  fan=19
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 304

  [5] !  SPLIT-FUNC      WupAssistant.run  CC=16  fan=17
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 272

  [6] !  SPLIT-FUNC      TestQLWatcher.run_quick_test  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [7] !  SPLIT-FUNC      TestQLWatcher._select_scenarios_for_service  CC=15  fan=8
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 120

  [8] !  SPLIT-FUNC      ASTDetector._extract_ast_info  CC=16  fan=7
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 112

  [9] !  SPLIT-FUNC      YAMLStructureDetector._compare_structures  CC=15  fan=7
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 105


RISKS[3]:
  ⚠ Splitting wup/assistant.py may break 23 import paths
  ⚠ Splitting wup/core.py may break 24 import paths
  ⚠ Splitting wup/anomaly_detector.py may break 23 import paths

METRICS-TARGET:
  CC̄:          2.7 → ≤1.9
  max-CC:      19 → ≤9
  god-modules: 3 → 0
  high-CC(≥15): 7 → ≤3
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
  prev CC̄=2.6 → now CC̄=2.7
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
