# AuroraLedger

AuroraLedger is a lightweight utility that helps a solo builder script, sample, and log small Web3 interactions when prototyping new concepts. It keeps everything local, tracks hypothetical payloads, and keeps notes on the design steps taken so independent devs can recall how they explored a new idea.

## What it does

- Keeps a simple configuration for target networks, RPC endpoints, and scripted steps.
- Helps craft repeatable payloads (mint, swap, stake) so a future CLI can hit the right entry points.
- Logs each proposal to a local `records/` folder with metadata about why the change was made.
- Provides a gentle planner so you can note what needs to be done next before running the real thing.

## Repository layout

- `README.md` — this guide.
- `.gitignore` — ignores build artifacts and keeps the instructions file safe.
- `src/auroralogger.py` — the current utility that builds payloads and writes mock records.

## Getting started

1. Make sure you have Python 3.10+ installed.
2. Run `python src/auroralogger.py --help` to see the CLI.
3. Use `python src/auroralogger.py --plan "add a new swap route"` to capture next steps.
4. Generate a placeholder payload with `python src/auroralogger.py --op mint --target 0xabc123 --amount 12.5 --note "initial seed"`.

### Persisting records

Each payload is serialized into the `records/` folder, named after the request id. This mirrors the way I might track payloads before hitting a real chain, which is important when juggling several small personal experiments.

## Roadmap

1. Draft a JSON schema to validate payloads before serialization.
2. Add a lightweight CLI wrapper that can schedule payload playback for testing.
3. Link the utility to a simple UI later when quick demos are needed for investors or friends.
