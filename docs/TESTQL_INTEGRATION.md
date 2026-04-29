# WUP + TestQL Integration Guide

This guide shows how to use WUP (What's Up) with TestQL to monitor file changes and run intelligent regression tests.

## Overview

TestQL is a large project with many endpoints. WUP helps by:
1. **Mapping dependencies**: Files → Endpoints → Services
2. **Watching files**: Detects changes in real-time
3. **Smart testing**: Only tests affected services, not all 200+ endpoints
4. **3-layer approach**: Quick smoke tests first, detailed tests only on failure

## Quick Start

### 1. Install WUP

```bash
cd /home/tom/github/semcod/wup
pip install -e .
```

### 2. Build Dependency Map for TestQL

```bash
# Navigate to TestQL project
cd /home/tom/github/oqlos/testql

# Build the dependency map
wup map-deps . --framework auto

# Or specify output file
wup map-deps . --output wup-deps.json
```

This creates a `deps.json` file mapping:
- Files to endpoints
- Endpoints to services
- Services to related tests

### 3. Start Watching

```bash
# Basic watching
wup watch .

# With custom settings
wup watch . \
  --cpu-throttle 0.7 \
  --debounce 3 \
  --cooldown 180

# With live dashboard
wup watch . --dashboard
```

## How It Works

### Service Detection

WUP automatically detects TestQL services:

```
testql/
├── commands/          → Service: testql/commands
│   ├── endpoints_cmd.py
│   ├── generate_cmd.py
│   └── run_cmd.py
├── discovery/         → Service: testql/discovery
│   ├── manifest.py
│   └── source.py
├── detectors/         → Service: testql/detectors
│   ├── fastapi_detector.py
│   └── flask_detector.py
└── adapters/          → Service: testql/adapters
    └── scenario_yaml.py
```

### 3-Layer Testing

When you edit `testql/commands/endpoints_cmd.py`:

```
┌──────────────────────────────────────────────────────┐
│ Layer 1: DETECTION                                    │
│ File change detected in testql/commands               │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 2: PRIORITY (Quick Test)                      │
│ Testing 3 endpoints:                                  │
│   • /api/v1/endpoints                                 │
│   • /api/v1/endpoints/detect                        │
│   • /api/v1/generate                                  │
│ Duration: ~1-2 seconds                              │
└────────────────────────┬───────────────────────────────┘
                         │ All passed?
                         │ No → Escalate
                         ▼
┌──────────────────────────────────────────────────────┐
│ Layer 3: DETAIL (Full Test)                         │
│ Running all tests for testql/commands               │
│ Generating blame report...                          │
│ Duration: ~5-10 seconds                             │
└──────────────────────────────────────────────────────┘
```

## Configuration

### CPU Throttling

Protect your development machine:

```bash
# Use only 50% CPU
wup watch . --cpu-throttle 0.5

# Use up to 80% CPU (default)
wup watch . --cpu-throttle 0.8
```

### Debounce & Cooldown

Prevent test spam:

```bash
# Wait 5 seconds after file change before testing
wup watch . --debounce 5

# Minimum 5 minutes between tests of same service
wup watch . --cooldown 300
```

### Watch Paths

By default, WUP watches:
- `app/`
- `src/`
- `tests/`

For TestQL, you might want to watch specific directories:

```python
# In your custom watcher script
watcher = TestQLWatcher("/home/tom/github/oqlos/testql")
watcher.start_watching(watch_paths=[
    "/home/tom/github/oqlos/testql/testql",
    "/home/tom/github/oqlos/testql/scenarios"
])
```

## Custom Integration

### Override Test Methods

Integrate with TestQL CLI:

```python
# custom_watcher.py
from wup.core import WupWatcher
import subprocess

class TestQLWatcher(WupWatcher):
    
    async def run_quick_test(self, service: str, endpoints: list) -> bool:
        """Run quick TestQL test."""
        # Find relevant scenarios
        scenarios = self._find_scenarios(service)
        
        for scenario in scenarios[:3]:  # Max 3
            result = subprocess.run([
                "python", "-m", "testql.cli", "run",
                str(scenario),
                "--dry-run"
            ])
            if result.returncode != 0:
                return False
        
        return True
    
    async def run_detail_test(self, service: str, endpoints: list) -> dict:
        """Run full TestQL test with blame report."""
        # Run actual TestQL tests
        result = subprocess.run([
            "pytest", f"tests/{service}/",
            "--cov", f"testql/{service}",
            "-v"
        ])
        
        return {
            "service": service,
            "passed": result.returncode == 0,
            "blame": self._generate_blame(service)
        }
```

### Usage

```bash
python custom_watcher.py
```

## Performance

### With TestQL (200+ endpoints)

| Scenario | CPU | Time | Endpoints Tested |
|----------|-----|------|------------------|
| Idle | 0.1% | - | 0 |
| File change (quick) | 2% | 1-2s | 3 |
| File change (detail) | 15% | 5-10s | 10-50 |
| Full regression | 50% | 30-60s | 200+ |

### Why It's Fast

1. **Service-based**: Tests only affected service, not entire project
2. **3-layer**: Quick tests catch 90% of issues in 2 seconds
3. **CPU throttling**: Never overwhelms your machine
4. **Debouncing**: Groups rapid file changes

## Troubleshooting

### WUP doesn't detect my changes

```bash
# Check if file is in watched directory
wup status --deps deps.json

# Add custom watch path
wup watch . --path testql/custom_modules
```

### Tests run too frequently

```bash
# Increase cooldown
wup watch . --cooldown 600  # 10 minutes

# Increase debounce
wup watch . --debounce 5    # 5 seconds
```

### High CPU usage

```bash
# Lower CPU throttle
wup watch . --cpu-throttle 0.3  # Max 30% CPU
```

## Demo

Run the included demo:

```bash
cd /home/tom/github/semcod/wup
python3 examples/testql_demo.py
```

This shows a simulated integration without actually running the watcher.

## See Also

- [WUP README](../README.md)
- TestQL documentation: `/home/tom/github/oqlos/testql/README.md`
- Example integration: `examples/testql_integration.py`
