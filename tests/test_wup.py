"""Tests for WUP (What's Up) - Intelligent file watcher for regression testing."""

import json
import tempfile
from pathlib import Path

import pytest

from wup.config import load_config, save_config, get_default_config
from wup.core import WupWatcher
from wup.dependency_mapper import DependencyMapper
from wup.models.config import (
    WupConfig,
    WatchConfig,
    ServiceConfig,
    TestStrategyConfig,
    TestQLConfig,
    NotifyConfig,
    ServiceTestConfig,
    ProjectConfig,
    VisualDiffConfig,
)
from wup.testql_watcher import TestQLWatcher
from wup.visual_diff import VisualDiffer, _diff_snapshots, _page_slug, _resolve_base_url


class TestDependencyMapper:
    """Tests for the DependencyMapper class."""
    
    def test_init(self):
        """Test initialization of DependencyMapper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            assert mapper.project_root == Path(tmpdir)
            assert len(mapper.file_to_endpoints) == 0
            assert len(mapper.service_to_endpoints) == 0
    
    def test_infer_service_from_path(self):
        """Test service inference from file paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            # Test various path patterns
            assert mapper._infer_service("app/users/routes.py") == "app/users"
            assert mapper._infer_service("src/components/auth.ts") == "src/components"
            assert mapper._infer_service("deeply/nested/path/file.py") == "deeply/nested"
    
    def test_build_from_codebase_empty(self):
        """Test building dependency map from empty codebase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            deps = mapper.build_from_codebase()
            
            assert "services" in deps
            assert "files" in deps
            assert len(deps["services"]) == 0
            assert len(deps["files"]) == 0
    
    def test_build_from_codebase_with_fastapi(self):
        """Test building dependency map with FastAPI endpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a sample FastAPI file
            app_dir = Path(tmpdir) / "app" / "users"
            app_dir.mkdir(parents=True)
            
            routes_file = app_dir / "routes.py"
            routes_file.write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def get_users():
    return []

@router.post("/users")
def create_user():
    return {"id": 1}
""")
            
            mapper = DependencyMapper(tmpdir)
            deps = mapper.build_from_codebase(framework="fastapi")
            
            assert len(deps["services"]) > 0
            assert len(deps["files"]) > 0
    
    def test_save_and_load(self):
        """Test saving and loading dependency map."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            # Add some dummy data
            mapper.file_to_endpoints["app/users/routes.py"] = ["/users", "/users/{id}"]
            mapper.service_to_endpoints["app/users"] = ["/users", "/users/{id}"]
            mapper.service_to_files["app/users"].add("app/users/routes.py")
            
            # Save
            output_file = Path(tmpdir) / "deps.json"
            mapper.save(str(output_file))
            assert output_file.exists()
            
            # Load into new mapper
            mapper2 = DependencyMapper(tmpdir)
            mapper2.load(str(output_file))
            
            assert mapper2.file_to_endpoints == mapper.file_to_endpoints
            assert mapper2.service_to_endpoints == mapper.service_to_endpoints
    
    def test_infer_service_from_path_edge_cases(self):
        """Test service inference with edge case paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            # Single directory - returns None (needs at least 2 parts)
            assert mapper._infer_service("app") is None
            
            # Very deep nesting
            assert mapper._infer_service("a/b/c/d/e/f/file.py") == "a/b"
            
            # Path with numbers
            assert mapper._infer_service("v1/api/routes.py") == "v1/api"
            
            # Path with underscores
            assert mapper._infer_service("src/user_auth/login.py") == "src/user_auth"
    
    def test_get_service_for_file_empty_mapper(self):
        """Test getting service for file when mapper is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            # Need to use absolute path under tmpdir
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            service = mapper.get_service_for_file(file_path)
            # Dependency mapper has fallback heuristic that returns first two path parts
            assert service == "app/users"
    
    def test_get_endpoints_for_service_empty_mapper(self):
        """Test getting endpoints for service when mapper is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            endpoints = mapper.get_endpoints_for_service("users")
            assert endpoints == []
    
    def test_build_from_codebase_with_flask(self):
        """Test building dependency map with Flask endpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a sample Flask file
            app_dir = Path(tmpdir) / "app" / "auth"
            app_dir.mkdir(parents=True)
            
            routes_file = app_dir / "views.py"
            routes_file.write_text("""
from flask import Blueprint, jsonify

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    return jsonify({'token': 'abc'})

@bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({'success': True})
""")
            
            mapper = DependencyMapper(tmpdir)
            deps = mapper.build_from_codebase(framework="flask")
            
            assert len(deps["services"]) > 0
            assert len(deps["files"]) > 0
    
    def test_service_to_files_tracking(self):
        """Test that service to files mapping is tracked correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            
            # Add file to service
            mapper.service_to_files["users"].add("app/users/routes.py")
            mapper.service_to_files["users"].add("app/users/models.py")
            
            assert len(mapper.service_to_files["users"]) == 2
            assert "app/users/routes.py" in mapper.service_to_files["users"]
    
    def test_build_from_codebase_nonexistent_directory(self):
        """Test building from codebase with non-existent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mapper = DependencyMapper(tmpdir)
            # Should not fail, just return empty deps
            deps = mapper.build_from_codebase(framework="fastapi")
            assert "services" in deps
            assert "files" in deps


class TestWupWatcher:
    """Tests for the WupWatcher class."""
    
    def test_init(self):
        """Test initialization of WupWatcher."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            assert watcher.project_root == Path(tmpdir)
            assert watcher.cpu_throttle == 0.8
            assert watcher.debounce_seconds == 2
            assert watcher.test_cooldown_seconds == 300
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config with custom debounce setting
            strategy = TestStrategyConfig(
                quick={"debounce_s": 5, "max_queue": 5, "timeout_s": 10},
                detail={"debounce_s": 10, "max_queue": 1, "timeout_s": 30}
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=strategy,
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(
                tmpdir,
                cpu_throttle=0.5,
                test_cooldown_seconds=600,
                config=config
            )
            assert watcher.cpu_throttle == 0.5
            assert watcher.debounce_seconds == 5
            assert watcher.test_cooldown_seconds == 600
    
    def test_infer_service(self):
        """Test service inference from file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            
            # Test with dependency mapper
            service = watcher.infer_service(str(Path(tmpdir) / "app" / "users" / "routes.py"))
            assert service == "app/users"
    
    def test_infer_service_with_auto_detection(self):
        """Test service inference with auto-detection from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create service with auto-detection (empty paths)
            service = ServiceConfig(
                name="users-shell",
                root="app/users-shell",
                paths=[],  # Empty paths triggers auto-detection
                type="shell"
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # File containing "users-shell" should match
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "users-shell" / "main.py"))
            assert inferred == "users-shell"
            
            # File containing "users" should not match auto-detection
            # Fallback heuristic returns "app/users" from dependency mapper
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "users" / "main.py"))
            assert inferred == "app/users"  # Fallback heuristic
    
    def test_infer_service_with_explicit_paths(self):
        """Test service inference with explicit config paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**", "routes/users/**"],
                type="auto"
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Explicit path should match
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "users" / "routes.py"))
            assert inferred == "users"
            
            # Alternative explicit path should match
            inferred = watcher.infer_service(str(Path(tmpdir) / "routes" / "users" / "main.py"))
            assert inferred == "users"
    
    def test_infer_service_priority_config_over_mapper(self):
        """Test that config services take priority over dependency mapper."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="custom-service",
                root="app/custom",
                paths=["app/custom/**"],
                type="auto"
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Config should take priority
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "custom" / "file.py"))
            assert inferred == "custom-service"
    
    def test_infer_service_fallback_to_heuristics(self):
        """Test fallback to heuristics when no config or mapper match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Should fallback to heuristics (first two path parts)
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "users" / "routes.py"))
            assert inferred == "app/users"
    
    def test_should_test_cooldown(self):
        """Test cooldown mechanism for testing."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir, test_cooldown_seconds=10)
            
            # First test should be allowed
            assert watcher.should_test("test-service")
            
            # Set last test time to current time
            watcher.last_test_times["test-service"] = time.time()
            
            # Immediate second test should be blocked
            assert not watcher.should_test("test-service")
    
    def test_schedule_quick_test(self):
        """Test scheduling of quick tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            
            # Add dummy endpoints
            watcher.dependency_mapper.service_to_endpoints["test-service"] = [
                "/api/endpoint1",
                "/api/endpoint2",
                "/api/endpoint3",
                "/api/endpoint4"
            ]
            
            watcher.schedule_quick_test("test-service")
            
            assert len(watcher.test_queue) == 1
            test_type, service, endpoints = watcher.test_queue[0]
            assert test_type == "quick"
            assert service == "test-service"
            assert len(endpoints) == 3  # Limited to 3 for quick test
    
    def test_schedule_detail_test(self):
        """Test scheduling of detail tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            
            # Add dummy endpoints
            watcher.dependency_mapper.service_to_endpoints["test-service"] = [
                "/api/endpoint1",
                "/api/endpoint2"
            ]
            
            watcher.schedule_detail_test("test-service")
            
            assert len(watcher.test_queue) == 1
            test_type, service, endpoints = watcher.test_queue[0]
            assert test_type == "detail"
            assert service == "test-service"
            assert len(endpoints) == 2  # All endpoints for detail test
    
    def test_on_file_change_skip_dirs(self):
        """Test that certain directories are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            
            # Test skipped directories
            skipped_paths = [
                str(Path(tmpdir) / ".git" / "config"),
                str(Path(tmpdir) / "__pycache__" / "module.pyc"),
                str(Path(tmpdir) / "node_modules" / "package.json"),
            ]
            
            for path in skipped_paths:
                watcher.on_file_change(path)
            
            # No services should have been added
            assert len(watcher.changed_services) == 0
    
    def test_detect_service_coincidences_shell_web(self):
        """Test coincidence detection between shell and web services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service1 = ServiceConfig(
                name="users-shell",
                root="app/users-shell",
                type="shell",
                paths=[]
            )
            service2 = ServiceConfig(
                name="users-web",
                root="app/users-web",
                type="web",
                paths=[]
            )
            service3 = ServiceConfig(
                name="payments-shell",
                root="app/payments-shell",
                type="shell",
                paths=[]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service1, service2, service3],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # users-shell should detect users-web as related
            related = watcher.detect_service_coincidences("users-shell")
            assert "users-web" in related
            assert "payments-shell" not in related
            
            # users-web should detect users-shell as related
            related = watcher.detect_service_coincidences("users-web")
            assert "users-shell" in related
            assert "payments-shell" not in related
    
    def test_detect_service_coincidences_auto_type(self):
        """Test coincidence detection with auto type services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service1 = ServiceConfig(
                name="users",
                root="app/users",
                type="auto",
                paths=[]
            )
            service2 = ServiceConfig(
                name="users-api",
                root="app/users-api",
                type="auto",
                paths=[]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service1, service2],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # users and users-api don't share domain (only shell/web suffixes are handled)
            # Since both are auto type and don't have shell/web suffixes, they don't match
            related = watcher.detect_service_coincidences("users")
            assert "users-api" not in related
    
    def test_detect_service_coincidences_no_config(self):
        """Test coincidence detection with no configured services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            related = watcher.detect_service_coincidences("users")
            assert len(related) == 0
    
    def test_detect_service_coincidences_unknown_service(self):
        """Test coincidence detection for unknown service."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service1 = ServiceConfig(
                name="users-shell",
                root="app/users-shell",
                type="shell",
                paths=[]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service1],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Unknown service should return empty list
            related = watcher.detect_service_coincidences("unknown")
            assert len(related) == 0
    
    def test_services_share_domain(self):
        """Test the _services_share_domain helper method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = WupWatcher(tmpdir)
            
            # Same domain with different suffixes
            assert watcher._services_share_domain("users-shell", "users-web")
            assert watcher._services_share_domain("users-shell", "users")
            assert watcher._services_share_domain("payments", "payments-shell")
            
            # Different domains
            assert not watcher._services_share_domain("users", "payments")
            assert not watcher._services_share_domain("api/auth", "api/users")
            
            # Underscore variants
            assert watcher._services_share_domain("users_shell", "users_web")
            assert watcher._services_share_domain("users_shell", "users")
    
    def test_on_file_change_filters_by_file_type(self):
        """Test that file change respects configured file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            watch = WatchConfig(
                paths=["app/**"],
                file_types=[".py", ".ts"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=watch,
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Python file should be processed
            py_file = str(Path(tmpdir) / "app" / "test.py")
            watcher.on_file_change(py_file)
            
            # TypeScript file should be processed
            ts_file = str(Path(tmpdir) / "app" / "test.ts")
            watcher.on_file_change(ts_file)
            
            # Markdown file should be filtered out
            md_file = str(Path(tmpdir) / "app" / "test.md")
            watcher.on_file_change(md_file)
            
            # Text file should be filtered out
            txt_file = str(Path(tmpdir) / "app" / "test.txt")
            watcher.on_file_change(txt_file)
            
            # Only .py and .ts files should trigger service detection
            # (though no services are configured, so changed_services will be empty)
            # The key is that no errors occur and filtering works
    
    def test_on_file_change_no_file_type_filter(self):
        """Test that when file_types is empty, all files are processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            watch = WatchConfig(
                paths=["app/**"],
                file_types=[]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=watch,
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # All file types should be processed
            py_file = str(Path(tmpdir) / "app" / "test.py")
            watcher.on_file_change(py_file)
            
            md_file = str(Path(tmpdir) / "app" / "test.md")
            watcher.on_file_change(md_file)
            
            # No filtering should occur


class TestIntegrationWorkflow:
    """Integration tests for complete workflows."""
    
    def test_full_workflow_file_change_to_test_scheduling(self):
        """Test complete workflow from file change to test scheduling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**"],
                quick_tests=ServiceTestConfig(scope="all", max_endpoints=3)
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(paths=["app/**"]),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            watcher.dependency_mapper.service_to_endpoints["users"] = [
                "/api/users",
                "/api/users/{id}",
                "/api/users/create"
            ]
            
            # Simulate file change
            file_path = str(Path(tmpdir) / "app" / "users" / "routes.py")
            watcher.on_file_change(file_path)
            
            # Verify service was detected
            assert "users" in watcher.changed_services
            
            # Verify test was scheduled
            assert len(watcher.test_queue) == 1
            test_type, service_name, endpoints = watcher.test_queue[0]
            assert test_type == "quick"
            assert service_name == "users"
            assert len(endpoints) == 3  # Limited by quick_tests.max_endpoints
    
    def test_workflow_with_file_type_filtering(self):
        """Test workflow with file type filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            watch = WatchConfig(
                paths=["app/**"],
                file_types=[".py"]
            )
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=watch,
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            watcher.dependency_mapper.service_to_endpoints["users"] = ["/api/users"]
            
            # Python file should trigger
            py_file = str(Path(tmpdir) / "app" / "users" / "routes.py")
            watcher.on_file_change(py_file)
            assert "users" in watcher.changed_services
            
            # Markdown file should not trigger
            watcher.changed_services.clear()
            md_file = str(Path(tmpdir) / "app" / "users" / "README.md")
            watcher.on_file_change(md_file)
            assert "users" not in watcher.changed_services
    
    def test_workflow_with_service_coincidence(self):
        """Test workflow that detects service coincidences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service1 = ServiceConfig(
                name="users-shell",
                root="app/users-shell",
                type="shell",
                paths=[]
            )
            service2 = ServiceConfig(
                name="users-web",
                root="app/users-web",
                type="web",
                paths=[]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service1, service2],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Detect coincidences
            related = watcher.detect_service_coincidences("users-shell")
            assert "users-web" in related
    
    def test_workflow_with_multiple_file_changes(self):
        """Test workflow with multiple rapid file changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(paths=["app/**"]),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            watcher.dependency_mapper.service_to_endpoints["users"] = ["/api/users"]
            
            # Multiple file changes for same service
            files = [
                str(Path(tmpdir) / "app" / "users" / "routes.py"),
                str(Path(tmpdir) / "app" / "users" / "models.py"),
                str(Path(tmpdir) / "app" / "users" / "schemas.py"),
            ]
            
            for file_path in files:
                watcher.on_file_change(file_path)
            
            # Service should be in changed_services
            assert "users" in watcher.changed_services
            
            # Multiple tests might be scheduled depending on debounce
            # But service should be tracked
            assert len(watcher.changed_services) == 1
    
    def test_workflow_with_auto_detection_and_explicit_paths(self):
        """Test workflow mixing auto-detection and explicit paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            service1 = ServiceConfig(
                name="users-shell",
                root="app/users-shell",
                type="shell",
                paths=[]  # Auto-detection
            )
            service2 = ServiceConfig(
                name="payments",
                root="app/payments",
                type="auto",
                paths=["app/payments/**"]  # Explicit paths
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service1, service2],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Auto-detection should match
            inferred1 = watcher.infer_service(str(Path(tmpdir) / "app" / "users-shell" / "main.py"))
            assert inferred1 == "users-shell"
            
            # Explicit path should match
            inferred2 = watcher.infer_service(str(Path(tmpdir) / "app" / "payments" / "routes.py"))
            assert inferred2 == "payments"


def test_import():
    """Verify the main package can be imported."""
    import wup  # noqa: F401
    from wup import WupWatcher, DependencyMapper  # noqa: F401


class TestFileFiltering:
    """Tests for file type filtering."""
    
    def test_should_watch_file_with_config(self):
        """Test file filtering with configured file types."""
        from wup.models.config import WupConfig, ProjectConfig, WatchConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(file_types=[".py", ".ts", ".tsx", ".js"])
            )
            watcher = WupWatcher(tmpdir, config=config)
            
            # Should watch allowed types
            assert watcher.should_watch_file(str(Path(tmpdir) / "app.py"))
            assert watcher.should_watch_file(str(Path(tmpdir) / "component.ts"))
            assert watcher.should_watch_file(str(Path(tmpdir) / "app.tsx"))
            assert watcher.should_watch_file(str(Path(tmpdir) / "main.js"))
            
            # Should skip disallowed types
            assert not watcher.should_watch_file(str(Path(tmpdir) / "README.md"))
            assert not watcher.should_watch_file(str(Path(tmpdir) / "config.yaml"))
    
    def test_should_watch_file_without_config(self):
        """Test file filtering without configured file types (watch all)."""
        from wup.models.config import WupConfig, ProjectConfig, WatchConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(file_types=[])
            )
            watcher = WupWatcher(tmpdir, config=config)
            
            # Should watch all files when no filter configured
            assert watcher.should_watch_file(str(Path(tmpdir) / "app.py"))
            assert watcher.should_watch_file(str(Path(tmpdir) / "README.md"))
            assert watcher.should_watch_file(str(Path(tmpdir) / "config.yaml"))


class TestConfigModels:
    """Tests for configuration dataclasses."""
    
    def test_project_config(self):
        """Test ProjectConfig dataclass."""
        config = ProjectConfig(name="test-project", description="Test project")
        assert config.name == "test-project"
        assert config.description == "Test project"
    
    def test_notify_config(self):
        """Test NotifyConfig dataclass."""
        config = NotifyConfig(type="http+file", url="http://localhost:8001", file="notify.json")
        assert config.type == "http+file"
        assert config.url == "http://localhost:8001"
        assert config.file == "notify.json"
    
    def test_service_test_config(self):
        """Test ServiceTestConfig dataclass."""
        config = ServiceTestConfig(scope="read,write", max_endpoints=5)
        assert config.scope == "read,write"
        assert config.max_endpoints == 5
    
    def test_service_config(self):
        """Test ServiceConfig dataclass."""
        notify = NotifyConfig(type="file", file="notify.json")
        quick = ServiceTestConfig(scope="read", max_endpoints=3)
        detail = ServiceTestConfig(scope="all", max_endpoints=10)
        
        config = ServiceConfig(
            name="users",
            root="app/users",
            paths=["app/users/**", "routes/users/**"],
            quick_tests=quick,
            detail_tests=detail,
            cpu_throttle=0.7,
            notify=notify
        )
        assert config.name == "users"
        assert config.root == "app/users"
        assert len(config.paths) == 2
        assert config.cpu_throttle == 0.7
    
    def test_watch_config(self):
        """Test WatchConfig dataclass."""
        config = WatchConfig(
            paths=["app/**", "src/**"],
            exclude_patterns=["*.md", "tests/**"]
        )
        assert len(config.paths) == 2
        assert len(config.exclude_patterns) == 2
    
    def test_test_strategy_config(self):
        """Test TestStrategyConfig dataclass."""
        config = TestStrategyConfig(
            quick={"debounce_s": 2, "max_queue": 5, "timeout_s": 10},
            detail={"debounce_s": 10, "max_queue": 1, "timeout_s": 30}
        )
        assert config.quick["debounce_s"] == 2
        assert config.detail["timeout_s"] == 30
    
    def test_testql_config(self):
        """Test TestQLConfig dataclass."""
        config = TestQLConfig(
            scenario_dir="scenarios/tests",
            smoke_scenario="smoke.testql.toon.yaml",
            output_format="json",
            extra_args=["--timeout 10s"]
        )
        assert config.scenario_dir == "scenarios/tests"
        assert config.output_format == "json"
        assert len(config.extra_args) == 1
    
    def test_wup_config(self):
        """Test WupConfig dataclass."""
        project = ProjectConfig(name="test", description="Test")
        watch = WatchConfig(paths=["app/**"])
        service = ServiceConfig(name="users", root="app/users")
        strategy = TestStrategyConfig()
        testql = TestQLConfig()
        
        config = WupConfig(
            project=project,
            watch=watch,
            services=[service],
            test_strategy=strategy,
            testql=testql
        )
        assert config.project.name == "test"
        assert len(config.services) == 1
        assert config.services[0].name == "users"
        # visual_diff is auto-populated with defaults
        assert isinstance(config.visual_diff, VisualDiffConfig)
        assert config.visual_diff.enabled is False

    def test_visual_diff_config_defaults(self):
        """Test VisualDiffConfig has sensible defaults."""
        cfg = VisualDiffConfig()
        assert cfg.enabled is False
        assert cfg.base_url == ""
        assert cfg.base_url_env == "WUP_BASE_URL"
        assert cfg.delay_seconds == 5.0
        assert cfg.max_depth == 10
        assert cfg.snapshot_dir == ".wup/visual-snapshots"
        assert cfg.diff_dir == ".wup/visual-diffs"
        assert cfg.pages == []
        assert cfg.pages_from_endpoints is True
        assert cfg.headless is True

    def test_visual_diff_config_custom(self):
        """Test VisualDiffConfig with custom values."""
        cfg = VisualDiffConfig(
            enabled=True,
            base_url="http://localhost:9000",
            pages=["/dashboard", "/users"],
            threshold_added=10,
        )
        assert cfg.enabled is True
        assert cfg.base_url == "http://localhost:9000"
        assert cfg.pages == ["/dashboard", "/users"]
        assert cfg.threshold_added == 10


class TestVisualDiffer:
    """Tests for the VisualDiffer class (no Playwright required)."""

    def test_resolve_base_url_from_config(self):
        cfg = VisualDiffConfig(base_url="http://localhost:8080/")
        assert _resolve_base_url(cfg) == "http://localhost:8080"

    def test_resolve_base_url_from_env(self, monkeypatch):
        cfg = VisualDiffConfig(base_url="", base_url_env="MY_VD_URL")
        monkeypatch.setenv("MY_VD_URL", "http://env-host:1234/")
        assert _resolve_base_url(cfg) == "http://env-host:1234"

    def test_resolve_base_url_empty(self, monkeypatch):
        cfg = VisualDiffConfig(base_url="", base_url_env="WUP_VD_NONE")
        monkeypatch.delenv("WUP_VD_NONE", raising=False)
        assert _resolve_base_url(cfg) == ""

    def test_page_slug(self):
        assert _page_slug("http://x/api/v1/users") == "api_v1_users"
        assert _page_slug("http://x/") == "root"

    def test_pages_for_service_explicit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(
                base_url="http://localhost:8080",
                pages=["/dashboard"],
                pages_from_endpoints=False,
            )
            differ = VisualDiffer(tmpdir, cfg)
            pages = differ._pages_for_service("users", ["/api/users"])
            assert pages == ["http://localhost:8080/dashboard"]

    def test_pages_for_service_from_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(
                base_url="http://localhost:8080",
                pages_from_endpoints=True,
            )
            differ = VisualDiffer(tmpdir, cfg)
            pages = differ._pages_for_service("users", ["/api/users", "/api/users/1"])
            assert "http://localhost:8080/api/users" in pages
            assert "http://localhost:8080/api/users/1" in pages

    def test_pages_for_service_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(
                base_url="http://localhost:8080",
                pages_from_endpoints=False,
            )
            differ = VisualDiffer(tmpdir, cfg)
            pages = differ._pages_for_service("users", [])
            assert pages == ["http://localhost:8080/users"]

    def test_pages_for_service_absolute_url_passthrough(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(
                base_url="http://localhost:8080",
                pages=["https://example.com/health"],
                pages_from_endpoints=False,
            )
            differ = VisualDiffer(tmpdir, cfg)
            pages = differ._pages_for_service("svc", [])
            assert pages == ["https://example.com/health"]

    def test_diff_snapshots_baseline(self):
        new = {"tag": "HTML", "children": [{"tag": "BODY"}]}
        diff = _diff_snapshots(None, new, max_depth=5,
                               threshold_added=1, threshold_removed=1, threshold_changed=1)
        assert diff["status"] == "new"

    def test_diff_snapshots_identical(self):
        snap = {"tag": "HTML", "children": [{"tag": "BODY", "id": "main"}]}
        diff = _diff_snapshots(snap, snap, max_depth=5,
                               threshold_added=1, threshold_removed=1, threshold_changed=1)
        assert diff["status"] == "ok"
        assert diff["counts"]["added"] == 0
        assert diff["counts"]["removed"] == 0

    def test_diff_snapshots_changed(self):
        old = {"tag": "HTML", "children": [{"tag": "BODY"}]}
        new = {"tag": "HTML", "children": [
            {"tag": "BODY"},
            {"tag": "DIV", "id": "added1"},
            {"tag": "DIV", "id": "added2"},
            {"tag": "DIV", "id": "added3"},
        ]}
        diff = _diff_snapshots(old, new, max_depth=5,
                               threshold_added=3, threshold_removed=10, threshold_changed=10)
        assert diff["status"] == "changed"
        assert diff["counts"]["added"] >= 3

    def test_run_for_service_disabled_returns_empty(self):
        """When disabled, run_for_service should be a no-op."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(enabled=False)
            differ = VisualDiffer(tmpdir, cfg)
            results = asyncio.run(differ.run_for_service("svc", ["/x"]))
            assert results == []

    def test_get_recent_diffs_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig()
            differ = VisualDiffer(tmpdir, cfg)
            assert differ.get_recent_diffs() == []

    def test_get_recent_diffs_filters_by_age(self):
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = VisualDiffConfig(diff_dir=".wup/visual-diffs")
            differ = VisualDiffer(tmpdir, cfg)
            now = int(time.time())
            diff_file = differ.diff_dir / "svc" / "page.jsonl"
            diff_file.parent.mkdir(parents=True, exist_ok=True)
            diff_file.write_text(
                json.dumps({"timestamp": now, "service": "svc", "url": "/x",
                            "diff": {"status": "changed"}}) + "\n"
                + json.dumps({"timestamp": now - 9999, "service": "svc", "url": "/y",
                              "diff": {"status": "changed"}}) + "\n",
                encoding="utf-8",
            )
            recent = differ.get_recent_diffs(seconds=300)
            assert len(recent) == 1
            assert recent[0]["url"] == "/x"


class TestConfigLoader:
    """Tests for configuration loading and saving."""
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = get_default_config(Path(tmpdir))
            assert isinstance(config, WupConfig)
            assert config.project.name == Path(tmpdir).name
            assert len(config.watch.paths) > 0
            assert len(config.watch.exclude_patterns) > 0
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a config
            project = ProjectConfig(name="test-project", description="Test")
            watch = WatchConfig(paths=["app/**"], exclude_patterns=["*.md"])
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**"]
            )
            config = WupConfig(
                project=project,
                watch=watch,
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            # Save it
            config_path = Path(tmpdir) / "wup.yaml"
            save_config(config, config_path)
            assert config_path.exists()
            
            # Load it
            loaded_config = load_config(Path(tmpdir), config_path)
            assert loaded_config.project.name == "test-project"
            assert len(loaded_config.services) == 1
            assert loaded_config.services[0].name == "users"
    
    def test_load_config_from_yaml(self):
        """Test loading configuration from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a YAML config file
            config_content = """
project:
  name: "test-project"
  description: "Test project from YAML"

watch:
  paths:
    - "app/**"
    - "src/**"
  exclude_patterns:
    - "*.md"
    - "tests/**"

services:
  - name: "users"
    root: "app/users"
    paths:
      - "app/users/**"
    quick_tests:
      scope: "read,write"
      max_endpoints: 3
    detail_tests:
      scope: "all"
      max_endpoints: 10
    cpu_throttle: 0.7
    notify:
      type: "file"
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
  scenario_dir: "scenarios/tests"
  smoke_scenario: "smoke.testql.toon.yaml"
  output_format: "json"
  extra_args:
    - "--timeout 10s"
"""
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text(config_content)
            
            # Load it
            config = load_config(Path(tmpdir), config_path)
            assert config.project.name == "test-project"
            assert len(config.watch.paths) == 2
            assert len(config.services) == 1
            assert config.services[0].name == "users"
            assert config.services[0].quick_tests.scope == "read,write"
            assert config.services[0].quick_tests.max_endpoints == 3
            assert config.test_strategy.quick["debounce_s"] == 2
            assert config.testql.scenario_dir == "scenarios/tests"
    
    def test_load_config_auto_detect(self):
        """Test auto-detection of config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create wup.yaml
            config_content = """
project:
  name: "test"
"""
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text(config_content)
            
            # Load without specifying path
            config = load_config(Path(tmpdir))
            assert config.project.name == "test"
    
    def test_load_config_no_file_returns_default(self):
        """Test that missing config file returns default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_config(Path(tmpdir))
            assert isinstance(config, WupConfig)
            assert config.project.name == Path(tmpdir).name
    
    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text("invalid: yaml: content: [")
            
            with pytest.raises(Exception):
                load_config(Path(tmpdir), config_path)
    
    def test_load_config_missing_project_name(self):
        """Test that missing project.name raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_content = """
project:
  description: "Test"
"""
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text(config_content)
            
            with pytest.raises(ValueError, match="project.name"):
                load_config(Path(tmpdir), config_path)

    def test_save_and_load_visual_diff_config(self):
        """Test that visual_diff section is correctly saved and reloaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WupConfig(
                project=ProjectConfig(name="vd-test"),
                visual_diff=VisualDiffConfig(
                    enabled=True,
                    base_url="http://localhost:9000",
                    pages=["/health", "/users"],
                    delay_seconds=2.5,
                    max_depth=6,
                    threshold_added=7,
                    threshold_removed=4,
                    threshold_changed=8,
                    headless=False,
                ),
            )
            config_path = Path(tmpdir) / "wup.yaml"
            save_config(config, config_path)

            loaded = load_config(Path(tmpdir), config_path)
            vd = loaded.visual_diff
            assert vd.enabled is True
            assert vd.base_url == "http://localhost:9000"
            assert vd.pages == ["/health", "/users"]
            assert vd.delay_seconds == 2.5
            assert vd.max_depth == 6
            assert vd.threshold_added == 7
            assert vd.threshold_removed == 4
            assert vd.threshold_changed == 8
            assert vd.headless is False

    def test_load_config_visual_diff_from_yaml(self):
        """Test parsing visual_diff section from raw YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_content = """
project:
  name: "my-app"
visual_diff:
  enabled: true
  base_url: "http://localhost:8100"
  base_url_env: "MY_BASE_URL"
  delay_seconds: 3.0
  max_depth: 8
  snapshot_dir: ".wup/snaps"
  diff_dir: ".wup/diffs"
  pages:
    - "/dashboard"
    - "/settings"
  pages_from_endpoints: false
  threshold_added: 5
  threshold_removed: 2
  threshold_changed: 9
  headless: false
"""
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text(yaml_content)
            config = load_config(Path(tmpdir), config_path)
            vd = config.visual_diff
            assert vd.enabled is True
            assert vd.base_url == "http://localhost:8100"
            assert vd.base_url_env == "MY_BASE_URL"
            assert vd.delay_seconds == 3.0
            assert vd.max_depth == 8
            assert vd.snapshot_dir == ".wup/snaps"
            assert vd.diff_dir == ".wup/diffs"
            assert vd.pages == ["/dashboard", "/settings"]
            assert vd.pages_from_endpoints is False
            assert vd.threshold_added == 5
            assert vd.threshold_removed == 2
            assert vd.threshold_changed == 9
            assert vd.headless is False

    def test_load_config_visual_diff_defaults_when_section_absent(self):
        """visual_diff section absent → all defaults used."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "wup.yaml"
            config_path.write_text("project:\n  name: x\n")
            config = load_config(Path(tmpdir), config_path)
            vd = config.visual_diff
            assert vd.enabled is False
            assert vd.base_url == ""
            assert vd.max_depth == 10
            assert vd.pages == []
            assert vd.headless is True

    def test_load_dotenv_sets_env_var(self):
        """_load_dotenv should load .wup.env into os.environ."""
        import os
        from wup.config import _load_dotenv

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            env_file = root / ".wup.env"
            env_file.write_text('WUP_TEST_DUMMY_VAR=hello_wup\n# comment\n', encoding="utf-8")
            existing = os.environ.pop("WUP_TEST_DUMMY_VAR", None)
            try:
                _load_dotenv(root)
                assert os.environ.get("WUP_TEST_DUMMY_VAR") == "hello_wup"
            finally:
                os.environ.pop("WUP_TEST_DUMMY_VAR", None)
                if existing is not None:
                    os.environ["WUP_TEST_DUMMY_VAR"] = existing

    def test_load_dotenv_does_not_overwrite_existing(self):
        """_load_dotenv must NOT overwrite already-set env vars."""
        import os
        from wup.config import _load_dotenv

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            env_file = root / ".wup.env"
            env_file.write_text('WUP_TEST_NOOVERWRITE=from_file\n', encoding="utf-8")
            os.environ["WUP_TEST_NOOVERWRITE"] = "original"
            try:
                _load_dotenv(root)
                assert os.environ["WUP_TEST_NOOVERWRITE"] == "original"
            finally:
                os.environ.pop("WUP_TEST_NOOVERWRITE", None)


class TestConfigIntegration:
    """Tests for configuration integration with WupWatcher."""
    
    def test_watcher_with_config(self):
        """Test WupWatcher initialization with config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = ProjectConfig(name="test", description="Test")
            watch = WatchConfig(paths=["app/**"])
            config = WupConfig(
                project=project,
                watch=watch,
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            assert watcher.config.project.name == "test"
            assert len(watcher.config.watch.paths) == 1
    
    def test_watcher_uses_config_debounce(self):
        """Test that watcher uses config debounce settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            strategy = TestStrategyConfig(
                quick={"debounce_s": 5, "max_queue": 5, "timeout_s": 10},
                detail={"debounce_s": 15, "max_queue": 1, "timeout_s": 30}
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=strategy,
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            assert watcher.debounce_seconds == 5
    
    def test_watcher_build_watched_paths_from_config(self):
        """Test build_watched_paths uses config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directories
            (Path(tmpdir) / "app").mkdir()
            (Path(tmpdir) / "src").mkdir()
            
            watch = WatchConfig(paths=["app/**", "src/**"])
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=watch,
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            paths = watcher.build_watched_paths()
            assert len(paths) == 2
            assert any("app" in p for p in paths)
            assert any("src" in p for p in paths)
    
    def test_watcher_infer_service_from_config(self):
        """Test service inference uses configured service paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="users",
                root="app/users",
                paths=["app/users/**", "routes/users/**"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            inferred = watcher.infer_service(str(Path(tmpdir) / "app" / "users" / "routes.py"))
            assert inferred == "users"
    
    def test_watcher_get_service_config(self):
        """Test getting service configuration by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="users",
                root="app/users",
                quick_tests=ServiceTestConfig(scope="read", max_endpoints=5)
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            svc_config = watcher.get_service_config("users")
            assert svc_config is not None
            assert svc_config.name == "users"
            assert svc_config.quick_tests.max_endpoints == 5
            
            # Test non-existent service
            assert watcher.get_service_config("nonexistent") is None
    
    def test_watcher_schedule_quick_test_uses_config_limit(self):
        """Test that quick test scheduling uses config max_endpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="users",
                root="app/users",
                quick_tests=ServiceTestConfig(scope="all", max_endpoints=5)
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            watcher.dependency_mapper.service_to_endpoints["users"] = [
                f"/api/endpoint{i}" for i in range(10)
            ]
            
            watcher.schedule_quick_test("users")
            test_type, service_name, endpoints = watcher.test_queue[0]
            assert len(endpoints) == 5  # Config limit
    
    def test_watcher_on_file_change_uses_exclude_patterns(self):
        """Test that file change respects config exclude patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app").mkdir()
            
            watch = WatchConfig(
                paths=["app/**"],
                exclude_patterns=["*.md", "*.txt"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=watch,
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = WupWatcher(tmpdir, config=config)
            
            # Test with excluded file
            md_file = str(Path(tmpdir) / "app" / "test.md")
            watcher.on_file_change(md_file)
            
            # Should not trigger any service changes
            assert len(watcher.changed_services) == 0


class TestTestQLWatcherConfig:
    """Tests for TestQLWatcher configuration integration."""
    
    def test_testql_watcher_with_config(self):
        """Test TestQLWatcher initialization with config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            testql_config = TestQLConfig(
                scenario_dir="scenarios/tests",
                smoke_scenario="smoke.testql.toon.yaml",
                extra_args=["--timeout 10s"]
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=testql_config
            )
            
            watcher = TestQLWatcher(tmpdir, config=config)
            assert watcher.config.project.name == "test"
            assert watcher.testql_extra_args == ["--timeout 10s"]
    
    def test_testql_watcher_uses_config_scenarios_dir(self):
        """Test that TestQLWatcher uses config scenario directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            testql_config = TestQLConfig(scenario_dir="custom/scenarios")
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=TestStrategyConfig(),
                testql=testql_config
            )
            
            watcher = TestQLWatcher(tmpdir, config=config)
            assert "custom/scenarios" in str(watcher.scenarios_dir)
    
    def test_testql_watcher_get_service_config(self):
        """Test getting service configuration in TestQLWatcher."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ServiceConfig(
                name="users",
                root="app/users",
                quick_tests=ServiceTestConfig(scope="read", max_endpoints=5)
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = TestQLWatcher(tmpdir, config=config)
            svc_config = watcher.get_service_config("users")
            assert svc_config is not None
            assert svc_config.name == "users"
            assert svc_config.quick_tests.max_endpoints == 5
    
    def test_testql_watcher_select_scenarios_uses_config_limit(self):
        """Test that scenario selection uses config max_endpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some dummy scenario files
            scenarios_dir = Path(tmpdir) / "testql-scenarios"
            scenarios_dir.mkdir()
            for i in range(5):
                (scenarios_dir / f"test{i}.testql.toon.yaml").write_text("# test")
            
            service = ServiceConfig(
                name="users",
                root="app/users",
                quick_tests=ServiceTestConfig(scope="all", max_endpoints=2)
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[service],
                test_strategy=TestStrategyConfig(),
                testql=TestQLConfig()
            )
            
            watcher = TestQLWatcher(tmpdir, scenarios_dir="testql-scenarios", config=config)
            scenarios = watcher._select_scenarios_for_service("users")
            # Should be limited by config when no matching scenarios found
            assert len(scenarios) <= 2
    
    def test_testql_watcher_uses_config_timeout(self):
        """Test that TestQLWatcher uses config timeout settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            strategy = TestStrategyConfig(
                quick={"debounce_s": 2, "max_queue": 5, "timeout_s": 30},
                detail={"debounce_s": 10, "max_queue": 1, "timeout_s": 60}
            )
            config = WupConfig(
                project=ProjectConfig(name="test"),
                watch=WatchConfig(),
                services=[],
                test_strategy=strategy,
                testql=TestQLConfig()
            )
            
            watcher = TestQLWatcher(tmpdir, config=config)
            assert watcher.config.test_strategy.quick["timeout_s"] == 30
            assert watcher.config.test_strategy.detail["timeout_s"] == 60
    
    def test_testql_watcher_without_config_loads_default(self):
        """Test that TestQLWatcher loads default config when not provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = TestQLWatcher(tmpdir)
            assert watcher.config is not None
            assert watcher.config.project.name == Path(tmpdir).name
