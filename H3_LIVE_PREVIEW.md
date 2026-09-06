# H3 Max Turbo live viewport

This experimental panel captures a 3D viewport and animates that image with
`minimax/h3-max-turbo/image-to-video`. It is an asynchronous AI preview, not a
pixel-accurate render engine. Generated camera motion and geometry can diverge
from Blender. A single image does not transmit the scene's animation.

## Use

1. Configure the extension's fal key, or launch Blender with `FAL_KEY` in its environment.
2. Open a 3D Viewport, press N, and choose **H3 Live**.
3. Click **Open side-by-side preview**. The adjacent Movie Clip Editor loops the result independently of the scene timeline. Its playback is silent.
4. Enter a motion prompt. **Capture once** makes one five-second clip.
5. **Auto refresh** captures after navigation, object transforms, geometry edits,
   timeline changes, or prompt/resolution changes settle. Only one request per
   session is in flight. An unchanged view does not generate repeatedly.
6. **Stop** prevents further submissions and discards late results for that session.
   An already submitted request may still finish and be billed. The session clip
   limit also stops submissions. Starting another session waits until the previous
   worker exits, avoiding accidental overlapping submissions.

The panel displays GPU denoising time, API turnaround, and total time including
capture and download. Each input PNG, output MP4, and timing JSON is saved in the
extension output directory. Credentials and image data URIs are not saved to JSON.
HTTP runs in a daemon worker; Blender data access, capture, and playback remain on
the main thread. Capturing may briefly pause interaction. Network errors stop the
session, with no automatic paid retry. Loading another blend file stops the session.

480p is the default. Each refresh is a paid API request. Current pricing is on the
[official endpoint](https://fal.ai/models/minimax/h3-max-turbo/image-to-video).
The schema was verified against its `llms.txt` on September 6, 2026.

## First/last camera stream

The **First + Last Frame Stream** panel follows an existing Blender camera animation.
Set the timeline to the first desired frame, set the session clip limit, and click
**Stream camera animation**. At least five seconds must remain in the frame range.

For each five-second segment, the extension captures the camera's initial and final
frames, sends both captures as base64 data URIs (`image_url` and `end_image_url`), and
reuses the identical boundary image for the next segment. PNG is the default;
the Small JPEG capture option also applies here. Captures restore the current
frame afterward. The API uses balanced prompt expansion and the safety checker.

Two requests can run concurrently. Responses are played in segment order, regardless
of completion order. Playback begins after two contiguous clips are ready (one if
the entire session is one clip). Queued plus pending clips are capped at three.
The source camera timeline follows the video being played. If the buffer runs dry,
playback holds its last frame and increments the visible wait counter. Completion
holds the last frame. Stop prevents further requests; already submitted calls finish
without retries. Loading a new blend file cancels the local session.

This is look-ahead rendering of a known animation. It does not turn free camera
navigation into immediate generated video. Edits to the scene cannot change footage
already in the buffer; stop and restart from the desired frame after changing a shot.
Base64 removes a separate upload call but increases request size. Measure capture,
API, download, and buffer waits rather than interpreting GPU time as delivery time.

`scripts/ship_live_demo.py` builds the PELAGIC expedition ship and a 60-second camera
orbit. Run it in a new Blender process, with the extension installed:

```text
blender --factory-startup --online-mode --python scripts/ship_live_demo.py -- --env /path/to/.env --output /path/to/output --clips 12 --stream
```

It creates a new scene, saves `pelagic-ship.blend`, opens an AI playback pane and
telemetry panel, and runs the paired-frame demonstration. Use a separate process so
an existing scene is not replaced. The API key is read into process memory only.
`stream-status.json` records segment metadata and underruns without credentials.

## Gray geometry live build

The auto-refresh panel now offers **H3 Max / interpret gray geometry** using
reference-to-video with one current viewport reference, and **Small JPEG** using
512×290 quality-80 captures. Keep Solid shading set to Single color for a gray
source. The generated clip loops beside the editable geometry. New edits settle
before capture; obsolete in-flight results are discarded. Geometry content is
compared rather than dependency-graph invalidations, which capture can trigger.
Evaluating and hashing geometry on each tick can be expensive in large scenes.

Run `scripts/gray_live_build.py` in a fresh GUI Blender process:

```text
blender --factory-startup --online-mode --python scripts/gray_live_build.py -- --env /path/to/.env --output /path/to/output
```

Wait for `ready.flag`, begin recording the Blender window, then create
`start-build.flag` in the output directory. Seven scripted geometry stages build
a ship; every stage waits for a newly generated result and displays it for five
seconds. No output clips are supplied in advance. The script saves the scene,
final screenshot, and `build-status.json` with per-stage timing. Record the whole
window continuously to preserve visible latency. The timer drives real Blender
object edits; this is a scripted build, not a manual modeling performance.

Reference conditioning is approximate. This mode is an asynchronous generative
preview: it may reinterpret geometry or drift between clips, and it has several
seconds of edit-to-visible latency. It is not a geometry-exact raster renderer.

## Four simultaneous styles

Add `--grid` to the gray-build command to arrange the gray source beside a 2×2
grid. The four treatments are expedition realism, North Sea storm, cinematic
science fiction, and a physical miniature. Style prompts specify surface palette,
roughness, lighting, and water. They deliberately avoid cues such as finished ships,
extra fittings, panel lines, or unmodeled windows. Shared geometry rules cap detail
at the reference's current completeness. Simple geometry stays simple; each modeled
addition supplies the next level of detail.

Each settled edit captures one JPEG and starts four independent requests together.
Each pane plays as its response arrives; the scripted build advances after all
four are visible. Results map by style index, not completion order. Editing during
a batch invalidates its remaining results. A failed request stops new batches;
there is no automatic retry. Single-preview and camera-stream sessions cannot run
at the same time as the grid.

In a fresh workspace, use **Open four-style layout**, then **Start four-style grid**
in the H3 Live panel. The session limit counts batches: 10 means up to 40 paid
requests. The scripted seven-stage demo generates 28 clips. **Stop four-style grid**
stops new requests while already submitted requests may finish. The four fixed
treatment prompts live in `live_grid.py`; the panel prompt supplies shared geometry
and scene direction. Approximate reference conditioning still allows drift.
Add `--keep-live` to leave auto-refresh active after the scripted build. Subsequent
edits continue using the current reference, up to the remaining session limit.

## Automated verification

Run `blender --background --factory-startup --python-exit-code 1 --python tests/test_h3_live.py`.
The tests cover full extension registration/teardown, payload validation, successful
download/timing persistence, and timeout behavior without retries or credential
disclosure. These tests do not make paid requests.
They also verify paired base64 inputs, shared boundary reuse, timeline restoration
on failure, ordered playback after out-of-order completion, and single-clip prefill.
Additional checks cover JPEG reference payloads, content-based geometry changes,
and discarding a result when geometry changed while its request was in flight.

Manual checks: capture a viewport, verify looping playback, rotate the view with
Auto refresh enabled, verify that idle does not submit additional requests, stop
while a request is in progress, and load another scene. Test on the target Blender
version; initial development uses Blender 5.1.2 on Windows.
