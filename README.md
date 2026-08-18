# AllTools Plugins

AllTools Plugins is the approved, offline-capable Python plugin repository for the AllTools desktop application. Each plugin is independently versioned and managed with `uv`. The repository does not contain Electron or frontend code.

## Current status

The current reference plugin is `pdf-to-text`. It uses `pypdf` to extract text locally from one or more PDF inputs and returns one `.txt` output per input. The desktop app displays those outputs with file sizes and native download actions.

The production plugin download and per-user installation flow is planned. During development, the desktop app reads the sibling repository directly.

## Repository layout

```text
alltools-plugins/
  catalog/
    catalog.json                 # approved plugin catalog
  schemas/
    plugin-manifest.v1.json      # manifest schema
    job-protocol.v1.md            # JSON-lines execution protocol
  plugins/
    pdf-to-text/
      plugin.json                # plugin identity and UI/job contract
      backend/
        pyproject.toml            # Python dependencies and scripts
        uv.lock                   # reproducible dependency lock
        src/alltools_pdf_to_text/
          __init__.py
          __main__.py
        tests/test_plugin.py
  AGENTS.md                       # agent and parallel-development guidance
```

## Prerequisites

Install the following tools:

| Tool | Purpose |
|---|---|
| Git | Source control and release workflows |
| Python 3.11 or newer | Plugin execution and tests |
| uv | Python environment and dependency management |

The plugin repository does not require Node.js or Electron for its own tests.

## Clone the repositories

The plugin repository can be cloned independently:

```bash
git clone https://github.com/bikrantlabs/alltools-plugins.git
cd alltools-plugins
```

For local desktop integration, place the repositories as siblings:

```text
AllToolsWorkspace/
  alltools-desktop/
  alltools-plugins/
```

The desktop application expects the plugin repository at `../alltools-plugins` during development. Plugin tests do not require the desktop repository.

## Set up the PDF-to-text plugin

Move into the plugin backend directory and create its managed environment:

```bash
cd plugins/pdf-to-text/backend
uv sync --dev --frozen
```

The command installs the locked runtime dependency (`pypdf`) and development dependency (`pytest`) into the local environment. The `.venv` directory is generated and must not be committed.

## Run plugin tests

Run the reference plugin test suite:

```bash
cd plugins/pdf-to-text/backend
PYTHONPATH=src uv run pytest -q
```

The tests cover invalid inputs, empty input lists, and successful PDF output generation. Validate metadata from the repository root:

```bash
python3 -m json.tool plugins/pdf-to-text/plugin.json >/dev/null
python3 -m json.tool catalog/catalog.json >/dev/null
```

## Run the plugin directly

The backend accepts newline-delimited JSON requests on standard input and writes newline-delimited JSON events to standard output. A minimal request can be stored in a temporary file or piped directly:

```bash
cd plugins/pdf-to-text/backend
printf '%s\n' '{"type":"start","protocolVersion":1,"jobId":"manual-1","jobDirectory":"/tmp/alltools-job","inputs":[{"id":"source-1","path":"/absolute/path/example.pdf","mimeType":"application/pdf"}],"options":{},"outputDirectory":"/tmp/alltools-job/output"}' | uv run --frozen python -m alltools_pdf_to_text
```

The output contains progress events followed by a completion event. The completion event lists output IDs, source filenames, output paths, MIME types, and byte sizes.

## Add or modify a plugin

Create a directory under `plugins/<plugin-id>`. Each plugin should include a `plugin.json`, a backend `pyproject.toml`, a committed `uv.lock`, source under `backend/src`, tests under `backend/tests`, and a short plugin README when the workflow needs additional explanation.

The plugin ID must be stable and kebab-case. The version must follow semantic versioning. The manifest must declare Python and uv runtime information, supported platforms, a network-disabled capability set, an entrypoint using protocol version 1, UI mode, and input/output schemas.

When dependencies change, run:

```bash
cd plugins/<plugin-id>/backend
uv lock
uv sync --dev --frozen
```

Never commit `.venv`, caches, model binaries, or user files.

## Update the approved catalog

The catalog at `catalog/catalog.json` contains only approved plugins. A development entry may use a local source. A production entry should point to an approved, versioned release artifact with integrity metadata. Update the catalog when a plugin version or manifest changes, and validate it as JSON before committing.

## Release preparation

The intended release process validates the manifest, runs tests, builds a versioned plugin archive, calculates an integrity hash, publishes an approved release artifact, and updates the catalog. The desktop app should consume immutable approved versions rather than arbitrary branches.

## Development rules

Plugins must run offline after installation and must not inject Electron frontend code. Use the versioned JSON-lines protocol documented in [`schemas/job-protocol.v1.md`](schemas/job-protocol.v1.md). Breaking protocol changes require a new protocol version and coordinated updates to the desktop repository.

See [`AGENTS.md`](AGENTS.md) for the complete cross-repository contract and parallel-development rules.

## Useful development commands

```bash
# Refresh a dependency lock
cd plugins/pdf-to-text/backend
uv lock

# Run tests from a clean locked environment
uv sync --dev --frozen
PYTHONPATH=src uv run pytest -q

# Check repository state
cd ../../..
git status
git log --oneline -5
```
