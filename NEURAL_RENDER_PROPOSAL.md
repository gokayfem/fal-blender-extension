# fal Render for Blender

## Product thesis

Give Blender a generated film view beside its authoritative 3D scene. Artists still
place objects, animate cameras, set focal length, and direct timing in Blender. The
film view interprets that scene as finished moving imagery: ocean, weather, atmosphere,
surface detail, and cinematography. A scheduler prepares upcoming footage while the
current shot plays. The 3D viewport remains immediately interactive.

The product promise is **direct a scene spatially and see it as a film**. It should
offer explicit choices between structural fidelity, creative freedom, and response
time. Generated video does not replace the underlying mesh or establish physically
correct rendering.

## Evidence from the PELAGIC prototype

Measured September 6, 2026. Five-second requests, balanced prompt expansion, base64
image inputs. Delivery includes API and output download; the Turbo result also
includes viewport capture. R2V numbers exclude preparation of its existing references.

| Route | Inputs | Resolution | GPU inference | Delivery |
|---|---|---|---:|---:|
| H3 Max Turbo I2V | First + last image | 480p | 0.535s mean | 7.079s mean |
| H3 Max R2V | Four ship images | 480p | 1.920s | 9.871s |
| H3 Max R2V | Four ship images | 768p | 4.973s | 20.663s |
| H3 Max R2V | Four ship images + motion video | 480p | 3.477s | 19.598s |

Turbo numbers cover twelve clips. With two concurrent requests, two clips prefetched,
and ordered playback, the ship sequence completed with zero buffer underruns. Actual
concatenated output is approximately 62.2 seconds because returned clips are slightly
longer than the requested five seconds. R2V measurements are single samples, not a
latency distribution. The two image-only R2V requests ran concurrently.

The four-reference 480p result validates roughly two seconds of GPU denoising in one
test. It does not establish two-second playable delivery. Qualitative inspection of
sampled R2V frames shows richer water, wake, and lighting than the viewport inputs;
the guided-video sample follows the intended broad view more closely than the free
480p reference sample. Exact camera error and geometry preservation were not scored.

Local artifacts live in `../outputs/reference-benchmark/` and `../outputs/ship-live/`.

## Three complementary rendering modes

### 1. Fast motion preview: first/last I2V + a motion brief

Use H3 Max Turbo I2V for short transitions whose opening and closing compositions
matter. Blender supplies both camera frames and generates a detailed prompt from
the scene's actual motion. Endpoints provide visual anchors; the prompt describes
the route between them. Prompt constraints are soft, not a camera trajectory API.

Compile the prompt from:

- Camera translation, orbit direction, target, focal length changes, and timing.
- Objects that must stay rigid, objects that move, and their intended actions.
- Environmental motion that the model may invent: sea, smoke, mist, vegetation.
- Continuity requirements: lighting, identity, shot duration, absence of cuts.

Example for the opening PELAGIC move:

> Produce one continuous five-second maritime tracking shot between the supplied
> starting and ending frames. The same PELAGIC expedition ship remains centered.
> The camera makes a small, smooth arc from its starboard quarter toward the bow,
> approximately eight degrees, maintaining distance, elevation, and focal length.
> Move continuously throughout the shot and reach the supplied final composition;
> do not cut, reverse direction, zoom, or perform an additional orbit.
>
> Keep the navy hull, orange sheer stripe, ivory bridge, mast, crane, lifeboats,
> windows, and railings rigid and consistent. Preserve their relative positions
> and correct occlusion as the camera moves. Allow only gentle whole-vessel heave
> and roll. Ocean waves flow past the hull, bow foam separates along its sides,
> and the wake trails aft. Maintain the same daylight direction and exposure.
> Prioritize matching both compositions and the ship's structure over adding detail.

Do not claim that a long prompt enforces exact intermediate poses. Compare a concise
motion brief with this detailed brief using the same seed and frames. Contradictory
instructions can reduce adherence. Keyframe pairs also retain the appearance of
their inputs: rough viewport images may keep the output looking like a viewport.

### 2. Film appearance: reference-to-video

Use H3 Max R2V when the artist wants a richer interpretation of the scene. A useful
four-image package is two complementary asset views, one close detail, and one
approved lighting/material reference. This is a proposed packing strategy; the API
does not assign hard roles or calibrated cameras to those images. Prompt references
must explicitly name Image 1, Image 2, and so on.

Optional Video 1 supplies a cheap Blender animation for the intended camera move,
composition, occlusion, and object motion. This is the strongest candidate for
mid-shot choreography because the model sees temporal evidence across the shot.
It costs additional preparation and inference. Its motion is guidance, not guaranteed
camera matching. R2V has no documented first/last image input fields; do not combine
the I2V and R2V schemas by assumption.

Four images are not four timestamped keyframes, and are not a reconstructed 3D asset.
The endpoint exposes no depth, normals, masks, or camera-matrix controls.

### 3. Look exploration: text-to-video

Use T2V to explore weather, film stock, environment, and visual direction before
locking a shot. Generate several candidate looks, approve one, and extract useful
appearance references for subsequent R2V work. This gives the artist a visual target
before detailed modeling. T2V alone is not appropriate for preserving the exact ship.

## The most valuable experiences

**A director's viewport.** Put the ship on a simple ocean, animate a camera, and
switch between documentary, storm rescue, night expedition, or stylized illustration.
Keep the camera and asset as scene data while replacing the film interpretation.

**Expensive effects from cheap motion.** Animate broad wave shapes or smoke proxies
to describe timing; ask R2V to create spray, turbulence, weather, and atmosphere.
This targets the visual impression of effects, not an engineering simulation.

**Speculative directing.** At a decision point, prepare three camera moves in parallel:
continue, orbit toward the bow, or move alongside. The director chooses an already
prepared branch. Arbitrary motion still waits for generation; precomputed branches
make selected interactions feel immediate.

**Shot-level revision.** Change a ship asset or a camera curve and invalidate only
affected shots. Keep accepted outputs and their scene snapshots. Never let an old
generation silently replace a result for a newer scene revision.

**Protected product rendering.** For jobs where shape or typography must be exact,
retain a conventional Blender hero render and explore generated environments/effects
as separate compositing layers. Matching perspective, occlusion, reflections, and
shadows remains work to solve. A single generated clip should not be sold as an exact
product render without verification.

## Architecture

1. **Scene snapshot:** record the camera, timeline range, asset transforms, prompt,
   references, model, seed, and a revision identifier.
2. **Input builder:** capture first/last frames or a low-cost motion guide; choose
   reference views; compile a concise motion brief from real scene data.
3. **Mode selection:** Turbo I2V for preview/control; R2V for appearance or complex
   choreography; T2V for approved look exploration.
4. **Scheduler:** prioritize near-playhead shots, run bounded parallel work, track
   latency distributions, and buffer ordered results. Stop stale work before
   submission; discard obsolete returns locally.
5. **Review:** show source and generated output at corresponding times. Track ship
   landmarks, silhouette drift, camera movement, temporal seams, and user preference.
6. **Output:** keep the accepted shot and its provenance; assemble the timeline while
   preserving the original Blender scene for corrections.

For independent jobs, a rough throughput condition is `concurrency × clip duration /
mean delivery time > 1`. It needs headroom for variance and input preparation.
If every next shot depends on the generated last frame of the previous shot, that
serial dependency removes much of the concurrency benefit. Planned Blender boundary
frames enable parallelism but may show visual seams; this tradeoff must be measured.

## Where fal can create a deeper advantage

These are serving/model development proposals, not capabilities verified in the
current public API:

- Persist uploaded asset references and cache reusable reference encodings where
  the architecture permits, reducing repeated transfer and conditioning work.
- Stream playable video fragments early and avoid waiting for whole-file publication
  when practical. Measure time to first playable frame as well as denoising.
- Separate prompt expansion, reference preprocessing, queueing, denoising, decoding,
  packaging, and transfer in telemetry.
- Explore a Blender-focused conditioning interface for camera trajectories,
  object identity, depth, and motion fields if true scene fidelity is a target.
- Distill or specialize a reference-conditioned fast path on paired Blender
  previews and high-quality targets, while evaluating camera and object consistency.

## Next build

Build the director's viewport around the existing ship prototype. Add a three-way
mode selector, a motion-brief preview, four reference slots, a motion-guide toggle,
and A/B playback. Benchmark identical ship shots across simple orbit, translation,
occlusion, lens change, and object motion, with repeated seeds.

Measure p50/p95 scene-to-play latency, sustainable throughput, buffer waits, camera
adherence, silhouette/landmark drift, look preference, and seam visibility. Treat
“best” as a combination of control, appearance, and delivery rather than one speed
number. The current evidence favors Turbo for a fast preview and R2V for a more
ambitious appearance layer, pending controlled comparisons.

## Sources

- [H3 Max R2V schema](https://fal.ai/models/minimax/h3-max/reference-to-video/llms.txt)
- [H3 Max R2V API and transport](https://fal.ai/models/minimax/h3-max/reference-to-video/api)
- [H3 Max Turbo I2V schema](https://fal.ai/models/minimax/h3-max-turbo/image-to-video/llms.txt)
- [H3 Max Turbo T2V schema](https://fal.ai/models/minimax/h3-max-turbo/text-to-video/llms.txt)
- [Endpoint research and measured samples](H3_ENDPOINT_RESEARCH.md)

Runtime discovery: a 12fps motion guide was rejected with HTTP 422. The validation
message reported a supported range of approximately 23.899–60.193fps. Re-encoding
the five-second guide at 24fps succeeded. The guide used 12 unique source frames per
second duplicated to 24; denser native motion sampling should be tested separately.
