# WUP Genericity Audit

_How `wup.yaml` and `deps.json` are generated, where the tool is hardwired to one
specific project, and a path toward a language-agnostic, AI-open design built on
TestQL + OQL + AQL._

Legend: **(a)** hard dependency baked into logic · **(b)** default overridable by
config · **(c)** demo/comment/example only.

---

## 1. How the artifacts are generated

### `wup.yaml` — three inconsistent paths

| Generator | Triggered when | Produces |
| --- | --- | --- |
| `CLIConfigGenerator` (`cli_config_generator.py`) | `pyproject.toml` / `setup.py` / `setup.cfg` present | `file_types:[.py]`, Python entry-points only, `scenario_dir: testql-scenarios` |
| `get_default_config` (`config.py`) | everything else (e.g. a Node monorepo) | watch paths from `detect_watch_paths`, **`services: []`**, no framework, `scenario_dir: scenarios/tests` |
| `generate_wup_config` (`generate.py`, via `wup assistant`) | interactive/NL setup | framework defaults to **`fastapi`**, `file_types:[.py,.yaml,.yml]`, also injects `wup/**` |

The three paths disagree on defaults (`testql-scenarios` vs `scenarios/tests`,
`cli-smoke…` vs `smoke…`), so the config you get depends on which path fired.

### `deps.json` — `DependencyMapper.build_from_codebase`

1. `_detect_framework()` matches signature strings for **only** fastapi / flask /
   django / express, else returns `generic`.
2. `_scan_endpoints()` runs a per-framework regex; `generic` scans nothing.
3. Result is serialized by `to_dict()` and written to `deps.json`.

**Verified failures:**

- **Empty for non-Python projects.** Running the mapper on `subactor/core`
  (Node/TS) yields framework `generic` and `deps.json = {"services": {}, "files": {}}`.
- **JS/TS scanning never worked.** `dependency_mapper.py:158` uses
  `rglob("*.{js,ts,jsx,tsx}")`; pathlib does **not** brace-expand, so this matches
  **0 files** (confirmed empirically). Express discovery is dead code.
- **Fragile `to_dict()`** (`dependency_mapper.py:236`) zips one dict's `keys()`
  with two other dicts' `values()` positionally — correct only while all three
  share an identical key set and insertion order.

---

## 2. Hardcoded, project-specific data

The tool is wired to one project — the **"connect / identification / firmware"
fleet** (maskservice / c2004). Highest-impact leaks (all class **(a)** unless noted):

### `monitoring_manifest.py`
- `:134-150` `_map_docker_to_wup_service` — docker→service mapping keyed on
  literals `firmware`, `frontend`, `backend`, `identification-backend`,
  `connect-scenario`, `connect` (via `-backend` suffix rule).
- `:316-325` a **Polish** `troubleshooting` block with ports `:8100` / `:8202`
  and path `/firmware`, written into **every** generated manifest.

### `testql_monitor.py`
- `:29-39` `_CONNECT_API_PREFIXES` (`/api/id`, `/api/manager`, `/api/scenario`,
  `/api/test`, `/api/template`, `/api/cql`, `/api/v1/data`, `/api/v2/menu`).
- `:40` `_PATH_TOKEN_BLOCKLIST = {"api","app","src","lib","bin","dist","out"}`.
- `:141-149` frontend-proxy rule pinned to port `8100`.
- `:431-432` default URLs `http://localhost:8202` (oqlos), `http://localhost:8096`
  (proxy) — **(b)** overridable.
- `:437-471` hardware-USB catalog with service names `firmware`, `connect-scenario`
  and paths `/api/v1/hardware/identify`, `/api/v3/hardware/peripheral-status/{mid}`.
- `:615-621` probe ranking hardcodes service `firmware` and ports `8202`/`8100`.

### `core.py`
- `:152` service-name inference regex
  `^(connect|backend|frontend|api|app|worker|service)[-_]`.

### `assistant_discovery.py`
- `:10-35` `FRAMEWORK_PATTERNS` — four frameworks with fixed service globs
  (`app/routers/*`, `blueprints/*`, `*/apps.py`, `routes/*`), `default_services`
  (`['web','api']`, `['models','views','tasks']`, …) and characteristic files
  (`main.py`, `wsgi.py`, `manage.py`, `server.js`).

### Directory / naming vocabularies (scattered, inconsistent)
- `config.py:395` `_DEFAULT_SOURCE_DIRS`, `dependency_mapper.py:190-196`
  (`app`/`src`), `testql_discovery.py:106` (`['tests','scenarios','api','views']`),
  `testql_monitor.py:40`.
- Scenario naming `.testql.toon.yaml`, prefix `cli-`, `smoke.testql.toon.yaml` in
  `testql_discovery.py`, `testql_cli_generator.py`, `cli_config_generator.py`.

### Python-only source scanning
- `dependency_mapper.py:86,110` `rglob("*.py")`; `cli_config_generator.py:83`
  `file_types:[.py]`; `cli_scanner.py` reads only `setup.py`/`setup.cfg`/`pyproject.toml`.

### Comments revealing the target project (class **(c)**)
- `models/config.py:73` `# Core API (c2004: http://localhost:8101)`.
- `generate.py:43` leaks the tool's own `wup/**` into generated watch paths.

---

## 3. Toward a generic, AI-open design (TestQL + OQL + AQL)

TestQL is already the generic layer (`testql_discovery` parses scenarios
declaratively). `wup.bus` already provides a CQRS `Query`/`Event`/`Command` bus
and `wup.testing.queries.GetServiceHealth` — a ready foundation for OQL.

| Language | Answers | Today's code |
| --- | --- | --- |
| **TestQL** | "is the behaviour correct?" (scenarios) | already generic |
| **OQL** (Observability QL) | "what is the observed state?" (health/events/probes) | `testql_monitor` + `wup.bus` queries |
| **AQL** (Assertion/Anomaly QL) | "is this change an anomaly?" (assertions on diffs) | `anomaly_detector` heuristics |

**Roadmap (cheapest first):**

1. ✅ **Move the "connect" fleet out of code into config.** Done:
   `testql.docker_service_map` + opt-in `testql.service_map_profile: connect`.
   Default carries no project-specific service names.
2. ✅ **Discovery as pluggable adapters** — done in `wup/discovery.py`: FastAPI,
   Flask, Django, NestJS, Express, Fastify, Hono, Go and OpenAPI adapters selected
   by repo markers. Fixes the empty/Python-only `deps.json`.
3. ✅ **Formalize OQL over `wup.bus`** — done in `wup/oql.py` + `wup oql`:
   declarative queries (`services where status = down`, `events since 5m`) with a
   `RunOQL` bus query.
4. ✅ **AQL = declarative assertions** — done in `wup/aql.py` + `wup aql`:
   assertions about a file's data (`json .services length > 0`,
   `yaml .project.name exists`) that emit `AnomalyResult` violations, with a
   `CheckAQL` bus query. AI can now generate checks instead of reading Python.

### Still hardcoded (follow-up)

- ✅ `testql_monitor.py` probe rejection (`_CONNECT_API_PREFIXES`) is now
  config-driven: generic default rejects nothing; the connect prefixes are a
  built-in profile (`service_map_profile: connect`) or set explicitly via
  `testql.monitoring_reject_prefixes`. This was the one that actively *broke*
  other projects (rejecting their valid `/api/*` health probes).
- ⏳ Lower-harm remainders (only trigger on specific ports/paths, else fall through
  to generic matching): the port `8202`/`8100`→`firmware` assignment and
  hardware-USB service names in `testql_monitor.py`, and `core.py:152`'s
  `^(connect|backend|…)[-_]` service regex. Same treatment (profile/config) applies.

"AI-open" = all three layers declarative (YAML/query) under one schema, so an agent
can read state (OQL), write scenarios (TestQL) and define assertions (AQL) without
knowing WUP's internals.
