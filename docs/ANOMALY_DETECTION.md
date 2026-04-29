# Anomaly Detection Guide

WUP provides multiple anomaly detection methods to identify configuration drift,
structural changes, and potential issues without requiring Playwright.

## Quick Start

```python
from wup.anomaly_detector import AnomalyDetector, YAMLAnomalyConfig

# Basic usage - scan YAML files for changes
detector = AnomalyDetector('./my-project')
results = detector.scan_directory('./my-project/config', '*.yaml')
detector.print_report(results)
```

## Detection Methods

### 1. Hash Detection (Fastest)
Compares file checksums to detect any changes.

```python
from wup.anomaly_detector import AnomalyDetector, YAMLAnomalyConfig

config = YAMLAnomalyConfig(methods=['hash'])
detector = AnomalyDetector('./my-project', config)

# Scan specific file
result = detector.scan_file('config/database.yaml')
```

**Use case:** Quick validation that files haven't changed unexpectedly.
**Performance:** ~1ms per file

### 2. Structure Detection
Deep comparison of YAML structure (keys, types, nesting).

```python
config = YAMLAnomalyConfig(methods=['structure'])
detector = AnomalyDetector('./my-project', config)

results = detector.scan_directory('./config', '*.yaml')
```

**Detects:**
- Added/removed keys
- Type changes (string → number)
- List length changes
- Nested structure changes

**Use case:** Detect configuration drift in Kubernetes manifests, Docker Compose files.

### 3. AST Detection (Python files)
Analyzes Python source code structure.

```python
config = YAMLAnomalyConfig(methods=['ast'])
detector = AnomalyDetector('./my-project', config)

results = detector.scan_directory('./src', '*.py')
```

**Detects:**
- New/removed classes
- New/removed functions
- Import changes
- Method signature changes

**Use case:** API compatibility checking before deployment.

### 4. Combined Detection
Use multiple methods for comprehensive analysis.

```python
config = YAMLAnomalyConfig(
    methods=['hash', 'structure', 'ast'],
    strict_mode=True
)
```

## Configuration Reference

```python
from wup.anomaly_detector import YAMLAnomalyConfig

config = YAMLAnomalyConfig(
    enabled=True,
    methods=['hash', 'structure'],  # Detection methods to use
    ignore_patterns=[               # Files to skip
        '*.tmp',
        '*.bak',
        '.git/*',
        '__pycache__/*',
        '.venv/*',
        'node_modules/*'
    ],
    max_key_depth=5,                # Max nesting level for structure analysis
    max_file_size_kb=500,           # Skip files larger than this
    strict_mode=False               # True = detect minor changes
)
```

## CLI Usage

### Basic scan
```bash
# Scan all YAML files
python -m wup.anomaly_detector ./my-project

# Scan specific pattern
python -m wup.anomaly_detector ./my-project --pattern "*.yml"

# Use specific methods
python -m wup.anomaly_detector ./my-project --methods hash,structure
```

### Watch mode (continuous)
```bash
# Watch for changes every 5 seconds
python -m wup.anomaly_detector ./my-project --watch --interval 5

# Alert on critical changes only
python -m wup.anomaly_detector ./my-project --watch --severity critical
```

## Integration with wup.yaml

```yaml
anomaly_detection:
  enabled: true
  methods:
    - hash
    - structure
  watch_paths:
    - "config/*.yaml"
    - "deployments/*.yml"
  ignore_patterns:
    - "*.tmp"
    - "*.local.yaml"
  severity_threshold: medium  # Only report medium+ severity
  
  # Auto-actions on detection
  on_detection:
    - alert_slack
    - create_ticket
    - notify_dashboard
```

## Severity Levels

| Level | Description | Example |
|-------|-------------|---------|
| `critical` | Breaking changes | Removed required key, syntax error |
| `high` | Significant changes | Type change, API removal |
| `medium` | Notable changes | New keys, structure changes |
| `low` | Minor changes | Whitespace, comments |

## Output Format

```python
{
    'detector': 'structure',
    'file_path': './config/database.yaml',
    'anomaly_type': 'drift',
    'severity': 'high',
    'message': 'Struktura YAML zmieniona (3 zmiany)',
    'details': {
        'diffs': [
            {'path': 'database.host', 'change': 'key_removed', 'key': 'host'},
            {'path': 'database.port', 'change': 'type_changed', 'old': 'str', 'new': 'int'}
        ],
        'total_diffs': 3
    },
    'suggestions': [
        "Sprawdź czy usunięcie klucza 'host' nie zepsuje integracji",
        "Typ zmieniony w 'database.port' - może to wpłynąć na parsing"
    ],
    'timestamp': 1714411200
}
```

## Performance Comparison

| Method | Speed | Memory | Best For |
|--------|-------|--------|----------|
| hash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Quick validation |
| structure | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Config drift detection |
| ast | ⭐⭐⭐ | ⭐⭐⭐ | Python code analysis |
| text | ⭐⭐ | ⭐⭐ | Detailed diff review |

## Best Practices

1. **Use hash for CI/CD** - Fast validation in pipelines
2. **Use structure for staging** - Detect config drift before production
3. **Use ast for Python projects** - API compatibility checking
4. **Combine methods** for production monitoring

## Troubleshooting

### "No YAML module found"
```bash
pip install pyyaml
```

### Large files causing slowdown
```python
config = YAMLAnomalyConfig(
    max_file_size_kb=100,  # Reduce limit
    max_key_depth=3        # Reduce depth
)
```

### Too many false positives
```python
config = YAMLAnomalyConfig(
    strict_mode=False,  # Relax detection
    ignore_patterns=['*.local.yaml', '*.test.yaml']
)
```

## Advanced: Custom Detectors

```python
from wup.anomaly_detector import AnomalyResult

class CustomDetector:
    def detect(self, file_path: Path) -> Optional[AnomalyResult]:
        # Your custom detection logic
        pass

detector = AnomalyDetector('./project')
detector.detectors['custom'] = CustomDetector()
```
