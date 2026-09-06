# Fixed camera and geometry alignment

## Finding

The current reference-to-video pipeline does not enforce the Blender projection. It asks a generative model to reinterpret a rendered image. A motionless output camera can still begin with the wrong object scale, perspective or proportions. This is separate from temporal zoom or camera drift.

The release film also contained a scale animation on its gray input image. That editorial zoom has been removed. Its language now names the experiment directly: Real-time neural rendering, gray geometry input, generated output, and four styles. The existing footage still contains model interpretation errors; the copy change does not fix them.

## Controlled probe, 2026-09-06

One seed, one completed workboat, 480P, five seconds, balanced prompt expansion. The reference pair is the same gray geometry and daylight style reference. The I2V pair uses an already generated colored frame, which tests temporal stability only, not alignment to Blender.

| Test | Delivery seconds | Maximum tracked rotation | Maximum tracked translation | Maximum tracked scale change |
|---|---:|---:|---:|---:|
| Strict fixed-camera reference prompt | 6.20 | 1.12° | 2.16 px | 0.55% |
| Same prompt plus two-second static geometry video | 32.46 | 0.43° | 1.46 px | 0.20% |
| Colored first frame only | 5.61 | 0.69° | 1.95 px | 0.16% |
| Identical colored first and last frames | 6.46 | 0.34° | 1.31 px | 0.17% |

These are diagnostic feature-motion estimates over the central object region at sampled frames, not calibrated camera poses. Water, deformation, tracking error and moving geometry can affect them. One seed does not establish a reliable improvement across scenes. “Pass” in the probe means below 1% scale, 2 pixels translation and 0.5° rotation; it does not mean zero drift or correct geometry.

The returned expanded prompts explicitly retained static camera and stationary-object instructions. This probe does not support prompt rewriting as the primary cause. Both reference outputs still visually reinterpret parts of the ship. Adding a static video is therefore not an adequate hard-lock solution, particularly given the measured delivery cost.

Run the offline diagnostic with the Blender Python interpreter:

```powershell
python ../outputs/camera-lock-probe/measure.py ../release-film/assets/stage-7-style-2.mp4
```

The probe's Python dependencies are isolated in `../outputs/camera-lock-probe/deps`. Its `probe.py` makes four paid requests; `measure.py` makes none. Request settings, expanded prompts, clips and measurements are retained there.

## What the public API can constrain

- H3 reference mode accepts subject/style images and reference videos, not a camera matrix or geometry raster contract.
- Turbo I2V accepts first and last images. Identical endpoints encourage a closed, stationary clip but do not constrain every intermediate pixel.
- Neither reviewed input schema exposes depth, normals, segmentation masks, optical flow, camera extrinsics/intrinsics or a geometric constraint strength.
- Documented prompt expansion values are balanced and quality. Do not assume an undocumented disabled mode.

Official schemas: [reference-to-video](https://fal.ai/models/minimax/h3-max/reference-to-video/llms.txt), [Turbo image-to-video](https://fal.ai/models/minimax/h3-max-turbo/image-to-video/llms.txt).

## Design for strict alignment

For a real zero-zoom, zero-misalignment requirement, Blender must own the camera projection and visible geometry. The neural component should supply appearance rather than replace the entire object image.

1. Freeze one explicit Blender camera: transform, lens or orthographic scale, sensor, shift, output dimensions and pixel aspect. Use the same camera and raster dimensions for every style. Navigation can change the modeling view without silently changing the render camera.
2. Render geometry buffers for the current revision: silhouette, depth, normals, object/material IDs and optionally motion vectors. Geometry edits invalidate the buffers and all dependent neural results.
3. Generate or infer appearance in material/UV space: base color, roughness and bounded normal detail. Preserve surface positions; do not use generated displacement in strict mode. The four fixed style references guide appearance.
4. Render those materials on the actual mesh using Blender. The depth test and geometry determine silhouette, occlusion, component placement and camera projection on every frame. Disable temporal screen jitter in a pixel-lock verification mode.
5. Keep generated environmental motion behind the geometry mask. An H3 water/background clip can contribute motion, but must not redefine the vessel or its camera.
6. Show current geometry immediately with the last valid material state while new appearance is computed. Do not show stale geometry as if it belonged to the latest edit.

This is a hybrid neural-material renderer, not the same system as full-frame H3 generation. It guarantees that the modeled geometry stays put, but cannot promise arbitrary photorealistic surface interpretation from today's H3 image API. New topology also needs defined UV/material assignment, and newly exposed surfaces may initially use a fallback material.

## If full-frame H3 rendering is required

The model/backend needs a spatial conditioning path, rather than another paragraph in the prompt: dense depth/normal/ID conditioning, fixed camera metadata, per-frame geometric supervision and a strict mode that preserves the geometry raster. Conditioning alone still needs measured fidelity; a hard constraint or final geometry-owned rasterization is required for a zero-error promise.

A practical softer prototype can generate an aligned still candidate per geometry revision, validate it against the source, then animate that same approved frame as both first and last input. Reject misaligned candidates instead of presenting them. An affine registration gate can correct small translation/scale errors; it cannot recover a different viewpoint, changed cabin height or missing components. A previous revision must be labeled stale while a new valid result is pending.

## Acceptance criteria before claiming this solved

- Source camera and resolution hashes identical across styles and repeated renders.
- No generated foreground pixels outside the Blender silhouette in strict mode.
- Object/material boundaries and depth ordering follow the current geometry revision.
- A known set of projected mesh landmarks remains fixed when only style changes.
- Temporal tests check the whole clip, not only endpoints; failures retain a validated frame and expose a status.
- Repeat across bare hull, intermediate assembly and full assembly, all four styles and multiple seeds. Report motion, geometry deviation and end-to-end latency separately.

The current work diagnoses the limitation and removes misleading camera-direction defaults. It does not claim a production camera lock has been implemented.
