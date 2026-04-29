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
- **version**: `0.2.17`
- **python_requires**: `>=3.9`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, src(10 mod), project/(2 analysis files)

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
  version: 0.2.17
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
# wup | 56f 10386L | python:53,shell:2,less:1 | 2026-04-29
# stats: 151 func | 55 cls | 56 mod | CC̄=2.8 | critical:5 | cycles:0
# alerts[5]: CC analyze_monorepo=22; CC test_service_health_transitions_are_persisted=12; CC simulate_testql_analysis=11; CC _diff_snapshots=11; CC _load_dotenv=10
# hotspots[5]: status fan=31; testql_endpoints fan=19; analyze_monorepo fan=18; map_deps fan=18; demo_snapshot_persistence fan=17
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[56]:
  app.doql.less,82
  examples/c2004_monorepo_demo.py,230
  examples/ci_cd_integration.py,338
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
  examples/testql_integration.py,268
  examples/visual_diff_demo.py,272
  examples/webhook_notifications.py,428
  project.sh,49
  tests/test_e2e.py,517
  tests/test_testql_watcher.py,256
  tests/test_web_client.py,168
  tests/test_wup.py,1624
  tree.sh,2
  wup/__init__.py,40
  wup/anomaly_detector.py,594
  wup/assistant.py,693
  wup/cli.py,479
  wup/config.py,395
  wup/core.py,605
  wup/dependency_mapper.py,285
  wup/models/__init__.py,35
  wup/models/config.py,131
  wup/testql_discovery.py,230
  wup/testql_watcher.py,478
  wup/visual_diff.py,334
  wup/web_client.py,179
  wupbro/tests/__init__.py,1
  wupbro/tests/conftest.py,24
  wupbro/tests/test_dashboard.py,36
  wupbro/tests/test_drivers.py,51
  wupbro/tests/test_events.py,96
  wupbro/wupbro/__init__.py,8
  wupbro/wupbro/__main__.py,22
  wupbro/wupbro/main.py,46
  wupbro/wupbro/models.py,124
  wupbro/wupbro/notifications.py,284
  wupbro/wupbro/routers/__init__.py,2
  wupbro/wupbro/routers/dashboard.py,25
  wupbro/wupbro/routers/drivers.py,130
  wupbro/wupbro/routers/events.py,66
  wupbro/wupbro/routers/notifications.py,235
  wupbro/wupbro/storage.py,111
D:
  examples/c2004_monorepo_demo.py:
    e: analyze_monorepo,simulate_monorepo,main
    analyze_monorepo(project_path)
    simulate_monorepo()
    main()
  examples/ci_cd_integration.py:
    e: generate_github_actions,generate_gitlab_ci,show_ci_cd_demo,main
    generate_github_actions()
    generate_gitlab_ci()
    show_ci_cd_demo()
    main()
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
    TestQLWatcher: __init__(2),run_quick_test(2),run_detail_test(2),_find_scenarios_for_service(1),_generate_blame_report(2)  # Custom WUP watcher integrated with TestQL test framework.
    main()
  examples/visual_diff_demo.py:
    e: _make_dom,_save_snapshot,demo_diff_algorithm,demo_page_slug,demo_snapshot_persistence,demo_config_yaml_round_trip,demo_disabled_is_noop,demo_live_page,main
    _make_dom(n_divs)
    _save_snapshot(path;dom)
    demo_diff_algorithm()
    demo_page_slug()
    demo_snapshot_persistence()
    demo_config_yaml_round_trip()
    demo_disabled_is_noop()
    demo_live_page(url)
    main()
  examples/webhook_notifications.py:
    e: create_slack_payload,create_teams_payload,create_discord_payload,show_webhook_demo,main,NotificationRouter
    NotificationRouter: __init__(0),add_slack(1),add_teams(1),add_discord(1),send(1)  # Routes WUP events to configured notification channels.
    create_slack_payload(event)
    create_teams_payload(event)
    create_discord_payload(event)
    show_webhook_demo()
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
    e: test_process_changed_file_creates_track_on_failure,test_browser_event_file_is_written_without_service_url,test_config_endpoints_use_base_url_from_yaml_config,test_config_endpoints_use_base_url_from_env_when_yaml_missing,test_service_health_transitions_are_persisted,test_visual_differ_disabled_by_default,test_visual_differ_initialized_when_enabled
    test_process_changed_file_creates_track_on_failure()
    test_browser_event_file_is_written_without_service_url()
    test_config_endpoints_use_base_url_from_yaml_config()
    test_config_endpoints_use_base_url_from_env_when_yaml_missing()
    test_service_health_transitions_are_persisted()
    test_visual_differ_disabled_by_default()
    test_visual_differ_initialized_when_enabled()
  tests/test_web_client.py:
    e: _make_handler,recorder_server,test_resolve_endpoint_from_config,test_resolve_endpoint_from_env,test_resolve_endpoint_empty,test_is_active_false_when_disabled,test_is_active_false_when_no_endpoint,test_send_event_disabled_returns_false,test_send_event_posts_to_recorder,test_send_event_with_api_key,test_send_event_swallows_connection_error,test_send_regression_helper,test_send_health_transition_helper,_Recorder
    _Recorder: __init__(0)
    _make_handler(recorder;status)
    recorder_server()
    test_resolve_endpoint_from_config()
    test_resolve_endpoint_from_env(monkeypatch)
    test_resolve_endpoint_empty(monkeypatch)
    test_is_active_false_when_disabled()
    test_is_active_false_when_no_endpoint()
    test_send_event_disabled_returns_false()
    test_send_event_posts_to_recorder(recorder_server)
    test_send_event_with_api_key(recorder_server)
    test_send_event_swallows_connection_error()
    test_send_regression_helper(recorder_server)
    test_send_health_transition_helper(recorder_server)
  tests/test_wup.py:
    e: test_import,TestDependencyMapper,TestWupWatcher,TestIntegrationWorkflow,TestFileFiltering,TestConfigModels,TestVisualDiffer,TestConfigLoader,TestConfigIntegration,TestTestQLWatcherConfig
    TestDependencyMapper: test_init(0),test_infer_service_from_path(0),test_build_from_codebase_empty(0),test_build_from_codebase_with_fastapi(0),test_save_and_load(0),test_infer_service_from_path_edge_cases(0),test_get_service_for_file_empty_mapper(0),test_get_endpoints_for_service_empty_mapper(0),test_build_from_codebase_with_flask(0),test_service_to_files_tracking(0),test_build_from_codebase_nonexistent_directory(0)  # Tests for the DependencyMapper class.
    TestWupWatcher: test_init(0),test_init_with_custom_params(0),test_infer_service(0),test_infer_service_with_auto_detection(0),test_infer_service_with_explicit_paths(0),test_infer_service_priority_config_over_mapper(0),test_infer_service_fallback_to_heuristics(0),test_should_test_cooldown(0),test_schedule_quick_test(0),test_schedule_detail_test(0),test_on_file_change_skip_dirs(0),test_detect_service_coincidences_shell_web(0),test_detect_service_coincidences_auto_type(0),test_detect_service_coincidences_no_config(0),test_detect_service_coincidences_unknown_service(0),test_services_share_domain(0),test_on_file_change_filters_by_file_type(0),test_on_file_change_no_file_type_filter(0)  # Tests for the WupWatcher class.
    TestIntegrationWorkflow: test_full_workflow_file_change_to_test_scheduling(0),test_workflow_with_file_type_filtering(0),test_workflow_with_service_coincidence(0),test_workflow_with_multiple_file_changes(0),test_workflow_with_auto_detection_and_explicit_paths(0)  # Integration tests for complete workflows.
    TestFileFiltering: test_should_watch_file_with_config(0),test_should_watch_file_without_config(0)  # Tests for file type filtering.
    TestConfigModels: test_project_config(0),test_notify_config(0),test_service_test_config(0),test_service_config(0),test_watch_config(0),test_test_strategy_config(0),test_testql_config(0),test_wup_config(0),test_visual_diff_config_defaults(0),test_visual_diff_config_custom(0)  # Tests for configuration dataclasses.
    TestVisualDiffer: test_resolve_base_url_from_config(0),test_resolve_base_url_from_env(1),test_resolve_base_url_empty(1),test_page_slug(0),test_pages_for_service_explicit(0),test_pages_for_service_from_endpoints(0),test_pages_for_service_fallback(0),test_pages_for_service_absolute_url_passthrough(0),test_diff_snapshots_baseline(0),test_diff_snapshots_identical(0),test_diff_snapshots_changed(0),test_run_for_service_disabled_returns_empty(0),test_get_recent_diffs_empty(0),test_get_recent_diffs_filters_by_age(0)  # Tests for the VisualDiffer class (no Playwright required).
    TestConfigLoader: test_get_default_config(0),test_save_and_load_config(0),test_load_config_from_yaml(0),test_load_config_auto_detect(0),test_load_config_no_file_returns_default(0),test_load_config_invalid_yaml(0),test_load_config_missing_project_name(0),test_save_and_load_visual_diff_config(0),test_load_config_visual_diff_from_yaml(0),test_load_config_visual_diff_defaults_when_section_absent(0),test_load_dotenv_sets_env_var(0),test_load_dotenv_does_not_overwrite_existing(0)  # Tests for configuration loading and saving.
    TestConfigIntegration: test_watcher_with_config(0),test_watcher_uses_config_debounce(0),test_watcher_build_watched_paths_from_config(0),test_watcher_infer_service_from_config(0),test_watcher_get_service_config(0),test_watcher_schedule_quick_test_uses_config_limit(0),test_watcher_on_file_change_uses_exclude_patterns(0)  # Tests for configuration integration with WupWatcher.
    TestTestQLWatcherConfig: test_testql_watcher_with_config(0),test_testql_watcher_uses_config_scenarios_dir(0),test_testql_watcher_get_service_config(0),test_testql_watcher_select_scenarios_uses_config_limit(0),test_testql_watcher_uses_config_timeout(0),test_testql_watcher_without_config_loads_default(0)  # Tests for TestQLWatcher configuration integration.
    test_import()
  wup/__init__.py:
  wup/anomaly_detector.py:
    e: quick_scan,scan_yaml_changes,AnomalyResult,YAMLAnomalyConfig,HashDetector,YAMLStructureDetector,ASTDetector,AnomalyDetector
    AnomalyResult:  # Result of anomaly detection.
    YAMLAnomalyConfig:  # Configuration for YAML anomaly detection.
    HashDetector: __init__(1),_compute_hash(1),_snapshot_path(1),detect(1)  # Fast anomaly detection using file hashes.
    YAMLStructureDetector: __init__(1),_load_yaml(1),_extract_structure(3),_snapshot_path(1),_compare_structures(3),detect(1),_generate_suggestions(1)  # Detect structural changes in YAML files.
    ASTDetector: __init__(1),_extract_ast_info(1),_snapshot_path(1),detect(1)  # Detect changes in Python files using AST comparison.
    AnomalyDetector: __init__(2),_should_scan(1),scan_file(1),scan_directory(3),get_summary(1),print_report(1)  # Main anomaly detector combining multiple detection methods.
    quick_scan(project_root;files)
    scan_yaml_changes(project_root;yaml_dir)
  wup/assistant.py:
    e: main,WupAssistant
    WupAssistant: __init__(1),run(2),_init_project(1),_detect_framework(0),_auto_detect_services(1),_detect_service_type(2),_configure_services(0),_add_service_interactive(0),_edit_service(1),_setup_watch(0),_configure_testql(0),_setup_web_dashboard(0),_setup_visual_diff(0),_setup_anomaly_detection(0),_review_and_validate(0),_validate_config(0),_generate_suggestions(0),_save_configuration(0),_save_draft(0),_load_draft(0),_config_to_dict(1),_quick_setup(1)  # Interactive configuration assistant.
    main()
  wup/cli.py:
    e: watch,map_deps,status,init,testql_endpoints,map_deps,assistant,version
    watch(project;deps_file;cpu_throttle;debounce;cooldown;dashboard;mode;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;config)
    map_deps(project;output;framework;config)
    status(deps_file;config;delta_seconds;failed_only;watch;interval)
    init(project;output)
    testql_endpoints(scenarios_dir;output;testql_bin)
    map_deps(project;output;framework)
    assistant(quick;template;project)
    version()
  wup/config.py:
    e: find_config_file,_load_dotenv,load_config,validate_config,get_default_config,save_config
    find_config_file(project_root)
    _load_dotenv(project_root)
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
    e: NotifyConfig,ServiceTestConfig,ServiceConfig,WatchConfig,TestStrategyConfig,TestQLConfig,VisualDiffConfig,WebConfig,AnomalyDetectionConfig,ProjectConfig,WupConfig
    NotifyConfig:  # Notification configuration for a service.
    ServiceTestConfig:  # Test configuration for a service (quick or detail).
    ServiceConfig:  # Configuration for a single service.
    WatchConfig:  # Configuration for file watching.
    TestStrategyConfig:  # Global test strategy configuration.
    TestQLConfig:  # TestQL-specific configuration.
    VisualDiffConfig:  # Configuration for visual DOM diff after file changes.
    WebConfig:  # Configuration for sending events to wupbro backend.
    AnomalyDetectionConfig:  # Configuration for fast anomaly detection without Playwright.
    ProjectConfig:  # Project metadata.
    WupConfig:  # Main WUP configuration.
  wup/testql_discovery.py:
    e: TestQLEndpointDiscovery
    TestQLEndpointDiscovery: __init__(2),discover_scenarios(0),parse_scenario_endpoints(1),infer_service_from_scenario(1),discover_all_endpoints(0),discover_via_testql_cli(1),to_dependency_map(0)  # Discover endpoints from TestQL scenario files.
  wup/testql_watcher.py:
    e: BrowserNotifier,TestQLWatcher
    BrowserNotifier: __init__(2),notify(1)  # Send watcher events to browser-facing service and local file
    TestQLWatcher: __init__(7),_load_service_health(0),_save_service_health(0),_record_health_transition(0),_tokenize_service(1),_get_config_endpoints_for_service(1),_resolve_base_url(0),_to_full_url(1),_discover_scenarios(0),get_service_config(1),_select_scenarios_for_service(1),_run_testql(2),_write_track(0),run_quick_test(2),run_detail_test(2),process_changed_file_once(1)  # WUP watcher running selective TestQL scenarios for changed s
  wup/visual_diff.py:
    e: _playwright_available,_fetch_dom_snapshot,_page_slug,_snapshot_path,_load_snapshot,_save_snapshot,_node_signature,_flatten,_diff_snapshots,_resolve_base_url,VisualDiffer
    VisualDiffer: __init__(2),_pages_for_service(2),run_for_service(2),_check_page(2),_write_diff_event(3),get_recent_diffs(1)  # Triggered by TestQLWatcher after a file change.
    _playwright_available()
    _fetch_dom_snapshot(url;max_depth;headless)
    _page_slug(url)
    _snapshot_path(snapshot_dir;service;url)
    _load_snapshot(path)
    _save_snapshot(path;snapshot)
    _node_signature(node;depth)
    _flatten(node;depth;max_depth)
    _diff_snapshots(old;new;max_depth;threshold_added;threshold_removed;threshold_changed)
    _resolve_base_url(cfg)
  wup/web_client.py:
    e: _httpx_available,resolve_endpoint,_normalize,WebClient
    WebClient: __init__(1),is_active(0),_headers(0),send_event(1),send_regression(5),send_pass(2),send_health_transition(3),send_visual_diff(3)  # Async event sink for the wupbro backend.
    _httpx_available()
    resolve_endpoint(cfg)
    _normalize(payload)
  wupbro/tests/__init__.py:
  wupbro/tests/conftest.py:
    e: fresh_store,client
    fresh_store()
    client(fresh_store)
  wupbro/tests/test_dashboard.py:
    e: test_root_serves_dashboard,test_dashboard_alias,test_healthz,test_openapi_schema_includes_routes
    test_root_serves_dashboard(client)
    test_dashboard_alias(client)
    test_healthz(client)
    test_openapi_schema_includes_routes(client)
  wupbro/tests/test_drivers.py:
    e: test_anomaly_report_creates_event,test_driver_health_reports_capabilities,test_browserless_unreachable_returns_503,test_dom_diff_endpoint_exists
    test_anomaly_report_creates_event(client)
    test_driver_health_reports_capabilities(client)
    test_browserless_unreachable_returns_503(client;monkeypatch)
    test_dom_diff_endpoint_exists(client)
  wupbro/tests/test_events.py:
    e: test_post_event_accepted,test_post_event_invalid_type_rejected,test_list_events_returns_recent,test_list_events_filter_by_type,test_list_events_filter_by_service,test_list_events_limit,test_event_stats,test_clear_events,test_event_extra_fields_preserved
    test_post_event_accepted(client)
    test_post_event_invalid_type_rejected(client)
    test_list_events_returns_recent(client)
    test_list_events_filter_by_type(client)
    test_list_events_filter_by_service(client)
    test_list_events_limit(client)
    test_event_stats(client)
    test_clear_events(client)
    test_event_extra_fields_preserved(client)
  wupbro/wupbro/__init__.py:
  wupbro/wupbro/__main__.py:
    e: main
    main()
  wupbro/wupbro/main.py:
    e: create_app
    create_app()
  wupbro/wupbro/models.py:
    e: Event,EventList,DomDiffRequest,ScreenshotRequest,AnomalyReport,NotificationConfig,NotificationSubscription,NotificationPayload
    Event:  # Generic WUP event posted by an agent.
    EventList:
    DomDiffRequest:
    ScreenshotRequest:
    AnomalyReport:
    NotificationConfig:  # Konfiguracja powiadomień przeglądarkowych dla użytkownika.
    NotificationSubscription:  # Subskrypcja powiadomień dla konkretnego klienta (przeglądark
    NotificationPayload:  # Payload wysyłany jako powiadomienie przeglądarkowe.
  wupbro/wupbro/notifications.py:
    e: get_notification_manager,set_notification_manager,NotificationManager
    NotificationManager: __init__(1),subscribe(2),unsubscribe(1),get_subscription(1),list_subscriptions(0),update_config(2),process_event(1),_detect_notification_types(2),_should_notify(2),_create_payload(2),register_sse_client(1),unregister_sse_client(1),push_to_sse(1)  # Manages browser notification subscriptions and event detecti
    get_notification_manager(store)
    set_notification_manager(manager)
  wupbro/wupbro/routers/__init__.py:
  wupbro/wupbro/routers/dashboard.py:
    e: root,dashboard
    root(request)
    dashboard(request)
  wupbro/wupbro/routers/drivers.py:
    e: _store,dom_diff_capture,browserless_screenshot,anomaly_report,driver_health
    _store()
    dom_diff_capture(req;store)
    browserless_screenshot(req)
    anomaly_report(report;store)
    driver_health()
  wupbro/wupbro/routers/events.py:
    e: _store,post_event,list_events,event_stats,clear_events
    _store()
    post_event(event;store)
    list_events(type;service;limit;store)
    event_stats(store)
    clear_events(store)
  wupbro/wupbro/routers/notifications.py:
    e: subscribe,list_subscriptions,get_subscription,update_subscription,unsubscribe,get_default_config,get_notification_types,get_status_transition_types,notification_stream,send_test_notification
    subscribe(config)
    list_subscriptions()
    get_subscription(subscription_id)
    update_subscription(subscription_id;config)
    unsubscribe(subscription_id)
    get_default_config()
    get_notification_types()
    get_status_transition_types()
    notification_stream(subscription_id)
    send_test_notification(subscription_id;background_tasks)
  wupbro/wupbro/storage.py:
    e: get_default_store,set_default_store,EventStore
    EventStore: __init__(2),_load_existing(0),add(1),list(3),clear(0),stats(0)  # Thread-safe ring buffer + JSONL persistence.
    get_default_store()
    set_default_store(store)
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

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
