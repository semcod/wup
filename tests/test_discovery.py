"""Regression coverage for host memory exhaustion during dependency discovery."""
from pathlib import Path

import pytest

from wup.discovery import SourceIndex, discover_endpoints


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_generated_directories_are_pruned_before_read(tmp_path, monkeypatch):
    import wup.discovery as discovery
    write(tmp_path, "services/api/routes.py", 'from fastapi import FastAPI\napp.get("/real")')
    for directory in SourceIndex.EXCLUDED_DIRS:
        write(tmp_path, f"services/api/{directory}/routes.py", 'app.get("/generated")')
    original = discovery.os.walk
    visited = []

    def walk(*args, **kwargs):
        for row in original(*args, **kwargs):
            visited.append(Path(row[0]).relative_to(tmp_path))
            yield row

    monkeypatch.setattr(discovery.os, "walk", walk)
    assert [p for p, _ in SourceIndex(tmp_path).files((".py",))] == ["services/api/routes.py"]
    assert not any(set(path.parts) & SourceIndex.EXCLUDED_DIRS for path in visited)


def test_cache_overflow_streams_all_sources_on_repeated_scans(tmp_path):
    for i in range(30):
        write(tmp_path, f"api/{i:02}.py", f'from fastapi import FastAPI\n@app.get("/route-{i}")')
    index = SourceIndex(tmp_path)
    index.MAX_CACHE_BYTES = 500
    expected = {f"/route-{i}" for i in range(30)}
    for _ in range(2):
        assert {e.path for e in discover_endpoints(tmp_path, "fastapi", index=index)} == expected
    assert index._cache_bytes <= index.MAX_CACHE_BYTES
    assert ".py" not in index._cache


def test_cache_budget_is_shared_by_extensions(tmp_path):
    for ext in ("py", "js", "ts", "go", "json"):
        write(tmp_path, f"app.{ext}", "x" * 400)
    index = SourceIndex(tmp_path)
    index.MAX_CACHE_BYTES = 1000
    assert len(list(index.files((".py", ".js", ".ts", ".go", ".json")))) == 5
    assert index._cache_bytes <= 1000
    assert len(index._cache) < 5


def test_oversized_source_warns_and_does_not_hide_other_sources(tmp_path):
    write(tmp_path, "large.py", "x" * 101)
    write(tmp_path, "small.py", "x" * 100)
    index = SourceIndex(tmp_path)
    index.MAX_FILE_BYTES = 100
    with pytest.warns(RuntimeWarning, match="coverage may be incomplete"):
        assert [p for p, _ in index.files((".py",))] == ["small.py"]


def test_symlinked_files_and_trees_are_not_followed(tmp_path):
    outside = tmp_path / "outside"
    project = tmp_path / "project"
    project.mkdir()
    source = write(outside, "api.py", 'app.get("/outside")')
    (project / "linked.py").symlink_to(source)
    (project / "linked-dir").symlink_to(outside, target_is_directory=True)
    assert list(SourceIndex(project).files((".py",))) == []


def test_short_circuit_detection_does_not_cache_partial_extension(tmp_path):
    write(tmp_path, "a.py", "marker")
    write(tmp_path, "b.py", "last")
    index = SourceIndex(tmp_path)
    assert index.contains("marker", (".py",))
    assert ".py" not in index._cache
    assert len(list(index.files((".py",)))) == 2


def test_invalid_utf8_and_special_files_do_not_block_sources(tmp_path):
    import os
    write(tmp_path, "valid.py", "ok")
    (tmp_path / "invalid.py").write_bytes(b"\xff")
    os.mkfifo(tmp_path / "pipe.py")
    assert list(SourceIndex(tmp_path).files((".py",))) == [("valid.py", "ok")]
