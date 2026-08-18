from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

SUPPORTED_FORMATS = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP", "bmp": "BMP", "tiff": "TIFF"}


def emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def run_job(request: dict[str, Any]) -> None:
    job_id = str(request.get("jobId", "unknown"))
    inputs = request.get("inputs", [])
    output_directory = Path(str(request.get("outputDirectory", "")))
    options = request.get("options", {}) if isinstance(request.get("options", {}), dict) else {}
    target = str(options.get("format", "png")).lower().lstrip(".")
    if target not in SUPPORTED_FORMATS:
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": f"Unsupported output format: {target}.", "recoverable": True})
        return
    if not isinstance(inputs, list) or not inputs:
        emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": "Select at least one image file.", "recoverable": True})
        return

    output_directory.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, Any]] = []
    used_names: set[str] = set()
    try:
        for index, descriptor in enumerate(inputs, start=1):
            source = Path(str(descriptor.get("path", "")))
            if not source.is_file():
                emit({"type": "failed", "jobId": job_id, "code": "INVALID_INPUT", "message": f"The selected file cannot be read: {source.name or 'unknown file'}.", "recoverable": True})
                return
            with Image.open(source) as image:
                converted = image.convert("RGB") if SUPPORTED_FORMATS[target] == "JPEG" and image.mode not in {"RGB", "L"} else image.copy()
                stem = source.stem
                filename = f"{stem}.{target}"
                suffix = 2
                while filename in used_names:
                    filename = f"{stem}-{suffix}.{target}"
                    suffix += 1
                used_names.add(filename)
                output_path = output_directory / filename
                converted.save(output_path, format=SUPPORTED_FORMATS[target])
                converted.close()
            emit({"type": "progress", "jobId": job_id, "value": index / len(inputs), "message": f"Converted {source.name} to {target.upper()}"})
            outputs.append({"id": f"image-{index}", "sourceName": source.name, "path": str(output_path), "mimeType": Image.MIME.get(SUPPORTED_FORMATS[target], f"image/{target}"), "sizeBytes": output_path.stat().st_size})
        emit({"type": "completed", "jobId": job_id, "outputs": outputs})
    except Exception as error:
        emit({"type": "failed", "jobId": job_id, "code": "PROCESSING_FAILED", "message": f"Could not convert the images: {error}", "recoverable": True})


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
