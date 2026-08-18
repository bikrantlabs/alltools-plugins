import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from alltools_pdf_to_text import run_job


def test_invalid_input_returns_protocol_error(tmp_path: Path) -> None:
    request = {
        "type": "start",
        "protocolVersion": 1,
        "jobId": "test-invalid",
        "inputs": [{"id": "source", "path": str(tmp_path / "not-a-pdf.txt")}],
        "outputDirectory": str(tmp_path / "output"),
    }
    output = StringIO()
    with redirect_stdout(output):
        run_job(request)
    response = json.loads(output.getvalue().strip())
    assert response["type"] == "failed"
    assert response["code"] == "INVALID_INPUT"
