# Reproduce the ship demo

## What the video shows

The recording shows a scripted build in the actual Blender UI. It starts with a simple hull, enclosures, roof and mast, then adds a larger faired hull, decks, rails, crane, tenders, fenders, research gantry, winches and fine fittings. The earlier audited final scene contains 267 objects; object count is not a quality metric.

Eight batches produce 32 fresh five-second 768P clips. Panes loop seconds **3.0–4.8** as 1.8-second moving excerpts. Full outputs are preserved. This is a fixed trim, not an automatic semantic quality filter or a guarantee against transitions on future runs.

The final edit adds a 1.5-second finished-view opening, retains two seconds of the initial shape, removes the first wait, hides the OS title bar/local path, and adds instrumental music. Later waits and Blender's UI remain. It is not presented as uninterrupted raw footage or a sub-second render benchmark.

## Run

Install the extension and FFmpeg, clone this repository, and copy `.env.example` to `.env` with your key.

```powershell
python scripts/run_demo.py `
  --blender 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' `
  --env .env --output outputs/my-demo --generate
```

```sh
python scripts/run_demo.py --blender /path/to/blender --env .env --output outputs/my-demo --generate
```

The launcher opens a fresh scene, waits for the grid, and arms the build. Use a new output folder. `--dry-run` prints the launch command without starting Blender or making calls. The `--generate` flag explicitly enables paid requests.

For direct control, launch `scripts/fresh_moving_build.py` with Blender and pass `--env`, `--output`, `--grid`, and `--start-stage 5` after `--`. It waits for `start-build.flag`. A `stop-build.flag` stops new work and saves the scene; submitted requests can still complete.

## Recording and outputs

Use a screen recorder on the Blender window or monitor. Begin recording before arming a direct run. Keep the source gray and leave update labels visible. Crop the OS title bar to avoid exposing local paths. Generated outputs belong in ignored `outputs/`, not source control.

- `research-ship.blend`: scene and layout.
- `build-status.json`: stages and display timings.
- `guides-*`: camera captures, normals and masks.
- `h3-live-*.mp4`: full generated clips.
- `h3-live-*-moving.mp4`: trimmed moving previews.
- Preview JSON: raw path, trim range and processing time.

Provider `inference` time measures denoising. API turnaround, capture, download, trim and display are additional. Batch wall time is a different measurement; do not interchange them.
