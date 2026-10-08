import os
import subprocess
import sys
from pathlib import Path

from conftest import ROOT

SENTINEL = "sentinel-password-value"


def test_missing_required_setting_stops_startup(tmp_path: Path) -> None:
    """DB_USER is missing: import fails, non-zero exit, no secret in the output."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("ARXIV_BOT_")}
    env.update(
        ARXIV_BOT_DB_PASSWORD=SENTINEL,
        ARXIV_BOT_DB_NAME="x",
        PYTHONPATH=str(ROOT / "src"),
    )
    result = subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "0"],
        cwd=tmp_path,  # no .env here
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode != 0
    assert "db_user" in (result.stdout + result.stderr).lower()
    assert SENTINEL not in result.stdout + result.stderr
