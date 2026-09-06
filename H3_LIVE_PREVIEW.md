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

## Development verification

Run `blender --background --factory-startup --python-exit-code 1 --python tests/test_h3_live.py`.
The tests cover full extension registration/teardown, payload validation, successful
download/timing persistence, and timeout behavior without retries or credential
disclosure. These tests do not make paid requests.

Manual checks: capture a viewport, verify looping playback, rotate the view with
Auto refresh enabled, verify that idle does not submit additional requests, stop
while a request is in progress, and load another scene. Test on the target Blender
version; initial development uses Blender 5.1.2 on Windows.
