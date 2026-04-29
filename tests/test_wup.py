"""Tests for WUP (What's Up) - Intelligent file watcher for regression testing."""

import json
import tempfile
from pathlib import Path

import pytest

from wup.dependency_mapper import DependencyMapper
from wup.core import WupWatcher


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
            watcher = WupWatcher(
                tmpdir,
                cpu_throttle=0.5,
                debounce_seconds=5,
                test_cooldown_seconds=600
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


def test_import():
    """Verify the main package can be imported."""
    import wup  # noqa: F401
    from wup import WupWatcher, DependencyMapper  # noqa: F401
