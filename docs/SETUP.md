# Installation and setup

## Tested environment

The H3 demo was exercised on Blender 5.1.2 / Windows x64. The inherited manifest permits older Blender versions, but that is not a claim that this workflow was tested on them. FFmpeg is required by the moving-excerpt demo; the normal grid plays full clips without it.

## Download or build an installable package

For Blender 5.1.2 on Windows x64, download the wheel-bundled ZIP from the [experimental preview release](https://github.com/gokayfem/fal-blender-extension/releases/tag/neural-preview-0.2.0). To build your own:

Use Python 3.11+ with pip. Target Blender's embedded Python:

```sh
python scripts/package_extension.py --platform windows-x64 --python-version 3.13
```

This downloads dependency wheels and writes a platform-specific ZIP under `dist/`. Install it via **Edit → Preferences → Add-ons → Install from Disk**, then enable **fal.ai — AI Generation Suite**. GitHub's source ZIP has no dependency wheels and is not an installable package.

The extension keeps ID `fal_ai`, occupying the same slot as upstream. Save work before updating an existing installation. This fork's releases are separate from upstream releases. The upstream `make package-split` workflow remains available for multi-platform packaging; a successful build alone does not establish runtime compatibility.

## Key and output directory

Configure a fal API key in preferences, or provide `FAL_KEY` before starting Blender. The demo launcher can read `--env .env`; Blender does not automatically read arbitrary `.env` files. Copy `.env.example` and fill it locally.

For demos, leave the preference output-directory override blank so the scene's chosen output folder is used. Metadata can contain prompts and local paths: review it before sharing. Never include keys in prompts, screenshots, or issues.

## Four-style preview

1. Add a scene camera and frame the object. Keep the viewport in camera view for comparison.
2. Press **N → H3 Live**.
3. Select **Cartoon / clay / real / painted** (`PER_STYLE_TEXT`).
4. Clear **Fixed style references**. This avoids loading an unused legacy manifest.
5. Select **768p** and a conservative session request limit.
6. Start the four-style grid, edit geometry, and let changes settle.
7. **Stop four-style grid** stops new batches. Submitted requests may still finish and be billed.

The four requests finish independently. Editing during a request invalidates that result for display; it does not cancel the model's work.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No H3 Live panel | Confirm this fork's package is enabled, rather than an upstream-only release. Restart after upgrading. |
| Missing `fal_client` or Pillow | Use the wheel-bundled ZIP, not a source archive. |
| Authentication fails | Check preferences / inherited environment and allow online access in Blender. |
| Manifest rejected | Clear the manifest in `PER_STYLE_TEXT`; legacy styles use a different contract. |
| Downloaded results do not appear | Stop editing long enough for the current revision to finish. |
| Demo stays at Ready | Use the launcher with `--generate`, or create `start-build.flag` in the output directory. |
| Preview trim fails | Ensure FFmpeg is on the PATH inherited by Blender. Raw outputs remain on disk. |
| Components or style change | See the [model-consistency findings](EXPERIMENTS.md). |
