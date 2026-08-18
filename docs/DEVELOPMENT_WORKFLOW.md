# AllTools Plugin Development Workflow

The plugin repository owns Python implementations, manifests, dependency metadata, fixtures, protocol behavior, and versioned distributable artifacts. The Electron repository owns the React screens, secure preload bridge, catalog presentation, installation lifecycle, and packaging. Use GitHub Issues as the durable record for requests and bugs; move discussion from chat into an issue before implementation begins.

## What belongs here

Open plugin-repository issues for new offline tools, input/output behavior, dependency changes, model downloads, protocol changes, performance work, platform compatibility, and incorrect backend output. If a user-facing screen is also required, choose the plugin request template and select **Both repositories**, then create or link the companion issue in `bikrantlabs/alltools-app`.

## Required plugin issue details

A plugin issue must describe the input and output workflow, accepted formats, options, progress and completion events, dependency requirements, model or GPU expectations, offline behavior, platform support, and fixture strategy. Avoid embedding product decisions only in implementation notes; the manifest and protocol contract must remain reviewable.

## Shared labels and states

Use the synchronized labels `type: feature`, `type: bug`, `type: design`, `type: chore`, `type: docs`, `area: plugin`, `area: protocol`, `area: packaging`, `priority: now`, `priority: next`, `priority: later`, `status: triage`, `status: ready`, `status: in progress`, `status: blocked`, `status: review`, `status: done`, and `coordination: app`, `coordination: plugin`, or `coordination: both`. Add `risk: contract` when a manifest or JSON-lines protocol change is involved.

## Definition of done

A plugin change is complete when its manifest validates against the versioned schema, the backend emits valid protocol events, fixtures or tests cover the meaningful path, dependencies are declared and reproducible, outputs are local and deterministic, and Plugin CI is green. For a cross-repository feature, link the app issue and confirm that Desktop CI also passes before moving the project item to Done.

## Cross-repository linking

Use `Part of #...`, `Blocked by bikrantlabs/alltools-app#...`, or `Related to bikrantlabs/alltools-app#...` in issue and pull-request descriptions. A shared-contract change must update the schema, implementation, and tests in both repositories in coordinated pull requests. The plugin repository must never inject React, HTML, CSS, or arbitrary frontend code into the desktop app.
