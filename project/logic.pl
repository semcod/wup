% ── Project Metadata ─────────────────────────────────────
project_metadata('wup', '0.2.39', 'python').

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
project_file('tests/test_wup.py', 1800, 'python').
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
project_file('wup/core.py', 653, 'python').
project_file('wup/dependency_mapper.py', 285, 'python').
project_file('wup/models/__init__.py', 35, 'python').
project_file('wup/models/config.py', 166, 'python').
project_file('wup/monitoring_manifest.py', 341, 'python').
project_file('wup/planfile_reporter.py', 204, 'python').
project_file('wup/testql_cli_generator.py', 216, 'python').
project_file('wup/testql_discovery.py', 230, 'python').
project_file('wup/testql_monitor.py', 522, 'python').
project_file('wup/testql_watcher.py', 843, 'python').
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
python_method('TestConfigModels', 'test_testql_config', 0, 4, 2).
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
python_method('WupWatcher', 'infer_service', 1, 12, 13).
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
python_method('WupWatcher', 'on_file_change', 1, 14, 10).
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
python_method('TestQLWatcher', '_select_scenarios_for_service', 1, 14, 9).
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

