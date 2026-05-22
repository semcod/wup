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
- **version**: `0.2.42`
- **python_requires**: `>=3.9`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(4), app.doql.less, goal.yaml, .env.example, src(20 mod), project/(3 analysis files)

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

## Interfaces

### CLI Entry Points

- `wup`

### testql Scenarios

#### `testql-scenarios/cli-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/cli-smoke.testql.toon.yaml
# SCENARIO: CLI Smoke Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, wup
  timeout_ms, 15000


# Test: wup --help
SHELL "wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test: wup --version
SHELL "wup --version" 5000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/cli-wup.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/cli-wup.testql.toon.yaml
# SCENARIO: wup Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, wup
  timeout_ms, 30000

# Test 1: wup --help
SHELL "wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: wup --version
SHELL "wup --version" 5000
ASSERT_EXIT_CODE 0


# Test: wup with invalid flag (should fail)
SHELL "wup --invalid-flag-xyz123" 5000
ASSERT_EXIT_CODE != 0
```

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
  version: 0.2.42
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
# wup | 53f 12689L | python:50,shell:2,less:1 | 2026-05-22
# stats: 180 func | 56 cls | 53 mod | CC̄=3.7 | critical:9 | cycles:0
# alerts[5]: CC main=14; CC validate_config=14; CC sync_testql=13; CC _assign_by_path_prefix=13; CC test_service_health_transitions_are_persisted=12
# hotspots[5]: status fan=35; sync_testql fan=28; validate_config fan=21; main fan=19; testql_endpoints fan=19
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[53]:
  app.doql.less,33
  examples/c2004_monorepo_demo.py,259
  examples/ci_cd_integration.py,340
  examples/fastapi-app/app/__init__.py,1
  examples/fastapi-app/app/users/__init__.py,1
  examples/fastapi-app/app/users/routes.py,39
  examples/fastapi-app/main.py,17
  examples/flask-app/app/__init__.py,1
  examples/flask-app/app/auth/__init__.py,1
  examples/flask-app/app/auth/routes.py,34
  examples/flask-app/main.py,21
  examples/multi-service/auth-service/app/auth/routes.py,14
  examples/multi-service/auth-service/main.py,21
  examples/multi-service/payments-service/app/payments/routes.py,19
  examples/multi-service/payments-service/main.py,17
  examples/multi-service/users-service/app/users/routes.py,19
  examples/multi-service/users-service/main.py,17
  examples/testql_demo.py,192
  examples/testql_integration.py,287
  examples/visual_diff_demo.py,306
  examples/webhook_notifications.py,376
  project.sh,49
  scripts/run_probe_smoke.py,65
  tests/test_e2e.py,517
  tests/test_monitoring_manifest.py,73
  tests/test_testql_monitor.py,169
  tests/test_testql_watcher.py,529
  tests/test_web_client.py,168
  tests/test_wup.py,1802
  tree.sh,2
  wup/__init__.py,47
  wup/_ast_detector.py,125
  wup/_hash_detector.py,73
  wup/_yaml_detector.py,129
  wup/anomaly_detector.py,176
  wup/anomaly_models.py,36
  wup/assistant.py,695
  wup/cli.py,800
  wup/cli_config_generator.py,224
  wup/cli_scanner.py,303
  wup/config.py,465
  wup/core.py,664
  wup/dependency_mapper.py,285
  wup/models/__init__.py,35
  wup/models/config.py,166
  wup/monitoring_manifest.py,341
  wup/planfile_reporter.py,204
  wup/testql_cli_generator.py,216
  wup/testql_discovery.py,230
  wup/testql_monitor.py,522
  wup/testql_watcher.py,859
  wup/visual_diff.py,519
  wup/web_client.py,186
D:
  examples/c2004_monorepo_demo.py:
    e: _discover_modules,_print_config_summary,_analyze_module,_analyze_module_structure,_test_file_inference,_print_endpoints_summary,_print_recommendations,analyze_monorepo,simulate_monorepo,main
    _discover_modules(project_root)
    _print_config_summary(config)
    _analyze_module(module_path)
    _analyze_module_structure(project_root;modules)
    _test_file_inference(project_root;config)
    _print_endpoints_summary(config)
    _print_recommendations()
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
    e: _run_with_mock_services,_build_mock_services,simulate_testql_analysis,simulate_with_mock_data
    _run_with_mock_services(mapper;mock_services)
    _build_mock_services(mapper)
    simulate_testql_analysis(testql_path)
    simulate_with_mock_data()
  examples/testql_integration.py:
    e: main,CustomTestQLWatcher
    CustomTestQLWatcher: __init__(2),run_quick_test(2),run_detail_test(2),_find_scenarios_for_service(1),_generate_blame_report(2)  # Custom WUP watcher integrated with TestQL test framework.
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
  scripts/run_probe_smoke.py:
    e: main
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
  tests/test_monitoring_manifest.py:
    e: test_discover_docker_compose,test_patch_and_load_monitoring_block
    test_discover_docker_compose()
    test_patch_and_load_monitoring_block()
  tests/test_testql_monitor.py:
    e: test_parse_scenario_probes_full_url,test_firmware_plugin_health_on_8202_not_live_probe,test_connect_api_paths_on_8100_are_not_monitoring_probes,test_connect_health_on_8103_not_assigned_to_backend,test_assign_firmware_service,test_monitor_merges_config_and_service_map,test_probes_for_service_ignores_non_health_extra_paths,test_live_probe_failure_updates_health
    test_parse_scenario_probes_full_url()
    test_firmware_plugin_health_on_8202_not_live_probe()
    test_connect_api_paths_on_8100_are_not_monitoring_probes()
    test_connect_health_on_8103_not_assigned_to_backend()
    test_assign_firmware_service()
    test_monitor_merges_config_and_service_map()
    test_probes_for_service_ignores_non_health_extra_paths()
    test_live_probe_failure_updates_health()
  tests/test_testql_watcher.py:
    e: test_process_changed_file_creates_track_on_failure,test_browser_event_file_is_written_without_service_url,test_config_endpoints_use_base_url_from_yaml_config,test_config_endpoints_use_base_url_from_env_when_yaml_missing,test_service_health_transitions_are_persisted,test_planfile_reporter_creates_deduped_ticket,test_planfile_reporter_clears_dedupe_after_recovery,test_health_transition_creates_planfile_ticket,test_normalize_fleet_health_entry_down_to_degraded,test_fleet_health_scenario_non_strict_records_degraded_not_down,test_visual_differ_disabled_by_default,test_visual_differ_initialized_when_enabled,test_get_config_endpoints_for_service_keeps_connect_pages_on_frontend,test_quick_pass_actions_prefer_config_endpoints_for_visual_diff
    test_process_changed_file_creates_track_on_failure()
    test_browser_event_file_is_written_without_service_url()
    test_config_endpoints_use_base_url_from_yaml_config()
    test_config_endpoints_use_base_url_from_env_when_yaml_missing()
    test_service_health_transitions_are_persisted()
    test_planfile_reporter_creates_deduped_ticket(monkeypatch)
    test_planfile_reporter_clears_dedupe_after_recovery(monkeypatch)
    test_health_transition_creates_planfile_ticket(monkeypatch)
    test_normalize_fleet_health_entry_down_to_degraded()
    test_fleet_health_scenario_non_strict_records_degraded_not_down()
    test_visual_differ_disabled_by_default()
    test_visual_differ_initialized_when_enabled()
    test_get_config_endpoints_for_service_keeps_connect_pages_on_frontend()
    test_quick_pass_actions_prefer_config_endpoints_for_visual_diff()
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
    TestWupWatcher: test_init(0),test_init_with_custom_params(0),test_infer_service(0),test_infer_service_with_auto_detection(0),test_infer_service_with_explicit_paths(0),test_infer_service_priority_config_over_mapper(0),test_infer_service_fallback_to_heuristics(0),test_should_test_cooldown(0),test_schedule_quick_test(0),test_schedule_detail_test(0),test_on_file_change_skip_dirs(0),test_detect_service_coincidences_shell_web(0),test_detect_service_coincidences_auto_type(0),test_detect_service_coincidences_no_config(0),test_detect_service_coincidences_unknown_service(0),test_services_share_domain(0),test_on_file_change_filters_by_file_type(0),test_on_file_change_no_file_type_filter(0),test_create_and_start_observer_fallback_on_enospc(0),test_create_and_start_observer_fallback_on_emfile(0),test_create_and_start_observer_reraises_other_oserror(0)  # Tests for the WupWatcher class.
    TestIntegrationWorkflow: test_full_workflow_file_change_to_test_scheduling(0),test_workflow_with_file_type_filtering(0),test_workflow_with_service_coincidence(0),test_workflow_with_multiple_file_changes(0),test_workflow_with_auto_detection_and_explicit_paths(0)  # Integration tests for complete workflows.
    TestFileFiltering: test_should_watch_file_with_config(0),test_should_watch_file_without_config(0)  # Tests for file type filtering.
    TestConfigModels: test_project_config(0),test_notify_config(0),test_service_test_config(0),test_service_config(0),test_watch_config(0),test_test_strategy_config(0),test_testql_config(0),test_wup_config(0),test_visual_diff_config_defaults(0),test_visual_diff_config_custom(0)  # Tests for configuration dataclasses.
    TestVisualDiffer: test_resolve_base_url_from_config(0),test_resolve_base_url_from_env(1),test_resolve_base_url_empty(1),test_page_slug(0),test_pages_for_service_explicit(0),test_pages_for_service_from_endpoints(0),test_looks_like_visual_page_skips_api_health_routes(0),test_pages_for_service_from_endpoints_skips_non_html_probes(0),test_pages_for_service_fallback(0),test_pages_for_service_absolute_url_passthrough(0),test_diff_snapshots_baseline(0),test_diff_snapshots_identical(0),test_diff_snapshots_changed(0),test_run_for_service_disabled_returns_empty(0),test_run_for_service_summarizes_fetch_errors(1),test_get_recent_diffs_empty(0),test_get_recent_diffs_filters_by_age(0)  # Tests for the VisualDiffer class (no Playwright required).
    TestConfigLoader: test_get_default_config(0),test_save_and_load_config(0),test_load_config_from_yaml(0),test_load_config_auto_detect(0),test_load_config_no_file_returns_default(0),test_load_config_invalid_yaml(0),test_load_config_missing_project_name(0),test_save_and_load_visual_diff_config(0),test_load_config_visual_diff_from_yaml(0),test_load_config_visual_diff_defaults_when_section_absent(0),test_load_config_visual_diff_env_overrides_page_discovery(1),test_save_and_load_planfile_config(0),test_load_config_planfile_env_override(1),test_load_dotenv_sets_env_var(0),test_load_dotenv_does_not_overwrite_existing(0)  # Tests for configuration loading and saving.
    TestConfigIntegration: test_watcher_with_config(0),test_watcher_uses_config_debounce(0),test_watcher_build_watched_paths_from_config(0),test_watcher_infer_service_from_config(0),test_watcher_get_service_config(0),test_watcher_schedule_quick_test_uses_config_limit(0),test_watcher_on_file_change_uses_exclude_patterns(0)  # Tests for configuration integration with WupWatcher.
    TestTestQLWatcherConfig: test_testql_watcher_with_config(0),test_testql_watcher_uses_config_scenarios_dir(0),test_testql_watcher_get_service_config(0),test_testql_watcher_select_scenarios_uses_config_limit(0),test_testql_watcher_uses_config_timeout(0),test_testql_watcher_without_config_loads_default(0)  # Tests for TestQLWatcher configuration integration.
    test_import()
  wup/__init__.py:
    e: __getattr__
    __getattr__(name)
  wup/_ast_detector.py:
    e: ASTDetector
    ASTDetector: __init__(1),_collect_import(1),_collect_import_from(1),_collect_class(1),_collect_function(1),_extract_ast_info(1),_snapshot_path(1),_compute_changes(2),detect(1)  # Detect changes in Python files using AST comparison.
  wup/_hash_detector.py:
    e: HashDetector
    HashDetector: __init__(1),_compute_hash(1),_snapshot_path(1),detect(1)  # Fast anomaly detection using file hashes.
  wup/_yaml_detector.py:
    e: YAMLStructureDetector
    YAMLStructureDetector: __init__(1),_load_yaml(1),_extract_structure(3),_snapshot_path(1),_compare_structures(3),_compare_dict_structures(3),detect(1),_generate_suggestions(1)  # Detect structural changes in YAML files.
  wup/anomaly_detector.py:
    e: quick_scan,scan_yaml_changes,AnomalyDetector
    AnomalyDetector: __init__(2),_should_scan(1),scan_file(1),scan_directory(3),get_summary(1),print_report(1)  # Main anomaly detector combining multiple detection methods.
    quick_scan(project_root;files)
    scan_yaml_changes(project_root;yaml_dir)
  wup/anomaly_models.py:
    e: AnomalyResult,YAMLAnomalyConfig
    AnomalyResult:  # Result of anomaly detection.
    YAMLAnomalyConfig:  # Configuration for YAML anomaly detection.
  wup/assistant.py:
    e: main,WupAssistant
    WupAssistant: __init__(1),_dispatch_menu_choice(2),run(2),_init_project(1),_detect_framework(0),_auto_detect_services(1),_detect_service_type(2),_configure_services(0),_add_service_interactive(0),_edit_service(1),_setup_watch(0),_configure_testql(0),_setup_web_dashboard(0),_setup_visual_diff(0),_setup_anomaly_detection(0),_review_and_validate(0),_validate_config(0),_generate_suggestions(0),_save_configuration(0),_save_draft(0),_load_draft(0),_config_to_dict(1),_quick_setup(1)  # Interactive configuration assistant.
    main()
  wup/cli.py:
    e: _load_watch_config,_print_watch_header,_refresh_monitoring_manifest,_create_watcher,watch,_auto_generate_config,map_deps,status,init,testql_endpoints,map_deps,sync_testql,assistant,version,init_cli
    _load_watch_config(project_path;config_path;probe_interval;mode)
    _print_watch_header(wup_config;cpu_throttle;debounce;cooldown;config_path)
    _refresh_monitoring_manifest(project_path;wup_config;cfg_path)
    _create_watcher(mode;project_path;deps_file;cpu_throttle;debounce;cooldown;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;config)
    watch(project;deps_file;cpu_throttle;debounce;cooldown;dashboard;mode;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;probe_interval;config)
    _auto_generate_config(project_path;mode)
    map_deps(project;output;framework;config)
    status(deps_file;config;delta_seconds;failed_only;watch;interval)
    init(project;output)
    testql_endpoints(scenarios_dir;output;testql_bin)
    map_deps(project;output;framework)
    sync_testql(project;write;merge_endpoints;config)
    assistant(quick;template;project)
    version()
    init_cli(project;output_config;output_scenarios;merge;infer_args)
  wup/cli_config_generator.py:
    e: CLIConfigGenerator
    CLIConfigGenerator: __init__(1),generate(2),_generate_config(2),_create_shell_service(1),_save_config(2),print_summary(1)  # Generate wup.yaml configuration for CLI/shell services.
  wup/cli_scanner.py:
    e: CLICommand,CLIPackage,CLIScanner
    CLICommand:  # Represents a detected CLI command.
    CLIPackage:  # Represents a detected CLI package.
    CLIScanner: __init__(1),scan(0),_scan_setup_py(1),_scan_setup_cfg(1),_scan_pyproject_toml(1),_scan_main_modules(0),_parse_entry_points_dict(2),_add_entry_point(4),infer_command_args(1),_find_module_path(1),_get_help_arguments(1),to_dict(0)  # Scanner for detecting CLI commands in a project.
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
    WupWatcher: __init__(6),_to_relative_path(1),infer_service(1),_is_coincident_pair(2),detect_service_coincidences(1),_services_share_domain(2),get_service_config(1),should_test(1),schedule_quick_test(1),schedule_detail_test(1),process_test_queue_once(0),cpu_ok(0),run_quick_test(2),run_detail_test(2),test_loop(0),should_watch_file(1),_is_file_ignored(1),_notify_all_configured_services(1),on_file_change(1),build_watched_paths(0),_create_and_start_observer(2),start_watching(1),create_status_table(0),run_with_dashboard(0)  # Intelligent file watcher for regression testing.
    WupEventHandler: __init__(1),on_modified(1),on_created(1),on_deleted(1)  # File system event handler for WUP watcher.
  wup/dependency_mapper.py:
    e: DependencyMapper
    DependencyMapper: __init__(1),build_from_codebase(1),_detect_framework(0),_search_codebase(1),_scan_endpoints(1),_scan_python_endpoints(1),_scan_js_endpoints(0),_infer_service(1),get_endpoints_for_file(1),get_endpoints_for_service(1),get_files_for_service(1),get_service_for_file(1),to_dict(0),save(1),load(1),build_from_testql_scenarios(2)  # Maps project dependencies for intelligent testing.
  wup/models/__init__.py:
  wup/models/config.py:
    e: NotifyConfig,ServiceTestConfig,ServiceConfig,WatchConfig,TestStrategyConfig,TestQLConfig,VisualDiffConfig,WebConfig,PlanfileConfig,AnomalyDetectionConfig,ProjectConfig,WupConfig
    NotifyConfig:  # Notification configuration for a service.
    ServiceTestConfig:  # Test configuration for a service (quick or detail).
    ServiceConfig:  # Configuration for a single service.
    WatchConfig:  # Configuration for file watching.
    TestStrategyConfig:  # Global test strategy configuration.
    TestQLConfig:  # TestQL-specific configuration.
    VisualDiffConfig:  # Configuration for visual DOM diff after file changes.
    WebConfig:  # Configuration for sending events to wupbro backend.
    PlanfileConfig:  # Configuration for creating planfile tickets from WUP failure
    AnomalyDetectionConfig:  # Configuration for fast anomaly detection without Playwright.
    ProjectConfig:  # Project metadata.
    WupConfig:  # Main WUP configuration.
  wup/monitoring_manifest.py:
    e: _parse_port_mapping,_load_compose_yaml,_extract_healthcheck_test,_extract_service_from_spec,discover_docker_compose_services,_host_port_from_mapping,_map_docker_to_wup_service,_probe_row,_build_wup_service_dicts,_build_docker_rows,_build_scenario_rows,build_monitoring_manifest,manifest_to_yaml_block,patch_wup_yaml_monitoring,load_monitoring_manifest_from_yaml,format_manifest_summary,DockerComposeService
    DockerComposeService:
    _parse_port_mapping(raw)
    _load_compose_yaml(compose_path)
    _extract_healthcheck_test(spec)
    _extract_service_from_spec(name;spec;source_file)
    discover_docker_compose_services(project_root)
    _host_port_from_mapping(mapping)
    _map_docker_to_wup_service(docker;wup_services)
    _probe_row(probe)
    _build_wup_service_dicts(config)
    _build_docker_rows(docker_all;wup_names;by_wup)
    _build_scenario_rows(monitor;project_root;wup_names;by_wup)
    build_monitoring_manifest(project_root;config)
    manifest_to_yaml_block(manifest)
    patch_wup_yaml_monitoring(config_path;manifest)
    load_monitoring_manifest_from_yaml(config_path)
    format_manifest_summary(manifest)
  wup/planfile_reporter.py:
    e: PlanfileReporter
    PlanfileReporter: __init__(3),enabled(0),report_failure(0),clear_service_stage(0),_create_ticket(0),_wait_for_planfile_store_ready(1),_load_dedupe(0),_save_dedupe(1),_fingerprint(0),_parse_ticket_id(1),_ticket_name(0),_ticket_description(0)  # Create deduplicated planfile tickets for WUP-detected failur
  wup/testql_cli_generator.py:
    e: TestQLCLIGenerator
    TestQLCLIGenerator: __init__(1),generate(2),_generate_smoke_scenario(2),_generate_command_scenario(3),generate_custom_scenario(3),print_summary(1)  # Generate TestQL scenarios for CLI command testing.
  wup/testql_discovery.py:
    e: TestQLEndpointDiscovery
    TestQLEndpointDiscovery: __init__(2),discover_scenarios(0),parse_scenario_endpoints(1),infer_service_from_scenario(1),discover_all_endpoints(0),discover_via_testql_cli(1),to_dependency_map(0)  # Discover endpoints from TestQL scenario files.
  wup/testql_monitor.py:
    e: _parse_api_lines,parse_scenario_probes,_extract_base_url,_parse_endpoint_row,parse_service_map_probes,_connect_module_api_on_frontend_proxy,_firmware_plugin_probe_without_runtime,is_monitoring_probe,_service_path_patterns,_find_service_by_name,_find_service_by_token,_assign_by_port_8101,_assign_by_port_8202,_assign_by_port_8100,_assign_by_connect_backend,_assign_http_probe,_assign_by_longest_token,_assign_by_path_prefix,assign_probe_to_service,ProbeTarget,_ProbeAccumulator,TestQLMonitor
    ProbeTarget: probe(1)  # Single HTTP probe derived from TestQL scenarios or service m
    _ProbeAccumulator: __init__(1),add(2)  # Deduplicated probe collector for discover_probes_by_service.
    TestQLMonitor: __init__(2),_service_map_paths(0),_add_config_endpoints(1),_add_scenario_probes(1),_add_service_map_probes(1),discover_probes_by_service(0),_resolve_base_url_for_service(1),_probeable_url(2),probes_for_service(2),_sort_probes_for_live(1),run_probes(2),suggested_endpoints_by_service(0),_resolve_base_url(0),_join_base(2)  # Build and run live probes from TestQL scenarios + WUP config
    _parse_api_lines(content;source)
    parse_scenario_probes(scenario_path)
    _extract_base_url(data)
    _parse_endpoint_row(row;base_url;source)
    parse_service_map_probes(map_path)
    _connect_module_api_on_frontend_proxy(probe)
    _firmware_plugin_probe_without_runtime(probe)
    is_monitoring_probe(probe)
    _service_path_patterns(services)
    _find_service_by_name(services;name)
    _find_service_by_token(services;token)
    _assign_by_port_8101(services)
    _assign_by_port_8202(services)
    _assign_by_port_8100(services;path_lower)
    _assign_by_connect_backend(services;path_lower)
    _assign_http_probe(probe;services;path_lower)
    _assign_by_longest_token(path_lower;services)
    _assign_by_path_prefix(path_lower;services)
    assign_probe_to_service(probe;services)
  wup/testql_watcher.py:
    e: BrowserNotifier,TestQLWatcher
    BrowserNotifier: __init__(2),notify(1)  # Send watcher events to browser-facing service and local file
    TestQLWatcher: __init__(7),_normalize_fleet_health_entry(0),_load_service_health(0),_save_service_health(0),_record_health_transition(0),_tokenize_service(1),_get_config_endpoints_for_service(1),_to_full_url_for_service(2),_resolve_base_url_for_service(1),_resolve_base_url(0),_to_full_url(1),_discover_scenarios(0),get_service_config(1),_score_scenario(2),_get_scored_scenarios(3),_get_smoke_fallback(1),_select_scenarios_for_service(1),_filter_scenarios_by_type(2),_scenario_matches_type(2),_run_testql(2),_write_track(0),_quick_timeout(0),_merge_endpoints(2),_run_scenario_quick(3),_quick_pass_actions(2),_quick_probe_limit(1),_quick_probe_timeout(0),_run_live_http_probes(2),_try_parse_json_summary(1),_try_find_line_summary(1),_summarize_health_scenario_failure(1),_run_fleet_health_scenario(0),run_quick_test(2),_publish_visual_events(2),run_detail_test(2),process_changed_file_once(1),_run_periodic_probes_once(0),_start_periodic_probe_thread(0),start_watching(1)  # WUP watcher running selective TestQL scenarios for changed s
  wup/visual_diff.py:
    e: _playwright_available,_warn_playwright_missing,_fetch_dom_snapshot,_detect_content_issues,_page_slug,_short_url,_compact_error_message,_sample_list,_looks_like_visual_page,_snapshot_path,_load_snapshot,_save_snapshot,_node_signature,_flatten,_diff_snapshots,_resolve_base_url,VisualDiffer
    VisualDiffer: __init__(2),_pages_for_service(2),_categorize_page_result(6),_print_scan_summary(4),run_for_service(2),_check_page(2),_write_diff_event(3),get_recent_diffs(1)  # Triggered by TestQLWatcher after a file change.
    _playwright_available()
    _warn_playwright_missing()
    _fetch_dom_snapshot(url;max_depth;headless;error_selectors)
    _detect_content_issues(snapshot;cfg)
    _page_slug(url)
    _short_url(url)
    _compact_error_message(message;max_len)
    _sample_list(items;limit)
    _looks_like_visual_page(url)
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
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('wup', '0.2.42', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 33, 'less').
project_file('examples/c2004_monorepo_demo.py', 259, 'python').
project_file('examples/ci_cd_integration.py', 340, 'python').
project_file('examples/fastapi-app/app/__init__.py', 1, 'python').
project_file('examples/fastapi-app/app/users/__init__.py', 1, 'python').
project_file('examples/fastapi-app/app/users/routes.py', 39, 'python').
project_file('examples/fastapi-app/main.py', 17, 'python').
project_file('examples/flask-app/app/__init__.py', 1, 'python').
project_file('examples/flask-app/app/auth/__init__.py', 1, 'python').
project_file('examples/flask-app/app/auth/routes.py', 34, 'python').
project_file('examples/flask-app/main.py', 21, 'python').
project_file('examples/multi-service/auth-service/app/auth/routes.py', 14, 'python').
project_file('examples/multi-service/auth-service/main.py', 21, 'python').
project_file('examples/multi-service/payments-service/app/payments/routes.py', 19, 'python').
project_file('examples/multi-service/payments-service/main.py', 17, 'python').
project_file('examples/multi-service/users-service/app/users/routes.py', 19, 'python').
project_file('examples/multi-service/users-service/main.py', 17, 'python').
project_file('examples/testql_demo.py', 192, 'python').
project_file('examples/testql_integration.py', 287, 'python').
project_file('examples/visual_diff_demo.py', 306, 'python').
project_file('examples/webhook_notifications.py', 376, 'python').
project_file('project.sh', 49, 'shell').
project_file('scripts/run_probe_smoke.py', 65, 'python').
project_file('tests/test_e2e.py', 517, 'python').
project_file('tests/test_monitoring_manifest.py', 73, 'python').
project_file('tests/test_testql_monitor.py', 169, 'python').
project_file('tests/test_testql_watcher.py', 529, 'python').
project_file('tests/test_web_client.py', 168, 'python').
project_file('tests/test_wup.py', 1802, 'python').
project_file('tree.sh', 2, 'shell').
project_file('wup/__init__.py', 47, 'python').
project_file('wup/_ast_detector.py', 125, 'python').
project_file('wup/_hash_detector.py', 73, 'python').
project_file('wup/_yaml_detector.py', 129, 'python').
project_file('wup/anomaly_detector.py', 176, 'python').
project_file('wup/anomaly_models.py', 36, 'python').
project_file('wup/assistant.py', 695, 'python').
project_file('wup/cli.py', 800, 'python').
project_file('wup/cli_config_generator.py', 224, 'python').
project_file('wup/cli_scanner.py', 303, 'python').
project_file('wup/config.py', 465, 'python').
project_file('wup/core.py', 664, 'python').
project_file('wup/dependency_mapper.py', 285, 'python').
project_file('wup/models/__init__.py', 35, 'python').
project_file('wup/models/config.py', 166, 'python').
project_file('wup/monitoring_manifest.py', 341, 'python').
project_file('wup/planfile_reporter.py', 204, 'python').
project_file('wup/testql_cli_generator.py', 216, 'python').
project_file('wup/testql_discovery.py', 230, 'python').
project_file('wup/testql_monitor.py', 522, 'python').
project_file('wup/testql_watcher.py', 859, 'python').
project_file('wup/visual_diff.py', 519, 'python').
project_file('wup/web_client.py', 186, 'python').

% ── Python Functions ─────────────────────────────────────
python_function('examples/c2004_monorepo_demo.py', '_discover_modules', 1, 5, 6).
python_function('examples/c2004_monorepo_demo.py', '_print_config_summary', 1, 3, 2).
python_function('examples/c2004_monorepo_demo.py', '_analyze_module', 1, 3, 4).
python_function('examples/c2004_monorepo_demo.py', '_analyze_module_structure', 2, 7, 6).
python_function('examples/c2004_monorepo_demo.py', '_test_file_inference', 2, 3, 4).
python_function('examples/c2004_monorepo_demo.py', '_print_endpoints_summary', 1, 5, 2).
python_function('examples/c2004_monorepo_demo.py', '_print_recommendations', 0, 1, 1).
python_function('examples/c2004_monorepo_demo.py', 'analyze_monorepo', 1, 2, 11).
python_function('examples/c2004_monorepo_demo.py', 'simulate_monorepo', 0, 2, 2).
python_function('examples/c2004_monorepo_demo.py', 'main', 0, 2, 2).
python_function('examples/ci_cd_integration.py', 'generate_github_actions', 0, 1, 4).
python_function('examples/ci_cd_integration.py', 'generate_gitlab_ci', 0, 3, 7).
python_function('examples/ci_cd_integration.py', 'show_ci_cd_demo', 0, 2, 1).
python_function('examples/ci_cd_integration.py', 'main', 0, 3, 6).
python_function('examples/fastapi-app/app/users/routes.py', 'list_users', 0, 1, 1).
python_function('examples/fastapi-app/app/users/routes.py', 'get_user', 1, 1, 1).
python_function('examples/fastapi-app/app/users/routes.py', 'create_user', 1, 1, 1).
python_function('examples/fastapi-app/app/users/routes.py', 'update_user', 2, 1, 1).
python_function('examples/fastapi-app/app/users/routes.py', 'delete_user', 1, 1, 1).
python_function('examples/fastapi-app/main.py', 'root', 0, 1, 1).
python_function('examples/fastapi-app/main.py', 'health', 0, 1, 1).
python_function('examples/flask-app/app/auth/routes.py', 'login', 0, 2, 4).
python_function('examples/flask-app/app/auth/routes.py', 'logout', 0, 1, 2).
python_function('examples/flask-app/app/auth/routes.py', 'register', 0, 2, 4).
python_function('examples/flask-app/app/auth/routes.py', 'profile', 0, 1, 2).
python_function('examples/flask-app/app/auth/routes.py', 'change_password', 0, 2, 3).
python_function('examples/flask-app/main.py', 'root', 0, 1, 1).
python_function('examples/flask-app/main.py', 'health', 0, 1, 1).
python_function('examples/multi-service/auth-service/app/auth/routes.py', 'login', 0, 1, 2).
python_function('examples/multi-service/auth-service/app/auth/routes.py', 'register', 0, 1, 2).
python_function('examples/multi-service/auth-service/main.py', 'root', 0, 1, 1).
python_function('examples/multi-service/auth-service/main.py', 'health', 0, 1, 1).
python_function('examples/multi-service/payments-service/app/payments/routes.py', 'list_payments', 0, 1, 1).
python_function('examples/multi-service/payments-service/app/payments/routes.py', 'get_payment', 1, 1, 1).
python_function('examples/multi-service/payments-service/app/payments/routes.py', 'create_payment', 0, 1, 1).
python_function('examples/multi-service/payments-service/main.py', 'root', 0, 1, 1).
python_function('examples/multi-service/payments-service/main.py', 'health', 0, 1, 1).
python_function('examples/multi-service/users-service/app/users/routes.py', 'list_users', 0, 1, 1).
python_function('examples/multi-service/users-service/app/users/routes.py', 'get_user', 1, 1, 1).
python_function('examples/multi-service/users-service/app/users/routes.py', 'create_user', 0, 1, 1).
python_function('examples/multi-service/users-service/main.py', 'root', 0, 1, 1).
python_function('examples/multi-service/users-service/main.py', 'health', 0, 1, 1).
python_function('examples/testql_demo.py', '_run_with_mock_services', 2, 6, 8).
python_function('examples/testql_demo.py', '_build_mock_services', 1, 5, 2).
python_function('examples/testql_demo.py', 'simulate_testql_analysis', 1, 2, 7).
python_function('examples/testql_demo.py', 'simulate_with_mock_data', 0, 1, 4).
python_function('examples/testql_integration.py', 'main', 0, 5, 10).
python_function('examples/visual_diff_demo.py', '_make_dom', 1, 2, 1).
python_function('examples/visual_diff_demo.py', '_save_snapshot', 2, 1, 3).
python_function('examples/visual_diff_demo.py', 'demo_diff_algorithm', 0, 3, 4).
python_function('examples/visual_diff_demo.py', 'demo_page_slug', 0, 2, 2).
python_function('examples/visual_diff_demo.py', 'demo_snapshot_persistence', 0, 3, 17).
python_function('examples/visual_diff_demo.py', 'demo_config_yaml_round_trip', 0, 6, 10).
python_function('examples/visual_diff_demo.py', 'demo_disabled_is_noop', 0, 2, 6).
python_function('examples/visual_diff_demo.py', 'demo_live_page', 1, 3, 7).
python_function('examples/visual_diff_demo.py', 'main', 0, 2, 9).
python_function('examples/webhook_notifications.py', 'create_slack_payload', 1, 6, 5).
python_function('examples/webhook_notifications.py', 'create_teams_payload', 1, 6, 2).
python_function('examples/webhook_notifications.py', 'create_discord_payload', 1, 5, 4).
python_function('examples/webhook_notifications.py', 'show_webhook_demo', 0, 4, 16).
python_function('examples/webhook_notifications.py', 'main', 0, 3, 5).
python_function('scripts/run_probe_smoke.py', 'main', 0, 14, 19).
python_function('tests/test_e2e.py', 'run_wup_command', 5, 1, 5).
python_function('tests/test_monitoring_manifest.py', 'test_discover_docker_compose', 0, 4, 5).
python_function('tests/test_monitoring_manifest.py', 'test_patch_and_load_monitoring_block', 0, 7, 13).
python_function('tests/test_testql_monitor.py', 'test_parse_scenario_probes_full_url', 0, 5, 9).
python_function('tests/test_testql_monitor.py', 'test_firmware_plugin_health_on_8202_not_live_probe', 0, 3, 2).
python_function('tests/test_testql_monitor.py', 'test_connect_api_paths_on_8100_are_not_monitoring_probes', 0, 3, 4).
python_function('tests/test_testql_monitor.py', 'test_connect_health_on_8103_not_assigned_to_backend', 0, 2, 3).
python_function('tests/test_testql_monitor.py', 'test_assign_firmware_service', 0, 2, 3).
python_function('tests/test_testql_monitor.py', 'test_monitor_merges_config_and_service_map', 0, 5, 11).
python_function('tests/test_testql_monitor.py', 'test_probes_for_service_ignores_non_health_extra_paths', 0, 3, 9).
python_function('tests/test_testql_monitor.py', 'test_live_probe_failure_updates_health', 0, 4, 15).
python_function('tests/test_testql_watcher.py', 'test_process_changed_file_creates_track_on_failure', 0, 7, 17).
python_function('tests/test_testql_watcher.py', 'test_browser_event_file_is_written_without_service_url', 0, 5, 11).
python_function('tests/test_testql_watcher.py', 'test_config_endpoints_use_base_url_from_yaml_config', 0, 3, 9).
python_function('tests/test_testql_watcher.py', 'test_config_endpoints_use_base_url_from_env_when_yaml_missing', 0, 3, 11).
python_function('tests/test_testql_watcher.py', 'test_service_health_transitions_are_persisted', 0, 12, 15).
python_function('tests/test_testql_watcher.py', 'test_planfile_reporter_creates_deduped_ticket', 1, 9, 9).
python_function('tests/test_testql_watcher.py', 'test_planfile_reporter_clears_dedupe_after_recovery', 1, 4, 10).
python_function('tests/test_testql_watcher.py', 'test_health_transition_creates_planfile_ticket', 1, 1, 13).
python_function('tests/test_testql_watcher.py', 'test_normalize_fleet_health_entry_down_to_degraded', 0, 2, 14).
python_function('tests/test_testql_watcher.py', 'test_fleet_health_scenario_non_strict_records_degraded_not_down', 0, 4, 16).
python_function('tests/test_testql_watcher.py', 'test_visual_differ_disabled_by_default', 0, 4, 10).
python_function('tests/test_testql_watcher.py', 'test_visual_differ_initialized_when_enabled', 0, 4, 9).
python_function('tests/test_testql_watcher.py', 'test_get_config_endpoints_for_service_keeps_connect_pages_on_frontend', 0, 5, 10).
python_function('tests/test_testql_watcher.py', 'test_quick_pass_actions_prefer_config_endpoints_for_visual_diff', 0, 2, 14).
python_function('tests/test_web_client.py', '_make_handler', 2, 1, 10).
python_function('tests/test_web_client.py', 'recorder_server', 0, 1, 7).
python_function('tests/test_web_client.py', 'test_resolve_endpoint_from_config', 0, 2, 2).
python_function('tests/test_web_client.py', 'test_resolve_endpoint_from_env', 1, 2, 3).
python_function('tests/test_web_client.py', 'test_resolve_endpoint_empty', 1, 2, 3).
python_function('tests/test_web_client.py', 'test_is_active_false_when_disabled', 0, 2, 2).
python_function('tests/test_web_client.py', 'test_is_active_false_when_no_endpoint', 0, 2, 2).
python_function('tests/test_web_client.py', 'test_send_event_disabled_returns_false', 0, 2, 4).
python_function('tests/test_web_client.py', 'test_send_event_posts_to_recorder', 1, 9, 5).
python_function('tests/test_web_client.py', 'test_send_event_with_api_key', 1, 2, 5).
python_function('tests/test_web_client.py', 'test_send_event_swallows_connection_error', 0, 2, 4).
python_function('tests/test_web_client.py', 'test_send_regression_helper', 1, 5, 4).
python_function('tests/test_web_client.py', 'test_send_health_transition_helper', 1, 5, 4).
python_function('tests/test_wup.py', 'test_import', 0, 1, 0).
python_function('wup/__init__.py', '__getattr__', 1, 2, 1).
python_function('wup/anomaly_detector.py', 'quick_scan', 2, 2, 3).
python_function('wup/anomaly_detector.py', 'scan_yaml_changes', 2, 1, 3).
python_function('wup/assistant.py', 'main', 0, 1, 5).
python_function('wup/cli.py', '_load_watch_config', 4, 4, 3).
python_function('wup/cli.py', '_print_watch_header', 5, 3, 1).
python_function('wup/cli.py', '_refresh_monitoring_manifest', 3, 3, 3).
python_function('wup/cli.py', '_create_watcher', 12, 2, 5).
python_function('wup/cli.py', 'watch', 14, 8, 17).
python_function('wup/cli.py', '_auto_generate_config', 2, 3, 9).
python_function('wup/cli.py', 'map_deps', 4, 2, 18).
python_function('wup/cli.py', 'status', 6, 5, 35).
python_function('wup/cli.py', 'init', 2, 3, 10).
python_function('wup/cli.py', 'testql_endpoints', 3, 3, 19).
python_function('wup/cli.py', 'map_deps', 3, 2, 15).
python_function('wup/cli.py', 'sync_testql', 4, 13, 28).
python_function('wup/cli.py', 'assistant', 3, 2, 11).
python_function('wup/cli.py', 'version', 0, 1, 2).
python_function('wup/cli.py', 'init_cli', 5, 8, 16).
python_function('wup/config.py', 'find_config_file', 1, 3, 1).
python_function('wup/config.py', '_load_dotenv', 1, 10, 6).
python_function('wup/config.py', 'load_config', 2, 5, 8).
python_function('wup/config.py', 'validate_config', 1, 14, 21).
python_function('wup/config.py', 'get_default_config', 1, 1, 5).
python_function('wup/config.py', 'save_config', 2, 2, 11).
python_function('wup/monitoring_manifest.py', '_parse_port_mapping', 1, 5, 2).
python_function('wup/monitoring_manifest.py', '_load_compose_yaml', 1, 5, 4).
python_function('wup/monitoring_manifest.py', '_extract_healthcheck_test', 1, 6, 4).
python_function('wup/monitoring_manifest.py', '_extract_service_from_spec', 3, 7, 6).
python_function('wup/monitoring_manifest.py', 'discover_docker_compose_services', 1, 7, 10).
python_function('wup/monitoring_manifest.py', '_host_port_from_mapping', 1, 3, 3).
python_function('wup/monitoring_manifest.py', '_map_docker_to_wup_service', 2, 11, 4).
python_function('wup/monitoring_manifest.py', '_probe_row', 1, 2, 0).
python_function('wup/monitoring_manifest.py', '_build_wup_service_dicts', 1, 3, 2).
python_function('wup/monitoring_manifest.py', '_build_docker_rows', 3, 5, 2).
python_function('wup/monitoring_manifest.py', '_build_scenario_rows', 4, 5, 7).
python_function('wup/monitoring_manifest.py', 'build_monitoring_manifest', 2, 9, 15).
python_function('wup/monitoring_manifest.py', 'manifest_to_yaml_block', 1, 1, 2).
python_function('wup/monitoring_manifest.py', 'patch_wup_yaml_monitoring', 2, 5, 10).
python_function('wup/monitoring_manifest.py', 'load_monitoring_manifest_from_yaml', 1, 9, 8).
python_function('wup/monitoring_manifest.py', 'format_manifest_summary', 1, 10, 6).
python_function('wup/testql_monitor.py', '_parse_api_lines', 2, 3, 6).
python_function('wup/testql_monitor.py', 'parse_scenario_probes', 1, 2, 3).
python_function('wup/testql_monitor.py', '_extract_base_url', 1, 4, 4).
python_function('wup/testql_monitor.py', '_parse_endpoint_row', 3, 8, 8).
python_function('wup/testql_monitor.py', 'parse_service_map_probes', 1, 6, 8).
python_function('wup/testql_monitor.py', '_connect_module_api_on_frontend_proxy', 1, 5, 4).
python_function('wup/testql_monitor.py', '_firmware_plugin_probe_without_runtime', 1, 5, 4).
python_function('wup/testql_monitor.py', 'is_monitoring_probe', 1, 9, 7).
python_function('wup/testql_monitor.py', '_service_path_patterns', 1, 6, 7).
python_function('wup/testql_monitor.py', '_find_service_by_name', 2, 3, 1).
python_function('wup/testql_monitor.py', '_find_service_by_token', 2, 3, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8101', 1, 1, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8202', 1, 1, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8100', 2, 2, 3).
python_function('wup/testql_monitor.py', '_assign_by_connect_backend', 2, 4, 3).
python_function('wup/testql_monitor.py', '_assign_http_probe', 3, 4, 5).
python_function('wup/testql_monitor.py', '_assign_by_longest_token', 2, 7, 3).
python_function('wup/testql_monitor.py', '_assign_by_path_prefix', 2, 13, 2).
python_function('wup/testql_monitor.py', 'assign_probe_to_service', 2, 5, 6).
python_function('wup/visual_diff.py', '_playwright_available', 0, 3, 0).
python_function('wup/visual_diff.py', '_warn_playwright_missing', 0, 2, 1).
python_function('wup/visual_diff.py', '_fetch_dom_snapshot', 4, 9, 14).
python_function('wup/visual_diff.py', '_detect_content_issues', 2, 6, 5).
python_function('wup/visual_diff.py', '_page_slug', 1, 2, 3).
python_function('wup/visual_diff.py', '_short_url', 1, 3, 1).
python_function('wup/visual_diff.py', '_compact_error_message', 2, 3, 3).
python_function('wup/visual_diff.py', '_sample_list', 2, 3, 2).
python_function('wup/visual_diff.py', '_looks_like_visual_page', 1, 7, 4).
python_function('wup/visual_diff.py', '_snapshot_path', 3, 1, 2).
python_function('wup/visual_diff.py', '_load_snapshot', 1, 3, 3).
python_function('wup/visual_diff.py', '_save_snapshot', 2, 1, 3).
python_function('wup/visual_diff.py', '_node_signature', 2, 3, 3).
python_function('wup/visual_diff.py', '_flatten', 3, 4, 4).
python_function('wup/visual_diff.py', '_diff_snapshots', 6, 11, 5).
python_function('wup/visual_diff.py', '_resolve_base_url', 1, 3, 2).
python_function('wup/web_client.py', '_httpx_available', 0, 4, 1).
python_function('wup/web_client.py', 'resolve_endpoint', 1, 3, 2).
python_function('wup/web_client.py', '_normalize', 1, 6, 5).

% ── Python Classes ───────────────────────────────────────
python_class('examples/fastapi-app/app/users/routes.py', 'User').
python_class('examples/testql_integration.py', 'CustomTestQLWatcher').
python_method('CustomTestQLWatcher', '__init__', 2, 2, 5).
python_method('CustomTestQLWatcher', 'run_quick_test', 2, 6, 7).
python_method('CustomTestQLWatcher', 'run_detail_test', 2, 5, 7).
python_method('CustomTestQLWatcher', '_find_scenarios_for_service', 1, 5, 6).
python_method('CustomTestQLWatcher', '_generate_blame_report', 2, 3, 5).
python_class('examples/webhook_notifications.py', 'NotificationRouter').
python_method('NotificationRouter', '__init__', 0, 1, 0).
python_method('NotificationRouter', 'add_slack', 1, 1, 0).
python_method('NotificationRouter', 'add_teams', 1, 1, 0).
python_method('NotificationRouter', 'add_discord', 1, 1, 0).
python_method('NotificationRouter', 'send', 1, 3, 4).
python_class('tests/test_e2e.py', 'TestE2ECLI').
python_method('TestE2ECLI', 'test_cli_init_creates_config_file', 0, 5, 6).
python_method('TestE2ECLI', 'test_cli_init_default_location', 0, 3, 4).
python_method('TestE2ECLI', 'test_cli_map_deps_creates_dependency_file', 0, 5, 8).
python_method('TestE2ECLI', 'test_cli_status_shows_dependency_info', 0, 1, 7).
python_class('tests/test_e2e.py', 'TestE2EWorkflow').
python_method('TestE2EWorkflow', 'test_full_workflow_with_config', 0, 3, 6).
python_method('TestE2EWorkflow', 'test_workflow_with_custom_config', 0, 3, 6).
python_method('TestE2EWorkflow', 'test_workflow_with_file_type_filtering', 0, 2, 5).
python_class('tests/test_e2e.py', 'TestE2EIntegration').
python_method('TestE2EIntegration', 'test_integration_with_testql_scenarios', 0, 3, 5).
python_method('TestE2EIntegration', 'test_integration_with_multiple_frameworks', 0, 4, 8).
python_class('tests/test_e2e.py', 'TestE2EErrorHandling').
python_method('TestE2EErrorHandling', 'test_cli_handles_invalid_config', 0, 2, 4).
python_method('TestE2EErrorHandling', 'test_cli_handles_missing_project', 0, 2, 1).
python_method('TestE2EErrorHandling', 'test_cli_handles_empty_project', 0, 4, 6).
python_class('tests/test_e2e.py', 'TestE2EPerformance').
python_method('TestE2EPerformance', 'test_map_deps_performance_on_small_project', 0, 4, 7).
python_method('TestE2EPerformance', 'test_init_performance', 0, 3, 3).
python_class('tests/test_e2e.py', 'TestE2EConfigScenarios').
python_method('TestE2EConfigScenarios', 'test_config_with_multiple_services', 0, 4, 6).
python_method('TestE2EConfigScenarios', 'test_config_with_service_coincidence', 0, 3, 5).
python_class('tests/test_web_client.py', '_Recorder').
python_method('_Recorder', '__init__', 0, 1, 0).
python_class('tests/test_wup.py', 'TestDependencyMapper').
python_method('TestDependencyMapper', 'test_init', 0, 5, 4).
python_method('TestDependencyMapper', 'test_infer_service_from_path', 0, 4, 3).
python_method('TestDependencyMapper', 'test_build_from_codebase_empty', 0, 5, 4).
python_method('TestDependencyMapper', 'test_build_from_codebase_with_fastapi', 0, 3, 7).
python_method('TestDependencyMapper', 'test_save_and_load', 0, 4, 8).
python_method('TestDependencyMapper', 'test_infer_service_from_path_edge_cases', 0, 5, 3).
python_method('TestDependencyMapper', 'test_get_service_for_file_empty_mapper', 0, 2, 5).
python_method('TestDependencyMapper', 'test_get_endpoints_for_service_empty_mapper', 0, 2, 3).
python_method('TestDependencyMapper', 'test_build_from_codebase_with_flask', 0, 3, 7).
python_method('TestDependencyMapper', 'test_service_to_files_tracking', 0, 3, 4).
python_method('TestDependencyMapper', 'test_build_from_codebase_nonexistent_directory', 0, 3, 3).
python_class('tests/test_wup.py', 'TestWupWatcher').
python_method('TestWupWatcher', 'test_init', 0, 5, 3).
python_method('TestWupWatcher', 'test_init_with_custom_params', 0, 4, 7).
python_method('TestWupWatcher', 'test_infer_service', 0, 2, 5).
python_method('TestWupWatcher', 'test_infer_service_with_auto_detection', 0, 3, 11).
python_method('TestWupWatcher', 'test_infer_service_with_explicit_paths', 0, 3, 11).
python_method('TestWupWatcher', 'test_infer_service_priority_config_over_mapper', 0, 2, 11).
python_method('TestWupWatcher', 'test_infer_service_fallback_to_heuristics', 0, 2, 10).
python_method('TestWupWatcher', 'test_should_test_cooldown', 0, 3, 4).
python_method('TestWupWatcher', 'test_schedule_quick_test', 0, 5, 4).
python_method('TestWupWatcher', 'test_schedule_detail_test', 0, 5, 4).
python_method('TestWupWatcher', 'test_on_file_change_skip_dirs', 0, 3, 6).
python_method('TestWupWatcher', 'test_detect_service_coincidences_shell_web', 0, 5, 9).
python_method('TestWupWatcher', 'test_detect_service_coincidences_auto_type', 0, 2, 9).
python_method('TestWupWatcher', 'test_detect_service_coincidences_no_config', 0, 2, 9).
python_method('TestWupWatcher', 'test_detect_service_coincidences_unknown_service', 0, 2, 10).
python_method('TestWupWatcher', 'test_services_share_domain', 0, 8, 3).
python_method('TestWupWatcher', 'test_on_file_change_filters_by_file_type', 0, 1, 11).
python_method('TestWupWatcher', 'test_on_file_change_no_file_type_filter', 0, 1, 11).
python_method('TestWupWatcher', 'test_create_and_start_observer_fallback_on_enospc', 0, 2, 7).
python_method('TestWupWatcher', 'test_create_and_start_observer_fallback_on_emfile', 0, 2, 7).
python_method('TestWupWatcher', 'test_create_and_start_observer_reraises_other_oserror', 0, 1, 7).
python_class('tests/test_wup.py', 'TestIntegrationWorkflow').
python_method('TestIntegrationWorkflow', 'test_full_workflow_file_change_to_test_scheduling', 0, 6, 14).
python_method('TestIntegrationWorkflow', 'test_workflow_with_file_type_filtering', 0, 3, 13).
python_method('TestIntegrationWorkflow', 'test_workflow_with_service_coincidence', 0, 2, 9).
python_method('TestIntegrationWorkflow', 'test_workflow_with_multiple_file_changes', 0, 4, 13).
python_method('TestIntegrationWorkflow', 'test_workflow_with_auto_detection_and_explicit_paths', 0, 3, 12).
python_class('tests/test_wup.py', 'TestFileFiltering').
python_method('TestFileFiltering', 'test_should_watch_file_with_config', 0, 7, 8).
python_method('TestFileFiltering', 'test_should_watch_file_without_config', 0, 4, 8).
python_class('tests/test_wup.py', 'TestConfigModels').
python_method('TestConfigModels', 'test_project_config', 0, 3, 1).
python_method('TestConfigModels', 'test_notify_config', 0, 4, 1).
python_method('TestConfigModels', 'test_service_test_config', 0, 3, 1).
python_method('TestConfigModels', 'test_service_config', 0, 5, 4).
python_method('TestConfigModels', 'test_watch_config', 0, 3, 2).
python_method('TestConfigModels', 'test_test_strategy_config', 0, 3, 1).
python_method('TestConfigModels', 'test_testql_config', 0, 5, 2).
python_method('TestConfigModels', 'test_wup_config', 0, 6, 8).
python_method('TestConfigModels', 'test_visual_diff_config_defaults', 0, 11, 1).
python_method('TestConfigModels', 'test_visual_diff_config_custom', 0, 5, 1).
python_class('tests/test_wup.py', 'TestVisualDiffer').
python_method('TestVisualDiffer', 'test_resolve_base_url_from_config', 0, 2, 2).
python_method('TestVisualDiffer', 'test_resolve_base_url_from_env', 1, 2, 3).
python_method('TestVisualDiffer', 'test_resolve_base_url_empty', 1, 2, 3).
python_method('TestVisualDiffer', 'test_page_slug', 0, 3, 1).
python_method('TestVisualDiffer', 'test_pages_for_service_explicit', 0, 2, 4).
python_method('TestVisualDiffer', 'test_pages_for_service_from_endpoints', 0, 3, 4).
python_method('TestVisualDiffer', 'test_looks_like_visual_page_skips_api_health_routes', 0, 4, 1).
python_method('TestVisualDiffer', 'test_pages_for_service_from_endpoints_skips_non_html_probes', 0, 4, 4).
python_method('TestVisualDiffer', 'test_pages_for_service_fallback', 0, 2, 4).
python_method('TestVisualDiffer', 'test_pages_for_service_absolute_url_passthrough', 0, 2, 4).
python_method('TestVisualDiffer', 'test_diff_snapshots_baseline', 0, 2, 1).
python_method('TestVisualDiffer', 'test_diff_snapshots_identical', 0, 4, 1).
python_method('TestVisualDiffer', 'test_diff_snapshots_changed', 0, 3, 1).
python_method('TestVisualDiffer', 'test_run_for_service_disabled_returns_empty', 0, 2, 5).
python_method('TestVisualDiffer', 'test_run_for_service_summarizes_fetch_errors', 1, 6, 9).
python_method('TestVisualDiffer', 'test_get_recent_diffs_empty', 0, 2, 4).
python_method('TestVisualDiffer', 'test_get_recent_diffs_filters_by_age', 0, 3, 10).
python_class('tests/test_wup.py', 'TestConfigLoader').
python_method('TestConfigLoader', 'test_get_default_config', 0, 5, 5).
python_method('TestConfigLoader', 'test_save_and_load_config', 0, 5, 12).
python_method('TestConfigLoader', 'test_load_config_from_yaml', 0, 9, 5).
python_method('TestConfigLoader', 'test_load_config_auto_detect', 0, 2, 4).
python_method('TestConfigLoader', 'test_load_config_no_file_returns_default', 0, 3, 4).
python_method('TestConfigLoader', 'test_load_config_invalid_yaml', 0, 1, 5).
python_method('TestConfigLoader', 'test_load_config_missing_project_name', 0, 1, 5).
python_method('TestConfigLoader', 'test_save_and_load_visual_diff_config', 0, 10, 7).
python_method('TestConfigLoader', 'test_load_config_visual_diff_from_yaml', 0, 14, 4).
python_method('TestConfigLoader', 'test_load_config_visual_diff_defaults_when_section_absent', 0, 7, 4).
python_method('TestConfigLoader', 'test_load_config_visual_diff_env_overrides_page_discovery', 1, 3, 5).
python_method('TestConfigLoader', 'test_save_and_load_planfile_config', 0, 8, 7).
python_method('TestConfigLoader', 'test_load_config_planfile_env_override', 1, 2, 5).
python_method('TestConfigLoader', 'test_load_dotenv_sets_env_var', 0, 3, 6).
python_method('TestConfigLoader', 'test_load_dotenv_does_not_overwrite_existing', 0, 2, 5).
python_class('tests/test_wup.py', 'TestConfigIntegration').
python_method('TestConfigIntegration', 'test_watcher_with_config', 0, 3, 8).
python_method('TestConfigIntegration', 'test_watcher_uses_config_debounce', 0, 2, 7).
python_method('TestConfigIntegration', 'test_watcher_build_watched_paths_from_config', 0, 4, 12).
python_method('TestConfigIntegration', 'test_watcher_infer_service_from_config', 0, 2, 11).
python_method('TestConfigIntegration', 'test_watcher_get_service_config', 0, 5, 10).
python_method('TestConfigIntegration', 'test_watcher_schedule_quick_test_uses_config_limit', 0, 3, 12).
python_method('TestConfigIntegration', 'test_watcher_on_file_change_uses_exclude_patterns', 0, 2, 12).
python_class('tests/test_wup.py', 'TestTestQLWatcherConfig').
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_with_config', 0, 3, 7).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_uses_config_scenarios_dir', 0, 2, 8).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_get_service_config', 0, 4, 10).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_select_scenarios_uses_config_limit', 0, 3, 15).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_uses_config_timeout', 0, 3, 7).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_without_config_loads_default', 0, 3, 3).
python_class('wup/_ast_detector.py', 'ASTDetector').
python_method('ASTDetector', '__init__', 1, 1, 1).
python_method('ASTDetector', '_collect_import', 1, 2, 0).
python_method('ASTDetector', '_collect_import_from', 1, 3, 1).
python_method('ASTDetector', '_collect_class', 1, 5, 3).
python_method('ASTDetector', '_collect_function', 1, 1, 1).
python_method('ASTDetector', '_extract_ast_info', 1, 6, 11).
python_method('ASTDetector', '_snapshot_path', 1, 1, 2).
python_method('ASTDetector', '_compute_changes', 2, 11, 3).
python_method('ASTDetector', 'detect', 1, 6, 13).
python_class('wup/_hash_detector.py', 'HashDetector').
python_method('HashDetector', '__init__', 1, 1, 1).
python_method('HashDetector', '_compute_hash', 1, 1, 3).
python_method('HashDetector', '_snapshot_path', 1, 1, 2).
python_method('HashDetector', 'detect', 1, 5, 9).
python_class('wup/_yaml_detector.py', 'YAMLStructureDetector').
python_method('YAMLStructureDetector', '__init__', 1, 1, 1).
python_method('YAMLStructureDetector', '_load_yaml', 1, 2, 2).
python_method('YAMLStructureDetector', '_extract_structure', 3, 6, 6).
python_method('YAMLStructureDetector', '_snapshot_path', 1, 1, 2).
python_method('YAMLStructureDetector', '_compare_structures', 3, 7, 4).
python_method('YAMLStructureDetector', '_compare_dict_structures', 3, 7, 6).
python_method('YAMLStructureDetector', 'detect', 1, 8, 14).
python_method('YAMLStructureDetector', '_generate_suggestions', 1, 6, 2).
python_class('wup/anomaly_detector.py', 'AnomalyDetector').
python_method('AnomalyDetector', '__init__', 2, 6, 6).
python_method('AnomalyDetector', '_should_scan', 1, 7, 4).
python_method('AnomalyDetector', 'scan_file', 1, 6, 7).
python_method('AnomalyDetector', 'scan_directory', 3, 6, 9).
python_method('AnomalyDetector', 'get_summary', 1, 2, 2).
python_method('AnomalyDetector', 'print_report', 1, 7, 12).
python_class('wup/anomaly_models.py', 'AnomalyResult').
python_class('wup/anomaly_models.py', 'YAMLAnomalyConfig').
python_class('wup/assistant.py', 'WupAssistant').
python_method('WupAssistant', '__init__', 1, 1, 4).
python_method('WupAssistant', '_dispatch_menu_choice', 2, 3, 3).
python_method('WupAssistant', 'run', 2, 8, 7).
python_method('WupAssistant', '_init_project', 1, 7, 7).
python_method('WupAssistant', '_detect_framework', 0, 6, 4).
python_method('WupAssistant', '_auto_detect_services', 1, 7, 8).
python_method('WupAssistant', '_detect_service_type', 2, 10, 5).
python_method('WupAssistant', '_configure_services', 0, 14, 11).
python_method('WupAssistant', '_add_service_interactive', 0, 11, 6).
python_method('WupAssistant', '_edit_service', 1, 5, 5).
python_method('WupAssistant', '_setup_watch', 0, 7, 7).
python_method('WupAssistant', '_configure_testql', 0, 3, 6).
python_method('WupAssistant', '_setup_web_dashboard', 0, 3, 3).
python_method('WupAssistant', '_setup_visual_diff', 0, 6, 4).
python_method('WupAssistant', '_setup_anomaly_detection', 0, 8, 6).
python_method('WupAssistant', '_review_and_validate', 0, 11, 7).
python_method('WupAssistant', '_validate_config', 0, 9, 3).
python_method('WupAssistant', '_generate_suggestions', 0, 6, 2).
python_method('WupAssistant', '_save_configuration', 0, 3, 10).
python_method('WupAssistant', '_save_draft', 0, 1, 4).
python_method('WupAssistant', '_load_draft', 0, 2, 4).
python_method('WupAssistant', '_config_to_dict', 1, 1, 4).
python_method('WupAssistant', '_quick_setup', 1, 4, 7).
python_class('wup/cli_config_generator.py', 'CLIConfigGenerator').
python_method('CLIConfigGenerator', '__init__', 1, 1, 3).
python_method('CLIConfigGenerator', 'generate', 2, 4, 5).
python_method('CLIConfigGenerator', '_generate_config', 2, 6, 8).
python_method('CLIConfigGenerator', '_create_shell_service', 1, 1, 5).
python_method('CLIConfigGenerator', '_save_config', 2, 2, 4).
python_method('CLIConfigGenerator', 'print_summary', 1, 3, 6).
python_class('wup/cli_scanner.py', 'CLICommand').
python_class('wup/cli_scanner.py', 'CLIPackage').
python_class('wup/cli_scanner.py', 'CLIScanner').
python_method('CLIScanner', '__init__', 1, 1, 2).
python_method('CLIScanner', 'scan', 0, 4, 5).
python_method('CLIScanner', '_scan_setup_py', 1, 3, 4).
python_method('CLIScanner', '_scan_setup_cfg', 1, 10, 6).
python_method('CLIScanner', '_scan_pyproject_toml', 1, 6, 8).
python_method('CLIScanner', '_scan_main_modules', 0, 5, 5).
python_method('CLIScanner', '_parse_entry_points_dict', 2, 4, 4).
python_method('CLIScanner', '_add_entry_point', 4, 6, 5).
python_method('CLIScanner', 'infer_command_args', 1, 7, 7).
python_method('CLIScanner', '_find_module_path', 1, 8, 5).
python_method('CLIScanner', '_get_help_arguments', 1, 7, 8).
python_method('CLIScanner', 'to_dict', 0, 3, 0).
python_class('wup/core.py', 'WupWatcher').
python_method('WupWatcher', '__init__', 6, 1, 15).
python_method('WupWatcher', '_to_relative_path', 1, 2, 2).
python_method('WupWatcher', 'infer_service', 1, 10, 9).
python_method('WupWatcher', '_is_coincident_pair', 2, 6, 0).
python_method('WupWatcher', 'detect_service_coincidences', 1, 9, 3).
python_method('WupWatcher', '_services_share_domain', 2, 1, 3).
python_method('WupWatcher', 'get_service_config', 1, 3, 0).
python_method('WupWatcher', 'should_test', 1, 1, 2).
python_method('WupWatcher', 'schedule_quick_test', 1, 3, 4).
python_method('WupWatcher', 'schedule_detail_test', 1, 1, 2).
python_method('WupWatcher', 'process_test_queue_once', 0, 7, 6).
python_method('WupWatcher', 'cpu_ok', 0, 2, 1).
python_method('WupWatcher', 'run_quick_test', 2, 6, 5).
python_method('WupWatcher', 'run_detail_test', 2, 10, 10).
python_method('WupWatcher', 'test_loop', 0, 2, 2).
python_method('WupWatcher', 'should_watch_file', 1, 3, 4).
python_method('WupWatcher', '_is_file_ignored', 1, 11, 3).
python_method('WupWatcher', '_notify_all_configured_services', 1, 4, 4).
python_method('WupWatcher', 'on_file_change', 1, 11, 9).
python_method('WupWatcher', 'build_watched_paths', 0, 6, 6).
python_method('WupWatcher', '_create_and_start_observer', 2, 5, 6).
python_method('WupWatcher', 'start_watching', 1, 7, 11).
python_method('WupWatcher', 'create_status_table', 0, 3, 10).
python_method('WupWatcher', 'run_with_dashboard', 0, 5, 12).
python_class('wup/core.py', 'WupEventHandler').
python_method('WupEventHandler', '__init__', 1, 1, 2).
python_method('WupEventHandler', 'on_modified', 1, 2, 1).
python_method('WupEventHandler', 'on_created', 1, 2, 1).
python_method('WupEventHandler', 'on_deleted', 1, 2, 1).
python_class('wup/dependency_mapper.py', 'DependencyMapper').
python_method('DependencyMapper', '__init__', 1, 1, 2).
python_method('DependencyMapper', 'build_from_codebase', 1, 5, 7).
python_method('DependencyMapper', '_detect_framework', 0, 4, 2).
python_method('DependencyMapper', '_search_codebase', 1, 4, 2).
python_method('DependencyMapper', '_scan_endpoints', 1, 3, 3).
python_method('DependencyMapper', '_scan_python_endpoints', 1, 10, 9).
python_method('DependencyMapper', '_scan_js_endpoints', 0, 4, 7).
python_method('DependencyMapper', '_infer_service', 1, 6, 4).
python_method('DependencyMapper', 'get_endpoints_for_file', 1, 1, 4).
python_method('DependencyMapper', 'get_endpoints_for_service', 1, 1, 1).
python_method('DependencyMapper', 'get_files_for_service', 1, 1, 2).
python_method('DependencyMapper', 'get_service_for_file', 1, 3, 5).
python_method('DependencyMapper', 'to_dict', 0, 2, 5).
python_method('DependencyMapper', 'save', 1, 1, 3).
python_method('DependencyMapper', 'load', 1, 2, 6).
python_method('DependencyMapper', 'build_from_testql_scenarios', 2, 3, 7).
python_class('wup/models/config.py', 'NotifyConfig').
python_class('wup/models/config.py', 'ServiceTestConfig').
python_class('wup/models/config.py', 'ServiceConfig').
python_class('wup/models/config.py', 'WatchConfig').
python_class('wup/models/config.py', 'TestStrategyConfig').
python_class('wup/models/config.py', 'TestQLConfig').
python_class('wup/models/config.py', 'VisualDiffConfig').
python_class('wup/models/config.py', 'WebConfig').
python_class('wup/models/config.py', 'PlanfileConfig').
python_class('wup/models/config.py', 'AnomalyDetectionConfig').
python_class('wup/models/config.py', 'ProjectConfig').
python_class('wup/models/config.py', 'WupConfig').
python_class('wup/monitoring_manifest.py', 'DockerComposeService').
python_class('wup/planfile_reporter.py', 'PlanfileReporter').
python_method('PlanfileReporter', '__init__', 3, 2, 2).
python_method('PlanfileReporter', 'enabled', 0, 1, 1).
python_method('PlanfileReporter', 'report_failure', 0, 4, 8).
python_method('PlanfileReporter', 'clear_service_stage', 0, 7, 6).
python_method('PlanfileReporter', '_create_ticket', 0, 13, 7).
python_method('PlanfileReporter', '_wait_for_planfile_store_ready', 1, 6, 7).
python_method('PlanfileReporter', '_load_dedupe', 0, 4, 4).
python_method('PlanfileReporter', '_save_dedupe', 1, 1, 3).
python_method('PlanfileReporter', '_fingerprint', 0, 1, 5).
python_method('PlanfileReporter', '_parse_ticket_id', 1, 2, 2).
python_method('PlanfileReporter', '_ticket_name', 0, 1, 0).
python_method('PlanfileReporter', '_ticket_description', 0, 3, 0).
python_class('wup/testql_cli_generator.py', 'TestQLCLIGenerator').
python_method('TestQLCLIGenerator', '__init__', 1, 1, 3).
python_method('TestQLCLIGenerator', 'generate', 2, 6, 7).
python_method('TestQLCLIGenerator', '_generate_smoke_scenario', 2, 5, 3).
python_method('TestQLCLIGenerator', '_generate_command_scenario', 3, 4, 5).
python_method('TestQLCLIGenerator', 'generate_custom_scenario', 3, 3, 5).
python_method('TestQLCLIGenerator', 'print_summary', 1, 4, 5).
python_class('wup/testql_discovery.py', 'TestQLEndpointDiscovery').
python_method('TestQLEndpointDiscovery', '__init__', 2, 1, 1).
python_method('TestQLEndpointDiscovery', 'discover_scenarios', 0, 2, 3).
python_method('TestQLEndpointDiscovery', 'parse_scenario_endpoints', 1, 11, 12).
python_method('TestQLEndpointDiscovery', 'infer_service_from_scenario', 1, 4, 2).
python_method('TestQLEndpointDiscovery', 'discover_all_endpoints', 0, 6, 9).
python_method('TestQLEndpointDiscovery', 'discover_via_testql_cli', 1, 8, 6).
python_method('TestQLEndpointDiscovery', 'to_dependency_map', 0, 4, 3).
python_class('wup/testql_monitor.py', 'ProbeTarget').
python_method('ProbeTarget', 'probe', 1, 5, 4).
python_class('wup/testql_monitor.py', '_ProbeAccumulator').
python_method('_ProbeAccumulator', '__init__', 1, 2, 1).
python_method('_ProbeAccumulator', 'add', 2, 3, 3).
python_class('wup/testql_monitor.py', 'TestQLMonitor').
python_method('TestQLMonitor', '__init__', 2, 2, 2).
python_method('TestQLMonitor', '_service_map_paths', 0, 3, 3).
python_method('TestQLMonitor', '_add_config_endpoints', 1, 11, 7).
python_method('TestQLMonitor', '_add_scenario_probes', 1, 5, 5).
python_method('TestQLMonitor', '_add_service_map_probes', 1, 5, 5).
python_method('TestQLMonitor', 'discover_probes_by_service', 0, 2, 4).
python_method('TestQLMonitor', '_resolve_base_url_for_service', 1, 8, 7).
python_method('TestQLMonitor', '_probeable_url', 2, 4, 2).
python_method('TestQLMonitor', 'probes_for_service', 2, 9, 10).
python_method('TestQLMonitor', '_sort_probes_for_live', 1, 1, 2).
python_method('TestQLMonitor', 'run_probes', 2, 5, 4).
python_method('TestQLMonitor', 'suggested_endpoints_by_service', 0, 5, 6).
python_method('TestQLMonitor', '_resolve_base_url', 0, 4, 3).
python_method('TestQLMonitor', '_join_base', 2, 5, 1).
python_class('wup/testql_watcher.py', 'BrowserNotifier').
python_method('BrowserNotifier', '__init__', 2, 13, 1).
python_method('BrowserNotifier', 'notify', 1, 3, 7).
python_class('wup/testql_watcher.py', 'TestQLWatcher').
python_method('TestQLWatcher', '__init__', 7, 13, 12).
python_method('TestQLWatcher', '_normalize_fleet_health_entry', 0, 6, 8).
python_method('TestQLWatcher', '_load_service_health', 0, 4, 4).
python_method('TestQLWatcher', '_save_service_health', 0, 1, 2).
python_method('TestQLWatcher', '_record_health_transition', 0, 9, 12).
python_method('TestQLWatcher', '_tokenize_service', 1, 3, 3).
python_method('TestQLWatcher', '_get_config_endpoints_for_service', 1, 10, 5).
python_method('TestQLWatcher', '_to_full_url_for_service', 2, 5, 2).
python_method('TestQLWatcher', '_resolve_base_url_for_service', 1, 8, 7).
python_method('TestQLWatcher', '_resolve_base_url', 0, 5, 3).
python_method('TestQLWatcher', '_to_full_url', 1, 5, 2).
python_method('TestQLWatcher', '_discover_scenarios', 0, 2, 3).
python_method('TestQLWatcher', 'get_service_config', 1, 3, 0).
python_method('TestQLWatcher', '_score_scenario', 2, 10, 4).
python_method('TestQLWatcher', '_get_scored_scenarios', 3, 4, 2).
python_method('TestQLWatcher', '_get_smoke_fallback', 1, 6, 3).
python_method('TestQLWatcher', '_select_scenarios_for_service', 1, 9, 8).
python_method('TestQLWatcher', '_filter_scenarios_by_type', 2, 8, 1).
python_method('TestQLWatcher', '_scenario_matches_type', 2, 4, 1).
python_method('TestQLWatcher', '_run_testql', 2, 2, 2).
python_method('TestQLWatcher', '_write_track', 0, 11, 9).
python_method('TestQLWatcher', '_quick_timeout', 0, 3, 1).
python_method('TestQLWatcher', '_merge_endpoints', 2, 3, 3).
python_method('TestQLWatcher', '_run_scenario_quick', 3, 6, 8).
python_method('TestQLWatcher', '_quick_pass_actions', 2, 11, 8).
python_method('TestQLWatcher', '_quick_probe_limit', 1, 3, 1).
python_method('TestQLWatcher', '_quick_probe_timeout', 0, 3, 2).
python_method('TestQLWatcher', '_run_live_http_probes', 2, 6, 7).
python_method('TestQLWatcher', '_try_parse_json_summary', 1, 8, 4).
python_method('TestQLWatcher', '_try_find_line_summary', 1, 7, 4).
python_method('TestQLWatcher', '_summarize_health_scenario_failure', 1, 8, 4).
python_method('TestQLWatcher', '_run_fleet_health_scenario', 0, 10, 16).
python_method('TestQLWatcher', 'run_quick_test', 2, 9, 10).
python_method('TestQLWatcher', '_publish_visual_events', 2, 6, 4).
python_method('TestQLWatcher', 'run_detail_test', 2, 9, 11).
python_method('TestQLWatcher', 'process_changed_file_once', 1, 4, 5).
python_method('TestQLWatcher', '_run_periodic_probes_once', 0, 5, 4).
python_method('TestQLWatcher', '_start_periodic_probe_thread', 0, 3, 6).
python_method('TestQLWatcher', 'start_watching', 1, 1, 3).
python_class('wup/visual_diff.py', 'VisualDiffer').
python_method('VisualDiffer', '__init__', 2, 1, 2).
python_method('VisualDiffer', '_pages_for_service', 2, 11, 4).
python_method('VisualDiffer', '_categorize_page_result', 6, 6, 6).
python_method('VisualDiffer', '_print_scan_summary', 4, 8, 7).
python_method('VisualDiffer', 'run_for_service', 2, 7, 11).
python_method('VisualDiffer', '_check_page', 2, 4, 9).
python_method('VisualDiffer', '_write_diff_event', 3, 1, 6).
python_method('VisualDiffer', 'get_recent_diffs', 1, 7, 11).
python_class('wup/web_client.py', 'WebClient').
python_method('WebClient', '__init__', 1, 2, 2).
python_method('WebClient', 'is_active', 0, 3, 2).
python_method('WebClient', '_headers', 0, 2, 0).
python_method('WebClient', 'send_event', 1, 5, 8).
python_method('WebClient', 'send_regression', 5, 1, 1).
python_method('WebClient', 'send_pass', 2, 1, 1).
python_method('WebClient', 'send_health_transition', 3, 1, 1).
python_method('WebClient', 'send_visual_diff', 3, 1, 1).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('cli-smoke.testql.toon.yaml', 'cli').
testql_scenario('cli-wup.testql.toon.yaml', 'cli').
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/cli-smoke.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/cli-wup.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
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

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
