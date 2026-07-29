# WUP (What's Up)

WUP (What's Up) - Intelligent file watcher for regression testing in large projects

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `wup`
- **version**: `0.2.77`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, testql(4), app.doql.less, goal.yaml, .env.example, src(39 mod), project/(3 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: wup;
  version: 0.2.77;
}

dependencies {
  runtime: "watchdog>=4.0.0, psutil>=5.9.0, rich>=13.0.0, typer>=0.9.0, pyyaml>=6.0";
  dev: "pytest>=7.0.0, pytest-cov>=5.0, ruff>=0.8, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60, uri2wup, dsl2wup, nlp2wup, cli2wup, mcp2wup, rest2wup, httpx>=0.27";
  visual: "playwright>=1.40,<2";
  control: "dsl2wup>=0.1.0, uri2wup>=0.1.0";
}

entity[name="AdoptCommand"] {
  verb: Literal[!;
  root: string!;
  out: string;
}

entity[name="EndpointsCommand"] {
  verb: Literal[!;
  scenarios_dir: string!;
  out: string!;
  testql_bin: string!;
}

entity[name="GenerateCommand"] {
  verb: Literal[!;
  text: string;
  out: string;
  project: string;
  template: Optional[Literal[;
}

entity[name="HealthCommand"] {
  verb: Literal[!;
  service: string;
  project: string;
}

entity[name="InitCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
}

entity[name="InitCliCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
  scenarios: string!;
  merge: bool!;
  infer_args: bool!;
}

entity[name="MapCommand"] {
  verb: Literal[!;
  project: string!;
  out: string!;
  framework: string!;
}

entity[name="PatchCommand"] {
  verb: Literal[!;
  target: string!;
  with_path: string!;
  file: string;
  project: string;
}

entity[name="QueryCommand"] {
  verb: Literal[!;
  target: string!;
  file: string;
  format: Literal[!;
  project: string;
}

entity[name="ResolveCommand"] {
  verb: Literal[!;
  text: string!;
  file: string;
  project: string;
}

entity[name="StatusCommand"] {
  verb: Literal[!;
  project: string!;
  deps_file: string!;
  file: string;
  delta_seconds: int!;
  failed_only: bool!;
}

entity[name="SyncCommand"] {
  verb: Literal[!;
  project: string!;
  file: string;
  merge_endpoints: bool!;
}

entity[name="ValidateCommand"] {
  verb: Literal[!;
  path: string;
  project: string;
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="wup"] {
  entry: wup.bootstrap:main;
}

interface[type="web"] {
  type: spa;
  framework: static;
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing WUP...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e .; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e .; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Installation completed!";
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Installing WUP with dev dependencies...";
  step-2: run cmd=if command -v uv > /dev/null 2>&1; then \;
  step-3: run cmd=uv pip install -e ".[dev]"; \;
  step-4: run cmd=else \;
  step-5: run cmd=pip install -e ".[dev]"; \;
  step-6: run cmd=fi;
  step-7: run cmd=echo "✅ Dev installation completed!";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ packages/ -v --tb=short;
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=echo "🧪 Running tests with coverage...";
  step-2: run cmd=.venv/bin/python -m pytest tests/ packages/ -v --cov=wup --cov-report=term-missing --cov-report=json;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=echo "🔍 Running linting with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff check wup/;
  step-3: run cmd=.venv/bin/python -m ruff check tests/;
  step-4: run cmd=.venv/bin/python -m ruff check packages/;
}

workflow[name="format"] {
  trigger: manual;
  step-1: run cmd=echo "📝 Formatting code with ruff...";
  step-2: run cmd=.venv/bin/python -m ruff format wup/;
  step-3: run cmd=.venv/bin/python -m ruff format tests/;
  step-4: run cmd=.venv/bin/python -m ruff format packages/;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=echo "🧹 Cleaning temporary files...";
  step-2: run cmd=find . -type f -name "*.pyc" -delete;
  step-3: run cmd=find . -type d -name "__pycache__" -delete;
  step-4: run cmd=find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true;
  step-5: run cmd=rm -rf build/ dist/ .coverage htmlcov/ coverage.json;
  step-6: run cmd=echo "✅ Clean completed!";
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Building release artifacts (no upload)...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine check dist/*;
  step-6: run cmd=echo "✅ Release artifacts are valid. Run 'make publish-confirm' to upload.";
}

workflow[name="publish-confirm"] {
  trigger: manual;
  step-1: run cmd=echo "⚡ Uploading release artifacts to PyPI...";
  step-2: run cmd=.venv/bin/twine upload dist/*;
}

workflow[name="publish-test"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Publishing to TestPyPI...";
  step-2: run cmd=command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build);
  step-3: run cmd=rm -rf dist/ build/ *.egg-info/;
  step-4: run cmd=.venv/bin/python -m build;
  step-5: run cmd=.venv/bin/twine upload --repository testpypi dist/*;
}

workflow[name="version"] {
  trigger: manual;
  step-1: run cmd=echo "📦 Version information...";
  step-2: run cmd=cat VERSION;
  step-3: run cmd=.venv/bin/python -c "from importlib.metadata import version; print(f'Installed version: {version(\"wup\")}')";
}

workflow[name="wup:watch"] {
  trigger: manual;
  step-1: run cmd=poetry run wup watch;
}

workflow[name="wup:status"] {
  trigger: manual;
  step-1: run cmd=poetry run wup status;
}

workflow[name="wup:sync"] {
  trigger: manual;
  step-1: run cmd=poetry run wup sync-testql . --write;
}

workflow[name="wup:endpoints"] {
  trigger: manual;
  step-1: run cmd=poetry run wup testql-endpoints;
}

workflow[name="wup:map"] {
  trigger: manual;
  step-1: run cmd=poetry run wup map-deps;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_MODEL, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

### Source Modules

- `wup._ast_detector`
- `wup._base_detector`
- `wup._hash_detector`
- `wup._yaml_detector`
- `wup.anomaly_detector`
- `wup.anomaly_models`
- `wup.aql`
- `wup.assistant`
- `wup.assistant_discovery`
- `wup.assistant_validator`
- `wup.bootstrap`
- `wup.bus`
- `wup.cli`
- `wup.cli_bridge`
- `wup.cli_config_generator`
- `wup.cli_scanner`
- `wup.config`
- `wup.control`
- `wup.core`
- `wup.dependency_mapper`
- `wup.discovery`
- `wup.endpoints`
- `wup.event_store`
- `wup.generate`
- `wup.init_cli`
- `wup.monitoring_manifest`
- `wup.multi`
- `wup.oql`
- `wup.paths`
- `wup.planfile_reporter`
- `wup.status_data`
- `wup.sync`
- `wup.testql_cli_generator`
- `wup.testql_discovery`
- `wup.testql_monitor`
- `wup.testql_watcher`
- `wup.validate`
- `wup.visual_diff`
- `wup.web_client`

## Interfaces

### CLI Entry Points

- `wup`

### testql Scenarios

#### `testql-scenarios/cli-smoke.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/cli-smoke.testql.toon.yaml
# SCENARIO: CLI Smoke Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, wup
  timeout_ms, 15000


# Test: wup --help
SHELL "wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "Usage"

# Test: wup --version
SHELL "wup version" 5000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/cli-wup.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/cli-wup.testql.toon.yaml
# SCENARIO: wup Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, wup
  timeout_ms, 30000

# Test 1: wup --help
SHELL "wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "Usage"

# Test 2: wup --version
SHELL "wup version" 5000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m wup
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m wup --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "Usage"

# Test 2: CLI version command
SHELL "python -m wup version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m wup --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 72 assertions from pytest
ASSERT[72]{field, operator, expected}:
  len(watcher.test_queue), ==, 1
  test_type, ==, "quick"
  service_name, ==, "users"
  len(endpoints), ==, 3  # Limited by quick_tests.max_endpoints
  len(watcher.changed_services), ==, 1
  inferred1, ==, "users-shell"
  inferred2, ==, "payments"
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  watcher.config.project.name, ==, "test"
  len(watcher.config.watch.paths), ==, 1
  watcher.debounce_seconds, ==, 5
  len(paths), ==, 2
  inferred, ==, "users"
  svc_config.name, ==, "users"
  svc_config.quick_tests.max_endpoints, ==, 5
  len(endpoints), ==, 5  # Config limit
  len(watcher.changed_services), ==, 0
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, !=, 0
  result.returncode, !=, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  len(watcher.test_queue), ==, 1
  test_type, ==, "quick"
  service_name, ==, "users"
  len(endpoints), ==, 3  # Limited by quick_tests.max_endpoints
  len(watcher.changed_services), ==, 1
  inferred1, ==, "users-shell"
  inferred2, ==, "payments"
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  watcher.config.project.name, ==, "test"
  len(watcher.config.watch.paths), ==, 1
  watcher.debounce_seconds, ==, 5
  len(paths), ==, 2
  inferred, ==, "users"
  svc_config.name, ==, "users"
  svc_config.quick_tests.max_endpoints, ==, 5
  len(endpoints), ==, 5  # Config limit
  len(watcher.changed_services), ==, 0
  config.type, ==, "http+file"
  config.url, ==, "http://localhost:8001"
  config.file, ==, "notify.json"
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, !=, 0
  result.returncode, !=, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
  result.returncode, ==, 0
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: '3'

tasks:
  wup:watch:
    desc: "Watch project for file changes and run WUP regression tests"
    cmds:
      - poetry run wup watch

  wup:status:
    desc: "Show dependency map status and configuration"
    cmds:
      - poetry run wup status

  wup:sync:
    desc: "Discover monitoring targets and update wup.yaml manifest"
    cmds:
      - poetry run wup sync-testql . --write

  wup:endpoints:
    desc: "Verify TestQL scenarios and discover endpoints"
    cmds:
      - poetry run wup testql-endpoints

  wup:map:
    desc: "Build dependency map from codebase"
    cmds:
      - poetry run wup map-deps

  test:
    desc: "Run WUP pytest test suite"
    cmds:
      - poetry run pytest
```

## Configuration

```yaml
project:
  name: wup
  version: 0.2.77
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
watchdog>=4.0.0
psutil>=5.9.0
rich>=13.0.0
typer>=0.9.0
pyyaml>=6.0
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0.0
pytest-cov>=5.0
ruff>=0.8
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
uri2wup
dsl2wup
nlp2wup
cli2wup
mcp2wup
rest2wup
httpx>=0.27
```

## Deployment

```bash markpact:run
pip install wup

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3.7-plus` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`wup`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `wup/__init__.py:__version__`

## Makefile Targets

- `help` — Default target
- `install` — Installation
- `install-dev`
- `test` — Testing
- `test-cov`
- `lint` — Code quality
- `format`
- `clean` — Utilities
- `publish` — Release helpers
- `publish-confirm`
- `publish-test`
- `version`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# wup | 159f 21216L | json:16,yaml:12,txt:12,python:102,yml:2,shell:3,toml:7,proto:2 | 2026-07-29
# generated in 0.02s
# stats: 651 func | 0 cls | 159 mod | CC̄=4.2 | critical:0 | cycles:0
# alerts[5]: fan-out create_app=26; fan-out EventStore.append=22; fan-out oql=21; fan-out TestQLWatcher._run_fleet_health_scenario=19; fan-out map_deps=19
# hotspots[5]: create_app fan=26; EventStore.append fan=22; oql fan=21; map_deps fan=19; status fan=19
# evolution: CC̄ 5.0→4.2 (improved -0.8)
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[159]:
  Makefile,101
  Taskfile.yml,32
  deps.json,4
  duplication.json,3481
  examples/c2004_monorepo_demo.py,258
  examples/ci_cd_integration.py,339
  examples/fastapi-app/app/users/routes.py,38
  examples/fastapi-app/main.py,16
  examples/fastapi-app/requirements.txt,3
  examples/fastapi-app/wup.yaml,28
  examples/flask-app/Dockerfile,26
  examples/flask-app/app/__init__.py,0
  examples/flask-app/app/auth/routes.py,33
  examples/flask-app/main.py,20
  examples/flask-app/requirements.txt,1
  examples/flask-app/wup.yaml,28
  examples/multi-service/auth-service/app/auth/routes.py,13
  examples/multi-service/auth-service/main.py,20
  examples/multi-service/auth-service/wup.yaml,21
  examples/multi-service/docker-compose.yml,33
  examples/multi-service/payments-service/Dockerfile,26
  examples/multi-service/payments-service/app/payments/routes.py,18
  examples/multi-service/payments-service/main.py,16
  examples/multi-service/payments-service/requirements.txt,2
  examples/multi-service/payments-service/wup.yaml,21
  examples/multi-service/users-service/app/users/routes.py,18
  examples/multi-service/users-service/main.py,16
  examples/multi-service/users-service/wup.yaml,21
  examples/testql_demo.py,191
  examples/testql_integration.py,286
  examples/visual_diff_demo.py,305
  examples/webhook_notifications.py,375
  goal.yaml,528
  koru.yaml,133
  local.dev.txt,17
  packages/cli2wup/local.dev.txt,9
  packages/cli2wup/pyproject.toml,26
  packages/cli2wup/src/cli2wup/__init__.py,1
  packages/cli2wup/src/cli2wup/cli.py,100
  packages/dsl2wup/local.dev.txt,10
  packages/dsl2wup/proto/dsl2wup/v1/command.proto,104
  packages/dsl2wup/proto/dsl2wup/v1/result.proto,23
  packages/dsl2wup/pyproject.toml,34
  packages/dsl2wup/scripts/generate-proto.sh,7
  packages/dsl2wup/src/dsl2wup/__init__.py,6
  packages/dsl2wup/src/dsl2wup/bus.py,79
  packages/dsl2wup/src/dsl2wup/cli.py,108
  packages/dsl2wup/src/dsl2wup/codec.py,35
  packages/dsl2wup/src/dsl2wup/codegen.py,70
  packages/dsl2wup/src/dsl2wup/engine.py,8
  packages/dsl2wup/src/dsl2wup/events.py,116
  packages/dsl2wup/src/dsl2wup/grammar.py,153
  packages/dsl2wup/src/dsl2wup/handlers/command.py,271
  packages/dsl2wup/src/dsl2wup/handlers/query.py,137
  packages/dsl2wup/src/dsl2wup/models.py,129
  packages/dsl2wup/src/dsl2wup/pb_codec.py,147
  packages/dsl2wup/src/dsl2wup/result.py,28
  packages/dsl2wup/src/dsl2wup/schema/commands/adopt.schema.json,11
  packages/dsl2wup/src/dsl2wup/schema/commands/endpoints.schema.json,12
  packages/dsl2wup/src/dsl2wup/schema/commands/generate.schema.json,13
  packages/dsl2wup/src/dsl2wup/schema/commands/health.schema.json,11
  packages/dsl2wup/src/dsl2wup/schema/commands/init.schema.json,11
  packages/dsl2wup/src/dsl2wup/schema/commands/init_cli.schema.json,14
  packages/dsl2wup/src/dsl2wup/schema/commands/map.schema.json,12
  packages/dsl2wup/src/dsl2wup/schema/commands/patch.schema.json,13
  packages/dsl2wup/src/dsl2wup/schema/commands/query.schema.json,13
  packages/dsl2wup/src/dsl2wup/schema/commands/resolve.schema.json,12
  packages/dsl2wup/src/dsl2wup/schema/commands/status.schema.json,14
  packages/dsl2wup/src/dsl2wup/schema/commands/sync.schema.json,12
  packages/dsl2wup/src/dsl2wup/schema/commands/validate.schema.json,11
  packages/dsl2wup/src/dsl2wup/schema_registry.py,84
  packages/dsl2wup/src/dsl2wup/v1/command_pb2.py,62
  packages/dsl2wup/src/dsl2wup/v1/result_pb2.py,39
  packages/install-dev.sh,24
  packages/mcp2wup/local.dev.txt,11
  packages/mcp2wup/pyproject.toml,29
  packages/mcp2wup/src/mcp2wup/__init__.py,5
  packages/mcp2wup/src/mcp2wup/cli.py,24
  packages/mcp2wup/src/mcp2wup/server.py,149
  packages/nlp2wup/local.dev.txt,10
  packages/nlp2wup/pyproject.toml,27
  packages/nlp2wup/src/nlp2wup/__init__.py,7
  packages/nlp2wup/src/nlp2wup/apply.py,167
  packages/nlp2wup/src/nlp2wup/cli.py,43
  packages/nlp2wup/src/nlp2wup/generate.py,24
  packages/nlp2wup/src/nlp2wup/validate.py,11
  packages/rest2wup/local.dev.txt,9
  packages/rest2wup/pyproject.toml,28
  packages/rest2wup/src/rest2wup/__init__.py,5
  packages/rest2wup/src/rest2wup/app.py,68
  packages/rest2wup/src/rest2wup/cli.py,28
  packages/uri2wup/local.dev.txt,9
  packages/uri2wup/pyproject.toml,27
  packages/uri2wup/src/uri2wup/__init__.py,7
  packages/uri2wup/src/uri2wup/cli.py,72
  packages/uri2wup/src/uri2wup/decode.py,61
  packages/uri2wup/src/uri2wup/nlp2uri.py,48
  packages/uri2wup/src/uri2wup/patch.py,91
  packages/uri2wup/src/uri2wup/query.py,147
  packages/uri2wup/src/uri2wup/uri.py,92
  project.sh,49
  pyproject.toml,143
  regix.yaml,51
  scripts/run_probe_smoke.py,88
  testql-deps.json,311
  testql-scenarios/cli-smoke.testql.toon.yaml,17
  testql-scenarios/cli-wup.testql.toon.yaml,16
  testql-scenarios/generated-cli-tests.testql.toon.yaml,20
  testql-scenarios/generated-from-pytests.testql.toon.yaml,82
  todo.txt,12
  tree.txt,337
  wup/__init__.py,46
  wup/_ast_detector.py,124
  wup/_base_detector.py,18
  wup/_hash_detector.py,72
  wup/_yaml_detector.py,128
  wup/anomaly_detector.py,175
  wup/anomaly_models.py,35
  wup/aql.py,308
  wup/assistant.py,584
  wup/assistant_discovery.py,99
  wup/assistant_validator.py,57
  wup/bootstrap.py,61
  wup/bus.py,65
  wup/cli.py,1079
  wup/cli_bridge.py,194
  wup/cli_config_generator.py,223
  wup/cli_scanner.py,301
  wup/config.py,584
  wup/control.py,127
  wup/core.py,740
  wup/dependency_mapper.py,177
  wup/discovery.py,279
  wup/endpoints.py,44
  wup/event_store.py,41
  wup/file_watcher/events/file_events.py,10
  wup/generate.py,62
  wup/init_cli.py,60
  wup/models/__init__.py,36
  wup/models/config.py,206
  wup/models/target.py,23
  wup/monitoring_manifest.py,478
  wup/multi.py,81
  wup/oql.py,267
  wup/paths.py,16
  wup/planfile_reporter.py,267
  wup/status_data.py,114
  wup/sync.py,70
  wup/testing/events/health_events.py,11
  wup/testing/handlers/event_handlers.py,55
  wup/testing/handlers/health_handlers.py,123
  wup/testing/queries/health_queries.py,7
  wup/testql_cli_generator.py,215
  wup/testql_discovery.py,229
  wup/testql_monitor.py,693
  wup/testql_watcher.py,1013
  wup/validate.py,34
  wup/visual_diff.py,638
  wup/web_client.py,185
D:
  wup/monitoring_manifest.py:
    e: DockerComposeService,_parse_port_mapping,_load_compose_yaml,_extract_healthcheck_test,_extract_service_from_spec,discover_docker_compose_services,_host_port_from_mapping,_connect_profile_rules,_map_docker_to_wup_service,_probe_row,_build_wup_service_dicts,_build_docker_rows,_build_scenario_rows,_artifact_row,_semcod_tool_row,discover_semcod_tools,build_monitoring_manifest,manifest_to_yaml_block,patch_wup_yaml_monitoring,load_monitoring_manifest_from_yaml,_service_summary_lines,_semcod_summary_lines,format_manifest_summary
    DockerComposeService:
    _parse_port_mapping(raw)
    _load_compose_yaml(compose_path)
    _extract_healthcheck_test(spec)
    _extract_service_from_spec(name;spec;source_file)
    discover_docker_compose_services(project_root)
    _host_port_from_mapping(mapping)
    _connect_profile_rules(name;container;wup_services)
    _map_docker_to_wup_service(docker;wup_services)
    _probe_row(probe)
    _build_wup_service_dicts(config)
    _build_docker_rows(docker_all;wup_names;by_wup)
    _build_scenario_rows(monitor;project_root;wup_names;by_wup)
    _artifact_row(repo_path;artifact)
    _semcod_tool_row(name;tool)
    discover_semcod_tools(config)
    build_monitoring_manifest(project_root;config)
    manifest_to_yaml_block(manifest)
    patch_wup_yaml_monitoring(config_path;manifest)
    load_monitoring_manifest_from_yaml(config_path)
    _service_summary_lines(svc;info)
    _semcod_summary_lines(semcod)
    format_manifest_summary(manifest)
  wup/oql.py:
    e: OQLError,Condition,OQLQuery,OQLEngine,RunOQL,_coerce_number,_compare,_parse_duration,_tokenize,parse,_parse_conditions,register_oql
    OQLError(ValueError):  # Raised for malformed OQL queries...
    Condition: matches(1)
    OQLQuery:
    OQLEngine: __init__(1),_service_rows(0),_event_rows(0),execute(1)  # Executes OQL queries against a project's observed state...
    RunOQL(Query):  # Query message: run an OQL string over observed state via the...
    _coerce_number(value)
    _compare(actual;op;expected)
    _parse_duration(token)
    _tokenize(query)
    parse(query)
    _parse_conditions(tokens;start;parsed)
    register_oql(bus;project_root)
  wup/planfile_reporter.py:
    e: PlanfileReporter
    PlanfileReporter: __init__(3),report_failure(0),_ticket_is_closed(1),clear_service_stage(0),_build_ticket_cmd(3),_run_planfile(1),_retry_without_files(1),_create_ticket(0),_wait_for_planfile_store_ready(1),_load_dedupe(0),_save_dedupe(1),_fingerprint(-1),_parse_ticket_id(0),_files_option_unsupported(0),_ticket_name(-1),_ticket_description(-1)  # Create deduplicated planfile tickets for WUP-detected failur...
  wup/cli.py:
    e: _load_watch_config,_print_watch_header,_refresh_monitoring_manifest,_create_watcher,_is_project_dir,_discover_projects,_resolve_project_paths,_build_project_watcher,watch,_auto_generate_config,map_deps,_add_failing_services_lines,_add_delta_events_lines,_add_monitoring_manifest_lines,_add_visual_diff_lines,_build_status_panel,status,oql,aql,init,testql_endpoints,sync_testql,assistant,version,init_cli
    _load_watch_config(project_path;config_path;probe_interval;mode)
    _print_watch_header(wup_config;cpu_throttle;debounce;cooldown;config_path)
    _refresh_monitoring_manifest(project_path;wup_config;cfg_path)
    _create_watcher(mode;project_path;deps_file;cpu_throttle;debounce;cooldown;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;config)
    _is_project_dir(path)
    _discover_projects(root)
    _resolve_project_paths(projects;discover)
    _build_project_watcher(project_path;config_path)
    watch(projects;deps_file;cpu_throttle;debounce;cooldown;dashboard;mode;scenarios_dir;testql_bin;browser_service_url;track_dir;quick_limit;probe_interval;discover;config)
    _auto_generate_config(project_path;mode)
    map_deps(project;output;framework;config)
    _add_failing_services_lines(lines;health_state_path;failed_only;watch)
    _add_delta_events_lines(lines;health_events_path;delta_seconds;watch;ts)
    _add_monitoring_manifest_lines(lines;config_path;project_path)
    _add_visual_diff_lines(lines;wup_config;project_path;delta_seconds;watch)
    _build_status_panel(ts;project_path;wup_config;config_path;health_state_path;health_events_path;delta_seconds;failed_only;watch)
    status(deps_file;config;delta_seconds;failed_only;watch;interval;json_out)
    oql(query;project;json_out)
    aql(file;rule;json_out)
    init(project;output)
    testql_endpoints(scenarios_dir;output;testql_bin)
    sync_testql(project;write;merge_endpoints;config)
    assistant(quick;template;project)
    version()
    init_cli(project;output_config;output_scenarios;merge;infer_args)
  wup/assistant.py:
    e: WupAssistant,main
    WupAssistant: __init__(1),_dispatch_menu_choice(2),run(2),_init_project(1),_detect_framework(0),_auto_detect_services(1),_detect_service_type(2),_configure_services(0),_add_service_interactive(0),_edit_service(1),_setup_watch(0),_configure_testql(0),_setup_web_dashboard(0),_setup_visual_diff(0),_setup_anomaly_detection(0),_review_and_validate(0),_validate_config(0),_generate_suggestions(0),_save_configuration(0),_save_draft(0),_load_draft(0),_config_to_dict(1),_quick_setup(1)  # Interactive configuration assistant...
    main()
  wup/aql.py:
    e: AQLError,AQLRule,AQLEngine,CheckAQL,_resolve_path,_split_severity,_tokenize,_rule_selector,_predicate_rule,parse_rule,_coerce_number,_compare,_length_of,_type_name,_passes,register_aql
    AQLError(ValueError):  # Raised for malformed AQL rules...
    AQLRule:
    AQLEngine: __init__(1),_load(1),check_file(2)  # Evaluates AQL rules against a file's data, producing Anomaly...
    CheckAQL(Query):  # Query message: evaluate AQL rules against a file via the eve...
    _resolve_path(data;path)
    _split_severity(tokens)
    _tokenize(rule)
    _rule_selector(tokens)
    _predicate_rule(selector;path;keyword;tokens;severity;raw)
    parse_rule(rule)
    _coerce_number(value)
    _compare(actual;op;expected)
    _length_of(value)
    _type_name(value)
    _passes(rule;value)
    register_aql(bus;project_root)
  packages/dsl2wup/src/dsl2wup/schema_registry.py:
    e: _load_schemas,schema_for_verb,all_schemas,validate_command_dict,_schema_verb_for,validate_schema_registry
    _load_schemas()
    schema_for_verb(verb)
    all_schemas()
    validate_command_dict(cmd)
    _schema_verb_for(verb)
    validate_schema_registry()
  wup/testql_monitor.py:
    e: ProbeTarget,_ProbeAccumulator,TestQLMonitor,reject_prefixes_for_config,_parse_api_lines,_parse_shell_curl_lines,parse_scenario_probes,_extract_base_url,_parse_endpoint_row,parse_service_map_probes,is_monitoring_probe,_service_path_patterns,_find_service_by_name,_find_service_by_token,_assign_by_port_8101,_assign_by_port_8202,_assign_by_port_8100,_assign_by_connect_backend,_assign_http_probe,_assign_by_longest_token,_assign_by_path_prefix,assign_probe_to_service
    ProbeTarget: probe(1)  # Single HTTP probe derived from TestQL scenarios or service m...
    _ProbeAccumulator: __init__(1),add(2)  # Deduplicated probe collector for discover_probes_by_service...
    TestQLMonitor: __init__(2),_is_monitoring_probe(1),_load_dot_env(0),_build_port_map(0),_service_map_paths(0),_add_hardware_usb_module_endpoints(1),_add_config_endpoints(1),_add_scenario_probes(2),_add_service_map_probes(2),discover_probes_by_service(0),_resolve_base_url_for_service(1),_probeable_url(2),probes_for_service(2),_sort_probes_for_live(1),run_probes(2),suggested_endpoints_by_service(0),_resolve_base_url(0),_join_base(1)  # Build and run live probes from TestQL scenarios + WUP config...
    reject_prefixes_for_config(config)
    _parse_api_lines(content;source)
    _parse_shell_curl_lines(content;source)
    parse_scenario_probes(scenario_path)
    _extract_base_url(data)
    _parse_endpoint_row(row;base_url;source)
    parse_service_map_probes(map_path)
    is_monitoring_probe(probe;reject_prefixes)
    _service_path_patterns(services)
    _find_service_by_name(services;name)
    _find_service_by_token(services;token)
    _assign_by_port_8101(services)
    _assign_by_port_8202(services)
    _assign_by_port_8100(services;path_lower)
    _assign_by_connect_backend(services;path_lower)
    _assign_http_probe(probe;services;path_lower;port_map)
    _assign_by_longest_token(path_lower;services)
    _assign_by_path_prefix(path_lower;services)
    assign_probe_to_service(probe;services;port_map)
  packages/uri2wup/src/uri2wup/query.py:
    e: QueryResult,_resolve_config_path,_extract_block,_runtime_block,_success,query_uri
    QueryResult: to_dict(0)
    _resolve_config_path(project;file_param)
    _extract_block(raw;parts)
    _runtime_block(parts;project)
    _success(uri;parts;data;output_fmt;file)
    query_uri(uri)
  wup/testql_watcher.py:
    e: BrowserNotifier,TestQLWatcher
    BrowserNotifier: __init__(2),notify(1)  # Send watcher events to browser-facing service and local file...
    TestQLWatcher(WupWatcher): __init__(7),_normalize_fleet_health_entry(0),_load_service_health(0),_record_health_transition(0),_tokenize_service(1),_get_config_endpoints_for_service(1),_to_full_url_for_service(2),_resolve_base_url_for_service(1),_resolve_base_url(0),_to_full_url(1),_discover_scenarios(0),get_service_config(1),_score_scenario(2),_get_scored_scenarios(3),_get_smoke_fallback(1),_resolve_scenario_path(1),_testql_trailing_json_ok(0),_health_summary_all_passed(0),_resolve_stage_config(2),_filter_connect_scenario(0),_select_scenarios_for_service(1),_filter_scenarios_by_type(2),_scenario_matches_type(2),_run_testql(2),_is_interrupted_result(0),_write_track(0),_quick_timeout(0),_merge_endpoints(2),_run_scenario_quick(3),_should_run_visual_diff(0),_quick_pass_actions(2),_quick_probe_limit(1),_quick_probe_timeout(0),_run_live_http_probes(2),_try_parse_json_summary(0),_try_find_line_summary(0),_summarize_testql_failure(0),_summarize_health_scenario_failure(0),_run_fleet_health_scenario(0),_run_quick_test_no_scenarios(2),_get_quick_scenarios(1),_run_quick_scenarios_loop(3),run_quick_test(2),_publish_visual_events(2),run_detail_test(2),process_test_queue_once(0),process_changed_file_once(1),_run_periodic_probes_once(0),_start_periodic_probe_thread(0),start_background_tasks(0)  # WUP watcher running selective TestQL scenarios for changed s...
  wup/status_data.py:
    e: _load_json,_recent_health_events,_summarize_deps,_load_manifest,collect_status_snapshot
    _load_json(path)
    _recent_health_events(events_path;delta_seconds)
    _summarize_deps(deps_path)
    _load_manifest(cfg_path)
    collect_status_snapshot(project_root)
  wup/core.py:
    e: WupWatcher,WupEventHandler
    WupWatcher: __init__(6),_to_relative_path(1),_service_name_prefixes(0),infer_service(1),_is_coincident_pair(2),detect_service_coincidences(1),_services_share_domain(2),get_service_config(1),should_test(1),schedule_quick_test(1),schedule_detail_test(1),process_test_queue_once(0),cpu_ok(0),run_quick_test(1),run_detail_test(1),test_loop(0),should_watch_file(1),_path_matches_exclude_pattern(2),_is_file_ignored(1),_notify_all_configured_services(1),on_file_change(1),build_watched_paths(0),_create_and_start_observer(2),start_background_tasks(0),prepare_observer(1),start_watching(1),create_status_table(0),run_with_dashboard(0)  # Intelligent file watcher for regression testing.

Implements...
    WupEventHandler(FileSystemEventHandler): __init__(1),on_modified(1),on_created(1),on_deleted(1)  # File system event handler for WUP watcher...
  wup/assistant_discovery.py:
    e: detect_framework,auto_detect_services,detect_service_type
    detect_framework(project_root)
    auto_detect_services(project_root;framework)
    detect_service_type(name;path)
  wup/multi.py:
    e: MultiProjectWatcher
    MultiProjectWatcher: __init__(2),start_watching(0)  # Drive multiple watchers from one loop, one observer per proj...
  wup/_ast_detector.py:
    e: ASTDetector
    ASTDetector(BaseDetector): __init__(1),_collect_import(0),_collect_import_from(0),_collect_class(0),_collect_function(0),_extract_ast_info(1),_snapshot_path(1),_compute_changes(2),detect(1)  # Detect changes in Python files using AST comparison...
  wup/visual_diff.py:
    e: VisualDiffer,_playwright_available,_warn_playwright_missing,_chromium_launch_options,_fetch_dom_snapshot,_detect_content_issues,_page_slug,_short_url,_compact_error_message,_sample_list,_looks_like_visual_page,_snapshot_path,_load_snapshot,_save_snapshot,_node_signature,_flatten,_diff_snapshots,_resolve_base_url
    VisualDiffer: __init__(2),_pages_for_service(1),_categorize_page_result(7),_print_scan_summary(4),run_for_service(1),_build_progress(2),_check_page(2),_write_diff_event(3),get_recent_diffs(1)  # Triggered by TestQLWatcher after a file change.

Usage::

  ...
    _playwright_available()
    _warn_playwright_missing()
    _chromium_launch_options(headless)
    _fetch_dom_snapshot(url;max_depth;headless;error_selectors;page_settle_ms)
    _detect_content_issues(snapshot;cfg)
    _page_slug(url)
    _short_url(url)
    _compact_error_message(message;max_len)
    _sample_list(items;limit)
    _looks_like_visual_page(url)
    _snapshot_path(snapshot_dir;service;url)
    _load_snapshot(file_path)
    _save_snapshot(file_path;snapshot)
    _node_signature(node;depth)
    _flatten(node;depth;max_depth)
    _diff_snapshots(old;new;max_depth;threshold_added;threshold_removed;threshold_changed)
    _resolve_base_url(cfg)
  packages/nlp2wup/src/nlp2wup/apply.py:
    e: ApplyResult,_intent,_simple_command,_generated_command,_special_command,to_dsl,apply_nl
    ApplyResult: to_dict(0)
    _intent(prompt)
    _simple_command(intent;explicit_file;project)
    _generated_command(prompt;explicit_file;project)
    _special_command(intent;prompt;explicit_file;file;project)
    to_dsl(prompt)
    apply_nl(prompt)
  packages/dsl2wup/src/dsl2wup/grammar.py:
    e: split_command,pick_flag,_flag_values,_parse_query,_parse_validate,_parse_resolve,_parse_health,_parse_patch,_parse_map,_parse_init,_parse_generate,_parse_sync,_parse_adopt,_parse_endpoints,_parse_status,_parse_init_cli,parse_line,to_text
    split_command(line)
    pick_flag(tokens;flag)
    _flag_values(cmd;tokens)
    _parse_query(rest;cmd)
    _parse_validate(rest;cmd)
    _parse_resolve(rest;cmd)
    _parse_health(rest;cmd)
    _parse_patch(rest;cmd)
    _parse_map(rest;cmd)
    _parse_init(rest;cmd)
    _parse_generate(rest;cmd)
    _parse_sync(rest;cmd)
    _parse_adopt(rest;cmd)
    _parse_endpoints(rest;cmd)
    _parse_status(rest;cmd)
    _parse_init_cli(rest;cmd)
    parse_line(line)
    to_text(cmd)
  wup/testql_discovery.py:
    e: TestQLEndpointDiscovery
    TestQLEndpointDiscovery: __init__(2),discover_scenarios(0),parse_scenario_endpoints(1),infer_service_from_scenario(1),discover_all_endpoints(0),discover_via_testql_cli(1),to_dependency_map(0)  # Discover endpoints from TestQL scenario files...
  packages/uri2wup/src/uri2wup/patch.py:
    e: PatchResult,_resolve_config_path,_replace_at_path,patch_uri
    PatchResult: to_dict(0)
    _resolve_config_path(project;file_param)
    _replace_at_path(raw;parts;fragment)
    patch_uri(uri)
  packages/dsl2wup/src/dsl2wup/pb_codec.py:
    e: _canonical_verb,_set_body,_body_to_dict,envelope_to_dict,encode_protobuf,decode_protobuf,encode_text_to_protobuf,decode_protobuf_to_text,result_to_pb,encode_result_protobuf
    _canonical_verb(verb)
    _set_body(envelope;cmd)
    _body_to_dict(verb;msg)
    envelope_to_dict(envelope)
    encode_protobuf(cmd)
    decode_protobuf(data)
    encode_text_to_protobuf(line)
    decode_protobuf_to_text(data)
    result_to_pb(result)
    encode_result_protobuf(result)
  packages/dsl2wup/src/dsl2wup/codegen.py:
    e: _field_type,_field_line,_append_model,generate_models,main
    _field_type(prop)
    _field_line(name;prop;required)
    _append_model(lines;schema_file)
    generate_models()
    main()
  wup/config.py:
    e: find_config_file,_read_dotenv,_load_dotenv,load_config,_parse_project_config,_parse_watch_config,_parse_services_config,_parse_strategy_config,_normalize_testql_timeout,_parse_testql_extra_args,_normalize_testql_extra_args,_parse_testql_config,_parse_visual_diff_config,_parse_web_config,_parse_planfile_config,_parse_anomaly_detection_config,_parse_semcod_tools_config,validate_config,detect_watch_paths,get_default_config,save_config
    find_config_file(project_root)
    _read_dotenv(project_root)
    _load_dotenv(project_root;environ)
    load_config(project_root;config_path)
    _parse_project_config(raw)
    _parse_watch_config(raw)
    _parse_services_config(raw)
    _parse_strategy_config(raw)
    _normalize_testql_timeout(val)
    _parse_testql_extra_args(extra_args_raw)
    _normalize_testql_extra_args(extra_args_raw)
    _parse_testql_config(raw;environ)
    _parse_visual_diff_config(raw;environ)
    _parse_web_config(raw;environ)
    _parse_planfile_config(raw;environ)
    _parse_anomaly_detection_config(raw)
    _parse_semcod_tools_config(raw)
    validate_config(raw)
    detect_watch_paths(project_root)
    get_default_config(project_root)
    save_config(config;output_path)
  wup/cli_scanner.py:
    e: CLICommand,CLIPackage,CLIScanner
    CLICommand:  # Represents a detected CLI command...
    CLIPackage:  # Represents a detected CLI package...
    CLIScanner: __init__(1),scan(0),_scan_setup_py(1),_scan_setup_cfg(1),_scan_pyproject_toml(1),_scan_main_modules(0),_parse_entry_points_dict(2),_add_entry_point(4),infer_command_args(1),_find_module_path(1),_get_help_arguments(1),to_dict(0)  # Scanner for detecting CLI commands in a project...
  packages/nlp2wup/src/nlp2wup/cli.py:
    e: main
    main(argv)
  wup/assistant_validator.py:
    e: validate_config,generate_suggestions
    validate_config(config;project_root)
    generate_suggestions(config)
  wup/init_cli.py:
    e: setup_cli_project
    setup_cli_project(project_root)
  wup/sync.py:
    e: _merge_endpoints,sync_testql_manifest
    _merge_endpoints(config_path;wup_config;suggested;project_path)
    sync_testql_manifest(project_root)
  packages/cli2wup/src/cli2wup/cli.py:
    e: run_shell,_print_result,_run_script,_run_command,main
    run_shell()
    _print_result(result)
    _run_script(args)
    _run_command(args)
    main(argv)
  packages/dsl2wup/src/dsl2wup/cli.py:
    e: _main_legacy,_main_subcommand,main
    _main_legacy(argv)
    _main_subcommand(argv)
    main(argv)
  wup/validate.py:
    e: validate_wup_file
    validate_wup_file(path)
  wup/generate.py:
    e: _detect_template,generate_wup_config
    _detect_template(hint;explicit)
    generate_wup_config(project_root)
  wup/_yaml_detector.py:
    e: YAMLStructureDetector
    YAMLStructureDetector(BaseDetector): __init__(1),_load_yaml(1),_extract_structure(3),_snapshot_path(1),_compare_structures(3),_compare_dict_structures(3),detect(1),_generate_suggestions(1)  # Detect structural changes in YAML files...
  wup/discovery.py:
    e: Endpoint,SourceIndex,DiscoveryAdapter,FastAPIAdapter,FlaskAdapter,DjangoAdapter,ExpressAdapter,FastifyAdapter,HonoAdapter,NestJSAdapter,GoAdapter,OpenAPIAdapter,detect_frameworks,discover_endpoints
    Endpoint: as_dict(0)  # A discovered HTTP endpoint...
    SourceIndex: __init__(1),_read_ext(1),files(1),contains(2)  # Reads and caches project source files once, so every adapter...
    DiscoveryAdapter: detect(1),scan(1)  # Base adapter. Subclasses set name/extensions/markers or over...
    FastAPIAdapter(DiscoveryAdapter):
    FlaskAdapter(DiscoveryAdapter):
    DjangoAdapter(DiscoveryAdapter):
    ExpressAdapter(DiscoveryAdapter):
    FastifyAdapter(DiscoveryAdapter):
    HonoAdapter(DiscoveryAdapter):
    NestJSAdapter(DiscoveryAdapter):
    GoAdapter(DiscoveryAdapter):
    OpenAPIAdapter(DiscoveryAdapter): _load_spec(1),detect(1),scan(1)  # Extract paths from an OpenAPI/Swagger document (yaml or json...
    detect_frameworks(index)
    discover_endpoints(project_root;framework;index)
  wup/testing/handlers/health_handlers.py:
    e: ServiceHealthProjection,register_health_handlers
    ServiceHealthProjection: __init__(5),_load_initial_state(0),_save_state(0),handle_health_changed(1),handle_get_health(1)  # Maintains the materialized view of service health...
    register_health_handlers(bus;health_state_path;event_store;planfile_reporter;browser_notifier;web_client)
  packages/dsl2wup/src/dsl2wup/handlers/command.py:
    e: _read_content,_project_root,handle_map,handle_init,handle_generate,handle_patch,handle_sync,handle_init_cli,_query_handlers,_command_handlers,handle_adopt,handle_from_tokens
    _read_content(path)
    _project_root(cmd)
    handle_map(cmd)
    handle_init(cmd)
    handle_generate(cmd)
    handle_patch(cmd)
    handle_sync(cmd)
    handle_init_cli(cmd)
    _query_handlers()
    _command_handlers()
    handle_adopt(cmd)
    handle_from_tokens(line;tokens)
  packages/uri2wup/src/uri2wup/uri.py:
    e: _encode,_decode,uri_for_cmd,uri_for_block,is_wup_uri,parse_wup_uri
    _encode(value)
    _decode(value)
    uri_for_cmd(verb)
    uri_for_block()
    is_wup_uri(uri)
    parse_wup_uri(uri)
  wup/anomaly_detector.py:
    e: AnomalyDetector,quick_scan,scan_yaml_changes
    AnomalyDetector: __init__(2),_should_scan(1),scan_file(1),scan_directory(3),get_summary(1),print_report(1)  # Main anomaly detector combining multiple detection methods...
    quick_scan(project_root;files)
    scan_yaml_changes(project_root;yaml_dir)
  examples/c2004_monorepo_demo.py:
    e: _discover_modules,_print_config_summary,_analyze_module,_analyze_module_structure,_test_file_inference,_print_endpoints_summary,_print_recommendations,analyze_monorepo,simulate_monorepo,main
    _discover_modules(project_root)
    _print_config_summary(config)
    _analyze_module(module_path)
    _analyze_module_structure(project_root;modules)
    _test_file_inference(project_root;config)
    _print_endpoints_summary(config)
    _print_recommendations()
    analyze_monorepo(project_path)
    simulate_monorepo()
    main()
  packages/uri2wup/src/uri2wup/decode.py:
    e: _dict_to_dsl,_command_from_params,_block_query,decode_uri
    _dict_to_dsl(cmd)
    _command_from_params(parts;params)
    _block_query(uri;parsed)
    decode_uri(uri)
  packages/dsl2wup/src/dsl2wup/events.py:
    e: DslEvent,EventStore,default_event_store
    DslEvent: to_dict(0)
    EventStore: __init__(1),append(2),replay(0)
    default_event_store(manifest_file)
  packages/dsl2wup/src/dsl2wup/bus.py:
    e: _dispatch_cmd,_bytes_to_cmd,dispatch,execute_dsl_line,execute_dsl
    _dispatch_cmd(cmd)
    _bytes_to_cmd(data)
    dispatch(envelope)
    execute_dsl_line(line)
    execute_dsl(text)
  wup/dependency_mapper.py:
    e: DependencyMapper
    DependencyMapper: __init__(1),build_from_codebase(1),_detect_framework(0),_infer_service(1),get_endpoints_for_file(1),get_endpoints_for_service(1),get_files_for_service(1),get_service_for_file(1),to_dict(0),save(1),load(1),build_from_testql_scenarios(2)  # Maps project dependencies for intelligent testing...
  wup/web_client.py:
    e: WebClient,_httpx_available,resolve_endpoint,_normalize
    WebClient: __init__(1),_headers(0),send_event(1),send_regression(5),send_pass(2),send_health_transition(3),send_visual_diff(3)  # Async event sink for the wupbro backend.

Usage::

    clien...
    _httpx_available()
    resolve_endpoint(cfg)
    _normalize(payload)
  examples/visual_diff_demo.py:
    e: _make_dom,_save_snapshot,demo_diff_algorithm,demo_page_slug,demo_snapshot_persistence,demo_config_yaml_round_trip,demo_disabled_is_noop,demo_live_page,main
    _make_dom(n_divs)
    _save_snapshot(path;dom)
    demo_diff_algorithm()
    demo_page_slug()
    demo_snapshot_persistence()
    demo_config_yaml_round_trip()
    demo_disabled_is_noop()
    demo_live_page(url)
    main()
  examples/testql_demo.py:
    e: _run_with_mock_services,_build_mock_services,simulate_testql_analysis,simulate_with_mock_data
    _run_with_mock_services(mapper;mock_services)
    _build_mock_services(mapper)
    simulate_testql_analysis(testql_path)
    simulate_with_mock_data()
  examples/testql_integration.py:
    e: CustomTestQLWatcher,main
    CustomTestQLWatcher(WupWatcher): __init__(2),run_quick_test(2),run_detail_test(2),_find_scenarios_for_service(1),_generate_blame_report(2)  # Custom WUP watcher integrated with TestQL test framework.

O...
    main()
  examples/webhook_notifications.py:
    e: NotificationRouter,create_slack_payload,create_teams_payload,create_discord_payload,show_webhook_demo,main
    NotificationRouter: __init__(0),add_slack(1),add_teams(1),add_discord(1),send(1)  # Routes WUP events to configured notification channels...
    create_slack_payload(event)
    create_teams_payload(event)
    create_discord_payload(event)
    show_webhook_demo()
    main()
  scripts/run_probe_smoke.py:
    e: print_probe_plan,run_live_http_probes,run_quick_testql_dryrun,print_service_health,check_manifest_stale_probes,main
    print_probe_plan(manifest)
    run_live_http_probes(watcher;services)
    run_quick_testql_dryrun(watcher;services)
    print_service_health(health_path)
    check_manifest_stale_probes(manifest_path)
    main()
  wup/testql_cli_generator.py:
    e: TestQLCLIGenerator
    TestQLCLIGenerator: __init__(1),generate(2),_generate_smoke_scenario(2),_generate_command_scenario(3),generate_custom_scenario(3),print_summary(1)  # Generate TestQL scenarios for CLI command testing...
  wup/bootstrap.py:
    e: _watchdog_preflight,main
    _watchdog_preflight()
    main(argv)
  wup/cli_config_generator.py:
    e: CLIConfigGenerator
    CLIConfigGenerator: __init__(1),generate(2),_generate_config(2),_create_shell_service(1),_save_config(2),print_summary(1)  # Generate wup.yaml configuration for CLI/shell services...
  packages/dsl2wup/src/dsl2wup/handlers/query.py:
    e: _project_root,handle_query,handle_validate,handle_resolve,handle_status,handle_endpoints,handle_health
    _project_root(cmd;default_file)
    handle_query(cmd)
    handle_validate(cmd)
    handle_resolve(cmd)
    handle_status(cmd)
    handle_endpoints(cmd)
    handle_health(cmd)
  wup/endpoints.py:
    e: discover_testql_endpoints
    discover_testql_endpoints(scenarios_dir)
  wup/_hash_detector.py:
    e: HashDetector
    HashDetector(BaseDetector): __init__(1),_compute_hash(1),_snapshot_path(1),detect(1)  # Fast anomaly detection using file hashes...
  wup/testing/handlers/event_handlers.py:
    e: TestResultEventHandler,register_testing_event_handlers
    TestResultEventHandler: __init__(3),handle_test_failed(1),handle_test_passed(1)  # Handles test result events to update planfile reporter and w...
    register_testing_event_handlers(bus;planfile_reporter;web_client;console)
  packages/uri2wup/src/uri2wup/cli.py:
    e: _run_resolve,_run_decode,_run_query,_run_dispatch,main
    _run_resolve(args)
    _run_decode(args)
    _run_query(args)
    _run_dispatch(args)
    main(argv)
  packages/rest2wup/src/rest2wup/cli.py:
    e: main
    main(argv)
  packages/uri2wup/src/uri2wup/nlp2uri.py:
    e: UriHit,nlp2uri,best_uri
    UriHit: to_dict(0)
    nlp2uri(prompt)
    best_uri(prompt)
  packages/mcp2wup/src/mcp2wup/cli.py:
    e: main
    main(argv)
  wup/bus.py:
    e: Message,Command,Event,Query,EventBus
    Message:  # Base message type...
    Command(Message):  # Command changes state...
    Event(Message):  # Event indicates something happened...
    Query(Message):  # Query requests data without changing state...
    EventBus: __init__(0),subscribe(2),publish(1),execute(1),query(1)  # Simple in-memory event bus and command/query dispatcher...
  wup/event_store.py:
    e: EventStore
    EventStore: __init__(1),append(1),read_all(0)  # Append-only store for domain events...
  wup/control.py:
    e: _result_dict,dispatch_validate,dispatch_query,dispatch_health,dispatch_map,dispatch_init,dispatch_sync,dispatch_generate,dispatch_status,dispatch_endpoints,dispatch_init_cli,dispatch_command
    _result_dict(line)
    dispatch_validate(path)
    dispatch_query(target)
    dispatch_health()
    dispatch_map()
    dispatch_init()
    dispatch_sync()
    dispatch_generate(hint)
    dispatch_status()
    dispatch_endpoints(scenarios_dir)
    dispatch_init_cli()
    dispatch_command(command)
  packages/dsl2wup/src/dsl2wup/codec.py:
    e: encode_text,roundtrip_text,encode_protobuf,decode_protobuf
    encode_text(line)
    roundtrip_text(line)
    encode_protobuf(line)
    decode_protobuf(data)
  examples/ci_cd_integration.py:
    e: generate_github_actions,generate_gitlab_ci,show_ci_cd_demo,main
    generate_github_actions()
    generate_gitlab_ci()
    show_ci_cd_demo()
    main()
  packages/nlp2wup/src/nlp2wup/generate.py:
    e: _extract_template,generate_from_nl
    _extract_template(prompt)
    generate_from_nl(prompt)
  wup/cli_bridge.py:
    e: _result,_guard,run_map_deps,run_init,run_sync,run_generate,run_validate,run_status,run_endpoints,run_init_cli
    _result(action;data)
    _guard(action;operation)
    run_map_deps()
    run_init()
    run_sync()
    run_generate()
    run_validate()
    run_status()
    run_endpoints()
    run_init_cli()
  wup/__init__.py:
    e: __getattr__
    __getattr__(name)
  packages/mcp2wup/src/mcp2wup/server.py:
    e: WupMCPServer,_require_fastmcp,create_server,run_server
    WupMCPServer: __post_init__(0),_register_tools(0),run(0)
    _require_fastmcp()
    create_server(name)
    run_server()
  examples/flask-app/app/auth/routes.py:
    e: login,logout,register,profile,change_password
    login()
    logout()
    register()
    profile()
    change_password()
  packages/rest2wup/src/rest2wup/app.py:
    e: create_app
    create_app()
  packages/nlp2wup/src/nlp2wup/validate.py:
    e: validate_wup_config
    validate_wup_config(path)
  packages/dsl2wup/src/dsl2wup/result.py:
    e: DslResult
    DslResult: to_dict(0)
  wup/_base_detector.py:
    e: BaseDetector
    BaseDetector: __init__(2),detect(1)  # Base anomaly detector...
  wup/paths.py:
    e: health_state_path,health_events_path
    health_state_path(project)
    health_events_path(project)
  examples/flask-app/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/payments-service/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/payments-service/app/payments/routes.py:
    e: list_payments,get_payment,create_payment
    list_payments()
    get_payment(payment_id)
    create_payment()
  examples/multi-service/auth-service/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/auth-service/app/auth/routes.py:
    e: login,register
    login()
    register()
  examples/multi-service/users-service/main.py:
    e: root,health
    root()
    health()
  examples/multi-service/users-service/app/users/routes.py:
    e: list_users,get_user,create_user
    list_users()
    get_user(user_id)
    create_user()
  examples/fastapi-app/main.py:
    e: root,health
    root()
    health()
  examples/fastapi-app/app/users/routes.py:
    e: User,list_users,get_user,create_user,update_user,delete_user
    User(BaseModel):
    list_users()
    get_user(user_id)
    create_user(user)
    update_user(user_id;user)
    delete_user(user_id)
  deps.json:
  goal.yaml:
  regix.yaml:
  local.dev.txt:
  koru.yaml:
  tree.txt:
  todo.txt:
  duplication.json:
  testql-deps.json:
  Taskfile.yml:
  project.sh:
  packages/install-dev.sh:
  packages/cli2wup/local.dev.txt:
  packages/cli2wup/pyproject.toml:
  packages/cli2wup/src/cli2wup/__init__.py:
  packages/rest2wup/local.dev.txt:
  packages/rest2wup/pyproject.toml:
  packages/rest2wup/src/rest2wup/__init__.py:
  packages/uri2wup/local.dev.txt:
  packages/uri2wup/pyproject.toml:
  packages/uri2wup/src/uri2wup/__init__.py:
  packages/nlp2wup/local.dev.txt:
  packages/nlp2wup/pyproject.toml:
  packages/nlp2wup/src/nlp2wup/__init__.py:
  packages/dsl2wup/local.dev.txt:
  packages/dsl2wup/pyproject.toml:
  packages/dsl2wup/src/dsl2wup/engine.py:
  packages/dsl2wup/src/dsl2wup/__init__.py:
  packages/dsl2wup/src/dsl2wup/models.py:
    e: AdoptCommand,EndpointsCommand,GenerateCommand,HealthCommand,InitCommand,InitCliCommand,MapCommand,PatchCommand,QueryCommand,ResolveCommand,StatusCommand,SyncCommand,ValidateCommand
    AdoptCommand(BaseModel):
    EndpointsCommand(BaseModel):
    GenerateCommand(BaseModel):
    HealthCommand(BaseModel):
    InitCommand(BaseModel):
    InitCliCommand(BaseModel):
    MapCommand(BaseModel):
    PatchCommand(BaseModel):
    QueryCommand(BaseModel):
    ResolveCommand(BaseModel):
    StatusCommand(BaseModel):
    SyncCommand(BaseModel):
    ValidateCommand(BaseModel):
  packages/dsl2wup/src/dsl2wup/schema/commands/patch.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/init_cli.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/health.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/adopt.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/map.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/endpoints.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/status.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/init.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/resolve.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/generate.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/query.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/sync.schema.json:
  packages/dsl2wup/src/dsl2wup/schema/commands/validate.schema.json:
  examples/flask-app/app/__init__.py:
  packages/dsl2wup/src/dsl2wup/v1/result_pb2.py:
  packages/dsl2wup/src/dsl2wup/v1/command_pb2.py:
  packages/dsl2wup/scripts/generate-proto.sh:
  packages/dsl2wup/proto/dsl2wup/v1/result.proto:
  packages/dsl2wup/proto/dsl2wup/v1/command.proto:
  packages/mcp2wup/local.dev.txt:
  packages/mcp2wup/pyproject.toml:
  packages/mcp2wup/src/mcp2wup/__init__.py:
  wup/anomaly_models.py:
    e: AnomalyResult,YAMLAnomalyConfig
    AnomalyResult:  # Result of anomaly detection...
    YAMLAnomalyConfig:  # Configuration for YAML anomaly detection...
  wup/file_watcher/events/file_events.py:
    e: FileChanged
    FileChanged(Event):
  wup/models/config.py:
    e: NotifyConfig,ServiceTestConfig,ServiceConfig,WatchConfig,TestStrategyConfig,TestQLConfig,VisualDiffConfig,WebConfig,PlanfileConfig,AnomalyDetectionConfig,SemcodToolConfig,SemcodToolsConfig,ProjectConfig,WupConfig
    NotifyConfig:  # Notification configuration for a service...
    ServiceTestConfig:  # Test configuration for a service (quick or detail)...
    ServiceConfig:  # Configuration for a single service...
    WatchConfig:  # Configuration for file watching...
    TestStrategyConfig:  # Global test strategy configuration...
    TestQLConfig:  # TestQL-specific configuration...
    VisualDiffConfig:  # Configuration for visual DOM diff after file changes...
    WebConfig:  # Configuration for sending events to wupbro backend...
    PlanfileConfig:  # Configuration for creating planfile tickets from WUP failure...
    AnomalyDetectionConfig:  # Configuration for fast anomaly detection without Playwright...
    SemcodToolConfig:  # Optional Semcod ecosystem tool attached to WUP monitoring au...
    SemcodToolsConfig:  # Optional Semcod ecosystem integrations (deta/regres/regix)...
    ProjectConfig:  # Project metadata...
    WupConfig:  # Main WUP configuration...
  wup/models/target.py:
    e: ServiceTestTarget
    ServiceTestTarget:  # A service and the endpoints that should be exercised for it...
  wup/models/__init__.py:
  wup/testing/queries/health_queries.py:
    e: GetServiceHealth
    GetServiceHealth(Query):
  wup/testing/events/health_events.py:
    e: ServiceHealthChanged
    ServiceHealthChanged(Event):
  examples/flask-app/wup.yaml:
  examples/flask-app/requirements.txt:
  examples/flask-app/Dockerfile:
  examples/multi-service/docker-compose.yml:
  examples/multi-service/payments-service/wup.yaml:
  examples/multi-service/payments-service/requirements.txt:
  examples/multi-service/payments-service/Dockerfile:
  examples/multi-service/auth-service/wup.yaml:
  examples/multi-service/users-service/wup.yaml:
  examples/fastapi-app/wup.yaml:
  examples/fastapi-app/requirements.txt:
  testql-scenarios/cli-smoke.testql.toon.yaml:
  testql-scenarios/cli-wup.testql.toon.yaml:
  testql-scenarios/generated-from-pytests.testql.toon.yaml:
  testql-scenarios/generated-cli-tests.testql.toon.yaml:
  Makefile:
  pyproject.toml:
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('wup', '0.2.77', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 264, 'less').
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
project_file('packages/cli2wup/src/cli2wup/__init__.py', 2, 'python').
project_file('packages/cli2wup/src/cli2wup/cli.py', 101, 'python').
project_file('packages/cli2wup/tests/test_cli2wup.py', 8, 'python').
project_file('packages/dsl2wup/scripts/generate-proto.sh', 8, 'shell').
project_file('packages/dsl2wup/src/dsl2wup/__init__.py', 7, 'python').
project_file('packages/dsl2wup/src/dsl2wup/bus.py', 80, 'python').
project_file('packages/dsl2wup/src/dsl2wup/cli.py', 109, 'python').
project_file('packages/dsl2wup/src/dsl2wup/codec.py', 36, 'python').
project_file('packages/dsl2wup/src/dsl2wup/codegen.py', 71, 'python').
project_file('packages/dsl2wup/src/dsl2wup/engine.py', 9, 'python').
project_file('packages/dsl2wup/src/dsl2wup/events.py', 117, 'python').
project_file('packages/dsl2wup/src/dsl2wup/grammar.py', 154, 'python').
project_file('packages/dsl2wup/src/dsl2wup/handlers/command.py', 272, 'python').
project_file('packages/dsl2wup/src/dsl2wup/handlers/query.py', 138, 'python').
project_file('packages/dsl2wup/src/dsl2wup/models.py', 130, 'python').
project_file('packages/dsl2wup/src/dsl2wup/pb_codec.py', 148, 'python').
project_file('packages/dsl2wup/src/dsl2wup/result.py', 29, 'python').
project_file('packages/dsl2wup/src/dsl2wup/schema_registry.py', 85, 'python').
project_file('packages/dsl2wup/src/dsl2wup/v1/__init__.py', 1, 'python').
project_file('packages/dsl2wup/src/dsl2wup/v1/command_pb2.py', 63, 'python').
project_file('packages/dsl2wup/src/dsl2wup/v1/result_pb2.py', 40, 'python').
project_file('packages/dsl2wup/tests/test_dsl2wup.py', 38, 'python').
project_file('packages/dsl2wup/tests/test_generate.py', 15, 'python').
project_file('packages/dsl2wup/tests/test_health_paths.py', 19, 'python').
project_file('packages/dsl2wup/tests/test_parity.py', 66, 'python').
project_file('packages/dsl2wup/tests/test_parity_across_adapters.py', 77, 'python').
project_file('packages/dsl2wup/tests/test_protobuf.py', 18, 'python').
project_file('packages/dsl2wup/tests/test_protobuf_extended.py', 21, 'python').
project_file('packages/dsl2wup/tests/test_validate_schema.py', 18, 'python').
project_file('packages/install-dev.sh', 25, 'shell').
project_file('packages/mcp2wup/src/mcp2wup/__init__.py', 6, 'python').
project_file('packages/mcp2wup/src/mcp2wup/cli.py', 25, 'python').
project_file('packages/mcp2wup/src/mcp2wup/server.py', 150, 'python').
project_file('packages/mcp2wup/tests/test_mcp2wup.py', 12, 'python').
project_file('packages/nlp2wup/src/nlp2wup/__init__.py', 8, 'python').
project_file('packages/nlp2wup/src/nlp2wup/apply.py', 168, 'python').
project_file('packages/nlp2wup/src/nlp2wup/cli.py', 44, 'python').
project_file('packages/nlp2wup/src/nlp2wup/generate.py', 25, 'python').
project_file('packages/nlp2wup/src/nlp2wup/validate.py', 12, 'python').
project_file('packages/nlp2wup/tests/test_apply.py', 45, 'python').
project_file('packages/rest2wup/src/rest2wup/__init__.py', 6, 'python').
project_file('packages/rest2wup/src/rest2wup/app.py', 69, 'python').
project_file('packages/rest2wup/src/rest2wup/cli.py', 29, 'python').
project_file('packages/rest2wup/tests/test_rest2wup.py', 21, 'python').
project_file('packages/uri2wup/src/uri2wup/__init__.py', 8, 'python').
project_file('packages/uri2wup/src/uri2wup/cli.py', 73, 'python').
project_file('packages/uri2wup/src/uri2wup/decode.py', 62, 'python').
project_file('packages/uri2wup/src/uri2wup/nlp2uri.py', 49, 'python').
project_file('packages/uri2wup/src/uri2wup/patch.py', 92, 'python').
project_file('packages/uri2wup/src/uri2wup/query.py', 154, 'python').
project_file('packages/uri2wup/src/uri2wup/uri.py', 93, 'python').
project_file('packages/uri2wup/tests/test_decode.py', 27, 'python').
project_file('packages/uri2wup/tests/test_patch.py', 29, 'python').
project_file('packages/uri2wup/tests/test_query.py', 36, 'python').
project_file('project.sh', 49, 'shell').
project_file('scripts/run_probe_smoke.py', 89, 'python').
project_file('tests/test_aql.py', 121, 'python').
project_file('tests/test_assistant.py', 180, 'python').
project_file('tests/test_auto_detection.py', 195, 'python').
project_file('tests/test_bootstrap.py', 32, 'python').
project_file('tests/test_cli_bridge.py', 36, 'python').
project_file('tests/test_cli_filtering.py', 266, 'python').
project_file('tests/test_control.py', 19, 'python').
project_file('tests/test_discovery_adapters.py', 119, 'python').
project_file('tests/test_e2e.py', 515, 'python').
project_file('tests/test_endpoints_init_cli.py', 69, 'python').
project_file('tests/test_genericity.py', 136, 'python').
project_file('tests/test_health_summary_passed.py', 54, 'python').
project_file('tests/test_monitoring_manifest.py', 72, 'python').
project_file('tests/test_multi_project.py', 155, 'python').
project_file('tests/test_oql.py', 105, 'python').
project_file('tests/test_planfile_reporter_dedupe.py', 79, 'python').
project_file('tests/test_probe_mutex.py', 39, 'python').
project_file('tests/test_service_inference.py', 210, 'python').
project_file('tests/test_status_data.py', 35, 'python').
project_file('tests/test_sync.py', 42, 'python').
project_file('tests/test_testql_monitor.py', 218, 'python').
project_file('tests/test_testql_watcher.py', 597, 'python').
project_file('tests/test_visual_diff_periodic_skip.py', 41, 'python').
project_file('tests/test_visual_diff_progress.py', 56, 'python').
project_file('tests/test_watch_exclude.py', 35, 'python').
project_file('tests/test_watch_no_paths_exit.py', 31, 'python').
project_file('tests/test_web_client.py', 168, 'python').
project_file('tests/test_wup.py', 1978, 'python').
project_file('tests/test_wup_generate.py', 22, 'python').
project_file('tree.sh', 2, 'shell').
project_file('wup/__init__.py', 47, 'python').
project_file('wup/_ast_detector.py', 125, 'python').
project_file('wup/_base_detector.py', 19, 'python').
project_file('wup/_hash_detector.py', 73, 'python').
project_file('wup/_yaml_detector.py', 129, 'python').
project_file('wup/anomaly_detector.py', 176, 'python').
project_file('wup/anomaly_models.py', 36, 'python').
project_file('wup/aql.py', 309, 'python').
project_file('wup/assistant.py', 585, 'python').
project_file('wup/assistant_discovery.py', 100, 'python').
project_file('wup/assistant_validator.py', 58, 'python').
project_file('wup/bootstrap.py', 62, 'python').
project_file('wup/bus.py', 66, 'python').
project_file('wup/cli.py', 1080, 'python').
project_file('wup/cli_bridge.py', 195, 'python').
project_file('wup/cli_config_generator.py', 224, 'python').
project_file('wup/cli_scanner.py', 302, 'python').
project_file('wup/config.py', 585, 'python').
project_file('wup/control.py', 128, 'python').
project_file('wup/core.py', 741, 'python').
project_file('wup/dependency_mapper.py', 178, 'python').
project_file('wup/discovery.py', 280, 'python').
project_file('wup/endpoints.py', 45, 'python').
project_file('wup/event_store.py', 42, 'python').
project_file('wup/file_watcher/events/file_events.py', 11, 'python').
project_file('wup/generate.py', 63, 'python').
project_file('wup/init_cli.py', 61, 'python').
project_file('wup/models/__init__.py', 37, 'python').
project_file('wup/models/config.py', 207, 'python').
project_file('wup/models/target.py', 24, 'python').
project_file('wup/monitoring_manifest.py', 479, 'python').
project_file('wup/multi.py', 82, 'python').
project_file('wup/oql.py', 268, 'python').
project_file('wup/paths.py', 17, 'python').
project_file('wup/planfile_reporter.py', 268, 'python').
project_file('wup/status_data.py', 115, 'python').
project_file('wup/sync.py', 71, 'python').
project_file('wup/testing/events/health_events.py', 12, 'python').
project_file('wup/testing/events/test_results.py', 22, 'python').
project_file('wup/testing/handlers/event_handlers.py', 56, 'python').
project_file('wup/testing/handlers/health_handlers.py', 124, 'python').
project_file('wup/testing/queries/health_queries.py', 8, 'python').
project_file('wup/testql_cli_generator.py', 216, 'python').
project_file('wup/testql_discovery.py', 230, 'python').
project_file('wup/testql_monitor.py', 694, 'python').
project_file('wup/testql_watcher.py', 1014, 'python').
project_file('wup/validate.py', 35, 'python').
project_file('wup/visual_diff.py', 639, 'python').
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
python_function('packages/cli2wup/src/cli2wup/cli.py', 'run_shell', 0, 9, 8).
python_function('packages/cli2wup/src/cli2wup/cli.py', '_print_result', 1, 4, 4).
python_function('packages/cli2wup/src/cli2wup/cli.py', '_run_script', 1, 3, 4).
python_function('packages/cli2wup/src/cli2wup/cli.py', '_run_command', 1, 2, 2).
python_function('packages/cli2wup/src/cli2wup/cli.py', 'main', 1, 4, 13).
python_function('packages/cli2wup/tests/test_cli2wup.py', 'test_cli_help', 0, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/bus.py', '_dispatch_cmd', 1, 5, 12).
python_function('packages/dsl2wup/src/dsl2wup/bus.py', '_bytes_to_cmd', 1, 3, 5).
python_function('packages/dsl2wup/src/dsl2wup/bus.py', 'dispatch', 1, 6, 11).
python_function('packages/dsl2wup/src/dsl2wup/bus.py', 'execute_dsl_line', 1, 1, 1).
python_function('packages/dsl2wup/src/dsl2wup/bus.py', 'execute_dsl', 1, 4, 5).
python_function('packages/dsl2wup/src/dsl2wup/cli.py', '_main_legacy', 1, 9, 14).
python_function('packages/dsl2wup/src/dsl2wup/cli.py', '_main_subcommand', 1, 9, 15).
python_function('packages/dsl2wup/src/dsl2wup/cli.py', 'main', 1, 4, 2).
python_function('packages/dsl2wup/src/dsl2wup/codec.py', 'encode_text', 1, 2, 2).
python_function('packages/dsl2wup/src/dsl2wup/codec.py', 'roundtrip_text', 1, 3, 5).
python_function('packages/dsl2wup/src/dsl2wup/codec.py', 'encode_protobuf', 1, 1, 1).
python_function('packages/dsl2wup/src/dsl2wup/codec.py', 'decode_protobuf', 1, 1, 1).
python_function('packages/dsl2wup/src/dsl2wup/codegen.py', '_field_type', 1, 3, 3).
python_function('packages/dsl2wup/src/dsl2wup/codegen.py', '_field_line', 3, 10, 5).
python_function('packages/dsl2wup/src/dsl2wup/codegen.py', '_append_model', 2, 4, 13).
python_function('packages/dsl2wup/src/dsl2wup/codegen.py', 'generate_models', 0, 3, 7).
python_function('packages/dsl2wup/src/dsl2wup/codegen.py', 'main', 0, 1, 4).
python_function('packages/dsl2wup/src/dsl2wup/events.py', 'default_event_store', 1, 2, 3).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', 'split_command', 1, 4, 3).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', 'pick_flag', 2, 3, 2).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_flag_values', 2, 3, 2).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_query', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_validate', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_resolve', 2, 1, 2).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_health', 2, 3, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_patch', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_map', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_init', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_generate', 2, 2, 2).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_sync', 2, 3, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_adopt', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_endpoints', 2, 2, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_status', 2, 4, 1).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', '_parse_init_cli', 2, 4, 3).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', 'parse_line', 1, 3, 4).
python_function('packages/dsl2wup/src/dsl2wup/grammar.py', 'to_text', 1, 11, 6).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', '_read_content', 1, 1, 3).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', '_project_root', 1, 2, 4).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_map', 1, 7, 13).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_init', 1, 4, 9).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_generate', 1, 4, 6).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_patch', 1, 3, 10).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_sync', 1, 4, 7).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_init_cli', 1, 4, 6).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', '_query_handlers', 0, 1, 0).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', '_command_handlers', 0, 1, 0).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_adopt', 1, 8, 13).
python_function('packages/dsl2wup/src/dsl2wup/handlers/command.py', 'handle_from_tokens', 2, 6, 9).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', '_project_root', 2, 2, 4).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_query', 1, 4, 8).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_validate', 1, 5, 8).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_resolve', 1, 4, 8).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_status', 1, 4, 8).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_endpoints', 1, 4, 5).
python_function('packages/dsl2wup/src/dsl2wup/handlers/query.py', 'handle_health', 1, 5, 9).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', '_canonical_verb', 1, 2, 0).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', '_set_body', 2, 7, 8).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', '_body_to_dict', 2, 10, 3).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'envelope_to_dict', 1, 3, 7).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'encode_protobuf', 1, 1, 6).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'decode_protobuf', 1, 1, 3).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'encode_text_to_protobuf', 1, 2, 3).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'decode_protobuf_to_text', 1, 1, 2).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'result_to_pb', 1, 4, 4).
python_function('packages/dsl2wup/src/dsl2wup/pb_codec.py', 'encode_result_protobuf', 1, 1, 2).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', '_load_schemas', 0, 3, 9).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', 'schema_for_verb', 1, 1, 3).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', 'all_schemas', 0, 1, 2).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', 'validate_command_dict', 1, 3, 7).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', '_schema_verb_for', 1, 1, 2).
python_function('packages/dsl2wup/src/dsl2wup/schema_registry.py', 'validate_schema_registry', 0, 13, 9).
python_function('packages/dsl2wup/tests/test_dsl2wup.py', 'test_validate_schema_registry', 0, 2, 1).
python_function('packages/dsl2wup/tests/test_dsl2wup.py', 'test_parity_text_vs_dict', 1, 3, 3).
python_function('packages/dsl2wup/tests/test_dsl2wup.py', 'test_health_query_offline', 1, 3, 2).
python_function('packages/dsl2wup/tests/test_dsl2wup.py', 'test_init_command', 1, 3, 2).
python_function('packages/dsl2wup/tests/test_generate.py', 'test_generate_fastapi_via_dsl', 1, 4, 3).
python_function('packages/dsl2wup/tests/test_health_paths.py', 'test_health_reads_service_health_json', 1, 3, 6).
python_function('packages/dsl2wup/tests/test_parity.py', 'test_parity_validate_and_query', 1, 12, 6).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', '_fixture_config', 1, 1, 1).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', 'test_parity_dispatch_vs_cli2wup_exec', 1, 3, 3).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', 'test_parity_dispatch_vs_rest2wup', 1, 4, 7).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', 'test_parity_dispatch_vs_uri2wup_run', 1, 3, 5).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', 'test_parity_dispatch_vs_rest_json', 1, 3, 7).
python_function('packages/dsl2wup/tests/test_parity_across_adapters.py', 'test_parity_query_via_uri_decode', 1, 4, 8).
python_function('packages/dsl2wup/tests/test_protobuf.py', 'test_encode_decode_roundtrip', 0, 2, 2).
python_function('packages/dsl2wup/tests/test_protobuf.py', 'test_text_roundtrip', 0, 2, 1).
python_function('packages/dsl2wup/tests/test_protobuf_extended.py', 'test_status_roundtrip', 0, 2, 3).
python_function('packages/dsl2wup/tests/test_protobuf_extended.py', 'test_init_cli_roundtrip', 0, 2, 3).
python_function('packages/dsl2wup/tests/test_protobuf_extended.py', 'test_endpoints_roundtrip', 0, 2, 2).
python_function('packages/dsl2wup/tests/test_validate_schema.py', 'test_validate_schema_registry_passes', 0, 2, 2).
python_function('packages/dsl2wup/tests/test_validate_schema.py', 'test_all_public_verbs_have_schemas', 0, 4, 2).
python_function('packages/mcp2wup/src/mcp2wup/cli.py', 'main', 1, 4, 6).
python_function('packages/mcp2wup/src/mcp2wup/server.py', '_require_fastmcp', 0, 2, 1).
python_function('packages/mcp2wup/src/mcp2wup/server.py', 'create_server', 1, 1, 1).
python_function('packages/mcp2wup/src/mcp2wup/server.py', 'run_server', 0, 1, 2).
python_function('packages/mcp2wup/tests/test_mcp2wup.py', 'test_create_server', 0, 3, 1).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', '_intent', 1, 4, 2).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', '_simple_command', 3, 2, 1).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', '_generated_command', 3, 3, 1).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', '_special_command', 5, 11, 5).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', 'to_dsl', 1, 11, 7).
python_function('packages/nlp2wup/src/nlp2wup/apply.py', 'apply_nl', 1, 4, 8).
python_function('packages/nlp2wup/src/nlp2wup/cli.py', 'main', 1, 9, 11).
python_function('packages/nlp2wup/src/nlp2wup/generate.py', '_extract_template', 1, 3, 1).
python_function('packages/nlp2wup/src/nlp2wup/generate.py', 'generate_from_nl', 1, 1, 2).
python_function('packages/nlp2wup/src/nlp2wup/validate.py', 'validate_wup_config', 1, 1, 1).
python_function('packages/nlp2wup/tests/test_apply.py', 'test_to_dsl_validate', 0, 2, 2).
python_function('packages/nlp2wup/tests/test_apply.py', 'test_to_dsl_map', 0, 2, 2).
python_function('packages/nlp2wup/tests/test_apply.py', 'test_to_dsl_init_cli_is_not_misclassified_as_generate', 0, 2, 2).
python_function('packages/nlp2wup/tests/test_apply.py', 'test_to_dsl_patch_is_not_misclassified_as_query', 0, 2, 2).
python_function('packages/nlp2wup/tests/test_apply.py', 'test_apply_patch_uses_supplied_content_without_fragment_file', 1, 3, 5).
python_function('packages/rest2wup/src/rest2wup/app.py', 'create_app', 0, 1, 24).
python_function('packages/rest2wup/src/rest2wup/cli.py', 'main', 1, 4, 8).
python_function('packages/rest2wup/tests/test_rest2wup.py', 'test_health_endpoint', 0, 3, 4).
python_function('packages/rest2wup/tests/test_rest2wup.py', 'test_post_dsl_health', 0, 2, 3).
python_function('packages/uri2wup/src/uri2wup/cli.py', '_run_resolve', 1, 3, 4).
python_function('packages/uri2wup/src/uri2wup/cli.py', '_run_decode', 1, 1, 2).
python_function('packages/uri2wup/src/uri2wup/cli.py', '_run_query', 1, 4, 4).
python_function('packages/uri2wup/src/uri2wup/cli.py', '_run_dispatch', 1, 5, 5).
python_function('packages/uri2wup/src/uri2wup/cli.py', 'main', 1, 3, 8).
python_function('packages/uri2wup/src/uri2wup/decode.py', '_dict_to_dsl', 1, 7, 5).
python_function('packages/uri2wup/src/uri2wup/decode.py', '_command_from_params', 2, 7, 3).
python_function('packages/uri2wup/src/uri2wup/decode.py', '_block_query', 2, 4, 2).
python_function('packages/uri2wup/src/uri2wup/decode.py', 'decode_uri', 1, 4, 8).
python_function('packages/uri2wup/src/uri2wup/nlp2uri.py', 'nlp2uri', 1, 4, 6).
python_function('packages/uri2wup/src/uri2wup/nlp2uri.py', 'best_uri', 1, 2, 1).
python_function('packages/uri2wup/src/uri2wup/patch.py', '_resolve_config_path', 2, 4, 5).
python_function('packages/uri2wup/src/uri2wup/patch.py', '_replace_at_path', 3, 10, 5).
python_function('packages/uri2wup/src/uri2wup/patch.py', 'patch_uri', 1, 9, 12).
python_function('packages/uri2wup/src/uri2wup/query.py', '_resolve_config_path', 2, 4, 5).
python_function('packages/uri2wup/src/uri2wup/query.py', '_extract_block', 2, 8, 3).
python_function('packages/uri2wup/src/uri2wup/query.py', '_runtime_block', 2, 6, 8).
python_function('packages/uri2wup/src/uri2wup/query.py', '_success', 5, 4, 7).
python_function('packages/uri2wup/src/uri2wup/query.py', '_query_context', 4, 7, 6).
python_function('packages/uri2wup/src/uri2wup/query.py', '_query_data', 3, 5, 6).
python_function('packages/uri2wup/src/uri2wup/query.py', 'query_uri', 1, 4, 7).
python_function('packages/uri2wup/src/uri2wup/uri.py', '_encode', 1, 1, 1).
python_function('packages/uri2wup/src/uri2wup/uri.py', '_decode', 1, 2, 1).
python_function('packages/uri2wup/src/uri2wup/uri.py', 'uri_for_cmd', 1, 7, 4).
python_function('packages/uri2wup/src/uri2wup/uri.py', 'uri_for_block', 0, 7, 3).
python_function('packages/uri2wup/src/uri2wup/uri.py', 'is_wup_uri', 1, 1, 2).
python_function('packages/uri2wup/src/uri2wup/uri.py', 'parse_wup_uri', 1, 7, 6).
python_function('packages/uri2wup/tests/test_decode.py', 'test_decode_cmd_query', 0, 4, 4).
python_function('packages/uri2wup/tests/test_decode.py', 'test_decode_block_defaults_to_query', 0, 3, 3).
python_function('packages/uri2wup/tests/test_patch.py', 'test_patch_nested_value_preserves_sibling_keys', 1, 4, 5).
python_function('packages/uri2wup/tests/test_query.py', 'test_query_config_block', 1, 3, 3).
python_function('packages/uri2wup/tests/test_query.py', 'test_query_nested_config_value', 1, 3, 3).
python_function('scripts/run_probe_smoke.py', 'print_probe_plan', 1, 6, 5).
python_function('scripts/run_probe_smoke.py', 'run_live_http_probes', 2, 4, 3).
python_function('scripts/run_probe_smoke.py', 'run_quick_testql_dryrun', 2, 3, 3).
python_function('scripts/run_probe_smoke.py', 'print_service_health', 1, 2, 5).
python_function('scripts/run_probe_smoke.py', 'check_manifest_stale_probes', 1, 2, 3).
python_function('scripts/run_probe_smoke.py', 'main', 0, 3, 12).
python_function('tests/test_aql.py', '_sample', 1, 1, 2).
python_function('tests/test_aql.py', '_check', 2, 1, 3).
python_function('tests/test_aql.py', 'test_parse_exists', 0, 2, 1).
python_function('tests/test_aql.py', 'test_parse_length_and_severity', 0, 2, 1).
python_function('tests/test_aql.py', 'test_parse_errors', 1, 1, 3).
python_function('tests/test_aql.py', 'test_passing_rules', 2, 2, 2).
python_function('tests/test_aql.py', 'test_failing_rules', 2, 2, 2).
python_function('tests/test_aql.py', 'test_violation_carries_severity', 1, 2, 4).
python_function('tests/test_aql.py', 'test_nested_and_indexed_paths', 1, 3, 1).
python_function('tests/test_aql.py', 'test_missing_file', 1, 2, 3).
python_function('tests/test_aql.py', 'test_yaml_file', 1, 2, 3).
python_function('tests/test_aql.py', 'test_bus_integration', 1, 2, 6).
python_function('tests/test_assistant.py', 'test_framework_detection_fastapi', 0, 2, 6).
python_function('tests/test_assistant.py', 'test_framework_detection_flask', 0, 2, 6).
python_function('tests/test_assistant.py', 'test_framework_detection_none', 0, 2, 5).
python_function('tests/test_assistant.py', 'test_auto_detect_services_fastapi', 0, 5, 9).
python_function('tests/test_assistant.py', 'test_detect_service_type', 0, 6, 5).
python_function('tests/test_assistant.py', 'test_validate_config_success', 0, 2, 10).
python_function('tests/test_assistant.py', 'test_validate_config_issues', 0, 6, 6).
python_function('tests/test_assistant.py', 'test_generate_suggestions', 0, 6, 7).
python_function('tests/test_assistant.py', 'test_quick_setup', 0, 6, 11).
python_function('tests/test_auto_detection.py', 'test_cli_scanner_detects_from_pyproject_toml', 0, 4, 7).
python_function('tests/test_auto_detection.py', 'test_cli_scanner_detects_from_setup_py', 0, 5, 7).
python_function('tests/test_auto_detection.py', 'test_cli_scanner_no_cli_packages', 0, 2, 7).
python_function('tests/test_auto_detection.py', 'test_cli_config_generator_creates_shell_service', 0, 5, 9).
python_function('tests/test_auto_detection.py', 'test_cli_config_generator_web_project_uses_default', 0, 4, 6).
python_function('tests/test_auto_detection.py', 'test_auto_generate_config_detects_cli', 0, 4, 7).
python_function('tests/test_auto_detection.py', 'test_auto_generate_config_web_uses_default', 0, 3, 6).
python_function('tests/test_bootstrap.py', 'test_watchdog_preflight_reports_signal', 1, 3, 3).
python_function('tests/test_bootstrap.py', 'test_main_stops_before_importing_cli_on_failed_watch_preflight', 2, 3, 3).
python_function('tests/test_cli_bridge.py', 'test_bridge_init', 1, 3, 3).
python_function('tests/test_cli_bridge.py', 'test_bridge_map_deps', 1, 3, 4).
python_function('tests/test_cli_bridge.py', 'test_bridge_validate', 1, 2, 3).
python_function('tests/test_cli_filtering.py', 'test_filter_scenarios_web_service_excludes_cli_scenarios', 0, 4, 15).
python_function('tests/test_cli_filtering.py', 'test_filter_scenarios_shell_service_only_cli_scenarios', 0, 4, 15).
python_function('tests/test_cli_filtering.py', 'test_filter_scenarios_auto_service_all_scenarios', 0, 4, 15).
python_function('tests/test_cli_filtering.py', 'test_score_scenario_cli_requires_exact_match', 0, 3, 12).
python_function('tests/test_cli_filtering.py', 'test_score_scenario_non_cli_uses_original_scoring', 0, 2, 12).
python_function('tests/test_cli_filtering.py', 'test_scenario_matches_type', 0, 6, 11).
python_function('tests/test_control.py', 'test_dispatch_validate_shim', 1, 3, 3).
python_function('tests/test_discovery_adapters.py', '_write', 3, 1, 2).
python_function('tests/test_discovery_adapters.py', 'test_adapter_detects_and_discovers', 2, 4, 6).
python_function('tests/test_discovery_adapters.py', 'test_mapper_builds_nonempty_deps', 2, 4, 7).
python_function('tests/test_discovery_adapters.py', 'test_auto_mode_prefers_specific_framework', 1, 2, 4).
python_function('tests/test_discovery_adapters.py', 'test_no_endpoints_for_plain_project', 1, 2, 4).
python_function('tests/test_discovery_adapters.py', 'test_endpoints_deduplicated', 1, 2, 5).
python_function('tests/test_e2e.py', 'run_wup_command', 5, 1, 5).
python_function('tests/test_endpoints_init_cli.py', '_write_scenario', 2, 1, 3).
python_function('tests/test_endpoints_init_cli.py', 'test_discover_testql_endpoints', 1, 3, 3).
python_function('tests/test_endpoints_init_cli.py', 'test_endpoints_via_bus', 1, 3, 3).
python_function('tests/test_endpoints_init_cli.py', 'test_init_cli_via_bus', 1, 4, 5).
python_function('tests/test_endpoints_init_cli.py', 'test_setup_cli_project_core', 1, 3, 3).
python_function('tests/test_genericity.py', '_dc', 2, 1, 1).
python_function('tests/test_genericity.py', 'test_express_ts_endpoints_discovered', 1, 4, 6).
python_function('tests/test_genericity.py', 'test_infer_service_uses_services_dir', 1, 2, 3).
python_function('tests/test_genericity.py', 'test_to_dict_handles_service_without_endpoints', 1, 4, 5).
python_function('tests/test_genericity.py', 'test_docker_map_default_is_generic', 0, 2, 2).
python_function('tests/test_genericity.py', 'test_docker_map_connect_profile_opt_in', 0, 2, 2).
python_function('tests/test_genericity.py', 'test_docker_map_user_rules', 0, 2, 2).
python_function('tests/test_genericity.py', 'test_docker_map_generic_token_match', 0, 2, 2).
python_function('tests/test_genericity.py', 'test_reject_prefixes_generic_by_default', 0, 3, 4).
python_function('tests/test_genericity.py', 'test_reject_prefixes_connect_profile_opt_in', 0, 3, 4).
python_function('tests/test_genericity.py', 'test_reject_prefixes_explicit_override', 0, 2, 2).
python_function('tests/test_genericity.py', '_prefix_matches', 2, 2, 6).
python_function('tests/test_genericity.py', 'test_service_prefix_generic_default', 0, 3, 2).
python_function('tests/test_genericity.py', 'test_service_prefix_connect_profile', 0, 2, 2).
python_function('tests/test_genericity.py', 'test_service_prefix_custom', 0, 3, 2).
python_function('tests/test_genericity.py', 'test_config_roundtrips_docker_service_map', 0, 3, 1).
python_function('tests/test_health_summary_passed.py', 'test_health_summary_all_passed_parser', 0, 3, 1).
python_function('tests/test_health_summary_passed.py', 'test_fleet_health_nonzero_exit_all_passed_counts_as_up', 0, 4, 15).
python_function('tests/test_monitoring_manifest.py', 'test_discover_docker_compose', 0, 4, 5).
python_function('tests/test_monitoring_manifest.py', 'test_patch_and_load_monitoring_block', 0, 7, 13).
python_function('tests/test_multi_project.py', '_make_project', 3, 1, 2).
python_function('tests/test_multi_project.py', '_watcher', 2, 1, 5).
python_function('tests/test_multi_project.py', 'test_detect_watch_paths_uses_existing_dirs', 1, 4, 2).
python_function('tests/test_multi_project.py', 'test_detect_watch_paths_falls_back_when_nothing_matches', 1, 2, 1).
python_function('tests/test_multi_project.py', 'test_detect_watch_paths_backend_frontend', 1, 3, 2).
python_function('tests/test_multi_project.py', 'test_default_config_watches_only_real_dirs', 1, 2, 2).
python_function('tests/test_multi_project.py', 'test_project_dotenv_is_resolved_without_cross_project_leakage', 2, 7, 4).
python_function('tests/test_multi_project.py', 'test_discover_finds_subprojects', 1, 3, 3).
python_function('tests/test_multi_project.py', 'test_discover_skips_vendor_and_hidden', 1, 3, 2).
python_function('tests/test_multi_project.py', 'test_resolve_paths_dedupes', 1, 2, 4).
python_function('tests/test_multi_project.py', 'test_prepare_observer_none_when_no_valid_paths', 1, 2, 2).
python_function('tests/test_multi_project.py', 'test_multi_watcher_returns_false_when_all_invalid', 1, 2, 3).
python_function('tests/test_multi_project.py', 'test_multi_watcher_starts_observers_for_valid_projects', 1, 7, 11).
python_function('tests/test_oql.py', '_project', 1, 1, 5).
python_function('tests/test_oql.py', 'test_parse_minimal', 0, 2, 1).
python_function('tests/test_oql.py', 'test_parse_full', 0, 5, 2).
python_function('tests/test_oql.py', 'test_parse_operator_without_spaces', 0, 2, 2).
python_function('tests/test_oql.py', 'test_parse_errors', 1, 1, 3).
python_function('tests/test_oql.py', 'test_filter_equals', 1, 2, 3).
python_function('tests/test_oql.py', 'test_filter_not_equals', 1, 2, 3).
python_function('tests/test_oql.py', 'test_contains_operator', 1, 2, 3).
python_function('tests/test_oql.py', 'test_since_filters_old_events', 1, 2, 3).
python_function('tests/test_oql.py', 'test_limit', 1, 2, 4).
python_function('tests/test_oql.py', 'test_numeric_comparison', 1, 2, 5).
python_function('tests/test_oql.py', 'test_missing_files_return_empty', 1, 2, 2).
python_function('tests/test_oql.py', 'test_bus_integration', 1, 2, 5).
python_function('tests/test_planfile_reporter_dedupe.py', '_reporter', 1, 1, 2).
python_function('tests/test_planfile_reporter_dedupe.py', '_seed_dedupe', 3, 1, 4).
python_function('tests/test_planfile_reporter_dedupe.py', 'test_open_ticket_still_mutes_recurrence', 2, 2, 6).
python_function('tests/test_planfile_reporter_dedupe.py', 'test_closed_ticket_refiles_fresh_ticket', 2, 3, 11).
python_function('tests/test_planfile_reporter_dedupe.py', 'test_show_error_keeps_muting_conservatively', 2, 2, 5).
python_function('tests/test_probe_mutex.py', '_minimal_watcher', 0, 1, 7).
python_function('tests/test_probe_mutex.py', 'test_periodic_probe_skipped_when_watch_lock_held', 0, 3, 7).
python_function('tests/test_service_inference.py', 'test_infer_service_with_empty_paths_uses_configured_services', 0, 2, 11).
python_function('tests/test_service_inference.py', 'test_infer_service_with_explicit_paths_matches_path_patterns', 0, 2, 11).
python_function('tests/test_service_inference.py', 'test_infer_service_with_auto_detection_matches_name_segments', 0, 2, 11).
python_function('tests/test_service_inference.py', 'test_infer_service_returns_none_for_unmatched_files', 0, 2, 11).
python_function('tests/test_service_inference.py', 'test_infer_service_with_duplicate_service_names', 0, 2, 11).
python_function('tests/test_service_inference.py', 'test_file_change_uses_configured_services_when_inference_fails', 0, 2, 12).
python_function('tests/test_status_data.py', 'test_collect_status_snapshot', 1, 4, 5).
python_function('tests/test_status_data.py', 'test_status_via_bus', 1, 3, 2).
python_function('tests/test_sync.py', '_minimal_config', 1, 1, 2).
python_function('tests/test_sync.py', 'test_sync_writes_manifest', 1, 3, 4).
python_function('tests/test_sync.py', 'test_sync_merge_endpoints_flag', 1, 3, 3).
python_function('tests/test_testql_monitor.py', 'test_parse_scenario_probes_full_url', 0, 5, 9).
python_function('tests/test_testql_monitor.py', 'test_hardware_identify_and_peripheral_status_are_live_probes', 0, 3, 2).
python_function('tests/test_testql_monitor.py', 'test_firmware_plugin_health_catalog_not_periodic_live_probe', 0, 9, 11).
python_function('tests/test_testql_monitor.py', 'test_connect_api_paths_rejection_is_opt_in', 0, 4, 4).
python_function('tests/test_testql_monitor.py', 'test_connect_health_on_8103_not_assigned_to_backend', 0, 2, 3).
python_function('tests/test_testql_monitor.py', 'test_assign_firmware_service', 0, 2, 3).
python_function('tests/test_testql_monitor.py', 'test_monitor_merges_config_and_service_map', 0, 5, 11).
python_function('tests/test_testql_monitor.py', 'test_firmware_live_probe_prefers_oqlos_8202', 0, 2, 2).
python_function('tests/test_testql_monitor.py', 'test_probes_for_service_ignores_non_health_extra_paths', 0, 3, 9).
python_function('tests/test_testql_monitor.py', 'test_live_probe_failure_updates_health', 0, 4, 14).
python_function('tests/test_testql_watcher.py', 'test_process_changed_file_creates_track_on_failure', 0, 5, 16).
python_function('tests/test_testql_watcher.py', 'test_browser_event_file_is_written_without_service_url', 0, 5, 11).
python_function('tests/test_testql_watcher.py', 'test_config_endpoints_use_base_url_from_yaml_config', 0, 3, 9).
python_function('tests/test_testql_watcher.py', 'test_config_endpoints_use_base_url_from_env_when_yaml_missing', 0, 3, 11).
python_function('tests/test_testql_watcher.py', 'test_service_health_transitions_are_persisted', 0, 13, 15).
python_function('tests/test_testql_watcher.py', 'test_planfile_reporter_creates_deduped_ticket', 1, 11, 9).
python_function('tests/test_testql_watcher.py', 'test_planfile_reporter_clears_dedupe_after_recovery', 1, 3, 10).
python_function('tests/test_testql_watcher.py', 'test_planfile_reporter_retries_without_files_for_old_planfile_cli', 1, 6, 9).
python_function('tests/test_testql_watcher.py', 'test_health_transition_creates_planfile_ticket', 1, 1, 13).
python_function('tests/test_testql_watcher.py', 'test_normalize_fleet_health_entry_down_to_degraded', 0, 2, 14).
python_function('tests/test_testql_watcher.py', 'test_fleet_health_scenario_non_strict_records_degraded_not_down', 0, 4, 16).
python_function('tests/test_testql_watcher.py', 'test_visual_differ_disabled_by_default', 0, 4, 11).
python_function('tests/test_testql_watcher.py', 'test_visual_differ_initialized_when_enabled', 0, 4, 9).
python_function('tests/test_testql_watcher.py', 'test_get_config_endpoints_for_service_keeps_connect_pages_on_frontend', 0, 5, 10).
python_function('tests/test_testql_watcher.py', 'test_quick_pass_actions_prefer_config_endpoints_for_visual_diff', 0, 2, 14).
python_function('tests/test_testql_watcher.py', 'test_quick_interrupt_does_not_create_failure_track', 0, 2, 17).
python_function('tests/test_visual_diff_periodic_skip.py', '_make_watcher', 1, 1, 3).
python_function('tests/test_visual_diff_periodic_skip.py', 'test_visual_diff_runs_on_file_change_cycles', 1, 2, 2).
python_function('tests/test_visual_diff_periodic_skip.py', 'test_visual_diff_skipped_on_periodic_probe_by_default', 1, 2, 2).
python_function('tests/test_visual_diff_periodic_skip.py', 'test_visual_diff_runs_on_periodic_probe_when_opted_in', 1, 2, 2).
python_function('tests/test_visual_diff_periodic_skip.py', 'test_visual_diff_skipped_when_disabled', 1, 2, 2).
python_function('tests/test_visual_diff_progress.py', '_make_differ', 1, 1, 3).
python_function('tests/test_visual_diff_progress.py', 'test_progress_returned_for_big_scans', 2, 3, 3).
python_function('tests/test_visual_diff_progress.py', 'test_progress_skipped_for_small_scans', 1, 2, 2).
python_function('tests/test_visual_diff_progress.py', 'test_progress_can_be_disabled_via_env', 2, 2, 3).
python_function('tests/test_visual_diff_progress.py', 'test_progress_uses_injected_console', 1, 3, 6).
python_function('tests/test_watch_exclude.py', '_watcher', 0, 1, 4).
python_function('tests/test_watch_exclude.py', 'test_nested_tests_directory_ignored', 0, 2, 3).
python_function('tests/test_watch_exclude.py', 'test_src_file_not_ignored', 0, 2, 3).
python_function('tests/test_watch_exclude.py', 'test_glob_exclude_pattern', 0, 2, 3).
python_function('tests/test_watch_no_paths_exit.py', '_watcher_with_paths', 1, 1, 4).
python_function('tests/test_watch_no_paths_exit.py', 'test_start_watching_returns_false_when_no_valid_paths', 0, 2, 2).
python_function('tests/test_watch_no_paths_exit.py', 'test_start_watching_returns_false_for_explicit_missing_paths', 0, 2, 2).
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
python_function('tests/test_wup_generate.py', 'test_generate_fastapi_config', 1, 5, 2).
python_function('tests/test_wup_generate.py', 'test_generate_refuses_existing_without_overwrite', 1, 2, 2).
python_function('wup/__init__.py', '__getattr__', 1, 2, 1).
python_function('wup/anomaly_detector.py', 'quick_scan', 2, 2, 3).
python_function('wup/anomaly_detector.py', 'scan_yaml_changes', 2, 1, 3).
python_function('wup/aql.py', '_resolve_path', 2, 13, 9).
python_function('wup/aql.py', '_split_severity', 1, 4, 4).
python_function('wup/aql.py', '_tokenize', 1, 4, 6).
python_function('wup/aql.py', '_rule_selector', 1, 4, 4).
python_function('wup/aql.py', '_predicate_rule', 6, 14, 9).
python_function('wup/aql.py', 'parse_rule', 1, 3, 6).
python_function('wup/aql.py', '_coerce_number', 1, 2, 1).
python_function('wup/aql.py', '_compare', 3, 4, 2).
python_function('wup/aql.py', '_length_of', 1, 2, 2).
python_function('wup/aql.py', '_type_name', 1, 7, 1).
python_function('wup/aql.py', '_passes', 2, 11, 6).
python_function('wup/aql.py', 'register_aql', 2, 2, 3).
python_function('wup/assistant.py', 'main', 0, 1, 5).
python_function('wup/assistant_discovery.py', 'detect_framework', 1, 7, 4).
python_function('wup/assistant_discovery.py', 'auto_detect_services', 2, 7, 8).
python_function('wup/assistant_discovery.py', 'detect_service_type', 2, 11, 5).
python_function('wup/assistant_validator.py', 'validate_config', 2, 9, 3).
python_function('wup/assistant_validator.py', 'generate_suggestions', 1, 6, 2).
python_function('wup/bootstrap.py', '_watchdog_preflight', 0, 5, 3).
python_function('wup/bootstrap.py', 'main', 1, 6, 5).
python_function('wup/cli.py', '_load_watch_config', 4, 4, 3).
python_function('wup/cli.py', '_print_watch_header', 5, 3, 1).
python_function('wup/cli.py', '_refresh_monitoring_manifest', 3, 3, 3).
python_function('wup/cli.py', '_create_watcher', 12, 2, 5).
python_function('wup/cli.py', '_is_project_dir', 1, 2, 2).
python_function('wup/cli.py', '_discover_projects', 1, 6, 5).
python_function('wup/cli.py', '_resolve_project_paths', 2, 8, 9).
python_function('wup/cli.py', '_build_project_watcher', 2, 9, 11).
python_function('wup/cli.py', 'watch', 15, 13, 14).
python_function('wup/cli.py', '_auto_generate_config', 2, 3, 9).
python_function('wup/cli.py', 'map_deps', 4, 12, 16).
python_function('wup/cli.py', '_add_failing_services_lines', 4, 13, 10).
python_function('wup/cli.py', '_add_delta_events_lines', 5, 14, 10).
python_function('wup/cli.py', '_add_monitoring_manifest_lines', 3, 11, 11).
python_function('wup/cli.py', '_add_visual_diff_lines', 5, 9, 7).
python_function('wup/cli.py', '_build_status_panel', 9, 1, 9).
python_function('wup/cli.py', 'status', 7, 8, 18).
python_function('wup/cli.py', 'oql', 3, 11, 21).
python_function('wup/cli.py', 'aql', 3, 9, 11).
python_function('wup/cli.py', 'init', 2, 5, 11).
python_function('wup/cli.py', 'testql_endpoints', 3, 6, 16).
python_function('wup/cli.py', 'sync_testql', 4, 10, 19).
python_function('wup/cli.py', 'assistant', 3, 8, 13).
python_function('wup/cli.py', 'version', 0, 1, 2).
python_function('wup/cli.py', 'init_cli', 5, 9, 13).
python_function('wup/cli_bridge.py', '_result', 2, 3, 3).
python_function('wup/cli_bridge.py', '_guard', 2, 3, 4).
python_function('wup/cli_bridge.py', 'run_map_deps', 0, 2, 15).
python_function('wup/cli_bridge.py', 'run_init', 0, 1, 9).
python_function('wup/cli_bridge.py', 'run_sync', 0, 1, 2).
python_function('wup/cli_bridge.py', 'run_generate', 0, 2, 2).
python_function('wup/cli_bridge.py', 'run_validate', 0, 1, 2).
python_function('wup/cli_bridge.py', 'run_status', 0, 3, 3).
python_function('wup/cli_bridge.py', 'run_endpoints', 0, 1, 2).
python_function('wup/cli_bridge.py', 'run_init_cli', 0, 1, 2).
python_function('wup/config.py', 'find_config_file', 1, 3, 1).
python_function('wup/config.py', '_read_dotenv', 1, 10, 6).
python_function('wup/config.py', '_load_dotenv', 2, 3, 3).
python_function('wup/config.py', 'load_config', 2, 5, 9).
python_function('wup/config.py', '_parse_project_config', 1, 2, 3).
python_function('wup/config.py', '_parse_watch_config', 1, 1, 2).
python_function('wup/config.py', '_parse_services_config', 1, 3, 5).
python_function('wup/config.py', '_parse_strategy_config', 1, 1, 2).
python_function('wup/config.py', '_normalize_testql_timeout', 1, 3, 4).
python_function('wup/config.py', '_parse_testql_extra_args', 1, 5, 5).
python_function('wup/config.py', '_normalize_testql_extra_args', 1, 5, 5).
python_function('wup/config.py', '_parse_testql_config', 2, 3, 6).
python_function('wup/config.py', '_parse_visual_diff_config', 2, 7, 7).
python_function('wup/config.py', '_parse_web_config', 2, 2, 3).
python_function('wup/config.py', '_parse_planfile_config', 2, 5, 7).
python_function('wup/config.py', '_parse_anomaly_detection_config', 1, 1, 6).
python_function('wup/config.py', '_parse_semcod_tools_config', 1, 9, 7).
python_function('wup/config.py', 'validate_config', 1, 2, 11).
python_function('wup/config.py', 'detect_watch_paths', 1, 4, 1).
python_function('wup/config.py', 'get_default_config', 1, 1, 6).
python_function('wup/config.py', 'save_config', 2, 1, 11).
python_function('wup/control.py', '_result_dict', 1, 3, 3).
python_function('wup/control.py', 'dispatch_validate', 1, 1, 1).
python_function('wup/control.py', 'dispatch_query', 1, 3, 3).
python_function('wup/control.py', 'dispatch_health', 0, 2, 2).
python_function('wup/control.py', 'dispatch_map', 0, 1, 1).
python_function('wup/control.py', 'dispatch_init', 0, 1, 1).
python_function('wup/control.py', 'dispatch_sync', 0, 2, 1).
python_function('wup/control.py', 'dispatch_generate', 1, 3, 1).
python_function('wup/control.py', 'dispatch_status', 0, 4, 1).
python_function('wup/control.py', 'dispatch_endpoints', 1, 1, 1).
python_function('wup/control.py', 'dispatch_init_cli', 0, 3, 1).
python_function('wup/control.py', 'dispatch_command', 1, 1, 1).
python_function('wup/discovery.py', 'detect_frameworks', 1, 3, 1).
python_function('wup/discovery.py', 'discover_endpoints', 3, 7, 5).
python_function('wup/endpoints.py', 'discover_testql_endpoints', 1, 5, 16).
python_function('wup/generate.py', '_detect_template', 2, 4, 1).
python_function('wup/generate.py', 'generate_wup_config', 1, 8, 15).
python_function('wup/init_cli.py', 'setup_cli_project', 1, 9, 13).
python_function('wup/monitoring_manifest.py', '_parse_port_mapping', 1, 5, 2).
python_function('wup/monitoring_manifest.py', '_load_compose_yaml', 1, 5, 4).
python_function('wup/monitoring_manifest.py', '_extract_healthcheck_test', 1, 6, 4).
python_function('wup/monitoring_manifest.py', '_extract_service_from_spec', 3, 7, 6).
python_function('wup/monitoring_manifest.py', 'discover_docker_compose_services', 1, 7, 10).
python_function('wup/monitoring_manifest.py', '_host_port_from_mapping', 1, 4, 5).
python_function('wup/monitoring_manifest.py', '_connect_profile_rules', 3, 9, 2).
python_function('wup/monitoring_manifest.py', '_map_docker_to_wup_service', 2, 14, 6).
python_function('wup/monitoring_manifest.py', '_probe_row', 1, 2, 0).
python_function('wup/monitoring_manifest.py', '_build_wup_service_dicts', 1, 3, 2).
python_function('wup/monitoring_manifest.py', '_build_docker_rows', 3, 5, 2).
python_function('wup/monitoring_manifest.py', '_build_scenario_rows', 4, 5, 7).
python_function('wup/monitoring_manifest.py', '_artifact_row', 2, 4, 5).
python_function('wup/monitoring_manifest.py', '_semcod_tool_row', 2, 7, 7).
python_function('wup/monitoring_manifest.py', 'discover_semcod_tools', 1, 7, 6).
python_function('wup/monitoring_manifest.py', 'build_monitoring_manifest', 2, 9, 16).
python_function('wup/monitoring_manifest.py', 'manifest_to_yaml_block', 1, 1, 2).
python_function('wup/monitoring_manifest.py', 'patch_wup_yaml_monitoring', 2, 5, 10).
python_function('wup/monitoring_manifest.py', 'load_monitoring_manifest_from_yaml', 1, 9, 8).
python_function('wup/monitoring_manifest.py', '_service_summary_lines', 2, 5, 3).
python_function('wup/monitoring_manifest.py', '_semcod_summary_lines', 1, 5, 5).
python_function('wup/monitoring_manifest.py', 'format_manifest_summary', 1, 7, 9).
python_function('wup/oql.py', '_coerce_number', 1, 2, 1).
python_function('wup/oql.py', '_compare', 3, 14, 4).
python_function('wup/oql.py', '_parse_duration', 1, 2, 6).
python_function('wup/oql.py', '_tokenize', 1, 2, 3).
python_function('wup/oql.py', 'parse', 1, 11, 10).
python_function('wup/oql.py', '_parse_conditions', 3, 7, 5).
python_function('wup/oql.py', 'register_oql', 2, 1, 3).
python_function('wup/paths.py', 'health_state_path', 1, 1, 1).
python_function('wup/paths.py', 'health_events_path', 1, 1, 1).
python_function('wup/status_data.py', '_load_json', 1, 4, 4).
python_function('wup/status_data.py', '_recent_health_events', 2, 7, 9).
python_function('wup/status_data.py', '_summarize_deps', 1, 4, 6).
python_function('wup/status_data.py', '_load_manifest', 1, 4, 2).
python_function('wup/status_data.py', 'collect_status_snapshot', 1, 12, 17).
python_function('wup/sync.py', '_merge_endpoints', 4, 6, 13).
python_function('wup/sync.py', 'sync_testql_manifest', 1, 9, 13).
python_function('wup/testing/handlers/event_handlers.py', 'register_testing_event_handlers', 4, 1, 2).
python_function('wup/testing/handlers/health_handlers.py', 'register_health_handlers', 6, 1, 2).
python_function('wup/testql_monitor.py', 'reject_prefixes_for_config', 1, 3, 4).
python_function('wup/testql_monitor.py', '_parse_api_lines', 2, 3, 6).
python_function('wup/testql_monitor.py', '_parse_shell_curl_lines', 2, 2, 5).
python_function('wup/testql_monitor.py', 'parse_scenario_probes', 1, 2, 4).
python_function('wup/testql_monitor.py', '_extract_base_url', 1, 4, 4).
python_function('wup/testql_monitor.py', '_parse_endpoint_row', 3, 8, 8).
python_function('wup/testql_monitor.py', 'parse_service_map_probes', 1, 6, 8).
python_function('wup/testql_monitor.py', 'is_monitoring_probe', 2, 10, 5).
python_function('wup/testql_monitor.py', '_service_path_patterns', 1, 6, 7).
python_function('wup/testql_monitor.py', '_find_service_by_name', 2, 3, 1).
python_function('wup/testql_monitor.py', '_find_service_by_token', 2, 3, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8101', 1, 1, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8202', 1, 1, 1).
python_function('wup/testql_monitor.py', '_assign_by_port_8100', 2, 2, 3).
python_function('wup/testql_monitor.py', '_assign_by_connect_backend', 2, 4, 3).
python_function('wup/testql_monitor.py', '_assign_http_probe', 4, 8, 6).
python_function('wup/testql_monitor.py', '_assign_by_longest_token', 2, 7, 3).
python_function('wup/testql_monitor.py', '_assign_by_path_prefix', 2, 13, 2).
python_function('wup/testql_monitor.py', 'assign_probe_to_service', 3, 5, 6).
python_function('wup/validate.py', 'validate_wup_file', 1, 8, 8).
python_function('wup/visual_diff.py', '_playwright_available', 0, 3, 0).
python_function('wup/visual_diff.py', '_warn_playwright_missing', 0, 2, 1).
python_function('wup/visual_diff.py', '_chromium_launch_options', 1, 7, 4).
python_function('wup/visual_diff.py', '_fetch_dom_snapshot', 5, 10, 16).
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
python_class('packages/dsl2wup/src/dsl2wup/events.py', 'DslEvent').
python_method('DslEvent', 'to_dict', 0, 1, 1).
python_class('packages/dsl2wup/src/dsl2wup/events.py', 'EventStore').
python_method('EventStore', '__init__', 1, 3, 1).
python_method('EventStore', 'append', 2, 3, 21).
python_method('EventStore', 'replay', 0, 7, 13).
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'AdoptCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'EndpointsCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'GenerateCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'HealthCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'InitCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'InitCliCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'MapCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'PatchCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'QueryCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'ResolveCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'StatusCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'SyncCommand').
python_class('packages/dsl2wup/src/dsl2wup/models.py', 'ValidateCommand').
python_class('packages/dsl2wup/src/dsl2wup/result.py', 'DslResult').
python_method('DslResult', 'to_dict', 0, 1, 0).
python_class('packages/mcp2wup/src/mcp2wup/server.py', 'WupMCPServer').
python_method('WupMCPServer', '__post_init__', 0, 1, 3).
python_method('WupMCPServer', '_register_tools', 0, 1, 12).
python_method('WupMCPServer', 'run', 0, 1, 1).
python_class('packages/nlp2wup/src/nlp2wup/apply.py', 'ApplyResult').
python_method('ApplyResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2wup/src/uri2wup/nlp2uri.py', 'UriHit').
python_method('UriHit', 'to_dict', 0, 1, 0).
python_class('packages/uri2wup/src/uri2wup/patch.py', 'PatchResult').
python_method('PatchResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2wup/src/uri2wup/query.py', 'QueryResult').
python_method('QueryResult', 'to_dict', 0, 1, 0).
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
python_method('TestConfigModels', 'test_testql_config', 0, 5, 2).
python_method('TestConfigModels', 'test_wup_config', 0, 6, 8).
python_method('TestConfigModels', 'test_visual_diff_config_defaults', 0, 14, 1).
python_method('TestConfigModels', 'test_visual_diff_config_custom', 0, 8, 1).
python_class('tests/test_wup.py', 'TestVisualDiffer').
python_method('TestVisualDiffer', 'test_resolve_base_url_from_config', 0, 2, 2).
python_method('TestVisualDiffer', 'test_resolve_base_url_from_env', 1, 2, 3).
python_method('TestVisualDiffer', 'test_resolve_base_url_empty', 1, 2, 3).
python_method('TestVisualDiffer', 'test_chromium_launch_options_uses_env_executable', 2, 3, 4).
python_method('TestVisualDiffer', 'test_page_slug', 0, 3, 1).
python_method('TestVisualDiffer', 'test_pages_for_service_explicit', 0, 2, 5).
python_method('TestVisualDiffer', 'test_pages_for_service_from_endpoints', 0, 3, 5).
python_method('TestVisualDiffer', 'test_looks_like_visual_page_skips_api_health_routes', 0, 4, 1).
python_method('TestVisualDiffer', 'test_pages_for_service_from_endpoints_skips_non_html_probes', 0, 4, 5).
python_method('TestVisualDiffer', 'test_pages_for_service_fallback', 0, 2, 5).
python_method('TestVisualDiffer', 'test_pages_for_service_absolute_url_passthrough', 0, 2, 5).
python_method('TestVisualDiffer', 'test_diff_snapshots_baseline', 0, 2, 1).
python_method('TestVisualDiffer', 'test_diff_snapshots_identical', 0, 4, 1).
python_method('TestVisualDiffer', 'test_diff_snapshots_changed', 0, 3, 1).
python_method('TestVisualDiffer', 'test_run_for_service_disabled_returns_empty', 0, 2, 6).
python_method('TestVisualDiffer', 'test_run_for_service_summarizes_fetch_errors', 1, 6, 10).
python_method('TestVisualDiffer', 'test_check_page_retries_transient_visual_issue', 1, 5, 9).
python_method('TestVisualDiffer', 'test_get_recent_diffs_empty', 0, 2, 4).
python_method('TestVisualDiffer', 'test_get_recent_diffs_filters_by_age', 0, 3, 10).
python_class('tests/test_wup.py', 'TestConfigLoader').
python_method('TestConfigLoader', 'test_get_default_config', 0, 5, 5).
python_method('TestConfigLoader', 'test_save_and_load_config', 0, 5, 12).
python_method('TestConfigLoader', 'test_save_and_load_preserves_every_non_default_section', 0, 6, 12).
python_method('TestConfigLoader', 'test_load_config_from_yaml', 0, 9, 5).
python_method('TestConfigLoader', 'test_load_config_auto_detect', 0, 2, 4).
python_method('TestConfigLoader', 'test_load_config_no_file_returns_default', 0, 3, 4).
python_method('TestConfigLoader', 'test_load_config_invalid_yaml', 0, 1, 5).
python_method('TestConfigLoader', 'test_load_config_missing_project_name', 0, 1, 5).
python_method('TestConfigLoader', 'test_load_config_extra_args_normalization', 0, 2, 4).
python_method('TestConfigLoader', 'test_save_and_load_visual_diff_config', 0, 13, 7).
python_method('TestConfigLoader', 'test_load_config_visual_diff_from_yaml', 0, 17, 4).
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
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_select_scenarios_uses_pinned_scenario', 0, 2, 13).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_uses_config_timeout', 0, 3, 7).
python_method('TestTestQLWatcherConfig', 'test_testql_watcher_without_config_loads_default', 0, 3, 3).
python_class('wup/_ast_detector.py', 'ASTDetector').
python_method('ASTDetector', '__init__', 1, 1, 2).
python_method('ASTDetector', '_collect_import', 1, 2, 0).
python_method('ASTDetector', '_collect_import_from', 1, 3, 1).
python_method('ASTDetector', '_collect_class', 1, 5, 3).
python_method('ASTDetector', '_collect_function', 1, 1, 1).
python_method('ASTDetector', '_extract_ast_info', 1, 6, 11).
python_method('ASTDetector', '_snapshot_path', 1, 1, 2).
python_method('ASTDetector', '_compute_changes', 2, 11, 3).
python_method('ASTDetector', 'detect', 1, 6, 13).
python_class('wup/_base_detector.py', 'BaseDetector').
python_method('BaseDetector', '__init__', 2, 1, 1).
python_method('BaseDetector', 'detect', 1, 1, 0).
python_class('wup/_hash_detector.py', 'HashDetector').
python_method('HashDetector', '__init__', 1, 1, 2).
python_method('HashDetector', '_compute_hash', 1, 1, 3).
python_method('HashDetector', '_snapshot_path', 1, 1, 2).
python_method('HashDetector', 'detect', 1, 5, 9).
python_class('wup/_yaml_detector.py', 'YAMLStructureDetector').
python_method('YAMLStructureDetector', '__init__', 1, 1, 2).
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
python_class('wup/aql.py', 'AQLError').
python_class('wup/aql.py', 'AQLRule').
python_class('wup/aql.py', 'AQLEngine').
python_method('AQLEngine', '__init__', 1, 1, 1).
python_method('AQLEngine', '_load', 2, 3, 3).
python_method('AQLEngine', 'check_file', 2, 11, 14).
python_class('wup/aql.py', 'CheckAQL').
python_class('wup/assistant.py', 'WupAssistant').
python_method('WupAssistant', '__init__', 1, 1, 4).
python_method('WupAssistant', '_dispatch_menu_choice', 2, 3, 3).
python_method('WupAssistant', 'run', 2, 8, 7).
python_method('WupAssistant', '_init_project', 1, 7, 7).
python_method('WupAssistant', '_detect_framework', 0, 1, 1).
python_method('WupAssistant', '_auto_detect_services', 1, 1, 1).
python_method('WupAssistant', '_detect_service_type', 2, 1, 1).
python_method('WupAssistant', '_configure_services', 0, 14, 11).
python_method('WupAssistant', '_add_service_interactive', 0, 11, 6).
python_method('WupAssistant', '_edit_service', 1, 5, 5).
python_method('WupAssistant', '_setup_watch', 0, 7, 7).
python_method('WupAssistant', '_configure_testql', 0, 3, 6).
python_method('WupAssistant', '_setup_web_dashboard', 0, 3, 3).
python_method('WupAssistant', '_setup_visual_diff', 0, 6, 4).
python_method('WupAssistant', '_setup_anomaly_detection', 0, 8, 6).
python_method('WupAssistant', '_review_and_validate', 0, 11, 7).
python_method('WupAssistant', '_validate_config', 0, 1, 1).
python_method('WupAssistant', '_generate_suggestions', 0, 1, 1).
python_method('WupAssistant', '_save_configuration', 0, 3, 10).
python_method('WupAssistant', '_save_draft', 0, 1, 4).
python_method('WupAssistant', '_load_draft', 0, 2, 4).
python_method('WupAssistant', '_config_to_dict', 1, 1, 4).
python_method('WupAssistant', '_quick_setup', 1, 4, 7).
python_class('wup/bus.py', 'Message').
python_class('wup/bus.py', 'Command').
python_class('wup/bus.py', 'Event').
python_class('wup/bus.py', 'Query').
python_class('wup/bus.py', 'EventBus').
python_method('EventBus', '__init__', 0, 1, 0).
python_method('EventBus', 'subscribe', 2, 4, 2).
python_method('EventBus', 'publish', 1, 2, 3).
python_method('EventBus', 'execute', 1, 3, 4).
python_method('EventBus', 'query', 1, 3, 4).
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
python_method('WupWatcher', '_service_name_prefixes', 0, 4, 5).
python_method('WupWatcher', 'infer_service', 1, 12, 11).
python_method('WupWatcher', '_is_coincident_pair', 2, 6, 0).
python_method('WupWatcher', 'detect_service_coincidences', 1, 9, 3).
python_method('WupWatcher', '_services_share_domain', 2, 1, 3).
python_method('WupWatcher', 'get_service_config', 1, 3, 0).
python_method('WupWatcher', 'should_test', 1, 1, 2).
python_method('WupWatcher', 'schedule_quick_test', 1, 3, 4).
python_method('WupWatcher', 'schedule_detail_test', 1, 1, 2).
python_method('WupWatcher', 'process_test_queue_once', 0, 7, 7).
python_method('WupWatcher', 'cpu_ok', 0, 2, 1).
python_method('WupWatcher', 'run_quick_test', 1, 6, 5).
python_method('WupWatcher', 'run_detail_test', 1, 10, 10).
python_method('WupWatcher', 'test_loop', 0, 2, 2).
python_method('WupWatcher', 'should_watch_file', 1, 3, 4).
python_method('WupWatcher', '_path_matches_exclude_pattern', 2, 5, 4).
python_method('WupWatcher', '_is_file_ignored', 1, 11, 3).
python_method('WupWatcher', '_notify_all_configured_services', 1, 4, 4).
python_method('WupWatcher', 'on_file_change', 1, 11, 9).
python_method('WupWatcher', 'build_watched_paths', 0, 6, 6).
python_method('WupWatcher', '_create_and_start_observer', 2, 5, 6).
python_method('WupWatcher', 'start_background_tasks', 0, 1, 0).
python_method('WupWatcher', 'prepare_observer', 1, 5, 7).
python_method('WupWatcher', 'start_watching', 1, 4, 7).
python_method('WupWatcher', 'create_status_table', 0, 3, 10).
python_method('WupWatcher', 'run_with_dashboard', 0, 5, 13).
python_class('wup/core.py', 'WupEventHandler').
python_method('WupEventHandler', '__init__', 1, 1, 2).
python_method('WupEventHandler', 'on_modified', 1, 2, 1).
python_method('WupEventHandler', 'on_created', 1, 2, 1).
python_method('WupEventHandler', 'on_deleted', 1, 2, 1).
python_class('wup/dependency_mapper.py', 'DependencyMapper').
python_method('DependencyMapper', '__init__', 1, 1, 2).
python_method('DependencyMapper', 'build_from_codebase', 1, 6, 6).
python_method('DependencyMapper', '_detect_framework', 0, 2, 2).
python_method('DependencyMapper', '_infer_service', 1, 5, 4).
python_method('DependencyMapper', 'get_endpoints_for_file', 1, 1, 4).
python_method('DependencyMapper', 'get_endpoints_for_service', 1, 1, 1).
python_method('DependencyMapper', 'get_files_for_service', 1, 1, 2).
python_method('DependencyMapper', 'get_service_for_file', 1, 3, 5).
python_method('DependencyMapper', 'to_dict', 0, 2, 4).
python_method('DependencyMapper', 'save', 1, 1, 3).
python_method('DependencyMapper', 'load', 1, 2, 6).
python_method('DependencyMapper', 'build_from_testql_scenarios', 2, 3, 7).
python_class('wup/discovery.py', 'Endpoint').
python_method('Endpoint', 'as_dict', 0, 1, 0).
python_class('wup/discovery.py', 'SourceIndex').
python_method('SourceIndex', '__init__', 1, 1, 1).
python_method('SourceIndex', '_read_ext', 1, 6, 7).
python_method('SourceIndex', 'files', 1, 2, 1).
python_method('SourceIndex', 'contains', 2, 2, 2).
python_class('wup/discovery.py', 'DiscoveryAdapter').
python_method('DiscoveryAdapter', 'detect', 1, 6, 4).
python_method('DiscoveryAdapter', 'scan', 1, 8, 6).
python_class('wup/discovery.py', 'FastAPIAdapter').
python_class('wup/discovery.py', 'FlaskAdapter').
python_class('wup/discovery.py', 'DjangoAdapter').
python_class('wup/discovery.py', 'ExpressAdapter').
python_class('wup/discovery.py', 'FastifyAdapter').
python_class('wup/discovery.py', 'HonoAdapter').
python_class('wup/discovery.py', 'NestJSAdapter').
python_class('wup/discovery.py', 'GoAdapter').
python_class('wup/discovery.py', 'OpenAPIAdapter').
python_method('OpenAPIAdapter', '_load_spec', 1, 4, 5).
python_method('OpenAPIAdapter', 'detect', 1, 6, 4).
python_method('OpenAPIAdapter', 'scan', 1, 8, 10).
python_class('wup/event_store.py', 'EventStore').
python_method('EventStore', '__init__', 1, 1, 1).
python_method('EventStore', 'append', 1, 2, 8).
python_method('EventStore', 'read_all', 0, 4, 5).
python_class('wup/file_watcher/events/file_events.py', 'FileChanged').
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
python_class('wup/models/config.py', 'SemcodToolConfig').
python_class('wup/models/config.py', 'SemcodToolsConfig').
python_class('wup/models/config.py', 'ProjectConfig').
python_class('wup/models/config.py', 'WupConfig').
python_class('wup/models/target.py', 'ServiceTestTarget').
python_class('wup/monitoring_manifest.py', 'DockerComposeService').
python_class('wup/multi.py', 'MultiProjectWatcher').
python_method('MultiProjectWatcher', '__init__', 2, 2, 1).
python_method('MultiProjectWatcher', 'start_watching', 0, 11, 10).
python_class('wup/oql.py', 'OQLError').
python_class('wup/oql.py', 'Condition').
python_method('Condition', 'matches', 1, 1, 2).
python_class('wup/oql.py', 'OQLQuery').
python_class('wup/oql.py', 'OQLEngine').
python_method('OQLEngine', '__init__', 1, 1, 1).
python_method('OQLEngine', '_service_rows', 0, 6, 8).
python_method('OQLEngine', '_event_rows', 0, 5, 7).
python_method('OQLEngine', 'execute', 1, 13, 9).
python_class('wup/oql.py', 'RunOQL').
python_class('wup/planfile_reporter.py', 'PlanfileReporter').
python_method('PlanfileReporter', '__init__', 3, 2, 2).
python_method('PlanfileReporter', 'enabled', 0, 1, 1).
python_method('PlanfileReporter', 'report_failure', 0, 6, 9).
python_method('PlanfileReporter', '_ticket_is_closed', 1, 6, 7).
python_method('PlanfileReporter', 'clear_service_stage', 0, 7, 6).
python_method('PlanfileReporter', '_build_ticket_cmd', 3, 3, 1).
python_method('PlanfileReporter', '_run_planfile', 1, 4, 4).
python_method('PlanfileReporter', '_retry_without_files', 1, 5, 2).
python_method('PlanfileReporter', '_create_ticket', 0, 14, 7).
python_method('PlanfileReporter', '_wait_for_planfile_store_ready', 1, 6, 7).
python_method('PlanfileReporter', '_load_dedupe', 0, 4, 4).
python_method('PlanfileReporter', '_save_dedupe', 1, 1, 3).
python_method('PlanfileReporter', '_fingerprint', 0, 1, 5).
python_method('PlanfileReporter', '_parse_ticket_id', 1, 2, 2).
python_method('PlanfileReporter', '_files_option_unsupported', 1, 3, 1).
python_method('PlanfileReporter', '_ticket_name', 0, 1, 0).
python_method('PlanfileReporter', '_ticket_description', 0, 3, 0).
python_class('wup/testing/events/health_events.py', 'ServiceHealthChanged').
python_class('wup/testing/events/test_results.py', 'ScenarioPassed').
python_class('wup/testing/events/test_results.py', 'ScenarioFailed').
python_class('wup/testing/handlers/event_handlers.py', 'TestResultEventHandler').
python_method('TestResultEventHandler', '__init__', 3, 1, 0).
python_method('TestResultEventHandler', 'handle_test_failed', 1, 5, 8).
python_method('TestResultEventHandler', 'handle_test_passed', 1, 1, 0).
python_class('wup/testing/handlers/health_handlers.py', 'ServiceHealthProjection').
python_method('ServiceHealthProjection', '__init__', 5, 1, 1).
python_method('ServiceHealthProjection', '_load_initial_state', 0, 3, 3).
python_method('ServiceHealthProjection', '_save_state', 0, 1, 3).
python_method('ServiceHealthProjection', 'handle_health_changed', 1, 8, 9).
python_method('ServiceHealthProjection', 'handle_get_health', 1, 2, 1).
python_class('wup/testing/queries/health_queries.py', 'GetServiceHealth').
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
python_method('TestQLMonitor', '__init__', 2, 2, 3).
python_method('TestQLMonitor', '_is_monitoring_probe', 1, 1, 1).
python_method('TestQLMonitor', '_load_dot_env', 0, 7, 6).
python_method('TestQLMonitor', '_build_port_map', 0, 6, 11).
python_method('TestQLMonitor', '_service_map_paths', 0, 3, 3).
python_method('TestQLMonitor', '_add_hardware_usb_module_endpoints', 1, 13, 11).
python_method('TestQLMonitor', '_add_config_endpoints', 1, 11, 8).
python_method('TestQLMonitor', '_add_scenario_probes', 2, 5, 5).
python_method('TestQLMonitor', '_add_service_map_probes', 2, 5, 5).
python_method('TestQLMonitor', 'discover_probes_by_service', 0, 2, 5).
python_method('TestQLMonitor', '_resolve_base_url_for_service', 1, 8, 7).
python_method('TestQLMonitor', '_probeable_url', 2, 4, 2).
python_method('TestQLMonitor', 'probes_for_service', 2, 9, 10).
python_method('TestQLMonitor', '_sort_probes_for_live', 2, 1, 4).
python_method('TestQLMonitor', 'run_probes', 2, 5, 4).
python_method('TestQLMonitor', 'suggested_endpoints_by_service', 0, 5, 6).
python_method('TestQLMonitor', '_resolve_base_url', 0, 4, 3).
python_method('TestQLMonitor', '_join_base', 2, 5, 1).
python_class('wup/testql_watcher.py', 'BrowserNotifier').
python_method('BrowserNotifier', '__init__', 2, 13, 1).
python_method('BrowserNotifier', 'notify', 1, 3, 8).
python_class('wup/testql_watcher.py', 'TestQLWatcher').
python_method('TestQLWatcher', '__init__', 7, 13, 15).
python_method('TestQLWatcher', '_normalize_fleet_health_entry', 0, 7, 9).
python_method('TestQLWatcher', '_load_service_health', 0, 1, 0).
python_method('TestQLWatcher', '_record_health_transition', 0, 6, 5).
python_method('TestQLWatcher', '_tokenize_service', 1, 3, 3).
python_method('TestQLWatcher', '_get_config_endpoints_for_service', 1, 10, 5).
python_method('TestQLWatcher', '_to_full_url_for_service', 2, 5, 2).
python_method('TestQLWatcher', '_resolve_base_url_for_service', 1, 8, 7).
python_method('TestQLWatcher', '_resolve_base_url', 0, 5, 3).
python_method('TestQLWatcher', '_to_full_url', 1, 5, 2).
python_method('TestQLWatcher', '_discover_scenarios', 0, 2, 3).
python_method('TestQLWatcher', 'get_service_config', 1, 3, 0).
python_method('TestQLWatcher', '_score_scenario', 2, 10, 4).
python_method('TestQLWatcher', '_get_scored_scenarios', 3, 4, 2).
python_method('TestQLWatcher', '_get_smoke_fallback', 1, 6, 3).
python_method('TestQLWatcher', '_resolve_scenario_path', 1, 7, 4).
python_method('TestQLWatcher', '_testql_trailing_json_ok', 1, 6, 6).
python_method('TestQLWatcher', '_health_summary_all_passed', 1, 5, 4).
python_method('TestQLWatcher', '_resolve_stage_config', 2, 6, 1).
python_method('TestQLWatcher', '_filter_connect_scenario', 1, 4, 2).
python_method('TestQLWatcher', '_select_scenarios_for_service', 1, 9, 9).
python_method('TestQLWatcher', '_filter_scenarios_by_type', 2, 8, 1).
python_method('TestQLWatcher', '_scenario_matches_type', 2, 4, 1).
python_method('TestQLWatcher', '_run_testql', 2, 4, 3).
python_method('TestQLWatcher', '_is_interrupted_result', 1, 4, 1).
python_method('TestQLWatcher', '_write_track', 0, 13, 10).
python_method('TestQLWatcher', '_quick_timeout', 0, 3, 1).
python_method('TestQLWatcher', '_merge_endpoints', 2, 3, 3).
python_method('TestQLWatcher', '_run_scenario_quick', 3, 3, 9).
python_method('TestQLWatcher', '_should_run_visual_diff', 0, 4, 2).
python_method('TestQLWatcher', '_quick_pass_actions', 2, 10, 10).
python_method('TestQLWatcher', '_quick_probe_limit', 1, 3, 1).
python_method('TestQLWatcher', '_quick_probe_timeout', 0, 3, 2).
python_method('TestQLWatcher', '_run_live_http_probes', 2, 6, 7).
python_method('TestQLWatcher', '_try_parse_json_summary', 1, 10, 4).
python_method('TestQLWatcher', '_try_find_line_summary', 1, 7, 4).
python_method('TestQLWatcher', '_summarize_testql_failure', 1, 3, 2).
python_method('TestQLWatcher', '_summarize_health_scenario_failure', 1, 8, 4).
python_method('TestQLWatcher', '_run_fleet_health_scenario', 0, 13, 18).
python_method('TestQLWatcher', '_run_quick_test_no_scenarios', 2, 11, 9).
python_method('TestQLWatcher', '_get_quick_scenarios', 1, 3, 2).
python_method('TestQLWatcher', '_run_quick_scenarios_loop', 3, 3, 1).
python_method('TestQLWatcher', 'run_quick_test', 2, 4, 8).
python_method('TestQLWatcher', '_publish_visual_events', 2, 6, 4).
python_method('TestQLWatcher', 'run_detail_test', 2, 11, 14).
python_method('TestQLWatcher', 'process_test_queue_once', 0, 4, 5).
python_method('TestQLWatcher', 'process_changed_file_once', 1, 4, 5).
python_method('TestQLWatcher', '_run_periodic_probes_once', 0, 6, 6).
python_method('TestQLWatcher', '_start_periodic_probe_thread', 0, 3, 6).
python_method('TestQLWatcher', 'start_background_tasks', 0, 1, 1).
python_class('wup/visual_diff.py', 'VisualDiffer').
python_method('VisualDiffer', '__init__', 2, 2, 3).
python_method('VisualDiffer', '_pages_for_service', 1, 11, 4).
python_method('VisualDiffer', '_categorize_page_result', 7, 7, 6).
python_method('VisualDiffer', '_print_scan_summary', 4, 8, 7).
python_method('VisualDiffer', 'run_for_service', 1, 10, 17).
python_method('VisualDiffer', '_build_progress', 2, 3, 7).
python_method('VisualDiffer', '_check_page', 2, 10, 13).
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
makefile_target('help', 'Default target').
makefile_target('install', 'Installation').
makefile_target('install-dev', '').
makefile_target('test', 'Testing').
makefile_target('test-cov', '').
makefile_target('lint', 'Code quality').
makefile_target('format', '').
makefile_target('clean', 'Utilities').
makefile_target('publish', 'Release helpers').
makefile_target('publish-confirm', '').
makefile_target('publish-test', '').
makefile_target('version', '').

% ── Taskfile Tasks ───────────────────────────────────────
taskfile_task('', 'Watch project for file changes and run WUP regression tests').
taskfile_task('', 'Show dependency map status and configuration').
taskfile_task('', 'Discover monitoring targets and update wup.yaml manifest').
taskfile_task('', 'Verify TestQL scenarios and discover endpoints').
taskfile_task('', 'Build dependency map from codebase').
taskfile_task('', 'Run WUP pytest test suite').

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3.7-plus', 'Model (default: openrouter/qwen/qwen3-coder-next)').
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
sumd_declared_file('Taskfile.yml', 'taskfile').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_interface('web', '').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, 'echo "📦 Installing WUP..."').
sumd_workflow_step('install', 2, 'if command -v uv > /dev/null 2>&1').
sumd_workflow_step('install', 3, 'uv pip install -e .').
sumd_workflow_step('install', 4, 'else \').
sumd_workflow_step('install', 5, 'pip install -e .').
sumd_workflow_step('install', 6, 'fi').
sumd_workflow_step('install', 7, 'echo "✅ Installation completed!"').
sumd_workflow('install-dev', 'manual').
sumd_workflow_step('install-dev', 1, 'echo "📦 Installing WUP with dev dependencies..."').
sumd_workflow_step('install-dev', 2, 'if command -v uv > /dev/null 2>&1').
sumd_workflow_step('install-dev', 3, 'uv pip install -e ".[dev]"').
sumd_workflow_step('install-dev', 4, 'else \').
sumd_workflow_step('install-dev', 5, 'pip install -e ".[dev]"').
sumd_workflow_step('install-dev', 6, 'fi').
sumd_workflow_step('install-dev', 7, 'echo "✅ Dev installation completed!"').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'echo "🧪 Running tests..."').
sumd_workflow_step('test', 2, '.venv/bin/python -m pytest tests/ packages/ -v --tb=short').
sumd_workflow('test-cov', 'manual').
sumd_workflow_step('test-cov', 1, 'echo "🧪 Running tests with coverage..."').
sumd_workflow_step('test-cov', 2, '.venv/bin/python -m pytest tests/ packages/ -v --cov=wup --cov-report=term-missing --cov-report=json').
sumd_workflow('lint', 'manual').
sumd_workflow_step('lint', 1, 'echo "🔍 Running linting with ruff..."').
sumd_workflow_step('lint', 2, '.venv/bin/python -m ruff check wup/').
sumd_workflow_step('lint', 3, '.venv/bin/python -m ruff check tests/').
sumd_workflow_step('lint', 4, '.venv/bin/python -m ruff check packages/').
sumd_workflow('format', 'manual').
sumd_workflow_step('format', 1, 'echo "📝 Formatting code with ruff..."').
sumd_workflow_step('format', 2, '.venv/bin/python -m ruff format wup/').
sumd_workflow_step('format', 3, '.venv/bin/python -m ruff format tests/').
sumd_workflow_step('format', 4, '.venv/bin/python -m ruff format packages/').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'echo "🧹 Cleaning temporary files..."').
sumd_workflow_step('clean', 2, 'find . -type f -name "*.pyc" -delete').
sumd_workflow_step('clean', 3, 'find . -type d -name "__pycache__" -delete').
sumd_workflow('publish', 'manual').
sumd_workflow_step('publish', 1, 'echo "📦 Building release artifacts (no upload)..."').
sumd_workflow_step('publish', 2, 'command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build)').
sumd_workflow_step('publish', 3, 'rm -rf dist/ build/ *.egg-info/').
sumd_workflow_step('publish', 4, '.venv/bin/python -m build').
sumd_workflow_step('publish', 5, '.venv/bin/twine check dist/*').
sumd_workflow_step('publish', 6, 'echo "✅ Release artifacts are valid. Run \'make publish-confirm\' to upload."').
sumd_workflow('publish-confirm', 'manual').
sumd_workflow_step('publish-confirm', 1, 'echo "⚡ Uploading release artifacts to PyPI..."').
sumd_workflow_step('publish-confirm', 2, '.venv/bin/twine upload dist/*').
sumd_workflow('publish-test', 'manual').
sumd_workflow_step('publish-test', 1, 'echo "📦 Publishing to TestPyPI..."').
sumd_workflow_step('publish-test', 2, 'command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build)').
sumd_workflow_step('publish-test', 3, 'rm -rf dist/ build/ *.egg-info/').
sumd_workflow_step('publish-test', 4, '.venv/bin/python -m build').
sumd_workflow_step('publish-test', 5, '.venv/bin/twine upload --repository testpypi dist/*').
sumd_workflow('version', 'manual').
sumd_workflow_step('version', 1, 'echo "📦 Version information..."').
sumd_workflow_step('version', 2, 'cat VERSION').
sumd_workflow_step('version', 3, '.venv/bin/python -c "from importlib.metadata import version').
sumd_workflow('wup:watch', 'manual').
sumd_workflow_step('wup:watch', 1, 'poetry run wup watch').
sumd_workflow('wup:status', 'manual').
sumd_workflow_step('wup:status', 1, 'poetry run wup status').
sumd_workflow('wup:sync', 'manual').
sumd_workflow_step('wup:sync', 1, 'poetry run wup sync-testql . --write').
sumd_workflow('wup:endpoints', 'manual').
sumd_workflow_step('wup:endpoints', 1, 'poetry run wup testql-endpoints').
sumd_workflow('wup:map', 'manual').
sumd_workflow_step('wup:map', 1, 'poetry run wup map-deps').
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `wup.testql_watcher` (`wup/testql_watcher.py`)

```python
class BrowserNotifier:  # Send watcher events to browser-facing service and local file
    def __init__(service_url, events_file)  # CC=13 ⚠
    def notify(payload)  # CC=3
class TestQLWatcher:  # WUP watcher running selective TestQL scenarios for changed s
    def __init__(project_root, scenarios_dir, testql_bin, track_dir, browser_service_url, quick_limit, config)  # CC=13 ⚠
    def _normalize_fleet_health_entry()  # CC=7
    def _load_service_health()  # CC=1
    def _record_health_transition()  # CC=6
    def _tokenize_service(service)  # CC=3
    def _get_config_endpoints_for_service(service)  # CC=10 ⚠
    def _to_full_url_for_service(service, endpoint)  # CC=5
    def _resolve_base_url_for_service(service)  # CC=8
    def _resolve_base_url()  # CC=5
    def _to_full_url(endpoint)  # CC=5
    def _discover_scenarios()  # CC=2
    def get_service_config(service_name)  # CC=3
    def _score_scenario(scenario, tokens)  # CC=10 ⚠
    def _get_scored_scenarios(scenarios, tokens, limit)  # CC=4
    def _get_smoke_fallback(svc_type)  # CC=6
    def _resolve_scenario_path(scenario)  # CC=7
    def _testql_trailing_json_ok(result)  # CC=6
    def _health_summary_all_passed(summary)  # CC=5
    def _resolve_stage_config(service, stage)  # CC=6
    def _filter_connect_scenario(scenarios)  # CC=4
    def _select_scenarios_for_service(service)  # CC=9
    def _filter_scenarios_by_type(scenarios, svc_type)  # CC=8
    def _scenario_matches_type(scenario, svc_type)  # CC=4
    def _run_testql(args, timeout)  # CC=4
    def _is_interrupted_result(result)  # CC=4
    def _write_track()  # CC=13 ⚠
    def _quick_timeout()  # CC=3
    def _merge_endpoints(service, endpoints)  # CC=3
    def _run_scenario_quick(service, scenario, merged_endpoints)  # CC=3
    def _should_run_visual_diff()  # CC=4
    def _quick_pass_actions(service, merged_endpoints)  # CC=10 ⚠
    def _quick_probe_limit(service)  # CC=3
    def _quick_probe_timeout()  # CC=3
    def _run_live_http_probes(service, merged_endpoints)  # CC=6
    def _try_parse_json_summary(blob)  # CC=10 ⚠
    def _try_find_line_summary(blob)  # CC=7
    def _summarize_testql_failure(result)  # CC=3
    def _summarize_health_scenario_failure(result)  # CC=8
    def _run_fleet_health_scenario()  # CC=13 ⚠
    def _run_quick_test_no_scenarios(service, merged_endpoints)  # CC=11 ⚠
    def _get_quick_scenarios(service)  # CC=3
    def _run_quick_scenarios_loop(service, scenarios, merged_endpoints)  # CC=3
    def run_quick_test(service, endpoints)  # CC=4
    def _publish_visual_events(service, visual_results)  # CC=6
    def run_detail_test(service, endpoints)  # CC=11 ⚠
    def process_test_queue_once()  # CC=4
    def process_changed_file_once(file_path)  # CC=4
    def _run_periodic_probes_once()  # CC=6
    def _start_periodic_probe_thread()  # CC=3
    def start_background_tasks()  # CC=1
```

### `wup.testql_monitor` (`wup/testql_monitor.py`)

```python
def reject_prefixes_for_config(config)  # CC=3, fan=4
def _parse_api_lines(content, source)  # CC=3, fan=6
def _parse_shell_curl_lines(content, source)  # CC=2, fan=5
def parse_scenario_probes(scenario_path)  # CC=2, fan=4
def _extract_base_url(data)  # CC=4, fan=4
def _parse_endpoint_row(row, base_url, source)  # CC=8, fan=8
def parse_service_map_probes(map_path)  # CC=6, fan=8
def is_monitoring_probe(probe, reject_prefixes)  # CC=10, fan=5 ⚠
def _service_path_patterns(services)  # CC=6, fan=7
def _find_service_by_name(services, name)  # CC=3, fan=1
def _find_service_by_token(services, token)  # CC=3, fan=1
def _assign_by_port_8101(services)  # CC=1, fan=1
def _assign_by_port_8202(services)  # CC=1, fan=1
def _assign_by_port_8100(services, path_lower)  # CC=2, fan=3
def _assign_by_connect_backend(services, path_lower)  # CC=4, fan=3
def _assign_http_probe(probe, services, path_lower, port_map)  # CC=8, fan=6
def _assign_by_longest_token(path_lower, services)  # CC=7, fan=3
def _assign_by_path_prefix(path_lower, services)  # CC=13, fan=2 ⚠
def assign_probe_to_service(probe, services, port_map)  # CC=5, fan=6
class ProbeTarget:  # Single HTTP probe derived from TestQL scenarios or service m
    def probe(timeout_s)  # CC=5
class _ProbeAccumulator:  # Deduplicated probe collector for discover_probes_by_service.
    def __init__(services)  # CC=2
    def add(service, probe)  # CC=3
class TestQLMonitor:  # Build and run live probes from TestQL scenarios + WUP config
    def __init__(project_root, config)  # CC=2
    def _is_monitoring_probe(probe)  # CC=1
    def _load_dot_env()  # CC=7
    def _build_port_map()  # CC=6
    def _service_map_paths()  # CC=3
    def _add_hardware_usb_module_endpoints(accumulator)  # CC=13 ⚠
    def _add_config_endpoints(accumulator)  # CC=11 ⚠
    def _add_scenario_probes(accumulator, port_map)  # CC=5
    def _add_service_map_probes(accumulator, port_map)  # CC=5
    def discover_probes_by_service()  # CC=2
    def _resolve_base_url_for_service(service)  # CC=8
    def _probeable_url(path, base)  # CC=4
    def probes_for_service(service, extra_paths)  # CC=9
    def _sort_probes_for_live(probes, service)  # CC=1
    def run_probes(service, probes)  # CC=5
    def suggested_endpoints_by_service()  # CC=5
    def _resolve_base_url()  # CC=4
    def _join_base(base, path)  # CC=5
```

### `wup.core` (`wup/core.py`)

```python
class WupWatcher:  # Intelligent file watcher for regression testing.
    def __init__(project_root, deps_file, cpu_throttle, debounce_seconds, test_cooldown_seconds, config)  # CC=1
    def _to_relative_path(file_path)  # CC=2
    def _service_name_prefixes()  # CC=4
    def infer_service(file_path)  # CC=12 ⚠
    def _is_coincident_pair(type_a, type_b)  # CC=6
    def detect_service_coincidences(changed_service)  # CC=9
    def _services_share_domain(service1, service2)  # CC=1
    def get_service_config(service_name)  # CC=3
    def should_test(service)  # CC=1
    def schedule_quick_test(service)  # CC=3
    def schedule_detail_test(service)  # CC=1
    def process_test_queue_once()  # CC=7
    def cpu_ok()  # CC=2
    def run_quick_test(target)  # CC=6
    def run_detail_test(target)  # CC=10 ⚠
    def test_loop()  # CC=2
    def should_watch_file(file_path)  # CC=3
    def _path_matches_exclude_pattern(rel_path, pattern)  # CC=5
    def _is_file_ignored(rel_path)  # CC=11 ⚠
    def _notify_all_configured_services(rel_path)  # CC=4
    def on_file_change(file_path)  # CC=11 ⚠
    def build_watched_paths()  # CC=6
    def _create_and_start_observer(event_handler, watch_paths)  # CC=5
    def start_background_tasks()  # CC=1
    def prepare_observer(watch_paths)  # CC=5
    def start_watching(watch_paths)  # CC=4
    def create_status_table()  # CC=3
    def run_with_dashboard()  # CC=5
class WupEventHandler:  # File system event handler for WUP watcher.
    def __init__(watcher)  # CC=1
    def on_modified(event)  # CC=2
    def on_created(event)  # CC=2
    def on_deleted(event)  # CC=2
```

### `wup.visual_diff` (`wup/visual_diff.py`)

```python
def _playwright_available()  # CC=3, fan=0
def _warn_playwright_missing()  # CC=2, fan=1
def _chromium_launch_options(headless)  # CC=7, fan=4
def _fetch_dom_snapshot(url, max_depth, headless, error_selectors, page_settle_ms)  # CC=10, fan=16 ⚠
def _detect_content_issues(snapshot, cfg)  # CC=6, fan=5
def _page_slug(url)  # CC=2, fan=3
def _short_url(url)  # CC=3, fan=1
def _compact_error_message(message, max_len)  # CC=3, fan=3
def _sample_list(items, limit)  # CC=3, fan=2
def _looks_like_visual_page(url)  # CC=7, fan=4
def _snapshot_path(snapshot_dir, service, url)  # CC=1, fan=2
def _load_snapshot(file_path)  # CC=3, fan=3
def _save_snapshot(file_path, snapshot)  # CC=1, fan=3
def _node_signature(node, depth)  # CC=3, fan=3
def _flatten(node, depth, max_depth)  # CC=4, fan=4
def _diff_snapshots(old, new, max_depth, threshold_added, threshold_removed, threshold_changed)  # CC=11, fan=5 ⚠
def _resolve_base_url(cfg)  # CC=3, fan=2
class VisualDiffer:  # Triggered by TestQLWatcher after a file change.
    def __init__(project_root, cfg)  # CC=2
    def _pages_for_service(target)  # CC=11 ⚠
    def _categorize_page_result(service, url, result, ok_urls, new_urls, error_results, pending_notices)  # CC=7
    def _print_scan_summary(service, ok_urls, new_urls, error_results)  # CC=8
    def run_for_service(target)  # CC=10 ⚠
    def _build_progress(service, total)  # CC=3
    def _check_page(service, url)  # CC=10 ⚠
    def _write_diff_event(service, url, result)  # CC=1
    def get_recent_diffs(seconds)  # CC=7
```

### `wup.cli` (`wup/cli.py`)

```python
def _load_watch_config(project_path, config_path, probe_interval, mode)  # CC=4, fan=3
def _print_watch_header(wup_config, cpu_throttle, debounce, cooldown, config_path)  # CC=3, fan=1
def _refresh_monitoring_manifest(project_path, wup_config, cfg_path)  # CC=3, fan=3
def _create_watcher(mode, project_path, deps_file, cpu_throttle, debounce, cooldown, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, config)  # CC=2, fan=5
def _is_project_dir(path)  # CC=2, fan=2
def _discover_projects(root)  # CC=6, fan=5
def _resolve_project_paths(projects, discover)  # CC=8, fan=9
def _build_project_watcher(project_path, config_path)  # CC=9, fan=11
def watch(projects, deps_file, cpu_throttle, debounce, cooldown, dashboard, mode, scenarios_dir, testql_bin, browser_service_url, track_dir, quick_limit, probe_interval, discover, config)  # CC=13, fan=14 ⚠
def _auto_generate_config(project_path, mode)  # CC=3, fan=9
def map_deps(project, output, framework, config)  # CC=12, fan=16 ⚠
def _add_failing_services_lines(lines, health_state_path, failed_only, watch)  # CC=13, fan=10 ⚠
def _add_delta_events_lines(lines, health_events_path, delta_seconds, watch, ts)  # CC=14, fan=10 ⚠
def _add_monitoring_manifest_lines(lines, config_path, project_path)  # CC=11, fan=11 ⚠
def _add_visual_diff_lines(lines, wup_config, project_path, delta_seconds, watch)  # CC=9, fan=7
def _build_status_panel(ts, project_path, wup_config, config_path, health_state_path, health_events_path, delta_seconds, failed_only, watch)  # CC=1, fan=9
def status(deps_file, config, delta_seconds, failed_only, watch, interval, json_out)  # CC=8, fan=18
def oql(query, project, json_out)  # CC=11, fan=21 ⚠
def aql(file, rule, json_out)  # CC=9, fan=11
def init(project, output)  # CC=5, fan=11
def testql_endpoints(scenarios_dir, output, testql_bin)  # CC=6, fan=16
def sync_testql(project, write, merge_endpoints, config)  # CC=10, fan=19 ⚠
def assistant(quick, template, project)  # CC=8, fan=13
def version()  # CC=1, fan=2
def init_cli(project, output_config, output_scenarios, merge, infer_args)  # CC=9, fan=13
```

## Call Graph

*331 nodes · 352 edges · 59 modules · CC̄=4.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `show_ci_cd_demo` *(in examples.ci_cd_integration)* | 2 | 1 | 69 | **70** |
| `show_webhook_demo` *(in examples.webhook_notifications)* | 4 | 1 | 68 | **69** |
| `_run_with_mock_services` *(in examples.testql_demo)* | 6 | 2 | 60 | **62** |
| `_parse_visual_diff_config` *(in wup.config)* | 7 | 1 | 49 | **50** |
| `map_deps` *(in wup.cli)* | 12 ⚠ | 0 | 45 | **45** |
| `create_app` *(in packages.rest2wup.src.rest2wup.app)* | 1 | 1 | 42 | **43** |
| `testql_endpoints` *(in wup.cli)* | 6 | 0 | 43 | **43** |
| `sync_testql` *(in wup.cli)* | 10 ⚠ | 0 | 38 | **38** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/wup
# generated in 0.16s
# nodes: 331 | edges: 352 | modules: 59
# CC̄=4.2

HUBS[20]:
  examples.ci_cd_integration.show_ci_cd_demo
    CC=2  in:1  out:69  total:70
  examples.webhook_notifications.show_webhook_demo
    CC=4  in:1  out:68  total:69
  examples.testql_demo._run_with_mock_services
    CC=6  in:2  out:60  total:62
  wup.config._parse_visual_diff_config
    CC=7  in:1  out:49  total:50
  wup.cli.map_deps
    CC=12  in:0  out:45  total:45
  packages.rest2wup.src.rest2wup.app.create_app
    CC=1  in:1  out:42  total:43
  wup.cli.testql_endpoints
    CC=6  in:0  out:43  total:43
  wup.cli.sync_testql
    CC=10  in:0  out:38  total:38
  packages.dsl2wup.src.dsl2wup.events.EventStore.append
    CC=3  in:0  out:33  total:33
  packages.dsl2wup.src.dsl2wup.bus.dispatch
    CC=6  in:16  out:15  total:31
  wup.cli.status
    CC=8  in:0  out:31  total:31
  wup.config._parse_testql_config
    CC=3  in:1  out:29  total:30
  wup.cli._add_delta_events_lines
    CC=14  in:1  out:29  total:30
  packages.dsl2wup.src.dsl2wup.cli._main_subcommand
    CC=9  in:1  out:28  total:29
  wup.init_cli.setup_cli_project
    CC=9  in:2  out:26  total:28
  packages.dsl2wup.src.dsl2wup.grammar.to_text
    CC=11  in:9  out:19  total:28
  wup.endpoints.discover_testql_endpoints
    CC=5  in:2  out:26  total:28
  examples.c2004_monorepo_demo.analyze_monorepo
    CC=2  in:1  out:26  total:27
  examples.visual_diff_demo.demo_snapshot_persistence
    CC=3  in:1  out:26  total:27
  packages.uri2wup.src.uri2wup.query.query_uri
    CC=13  in:3  out:23  total:26

MODULES:
  examples.c2004_monorepo_demo  [5 funcs]
    _analyze_module  CC=3  out:9
    _analyze_module_structure  CC=7  out:10
    _discover_modules  CC=5  out:8
    analyze_monorepo  CC=2  out:26
    main  CC=2  out:2
  examples.ci_cd_integration  [4 funcs]
    generate_github_actions  CC=1  out:9
    generate_gitlab_ci  CC=3  out:10
    main  CC=3  out:7
    show_ci_cd_demo  CC=2  out:69
  examples.testql_demo  [4 funcs]
    _build_mock_services  CC=5  out:4
    _run_with_mock_services  CC=6  out:60
    simulate_testql_analysis  CC=2  out:18
    simulate_with_mock_data  CC=1  out:12
  examples.visual_diff_demo  [8 funcs]
    _make_dom  CC=2  out:1
    demo_config_yaml_round_trip  CC=6  out:16
    demo_diff_algorithm  CC=3  out:16
    demo_disabled_is_noop  CC=2  out:11
    demo_live_page  CC=3  out:14
    demo_page_slug  CC=2  out:6
    demo_snapshot_persistence  CC=3  out:26
    main  CC=2  out:15
  examples.webhook_notifications  [2 funcs]
    main  CC=3  out:7
    show_webhook_demo  CC=4  out:68
  packages.cli2wup.src.cli2wup.cli  [4 funcs]
    _print_result  CC=4  out:6
    _run_command  CC=2  out:2
    _run_script  CC=3  out:4
    run_shell  CC=9  out:12
  packages.dsl2wup.src.dsl2wup.bus  [5 funcs]
    _bytes_to_cmd  CC=3  out:5
    _dispatch_cmd  CC=5  out:12
    dispatch  CC=6  out:15
    execute_dsl  CC=4  out:6
    execute_dsl_line  CC=1  out:1
  packages.dsl2wup.src.dsl2wup.cli  [3 funcs]
    _main_legacy  CC=9  out:20
    _main_subcommand  CC=9  out:28
    main  CC=4  out:2
  packages.dsl2wup.src.dsl2wup.codec  [4 funcs]
    decode_protobuf  CC=1  out:1
    encode_protobuf  CC=1  out:1
    encode_text  CC=2  out:2
    roundtrip_text  CC=3  out:6
  packages.dsl2wup.src.dsl2wup.codegen  [5 funcs]
    _append_model  CC=4  out:15
    _field_line  CC=10  out:7
    _field_type  CC=3  out:5
    generate_models  CC=3  out:11
    main  CC=1  out:4
  packages.dsl2wup.src.dsl2wup.events  [2 funcs]
    append  CC=3  out:33
    default_event_store  CC=2  out:6
  packages.dsl2wup.src.dsl2wup.grammar  [18 funcs]
    _flag_values  CC=3  out:2
    _parse_adopt  CC=2  out:1
    _parse_endpoints  CC=2  out:1
    _parse_generate  CC=2  out:3
    _parse_health  CC=3  out:1
    _parse_init  CC=2  out:1
    _parse_init_cli  CC=4  out:3
    _parse_map  CC=2  out:1
    _parse_patch  CC=2  out:1
    _parse_query  CC=2  out:1
  packages.dsl2wup.src.dsl2wup.handlers.command  [9 funcs]
    _project_root  CC=2  out:4
    _read_content  CC=1  out:3
    handle_from_tokens  CC=6  out:14
    handle_generate  CC=4  out:11
    handle_init  CC=4  out:11
    handle_init_cli  CC=4  out:12
    handle_map  CC=7  out:20
    handle_patch  CC=3  out:13
    handle_sync  CC=4  out:12
  packages.dsl2wup.src.dsl2wup.handlers.query  [7 funcs]
    _project_root  CC=2  out:4
    handle_endpoints  CC=4  out:10
    handle_health  CC=5  out:12
    handle_query  CC=4  out:10
    handle_resolve  CC=4  out:9
    handle_status  CC=4  out:11
    handle_validate  CC=5  out:13
  packages.dsl2wup.src.dsl2wup.pb_codec  [10 funcs]
    _body_to_dict  CC=10  out:3
    _canonical_verb  CC=2  out:0
    _set_body  CC=7  out:13
    decode_protobuf  CC=1  out:3
    decode_protobuf_to_text  CC=1  out:2
    encode_protobuf  CC=1  out:6
    encode_result_protobuf  CC=1  out:2
    encode_text_to_protobuf  CC=2  out:3
    envelope_to_dict  CC=3  out:7
    result_to_pb  CC=4  out:4
  packages.dsl2wup.src.dsl2wup.schema_registry  [6 funcs]
    _load_schemas  CC=3  out:9
    _schema_verb_for  CC=1  out:3
    all_schemas  CC=1  out:2
    schema_for_verb  CC=1  out:3
    validate_command_dict  CC=3  out:7
    validate_schema_registry  CC=13  out:19
  packages.mcp2wup.src.mcp2wup.cli  [1 funcs]
    main  CC=4  out:6
  packages.mcp2wup.src.mcp2wup.server  [4 funcs]
    __post_init__  CC=1  out:3
    _require_fastmcp  CC=2  out:1
    create_server  CC=1  out:1
    run_server  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.apply  [6 funcs]
    _generated_command  CC=3  out:1
    _intent  CC=4  out:2
    _simple_command  CC=2  out:1
    _special_command  CC=11  out:5
    apply_nl  CC=4  out:10
    to_dsl  CC=11  out:11
  packages.nlp2wup.src.nlp2wup.generate  [2 funcs]
    _extract_template  CC=3  out:1
    generate_from_nl  CC=1  out:2
  packages.nlp2wup.src.nlp2wup.validate  [1 funcs]
    validate_wup_config  CC=1  out:1
  packages.rest2wup.src.rest2wup.app  [1 funcs]
    create_app  CC=1  out:42
  packages.rest2wup.src.rest2wup.cli  [1 funcs]
    main  CC=4  out:9
  packages.uri2wup.src.uri2wup.cli  [4 funcs]
    _run_decode  CC=1  out:2
    _run_dispatch  CC=5  out:6
    _run_query  CC=4  out:4
    _run_resolve  CC=3  out:4
  packages.uri2wup.src.uri2wup.decode  [4 funcs]
    _block_query  CC=4  out:2
    _command_from_params  CC=7  out:6
    _dict_to_dsl  CC=7  out:7
    decode_uri  CC=4  out:9
  packages.uri2wup.src.uri2wup.nlp2uri  [2 funcs]
    best_uri  CC=2  out:1
    nlp2uri  CC=4  out:9
  packages.uri2wup.src.uri2wup.patch  [3 funcs]
    _replace_at_path  CC=10  out:11
    _resolve_config_path  CC=4  out:7
    patch_uri  CC=9  out:18
  packages.uri2wup.src.uri2wup.query  [5 funcs]
    _extract_block  CC=8  out:6
    _resolve_config_path  CC=4  out:7
    _runtime_block  CC=6  out:13
    _success  CC=4  out:7
    query_uri  CC=13  out:23
  packages.uri2wup.src.uri2wup.uri  [6 funcs]
    _decode  CC=2  out:1
    _encode  CC=1  out:1
    is_wup_uri  CC=1  out:2
    parse_wup_uri  CC=7  out:14
    uri_for_block  CC=7  out:9
    uri_for_cmd  CC=7  out:13
  scripts.run_probe_smoke  [6 funcs]
    check_manifest_stale_probes  CC=2  out:3
    main  CC=3  out:13
    print_probe_plan  CC=6  out:13
    print_service_health  CC=2  out:6
    run_live_http_probes  CC=4  out:4
    run_quick_testql_dryrun  CC=3  out:4
  wup._ast_detector  [1 funcs]
    _snapshot_path  CC=1  out:3
  wup.aql  [12 funcs]
    check_file  CC=11  out:21
    _coerce_number  CC=2  out:1
    _compare  CC=4  out:3
    _length_of  CC=2  out:2
    _passes  CC=11  out:9
    _predicate_rule  CC=14  out:21
    _resolve_path  CC=13  out:13
    _rule_selector  CC=4  out:6
    _split_severity  CC=4  out:5
    _tokenize  CC=4  out:11
  wup.assistant  [5 funcs]
    _auto_detect_services  CC=1  out:1
    _detect_framework  CC=1  out:1
    _detect_service_type  CC=1  out:1
    _generate_suggestions  CC=1  out:1
    _validate_config  CC=1  out:1
  wup.assistant_discovery  [3 funcs]
    auto_detect_services  CC=7  out:9
    detect_framework  CC=7  out:4
    detect_service_type  CC=11  out:9
  wup.assistant_validator  [2 funcs]
    generate_suggestions  CC=6  out:5
    validate_config  CC=9  out:9
  wup.bootstrap  [2 funcs]
    _watchdog_preflight  CC=5  out:3
    main  CC=6  out:5
  wup.cli  [20 funcs]
    _add_delta_events_lines  CC=14  out:29
    _add_failing_services_lines  CC=13  out:23
    _add_monitoring_manifest_lines  CC=11  out:24
    _add_visual_diff_lines  CC=9  out:18
    _auto_generate_config  CC=3  out:13
    _build_project_watcher  CC=9  out:15
    _build_status_panel  CC=1  out:9
    _create_watcher  CC=2  out:6
    _discover_projects  CC=6  out:7
    _is_project_dir  CC=2  out:2
  wup.cli_bridge  [10 funcs]
    _guard  CC=3  out:6
    _result  CC=3  out:4
    run_endpoints  CC=1  out:2
    run_generate  CC=2  out:2
    run_init  CC=1  out:10
    run_init_cli  CC=1  out:2
    run_map_deps  CC=2  out:21
    run_status  CC=3  out:3
    run_sync  CC=1  out:2
    run_validate  CC=1  out:2
  wup.cli_config_generator  [1 funcs]
    generate  CC=4  out:5
  wup.config  [20 funcs]
    _load_dotenv  CC=3  out:3
    _normalize_testql_extra_args  CC=5  out:10
    _normalize_testql_timeout  CC=3  out:4
    _parse_anomaly_detection_config  CC=1  out:19
    _parse_planfile_config  CC=5  out:15
    _parse_project_config  CC=2  out:5
    _parse_services_config  CC=3  out:23
    _parse_strategy_config  CC=1  out:4
    _parse_testql_config  CC=3  out:29
    _parse_testql_extra_args  CC=5  out:8
  wup.control  [12 funcs]
    _result_dict  CC=3  out:3
    dispatch_command  CC=1  out:1
    dispatch_endpoints  CC=1  out:1
    dispatch_generate  CC=3  out:1
    dispatch_health  CC=2  out:2
    dispatch_init  CC=1  out:1
    dispatch_init_cli  CC=3  out:1
    dispatch_map  CC=1  out:1
    dispatch_query  CC=3  out:5
    dispatch_status  CC=4  out:1
  wup.core  [1 funcs]
    __init__  CC=7  out:18
  wup.dependency_mapper  [2 funcs]
    _detect_framework  CC=2  out:2
    build_from_codebase  CC=6  out:7
  wup.discovery  [2 funcs]
    detect_frameworks  CC=3  out:1
    discover_endpoints  CC=7  out:6
  wup.endpoints  [1 funcs]
    discover_testql_endpoints  CC=5  out:26
  wup.generate  [2 funcs]
    _detect_template  CC=4  out:2
    generate_wup_config  CC=8  out:20
  wup.init_cli  [1 funcs]
    setup_cli_project  CC=9  out:26
  wup.monitoring_manifest  [18 funcs]
    _artifact_row  CC=4  out:5
    _build_docker_rows  CC=5  out:3
    _build_scenario_rows  CC=5  out:8
    _build_wup_service_dicts  CC=3  out:2
    _extract_healthcheck_test  CC=6  out:7
    _extract_service_from_spec  CC=7  out:12
    _load_compose_yaml  CC=5  out:5
    _map_docker_to_wup_service  CC=14  out:11
    _parse_port_mapping  CC=5  out:4
    _semcod_summary_lines  CC=5  out:9
  wup.oql  [9 funcs]
    matches  CC=1  out:2
    _event_rows  CC=5  out:7
    _service_rows  CC=6  out:9
    execute  CC=13  out:12
    _coerce_number  CC=2  out:1
    _compare  CC=14  out:8
    _parse_conditions  CC=7  out:10
    _tokenize  CC=2  out:7
    parse  CC=11  out:19
  wup.paths  [2 funcs]
    health_events_path  CC=1  out:1
    health_state_path  CC=1  out:1
  wup.status_data  [4 funcs]
    _load_json  CC=4  out:4
    _load_manifest  CC=4  out:2
    _summarize_deps  CC=4  out:8
    collect_status_snapshot  CC=12  out:23
  wup.sync  [2 funcs]
    _merge_endpoints  CC=6  out:14
    sync_testql_manifest  CC=9  out:16
  wup.testing.handlers.event_handlers  [1 funcs]
    register_testing_event_handlers  CC=1  out:3
  wup.testing.handlers.health_handlers  [1 funcs]
    register_health_handlers  CC=1  out:3
  wup.testql_monitor  [26 funcs]
    __init__  CC=2  out:3
    _add_config_endpoints  CC=11  out:14
    _add_scenario_probes  CC=5  out:5
    _add_service_map_probes  CC=5  out:5
    _build_port_map  CC=6  out:13
    _is_monitoring_probe  CC=1  out:1
    _resolve_base_url  CC=4  out:6
    _assign_by_connect_backend  CC=4  out:4
    _assign_by_longest_token  CC=7  out:5
    _assign_by_path_prefix  CC=13  out:7
  wup.testql_watcher  [2 funcs]
    __init__  CC=13  out:17
    _get_config_endpoints_for_service  CC=10  out:7
  wup.validate  [1 funcs]
    validate_wup_file  CC=8  out:15
  wup.visual_diff  [22 funcs]
    __init__  CC=2  out:3
    _categorize_page_result  CC=7  out:12
    _check_page  CC=10  out:19
    _pages_for_service  CC=11  out:8
    _print_scan_summary  CC=8  out:13
    _write_diff_event  CC=1  out:6
    run_for_service  CC=10  out:22
    _compact_error_message  CC=3  out:3
    _detect_content_issues  CC=6  out:11
    _diff_snapshots  CC=11  out:15
  wup.web_client  [4 funcs]
    __init__  CC=2  out:2
    send_event  CC=5  out:9
    _normalize  CC=6  out:7
    resolve_endpoint  CC=3  out:3

EDGES:
  packages.rest2wup.src.rest2wup.cli.main → packages.rest2wup.src.rest2wup.app.create_app
  packages.rest2wup.src.rest2wup.app.create_app → packages.dsl2wup.src.dsl2wup.schema_registry.schema_for_verb
  packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri → packages.uri2wup.src.uri2wup.uri.uri_for_block
  packages.uri2wup.src.uri2wup.nlp2uri.best_uri → packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri
  packages.uri2wup.src.uri2wup.uri.uri_for_cmd → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.uri_for_block → packages.uri2wup.src.uri2wup.uri._encode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri._decode
  packages.uri2wup.src.uri2wup.uri.parse_wup_uri → packages.uri2wup.src.uri2wup.uri.is_wup_uri
  packages.nlp2wup.src.nlp2wup.validate.validate_wup_config → wup.validate.validate_wup_file
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.handlers.command.handle_from_tokens
  packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd → packages.dsl2wup.src.dsl2wup.events.default_event_store
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.codec.decode_protobuf
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd → packages.dsl2wup.src.dsl2wup.grammar.parse_line
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.split_command
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._dispatch_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.bus._bytes_to_cmd
  packages.dsl2wup.src.dsl2wup.bus.dispatch → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line → packages.dsl2wup.src.dsl2wup.bus.dispatch
  packages.dsl2wup.src.dsl2wup.bus.execute_dsl → packages.dsl2wup.src.dsl2wup.bus.execute_dsl_line
  packages.dsl2wup.src.dsl2wup.schema_registry.schema_for_verb → packages.dsl2wup.src.dsl2wup.schema_registry._load_schemas
  packages.dsl2wup.src.dsl2wup.schema_registry.all_schemas → packages.dsl2wup.src.dsl2wup.schema_registry._load_schemas
  packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict → packages.dsl2wup.src.dsl2wup.schema_registry.schema_for_verb
  packages.dsl2wup.src.dsl2wup.schema_registry.validate_schema_registry → packages.dsl2wup.src.dsl2wup.schema_registry._load_schemas
  packages.dsl2wup.src.dsl2wup.schema_registry.validate_schema_registry → packages.dsl2wup.src.dsl2wup.schema_registry._schema_verb_for
  packages.dsl2wup.src.dsl2wup.codec.encode_text → packages.dsl2wup.src.dsl2wup.grammar.parse_line
  packages.dsl2wup.src.dsl2wup.codec.encode_text → packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict
  packages.dsl2wup.src.dsl2wup.codec.roundtrip_text → packages.dsl2wup.src.dsl2wup.grammar.parse_line
  packages.dsl2wup.src.dsl2wup.codec.roundtrip_text → packages.dsl2wup.src.dsl2wup.schema_registry.validate_command_dict
  packages.dsl2wup.src.dsl2wup.codec.roundtrip_text → packages.dsl2wup.src.dsl2wup.grammar.to_text
  packages.dsl2wup.src.dsl2wup.codec.encode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec.encode_text_to_protobuf
  packages.dsl2wup.src.dsl2wup.codec.decode_protobuf → packages.dsl2wup.src.dsl2wup.pb_codec.decode_protobuf_to_text
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_query → packages.uri2wup.src.uri2wup.query.query_uri
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_query → packages.dsl2wup.src.dsl2wup.handlers.query._project_root
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_validate → wup.validate.validate_wup_file
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_validate → packages.dsl2wup.src.dsl2wup.handlers.query._project_root
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_resolve → packages.uri2wup.src.uri2wup.nlp2uri.nlp2uri
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_resolve → packages.dsl2wup.src.dsl2wup.handlers.query._project_root
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_status → wup.status_data.collect_status_snapshot
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_status → packages.dsl2wup.src.dsl2wup.handlers.query._project_root
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_endpoints → wup.endpoints.discover_testql_endpoints
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_health → packages.dsl2wup.src.dsl2wup.handlers.query._project_root
  packages.dsl2wup.src.dsl2wup.handlers.query.handle_health → wup.paths.health_state_path
  packages.mcp2wup.src.mcp2wup.cli.main → packages.mcp2wup.src.mcp2wup.server.run_server
  packages.mcp2wup.src.mcp2wup.server.WupMCPServer.__post_init__ → packages.mcp2wup.src.mcp2wup.server._require_fastmcp
  packages.mcp2wup.src.mcp2wup.server.run_server → packages.mcp2wup.src.mcp2wup.server.create_server
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._parse_port_mapping
  wup.monitoring_manifest._extract_service_from_spec → wup.monitoring_manifest._extract_healthcheck_test
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (3)

**`CLI Smoke Tests`**

**`wup Command Tests`**

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**
- assert `test_type == "quick"`
- assert `service_name == "users"`
- assert `inferred == "users"`

## Intent

WUP (What's Up) - Intelligent file watcher for regression testing in large projects
