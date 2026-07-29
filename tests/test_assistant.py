"""Unit tests for WupAssistant."""
import tempfile
from pathlib import Path

from wup.assistant import WupAssistant
from wup.models.config import WupConfig, ProjectConfig, ServiceConfig


def test_framework_detection_fastapi():
    """Test auto-detecting FastAPI project framework."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create FastAPI characteristic files and content
        main_py = root / "main.py"
        main_py.write_text("from fastapi import FastAPI\napp = FastAPI()", encoding="utf-8")
        
        assistant = WupAssistant(str(root))
        detected = assistant._detect_framework()
        assert detected == "fastapi"


def test_framework_detection_flask():
    """Test auto-detecting Flask project framework."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create Flask characteristic files and content
        app_py = root / "app.py"
        app_py.write_text("from flask import Flask\napp = Flask(__name__)", encoding="utf-8")
        
        assistant = WupAssistant(str(root))
        detected = assistant._detect_framework()
        assert detected == "flask"


def test_framework_detection_none():
    """Test framework detection returns None when no markers match."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assistant = WupAssistant(str(root))
        detected = assistant._detect_framework()
        assert detected is None


def test_auto_detect_services_fastapi():
    """Test auto-detecting services for a FastAPI project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a router folder under app
        router_dir = root / "app" / "routers"
        router_dir.mkdir(parents=True)
        (router_dir / "users.py").write_text("# user routes", encoding="utf-8")
        
        assistant = WupAssistant(str(root))
        services = assistant._auto_detect_services("fastapi")
        
        assert len(services) == 1
        assert services[0].name == "users"
        assert services[0].type == "auto"
        assert services[0].paths[0].endswith("app/routers/users.py")


def test_detect_service_type():
    """Test service type detection based on name and path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assistant = WupAssistant(str(root))
        
        # Web service detection
        assert assistant._detect_service_type("my-api", root) == "web"
        assert assistant._detect_service_type("http-server", root) == "web"
        
        # Shell service detection
        assert assistant._detect_service_type("cli-tool", root) == "shell"
        assert assistant._detect_service_type("run-command", root) == "shell"
        
        # Default fallback
        assert assistant._detect_service_type("unknown", root) == "auto"


def test_validate_config_success():
    """Test config validation passes on a valid config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a watch path to satisfy validator
        src_dir = root / "src"
        src_dir.mkdir()
        
        # Create scenario dir to satisfy validator
        scenario_dir = root / "scenarios"
        scenario_dir.mkdir()
        
        assistant = WupAssistant(str(root))
        assistant.config = WupConfig(
            project=ProjectConfig(
                name="MyProj",
                description="Valid project"
            ),
            services=[
                ServiceConfig(name="web-service", type="web", paths=["src"])
            ]
        )
        assistant.config.watch.paths = ["src/**"]
        assistant.config.testql.scenario_dir = "scenarios"
        
        issues = assistant._validate_config()
        assert len(issues) == 0


def test_validate_config_issues():
    """Test config validation detects common errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assistant = WupAssistant(str(root))
        
        # 1. Empty/Missing project name
        assistant.config.project.name = ""
        # 2. No services configured
        assistant.config.services = []
        # 3. Non-existent watch path
        assistant.config.watch.paths = ["non_existent_dir/**"]
        # 4. Non-existent scenario directory
        assistant.config.testql.scenario_dir = "missing_scenarios"
        
        issues = assistant._validate_config()
        assert len(issues) == 4
        assert "Project name is required" in issues
        assert "No services configured" in issues
        assert "Watch path does not exist" in issues[2]
        assert "TestQL scenario directory not found" in issues[3]


def test_generate_suggestions():
    """Test assistant suggestions generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        assistant = WupAssistant(str(root))
        
        # Empty watch file types, single service, web dashboard disabled
        assistant.config.services = [ServiceConfig(name="single", type="web")]
        assistant.config.watch.file_types = []
        assistant.config.web.enabled = False
        assistant.config.testql.scenario_dir = "scenarios"
        assistant.config.testql.smoke_scenario = ""
        
        suggestions = assistant._generate_suggestions()
        assert len(suggestions) == 4
        assert "Consider splitting into multiple services" in suggestions[0]
        assert "Specify file types to avoid watching" in suggestions[1]
        assert "Enable web dashboard for real-time monitoring" in suggestions[2]
        assert "Set a smoke test scenario for quick health checks" in suggestions[3]


def test_quick_setup():
    """Test quick non-interactive setup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create FastAPI marker to let quick setup detect it
        main_py = root / "main.py"
        main_py.write_text("from fastapi import FastAPI", encoding="utf-8")
        
        assistant = WupAssistant(str(root))
        assistant.run(quick=True)
        
        # Should save wup.yaml
        config_path = root / "wup.yaml"
        assert config_path.exists()
        
        # Verify content of saved config
        import yaml
        saved_data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert saved_data["project"]["name"] == root.name
        assert "fastapi" in saved_data["project"]["description"].lower()
        assert len(saved_data["services"]) > 0
        assert saved_data["web"]["enabled"] is True
