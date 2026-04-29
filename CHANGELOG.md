# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

