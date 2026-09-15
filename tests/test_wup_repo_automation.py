"""Repository-level contract for the TestQL → Planfile incident flow."""

from pathlib import Path

from wup.config import load_config


def test_wup_testql_and_planfile_configuration_is_runnable():
    root = Path(__file__).resolve().parents[1]
    config = load_config(root)

    assert config.project.name == "wup"
    assert config.planfile.enabled is True
    assert config.planfile.sync_on_change is True
    assert config.planfile.complete_on_recovery is True
    assert config.planfile.integrations == ["github"]
    assert config.testql.extra_args == ["--timeout", "10000"]

    integration = root / ".planfile" / "integrations.oql.planfile.yaml"
    assert integration.is_file()
    assert "repo: semcod/wup" in integration.read_text(encoding="utf-8")

    service = next(item for item in config.services if item.name == "wup-shell")
    for scenario in (
        config.testql.smoke_scenario,
        config.testql.health_scenario,
        service.quick_tests.scenario,
        service.detail_tests.scenario,
    ):
        assert (root / config.testql.scenario_dir / scenario).is_file(), scenario
