from pathlib import Path

import yaml

from deploy.validate_deployment import validate_deployment


ROOT = Path(__file__).resolve().parents[1]


def test_production_compose_uses_private_persistent_ollama_service():
    compose = yaml.safe_load((ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    app = services["tamanna-ai"]
    ollama = services["ollama"]

    assert app["environment"]["TAMANNA_MODEL_PROVIDER"] == "ollama"
    assert app["environment"]["TAMANNA_OLLAMA_URL"] == "http://ollama:11434"
    assert app["depends_on"]["ollama"]["condition"] == "service_healthy"
    assert ollama["image"] == "ollama/ollama:latest"
    assert ollama["volumes"] == ["ollama_data:/root/.ollama"]
    assert "ports" not in ollama


def test_development_compose_uses_private_persistent_ollama_service():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    app = services["tamanna-ai"]
    ollama = services["ollama"]

    assert app["environment"]["TAMANNA_OLLAMA_URL"] == "http://ollama:11434"
    assert app["depends_on"]["ollama"]["condition"] == "service_healthy"
    assert ollama["image"] == "ollama/ollama:latest"
    assert ollama["volumes"] == ["tamanna_ollama_data:/root/.ollama"]
    assert "ports" not in ollama

def test_deployment_preflight_accepts_private_ollama_compose():
    report = validate_deployment(
        ROOT / "deploy" / "docker-compose.yml",
        ROOT / "deploy" / "nginx" / "tamanna-https.conf",
    )
    assert report["status"] == "PASS", report["findings"]
