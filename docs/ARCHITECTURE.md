# Architecture

The inherited fal suite lives in `controllers/`, `models/`, and `job_queue.py`. The H3 preview uses dedicated modules.

1. A Blender timer checks scene/view signatures, including evaluated geometry content.
2. Once edits settle, the main thread captures camera guidance and restores temporary render settings and colors.
3. `image_guidance.py` encodes JPEG/PNG references with explicit roles.
4. `live_grid.py` starts four workers for `minimax/h3-max/reference-to-video`.
5. Workers download MP4s and write timings without accessing `bpy`.
6. Main-thread completion handling rejects stale geometry results for display.
7. Movie Clip Editors loop accepted clips independently of the scene timeline.

Stop/load clears sessions. Submitted requests may finish. There is no automatic paid retry after uncertain completion.

## Per-style image guidance

| Pane | Images in `PER_STYLE_TEXT` |
| --- | --- |
| Cartoon | Three copies of the current full camera image |
| Claymation | Full image, camera-space normals, silhouette mask |
| Realistic | Full camera image |
| Gouache | Full image and 3×3 detail sheet |

Text defines the medium; no video or abstract swatch is supplied. Detail-sheet crops are ship-fixture-specific, not a general object detector. The model sees images, not mesh topology.

## Demo-specific behavior

`fresh_moving_build.py` builds a new scene and wraps completion events to trim moving previews using FFmpeg. It retains raw clips and trim metadata. **The normal addon grid plays full clips**; the excerpt behavior is specific to this demonstration.

Stage briefs describe existing components. Prompt constraints are soft: camera, inventory and style can still drift. `live_stream.py` / `stream_buffer.py` implement a separate first/last-frame camera-stream experiment, documented in [H3 notes](../H3_LIVE_PREVIEW.md).
