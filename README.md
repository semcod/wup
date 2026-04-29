# WUP (What's Up)


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.90-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.9000 (6 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-04-29 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

![PyPI](https://img.shields.io/badge/pypi-wup-blue) ![Version](https://img.shields.io/badge/version-0.2.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)

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

## Installation

```bash
# Install from source
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# 1. Initialize configuration (optional)
wup init

# 2. Build dependency map (one-time setup)
wup map-deps ./my-project

# 3. Start watching for changes
wup watch ./my-project

# 4. Start with live dashboard
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
# Basic watching (uses wup.yaml if present)
wup watch ./my-project

# With custom settings
wup watch ./my-project \
  --cpu-throttle 0.5 \
  --debounce 3 \
  --cooldown 600

# With live dashboard
wup watch ./my-project --dashboard

# Use specific config file
wup watch ./my-project --config custom-config.yaml

# TestQL mode
wup watch ./my-project --mode testql
```

### Initialize Configuration

```bash
# Generate default wup.yaml configuration
wup init

# Generate with custom output path
wup init --output .wup.yaml
```

### Check Status

```bash
# View dependency map status
wup status

# Custom deps file
wup status --deps my-deps.json
```

## Architecture

### 3-Layer Testing Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    DETECTION LAYER                           │
│  File watching with watchdog + heuristics                   │
│  Skips: .git, __pycache__, node_modules, .venv              │
└──────────────────────┬──────────────────────────────────────┘
                       │ File change
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   PRIORITY LAYER                             │
│  Quick test: 3 endpoints max per service                    │
│  Duration: ~1-2 seconds                                      │
│  Result: Pass → Done, Fail → Escalate                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Failure
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DETAIL LAYER                              │
│  Full test: All endpoints with blame report                 │
│  Duration: ~3-5 seconds                                      │
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

### wup.yaml Configuration File

WUP supports declarative configuration via `wup.yaml` (or `.wup.yaml`) in your project root. This allows you to define watch paths, service-specific settings, and test strategies.

Generate a default configuration:

```bash
wup init
```

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

services:
  # Service configurations
  - name: "users"
    root: "app/users"
    paths:
      - "app/users/**"
      - "routes/users/**"
    quick_tests:
      scope: "read,write"
      max_endpoints: 3
    detail_tests:
      scope: "all"
      max_endpoints: 10
    cpu_throttle: 0.7
    notify:
      type: "http+file"
      url: "http://localhost:8001/notify"
      file: "wup/notify-users.json"

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

## Integration with Test Frameworks

WUP is designed to work with any test framework. The current implementation includes placeholder test methods that you can customize:

```python
# In wup/core.py, customize these methods:

async def run_quick_test(self, service: str, endpoints: List[str]) -> bool:
    # Integrate with your test framework (pytest, unittest, TestQL, etc.)
    # Example:
    result = subprocess.run([
        "pytest", f"tests/{service}/test_smoke.py",
        "--maxfail=1", "-q"
    ])
    return result.returncode == 0

async def run_detail_test(self, service: str, endpoints: List[str]) -> Dict:
    # Run full test suite with blame reporting
    # Example:
    result = subprocess.run([
        "pytest", f"tests/{service}/",
        "--cov", f"app/{service}",
        "--cov-report=json"
    ])
    return parse_coverage_report("coverage.json")
```

## Project Structure

```
wup/
├── wup/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Configuration loader
│   ├── models/
│   │   ├── __init__.py       # Models package
│   │   └── config.py         # Configuration dataclasses
│   ├── core.py               # WupWatcher implementation
│   ├── dependency_mapper.py  # Dependency mapping logic
│   ├── testql_watcher.py     # TestQL integration
│   └── cli.py                # CLI interface
├── tests/
│   └── test_wup.py           # Unit tests
├── docs/
│   ├── 2.md                  # Refactoring documentation
│   ├── 3.md                  # Configuration plan
│   └── TESTQL_INTEGRATION.md # TestQL integration docs
├── wup.yaml.example          # Example configuration
├── pyproject.toml           # Package configuration
└── README.md                 # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wup

# Run specific test
pytest tests/test_wup.py::TestDependencyMapper::test_init
```

### Building for Distribution

```bash
# Build wheel and source distribution
python -m build

# Install from dist
pip install dist/wup-0.1.6-py3-none-any.whl
```

## License

Licensed under Apache-2.0.
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
