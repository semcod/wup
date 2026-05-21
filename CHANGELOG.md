# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

