"""Tests for simultaneous multi-project watching."""

from __future__ import annotations

import os
from pathlib import Path

from wup.cli import _discover_projects, _resolve_project_paths
from wup.config import detect_watch_paths, get_default_config, load_config
from wup.core import WupWatcher
from wup.models.config import ProjectConfig, WatchConfig, WupConfig
from wup.multi import MultiProjectWatcher


def _make_project(root: Path, name: str, src: str = "src") -> Path:
    """Create a project dir with a wup.yaml and one watchable source folder."""
    proj = root / name
    (proj / src).mkdir(parents=True)
    (proj / src / "main.py").write_text("print('hi')\n")
    (proj / "wup.yaml").write_text(
        f"project:\n  name: {name}\nwatch:\n  paths:\n  - {src}/**\n"
    )
    return proj


def _watcher(project_root: Path, paths: list[str]) -> WupWatcher:
    cfg = WupConfig(
        project=ProjectConfig(name=project_root.name),
        watch=WatchConfig(paths=paths),
    )
    return WupWatcher(
        project_root=str(project_root),
        deps_file=str(project_root / "deps.json"),
        config=cfg,
    )


def test_detect_watch_paths_uses_existing_dirs(tmp_path: Path) -> None:
    (tmp_path / "services").mkdir()
    (tmp_path / "lib").mkdir()
    paths = detect_watch_paths(tmp_path)
    assert "services/**" in paths
    assert "lib/**" in paths
    # A non-existent common dir is not emitted.
    assert "app/**" not in paths


def test_detect_watch_paths_falls_back_when_nothing_matches(tmp_path: Path) -> None:
    assert detect_watch_paths(tmp_path) == ["app/**", "src/**", "routes/**"]


def test_detect_watch_paths_backend_frontend(tmp_path: Path) -> None:
    # c2004-style module layout (backend/ + frontend/, no app/src).
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend").mkdir()
    paths = detect_watch_paths(tmp_path)
    assert "backend/**" in paths and "frontend/**" in paths
    assert "app/**" not in paths


def test_default_config_watches_only_real_dirs(tmp_path: Path) -> None:
    (tmp_path / "services").mkdir()
    cfg = get_default_config(tmp_path)
    assert cfg.watch.paths == ["services/**"]


def test_project_dotenv_is_resolved_without_cross_project_leakage(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.delenv("WUP_BASE_URL", raising=False)
    monkeypatch.delenv("WUPBRO_ENDPOINT", raising=False)
    alpha = _make_project(tmp_path, "alpha")
    beta = _make_project(tmp_path, "beta")
    (alpha / ".wup.env").write_text(
        "WUP_BASE_URL=http://alpha.invalid\nWUPBRO_ENDPOINT=http://alpha-web.invalid\n",
        encoding="utf-8",
    )
    (beta / ".wup.env").write_text(
        "WUP_BASE_URL=http://beta.invalid\nWUPBRO_ENDPOINT=http://beta-web.invalid\n",
        encoding="utf-8",
    )

    alpha_cfg = load_config(alpha)
    beta_cfg = load_config(beta)

    assert alpha_cfg.testql.base_url == "http://alpha.invalid"
    assert beta_cfg.testql.base_url == "http://beta.invalid"
    assert alpha_cfg.web.endpoint == "http://alpha-web.invalid"
    assert beta_cfg.web.endpoint == "http://beta-web.invalid"
    assert "WUP_BASE_URL" not in os.environ
    assert "WUPBRO_ENDPOINT" not in os.environ


def test_discover_finds_subprojects(tmp_path: Path) -> None:
    _make_project(tmp_path, "alpha")
    _make_project(tmp_path, "beta")
    (tmp_path / "not_a_project").mkdir()  # no wup.yaml -> skipped

    discovered = {p.name for p in _discover_projects(tmp_path)}
    assert discovered == {"alpha", "beta"}


def test_discover_skips_vendor_and_hidden(tmp_path: Path) -> None:
    _make_project(tmp_path, "alpha")
    _make_project(tmp_path, "node_modules")  # vendored -> skipped
    _make_project(tmp_path, ".hidden")  # hidden -> skipped

    discovered = {p.name for p in _discover_projects(tmp_path)}
    assert discovered == {"alpha"}


def test_resolve_paths_dedupes(tmp_path: Path) -> None:
    _make_project(tmp_path, "alpha")
    resolved = _resolve_project_paths(
        [str(tmp_path / "alpha"), str(tmp_path / "alpha")], discover=False
    )
    assert len(resolved) == 1


def test_prepare_observer_none_when_no_valid_paths(tmp_path: Path) -> None:
    watcher = _watcher(tmp_path, paths=["does-not-exist/**"])
    assert watcher.prepare_observer() is None


def test_multi_watcher_returns_false_when_all_invalid(tmp_path: Path) -> None:
    w1 = _watcher(tmp_path, paths=["missing-a/**"])
    w2 = _watcher(tmp_path, paths=["missing-b/**"])
    assert MultiProjectWatcher([w1, w2]).start_watching() is False


def test_multi_watcher_starts_observers_for_valid_projects(tmp_path: Path) -> None:
    alpha = _make_project(tmp_path, "alpha")
    beta = _make_project(tmp_path, "beta")
    w1 = _watcher(alpha, paths=["src/**"])
    w2 = _watcher(beta, paths=["src/**"])

    multi = MultiProjectWatcher([w1, w2])
    observers = []
    active = []
    for watcher in multi.watchers:
        watcher.start_background_tasks()
        obs = watcher.prepare_observer()
        if obs is not None:
            observers.append(obs)
            active.append(watcher)

    try:
        assert len(active) == 2
        assert all(obs.is_alive() for obs in observers)
    finally:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()
