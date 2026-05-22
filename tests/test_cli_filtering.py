"""Unit tests for CLI scenario filtering logic."""
import tempfile
from pathlib import Path

from wup.testql_watcher import TestQLWatcher
from wup.models.config import (
    ProjectConfig,
    ServiceConfig,
    TestQLConfig,
    WatchConfig,
    WupConfig,
)


def test_filter_scenarios_web_service_excludes_cli_scenarios():
    """Verify CLI scenarios excluded for web services."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create scenarios directory with mixed scenarios
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        cli_scenario = scenarios_dir / "cli-smoke.testql.toon.yaml"
        cli_scenario.write_text("name: cli-smoke", encoding="utf-8")
        
        web_scenario = scenarios_dir / "api-users-smoke.testql.toon.yaml"
        web_scenario.write_text("name: api-smoke", encoding="utf-8")
        
        # Create config with web service
        service_config = ServiceConfig(
            name="api-service",
            type="web",
            paths=[],
            root="",
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Filter scenarios for web service
        all_scenarios = list(scenarios_dir.glob("*.testql.toon.yaml"))
        filtered = watcher._filter_scenarios_by_type(all_scenarios, "web")
        
        # Should exclude CLI scenarios
        assert len(filtered) == 1
        assert web_scenario in filtered
        assert cli_scenario not in filtered


def test_filter_scenarios_shell_service_only_cli_scenarios():
    """Verify only CLI scenarios for shell services."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create scenarios directory with mixed scenarios
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        cli_scenario = scenarios_dir / "cli-smoke.testql.toon.yaml"
        cli_scenario.write_text("name: cli-smoke", encoding="utf-8")
        
        web_scenario = scenarios_dir / "api-users-smoke.testql.toon.yaml"
        web_scenario.write_text("name: api-smoke", encoding="utf-8")
        
        # Create config with shell service
        service_config = ServiceConfig(
            name="cli-service",
            type="shell",
            paths=[],
            root="",
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Filter scenarios for shell service
        all_scenarios = list(scenarios_dir.glob("*.testql.toon.yaml"))
        filtered = watcher._filter_scenarios_by_type(all_scenarios, "shell")
        
        # Should only include CLI scenarios
        assert len(filtered) == 1
        assert cli_scenario in filtered
        assert web_scenario not in filtered


def test_filter_scenarios_auto_service_all_scenarios():
    """Verify no filtering for auto services."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create scenarios directory with mixed scenarios
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        cli_scenario = scenarios_dir / "cli-smoke.testql.toon.yaml"
        cli_scenario.write_text("name: cli-smoke", encoding="utf-8")
        
        web_scenario = scenarios_dir / "api-users-smoke.testql.toon.yaml"
        web_scenario.write_text("name: api-smoke", encoding="utf-8")
        
        # Create config with auto service
        service_config = ServiceConfig(
            name="auto-service",
            type="auto",
            paths=[],
            root="",
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Filter scenarios for auto service
        all_scenarios = list(scenarios_dir.glob("*.testql.toon.yaml"))
        filtered = watcher._filter_scenarios_by_type(all_scenarios, "auto")
        
        # Should include all scenarios
        assert len(filtered) == 2
        assert cli_scenario in filtered
        assert web_scenario in filtered


def test_score_scenario_cli_requires_exact_match():
    """Test CLI scenario exact matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        # Create CLI scenarios for different services
        cli_wup = scenarios_dir / "cli-wup.testql.toon.yaml"
        cli_wup.write_text("name: cli-wup", encoding="utf-8")
        
        cli_koru = scenarios_dir / "cli-koru.testql.toon.yaml"
        cli_koru.write_text("name: cli-koru", encoding="utf-8")
        
        # Create config
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Score scenarios for "wup-shell" service
        tokens = watcher._tokenize_service("wup-shell")
        
        wup_score = watcher._score_scenario(cli_wup, tokens)
        koru_score = watcher._score_scenario(cli_koru, tokens)
        
        # wup scenario should match, koru should not
        assert wup_score > 0  # Should match
        assert koru_score < 0  # Should be penalized


def test_score_scenario_non_cli_uses_original_scoring():
    """Test non-CLI scenario scoring."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        # Create non-CLI scenarios
        api_scenario = scenarios_dir / "api-users-smoke.testql.toon.yaml"
        api_scenario.write_text("name: api-users-smoke", encoding="utf-8")
        
        smoke_scenario = scenarios_dir / "infra-smoke.testql.toon.yaml"
        smoke_scenario.write_text("name: infra-smoke", encoding="utf-8")
        
        # Create config
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Score scenarios for "api-users" service
        tokens = watcher._tokenize_service("api-users")
        
        api_score = watcher._score_scenario(api_scenario, tokens)
        smoke_score = watcher._score_scenario(smoke_scenario, tokens)
        
        # api scenario should score higher for api-users service
        assert api_score > smoke_score


def test_scenario_matches_type():
    """Test scenario type matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        scenarios_dir = root / "testql-scenarios"
        scenarios_dir.mkdir()
        
        cli_scenario = scenarios_dir / "cli-wup.testql.toon.yaml"
        cli_scenario.write_text("name: cli-wup", encoding="utf-8")
        
        web_scenario = scenarios_dir / "api-users.testql.toon.yaml"
        web_scenario.write_text("name: api-users", encoding="utf-8")
        
        # Create config
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[],
            watch=WatchConfig(),
            testql=TestQLConfig(scenario_dir="testql-scenarios"),
        )
        
        watcher = TestQLWatcher(
            project_root=str(root),
            scenarios_dir="testql-scenarios",
            config=config,
        )
        
        # Test type matching
        assert watcher._scenario_matches_type(cli_scenario, "shell") == True
        assert watcher._scenario_matches_type(cli_scenario, "web") == False
        assert watcher._scenario_matches_type(web_scenario, "shell") == False
        assert watcher._scenario_matches_type(web_scenario, "web") == True
        assert watcher._scenario_matches_type(cli_scenario, "auto") == True
