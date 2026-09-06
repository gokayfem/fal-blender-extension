# Reference transport and JPEG experiment

Measured September 6, 2026 on H3 Max reference-to-video, four views of the same ship,
five-second 480P output, balanced prompt expansion. Three matched seed pairs per
image configuration (4200, 4201, 4202), alternating base64/URL order. A persistent
HTTP client was used. PNG and JPEG batches ran separately, so timing/load remains
a possible confound. These are small-sample medians, not production p95 estimates.

| Input | Generation request bytes | GPU median | API median | Delivery median |
|---|---:|---:|---:|---:|
| Original PNG / base64 | 2,395,514 | 1.915s | 11.090s | 12.779s |
| Original PNG / hosted URLs | 1,318 | 1.905s | 5.770s | 7.454s |
| 512x290 JPEG Q80 / base64 | 51,550 | 1.873s | 4.802s | 6.417s |
| 512x290 JPEG Q80 / hosted URLs | 1,294 | 1.851s | 5.011s | 6.496s |

Delivery includes API response and direct MP4 download, excluding preprocessing and
one-time upload. Four PNG uploads took 2.059s together; four JPEG uploads took 1.539s.
The four JPEG files totaled 37,860 bytes. Original PNG files totaled approximately
1.8MB. Images were resized and compressed together, so this test does not isolate
JPEG encoding from reduced pixel dimensions.

All output videos were returned as URLs (`sync_mode=false`) and downloaded directly.
Base64 here refers only to the input images. Hosted inputs were uploaded once and
reused across requests.

Interpretation: large embedded PNGs performed worst in this run. Small JPEG inputs
removed most of the observed difference between base64 and URLs. GPU inference
changed little. Small-JPEG base64 is a good next candidate for changing viewport
keyframes; persistent asset references can use cached URLs. This R2V experiment
does not establish the same benefit on I2V without a separate test.

The 384px-long-edge images were rejected because their short edge was below the
runtime minimum of 256 pixels. 512x290 was accepted. Sampled generated frames
preserved the general vessel design, but exact geometry, text, and small fittings
were not scored. Keep higher-resolution references where those details matter.

Local records: `../outputs/transport-benchmark/summary.json`,
`../outputs/jpeg-benchmark/summary.json`, and the corresponding `results.json` files.
