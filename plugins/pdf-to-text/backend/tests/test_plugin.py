import json
import subprocess
import sys
from pathlib import Path


def test_invalid_input_returns_protocol_error(tmp_path: Path) -> None:
    package_root = Path(__file__).parents[1] / "src"
    env = {**__import__("os").environ, "PYTHONPATH": str(package_root)}
    request = {
        "type": "start",
        "protocolVersion": 1,
        "jobId": "test-invalid",
        "inputs": [{"id": "source", "path": str(tmp_path / "not-a-pdf.txt")}],
        "outputDirectory": str(tmp_path / "output"),
    }
    process = subprocess.run(
        [sys.executable, "-m", "alltools_pdf_to_text"],
        input=json.dumps(request) + "\n",
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )
    response = json.loads(process.stdout.strip())
    assert response["type"] == "failed"
    assert response["code"] == "INVALID_INPUT"
