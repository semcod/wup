# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/wup
- **Primary Language**: python
- **Languages**: python: 52, yaml: 20, json: 13, md: 13, txt: 7
- **Analysis Mode**: static
- **Total Functions**: 1047
- **Total Classes**: 72
- **Modules**: 115
- **Entry Points**: 937

## Architecture by Module

### SUMD
- **Functions**: 375
- **Classes**: 9
- **File**: `SUMD.md`

### project.map.toon
- **Functions**: 219
- **File**: `map.toon.yaml`

### SUMR
- **Functions**: 156
- **Classes**: 9
- **File**: `SUMR.md`

### wup.testql_watcher
- **Functions**: 48
- **Classes**: 2
- **File**: `testql_watcher.py`

### wup.testql_monitor
- **Functions**: 36
- **Classes**: 3
- **File**: `testql_monitor.py`

### wup.core
- **Functions**: 29
- **Classes**: 2
- **File**: `core.py`

### wup.visual_diff
- **Functions**: 25
- **Classes**: 1
- **File**: `visual_diff.py`

### wup.assistant
- **Functions**: 24
- **Classes**: 1
- **File**: `assistant.py`

### wup.config
- **Functions**: 17
- **File**: `config.py`

### wup.dependency_mapper
- **Functions**: 16
- **Classes**: 1
- **File**: `dependency_mapper.py`

### wup.monitoring_manifest
- **Functions**: 16
- **Classes**: 1
- **File**: `monitoring_manifest.py`

### wup.cli
- **Functions**: 15
- **File**: `cli.py`

### wup.cli_scanner
- **Functions**: 12
- **Classes**: 3
- **File**: `cli_scanner.py`

### wup.planfile_reporter
- **Functions**: 11
- **Classes**: 1
- **File**: `planfile_reporter.py`

### wup.web_client
- **Functions**: 10
- **Classes**: 1
- **File**: `web_client.py`

### examples.c2004_monorepo_demo
- **Functions**: 10
- **File**: `c2004_monorepo_demo.py`

### examples.webhook_notifications
- **Functions**: 10
- **Classes**: 1
- **File**: `webhook_notifications.py`

### wup._ast_detector
- **Functions**: 9
- **Classes**: 1
- **File**: `_ast_detector.py`

### examples.visual_diff_demo
- **Functions**: 9
- **File**: `visual_diff_demo.py`

### wup.anomaly_detector
- **Functions**: 8
- **Classes**: 1
- **File**: `anomaly_detector.py`

## Key Entry Points

Main execution flows into the system:

### wup.cli.status
> Show dependency map status and configuration.
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, None.resolve

### wup.cli.init_cli
> Automatically generate wup.yaml configuration and TestQL scenarios for CLI/shell services.

Scans the project for CLI commands (entry points, setup.py
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, None.resolve, console.print

### wup.cli.sync_testql
> Discover monitoring targets and document them in wup.yaml.

With ``--write``, appends/updates the auto-generated ``monitoring:`` block
(Docker Compose
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, None.resolve, SUMD.load_config, TestQLMonitor

### wup.cli.testql_endpoints
> Discover endpoints from TestQL scenario files and build dependency map.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, Path, console.print, console.print, console.print

### scripts.run_probe_smoke.main
- **Calls**: None.resolve, SUMD.load_config, SUMD.build_monitoring_manifest, docs.NOTIFICATIONS.print, sorted, TestQLWatcher, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print

### wup.cli.watch
> Watch project for file changes and run regression tests.

Defaults (no extra flags): ``--mode testql`` and live probes every **60s**
(unless ``testql.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### examples.testql_integration.main
> Run WUP + TestQL integration demo.
- **Calls**: docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, VisualDiffConfig, CustomTestQLWatcher, docs.NOTIFICATIONS.print, watcher.dependency_mapper.build_from_codebase, watcher.dependency_mapper.save

### wup.anomaly_detector.AnomalyDetector.print_report
> Print formatted report of anomalies.
- **Calls**: self.get_summary, console.print, console.print, Table, table.add_column, table.add_column, table.add_column, table.add_column

### wup.assistant.WupAssistant._review_and_validate
> Review and validate configuration.
- **Calls**: console.print, console.print, console.print, console.print, console.print, console.print, console.print, self._validate_config

### wup.testql_watcher.TestQLWatcher.run_detail_test
- **Calls**: list, self._get_config_endpoints_for_service, self._select_scenarios_for_service, self.console.print, len, len, self._run_testql, None.append

### wup.cli.map_deps
> Build dependency map from codebase.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, None.resolve, console.print, console.print, console.print

### wup.monitoring_manifest.format_manifest_summary
> Short human-readable summary for CLI.
- **Calls**: lines.append, lines.append, manifest.get, sorted, None.join, lines.append, manifest.get, wup_services.items

### wup.assistant.WupAssistant._setup_anomaly_detection
> Setup anomaly detection configuration.
- **Calls**: console.print, Confirm.ask, console.print, hasattr, AnomalyDetectionConfig, console.print, console.print, console.print

### wup.visual_diff.VisualDiffer.run_for_service
> Scan pages for *service*, diff against stored snapshots.
Returns list of diff results (one per page).
- **Calls**: self._pages_for_service, max, self._build_progress, self._print_scan_summary, SUMR._playwright_available, SUMR._warn_playwright_missing, int, len

### wup.testql_watcher.TestQLWatcher._run_fleet_health_scenario
> Optional full TestQL run (not dry-run) for fleet-wide health scenarios.
- **Calls**: None.strip, Path, self._run_testql, self._summarize_health_scenario_failure, bool, self._write_track, self._record_health_transition, self.console.print

### wup.assistant.WupAssistant._configure_services
> Interactive service configuration.
- **Calls**: console.print, console.print, enumerate, Prompt.ask, console.print, self._add_service_interactive, len, self._edit_service

### wup._ast_detector.ASTDetector.detect
> Detect changes in Python file structure.
- **Calls**: None.endswith, file_path.read_text, ast.parse, self._extract_ast_info, self._snapshot_path, snap_path.exists, json.loads, self._compute_changes

### examples.testql_demo.simulate_testql_analysis
> Simulate WUP analysis on TestQL project.
- **Calls**: docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, Path, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print, docs.NOTIFICATIONS.print

### wup.core.WupWatcher.__init__
> Initialize the WUP watcher.

Args:
    project_root: Path to the project root directory
    deps_file: Path to the dependency map JSON file
    cpu_th
- **Calls**: Path, DependencyMapper, set, deque, defaultdict, Console, PlanfileReporter, None.exists

### wup._yaml_detector.YAMLStructureDetector.detect
- **Calls**: self._load_yaml, self._snapshot_path, self._extract_structure, snap_path.exists, snap_path.write_text, json.dumps, json.loads, self._compare_structures

### wup.assistant.WupAssistant._setup_watch
> Setup file watching configuration.
- **Calls**: console.print, console.print, enumerate, Confirm.ask, console.print, Confirm.ask, console.print, IntPrompt.ask

### wup.visual_diff._fetch_dom_snapshot
> Return a DOM structure dict for *url* using Playwright.
- **Calls**: wup.visual_diff._playwright_available, wup.visual_diff._warn_playwright_missing, async_playwright, pw.chromium.launch, browser.new_page, isinstance, str, page.goto

### wup.testql_watcher.TestQLWatcher.__init__
- **Calls**: None.__init__, self.track_dir.mkdir, BrowserNotifier, self.health_state_path.parent.mkdir, SUMD.register_testing_event_handlers, EventStore, SUMD.register_health_handlers, threading.Lock

### wup._hash_detector.HashDetector.detect
> Detect changes using hash comparison.
- **Calls**: file_path.read_text, self._compute_hash, self._snapshot_path, snap_path.exists, file_path.exists, None.strip, snap_path.write_text, AnomalyResult

### wup.dependency_mapper.DependencyMapper._scan_python_endpoints
> Scan Python files for endpoint definitions.
- **Calls**: self.project_root.rglob, py_file.read_text, str, py_file.relative_to, re.findall, endpoints.append, re.findall, None.split

### wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
> Extract endpoints from a TestQL scenario file.

Args:
    scenario_path: Path to scenario file
    
Returns:
    List of endpoint paths found in the s
- **Calls**: list, re.compile, api_pattern.findall, set, open, f.read, endpoints.append, yaml.safe_load

### wup.assistant.WupAssistant._setup_visual_diff
> Setup visual diff configuration.
- **Calls**: console.print, Confirm.ask, console.print, Prompt.ask, console.print, enumerate, Confirm.ask, console.print

### wup.testql_watcher.TestQLWatcher._write_track
- **Calls**: int, None.replace, None.splitlines, None.splitlines, track_path.write_text, self.browser_notifier.notify, time.time, self._summarize_testql_failure

### wup.cli.init
> Initialize a new wup.yaml configuration file.
- **Calls**: app.command, typer.Argument, typer.Option, None.resolve, Path, output_path.exists, SUMD.get_default_config, SUMD.save_config

### wup.core.WupWatcher.run_detail_test
> Run a detailed test for a service with blame report.

Args:
    service: Service name
    endpoints: List of endpoints to test

Returns:
    Dictionar
- **Calls**: self.console.print, len, self.console.print, self.planfile_reporter.report_failure, self.console.print, urllib.request.Request, subprocess.run, len

## Process Flows

Key execution flows identified:

### Flow 1: status
```
status [wup.cli]
```

### Flow 2: init_cli
```
init_cli [wup.cli]
```

### Flow 3: sync_testql
```
sync_testql [wup.cli]
```

### Flow 4: testql_endpoints
```
testql_endpoints [wup.cli]
```

### Flow 5: main
```
main [scripts.run_probe_smoke]
  └─ →> load_config
  └─ →> build_monitoring_manifest
  └─ →> print
```

### Flow 6: watch
```
watch [wup.cli]
```

### Flow 7: print_report
```
print_report [wup.anomaly_detector.AnomalyDetector]
```

### Flow 8: _review_and_validate
```
_review_and_validate [wup.assistant.WupAssistant]
```

### Flow 9: run_detail_test
```
run_detail_test [wup.testql_watcher.TestQLWatcher]
```

### Flow 10: map_deps
```
map_deps [wup.cli]
```

## Key Classes

### wup.testql_watcher.TestQLWatcher
> WUP watcher running selective TestQL scenarios for changed services.
- **Methods**: 46
- **Key Methods**: wup.testql_watcher.TestQLWatcher.__init__, wup.testql_watcher.TestQLWatcher._normalize_fleet_health_entry, wup.testql_watcher.TestQLWatcher._load_service_health, wup.testql_watcher.TestQLWatcher._record_health_transition, wup.testql_watcher.TestQLWatcher._tokenize_service, wup.testql_watcher.TestQLWatcher._get_config_endpoints_for_service, wup.testql_watcher.TestQLWatcher._to_full_url_for_service, wup.testql_watcher.TestQLWatcher._resolve_base_url_for_service, wup.testql_watcher.TestQLWatcher._resolve_base_url, wup.testql_watcher.TestQLWatcher._to_full_url
- **Inherits**: WupWatcher

### wup.core.WupWatcher
> Intelligent file watcher for regression testing.

Implements 3-layer testing:
1. Detection Layer: Fi
- **Methods**: 25
- **Key Methods**: wup.core.WupWatcher.__init__, wup.core.WupWatcher._to_relative_path, wup.core.WupWatcher.infer_service, wup.core.WupWatcher._is_coincident_pair, wup.core.WupWatcher.detect_service_coincidences, wup.core.WupWatcher._services_share_domain, wup.core.WupWatcher.get_service_config, wup.core.WupWatcher.should_test, wup.core.WupWatcher.schedule_quick_test, wup.core.WupWatcher.schedule_detail_test

### wup.assistant.WupAssistant
> Interactive configuration assistant.
- **Methods**: 23
- **Key Methods**: wup.assistant.WupAssistant.__init__, wup.assistant.WupAssistant._dispatch_menu_choice, wup.assistant.WupAssistant.run, wup.assistant.WupAssistant._init_project, wup.assistant.WupAssistant._detect_framework, wup.assistant.WupAssistant._auto_detect_services, wup.assistant.WupAssistant._detect_service_type, wup.assistant.WupAssistant._configure_services, wup.assistant.WupAssistant._add_service_interactive, wup.assistant.WupAssistant._edit_service

### wup.dependency_mapper.DependencyMapper
> Maps project dependencies for intelligent testing.
- **Methods**: 16
- **Key Methods**: wup.dependency_mapper.DependencyMapper.__init__, wup.dependency_mapper.DependencyMapper.build_from_codebase, wup.dependency_mapper.DependencyMapper._detect_framework, wup.dependency_mapper.DependencyMapper._search_codebase, wup.dependency_mapper.DependencyMapper._scan_endpoints, wup.dependency_mapper.DependencyMapper._scan_python_endpoints, wup.dependency_mapper.DependencyMapper._scan_js_endpoints, wup.dependency_mapper.DependencyMapper._infer_service, wup.dependency_mapper.DependencyMapper.get_endpoints_for_file, wup.dependency_mapper.DependencyMapper.get_endpoints_for_service

### wup.testql_monitor.TestQLMonitor
> Build and run live probes from TestQL scenarios + WUP config.
- **Methods**: 14
- **Key Methods**: wup.testql_monitor.TestQLMonitor.__init__, wup.testql_monitor.TestQLMonitor._service_map_paths, wup.testql_monitor.TestQLMonitor._add_config_endpoints, wup.testql_monitor.TestQLMonitor._add_scenario_probes, wup.testql_monitor.TestQLMonitor._add_service_map_probes, wup.testql_monitor.TestQLMonitor.discover_probes_by_service, wup.testql_monitor.TestQLMonitor._resolve_base_url_for_service, wup.testql_monitor.TestQLMonitor._probeable_url, wup.testql_monitor.TestQLMonitor.probes_for_service, wup.testql_monitor.TestQLMonitor._sort_probes_for_live

### wup.planfile_reporter.PlanfileReporter
> Create deduplicated planfile tickets for WUP-detected failures.
- **Methods**: 12
- **Key Methods**: wup.planfile_reporter.PlanfileReporter.__init__, wup.planfile_reporter.PlanfileReporter.enabled, wup.planfile_reporter.PlanfileReporter.report_failure, wup.planfile_reporter.PlanfileReporter.clear_service_stage, wup.planfile_reporter.PlanfileReporter._create_ticket, wup.planfile_reporter.PlanfileReporter._wait_for_planfile_store_ready, wup.planfile_reporter.PlanfileReporter._load_dedupe, wup.planfile_reporter.PlanfileReporter._save_dedupe, wup.planfile_reporter.PlanfileReporter._fingerprint, wup.planfile_reporter.PlanfileReporter._parse_ticket_id

### wup.cli_scanner.CLIScanner
> Scanner for detecting CLI commands in a project.
- **Methods**: 12
- **Key Methods**: wup.cli_scanner.CLIScanner.__init__, wup.cli_scanner.CLIScanner.scan, wup.cli_scanner.CLIScanner._scan_setup_py, wup.cli_scanner.CLIScanner._scan_setup_cfg, wup.cli_scanner.CLIScanner._scan_pyproject_toml, wup.cli_scanner.CLIScanner._scan_main_modules, wup.cli_scanner.CLIScanner._parse_entry_points_dict, wup.cli_scanner.CLIScanner._add_entry_point, wup.cli_scanner.CLIScanner.infer_command_args, wup.cli_scanner.CLIScanner._find_module_path

### wup.visual_diff.VisualDiffer
> Triggered by TestQLWatcher after a file change.

Usage::

    differ = VisualDiffer(project_root, co
- **Methods**: 9
- **Key Methods**: wup.visual_diff.VisualDiffer.__init__, wup.visual_diff.VisualDiffer._pages_for_service, wup.visual_diff.VisualDiffer._categorize_page_result, wup.visual_diff.VisualDiffer._print_scan_summary, wup.visual_diff.VisualDiffer.run_for_service, wup.visual_diff.VisualDiffer._build_progress, wup.visual_diff.VisualDiffer._check_page, wup.visual_diff.VisualDiffer._write_diff_event, wup.visual_diff.VisualDiffer.get_recent_diffs

### wup._ast_detector.ASTDetector
> Detect changes in Python files using AST comparison.
- **Methods**: 9
- **Key Methods**: wup._ast_detector.ASTDetector.__init__, wup._ast_detector.ASTDetector._collect_import, wup._ast_detector.ASTDetector._collect_import_from, wup._ast_detector.ASTDetector._collect_class, wup._ast_detector.ASTDetector._collect_function, wup._ast_detector.ASTDetector._extract_ast_info, wup._ast_detector.ASTDetector._snapshot_path, wup._ast_detector.ASTDetector._compute_changes, wup._ast_detector.ASTDetector.detect
- **Inherits**: BaseDetector

### wup.web_client.WebClient
> Async event sink for the wupbro backend.

Usage::

    client = WebClient(config.web)
    await clie
- **Methods**: 8
- **Key Methods**: wup.web_client.WebClient.__init__, wup.web_client.WebClient.is_active, wup.web_client.WebClient._headers, wup.web_client.WebClient.send_event, wup.web_client.WebClient.send_regression, wup.web_client.WebClient.send_pass, wup.web_client.WebClient.send_health_transition, wup.web_client.WebClient.send_visual_diff

### wup._yaml_detector.YAMLStructureDetector
> Detect structural changes in YAML files.
- **Methods**: 8
- **Key Methods**: wup._yaml_detector.YAMLStructureDetector.__init__, wup._yaml_detector.YAMLStructureDetector._load_yaml, wup._yaml_detector.YAMLStructureDetector._extract_structure, wup._yaml_detector.YAMLStructureDetector._snapshot_path, wup._yaml_detector.YAMLStructureDetector._compare_structures, wup._yaml_detector.YAMLStructureDetector._compare_dict_structures, wup._yaml_detector.YAMLStructureDetector.detect, wup._yaml_detector.YAMLStructureDetector._generate_suggestions
- **Inherits**: BaseDetector

### wup.testql_discovery.TestQLEndpointDiscovery
> Discover endpoints from TestQL scenario files.
- **Methods**: 7
- **Key Methods**: wup.testql_discovery.TestQLEndpointDiscovery.__init__, wup.testql_discovery.TestQLEndpointDiscovery.discover_scenarios, wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints, wup.testql_discovery.TestQLEndpointDiscovery.infer_service_from_scenario, wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints, wup.testql_discovery.TestQLEndpointDiscovery.discover_via_testql_cli, wup.testql_discovery.TestQLEndpointDiscovery.to_dependency_map

### wup.anomaly_detector.AnomalyDetector
> Main anomaly detector combining multiple detection methods.
- **Methods**: 6
- **Key Methods**: wup.anomaly_detector.AnomalyDetector.__init__, wup.anomaly_detector.AnomalyDetector._should_scan, wup.anomaly_detector.AnomalyDetector.scan_file, wup.anomaly_detector.AnomalyDetector.scan_directory, wup.anomaly_detector.AnomalyDetector.get_summary, wup.anomaly_detector.AnomalyDetector.print_report

### wup.testql_cli_generator.TestQLCLIGenerator
> Generate TestQL scenarios for CLI command testing.
- **Methods**: 6
- **Key Methods**: wup.testql_cli_generator.TestQLCLIGenerator.__init__, wup.testql_cli_generator.TestQLCLIGenerator.generate, wup.testql_cli_generator.TestQLCLIGenerator._generate_smoke_scenario, wup.testql_cli_generator.TestQLCLIGenerator._generate_command_scenario, wup.testql_cli_generator.TestQLCLIGenerator.generate_custom_scenario, wup.testql_cli_generator.TestQLCLIGenerator.print_summary

### wup.cli_config_generator.CLIConfigGenerator
> Generate wup.yaml configuration for CLI/shell services.
- **Methods**: 6
- **Key Methods**: wup.cli_config_generator.CLIConfigGenerator.__init__, wup.cli_config_generator.CLIConfigGenerator.generate, wup.cli_config_generator.CLIConfigGenerator._generate_config, wup.cli_config_generator.CLIConfigGenerator._create_shell_service, wup.cli_config_generator.CLIConfigGenerator._save_config, wup.cli_config_generator.CLIConfigGenerator.print_summary

### wup.bus.EventBus
> Simple in-memory event bus and command/query dispatcher.
- **Methods**: 5
- **Key Methods**: wup.bus.EventBus.__init__, wup.bus.EventBus.subscribe, wup.bus.EventBus.publish, wup.bus.EventBus.execute, wup.bus.EventBus.query

### wup.testing.handlers.health_handlers.ServiceHealthProjection
> Maintains the materialized view of service health.
- **Methods**: 5
- **Key Methods**: wup.testing.handlers.health_handlers.ServiceHealthProjection.__init__, wup.testing.handlers.health_handlers.ServiceHealthProjection._load_initial_state, wup.testing.handlers.health_handlers.ServiceHealthProjection._save_state, wup.testing.handlers.health_handlers.ServiceHealthProjection.handle_health_changed, wup.testing.handlers.health_handlers.ServiceHealthProjection.handle_get_health

### examples.webhook_notifications.NotificationRouter
> Routes WUP events to configured notification channels.
- **Methods**: 5
- **Key Methods**: examples.webhook_notifications.NotificationRouter.__init__, examples.webhook_notifications.NotificationRouter.add_slack, examples.webhook_notifications.NotificationRouter.add_teams, examples.webhook_notifications.NotificationRouter.add_discord, examples.webhook_notifications.NotificationRouter.send

### examples.testql_integration.CustomTestQLWatcher
> Custom WUP watcher integrated with TestQL test framework.

Overrides test methods to run actual Test
- **Methods**: 5
- **Key Methods**: examples.testql_integration.CustomTestQLWatcher.__init__, examples.testql_integration.CustomTestQLWatcher.run_quick_test, examples.testql_integration.CustomTestQLWatcher.run_detail_test, examples.testql_integration.CustomTestQLWatcher._find_scenarios_for_service, examples.testql_integration.CustomTestQLWatcher._generate_blame_report
- **Inherits**: WupWatcher

### wup._hash_detector.HashDetector
> Fast anomaly detection using file hashes.
- **Methods**: 4
- **Key Methods**: wup._hash_detector.HashDetector.__init__, wup._hash_detector.HashDetector._compute_hash, wup._hash_detector.HashDetector._snapshot_path, wup._hash_detector.HashDetector.detect
- **Inherits**: BaseDetector

## Data Transformation Functions

Key functions that process and transform data:

### SUMR._try_parse_json_summary

### SUMR.process_changed_file_once

### SUMR._parse_api_lines

### SUMR.parse_scenario_probes

### SUMR._parse_endpoint_row

### SUMR.parse_service_map_probes

### SUMR.process_test_queue_once

### SUMR._review_and_validate

### SUMR._validate_config

### SUMD.test_parse_scenario_probes_full_url

### SUMD.test_process_changed_file_creates_track_on_failure

### SUMD._parse_project_config

### SUMD._parse_watch_config

### SUMD._parse_services_config

### SUMD._parse_strategy_config

### SUMD._parse_testql_config

### SUMD._parse_visual_diff_config

### SUMD._parse_web_config

### SUMD._parse_planfile_config

### SUMD.validate_config

### SUMD._parse_port_mapping

### SUMD.format_manifest_summary

### SUMD._parse_api_lines

### SUMD.parse_scenario_probes

### SUMD._parse_endpoint_row

## Behavioral Patterns

### recursion__normalize
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: wup.web_client._normalize

### recursion__flatten
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: wup.visual_diff._flatten

### state_machine_ServiceHealthProjection
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: wup.testing.handlers.health_handlers.ServiceHealthProjection.__init__, wup.testing.handlers.health_handlers.ServiceHealthProjection._load_initial_state, wup.testing.handlers.health_handlers.ServiceHealthProjection._save_state, wup.testing.handlers.health_handlers.ServiceHealthProjection.handle_health_changed, wup.testing.handlers.health_handlers.ServiceHealthProjection.handle_get_health

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `wup.cli.status` - 121 calls
- `examples.ci_cd_integration.show_ci_cd_demo` - 69 calls
- `examples.webhook_notifications.show_webhook_demo` - 68 calls
- `wup.cli.init_cli` - 47 calls
- `wup.cli.sync_testql` - 45 calls
- `wup.cli.testql_endpoints` - 40 calls
- `scripts.run_probe_smoke.main` - 38 calls
- `wup.cli.watch` - 37 calls
- `examples.testql_integration.main` - 27 calls
- `wup.anomaly_detector.AnomalyDetector.print_report` - 26 calls
- `examples.c2004_monorepo_demo.analyze_monorepo` - 26 calls
- `examples.visual_diff_demo.demo_snapshot_persistence` - 26 calls
- `wup.testql_watcher.TestQLWatcher.run_detail_test` - 25 calls
- `wup.cli.map_deps` - 25 calls
- `wup.monitoring_manifest.format_manifest_summary` - 25 calls
- `wup.visual_diff.VisualDiffer.run_for_service` - 22 calls
- `wup._ast_detector.ASTDetector.detect` - 19 calls
- `examples.testql_demo.simulate_testql_analysis` - 18 calls
- `wup._yaml_detector.YAMLStructureDetector.detect` - 17 calls
- `examples.c2004_monorepo_demo.simulate_monorepo` - 17 calls
- `wup._hash_detector.HashDetector.detect` - 16 calls
- `wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints` - 16 calls
- `examples.visual_diff_demo.demo_diff_algorithm` - 16 calls
- `examples.visual_diff_demo.demo_config_yaml_round_trip` - 16 calls
- `wup.cli.init` - 16 calls
- `wup.core.WupWatcher.run_detail_test` - 16 calls
- `examples.visual_diff_demo.main` - 15 calls
- `wup.monitoring_manifest.build_monitoring_manifest` - 15 calls
- `wup.anomaly_detector.AnomalyDetector.scan_directory` - 14 calls
- `examples.visual_diff_demo.demo_live_page` - 14 calls
- `wup.monitoring_manifest.load_monitoring_manifest_from_yaml` - 14 calls
- `wup.cli_config_generator.CLIConfigGenerator.print_summary` - 13 calls
- `wup.core.WupWatcher.start_watching` - 13 calls
- `wup.core.WupWatcher.create_status_table` - 13 calls
- `wup.core.WupWatcher.run_with_dashboard` - 13 calls
- `examples.testql_integration.CustomTestQLWatcher.run_detail_test` - 13 calls
- `wup.visual_diff.VisualDiffer.get_recent_diffs` - 12 calls
- `examples.testql_demo.simulate_with_mock_data` - 12 calls
- `wup.cli.assistant` - 12 calls
- `wup.config.save_config` - 12 calls

## System Interactions

How components interact:

```mermaid
graph TD
    status --> command
    status --> Option
    init_cli --> command
    init_cli --> Argument
    init_cli --> Option
    sync_testql --> command
    sync_testql --> Argument
    sync_testql --> Option
    testql_endpoints --> command
    testql_endpoints --> Argument
    testql_endpoints --> Option
    testql_endpoints --> Path
    main --> resolve
    main --> load_config
    main --> build_monitoring_man
    main --> print
    main --> sorted
    watch --> command
    watch --> Argument
    watch --> Option
    main --> VisualDiffConfig
    main --> CustomTestQLWatcher
    print_report --> get_summary
    print_report --> print
    print_report --> Table
    print_report --> add_column
    _review_and_validate --> print
    run_detail_test --> list
    run_detail_test --> _get_config_endpoint
    run_detail_test --> _select_scenarios_fo
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.