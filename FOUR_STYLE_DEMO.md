# Four-style Blender live build

Measured September 6, 2026 in Blender 5.1.2 on Windows. A continuous screen
recording captured seven actual scripted geometry stages beside four generated
Movie Clip Editor panes. Each stage sent the same 512×290 gray JPEG to four
concurrent H3 Max reference-to-video calls, producing 28 distinct five-second
480P clips. There were no supplied output clips, cuts, or time compression.

| Measured interval | Minimum | Median | Maximum |
|---|---:|---:|---:|
| Capture start to all four visible | 7.98s | 13.99s | 17.08s |
| Settled geometry edit to all four visible | 8.84s | 14.86s | 17.99s |
| Reported GPU inference per clip | 1.37s | 1.39s | 1.40s |

Treatments: expedition realism, North Sea storm, cinematic science fiction, and
physical miniature. Each pane uses a fixed object-free Krea 2 Turbo style image
as Image 2, with the current gray geometry as Image 1. Semantic prompts preserve
existing components while refining coarse proxy surfaces into manufactured forms.
The reference manifest validates SHA-256 hashes and images are cached for the
session. Fixed conditioning improves consistency but cannot guarantee exact style,
geometry, camera or temporal behavior. This remains an asynchronous live preview.
Parallelism produces four alternatives per refresh; it does not remove transfer
and edit-to-visible latency.

The first single-view attempt discarded valid responses because dependency-graph
invalidations were treated as edits. Content-based geometry comparison fixed it.
The test suite checks that invalidation alone does not change the geometry digest,
vertex edits do, four calls run concurrently from one capture, and out-of-order
responses reach the correct panes. Fifteen headless checks pass.

Local artifacts: `../outputs/style-anchored-live-build/gray-live-build.blend`,
`build-status.json`, `summary.json`, `final-screen.png`, and `recordings/*.mp4`.
The video retains real wait times. Scripted construction is explicitly labeled.
