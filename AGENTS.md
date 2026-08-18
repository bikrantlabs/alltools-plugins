# AllTools Plugins Agent Guide

This repository owns approved, offline-capable Python plugins. It must remain independently testable and must not require the Electron desktop repository to be checked out.

## Repository boundary

The companion desktop repository is `bikrantlabs/alltools-app`. Its local development sibling is expected at `../alltools-desktop`, but plugin tests must run without it. The plugin repository owns the catalog, manifests, Python projects, dependency locks, backend tests, and release artifacts.

## Technology rules

Plugins use Python and `uv`. Each plugin owns a `pyproject.toml`, a committed `uv.lock`, source under `backend/src`, and tests under `backend/tests`. Do not commit virtual environments, generated caches, model binaries, or user files. Use dependency locks and keep runtime dependencies as small as practical.

Plugins are offline by default. The manifest must declare `network: false` for the MVP. Any GPU, model, filesystem, or platform requirement must be explicit in the manifest and documented. A plugin must not contain Electron code or provide frontend JavaScript, HTML, React components, or CSS.

## Stable manifest and protocol

The desktop app consumes `schemas/plugin-manifest.v1.json`. The current job protocol version is `1`, documented in `schemas/job-protocol.v1.md`. A plugin receives one newline-delimited JSON `start` request with a `jobId`, private job directory, input descriptors, options, and output directory. It emits JSON-line `progress`, `log`, `completed`, `failed`, or `cancelled` events.

A completed event must list output IDs, absolute output paths inside the job output directory, MIME types, and sizes. Errors must use stable codes and user-safe messages. A plugin should cooperate with cancellation and must not depend on network access for installed operation.

## Reference plugin: pdf-to-text

The reference implementation is `plugins/pdf-to-text`. It uses `pypdf` for local extraction and supports one or more PDF input files through separate job requests. The desktop application may submit one job per file in the MVP, then aggregate the results into a single output screen. Each output should have a predictable text filename based on the input filename.

If a plugin changes its input or output schema, update `plugin.json`, tests, and the catalog entry together. Do not silently change the behavior behind the same version. Use a new patch/minor version according to the compatibility impact.

## Parallel-development rules

Plugin work may proceed with protocol fixture requests without the desktop repository. Desktop work may use the committed manifest and catalog entry without the plugin source. Keep cross-repository assumptions in this file and in the desktop repository’s `AGENTS.md`, not only in code comments.

Before committing, run `uv lock` when dependency metadata changes, `uv sync --dev --frozen`, `PYTHONPATH=src uv run pytest -q`, and JSON validation for the plugin manifest and catalog. Keep commits focused and explain whether a change affects plugin behavior, protocol, manifest, dependencies, models, catalog, tests, or release packaging.

## Do not do

Do not execute arbitrary network code, do not require system Python packages, do not include unreviewed third-party plugins in the approved catalog, do not commit large model files without an explicit artifact strategy, and do not change protocol semantics without a versioned contract update.
