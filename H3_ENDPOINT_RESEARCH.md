# H3 endpoint research for Blender

Verified 2026-09-06 against official endpoint `llms.txt` files. No paid generations were made for this research. The fal generation gatekeeper and workflow prompt packs skills were read.

## Verified interfaces

| Route | Inputs relevant to Blender | Best candidate role |
| --- | --- | --- |
| `minimax/h3-max-turbo/text-to-video` | Prompt, aspect ratio | Mood/environment exploration with little scene fidelity |
| `minimax/h3-max-turbo/image-to-video` | `image_url` opening frame, optional `end_image_url` final frame | Fast shot previews anchored at two Blender-rendered poses |
| `minimax/h3-max/reference-to-video` | `reference_image_urls` for subjects/style; `reference_video_urls` for motion/reference; optional audio | Interpret a cheap Blender animation with approved asset/style references |

All three documented routes accept integer durations 5–15 seconds, `480P` or `768P`, seed, and `prompt_expansion_mode`. R2V permits at most 12 assets across images, videos, and audio. Each reference video is 2–15 seconds and video references total at most 15 seconds. Audio has equivalent duration constraints and cannot be the only reference. Refer to assets as `Image 1`, `Video 1`, and `Audio 1` in prompts.

Sources: [Turbo T2V llms](https://fal.ai/models/minimax/h3-max-turbo/text-to-video/llms.txt), [Turbo I2V llms](https://fal.ai/models/minimax/h3-max-turbo/image-to-video/llms.txt), [H3 Max R2V llms](https://fal.ai/models/minimax/h3-max/reference-to-video/llms.txt).

## Important boundaries

- Four reference images fit the documented input limit. They are subject/style references, not four time-indexed keyframes or calibrated multiview cameras.
- R2V's input schema does not expose `image_url`, `end_image_url`, depth, normals, masks, camera matrices, or per-frame camera paths. I2V explicitly supports first/last conditioning. Do not combine the two schemas by assumption.
- A Blender reference video can convey camera movement, layout, and motion visually, but following it is a model behavior to measure; it is not a hard geometric constraint.
- The R2V API page includes an auxiliary `H3MaxCameraKeyframe` type under Other types. No camera keyframe input field is exposed in this endpoint's input schema or llms. This type alone does not establish supported camera control on R2V.
- A separate `minimax/h3-max-turbo/reference-to-video` llms URL returned an empty response in this check. Use the verified `minimax/h3-max/reference-to-video` route rather than inventing a Turbo R2V route.

Sources: [R2V API](https://fal.ai/models/minimax/h3-max/reference-to-video/api), [I2V API](https://fal.ai/models/minimax/h3-max-turbo/image-to-video/api).

## Timing and transport

`timings.inference` is DiT denoising time on the GPU backend. It is not request completion, input encoding, upload, queue delay, output encoding, download, or time until a playable frame. The docs describe balanced prompt expansion as about one second and quality as up to roughly 30 seconds. Do not infer the ability to disable expansion from output-field prose; supported input examples list balanced and quality.

Base64 data URI inputs are documented. They remove a separate file-upload step but do not eliminate transfer or model processing; the API explicitly notes that large base64 inputs can hurt request performance. `sync_mode` returns video as base64 rather than a CDN URL. Both transport paths require measurement.

**Measured locally after this documentation review:** Four existing ship viewport PNGs supplied as base64, five-second output, seed 42, balanced prompt expansion. One request per resolution; both requests ran concurrently.

| Resolution | GPU inference | API turnaround | Total delivery |
| --- | ---: | ---: | ---: |
| 480P | 1.919914s | 8.429726s | 9.871473s |
| 768P | 4.972883s | 19.172419s | 20.663297s |

The four-reference 480P request therefore achieved approximately two seconds of GPU inference in this sample. It did not deliver playable output in two seconds. These are single samples, not a latency distribution or a comparison against I2V. Concurrent execution may affect observed timings. Records: `../outputs/reference-benchmark/reference-480P-timing.json` and `../outputs/reference-benchmark/reference-768P-timing.json`.

**Unknown:** General performance with four references and scaling with reference number/size remain unverified. Exact geometric fidelity, camera adherence, multiview consistency, temporal continuity across independent calls, and scene edit response latency are also unverified.

Sources: [R2V API timing/files](https://fal.ai/models/minimax/h3-max/reference-to-video/api), [Turbo I2V llms](https://fal.ai/models/minimax/h3-max-turbo/image-to-video/llms.txt).

## Strongest Blender opportunity (proposal, not a verified result)

An additional local test with the same four images and a five-second 24fps motion
guide succeeded: 3.477495s GPU inference, 18.288849s API, 19.598057s total delivery,
excluding guide preparation. This is also one sample. A 12fps guide was rejected
with a frame-rate validation error; a guide encoded at 24fps was accepted. The
guide contains 12 unique rendered frames per second duplicated to 24fps.
See `../outputs/reference-benchmark/motion-reference-timing.json`.

Use Blender as the authoritative scene and animation system. Render a cheap five-second viewport animation ahead of the playhead. Send it as `Video 1` alongside up to four approved ship/environment/style images to R2V. Ask for the motion and composition of the video with the identity/materials of the images. Keep the original Blender view instantly interactive while the generated view catches up.

Compare this against first/last I2V on exactly the same camera move. R2V is the better hypothesis for mid-shot choreography because it receives temporal evidence throughout the shot; I2V is the simpler hypothesis for low-latency endpoints and pose anchoring. More references do not inherently make rendering faster.

Measure time from scene snapshot to first playable result, p50/p95 latency, GPU inference, reference preparation, scene silhouette/landmark drift, camera-motion drift, texture identity, seams, and stale-result discard rate. For buffered playback with independent jobs, a rough necessary throughput condition is concurrent jobs × clip duration / mean job delivery time > 1; serial continuity dependencies can remove that advantage. Interactive response time remains bounded by delivery latency even when throughput beats playback.
