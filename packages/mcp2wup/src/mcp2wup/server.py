"""FastMCP server exposing WUP control tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _require_fastmcp():
    try:
        from mcp.server.fastmcp import FastMCP
        return FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP support requires optional dependency 'mcp'. Install with: pip install mcp",
        ) from exc


@dataclass
class WupMCPServer:
    name: str = "wup"

    def __post_init__(self) -> None:
        FastMCP = _require_fastmcp()
        self.app = FastMCP(self.name)
        self._register_tools()

    def _register_tools(self) -> None:
        from dsl2wup import dispatch, execute_dsl, execute_dsl_line
        from dsl2wup.pb_codec import encode_result_protobuf
        from nlp2wup.apply import apply_nl, to_dsl
        from uri2wup.nlp2uri import nlp2uri
        from uri2wup.patch import patch_uri
        from uri2wup.query import query_uri

        @self.app.tool()
        def wup_query(uri: str, file: str = "", fmt: str = "json", project: str = ".") -> dict[str, Any]:
            result = query_uri(uri, file=file or None, fmt=fmt, project=project)
            return result.to_dict()

        @self.app.tool()
        def wup_validate(path: str = "wup.yaml", project: str = ".") -> dict[str, Any]:
            return dispatch(f"VALIDATE {path} PROJECT {project}").to_dict()

        @self.app.tool()
        def wup_health(project: str = ".", service: str = "") -> dict[str, Any]:
            line = f"HEALTH {service} PROJECT {project}".strip() if service else f"HEALTH PROJECT {project}"
            return dispatch(line).to_dict()

        @self.app.tool()
        def wup_status(
            project: str = ".",
            deps_file: str = "deps.json",
            delta_seconds: int = 0,
            failed_only: bool = False,
        ) -> dict[str, Any]:
            line = f"STATUS PROJECT {project} DEPS {deps_file}"
            if delta_seconds:
                line += f" DELTA {delta_seconds}"
            if failed_only:
                line += " FAILED_ONLY"
            return dispatch(line).to_dict()

        @self.app.tool()
        def wup_map(project: str = ".", out: str = "deps.json", framework: str = "auto") -> dict[str, Any]:
            return dispatch(f"MAP {project} OUT {out} FRAMEWORK {framework}").to_dict()

        @self.app.tool()
        def wup_sync(project: str = ".", file: str = "wup.yaml", merge_endpoints: bool = False) -> dict[str, Any]:
            line = f"SYNC {project} FILE {file}"
            if merge_endpoints:
                line += " MERGE"
            return dispatch(line).to_dict()

        @self.app.tool()
        def wup_generate(
            hint: str,
            project: str = ".",
            out: str = "wup.yaml",
            template: str = "",
        ) -> dict[str, Any]:
            line = f'GENERATE "{hint}" OUT {out} PROJECT {project}'
            if template:
                line += f" TEMPLATE {template}"
            return dispatch(line).to_dict()

        @self.app.tool()
        def wup_endpoints(
            scenarios_dir: str,
            out: str = "testql-deps.json",
            testql_bin: str = "testql",
        ) -> dict[str, Any]:
            return dispatch(f"ENDPOINTS {scenarios_dir} OUT {out} TESTQL_BIN {testql_bin}").to_dict()

        @self.app.tool()
        def wup_init_cli(
            project: str = ".",
            out: str = "wup.yaml",
            scenarios: str = "testql-scenarios",
            merge: bool = False,
        ) -> dict[str, Any]:
            line = f"INIT_CLI {project} OUT {out} SCENARIOS {scenarios}"
            if merge:
                line += " MERGE"
            return dispatch(line).to_dict()

        @self.app.tool()
        def wup_run_dsl(script: str, default_file: str = "") -> list[dict[str, Any]]:
            results = execute_dsl(script, default_file=default_file or None)
            return [r.to_dict() for r in results]

        @self.app.tool()
        def wup_run_command(command: str, default_file: str = "") -> dict[str, Any]:
            return execute_dsl_line(command, default_file=default_file or None).to_dict()

        @self.app.tool()
        def wup_run_command_pb(envelope_bytes: bytes, default_file: str = "") -> bytes:
            return encode_result_protobuf(dispatch(envelope_bytes, default_file=default_file or None))

        @self.app.tool()
        def wup_to_dsl(prompt: str, file: str = "", project: str = ".") -> str:
            return to_dsl(prompt, file=file or None, project=project)

        @self.app.tool()
        def wup_resolve(prompt: str, file: str = "", project: str = ".") -> list[dict[str, Any]]:
            return [hit.to_dict() for hit in nlp2uri(prompt, file=file or None, project=project)]

        @self.app.tool()
        def wup_patch(uri: str, content: str, file: str = "", project: str = ".") -> dict[str, Any]:
            return patch_uri(uri, content=content, file=file or None, project=project).to_dict()

        @self.app.tool()
        def wup_apply_nl(prompt: str, file: str = "", project: str = ".") -> dict[str, Any]:
            return apply_nl(prompt, file=file or None, project=project).to_dict()

    def run(self) -> None:
        self.app.run()


def create_server(name: str = "wup") -> WupMCPServer:
    return WupMCPServer(name=name)


def run_server() -> None:
    create_server().run()


if __name__ == "__main__":
    run_server()
