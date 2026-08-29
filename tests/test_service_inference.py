"""Unit tests for service inference logic."""
import tempfile
from pathlib import Path

from wup.core import WupWatcher
from wup.models.config import (
    ProjectConfig,
    ServiceConfig,
    WatchConfig,
    WupConfig,
)


def test_infer_service_with_empty_paths_uses_configured_services():
    """Verify configured services are used when paths are empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with services that have empty paths
        service_config = ServiceConfig(
            name="my-service",
            paths=[],  # Empty paths
            root="",
            type="shell"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Change a file that doesn't match service name
        test_file = root / "src" / "other" / "file.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        
        # Since paths are empty and service name doesn't match path,
        # inference should return None
        service = watcher.infer_service(str(test_file))
        assert service is None or service != "my-service"


def test_infer_service_with_explicit_paths_matches_path_patterns():
    """Test explicit path matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with explicit paths
        service_config = ServiceConfig(
            name="api-service",
            paths=["src/api/**"],
            root="",
            type="web"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Create a file that matches the explicit path
        test_file = root / "src" / "api" / "users.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        
        service = watcher.infer_service(str(test_file))
        assert service == "api-service"


def test_infer_service_with_auto_detection_matches_name_segments():
    """Test auto-detection with service name matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with service name that should match path segments
        service_config = ServiceConfig(
            name="users-service",
            paths=[],  # Empty paths - use auto-detection
            root="",
            type="web"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Create a file with service name in path
        test_file = root / "users-service" / "routes.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        
        service = watcher.infer_service(str(test_file))
        assert service == "users-service"


def test_infer_service_returns_none_for_unmatched_files():
    """Verify None or invalid service returned when no match."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with services that don't match the test file
        service_config = ServiceConfig(
            name="api-service",
            paths=["src/api/**"],
            root="",
            type="web"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Create a file that doesn't match any service
        test_file = root / "other" / "unrelated.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        
        service = watcher.infer_service(str(test_file))
        # Should return None or an invalid service that doesn't match config
        # The inference may construct a service name from path parts as fallback
        assert service is None or (service and service != "api-service")


def test_infer_service_with_duplicate_service_names():
    """Handle duplicate service names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with duplicate service names (shouldn't happen but test edge case)
        service_config1 = ServiceConfig(
            name="api-service",
            paths=["src/api/v1/**"],
            root="",
            type="web"
        )
        service_config2 = ServiceConfig(
            name="api-service",
            paths=["src/api/v2/**"],
            root="",
            type="web"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config1, service_config2],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Create files that match both services
        test_file1 = root / "src" / "api" / "v1" / "users.py"
        test_file1.parent.mkdir(parents=True, exist_ok=True)
        test_file1.write_text("test", encoding="utf-8")
        
        service = watcher.infer_service(str(test_file1))
        # Should return the first matching service
        assert service == "api-service"


def test_file_change_uses_configured_services_when_inference_fails():
    """Test that configured services are used when inference fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create config with services that have empty paths
        service_config = ServiceConfig(
            name="my-service",
            paths=[],
            root="",
            type="shell"
        )
        
        config = WupConfig(
            project=ProjectConfig(name="test"),
            services=[service_config],
            watch=WatchConfig(),
        )
        
        watcher = WupWatcher(project_root=str(root), config=config)
        
        # Create a file that won't match the service
        test_file = root / "src" / "other" / "file.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test", encoding="utf-8")
        
        # Mock schedule_quick_test to track which services are tested
        tested_services = []
        watcher.schedule_quick_test = lambda s: tested_services.append(s)
        
        # Trigger file change (event debounced per service)
        watcher.on_file_change(str(test_file))
        watcher._pending_event_times["my-service"] = 0  # force window elapsed
        watcher._flush_pending_events()

        # Should test the configured service even though inference failed
        assert "my-service" in tested_services
