# WUP Test Plan

## Objective
Eliminate potential usage problems, optimize execution time, improve reaction time, and increase work efficiency.

## Test Categories

### 1. Service Inference Tests (`tests/test_service_inference.py`)

**Unit Tests:**
- `test_infer_service_with_empty_paths_uses_configured_services` - Verify configured services are used when paths are empty
- `test_infer_service_with_explicit_paths_matches_path_patterns` - Test explicit path matching
- `test_infer_service_with_auto_detection_matches_name_segments` - Test auto-detection with service name matching
- `test_infer_service_returns_none_for_unmatched_files` - Verify None returned when no match
- `test_infer_service_with_dependency_mapper_fallback` - Test dependency mapper integration

**Edge Cases:**
- `test_infer_service_with_duplicate_service_names` - Handle duplicate service names
- `test_infer_service_with_nested_paths` - Test nested directory structures
- `test_infer_service_with_special_characters_in_names` - Test special characters
- `test_infer_service_with_case_insensitive_matching` - Verify case handling
- `test_infer_service_with_unicode_paths` - Test Unicode support

### 2. CLI Scenario Filtering Tests (`tests/test_cli_filtering.py`)

**Unit Tests:**
- `test_filter_scenarios_web_service_excludes_cli_scenarios` - Verify CLI scenarios excluded for web services
- `test_filter_scenarios_shell_service_only_cli_scenarios` - Verify only CLI scenarios for shell services
- `test_filter_scenarios_auto_service_all_scenarios` - Verify no filtering for auto services
- `test_score_scenario_cli_requires_exact_match` - Test CLI scenario exact matching
- `test_score_scenario_non_cli_uses_original_scoring` - Test non-CLI scenario scoring

**Integration Tests:**
- `test_select_scenarios_for_service_with_mixed_types` - Test mixed service types
- `test_select_scenarios_for_service_with_no_matching_scenarios` - Test fallback behavior
- `test_select_scenarios_for_service_with_smoke_scenario_type_check` - Test smoke scenario type matching

### 3. Auto-Detection Tests (`tests/test_auto_detection.py`)

**Unit Tests:**
- `test_auto_generate_config_detects_cli_packages` - Test CLI package detection
- `test_auto_generate_config_detects_web_frameworks` - Test web framework detection
- `test_auto_generate_config_mixed_project_handling` - Test mixed project handling
- `test_auto_generate_config_no_cli_uses_default` - Test default config for non-CLI projects

**Integration Tests:**
- `test_watch_auto_generates_config_when_missing` - Test watch auto-generation
- `test_watch_uses_existing_config_when_present` - Test existing config usage
- `test_init_cli_generates_scenarios` - Test scenario generation
- `test_init_cli_merge_with_existing_config` - Test config merging

### 4. Performance Tests (`tests/test_performance.py`)

**Large Project Tests:**
- `test_service_inference_with_1000_files` - Performance with 1000 files
- `test_service_inference_with_100_services` - Performance with 100 services
- `test_scenario_selection_with_100_scenarios` - Performance with 100 scenarios
- `test_file_change_handling_with_rapid_changes` - Test rapid file changes

**Optimization Targets:**
- Service inference: <10ms for 1000 files
- Scenario selection: <5ms for 100 scenarios
- File change handling: <50ms from change to queue
- Memory usage: <50MB for 1000 files

### 5. Edge Case Tests (`tests/test_edge_cases.py`)

**Project Type Tests:**
- `test_pure_cli_project` - Test pure CLI project setup
- `test_pure_web_project` - Test pure web project setup
- `test_mixed_cli_web_project` - Test mixed project setup
- `test_monorepo_with_multiple_services` - Test monorepo setup
- `test_project_with_no_entry_points` - Test project without CLI entry points

**Configuration Tests:**
- `test_empty_service_paths` - Test empty service paths handling
- `test_missing_service_config` - Test missing service configuration
- `test_invalid_service_type` - Test invalid service type handling
- `test_malformed_yaml_config` - Test malformed YAML handling
- `test_config_with_circular_dependencies` - Test circular dependency handling

### 6. Reaction Time Tests (`tests/test_reaction_time.py`)

**Debouncing Tests:**
- `test_debounce_with_single_change` - Test single change debouncing
- `test_debounce_with_rapid_changes` - Test rapid changes debouncing
- `test_debounce_with_cooldown` - Test cooldown behavior

**Queue Processing Tests:**
- `test_queue_processing_order` - Test queue processing order
- `test_queue_max_queue_limit` - Test queue limit enforcement
- `test_queue_priority_handling` - Test priority handling

### 7. Efficiency Tests (`tests/test_efficiency.py`)

**Coincidence Detection Tests:**
- `test_coincidence_detection_shell_web` - Test shell-web coincidence
- `test_coincidence_detection_auto_explicit` - Test auto-explicit coincidence
- `test_coincidence_detection_no_matches` - Test no coincidence case

**Resource Usage Tests:**
- `test_memory_usage_with_large_file_count` - Test memory efficiency
- `test_cpu_usage_during_idle` - Test idle CPU usage
- `test_cpu_usage_during_test_execution` - Test test execution CPU usage

## Test Implementation Priority

**High Priority (Critical for usage):**
1. Service inference tests - prevents incorrect service matching
2. CLI filtering tests - ensures correct scenario assignment
3. Auto-detection tests - validates init-cli and watch auto-generation

**Medium Priority (Performance optimization):**
4. Performance tests - identifies bottlenecks
5. Reaction time tests - improves user experience

**Low Priority (Edge cases):**
6. Edge case tests - handles rare scenarios
7. Efficiency tests - resource optimization

## Test Metrics

**Coverage Targets:**
- Service inference: 95%+ coverage
- CLI filtering: 95%+ coverage
- Auto-detection: 90%+ coverage
- Overall codebase: 85%+ coverage

**Performance Targets:**
- Service inference: <10ms for 1000 files
- Scenario selection: <5ms for 100 scenarios
- File change to test queue: <50ms
- Quick test execution: <2s for 3 scenarios
- Detail test execution: <10s for 10 scenarios

**Quality Targets:**
- Zero critical bugs in production
- <5% flaky test rate
- <100ms average test execution time for unit tests

## Implementation Plan

1. Create test file structure
2. Implement service inference tests (highest priority)
3. Implement CLI filtering tests (highest priority)
4. Implement auto-detection tests (highest priority)
5. Implement performance tests (medium priority)
6. Implement edge case tests (low priority)
7. Implement reaction time tests (medium priority)
8. Implement efficiency tests (low priority)
9. Add CI/CD integration
10. Add performance regression monitoring
