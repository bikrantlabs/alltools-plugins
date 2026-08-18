from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def safe_output_name(source: Path, used_names: set[str]) -> str:
    candidate = f"{source.stem}.txt"
    if candidate not in used_names:
        used_names.add(candidate)
        return candidate
    index = 2
    while f"{source.stem}-{index}.txt" in used_names:
        index += 1
    candidate = f"{source.stem}-{index}.txt"
    used_names.add(candidate)
    return candidate


def run_job(request: dict[str, Any]) -> None:
    job_id = str(request.get("jobId", "unknown"))
    inputs = request.get("inputs", [])
    output_directory = Path(request["outputDirectory"])

    if not isinstance(inputs, list) or not inputs:
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": "At least one PDF input is required.", "recoverable": True})
        return

    output_directory.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, Any]] = []
    used_names: set[str] = set()
    total_files = len(inputs)

    for file_index, descriptor in enumerate(inputs, start=1):
        source = Path(str(descriptor.get("path", "")))
        if source.suffix.lower() != ".pdf" or not source.is_file():
            emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": f"The selected file is not a readable PDF: {source.name or 'unknown file'}.", "recoverable": True})
            return

        try:
            reader = PdfReader(str(source))
            total_pages = len(reader.pages)
            chunks: list[str] = []
            for page_index, page in enumerate(reader.pages, start=1):
                chunks.append(page.extract_text() or "")
                completed_units = (file_index - 1) + page_index / max(total_pages, 1)
                emit({
                    "type": "progress",
                    "jobId": job_id,
                    "value": completed_units / total_files,
                    "message": f"Extracting {source.name} — page {page_index} of {total_pages}",
                })

            output_path = output_directory / safe_output_name(source, used_names)
            output_path.write_text("\n\n".join(chunks), encoding="utf-8")
            outputs.append({
                "id": f"text-{file_index}",
                "sourceName": source.name,
                "path": str(output_path),
                "mimeType": "text/plain",
                "sizeBytes": output_path.stat().st_size,
            })
        except Exception as error:  # plugin boundary converts errors to user-safe protocol messages
            emit({"type": "failed", "jobId": job_id, "code": "PROCESSING_FAILED", "message": f"Could not extract {source.name}: {error}", "recoverable": True})
            return

    emit({"type": "completed", "jobId": job_id, "outputs": outputs})


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
