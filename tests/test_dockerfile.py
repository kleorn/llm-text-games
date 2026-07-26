from pathlib import Path


def test_dockerfile_grants_appuser_access_to_logs_directory():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "chown -R appuser:appuser /app" in dockerfile
