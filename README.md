# WUP (What's Up)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.73-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$7.24-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-52.4h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $7.2381 (101 commits)
- 👤 **Human dev:** ~$5241 (52.4h @ $100/h, 30min dedup)

Generated on 2026-07-17 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

![PyPI](https://img.shields.io/badge/pypi-wup-blue) ![Version](https://img.shields.io/badge/version-0.2.73-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)

**WUP (What's Up)** - Intelligent file watcher for regression testing in large projects.

WUP monitors file changes and runs intelligent regression tests using a 3-layer approach:
1. **Detection Layer**: File watching with heuristics
2. **Priority Layer**: Quick tests of related services (3 endpoints max)
3. **Detail Layer**: Full tests with blame reports (only on failure)

## Features

- 🎯 **Intelligent Testing**: Only tests related services when files change
- ⚡ **CPU Throttling**: Respects system resources with configurable CPU limits
- 🔄 **3-Layer Architecture**: Quick smoke tests first, detailed tests only on failure
- 📊 **Live Dashboard**: Real-time status monitoring with Rich CLI
- 🔍 **Dependency Mapping**: Automatic detection of files → endpoints → services
- 🚀 **Framework Support**: FastAPI, Flask, Django, Express.js, and more
- 📝 **Blame Reports**: Detailed regression reports with file/line/commit info
- ⚙️ **Configuration System**: Declarative configuration via `wup.yaml` file
- 🎛️ **Per-Service Settings**: Custom test strategies per service
- 🧪 **TestQL Integration**: Native support for TestQL scenarios
- 🔧 **CLI/Shell Automation**: Auto-detection and configuration of CLI tools and shell scripts

## Installation

```bash
# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# 1. Interactive configuration (recommended)
wup assistant

# 2. Or quick auto-setup
wup assistant --quick --template fastapi

# 3. Build dependency map (one-time setup)
wup map-deps ./my-project

# 4. Start watching (TestQL + live probes every 60s by default)
wup watch ./my-project

# 5. Start with live dashboard


wup watch ./my-project --dashboard
```

## Usage

### Build Dependency Map

```bash
# Auto-detect framework
wup map-deps ./my-project

# Specify framework
wup map-deps ./my-project --framework fastapi

# Custom output file
wup map-deps ./my-project --output my-deps.json
```

### Watch Project

```bash
# Basic watching: TestQL mode + live HTTP probes every 60s (uses wup.yaml if present)
wup watch ./my-project

# Legacy HTTP-only watcher (no TestQL, no periodic probes unless configured)
wup watch ./my-project --mode default --probe-interval 0

# With custom settings
wup watch ./my-project \
  --cpu-throttle 0.5 \
  --debounce 3 \
  --cooldown 600 \
  --probe-interval 120

# With live dashboard
wup watch ./my-project --dashboard

# Use specific config file
wup watch ./my-project --config custom-config.yaml

# Discover endpoints from TestQL scenarios
wup testql-endpoints /path/to/scenarios --output testql-deps.json
```

### Watch Multiple Projects Simultaneously

Pass several project roots to watch them all at once in a single process. Each
project keeps its own `wup.yaml`, dependency map, file observer and test queue.

```bash
# Watch several projects at the same time
wup watch ./service-a ./service-b ./service-c

# Discover: expand a monorepo root into every sub-project that has a wup.yaml
wup watch --discover ./my-monorepo

# Discover from the current directory
wup watch -D .
```

`--discover` walks the immediate sub-directories of each given path and watches
those that already contain a `wup.yaml` (hidden and vendor folders such as
`node_modules`, `.venv`, `dist` and `build` are skipped). A relative `--deps`
path is resolved per project, so each project uses its own `deps.json`.

> The live `--dashboard` and single `--config` options apply to single-project
> runs only; when watching multiple projects each uses its own `wup.yaml`.

### Initialize Configuration

```bash
# Generate default wup.yaml configuration
wup init

# Generate with custom output path
wup init --output .wup.yaml

# Auto-detect and configure CLI/shell services
wup init-cli ./my-project

# Merge CLI configuration with existing wup.yaml
wup init-cli ./my-project --merge
```

### Check Status

```bash
# View dependency map status
wup status

# Custom deps file
wup status --deps my-deps.json
```

### CLI/Shell Automation

WUP can automatically detect and configure CLI tools and shell scripts for testing:

```bash
# Auto-detect CLI commands and generate configuration
wup init-cli ./my-project

# Merge with existing wup.yaml
wup init-cli ./my-project --merge

# Custom output paths
wup init-cli ./my-project --output-config custom.yaml --output-scenarios custom-scenarios

# Skip argument inference (faster)
wup init-cli ./my-project --no-infer-args
```

The `init-cli` command:
- Scans `pyproject.toml`, `setup.py`, `setup.cfg` for entry points
- Detects packages with `__main__.py` modules
- Generates shell service configuration in `wup.yaml`
- Creates TestQL scenarios for CLI commands in `testql-scenarios/`
- Supports merging with existing configurations

**Generated files:**
- `cli-smoke.testql.toon.yaml` - Smoke tests for all CLI commands
- `cli-{command}.testql.toon.yaml` - Detailed tests for each command

## Architecture

### 3-Layer Testing Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    DETECTION LAYER                          │
│  File watching with watchdog + heuristics                   │
│  Skips: .git, __pycache__, node_modules, .venv              │
└──────────────────────┬──────────────────────────────────────┘
                       │ File change
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRIORITY LAYER                            │
│  Quick test: 3 endpoints max per service                    │
│  Duration: ~1-2 seconds                                     │
│  Result: Pass → Done, Fail → Escalate                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ Failure
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DETAIL LAYER                             │
│  Full test: All endpoints with blame report                 │
│  Duration: ~3-5 seconds                                     │
│  Result: Regression report with file/line/commit            │
└─────────────────────────────────────────────────────────────┘
```

### Performance Characteristics

```
Idle:           0.1% CPU, 10MB RAM
File change:    5s test → 2% CPU spike
Full regression: 15s test → 15% CPU spike
200+ files/min: 100 req/s → OK (throttled)
```

## Configuration

### Service Types

WUP supports three service types for coincidence detection and intelligent testing:

- **web** - HTTP/API services (FastAPI, Flask, Django, Express.js, etc.)
- **shell** - CLI tools, scripts, and command-line services
- **auto** - Automatic detection (default)

Coincidence detection allows WUP to identify related services. For example, if you have `users-web` and `users-shell`, WUP will detect they share the same domain and test both when relevant files change.

### wup.yaml Configuration File

WUP supports declarative configuration via `wup.yaml` (or `.wup.yaml`) in your project root. This allows you to define watch paths, service-specific settings, and test strategies.

Generate a default configuration:

```bash
wup init
```

The generated `wup.yaml` includes:
- **Metadata header**: Version, generation date, documentation links
- **Dependencies info**: WUP version and optional wupbro dashboard
- **Quick start guide**: Common commands to get started

Example `wup.yaml`:

```yaml
project:
  name: "my-project"
  description: "My awesome project"

watch:
  # Folders to watch (supports glob patterns)
  paths:
    - "app/**"
    - "src/**"
    - "routes/**"
    - "!tests/**"         # exclusion
    - "!node_modules/**"

  # Global exclude patterns
  exclude_patterns:
    - "*.md"
    - "*.txt"
    - "migrations/**"

  # File types to watch (empty = watch all files)
  # Only changes to these file extensions will trigger tests
  file_types:
    - ".py"
    - ".ts"
    - ".jsx"

services:
  # Service configurations - simplified with auto-detection
  # If paths are empty, WUP auto-detects files by service name
  
  - name: "users-shell"
    type: "shell"
    # Auto-detects files containing "users-shell"
  
  - name: "users-web"
    type: "web"
    # Auto-detects files containing "users-web"
    # Will detect coincidence with users-shell
  
  # Or use explicit paths (old style still works)
  - name: "payments"
    paths:
      - "app/payments/**"
    type: "auto"

test_strategy:
  quick:
    debounce_s: 2
    max_queue: 5
    timeout_s: 10
  detail:
    debounce_s: 10
    max_queue: 1
    timeout_s: 30

testql:
  # TestQL-specific configuration
  scenario_dir: "scenarios/tests"
  smoke_scenario: "smoke.testql.toon.yaml"
  output_format: "json"
  extra_args:
    - "--timeout 10s"
```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--config` | auto | Path to wup.yaml config file |
| `--cpu-throttle` | 0.8 | CPU usage threshold (0.0-1.0) |
| `--debounce` | 2 | Debounce time in seconds |
| `--cooldown` | 300 | Test cooldown in seconds |
| `--dashboard` | false | Enable live dashboard |
| `--deps` | deps.json | Dependency map file path |
| `--mode` | default | Watcher mode: default or testql |

### Environment Variables

```bash
# Set default CPU throttle
export WUP_CPU_THROTTLE=0.5

# Set default debounce time
export WUP_DEBOUNCE=3
```

Full list of supported variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `WUP_CPU_THROTTLE` | — | CPU usage threshold (0.0-1.0) |
| `WUP_DEBOUNCE` | — | Debounce time in seconds |
| `WUPBRO_ENDPOINT` | — | wupbro backend URL |
| `WUP_BASE_URL` | — | Base URL for visual diff page scanning |
| `OPENROUTER_API_KEY` | *(not set)* | Required for LLM features (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | LLM model for assistant |
| `PFIX_AUTO_APPLY` | `true` | Apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | Auto pip/uv install missing deps |
| `PFIX_AUTO_RESTART` | `false` | Restart process after fix |
| `PFIX_MAX_RETRIES` | `3` | Max fix retries |
| `PFIX_DRY_RUN` | `false` | Dry-run mode (no changes written) |
| `PFIX_ENABLED` | `true` | Enable/disable pfix |
| `PFIX_GIT_COMMIT` | `false` | Auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | Commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | Create .pfix_backups/ directory |

## Visual DOM Diff

WUP optionally scans configured pages with Playwright after each successful quick test, compares the DOM structure to the previous snapshot, and reports significant changes.

### Setup

```bash
pip install playwright
playwright install chromium
```

### Configuration

```yaml
visual_diff:
  enabled: true
  base_url: "http://localhost:8100"   # or leave empty and set WUP_BASE_URL env var
  base_url_env: "WUP_BASE_URL"
  delay_seconds: 5.0      # wait after file change before scanning
  max_depth: 10            # DOM snapshot depth
  pages:
    - "/health"
    - "/dashboard"
  pages_from_endpoints: true   # also scan endpoints from testql config
  threshold_added: 3           # min node additions to report as "changed"
  threshold_removed: 3
  threshold_changed: 5
  headless: true
```

Or set the base URL in `.wup.env` in the project root (not committed to git):

```bash
# .wup.env
WUP_BASE_URL=http://localhost:8100
```

### Output

- **Snapshots** — `.wup/visual-snapshots/<service>/<page>.json`
- **Diff events** — `.wup/visual-diffs/<service>/<page>.jsonl` (appended on each change)

Visible in `wup status` as a "Visual DOM diffs" section.

### Graceful degradation

If Playwright is not installed, the visual diff module logs a warning and skips scanning — it does **not** break the watcher.

## Web Dashboard (wupbro)

Optional FastAPI backend that receives events from WUP agents and renders a live dashboard.

### Run

```bash
pip install -e wupbro/
wupbro --reload --port 8000
```

Open <http://localhost:8000/> to see regressions, passes, anomalies, visual diffs, and health transitions in real time.

### Configure agent → backend

```yaml
# wup.yaml
web:
  enabled: true
  endpoint: "http://localhost:8000"
  timeout_s: 2.0
```

Or via env:

```bash
export WUPBRO_ENDPOINT=http://localhost:8000
```

The agent fire-and-forgets `REGRESSION`, `PASS`, `ANOMALY`, `VISUAL_DIFF`, and `HEALTH_TRANSITION` events. Network errors never break the watcher (soft-fail).

See `wupbro/README.md` for full API reference and driver endpoints (DOM diff, browserless, anomaly).

## Project Structure

```
wup/
├── wup/
│   ├── __init__.py            # Package exports
│   ├── anomaly_detector.py    # AnomalyDetector: hash, YAML structure, AST diff
│   ├── assistant.py           # WupAssistant: interactive configuration wizard
│   ├── cli.py                 # CLI: watch, map-deps, status, init, testql-endpoints, assistant, version, init-cli
│   ├── cli_scanner.py         # CLIScanner: detects CLI commands from pyproject.toml, setup.py, etc.
│   ├── cli_config_generator.py # CLIConfigGenerator: generates wup.yaml for shell services
│   ├── testql_cli_generator.py # TestQLCliGenerator: generates TestQL scenarios for CLI commands
│   ├── config.py              # Config loading/saving + .wup.env support
│   ├── core.py                # WupWatcher: detection, inference, scheduling
│   ├── dependency_mapper.py   # DependencyMapper: codebase → deps.json
│   ├── testql_discovery.py    # TestQLEndpointDiscovery: scenario parsing
│   ├── testql_monitor.py      # TestQLMonitor: extracts live HTTP probes and Docker services
│   ├── testql_watcher.py      # TestQLWatcher: scenario runner + health tracking
│   ├── visual_diff.py         # VisualDiffer: Playwright DOM snapshot + diff engine
│   ├── web_client.py          # WebClient: async HTTP event sink → wupbro
│   ├── monitoring_manifest.py # Builds and patches the wup.yaml monitoring block
│   ├── planfile_reporter.py   # PlanfileReporter: creates and deduplicates Planfile tickets
│   └── models/
│       ├── __init__.py
│       └── config.py          # Dataclasses: WupConfig, ServiceConfig, WatchConfig, TestStrategyConfig, TestQLConfig, VisualDiffConfig, WebConfig, AnomalyDetectionConfig...
├── wupbro/                   # Optional FastAPI dashboard (separate package)
│   ├── wupbro/
│   │   ├── main.py            # FastAPI app
│   │   ├── routers/           # events, drivers, dashboard
│   │   ├── storage.py         # EventStore (in-memory + JSONL)
│   │   └── templates/         # index.html dashboard
│   └── tests/                 # FastAPI endpoint tests (pytest + TestClient)
├── tests/
│   ├── test_wup.py            # unit/integration tests (incl. VisualDiffer, config)
│   ├── test_testql_watcher.py # TestQLWatcher + VisualDiffer integration tests
│   ├── test_web_client.py     # WebClient + WebConfig tests
│   └── test_e2e.py            # end-to-end CLI tests
├── examples/
│   ├── fastapi-app/           # FastAPI example project
│   ├── flask-app/             # Flask example project
│   ├── multi-service/         # Multi-service example
│   ├── testql_demo.py         # TestQL simulation demo
│   ├── testql_integration.py  # Custom TestQLWatcher + visual diff example
│   └── visual_diff_demo.py    # Visual DOM diff demo (no Playwright required)
├── docs/
│   └── TESTQL_INTEGRATION.md  # TestQL integration guide
├── testql-scenarios/          # Auto-generated TestQL scenarios
├── pyproject.toml             # Package config (setuptools)
└── README.md
```

## Development

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific suite
python3 -m pytest tests/test_wup.py -v
python3 -m pytest tests/test_testql_watcher.py -v

# Run with coverage
python3 -m pytest tests/ --cov=wup
```

### Goal wrapper (local `.venv`)

When `goal` is installed globally, it may inherit another project's `VIRTUAL_ENV`.
Use the local wrapper to force `wup/.venv` before running `goal` commands:

```bash
# Default: runs goal -a
bash scripts/goal-local

# Explicit arguments
bash scripts/goal-local -a
bash scripts/goal-local --dry-run
```

If needed, point to a specific `goal` binary:

```bash
GOAL_BIN=/home/tom/.local/bin/goal bash scripts/goal-local -a
```

### Examples

```bash
# Visual diff demo (no Playwright required)
python3 examples/visual_diff_demo.py

# With live page scan (requires playwright)
python3 examples/visual_diff_demo.py http://localhost:8100/health

# TestQL + visual diff integration
python3 examples/testql_integration.py /path/to/project

# Monorepo analysis (c2004-style large projects)
python3 examples/c2004_monorepo_demo.py /path/to/monorepo

# CI/CD integration patterns
python3 examples/ci_cd_integration.py

# Generate GitHub Actions workflow
python3 examples/ci_cd_integration.py --generate-github-actions

# Webhook notifications (Slack, Teams, Discord)
python3 examples/webhook_notifications.py
```

### Building & Publishing

```bash
python -m build
```

## Real-World Testing

WUP has been tested on production-scale projects:

- **c2004 Project** (maskservice/c2004): Large IoT platform with 21+ connect-* modules
  - 29 services auto-detected by assistant
  - 100+ YAML configuration files monitored
  - Anomaly detection: 0.06s for 5 config files (~1ms/file)
  - Framework: Custom Python/FastAPI hybrid

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Configuration Assistant](docs/WUP_ASSISTANT.md)** - Interactive setup guide for `wup.yaml`
  - `wup assistant` - Interactive configuration wizard
  - Auto-detects framework and services
  - Intelligent suggestions and validation
  - `wup init-cli` - Automated CLI/shell project setup

- **[Anomaly Detection](docs/ANOMALY_DETECTION.md)** - Fast alternatives to Playwright
  - Hash-based change detection (~1ms per file)
  - YAML structure analysis
  - Python AST diff for API changes
  - Configure with `anomaly_detection:` in wup.yaml

- **[Browser Notifications](docs/NOTIFICATIONS.md)** - Real-time alerts in wupbro
  - 7 notification types (regressions, status changes, recoveries)
  - Configurable per-type with cooldown
  - Server-Sent Events for instant delivery
  - Browser Notifications API integration

- **[TestQL Integration](docs/TESTQL_INTEGRATION.md)** - TestQL scenario support
  - `wup init-cli` - Automated CLI command detection and TestQL scenario generation
  - Shell service configuration for CLI tools
  - TestQL scenarios for CLI commands

## License

Licensed under Apache-2.0.
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
