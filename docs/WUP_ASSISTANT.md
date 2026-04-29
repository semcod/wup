# WUP Configuration Assistant

Interactive shell assistant for configuring `wup.yaml` with intelligent suggestions.

## Starting the Assistant

```bash
# Interactive mode
wup assistant

# Or with specific goal
wup assistant --goal setup-project

# Quick mode (non-interactive)
wup assistant --quick --template fastapi
```

## Assistant Commands

### `help` - Show available commands
```
> help
Available commands:
  init       Initialize new wup.yaml
  services   Configure services to watch
  watch      Set up file watching
  testql     Configure TestQL integration
  web        Configure web dashboard
  visual     Set up visual diff
  review     Review current configuration
  validate   Validate wup.yaml syntax
  save       Save configuration to file
  exit       Exit assistant
```

### `init` - Initialize Project

```
> init
Project name: my-awesome-service
Description: FastAPI microservice for user management
Framework detected: fastapi
Initialize with example services? [Y/n]: y

✓ Created wup.yaml with:
  - 2 services detected (users-web, users-shell)
  - FastAPI patterns configured
  - TestQL scenarios linked
```

### `services` - Configure Services

```
> services

Current services:
  1. users-web (auto-detected)
  2. users-shell (auto-detected)

Commands:
  add        Add new service
  edit <n>   Edit service #n
  remove <n> Remove service #n
  detect     Auto-detect from project structure

> add
Service name: payments-api
Type: [web/shell/auto]: web
Paths (comma-separated or empty for auto-detect): app/payments/**
Coincidence with: users-web

✓ Added service 'payments-api'
  Auto-detected coincidence with users-web
```

### `watch` - File Watching Configuration

```
> watch

Current watch configuration:
  Paths: app/**, src/**
  Exclude: tests/**, node_modules/**
  File types: .py

Commands:
  add-path <path>      Add watch path
  exclude <pattern>   Add exclusion pattern
  filetypes <exts>    Set file extensions (.py,.ts,.js)
  debounce <seconds>  Set debounce time

> add-path "lib/shared/**"
✓ Added watch path: lib/shared/**

> exclude "*.test.py"
✓ Added exclusion: *.test.py
```

### `testql` - TestQL Configuration

```
> testql

TestQL configuration:
  Scenario directory: scenarios/
  Output format: json
  Extra args: --timeout 10s

Commands:
  dir <path>          Set scenario directory
  format <json|yaml>  Set output format
  args <args>         Set extra arguments
  smoke <file>        Set smoke test scenario

> dir scenarios/tests
✓ Updated scenario directory
Found 12 scenarios in scenarios/tests/
```

### `web` - Web Dashboard (wupbro)

```
> web

Web dashboard configuration:
  Enabled: true
  Endpoint: http://localhost:8000
  Timeout: 2.0s

Commands:
  enable              Enable web dashboard
  disable             Disable web dashboard
  endpoint <url>      Set endpoint URL
  notifications       Configure browser notifications

> notifications

Browser notification types:
  [✓] REGRESSION_NEW       - New regressions
  [ ] REGRESSION_DIFF      - Multiple regressions in 30s
  [✓] STATUS_TRANSITION    - Any status change
  [✓] PASS_RECOVERY        - Service recovery (fail→pass)
  [✓] ANOMALY_NEW          - New anomalies
  [ ] VISUAL_DIFF_NEW      - Visual differences
  [✓] HEALTH_CHANGE        - Service health changes

Cooldown: 5 seconds

Toggle types: toggle <type>
Set cooldown: cooldown <seconds>
```

### `visual` - Visual Diff Setup

```
> visual

Visual diff configuration:
  Enabled: true
  Base URL: http://localhost:8100
  Pages: /health, /dashboard
  Max depth: 10
  Thresholds: +3 added, -3 removed, ~5 changed

Commands:
  enable/disable      Toggle visual diff
  url <url>           Set base URL
  pages <paths>       Set pages to scan
  threshold <t> <n>   Set threshold (added/removed/changed)
  delay <seconds>     Set scan delay

> pages /health /dashboard /api/docs
✓ Pages updated: /health, /dashboard, /api/docs

> threshold added 5
✓ Threshold for 'added' nodes set to 5
```

### `review` - Review Configuration

```
> review

📋 Configuration Review
======================

Project: my-awesome-service
Framework: FastAPI

Services (3):
  ✓ users-web    [web]  paths: app/users/**
  ✓ users-shell  [shell] paths: detected by name
  ✓ payments-api [web]  paths: app/payments/**
    └─ Coincidence: shares domain with users-web

Watch Configuration:
  ✓ 3 paths configured
  ✓ 2 exclude patterns
  ✓ File types: .py

TestQL Integration:
  ✓ 12 scenarios found
  ⚠ Smoke scenario not set (recommended)

Web Dashboard:
  ✓ wupbro enabled at http://localhost:8000
  ✓ Notifications: 4 types enabled

Recommendations:
  1. Set smoke scenario for faster testing
  2. Consider reducing debounce for quicker feedback
  3. Add notification for VISUAL_DIFF if using visual diff

> validate
✓ Configuration is valid
✓ All paths exist
✓ TestQL scenarios are accessible
```

## Configuration Templates

### FastAPI Template
```
> init --template fastapi

Framework: FastAPI
Auto-detect patterns:
  - Routers in app/**/routes.py
  - Services by directory name
  - TestQL scenarios in scenarios/

Suggested services: web, api, worker
```

### Flask Template
```
> init --template flask

Framework: Flask
Auto-detect patterns:
  - Blueprints in app/**/__init__.py
  - Views in app/**/views.py
  - Services by blueprint name

Suggested services: web, admin, api
```

### Django Template
```
> init --template django

Framework: Django
Auto-detect patterns:
  - Apps in */apps.py
  - Models in */models.py
  - Services by app name

Suggested services: models, views, tasks
```

## Interactive Prompts

The assistant uses intelligent prompts based on project structure:

```
> init
Detected project structure:
  ✓ FastAPI app found in ./app/
  ✓ 2 route modules detected
  ✓ TestQL scenarios in ./scenarios/

Suggested configuration:
┌─────────────────────────────────────────┐
│ Project: auto-detected                 │
│ Framework: FastAPI                     │
│                                        │
│ Services:                              │
│   - main-web (from ./app/main/)        │
│   - auth-web (from ./app/auth/)        │
│                                        │
│ Watch paths:                           │
│   - app/**                             │
│   - tests/**                           │
│                                        │
│ Accept suggestion? [Y/n/custom]:     │
└─────────────────────────────────────────┘
```

## Validation & Suggestions

The assistant validates configuration in real-time:

```
> add-path "nonexistent/**"
⚠ Path "nonexistent/**" doesn't exist
   Suggestions:
     - Did you mean "src/**"?
     - Create directory? [y/N]

> endpoint http://localhost:8000
⚠ Cannot connect to http://localhost:8000
   Is wupbro running? Start with:
     $ wupbro --port 8000
```

## Configuration Export

```
> save
Save to [wup.yaml]: wup.yaml
Backup existing? [Y/n]: y
✓ Saved to wup.yaml
✓ Backup created: wup.yaml.bak.2024-04-29

> export --format json
{
  "project": {
    "name": "my-awesome-service",
    "framework": "fastapi"
  },
  "services": [...],
  "watch": {...}
}
```

## Shell Integration

### Bash/Zsh Completion
```bash
# Generate completion script
wup assistant --completion bash >> ~/.bashrc

# Or for zsh
wup assistant --completion zsh >> ~/.zshrc
```

### VS Code Integration
```bash
# Generate VS Code tasks
wup assistant --vscode-tasks
✓ Created .vscode/tasks.json
```

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ WUP Assistant Quick Commands                                │
├─────────────────────────────────────────────────────────────┤
│ init           Start new project configuration              │
│ services       Add/edit/remove services                     │
│ watch          Configure file watching                      │
│ testql         Setup TestQL integration                     │
│ web            Configure wupbro dashboard                 │
│ visual         Setup visual diff                          │
│ anomaly        Configure anomaly detection                  │
│ review         Review and validate config                   │
│ save           Save configuration                           │
│ help           Show this help                               │
│ exit           Exit assistant                               │
├─────────────────────────────────────────────────────────────┤
│ Tips:                                                       │
│ • Use TAB for auto-completion                               │
│ • Type '?' after any command for help                       │
│ • Configuration auto-saves to draft file                     │
│ • Use 'review' before saving to check for issues            │
└─────────────────────────────────────────────────────────────┘
```
