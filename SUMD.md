# WUP (What's Up)

WUP (What's Up) - Intelligent file watcher for regression testing in large projects

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `wup`
- **version**: `0.2.11`
- **python_requires**: `>=3.9`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(6 mod), project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.11;
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

- `wup.cli`
- `wup.config`
- `wup.core`
- `wup.dependency_mapper`
- `wup.testql_discovery`
- `wup.testql_watcher`

## Interfaces

### CLI Entry Points

- `wup`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m wup
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m wup --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m wup --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 72 assertions from pytest
ASSERT[72]{field, operator, expected}:
  len(watcher.test_queue), ==, 1
  test_type, ==, "quick"
  service_name, ==, "users"
  len(endpoints), ==, 3  # Limited by quick_tests.max_endpoints
  len(watcher.changed_services), ==, 1
  inferred1, ==, "users-shell"
  inferred2, ==, "payments"
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  watcher.config.project.name, ==, "test"
  len(watcher.config.watch.paths), ==, 1
  watcher.debounce_seconds, ==, 5
  len(paths), ==, 2
  inferred, ==, "users"
  svc_config.name, ==, "users"
  svc_config.quick_tests.max_endpoints, ==, 5
  len(endpoints), ==, 5  # Config limit
  len(watcher.changed_services), ==, 0
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, !=, 0
  result.returncode, !=, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  len(watcher.test_queue), ==, 1
  test_type, ==, "quick"
  service_name, ==, "users"
  len(endpoints), ==, 3  # Limited by quick_tests.max_endpoints
  len(watcher.changed_services), ==, 1
  inferred1, ==, "users-shell"
  inferred2, ==, "payments"
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  watcher.config.project.name, ==, "test"
  len(watcher.config.watch.paths), ==, 1
  watcher.debounce_seconds, ==, 5
  len(paths), ==, 2
  inferred, ==, "users"
  svc_config.name, ==, "users"
  svc_config.quick_tests.max_endpoints, ==, 5
  len(endpoints), ==, 5  # Config limit
  len(watcher.changed_services), ==, 0
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, !=, 0
  result.returncode, !=, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
```

## Configuration

```yaml
project:
  name: wup
  version: 0.2.11
  env: local
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

## Deployment

```bash markpact:run
pip install wup

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`wup`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `wup/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# wup | 31f 5235L | python:28,shell:2,less:1 | 2026-04-29
# stats: 50 func | 30 cls | 31 mod | CC̄=2.9 | critical:3 | cycles:0
# alerts[5]: CC status=32; CC test_service_health_transitions_are_persisted=12; CC simulate_testql_analysis=11; CC test_process_changed_file_creates_track_on_failure=7; CC watch=6
# hotspots[5]: status fan=22; testql_endpoints fan=19; map_deps fan=18; test_process_changed_file_creates_track_on_failure fan=16; watch fan=16
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[31]:
  app.doql.less,33
  examples/fastapi-app/app/__init__.py,1
  examples/fastapi-app/app/users/__init__.py,1
  examples/fastapi-app/app/users/routes.py,39
  examples/fastapi-app/main.py,17
  examples/flask-app/app/__init__.py,1
  examples/flask-app/app/auth/__init__.py,1
  examples/flask-app/app/auth/routes.py,32
  examples/flask-app/main.py,21
  examples/multi-service/auth-service/app/auth/routes.py,14
  examples/multi-service/auth-service/main.py,21
  examples/multi-service/payments-service/app/payments/routes.py,19
  examples/multi-service/payments-service/main.py,17
  examples/multi-service/users-service/app/users/routes.py,19
  examples/multi-service/users-service/main.py,17
  examples/testql_demo.py,193
  examples/testql_integration.py,238
  project.sh,49
  tests/test_e2e.py,517
  tests/test_testql_watcher.py,202
  tests/test_wup.py,1346
  tree.sh,2
  wup/__init__.py,40
  wup/cli.py,459
  wup/config.py,255
  wup/core.py,605
  wup/dependency_mapper.py,285
  wup/models/__init__.py,22
  wup/models/config.py,83
  wup/testql_discovery.py,230
  wup/testql_watcher.py,456
D:
  examples/fastapi-app/app/__init__.py:
  examples/fastapi-app/app/users/__init__.py:
  examples/fastapi-app/app/users/routes.py:
    e: list_users,get_user,create_user,update_user,delete_user,User
    User:
    list_users()
    get_user(user_id)
    create_user(user)
    update_user(user_id;user)
    delete_user(user_id)
  examples/fastapi-app/main.py:
    e: root,health
    root()
    health()
  examples/flask-app/app/__init__.py:
  examples/flask-app/app/auth/__init__.py:
  examples/flask-app/app/auth/routes.py:
    e: login,logout,register,profile,change_password
    login()
    logout()
    register()
    profile()
    change_password()
  examples/flask-app/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/auth-service/app/auth/routes.py:
    e: login,register
    login()
    register()
  examples/multi-service/auth-service/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/payments-service/app/payments/routes.py:
    e: list_payments,get_payment,create_payment
    list_payments()
    get_payment(payment_id)
    create_payment()
  examples/multi-service/payments-service/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/users-service/app/users/routes.py:
    e: list_users,get_user,create_user
    list_users()
    get_user(user_id)
    create_user()
  examples/multi-service/users-service/main.py:
    e: root,health
    root()
    health()
  examples/testql_demo.py:
    e: simulate_testql_analysis,simulate_with_mock_data
    simulate_testql_analysis(testql_path)
    simulate_with_mock_data()
  examples/testql_integration.py:
    e: main,TestQLWatcher
    TestQLWatcher: __init__(1),run_quick_test(2),run_detail_test(2),_find_scenarios_for_service(1),_generate_blame_report(2)  # Custom WUP watcher integrated with TestQL test framework.
    main()
  tests/test_e2e.py:
    e: run_wup_command,TestE2ECLI,TestE2EWorkflow,TestE2EIntegration,TestE2EErrorHandling,TestE2EPerformance,TestE2EConfigScenarios
    TestE2ECLI: test_cli_init_creates_config_file(0),test_cli_init_default_location(0),test_cli_map_deps_creates_dependency_file(0),test_cli_status_shows_dependency_info(0)  # End-to-end tests for CLI commands.
    TestE2EWorkflow: test_full_workflow_with_config(0),test_workflow_with_custom_config(0),test_workflow_with_file_type_filtering(0)  # End-to-end tests for complete workflows.
    TestE2EIntegration: test_integration_with_testql_scenarios(0),test_integration_with_multiple_frameworks(0)  # End-to-end integration tests with external tools.
    TestE2EErrorHandling: test_cli_handles_invalid_config(0),test_cli_handles_missing_project(0),test_cli_handles_empty_project(0)  # End-to-end tests for error handling.
    TestE2EPerformance: test_map_deps_performance_on_small_project(0),test_init_performance(0)  # End-to-end tests for performance characteristics.
    TestE2EConfigScenarios: test_config_with_multiple_services(0),test_config_with_service_coincidence(0)  # End-to-end tests for configuration scenarios.
    run_wup_command(args;cwd;timeout;capture_output;text)
  tests/test_testql_watcher.py:
    e: test_process_changed_file_creates_track_on_failure,test_browser_event_file_is_written_without_service_url,test_config_endpoints_use_base_url_from_yaml_config,test_config_endpoints_use_base_url_from_env_when_yaml_missing,test_service_health_transitions_are_persisted
    test_process_changed_file_creates_track_on_failure()
    test_browser_event_file_is_written_without_service_url()
    test_config_endpoints_use_base_url_from_yaml_config()
    test_config_endpoints_use_base_url_from_env_when_yaml_missing()
    test_service_health_transitions_are_persisted()
  tests/test_wup.py:
    e: test_import,TestDependencyMapper,TestWupWatcher,TestIntegrationWorkflow,TestFileFiltering,TestConfigModels,TestConfigLoader,TestConfigIntegration,TestTestQLWatcherConfig
    TestDependencyMapper: test_init(0),test_infer_service_from_path(0),test_build_from_codebase_empty(0),test_build_from_codebase_with_fastapi(0),test_save_and_load(0),test_infer_service_from_path_edge_cases(0),test_get_service_for_file_empty_mapper(0),test_get_endpoints_for_service_empty_mapper(0),test_build_from_codebase_with_flask(0),test_service_to_files_tracking(0),test_build_from_codebase_nonexistent_directory(0)  # Tests for the DependencyMapper class.
    TestWupWatcher: test_init(0),test_init_with_custom_params(0),test_infer_service(0),test_infer_service_with_auto_detection(0),test_infer_service_with_explicit_paths(0),test_infer_service_priority_config_over_mapper(0),test_infer_service_fallback_to_heuristics(0),test_should_test_cooldown(0),test_schedule_quick_test(0),test_schedule_detail_test(0),test_on_file_change_skip_dirs(0),test_detect_service_coincidences_shell_web(0),test_detect_service_coincidences_auto_type(0),test_detect_service_coincidences_no_config(0),test_detect_service_coincidences_unknown_service(0),test_services_share_domain(0),test_on_file_change_filters_by_file_type(0),test_on_file_change_no_file_type_filter(0)  # Tests for the WupWatcher class.
    TestIntegrationWorkflow: test_full_workflow_file_change_to_test_scheduling(0),test_workflow_with_file_type_filtering(0),test_workflow_with_service_coincidence(0),test_workflow_with_multiple_file_changes(0),test_workflow_with_auto_detection_and_explicit_paths(0)  # Integration tests for complete workflows.
    TestFileFiltering: test_should_watch_file_with_config(0),test_should_watch_file_without_config(0)  # Tests for file type filtering.
    TestConfigModels: test_project_config(0),test_notify_config(0),test_service_test_config(0),test_service_config(0),test_watch_config(0),test_test_strategy_config(0),test_testql_config(0),test_wup_config(0)  # Tests for configuration dataclasses.
    TestConfigLoader: test_get_default_config(0),test_save_and_load_config(0),test_load_config_from_yaml(0),test_load_config_auto_detect(0),test_load_config_no_file_returns_default(0),test_load_config_invalid_yaml(0),test_load_config_missing_project_name(0)  # Tests for configuration loading and saving.
    TestConfigIntegration: test_watcher_with_config(0),test_watcher_uses_config_debounce(0),test_watcher_build_watched_paths_from_config(0),test_watcher_infer_service_from_config(0),test_watcher_get_service_config(0),test_watcher_schedule_quick_test_uses_config_limit(0),test_watcher_on_file_change_uses_exclude_patterns(0)  # Tests for configuration integration with WupWatcher.
    TestTestQLWatcherConfig: test_testql_watcher_with_config(0),test_testql_watcher_uses_config_scenarios_dir(0),test_testql_watcher_get_service_config(0),test_testql_watcher_select_scenarios_uses_config_limit(0),test_testql_watcher_uses_config_timeout(0),test_testql_watcher_without_config_loads_default(0)  # Tests for TestQLWatcher configuration integration.
    test_import()
  wup/__init__.py:
  wup/cli.py:
    e: watch,map_deps,status,init,testql_endpoints,map_deps,version
    watch(project;deps_file;cpu_throttle;debounce;cooldown;dashboard;mode;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;config)
    map_deps(project;output;framework;config)
    status(deps_file;config;delta_seconds;failed_only)
    init(project;output)
    testql_endpoints(scenarios_dir;output;testql_bin)
    map_deps(project;output;framework)
    version()
  wup/config.py:
    e: find_config_file,load_config,validate_config,get_default_config,save_config
    find_config_file(project_root)
    load_config(project_root;config_path)
    validate_config(raw)
    get_default_config(project_root)
    save_config(config;output_path)
  wup/core.py:
    e: WupWatcher,WupEventHandler
    WupWatcher: __init__(6),_to_relative_path(1),infer_service(1),detect_service_coincidences(1),_services_share_domain(2),get_service_config(1),should_test(1),schedule_quick_test(1),schedule_detail_test(1),process_test_queue_once(0),cpu_ok(0),run_quick_test(2),run_detail_test(2),test_loop(0),should_watch_file(1),on_file_change(1),build_watched_paths(0),start_watching(1),create_status_table(0),run_with_dashboard(0)  # Intelligent file watcher for regression testing.
    WupEventHandler: __init__(1),on_modified(1),on_created(1),on_deleted(1)  # File system event handler for WUP watcher.
  wup/dependency_mapper.py:
    e: DependencyMapper
    DependencyMapper: __init__(1),build_from_codebase(1),_detect_framework(0),_search_codebase(1),_scan_endpoints(1),_scan_python_endpoints(1),_scan_js_endpoints(0),_infer_service(1),get_endpoints_for_file(1),get_endpoints_for_service(1),get_files_for_service(1),get_service_for_file(1),to_dict(0),save(1),load(1),build_from_testql_scenarios(2)  # Maps project dependencies for intelligent testing.
  wup/models/__init__.py:
  wup/models/config.py:
    e: NotifyConfig,ServiceTestConfig,ServiceConfig,WatchConfig,TestStrategyConfig,TestQLConfig,ProjectConfig,WupConfig
    NotifyConfig:  # Notification configuration for a service.
    ServiceTestConfig:  # Test configuration for a service (quick or detail).
    ServiceConfig:  # Configuration for a single service.
    WatchConfig:  # Configuration for file watching.
    TestStrategyConfig:  # Global test strategy configuration.
    TestQLConfig:  # TestQL-specific configuration.
    ProjectConfig:  # Project metadata.
    WupConfig:  # Main WUP configuration.
  wup/testql_discovery.py:
    e: TestQLEndpointDiscovery
    TestQLEndpointDiscovery: __init__(2),discover_scenarios(0),parse_scenario_endpoints(1),infer_service_from_scenario(1),discover_all_endpoints(0),discover_via_testql_cli(1),to_dependency_map(0)  # Discover endpoints from TestQL scenario files.
  wup/testql_watcher.py:
    e: BrowserNotifier,TestQLWatcher
    BrowserNotifier: __init__(2),notify(1)  # Send watcher events to browser-facing service and local file
    TestQLWatcher: __init__(7),_load_service_health(0),_save_service_health(0),_record_health_transition(0),_tokenize_service(1),_get_config_endpoints_for_service(1),_resolve_base_url(0),_to_full_url(1),_discover_scenarios(0),get_service_config(1),_select_scenarios_for_service(1),_run_testql(2),_write_track(0),run_quick_test(2),run_detail_test(2),process_changed_file_once(1)  # WUP watcher running selective TestQL scenarios for changed s
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
    def __init__(service_url, events_file)  # CC=8
    def notify(payload)  # CC=3
class TestQLWatcher:  # WUP watcher running selective TestQL scenarios for changed s
    def __init__(project_root, scenarios_dir, testql_bin, track_dir, browser_service_url, quick_limit, config)  # CC=8
    def _load_service_health()  # CC=4
    def _save_service_health()  # CC=1
    def _record_health_transition()  # CC=4
    def _tokenize_service(service)  # CC=3
    def _get_config_endpoints_for_service(service)  # CC=5
    def _resolve_base_url()  # CC=5
    def _to_full_url(endpoint)  # CC=5
    def _discover_scenarios()  # CC=2
    def get_service_config(service_name)  # CC=3
    def _select_scenarios_for_service(service)  # CC=15 ⚠
    def _run_testql(args, timeout)  # CC=2
    def _write_track()  # CC=11 ⚠
    def run_quick_test(service, endpoints)  # CC=13 ⚠
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

### `wup.cli` (`wup/cli.py`)

```python
def watch(project, deps_file, cpu_throttle, debounce, cooldown, dashboard, mode, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, config)  # CC=6, fan=16
def map_deps(project, output, framework, config)  # CC=2, fan=18
def status(deps_file, config, delta_seconds, failed_only)  # CC=32, fan=22 ⚠
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

*11 nodes · 9 edges · 5 modules · CC̄=2.9*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `status` *(in wup.cli)* | 32 ⚠ | 0 | 97 | **97** |
| `simulate_testql_analysis` *(in examples.testql_demo)* | 11 ⚠ | 1 | 80 | **81** |
| `validate_config` *(in wup.config)* | 4 | 1 | 47 | **48** |
| `__init__` *(in wup.core.WupWatcher)* | 7 | 0 | 17 | **17** |
| `init` *(in wup.cli)* | 3 | 0 | 16 | **16** |
| `load_config` *(in wup.config)* | 5 | 4 | 7 | **11** |
| `__init__` *(in wup.testql_watcher.TestQLWatcher)* | 8 | 0 | 8 | **8** |
| `get_default_config` *(in wup.config)* | 1 | 2 | 5 | **7** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# nodes: 11 | edges: 9 | modules: 5
# CC̄=2.9

HUBS[20]:
  wup.cli.status
    CC=32  in:0  out:97  total:97
  examples.testql_demo.simulate_testql_analysis
    CC=11  in:1  out:80  total:81
  wup.config.validate_config
    CC=4  in:1  out:47  total:48
  wup.core.WupWatcher.__init__
    CC=7  in:0  out:17  total:17
  wup.cli.init
    CC=3  in:0  out:16  total:16
  wup.config.load_config
    CC=5  in:4  out:7  total:11
  wup.testql_watcher.TestQLWatcher.__init__
    CC=8  in:0  out:8  total:8
  wup.config.get_default_config
    CC=1  in:2  out:5  total:7
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
    status  CC=32  out:97
  wup.config  [5 funcs]
    find_config_file  CC=3  out:1
    get_default_config  CC=1  out:5
    load_config  CC=5  out:7
    save_config  CC=2  out:3
    validate_config  CC=4  out:47
  wup.core  [1 funcs]
    __init__  CC=7  out:17
  wup.testql_watcher  [1 funcs]
    __init__  CC=8  out:8

EDGES:
  wup.config.load_config → wup.config.validate_config
  wup.config.load_config → wup.config.find_config_file
  wup.config.load_config → wup.config.get_default_config
  examples.testql_demo.simulate_with_mock_data → examples.testql_demo.simulate_testql_analysis
  wup.testql_watcher.TestQLWatcher.__init__ → wup.config.load_config
  wup.cli.status → wup.config.load_config
  wup.cli.init → wup.config.get_default_config
  wup.cli.init → wup.config.save_config
  wup.core.WupWatcher.__init__ → wup.config.load_config
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

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
