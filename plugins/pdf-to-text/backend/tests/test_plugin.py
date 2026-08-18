import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from pypdf import PdfWriter
from alltools_pdf_to_text import run_job


def invoke(request: dict) -> dict:
    output = StringIO()
    with redirect_stdout(output):
        run_job(request)
    return json.loads(output.getvalue().strip().splitlines()[-1])


def test_invalid_input_returns_protocol_error(tmp_path: Path) -> None:
    response = invoke({
        "type": "start", "protocolVersion": 1, "jobId": "test-invalid",
        "inputs": [{"id": "source", "path": str(tmp_path / "not-a-pdf.txt")}],
        "outputDirectory": str(tmp_path / "output"),
    })
    assert response["type"] == "failed"
    assert response["code"] == "INVALID_INPUT"


def test_missing_multiple_inputs_are_rejected(tmp_path: Path) -> None:
    response = invoke({"type": "start", "jobId": "test-empty", "inputs": [], "outputDirectory": str(tmp_path)})
    assert response["type"] == "failed"
    assert response["code"] == "INVALID_INPUT"


def test_pdf_input_produces_text_output(tmp_path: Path) -> None:
    source = tmp_path / "report.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    with source.open("wb") as handle:
        writer.write(handle)
    output_directory = tmp_path / "output"
    response = invoke({
        "type": "start", "protocolVersion": 1, "jobId": "test-success",
        "inputs": [{"id": "source", "path": str(source)}],
        "outputDirectory": str(output_directory),
    })
    assert response["type"] == "completed"
    assert response["outputs"][0]["sourceName"] == "report.pdf"
    output_path = Path(response["outputs"][0]["path"])
    assert output_path.name == "report.txt"
    assert output_path.is_file()
