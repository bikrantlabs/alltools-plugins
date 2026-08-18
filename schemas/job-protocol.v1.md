# AllTools Job Protocol v1

The MVP uses newline-delimited JSON over the plugin process standard input and standard output. The protocol is intentionally small, deterministic, and independent of Electron internals.

## Request

The supervisor sends one request as a single JSON line:

```json
{
  "type": "start",
  "protocolVersion": 1,
  "jobId": "job-unique-id",
  "jobDirectory": "/absolute/path/to/private/job-directory",
  "inputs": [
    {
      "id": "source",
      "path": "/absolute/path/to/private/job-directory/input/source.pdf",
      "mimeType": "application/pdf"
    }
  ],
  "options": {},
  "outputDirectory": "/absolute/path/to/private/job-directory/output"
}
```

The plugin must treat the job directory as its working boundary. It must not require network access for a normal installed operation.

## Progress event

```json
{
  "type": "progress",
  "jobId": "job-unique-id",
  "value": 0.45,
  "message": "Extracting page 9 of 20"
}
```

`value` is a number from `0` to `1`. The plugin may emit multiple progress events. The frontend displays the latest value and message.

## Log event

```json
{
  "type": "log",
  "jobId": "job-unique-id",
  "level": "info",
  "message": "Input file validated"
}
```

Allowed levels are `debug`, `info`, `warning`, and `error`.

## Completion event

```json
{
  "type": "completed",
  "jobId": "job-unique-id",
  "outputs": [
    {
      "id": "text",
      "path": "/absolute/path/to/private/job-directory/output/result.txt",
      "mimeType": "text/plain",
      "sizeBytes": 2048
    }
  ]
}
```

## Failure event

```json
{
  "type": "failed",
  "jobId": "job-unique-id",
  "code": "INVALID_INPUT",
  "message": "The selected file is not a readable PDF.",
  "recoverable": true
}
```

Errors should be user-readable and must not expose secrets or unnecessary system paths.

## Cancellation

The supervisor sends a cancellation line:

```json
{
  "type": "cancel",
  "protocolVersion": 1,
  "jobId": "job-unique-id"
}
```

A cooperative plugin should stop promptly and respond:

```json
{
  "type": "cancelled",
  "jobId": "job-unique-id"
}
```

The supervisor will still terminate a plugin that does not stop within the configured timeout.

## MVP execution policy

The MVP runs one active job at a time. The protocol includes `jobId` so a future queue can support multiple jobs without changing the message shape. The desktop application owns temporary job directories and decides when completed outputs are copied to a user-selected destination.
