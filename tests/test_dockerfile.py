from pathlib import Path


def test_dockerfile_grants_appuser_access_to_logs_directory():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert "chown -R appuser:appuser /app" in dockerfile


def test_docker_run_loads_proxy_settings_from_env_file():
    makefile = Path("Makefile").read_text(encoding="utf-8")
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "--env-file .env" in makefile
    assert "-e HTTP_PROXY" not in makefile
    assert "HTTP_PROXY=" in env_example
    assert "HTTPS_PROXY=" in env_example
    assert "NO_PROXY=localhost,127.0.0.1" in env_example
