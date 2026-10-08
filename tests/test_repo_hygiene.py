import subprocess

from conftest import ROOT


def test_dotenv_is_git_ignored() -> None:
    result = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT)
    assert result.returncode == 0


def test_env_example_has_placeholders_only() -> None:
    values = {}
    for line in (ROOT / ".env.example").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            key, _, value = line.partition("=")
            values[key] = value
    for key in ("ARXIV_BOT_DB_USER", "ARXIV_BOT_DB_PASSWORD", "ARXIV_BOT_DB_NAME"):
        assert values[key].startswith("change_me")


def test_compose_has_no_hardcoded_credentials() -> None:
    text = (ROOT / "docker-compose.yml").read_text()
    assert "${ARXIV_BOT_DB_PASSWORD:?" in text
    assert "127.0.0.1:" in text
