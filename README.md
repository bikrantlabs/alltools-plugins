# AllTools Plugins

This repository contains approved, offline-capable Python plugins for AllTools.

## Plugin requirements

Each plugin must provide a stable identifier, semantic version, manifest, Python project metadata, a locked dependency definition, tests, and a documented job contract. Plugins must process files locally after installation and must not provide or inject Electron renderer code.

## Expected plugin layout

```text
plugins/<plugin-id>/
  plugin.json
  backend/
    pyproject.toml
    uv.lock
    src/
    tests/
  README.md
```

Model-heavy plugins may additionally contain model metadata and a separate downloadable model artifact. Large model files should not be committed directly to the main source history unless there is a compelling reason.

## Release policy

Only approved tags and release artifacts are eligible for the production catalog. A release process will validate manifests, run tests, build an archive, calculate an integrity hash, and update the catalog entry.
