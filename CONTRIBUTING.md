# Contributing

Read [architecture](docs/ARCHITECTURE.md) and [limitations](docs/EXPERIMENTS.md). Keep changes focused; distinguish deterministic bugs from stochastic model behavior.

## Checks

Install `requirements.txt` in your development environment. Blender tests need the dependencies in its Python environment or `vendor/`.

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/test_h3_live.py
python scripts/check_repository.py
```

H3 tests mock HTTP and spend no API credits. The inherited model tests mock model behavior and are not live endpoint verification.

For UI/capture changes, test a capture, geometry edit, unchanged idle scene, Stop during a request, and loading another scene. For playback, verify moving frames rather than screenshots alone.

## Pull requests

Explain the trigger, changed behavior and checks actually run. Model experiments should include endpoint, resolution, seed, guidance and sample count. Separate inference from end-to-end latency. Never attach keys, `.env`, private scenes, or unreviewed logs.

Contributions retain GPL-3.0-or-later and upstream attribution.
