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
- **version**: `0.2.9`
- **python_requires**: `>=3.9`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(6 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.9;
}

dependencies {
  runtime: "watchdog>=4.0.0, psutil>=5.9.0, rich>=13.0.0, typer>=0.9.0";
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

## Dependencies

### Runtime

```text markpact:deps python
watchdog>=4.0.0
psutil>=5.9.0
rich>=13.0.0
typer>=0.9.0
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `wup.core` (`wup/core.py`)

```python
class WupWatcher:  # Intelligent file watcher for regression testing.
    def __init__(project_root, deps_file, cpu_throttle, debounce_seconds, test_cooldown_seconds, config)  # CC=1
    def _to_relative_path(file_path)  # CC=2
    def infer_service(file_path)  # CC=10 ⚠
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

### `wup.testql_watcher` (`wup/testql_watcher.py`)

```python
class BrowserNotifier:  # Send watcher events to browser-facing service and local file
    def __init__(service_url, events_file)  # CC=7
    def notify(payload)  # CC=3
class TestQLWatcher:  # WUP watcher running selective TestQL scenarios for changed s
    def __init__(project_root, scenarios_dir, testql_bin, track_dir, browser_service_url, quick_limit, config)  # CC=7
    def _tokenize_service(service)  # CC=3
    def _get_config_endpoints_for_service(service)  # CC=5
    def _resolve_base_url()  # CC=5
    def _to_full_url(endpoint)  # CC=5
    def _discover_scenarios()  # CC=2
    def get_service_config(service_name)  # CC=3
    def _select_scenarios_for_service(service)  # CC=15 ⚠
    def _run_testql(args, timeout)  # CC=2
    def _write_track()  # CC=11 ⚠
    def run_quick_test(service, endpoints)  # CC=11 ⚠
    def run_detail_test(service, endpoints)  # CC=9
    def process_changed_file_once(file_path)  # CC=4
```

### `wup.cli` (`wup/cli.py`)

```python
def watch(project, deps_file, cpu_throttle, debounce, cooldown, dashboard, mode, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, config)  # CC=6, fan=16
def map_deps(project, output, framework, config)  # CC=2, fan=18
def status(deps_file, config)  # CC=11, fan=15 ⚠
def init(project, output)  # CC=3, fan=10
def testql_endpoints(scenarios_dir, output, testql_bin)  # CC=3, fan=19
def map_deps(project, output, framework)  # CC=2, fan=15
def version()  # CC=1, fan=2
```

### `wup.testql_discovery` (`wup/testql_discovery.py`)

```python
class TestQLEndpointDiscovery:  # Discover endpoints from TestQL scenario files.
    def __init__(scenarios_dir, testql_bin)  # CC=1
    def discover_scenarios()  # CC=2
    def parse_scenario_endpoints(scenario_path)  # CC=11 ⚠
    def infer_service_from_scenario(scenario_path)  # CC=4
    def discover_all_endpoints()  # CC=6
    def discover_via_testql_cli(service)  # CC=8
    def to_dependency_map()  # CC=4
```

## Call Graph

*11 nodes · 9 edges · 5 modules · CC̄=2.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `simulate_testql_analysis` *(in examples.testql_demo)* | 11 ⚠ | 1 | 80 | **81** |
| `status` *(in wup.cli)* | 11 ⚠ | 0 | 53 | **53** |
| `validate_config` *(in wup.config)* | 4 | 1 | 47 | **48** |
| `__init__` *(in wup.core.WupWatcher)* | 7 | 0 | 17 | **17** |
| `init` *(in wup.cli)* | 3 | 0 | 16 | **16** |
| `load_config` *(in wup.config)* | 5 | 4 | 7 | **11** |
| `get_default_config` *(in wup.config)* | 1 | 2 | 5 | **7** |
| `__init__` *(in wup.testql_watcher.TestQLWatcher)* | 7 | 0 | 6 | **6** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# nodes: 11 | edges: 9 | modules: 5
# CC̄=2.7

HUBS[20]:
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  wup.cli.status
    CC=11  in:0  out:53  total:53
  wup.config.validate_config
    CC=4  in:1  out:47  total:48
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.config.load_config
    CC=5  in:4  out:7  total:11
  wup.config.get_default_config
    CC=1  in:2  out:5  total:7
  wup.testql_watcher.TestQLWatcher.__init__
    CC=7  in:0  out:6  total:6
  examples.testql_demo.simulate_with_mock_data
    CC=1  in:1  out:3  total:4
  wup.config.save_config
    CC=2  in:1  out:3  total:4
  wup.config.find_config_file
    CC=3  in:1  out:1  total:2

MODULES:
  examples.testql_demo  [2 funcs]
    simulate_testql_analysis  CC=11  out:80
    simulate_with_mock_data  CC=1  out:3
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=11  out:53
  wup.config  [5 funcs]
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:7
    save_config  CC=2  out:3
    validate_config  CC=4  out:47
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.testql_watcher  [1 funcs]
    __init__  CC=7  out:6

EDGES:
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.core.WupWatcher.__init__ → wup.config.load_config
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
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
# nodes: 11 | edges: 9 | modules: 5
# CC̄=2.7

HUBS[20]:
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  wup.cli.status
    CC=11  in:0  out:53  total:53
  wup.config.validate_config
    CC=4  in:1  out:47  total:48
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.config.load_config
    CC=5  in:4  out:7  total:11
  wup.config.get_default_config
    CC=1  in:2  out:5  total:7
  wup.testql_watcher.TestQLWatcher.__init__
    CC=7  in:0  out:6  total:6
  examples.testql_demo.simulate_with_mock_data
    CC=1  in:1  out:3  total:4
  wup.config.save_config
    CC=2  in:1  out:3  total:4
  wup.config.find_config_file
    CC=3  in:1  out:1  total:2

MODULES:
  examples.testql_demo  [2 funcs]
    simulate_testql_analysis  CC=11  out:80
    simulate_with_mock_data  CC=1  out:3
  wup.cli  [2 funcs]
    init  CC=3  out:16
    status  CC=11  out:53
  wup.config  [5 funcs]
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:7
    save_config  CC=2  out:3
    validate_config  CC=4  out:47
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.testql_watcher  [1 funcs]
    __init__  CC=7  out:6

EDGES:
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.core.WupWatcher.__init__ → wup.config.load_config
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 49f 4825L | python:22,yaml:15,txt:4,json:2,shell:2,toml:1,yml:1 | 2026-04-29
# CC̄=2.7 | critical:2/144 | dups:0 | cycles:1

HEALTH[3]:
  🔴 CYCLE Circular dependency detected: examples.testql_demo.simulate_with_mock_data -> examples.testql_demo.simulate_testql_analysis. This indicates high coupling and may lead to infinite recursion or initialization issues.
  🟡 CC    detect_service_coincidences CC=19 (limit:15)
  🟡 CC    _select_scenarios_for_service CC=15 (limit:15)

REFACTOR[2]:
  1. split 2 high-CC methods  (CC>15)
  2. break 1 circular dependencies

PIPELINES[100]:
  [1] Src [watch]: watch → load_config → validate_config
      PURITY: 100% pure
  [2] Src [map_deps]: map_deps
      PURITY: 100% pure
  [3] Src [status]: status → load_config → validate_config
      PURITY: 100% pure
  [4] Src [init]: init → get_default_config
      PURITY: 100% pure
  [5] Src [testql_endpoints]: testql_endpoints
      PURITY: 100% pure

LAYERS:
  wup/                            CC̄=4.4    ←in:0  →out:0
  │ !! core                       596L  2C   24m  CC=19     ←0
  │ cli                        381L  0C    6m  CC=11     ←0
  │ !! testql_watcher             367L  2C   15m  CC=15     ←0
  │ dependency_mapper          284L  1C   16m  CC=10     ←0
  │ config                     254L  0C    5m  CC=5      ←3
  │ testql_discovery           229L  1C    7m  CC=11     ←0
  │ config                      82L  8C    0m  CC=0.0    ←0
  │ __init__                    39L  0C    0m  CC=0.0    ←0
  │ __init__                    21L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=1.9    ←in:0  →out:0
  │ testql_integration         237L  1C    6m  CC=5      ←0
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
  │ calls.yaml                 232L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              167L  0C   35m  CC=0.0    ←0
  │ analysis.toon.yaml          93L  0C    0m  CC=0.0    ←0
  │ calls.toon.yaml             56L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           56L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         52L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  49L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       29L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ testql-deps.json           311L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              66L  0C    0m  CC=0.0    ←0
  │ project.sh                  49L  0C    0m  CC=0.0    ←0
  │ deps.json                    4L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-from-pytests.testql.toon.yaml    82L  0C    0m  CC=0.0    ←0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  ── zero ──
     examples/flask-app/Dockerfile             0L
     examples/flask-app/app/__init__.py        0L
     examples/multi-service/payments-service/Dockerfile  0L

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 21f 1863L | 2026-04-29

SUMMARY:
  files_scanned: 21
  total_lines:   1863
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   3
  scan_ms:       4263

HOTSPOTS[1] (files with most duplication):
  examples/flask-app/app/auth/routes.py  dup=6L  groups=1  frags=2  (0.3%)

DUPLICATES[1] (ranked by impact):
  [e86dae8501b38602]   STRU  login  L=3 N=2 saved=3 sim=1.00
      examples/flask-app/app/auth/routes.py:7-9  (login)
      examples/flask-app/app/auth/routes.py:18-20  (register)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_function   → examples/flask-app/app/auth/utils/login.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: examples/flask-app/app/auth/routes.py

EFFORT_ESTIMATE (total ≈ 0.1h):
  easy   login                               saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 3 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 108 func | 7f | 2026-04-29

NEXT[3] (ranked by impact):
  [1] !! SPLIT           wup/core.py
      WHY: 596L, 2 classes, max CC=19
      EFFORT: ~4h  IMPACT: 11324

  [2] !  SPLIT-FUNC      TestQLWatcher._select_scenarios_for_service  CC=15  fan=8
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 120

  [3] !  SPLIT-FUNC      WupWatcher.detect_service_coincidences  CC=19  fan=2
      WHY: CC=19 exceeds 15
      EFFORT: ~1h  IMPACT: 38


RISKS[1]:
  ⚠ Splitting wup/core.py may break 24 import paths

METRICS-TARGET:
  CC̄:          3.0 → ≤2.1
  max-CC:      19 → ≤9
  god-modules: 1 → 0
  high-CC(≥15): 2 → ≤1
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
  prev CC̄=4.4 → now CC̄=3.0
```

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
