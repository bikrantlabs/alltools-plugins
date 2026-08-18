from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def run_job(request: dict[str, Any]) -> None:
    job_id = str(request.get("jobId", "unknown"))
    inputs = request.get("inputs", [])
    output_directory = Path(str(request.get("outputDirectory", "")))
    if not isinstance(inputs, list) or len(inputs) < 2:
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": "Select at least two PDF files to merge.", "recoverable": True})
        return

    output_directory.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    total_pages = 0
    try:
        readers: list[tuple[Path, PdfReader]] = []
        for descriptor in inputs:
            source = Path(str(descriptor.get("path", "")))
            if source.suffix.lower() != ".pdf" or not source.is_file():
                emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": f"The selected file is not a readable PDF: {source.name or 'unknown file'}.", "recoverable": True})
                return
            reader = PdfReader(str(source))
            readers.append((source, reader))
            total_pages += len(reader.pages)

        completed_pages = 0
        for source, reader in readers:
            for page in reader.pages:
                writer.add_page(page)
                completed_pages += 1
                emit({
                    "type": "progress",
                    "jobId": job_id,
                    "value": completed_pages / max(total_pages, 1),
                    "message": f"Merging {source.name} — page {completed_pages} of {total_pages}",
                })

        output_path = output_directory / "merged.pdf"
        with output_path.open("wb") as handle:
            writer.write(handle)
        emit({
            "type": "completed",
            "jobId": job_id,
            "outputs": [{"id": "merged-pdf", "sourceName": "Merged PDFs", "path": str(output_path), "mimeType": "application/pdf", "sizeBytes": output_path.stat().st_size}],
        })
    except Exception as error:
        emit({"type": "failed", "jobId": job_id, "code": "PROCESSING_FAILED", "message": f"Could not merge the PDFs: {error}", "recoverable": True})


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
