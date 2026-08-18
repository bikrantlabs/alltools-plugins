from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def run_job(request: dict) -> None:
    job_id = request.get("jobId", "unknown")
    inputs = request.get("inputs", [])
    output_directory = Path(request["outputDirectory"])

    if not inputs:
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": "A PDF input is required.", "recoverable": True})
        return

    source = Path(inputs[0]["path"])
    if source.suffix.lower() != ".pdf" or not source.is_file():
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": "The selected file is not a readable PDF.", "recoverable": True})
        return

    try:
        reader = PdfReader(str(source))
        total_pages = len(reader.pages)
        chunks: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            chunks.append(page.extract_text() or "")
            emit({"type": "progress", "jobId": job_id, "value": index / max(total_pages, 1), "message": f"Extracting page {index} of {total_pages}"})

        output_directory.mkdir(parents=True, exist_ok=True)
        output_path = output_directory / f"{source.stem}.txt"
        output_path.write_text("\n\n".join(chunks), encoding="utf-8")
        emit({"type": "completed", "jobId": job_id, "outputs": [{"id": "text", "path": str(output_path), "mimeType": "text/plain", "sizeBytes": output_path.stat().st_size}]})
    except Exception as error:  # plugin boundary converts errors to user-safe protocol messages
        emit({"type": "failed", "jobId": job_id, "code": "PROCESSING_FAILED", "message": str(error), "recoverable": True})


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        if request.get("type") == "start":
            run_job(request)
        elif request.get("type") == "cancel":
            emit({"type": "cancelled", "jobId": request.get("jobId", "unknown")})


if __name__ == "__main__":
    main()
