# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/wup
- **Primary Language**: python
- **Languages**: python: 41, yaml: 15, txt: 5, json: 2, toml: 2
- **Analysis Mode**: static
- **Total Functions**: 363
- **Total Classes**: 39
- **Modules**: 69
- **Entry Points**: 322

## Architecture by Module

### project.map.toon
- **Functions**: 123
- **File**: `map.toon.yaml`

### wup.core
- **Functions**: 24
- **Classes**: 2
- **File**: `core.py`

### wup.assistant
- **Functions**: 23
- **Classes**: 1
- **File**: `assistant.py`

### wup.anomaly_detector
- **Functions**: 23
- **Classes**: 6
- **File**: `anomaly_detector.py`

### wup.testql_watcher
- **Functions**: 18
- **Classes**: 2
- **File**: `testql_watcher.py`

### wup.dependency_mapper
- **Functions**: 16
- **Classes**: 1
- **File**: `dependency_mapper.py`

### wup.visual_diff
- **Functions**: 16
- **Classes**: 1
- **File**: `visual_diff.py`

### wupbro.wupbro.notifications
- **Functions**: 15
- **Classes**: 1
- **File**: `notifications.py`

### wup.web_client
- **Functions**: 10
- **Classes**: 1
- **File**: `web_client.py`

### wupbro.wupbro.routers.notifications
- **Functions**: 10
- **File**: `notifications.py`

### examples.webhook_notifications
- **Functions**: 10
- **Classes**: 1
- **File**: `webhook_notifications.py`

### examples.visual_diff_demo
- **Functions**: 9
- **File**: `visual_diff_demo.py`

### wupbro.wupbro.storage
- **Functions**: 8
- **Classes**: 1
- **File**: `storage.py`

### wup.cli
- **Functions**: 8
- **File**: `cli.py`

### wup.testql_discovery
- **Functions**: 7
- **Classes**: 1
- **File**: `testql_discovery.py`

### examples.testql_integration
- **Functions**: 6
- **Classes**: 1
- **File**: `testql_integration.py`

### wup.config
- **Functions**: 6
- **File**: `config.py`

### examples.flask-app.app.auth.routes
- **Functions**: 5
- **File**: `routes.py`

### examples.fastapi-app.app.users.routes
- **Functions**: 5
- **Classes**: 1
- **File**: `routes.py`

### wupbro.wupbro.routers.events
- **Functions**: 5
- **File**: `events.py`

## Key Entry Points

Main execution flows into the system:

### wup.cli.status
> Show dependency map status and configuration.
- **Calls**: app.command, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, None.resolve

### wup.cli.watch
> Watch project for file changes and run intelligent regression tests.

Uses a 3-layer approach:
1. Detection: File watching with heuristics
2. Priority
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### wup.cli.testql_endpoints
> Discover endpoints from TestQL scenario files and build dependency map.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, Path, console.print, console.print, console.print

### wup.anomaly_detector.ASTDetector.detect
> Detect changes in Python file structure.
- **Calls**: None.endswith, file_path.read_text, ast.parse, self._extract_ast_info, self._snapshot_path, snap_path.exists, json.loads, snap_path.write_text

### wup.assistant.WupAssistant.run
> Run the assistant.
- **Calls**: console.print, self.draft_path.exists, Panel.fit, self._quick_setup, Confirm.ask, console.print, console.print, console.print

### examples.testql_integration.main
> Run WUP + TestQL integration demo.
- **Calls**: print, print, print, VisualDiffConfig, TestQLWatcher, print, watcher.dependency_mapper.build_from_codebase, watcher.dependency_mapper.save

### wup.anomaly_detector.AnomalyDetector.print_report
> Print formatted report of anomalies.
- **Calls**: self.get_summary, console.print, console.print, Table, table.add_column, table.add_column, table.add_column, table.add_column

### wup.cli.map_deps
> Build dependency map from codebase.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, None.resolve, console.print, console.print, console.print

### wup.assistant.WupAssistant._review_and_validate
> Review and validate configuration.
- **Calls**: console.print, console.print, console.print, console.print, console.print, console.print, console.print, self._validate_config

### wup.anomaly_detector.YAMLStructureDetector._compare_structures
> Compare two structures and return differences.
- **Calls**: old.get, new.get, diffs.append, set, set, old.get, new.get, None.keys

### wup.testql_watcher.TestQLWatcher.run_quick_test
- **Calls**: wupbro.wupbro.storage.EventStore.list, self._get_config_endpoints_for_service, self._select_scenarios_for_service, self.get_service_config, self.console.print, self._record_health_transition, self.console.print, self.console.print

### wup.assistant.WupAssistant._setup_anomaly_detection
> Setup anomaly detection configuration.
- **Calls**: console.print, Confirm.ask, console.print, hasattr, AnomalyDetectionConfig, console.print, console.print, console.print

### wup.assistant.WupAssistant._configure_services
> Interactive service configuration.
- **Calls**: console.print, console.print, enumerate, Prompt.ask, console.print, self._add_service_interactive, len, self._edit_service

### wup.testql_watcher.TestQLWatcher.run_detail_test
- **Calls**: wupbro.wupbro.storage.EventStore.list, self._get_config_endpoints_for_service, self._select_scenarios_for_service, self.console.print, len, len, self._run_testql, None.append

### wup.anomaly_detector.ASTDetector._extract_ast_info
> Extract relevant info from AST.
- **Calls**: ast.iter_child_nodes, isinstance, isinstance, None.append, None.append, isinstance, None.append, isinstance

### wup.core.WupWatcher.__init__
> Initialize the WUP watcher.

Args:
    project_root: Path to the project root directory
    deps_file: Path to the dependency map JSON file
    cpu_th
- **Calls**: Path, DependencyMapper, set, deque, defaultdict, Console, None.exists, project.map.toon.load_config

### wup.assistant.WupAssistant._setup_watch
> Setup file watching configuration.
- **Calls**: console.print, console.print, enumerate, Confirm.ask, console.print, Confirm.ask, console.print, IntPrompt.ask

### wup.anomaly_detector.YAMLStructureDetector.detect
> Detect structural changes in YAML.
- **Calls**: self._load_yaml, self._snapshot_path, self._extract_structure, snap_path.exists, snap_path.write_text, json.dumps, json.loads, self._compare_structures

### wup.dependency_mapper.DependencyMapper._scan_python_endpoints
> Scan Python files for endpoint definitions.
- **Calls**: self.project_root.rglob, py_file.read_text, str, py_file.relative_to, re.findall, endpoints.append, re.findall, None.split

### wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
> Extract endpoints from a TestQL scenario file.

Args:
    scenario_path: Path to scenario file
    
Returns:
    List of endpoint paths found in the s
- **Calls**: wupbro.wupbro.storage.EventStore.list, re.compile, api_pattern.findall, set, open, f.read, endpoints.append, yaml.safe_load

### wup.cli.init
> Initialize a new wup.yaml configuration file.
- **Calls**: app.command, typer.Argument, typer.Option, None.resolve, Path, output_path.exists, project.map.toon.get_default_config, project.map.toon.save_config

### wup.assistant.WupAssistant._setup_visual_diff
> Setup visual diff configuration.
- **Calls**: console.print, Confirm.ask, console.print, Prompt.ask, console.print, enumerate, Confirm.ask, console.print

### wup.anomaly_detector.HashDetector.detect
> Detect changes using hash comparison.
- **Calls**: file_path.read_text, self._compute_hash, self._snapshot_path, snap_path.exists, file_path.exists, None.strip, snap_path.write_text, AnomalyResult

### wup.anomaly_detector.AnomalyDetector.scan_directory
> Scan directory for anomalies.
- **Calls**: Path, console.print, directory.exists, wupbro.wupbro.storage.EventStore.list, wupbro.wupbro.storage.EventStore.list, files.extend, self.scan_file, results.extend

### wup.core.WupWatcher.infer_service
> Infer service name from file path.

Uses config services first, then dependency mapper, then heuristics.
- **Calls**: self._to_relative_path, self.dependency_mapper.get_service_for_file, _re.match, len, None.is_file, None.join, None.lower, svc.name.lower

### wup.core.WupWatcher.start_watching
> Start watching for file changes.

Args:
    watch_paths: List of paths to watch (default: from config or common source directories)
- **Calls**: WupEventHandler, Observer, observer.start, self.console.print, observer.join, self.build_watched_paths, self.console.print, observer.schedule

### wup.core.WupWatcher.run_with_dashboard
> Run watcher with live dashboard.
- **Calls**: self.build_watched_paths, WupEventHandler, Observer, observer.start, observer.join, observer.schedule, Live, None.exists

### examples.visual_diff_demo.main
- **Calls**: print, print, print, examples.visual_diff_demo.demo_diff_algorithm, examples.visual_diff_demo.demo_page_slug, examples.visual_diff_demo.demo_snapshot_persistence, examples.visual_diff_demo.demo_config_yaml_round_trip, examples.visual_diff_demo.demo_disabled_is_noop

### wup.testql_watcher.TestQLWatcher._write_track
- **Calls**: int, None.replace, track_path.write_text, self.browser_notifier.notify, time.time, None.splitlines, None.splitlines, json.dumps

### wupbro.wupbro.routers.notifications.notification_stream
> Server-Sent Events endpoint for real-time notifications.

Connect to this endpoint to receive notifications in real-time.
Requires active subscription
- **Calls**: router.get, Query, wupbro.wupbro.notifications.get_notification_manager, manager.get_subscription, manager.register_sse_client, StreamingResponse, HTTPException, event_generator

## Process Flows

Key execution flows identified:

### Flow 1: status
```
status [wup.cli]
```

### Flow 2: watch
```
watch [wup.cli]
```

### Flow 3: testql_endpoints
```
testql_endpoints [wup.cli]
```

### Flow 4: detect
```
detect [wup.anomaly_detector.ASTDetector]
```

### Flow 5: run
```
run [wup.assistant.WupAssistant]
```

### Flow 6: main
```
main [examples.testql_integration]
```

### Flow 7: print_report
```
print_report [wup.anomaly_detector.AnomalyDetector]
```

### Flow 8: map_deps
```
map_deps [wup.cli]
```

### Flow 9: _review_and_validate
```
_review_and_validate [wup.assistant.WupAssistant]
```

### Flow 10: _compare_structures
```
_compare_structures [wup.anomaly_detector.YAMLStructureDetector]
```

## Key Classes

### wup.assistant.WupAssistant
> Interactive configuration assistant.
- **Methods**: 22
- **Key Methods**: wup.assistant.WupAssistant.__init__, wup.assistant.WupAssistant.run, wup.assistant.WupAssistant._init_project, wup.assistant.WupAssistant._detect_framework, wup.assistant.WupAssistant._auto_detect_services, wup.assistant.WupAssistant._detect_service_type, wup.assistant.WupAssistant._configure_services, wup.assistant.WupAssistant._add_service_interactive, wup.assistant.WupAssistant._edit_service, wup.assistant.WupAssistant._setup_watch

### wup.core.WupWatcher
> Intelligent file watcher for regression testing.

Implements 3-layer testing:
1. Detection Layer: Fi
- **Methods**: 20
- **Key Methods**: wup.core.WupWatcher.__init__, wup.core.WupWatcher._to_relative_path, wup.core.WupWatcher.infer_service, wup.core.WupWatcher.detect_service_coincidences, wup.core.WupWatcher._services_share_domain, wup.core.WupWatcher.get_service_config, wup.core.WupWatcher.should_test, wup.core.WupWatcher.schedule_quick_test, wup.core.WupWatcher.schedule_detail_test, wup.core.WupWatcher.process_test_queue_once

### wup.dependency_mapper.DependencyMapper
> Maps project dependencies for intelligent testing.
- **Methods**: 16
- **Key Methods**: wup.dependency_mapper.DependencyMapper.__init__, wup.dependency_mapper.DependencyMapper.build_from_codebase, wup.dependency_mapper.DependencyMapper._detect_framework, wup.dependency_mapper.DependencyMapper._search_codebase, wup.dependency_mapper.DependencyMapper._scan_endpoints, wup.dependency_mapper.DependencyMapper._scan_python_endpoints, wup.dependency_mapper.DependencyMapper._scan_js_endpoints, wup.dependency_mapper.DependencyMapper._infer_service, wup.dependency_mapper.DependencyMapper.get_endpoints_for_file, wup.dependency_mapper.DependencyMapper.get_endpoints_for_service

### wup.testql_watcher.TestQLWatcher
> WUP watcher running selective TestQL scenarios for changed services.
- **Methods**: 16
- **Key Methods**: wup.testql_watcher.TestQLWatcher.__init__, wup.testql_watcher.TestQLWatcher._load_service_health, wup.testql_watcher.TestQLWatcher._save_service_health, wup.testql_watcher.TestQLWatcher._record_health_transition, wup.testql_watcher.TestQLWatcher._tokenize_service, wup.testql_watcher.TestQLWatcher._get_config_endpoints_for_service, wup.testql_watcher.TestQLWatcher._resolve_base_url, wup.testql_watcher.TestQLWatcher._to_full_url, wup.testql_watcher.TestQLWatcher._discover_scenarios, wup.testql_watcher.TestQLWatcher.get_service_config
- **Inherits**: WupWatcher

### wupbro.wupbro.notifications.NotificationManager
> Manages browser notification subscriptions and event detection.
- **Methods**: 13
- **Key Methods**: wupbro.wupbro.notifications.NotificationManager.__init__, wupbro.wupbro.notifications.NotificationManager.subscribe, wupbro.wupbro.notifications.NotificationManager.unsubscribe, wupbro.wupbro.notifications.NotificationManager.get_subscription, wupbro.wupbro.notifications.NotificationManager.list_subscriptions, wupbro.wupbro.notifications.NotificationManager.update_config, wupbro.wupbro.notifications.NotificationManager.process_event, wupbro.wupbro.notifications.NotificationManager._detect_notification_types, wupbro.wupbro.notifications.NotificationManager._should_notify, wupbro.wupbro.notifications.NotificationManager._create_payload

### wup.web_client.WebClient
> Async event sink for the wupbro backend.

Usage::

    client = WebClient(config.web)
    await clie
- **Methods**: 8
- **Key Methods**: wup.web_client.WebClient.__init__, wup.web_client.WebClient.is_active, wup.web_client.WebClient._headers, wup.web_client.WebClient.send_event, wup.web_client.WebClient.send_regression, wup.web_client.WebClient.send_pass, wup.web_client.WebClient.send_health_transition, wup.web_client.WebClient.send_visual_diff

### wup.testql_discovery.TestQLEndpointDiscovery
> Discover endpoints from TestQL scenario files.
- **Methods**: 7
- **Key Methods**: wup.testql_discovery.TestQLEndpointDiscovery.__init__, wup.testql_discovery.TestQLEndpointDiscovery.discover_scenarios, wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints, wup.testql_discovery.TestQLEndpointDiscovery.infer_service_from_scenario, wup.testql_discovery.TestQLEndpointDiscovery.discover_all_endpoints, wup.testql_discovery.TestQLEndpointDiscovery.discover_via_testql_cli, wup.testql_discovery.TestQLEndpointDiscovery.to_dependency_map

### wup.anomaly_detector.YAMLStructureDetector
> Detect structural changes in YAML files.
- **Methods**: 7
- **Key Methods**: wup.anomaly_detector.YAMLStructureDetector.__init__, wup.anomaly_detector.YAMLStructureDetector._load_yaml, wup.anomaly_detector.YAMLStructureDetector._extract_structure, wup.anomaly_detector.YAMLStructureDetector._snapshot_path, wup.anomaly_detector.YAMLStructureDetector._compare_structures, wup.anomaly_detector.YAMLStructureDetector.detect, wup.anomaly_detector.YAMLStructureDetector._generate_suggestions

### wup.visual_diff.VisualDiffer
> Triggered by TestQLWatcher after a file change.

Usage::

    differ = VisualDiffer(project_root, co
- **Methods**: 6
- **Key Methods**: wup.visual_diff.VisualDiffer.__init__, wup.visual_diff.VisualDiffer._pages_for_service, wup.visual_diff.VisualDiffer.run_for_service, wup.visual_diff.VisualDiffer._check_page, wup.visual_diff.VisualDiffer._write_diff_event, wup.visual_diff.VisualDiffer.get_recent_diffs

### wupbro.wupbro.storage.EventStore
> Thread-safe ring buffer + JSONL persistence.
- **Methods**: 6
- **Key Methods**: wupbro.wupbro.storage.EventStore.__init__, wupbro.wupbro.storage.EventStore._load_existing, wupbro.wupbro.storage.EventStore.add, wupbro.wupbro.storage.EventStore.list, wupbro.wupbro.storage.EventStore.clear, wupbro.wupbro.storage.EventStore.stats

### wup.anomaly_detector.AnomalyDetector
> Main anomaly detector combining multiple detection methods.
- **Methods**: 6
- **Key Methods**: wup.anomaly_detector.AnomalyDetector.__init__, wup.anomaly_detector.AnomalyDetector._should_scan, wup.anomaly_detector.AnomalyDetector.scan_file, wup.anomaly_detector.AnomalyDetector.scan_directory, wup.anomaly_detector.AnomalyDetector.get_summary, wup.anomaly_detector.AnomalyDetector.print_report

### examples.testql_integration.TestQLWatcher
> Custom WUP watcher integrated with TestQL test framework.

Overrides test methods to run actual Test
- **Methods**: 5
- **Key Methods**: examples.testql_integration.TestQLWatcher.__init__, examples.testql_integration.TestQLWatcher.run_quick_test, examples.testql_integration.TestQLWatcher.run_detail_test, examples.testql_integration.TestQLWatcher._find_scenarios_for_service, examples.testql_integration.TestQLWatcher._generate_blame_report
- **Inherits**: WupWatcher

### examples.webhook_notifications.NotificationRouter
> Routes WUP events to configured notification channels.
- **Methods**: 5
- **Key Methods**: examples.webhook_notifications.NotificationRouter.__init__, examples.webhook_notifications.NotificationRouter.add_slack, examples.webhook_notifications.NotificationRouter.add_teams, examples.webhook_notifications.NotificationRouter.add_discord, examples.webhook_notifications.NotificationRouter.send

### wup.core.WupEventHandler
> File system event handler for WUP watcher.
- **Methods**: 4
- **Key Methods**: wup.core.WupEventHandler.__init__, wup.core.WupEventHandler.on_modified, wup.core.WupEventHandler.on_created, wup.core.WupEventHandler.on_deleted
- **Inherits**: FileSystemEventHandler

### wup.anomaly_detector.HashDetector
> Fast anomaly detection using file hashes.
- **Methods**: 4
- **Key Methods**: wup.anomaly_detector.HashDetector.__init__, wup.anomaly_detector.HashDetector._compute_hash, wup.anomaly_detector.HashDetector._snapshot_path, wup.anomaly_detector.HashDetector.detect

### wup.anomaly_detector.ASTDetector
> Detect changes in Python files using AST comparison.
- **Methods**: 4
- **Key Methods**: wup.anomaly_detector.ASTDetector.__init__, wup.anomaly_detector.ASTDetector._extract_ast_info, wup.anomaly_detector.ASTDetector._snapshot_path, wup.anomaly_detector.ASTDetector.detect

### wup.testql_watcher.BrowserNotifier
> Send watcher events to browser-facing service and local file.
- **Methods**: 2
- **Key Methods**: wup.testql_watcher.BrowserNotifier.__init__, wup.testql_watcher.BrowserNotifier.notify

### examples.fastapi-app.app.users.routes.User
- **Methods**: 0
- **Inherits**: BaseModel

### wup.anomaly_detector.AnomalyResult
> Result of anomaly detection.
- **Methods**: 0

### wup.anomaly_detector.YAMLAnomalyConfig
> Configuration for YAML anomaly detection.
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints
> Extract endpoints from a TestQL scenario file.

Args:
    scenario_path: Path to scenario file
    

- **Output to**: wupbro.wupbro.storage.EventStore.list, re.compile, api_pattern.findall, set, open

### wup.core.WupWatcher.process_test_queue_once
- **Output to**: self.test_queue.popleft, self.console.print, self.cpu_ok, self.run_quick_test, self.schedule_detail_test

### project.map.toon.test_process_changed_file_creates_track_on_failure

### project.map.toon.validate_config

### wupbro.wupbro.notifications.NotificationManager.process_event
> Process event and generate notifications for matching subscriptions.

Returns list of (subscription_
- **Output to**: int, self._detect_notification_types, self._subscriptions.items, time.time, self._should_notify

### wup.config.validate_config
> Validate raw config dict and convert to WupConfig object.

Args:
    raw: Raw configuration dictiona
- **Output to**: raw.get, ProjectConfig, raw.get, WatchConfig, raw.get

### wup.testql_watcher.TestQLWatcher.process_changed_file_once
- **Output to**: self.on_file_change, len, self.process_test_queue_once, asyncio.sleep, str

### wup.assistant.WupAssistant._review_and_validate
> Review and validate configuration.
- **Output to**: console.print, console.print, console.print, console.print, console.print

### wup.assistant.WupAssistant._validate_config
> Validate current configuration.
- **Output to**: issues.append, issues.append, issues.append, None.replace, resolved.exists

## Behavioral Patterns

### recursion__flatten
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: wup.visual_diff._flatten

### recursion__normalize
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: wup.web_client._normalize

### recursion_list
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: wupbro.wupbro.storage.EventStore.list

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `wup.cli.status` - 97 calls
- `examples.c2004_monorepo_demo.analyze_monorepo` - 94 calls
- `wup.config.validate_config` - 82 calls
- `examples.testql_demo.simulate_testql_analysis` - 80 calls
- `examples.ci_cd_integration.show_ci_cd_demo` - 69 calls
- `examples.webhook_notifications.show_webhook_demo` - 68 calls
- `wup.cli.watch` - 40 calls
- `wup.cli.testql_endpoints` - 40 calls
- `wup.anomaly_detector.ASTDetector.detect` - 31 calls
- `wup.assistant.WupAssistant.run` - 29 calls
- `examples.testql_integration.main` - 27 calls
- `wup.anomaly_detector.AnomalyDetector.print_report` - 27 calls
- `examples.visual_diff_demo.demo_snapshot_persistence` - 26 calls
- `wup.cli.map_deps` - 25 calls
- `wup.testql_watcher.TestQLWatcher.run_quick_test` - 23 calls
- `wup.testql_watcher.TestQLWatcher.run_detail_test` - 20 calls
- `examples.c2004_monorepo_demo.simulate_monorepo` - 17 calls
- `wup.anomaly_detector.YAMLStructureDetector.detect` - 17 calls
- `wup.testql_discovery.TestQLEndpointDiscovery.parse_scenario_endpoints` - 16 calls
- `examples.visual_diff_demo.demo_diff_algorithm` - 16 calls
- `examples.visual_diff_demo.demo_config_yaml_round_trip` - 16 calls
- `wup.cli.init` - 16 calls
- `wup.anomaly_detector.HashDetector.detect` - 16 calls
- `wup.anomaly_detector.AnomalyDetector.scan_directory` - 16 calls
- `wup.core.WupWatcher.infer_service` - 15 calls
- `wup.core.WupWatcher.start_watching` - 15 calls
- `wup.core.WupWatcher.run_with_dashboard` - 15 calls
- `examples.visual_diff_demo.main` - 15 calls
- `examples.visual_diff_demo.demo_live_page` - 14 calls
- `wupbro.wupbro.routers.notifications.notification_stream` - 14 calls
- `wup.core.WupWatcher.create_status_table` - 13 calls
- `examples.testql_integration.TestQLWatcher.run_detail_test` - 13 calls
- `wupbro.wupbro.routers.drivers.dom_diff_capture` - 13 calls
- `wup.visual_diff.VisualDiffer.get_recent_diffs` - 12 calls
- `examples.testql_integration.TestQLWatcher.run_quick_test` - 12 calls
- `wup.config.save_config` - 12 calls
- `wup.cli.assistant` - 12 calls
- `wup.core.WupWatcher.on_file_change` - 11 calls
- `examples.visual_diff_demo.demo_disabled_is_noop` - 11 calls
- `examples.webhook_notifications.create_slack_payload` - 11 calls

## System Interactions

How components interact:

```mermaid
graph TD
    status --> command
    status --> Option
    watch --> command
    watch --> Argument
    watch --> Option
    testql_endpoints --> command
    testql_endpoints --> Argument
    testql_endpoints --> Option
    testql_endpoints --> Path
    detect --> endswith
    detect --> read_text
    detect --> parse
    detect --> _extract_ast_info
    detect --> _snapshot_path
    run --> print
    run --> exists
    run --> fit
    run --> _quick_setup
    run --> ask
    main --> print
    main --> VisualDiffConfig
    main --> TestQLWatcher
    print_report --> get_summary
    print_report --> print
    print_report --> Table
    print_report --> add_column
    map_deps --> command
    map_deps --> Argument
    map_deps --> Option
    map_deps --> resolve
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.