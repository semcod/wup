"""Runtime GENERATE via bus."""

from __future__ import annotations

from pathlib import Path

from dsl2wup import dispatch


def test_generate_fastapi_via_dsl(tmp_path: Path) -> None:
    result = dispatch(
        f'GENERATE "fastapi CRM" OUT wup.yaml PROJECT {tmp_path}',
        default_file=str(tmp_path / "app.doql.less"),
    )
    assert result.ok
    assert (tmp_path / "wup.yaml").exists()
    assert result.data.get("framework") == "fastapi"
