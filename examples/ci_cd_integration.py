#!/usr/bin/env python3
"""
Demo: WUP CI/CD Integration

This example shows how to integrate WUP into CI/CD pipelines for:
  - Pre-commit validation
  - Pull request testing
  - Post-merge regression detection
  - Nightly full test runs

Supported CI/CD Platforms:
  - GitHub Actions
  - GitLab CI
  - Jenkins
  - Azure DevOps
  - CircleCI

Usage:
  python3 examples/ci_cd_integration.py
  python3 examples/ci_cd_integration.py --generate-github-actions
  python3 examples/ci_cd_integration.py --generate-gitlab-ci
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wup.config import load_config
from wup.core import WupWatcher
from wup.dependency_mapper import DependencyMapper


GITHUB_ACTIONS_TEMPLATE = '''\
name: WUP Regression Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    # Run nightly at 2 AM
    - cron: '0 2 * * *'

jobs:
  wup-quick-test:
    name: Quick Regression Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install WUP
        run: |
          pip install wup
      
      - name: Build dependency map
        run: |
          wup map-deps . --output deps-ci.json
      
      - name: Check changed files
        id: changed-files
        uses: tj-actions/changed-files@v42
      
      - name: Run WUP on changed files
        run: |
          # Only test services affected by changed files
          for file in ${{ steps.changed-files.outputs.all_changed_files }}; do
            echo "Testing changes in: $file"
            # wup test --file "$file" --deps deps-ci.json
          done
      
      - name: Upload dependency map
        uses: actions/upload-artifact@v4
        with:
          name: deps-map
          path: deps-ci.json

  wup-full-test:
    name: Full Regression Test
    if: github.event_name == 'schedule' || contains(github.event.head_commit.message, '[full-test]')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for blame reports
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install WUP
        run: |
          pip install wup
      
      - name: Run full regression test
        run: |
          wup map-deps . --output deps-full.json
          wup status --deps deps-full.json --format json > wup-status.json
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: wup-full-results
          path: |
            deps-full.json
            wup-status.json
'''


GITLAB_CI_TEMPLATE = '''\
stages:
  - validate
  - test
  - report

variables:
  WUP_CPU_THROTTLE: "0.8"
  WUP_DEBOUNCE: "2"

wup:validate:
  stage: validate
  image: python:3.11
  before_script:
    - pip install wup
  script:
    - wup map-deps . --output deps-ci.json
    - wup status --deps deps-ci.json
  artifacts:
    paths:
      - deps-ci.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

wup:quick-test:
  stage: test
  image: python:3.11
  needs:
    - wup:validate
  script:
    - |
      # Get changed files and test affected services
      CHANGED_FILES=$(git diff --name-only HEAD~1)
      for file in $CHANGED_FILES; do
        echo "Analyzing: $file"
        # wup test --file "$file" --deps deps-ci.json
      done
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

wup:full-regression:
  stage: test
  image: python:3.11
  needs:
    - wup:validate
  script:
    - wup map-deps . --output deps-full.json
    - wup status --deps deps-full.json --verbose
  artifacts:
    paths:
      - deps-full.json
    expire_in: 30 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_COMMIT_MESSAGE =~ /\\[full-regression\\]/

wup:report:
  stage: report
  image: python:3.11
  needs:
    - wup:full-regression
  script:
    - |
      echo "Generating regression report..."
      # Custom report generation
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
'''


def generate_github_actions():
    """Generate GitHub Actions workflow file."""
    output_path = Path(".github/workflows/wup-regression.yml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(GITHUB_ACTIONS_TEMPLATE)
    print(f"✅ Generated GitHub Actions workflow: {output_path}")
    print()
    print("To use this workflow:")
    print("  1. Commit the file to your repository")
    print("  2. Push to main or create a pull request")
    print("  3. The workflow will run automatically")


def generate_gitlab_ci():
    """Generate GitLab CI configuration."""
    output_path = Path(".gitlab-ci.yml")
    
    # Check if file exists and append or create
    if output_path.exists():
        content = output_path.read_text()
        if "wup:" in content:
            print("⚠️  GitLab CI already contains WUP configuration")
            return
        # Append to existing
        with open(output_path, "a") as f:
            f.write("\n\n# WUP Integration\n")
            f.write(GITLAB_CI_TEMPLATE)
        print(f"✅ Appended WUP to existing {output_path}")
    else:
        output_path.write_text(GITLAB_CI_TEMPLATE)
        print(f"✅ Generated GitLab CI configuration: {output_path}")


def show_ci_cd_demo():
    """Show CI/CD integration demo."""
    
    print("=" * 70)
    print("🔧 WUP CI/CD Integration Demo")
    print("=" * 70)
    print()
    
    print("📋 Integration Patterns:")
    print("-" * 70)
    print()
    
    print("1️⃣  Pre-commit Validation")
    print("   • Run: wup map-deps . --validate")
    print("   • Purpose: Ensure dependency map is up-to-date")
    print("   • Time: ~5 seconds")
    print()
    
    print("2️⃣  Pull Request Testing (Quick)")
    print("   • Run: wup test --changed-files --mode quick")
    print("   • Purpose: Test only services affected by PR changes")
    print("   • Time: ~30 seconds")
    print()
    
    print("3️⃣  Pull Request Testing (Detail on Failure)")
    print("   • Run: wup test --failed-services --mode detail")
    print("   • Purpose: Full test with blame report if quick fails")
    print("   • Time: ~2-3 minutes (only on failure)")
    print()
    
    print("4️⃣  Post-merge Regression")
    print("   • Run: wup status --format json")
    print("   • Purpose: Track service health after merge")
    print("   • Output: Artifact for trend analysis")
    print()
    
    print("5️⃣  Nightly Full Test")
    print("   • Run: wup test --all-services --mode full")
    print("   • Purpose: Complete regression detection")
    print("   • Schedule: Daily at 2 AM")
    print()
    
    print("📊 CI/CD Performance Matrix:")
    print("-" * 70)
    print()
    
    scenarios = [
        ("Pre-commit", "5s", "Validate deps map", "No"),
        ("PR Quick", "30s", "3 endpoints per service", "Yes"),
        ("PR Detail", "2-3m", "Full test + blame", "No (on failure)"),
        ("Post-merge", "10s", "Health check", "Yes"),
        ("Nightly", "5-10m", "Full regression", "No"),
    ]
    
    print(f"{'Scenario':<15} {'Time':<10} {'Coverage':<25} {'Parallel'}")
    print("-" * 70)
    for name, time, coverage, parallel in scenarios:
        print(f"{name:<15} {time:<10} {coverage:<25} {parallel}")
    print()
    
    print("🎯 CI/CD Best Practices:")
    print("-" * 70)
    print()
    print("   1. Cache dependency maps between runs")
    print("      → Store deps.json as CI artifact")
    print()
    print("   2. Use file change detection")
    print("      → Only test affected services")
    print()
    print("   3. Set appropriate CPU throttle")
    print("      → WUP_CPU_THROTTLE=0.7 in CI environment")
    print()
    print("   4. Enable notifications on regression")
    print("      → Slack/Teams webhook on HEALTH_TRANSITION")
    print()
    print("   5. Track trends over time")
    print("      → Store wup-status.json for analytics")
    print()
    
    print("🔧 Environment Variables for CI/CD:")
    print("-" * 70)
    print()
    print("   WUP_CPU_THROTTLE=0.7      # Be gentle on shared CI runners")
    print("   WUP_DEBOUNCE=1            # Fast feedback in CI")
    print("   WUP_TIMEOUT=30            # Shorter timeouts")
    print("   WUP_BASE_URL=http://...   # Test server URL")
    print("   WUP_WEB_ENDPOINT=http://... # Dashboard endpoint")
    print()
    
    print("=" * 70)
    print("✅ CI/CD integration demo complete!")
    print("=" * 70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WUP CI/CD Integration Demo")
    parser.add_argument("--generate-github-actions", action="store_true",
                       help="Generate GitHub Actions workflow file")
    parser.add_argument("--generate-gitlab-ci", action="store_true",
                       help="Generate GitLab CI configuration file")
    
    args = parser.parse_args()
    
    if args.generate_github_actions:
        generate_github_actions()
    elif args.generate_gitlab_ci:
        generate_gitlab_ci()
    else:
        show_ci_cd_demo()


if __name__ == "__main__":
    main()
