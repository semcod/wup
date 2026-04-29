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
- **version**: `0.2.16`
- **python_requires**: `>=3.9`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(8 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.16;
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

### `wup.visual_diff` (`wup/visual_diff.py`)

```python
def _playwright_available()  # CC=3, fan=0
def _fetch_dom_snapshot(url, max_depth, headless)  # CC=3, fan=8
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
    def run_for_service(service, endpoints)  # CC=6
    def _check_page(service, url)  # CC=2
    def _write_diff_event(service, url, result)  # CC=1
    def get_recent_diffs(seconds)  # CC=7
```

### `wup.web_client` (`wup/web_client.py`)

```python
def _httpx_available()  # CC=4, fan=1
def resolve_endpoint(cfg)  # CC=3, fan=2
def _normalize(payload)  # CC=6, fan=5
class WebClient:  # Async event sink for the wupbro backend.
    def __init__(cfg)  # CC=2
    def is_active()  # CC=3
    def _headers()  # CC=2
    def send_event(event)  # CC=4
    def send_regression(service, file, endpoint, reason, stage)  # CC=1
    def send_pass(service, stage)  # CC=1
    def send_health_transition(service, from_status, to_status)  # CC=1
    def send_visual_diff(service, url, diff)  # CC=1
```

## Call Graph

*47 nodes · 42 edges · 14 modules · CC̄=2.5*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `status` *(in wup.cli)* | 5 | 0 | 97 | **97** |
| `validate_config` *(in wup.config)* | 7 | 1 | 82 | **83** |
| `simulate_testql_analysis` *(in examples.testql_demo)* | 11 ⚠ | 1 | 80 | **81** |
| `demo_snapshot_persistence` *(in examples.visual_diff_demo)* | 3 | 1 | 26 | **27** |
| `run_quick_test` *(in wup.testql_watcher.TestQLWatcher)* | 15 ⚠ | 0 | 23 | **23** |
| `run_detail_test` *(in wup.testql_watcher.TestQLWatcher)* | 9 | 0 | 20 | **20** |
| `__init__` *(in wup.core.WupWatcher)* | 7 | 0 | 17 | **17** |
| `demo_config_yaml_round_trip` *(in examples.visual_diff_demo)* | 6 | 1 | 16 | **17** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# nodes: 47 | edges: 42 | modules: 14
# CC̄=2.5

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  wup.config.validate_config
    CC=7  in:1  out:82  total:83
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  wup.testql_watcher.TestQLWatcher.run_quick_test
    CC=15  in:0  out:23  total:23
  wup.testql_watcher.TestQLWatcher.run_detail_test
    CC=9  in:0  out:20  total:20
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
    CC=11  in:0  out:16  total:16
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  wup.config.load_config
    CC=5  in:5  out:8  total:13
  examples.visual_diff_demo.demo_disabled_is_noop
    CC=2  in:1  out:11  total:12
  wup.testql_watcher.TestQLWatcher.__init__
    CC=12  in:0  out:12  total:12
  wupbro.wupbro.storage.EventStore.list
    CC=7  in:7  out:5  total:12
  wup.config._load_dotenv
    CC=10  in:1  out:10  total:11
  wup.visual_diff._fetch_dom_snapshot
    CC=3  in:1  out:9  total:10

MODULES:
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
  project.map.toon  [2 funcs]
    _normalize  CC=0  out:0
    resolve_endpoint  CC=0  out:0
  wupbro.wupbro.routers.drivers  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.routers.events  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.storage  [2 funcs]
    list  CC=7  out:5
    get_default_store  CC=2  out:2
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:3
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
  wup.web_client  [2 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9

EDGES:
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.dependency_mapper.DependencyMapper.to_dict → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.core.WupWatcher.__init__ → wup.config.load_config
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
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
  wup.web_client.WebClient.__init__ → project.map.toon.resolve_endpoint
  wup.web_client.WebClient.send_event → project.map.toon._normalize
  wupbro.wupbro.routers.drivers._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.events._store → wupbro.wupbro.storage.get_default_store
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  wup.testql_watcher.TestQLWatcher.run_quick_test → wupbro.wupbro.storage.EventStore.list
  wup.testql_watcher.TestQLWatcher.run_detail_test → wupbro.wupbro.storage.EventStore.list
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
# nodes: 47 | edges: 42 | modules: 14
# CC̄=2.5

HUBS[20]:
  wup.cli.status
    CC=5  in:0  out:97  total:97
  wup.config.validate_config
    CC=7  in:1  out:82  total:83
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  wup.testql_watcher.TestQLWatcher.run_quick_test
    CC=15  in:0  out:23  total:23
  wup.testql_watcher.TestQLWatcher.run_detail_test
    CC=9  in:0  out:20  total:20
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  examples.visual_diff_demo.demo_config_yaml_round_trip
    CC=6  in:1  out:16  total:17
  examples.visual_diff_demo.demo_diff_algorithm
    CC=3  in:1  out:16  total:17
  wup.visual_diff._diff_snapshots
    CC=11  in:2  out:15  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
    CC=11  in:0  out:16  total:16
  examples.visual_diff_demo.main
    CC=2  in:0  out:15  total:15
  examples.visual_diff_demo.demo_live_page
    CC=3  in:1  out:14  total:15
  wup.config.load_config
    CC=5  in:5  out:8  total:13
  examples.visual_diff_demo.demo_disabled_is_noop
    CC=2  in:1  out:11  total:12
  wup.testql_watcher.TestQLWatcher.__init__
    CC=12  in:0  out:12  total:12
  wupbro.wupbro.storage.EventStore.list
    CC=7  in:7  out:5  total:12
  wup.config._load_dotenv
    CC=10  in:1  out:10  total:11
  wup.visual_diff._fetch_dom_snapshot
    CC=3  in:1  out:9  total:10

MODULES:
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
  project.map.toon  [2 funcs]
    _normalize  CC=0  out:0
    resolve_endpoint  CC=0  out:0
  wupbro.wupbro.routers.drivers  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.routers.events  [1 funcs]
    _store  CC=1  out:1
  wupbro.wupbro.storage  [2 funcs]
    list  CC=7  out:5
    get_default_store  CC=2  out:2
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=5  out:97
  wup.config  [6 funcs]
    _load_dotenv  CC=10  out:10
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:8
    save_config  CC=2  out:3
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
  wup.web_client  [2 funcs]
    __init__  CC=2  out:2
    send_event  CC=4  out:9

EDGES:
  wup.config.load_config → wup.config._load_dotenv
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.dependency_mapper.DependencyMapper.to_dict → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints → wupbro.wupbro.storage.EventStore.list
  wup.core.WupWatcher.__init__ → wup.config.load_config
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
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.save_config
  examples.visual_diff_demo.demo_config_yaml_round_trip → wup.config.load_config
  examples.visual_diff_demo.demo_live_page → wup.visual_diff._playwright_available
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_diff_algorithm
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_page_slug
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_snapshot_persistence
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_config_yaml_round_trip
  examples.visual_diff_demo.main → examples.visual_diff_demo.demo_disabled_is_noop
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
  wup.web_client.WebClient.__init__ → project.map.toon.resolve_endpoint
  wup.web_client.WebClient.send_event → project.map.toon._normalize
  wupbro.wupbro.routers.drivers._store → wupbro.wupbro.storage.get_default_store
  wupbro.wupbro.routers.events._store → wupbro.wupbro.storage.get_default_store
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  wup.testql_watcher.TestQLWatcher.run_quick_test → wupbro.wupbro.storage.EventStore.list
  wup.testql_watcher.TestQLWatcher.run_detail_test → wupbro.wupbro.storage.EventStore.list
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 62f 7005L | python:34,yaml:15,txt:5,json:2,toml:2,shell:1,yml:1 | 2026-04-29
# CC̄=2.5 | critical:3/229 | dups:0 | cycles:4

HEALTH[4]:
  🔴 CYCLE Circular dependency detected: examples.testql_demo.simulate_with_mock_data -> examples.testql_demo.simulate_testql_analysis. This indicates high coupling and may lead to infinite recursion or initialization issues.
  🟡 CC    detect_service_coincidences CC=19 (limit:15)
  🟡 CC    _select_scenarios_for_service CC=15 (limit:15)
  🟡 CC    run_quick_test CC=15 (limit:15)

REFACTOR[2]:
  1. split 3 high-CC methods  (CC>15)
  2. break 4 circular dependencies

PIPELINES[137]:
  [1] Src [watch]: watch → load_config → _load_dotenv
      PURITY: 100% pure
  [2] Src [map_deps]: map_deps
      PURITY: 100% pure
  [3] Src [status]: status → load_config → _load_dotenv
      PURITY: 100% pure
  [4] Src [init]: init → get_default_config
      PURITY: 100% pure
  [5] Src [testql_endpoints]: testql_endpoints
      PURITY: 100% pure

LAYERS:
  wup/                            CC̄=4.2    ←in:5  →out:8  !! split
  │ !! core                       604L  2C   24m  CC=19     ←0
  │ !! testql_watcher             477L  2C   18m  CC=15     ←0
  │ cli                        450L  0C    6m  CC=6      ←0
  │ config                     350L  0C    6m  CC=10     ←4
  │ visual_diff                333L  1C   16m  CC=11     ←1
  │ dependency_mapper          284L  1C   16m  CC=10     ←0
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ web_client                 178L  1C   10m  CC=6      ←0
  │ config                     112L  10C    0m  CC=0.0    ←0
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ __init__                    21L  0C    0m  CC=0.0    ←0
  │
  wupbro/                        CC̄=2.2    ←in:0  →out:0
  │ drivers                    129L  0C    5m  CC=3      ←0
  │ storage                    110L  1C    8m  CC=7      ←6
  │ pyproject.toml              72L  0C    0m  CC=0.0    ←0
  │ models                      59L  5C    0m  CC=0.0    ←0
  │ events                      48L  0C    5m  CC=1      ←0
  │ main                        44L  0C    1m  CC=1      ←0
  │ dashboard                   24L  0C    2m  CC=1      ←0
  │ __main__                    21L  0C    1m  CC=1      ←0
  │ __init__                     7L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.1    ←in:0  →out:5
  │ visual_diff_demo           271L  0C    9m  CC=6      ←0
  │ testql_integration         267L  1C    6m  CC=6      ←0
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
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                 542L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              208L  0C   59m  CC=0.0    ←1
  │ calls.toon.yaml            122L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml         103L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           54L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         52L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       43L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ tree.txt                    99L  0C    0m  CC=0.0    ←0
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
                               wup  wupbro.wupbro         examples      project.map
              wup               ──                6               ←5                2  hub
  wupbro.wupbro               ←6               ──                                    hub
         examples                5                                ──                 
      project.map               ←2                                                 ──
  CYCLES: 4
  HUB: wupbro.wupbro/ (fan-in=6)
  HUB: wup/ (fan-in=5)
  SMELL: wup/ fan-out=8 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 33f 3291L | 2026-04-29

SUMMARY:
  files_scanned: 33
  total_lines:   3291
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   6
  scan_ms:       4604

HOTSPOTS[3] (files with most duplication):
  examples/flask-app/app/auth/routes.py  dup=6L  groups=1  frags=2  (0.2%)
  examples/visual_diff_demo.py  dup=3L  groups=1  frags=1  (0.1%)
  wup/visual_diff.py  dup=3L  groups=1  frags=1  (0.1%)

DUPLICATES[2] (ranked by impact):
  [e86dae8501b38602]   STRU  login  L=3 N=2 saved=3 sim=1.00
      examples/flask-app/app/auth/routes.py:7-9  (login)
      examples/flask-app/app/auth/routes.py:18-20  (register)
  [94e52a5e17c9baae]   STRU  _save_snapshot  L=3 N=2 saved=3 sim=1.00
      examples/visual_diff_demo.py:55-57  (_save_snapshot)
      wup/visual_diff.py:125-127  (_save_snapshot)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: examples/flask-app/app/auth/routes.py
  [2] ○ extract_function   → utils/_save_snapshot.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: examples/visual_diff_demo.py, wup/visual_diff.py

DEPENDENCY_RISK[1] (duplicates spanning multiple packages):
  _save_snapshot  packages=2  files=2
      examples/visual_diff_demo.py
      wup/visual_diff.py

EFFORT_ESTIMATE (total ≈ 0.3h):
  easy   login                               saved=3L  ~6min
  easy   _save_snapshot                      saved=3L  ~12min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 6 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 184 func | 15f | 2026-04-29

NEXT[3] (ranked by impact):
  [1] !! SPLIT           wup/core.py
      WHY: 604L, 2 classes, max CC=19
      EFFORT: ~4h  IMPACT: 11476

  [2] !  SPLIT-FUNC      TestQLWatcher.run_quick_test  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [3] !  SPLIT-FUNC      TestQLWatcher._select_scenarios_for_service  CC=15  fan=8
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 120


RISKS[1]:
  ⚠ Splitting wup/core.py may break 24 import paths

METRICS-TARGET:
  CC̄:          2.6 → ≤1.8
  max-CC:      19 → ≤9
  god-modules: 1 → 0
  high-CC(≥15): 3 → ≤1
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
  prev CC̄=3.2 → now CC̄=2.6
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
